#!/usr/bin/env python3
"""Mix voice, music, sound effects and ambience from a cue sheet into one
loudness-normalized WAV, with music ducked under the voice.

    python scripts/mix.py audio/cues.json
    python scripts/mix.py audio/cues.json --print

Cue sheet format: references/audio.md § mix.py cue sheet. Paths are relative to the cue sheet.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _media import media_info, require, run  # noqa: E402
from assemble import ffmpeg_major  # noqa: E402

GROUPS = ("voice", "music", "sfx", "ambience")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cues")
    ap.add_argument("--print", action="store_true")
    args = ap.parse_args()
    require("ffmpeg")

    cue_path = Path(args.cues).resolve()
    base = cue_path.parent
    cues = json.loads(cue_path.read_text(encoding="utf-8"))
    duration = float(cues["duration"])
    sr = int(cues.get("sample_rate", 48000))
    out = (base / cues.get("output", "mix.wav")).resolve()
    target = float(cues.get("target_lufs", -14))
    # -1.5 rather than -1.0: AAC/Opus encoding adds a few tenths of a dB of overshoot,
    # and the delivered file (not this WAV) is what platforms measure.
    tp = float(cues.get("true_peak", -1.5))
    duck = cues.get("duck") or {}

    inputs: list[str] = []
    graph: list[str] = []
    labels: dict[str, list[str]] = {g: [] for g in GROUPS}
    n = 0
    for group in GROUPS:
        for item in cues.get(group) or []:
            f = (base / item["file"]).resolve()
            if not f.exists():
                sys.exit(f"Missing audio file: {f}")
            if item.get("loop"):
                inputs += ["-stream_loop", "-1"]
            inputs += ["-i", str(f)]
            start = float(item.get("start", 0))
            offset = float(item.get("in", 0))
            gain = float(item.get("gain_db", 0))
            chain = [f"[{n}:a]aresample={sr}", "aformat=sample_fmts=fltp:channel_layouts=stereo"]
            if offset:
                chain.append(f"atrim=start={offset}")
                chain.append("asetpts=PTS-STARTPTS")
            length = duration - start
            if item.get("length"):
                length = min(length, float(item["length"]))
            chain.append(f"atrim=duration={max(0.01, length):.4f}")
            if item.get("fade_in"):
                chain.append(f"afade=t=in:d={item['fade_in']}")
            if item.get("fade_out"):
                if item.get("loop") or item.get("length"):
                    seg = length
                else:
                    seg = min(length, max(0.01, media_info(f)["duration"] - offset))
                chain.append(f"afade=t=out:st={max(0.0, seg - float(item['fade_out'])):.4f}:d={item['fade_out']}")
            chain.append(f"volume={gain}dB")
            if start:
                ms = int(round(start * 1000))
                chain.append(f"adelay={ms}|{ms}")
            chain.append(f"apad=whole_dur={duration:.4f}")
            graph.append(",".join(chain) + f"[{group}{n}]")
            labels[group].append(f"[{group}{n}]")
            n += 1
    if n == 0:
        sys.exit("Cue sheet has no audio.")

    def bus(group: str) -> str | None:
        ls = labels[group]
        if not ls:
            return None
        if len(ls) == 1:
            return ls[0]
        graph.append("".join(ls) + f"amix=inputs={len(ls)}:duration=longest:normalize=0[{group}bus]")
        return f"[{group}bus]"

    voice, music, sfx, amb = bus("voice"), bus("music"), bus("sfx"), bus("ambience")
    bed = None
    if music and amb:
        graph.append(f"{music}{amb}amix=inputs=2:duration=longest:normalize=0[bed]")
        bed = "[bed]"
    else:
        bed = music or amb

    if voice and bed and duck.get("enabled", True):
        amount = abs(float(duck.get("amount_db", 14)))
        # Speech sits roughly 15-25 dB above the threshold below, so ratio ~ amount/2
        # yields close to `amount` dB of reduction while the voice is present.
        ratio = max(2.0, min(20.0, amount / 2))
        graph.append(f"{voice}asplit=2[vmain][vkey]")
        graph.append(f"{bed}[vkey]sidechaincompress=threshold=0.02:ratio={ratio:.1f}:attack={duck.get('attack_ms', 40)}:release={duck.get('release_ms', 400)}:makeup=1[bedduck]")
        voice, bed = "[vmain]", "[bedduck]"

    final = [x for x in (voice, bed, sfx) if x]
    if len(final) > 1:
        graph.append("".join(final) + f"amix=inputs={len(final)}:duration=longest:normalize=0,atrim=duration={duration:.4f}[premix]")
    else:
        graph.append(f"{final[0]}atrim=duration={duration:.4f}[premix]")

    tmpdir = Path(tempfile.mkdtemp(prefix="dailies_mix_"))
    premix = tmpdir / "premix.wav"
    gfile = tmpdir / "graph.txt"
    gfile.write_text(";\n".join(graph), encoding="utf-8")
    gflag = ["-/filter_complex", str(gfile)] if ffmpeg_major() >= 7 else ["-filter_complex_script", str(gfile)]
    cmd1 = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, *gflag, "-map", "[premix]", "-c:a", "pcm_s24le", "-ar", str(sr), str(premix)]
    if args.print:
        print(subprocess.list2cmdline(cmd1))
        print("\n# filter graph\n" + ";\n".join(graph))
        return

    print(f"Mixing {n} cues ({duration:.2f}s)...")
    p1 = subprocess.run(cmd1)
    if p1.returncode != 0:
        print("\n# filter graph that failed\n" + ";\n".join(graph), file=sys.stderr)
        sys.exit(p1.returncode)

    # Two-pass loudnorm: measure, then apply with the measured values for an accurate target.
    meas = run(["ffmpeg", "-hide_banner", "-i", str(premix), "-af", f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"], capture=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", meas.stderr, re.S)
    if not m:
        sys.exit("Could not read loudness measurement.")
    s = json.loads(m.group(0))
    out.parent.mkdir(parents=True, exist_ok=True)
    ln = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={s['input_i']}:measured_TP={s['input_tp']}:"
          f"measured_LRA={s['input_lra']}:measured_thresh={s['input_thresh']}:offset={s['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(premix), "-af", ln, "-ar", str(sr), "-c:a", "pcm_s24le", str(out)])
    check = run(["ffmpeg", "-hide_banner", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"], capture=True).stderr
    integ = re.findall(r"I:\s+(-?[\d.]+) LUFS", check)
    peak = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", check)
    print(f"Wrote {out}")
    print(f"Loudness: {integ[-1] if integ else '?'} LUFS integrated (target {target}), true peak {peak[-1] if peak else '?'} dBTP (limit {tp})")


if __name__ == "__main__":
    main()
