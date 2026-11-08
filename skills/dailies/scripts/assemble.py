#!/usr/bin/env python3
"""Assemble an edit from edit.json: frame-accurate cuts, punch-ins, reframing,
speed changes, stills with slow zooms, transitions, overlays, burned captions and audio.

    python scripts/assemble.py edit.json
    python scripts/assemble.py edit.json --print     # show the ffmpeg command and filter graph only

The edit.json format is documented in references/workflow-footage.md. Paths in
edit.json are relative to the edit.json file.
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
from _media import is_image, media_info, require, run  # noqa: E402

FADE = 0.015  # seconds of audio fade at every cut, so cuts do not click


def atempo_chain(speed: float) -> list[str]:
    """atempo accepts 0.5..2.0 per instance; chain for larger changes."""
    parts, s = [], speed
    while s > 2.0:
        parts.append("atempo=2.0")
        s /= 2.0
    while s < 0.5:
        parts.append("atempo=0.5")
        s /= 0.5
    parts.append(f"atempo={s:.6f}")
    return parts


def piecewise(keys: list[list[float]], index: int, default: float) -> str:
    """ffmpeg expression in t that linearly interpolates keyframes [[t, x, y], ...]."""
    if not keys:
        return f"{default}"
    keys = sorted(keys, key=lambda k: k[0])
    expr = f"{keys[-1][index]}"
    for (t0, *v0), (t1, *v1) in reversed(list(zip(keys, keys[1:]))):
        a, b = v0[index - 1], v1[index - 1]
        seg = f"({a}+({b}-{a})*(t-{t0})/{max(t1 - t0, 1e-6)})"
        expr = f"if(lt(t,{t1}),{seg},{expr})"
    return f"if(lt(t,{keys[0][0]}),{keys[0][index]},{expr})"


def ffmpeg_major() -> int:
    out = run(["ffmpeg", "-version"], capture=True).stdout
    m = re.search(r"ffmpeg version n?(\d+)", out)
    return int(m.group(1)) if m else 6


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edit")
    ap.add_argument("--print", action="store_true")
    args = ap.parse_args()
    require("ffmpeg")

    edit_path = Path(args.edit).resolve()
    base = edit_path.parent
    e = json.loads(edit_path.read_text(encoding="utf-8"))
    W, H, fps = int(e.get("width", 1920)), int(e.get("height", 1080)), float(e.get("fps", 30))
    fit = e.get("fit", "cover")
    out = (base / e.get("output", "renders/output.mp4")).resolve()
    clips = e.get("clips") or []
    if not clips:
        sys.exit("edit.json has no clips.")

    def p(rel: str) -> Path:
        q = (base / rel).resolve()
        if not q.exists():
            sys.exit(f"Missing file: {q}")
        return q

    inputs: list[str] = []
    graph: list[str] = []
    vlabels, alabels, durations = [], [], []

    for i, c in enumerate(clips):
        src = p(c["src"])
        speed = float(c.get("speed", 1.0))
        image = is_image(src)
        if image:
            dur = float(c.get("duration", 3.0))
            inputs += ["-loop", "1", "-framerate", f"{fps}", "-t", f"{dur:.3f}", "-i", str(src)]
            has_audio = False
        else:
            info = media_info(src)
            t_in = float(c.get("in", 0.0))
            t_out = float(c.get("out", info["duration"]))
            if t_out <= t_in:
                sys.exit(f"Clip {i}: out ({t_out}) must be after in ({t_in}).")
            dur = (t_out - t_in) / speed
            inputs += ["-ss", f"{t_in:.3f}", "-t", f"{t_out - t_in:.3f}", "-i", str(src)]
            has_audio = info.get("has_audio") and c.get("audio", True) is not False
        durations.append(dur)
        idx = len([x for x in inputs if x == "-i"]) - 1

        fx, fy = (c.get("focus") or [0.5, 0.5])[:2]
        punch = float(c.get("punch", 1.0))
        chain = [f"[{idx}:v]setpts=PTS-STARTPTS"]
        if speed != 1.0 and not image:
            chain.append(f"setpts=PTS/{speed}")
        chain.append(f"fps={fps}")
        if image and c.get("kenburns"):
            z0, z1 = (float(z) for z in c["kenburns"][:2])
            n = max(1, round(dur * fps) - 1)
            chain += [f"scale={2 * W}:{2 * H}:force_original_aspect_ratio=increase", f"crop={2 * W}:{2 * H}",
                      f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':d=1:s={W}x{H}:fps={fps}"]
        elif fit == "contain" and punch == 1.0:
            chain += [f"scale={W}:{H}:force_original_aspect_ratio=decrease", f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black"]
        else:
            sw, sh = round(W * punch / 2) * 2, round(H * punch / 2) * 2
            keys = c.get("focus_keys") or []
            xexpr = piecewise(keys, 1, fx) if keys else f"{fx}"
            yexpr = piecewise(keys, 2, fy) if keys else f"{fy}"
            chain += [f"scale={sw}:{sh}:force_original_aspect_ratio=increase",
                      f"crop={W}:{H}:x='(iw-{W})*clip({xexpr},0,1)':y='(ih-{H})*clip({yexpr},0,1)'"]
        chain += ["setsar=1", "format=yuv420p", f"trim=duration={dur:.4f}", "setpts=PTS-STARTPTS"]
        graph.append(",".join(chain) + f"[v{i}]")
        vlabels.append(f"[v{i}]")

        if has_audio:
            achain = [f"[{idx}:a]asetpts=PTS-STARTPTS"]
            if speed != 1.0:
                achain += atempo_chain(speed)
            achain += ["aresample=48000", "aformat=sample_fmts=fltp:channel_layouts=stereo", f"apad=whole_dur={dur:.4f}",
                       f"atrim=duration={dur:.4f}", f"afade=t=in:d={FADE}", f"afade=t=out:st={max(0.0, dur - FADE):.4f}:d={FADE}"]
            graph.append(",".join(achain) + f"[a{i}]")
        else:
            graph.append(f"aevalsrc=0:c=stereo:s=48000:d={dur:.4f},aformat=sample_fmts=fltp[a{i}]")
        alabels.append(f"[a{i}]")

    trans = e.get("transition") or {"type": "none"}
    T = float(trans.get("duration", 0.4)) if trans.get("type", "none") != "none" else 0.0
    if T and len(clips) > 1:
        if any(d <= T * 2 for d in durations):
            sys.exit(f"Every clip must be longer than twice the transition ({T}s).")
        xtype = "fade" if trans["type"] in ("fade", "dissolve", "crossfade") else trans["type"]
        v_prev, a_prev, length = vlabels[0], alabels[0], durations[0]
        for i in range(1, len(clips)):
            offset = length - T
            graph.append(f"{v_prev}{vlabels[i]}xfade=transition={xtype}:duration={T}:offset={offset:.4f}[vx{i}]")
            graph.append(f"{a_prev}{alabels[i]}acrossfade=d={T}[ax{i}]")
            v_prev, a_prev = f"[vx{i}]", f"[ax{i}]"
            length = length + durations[i] - T
        vcur, acur, total = v_prev, a_prev, length
    else:
        graph.append("".join(v + a for v, a in zip(vlabels, alabels)) + f"concat=n={len(clips)}:v=1:a=1[vcat][acat]")
        vcur, acur, total = "[vcat]", "[acat]", sum(durations)

    for j, o in enumerate(e.get("overlays") or []):
        osrc = p(o["src"])
        start = float(o.get("start", 0.0))
        end = float(o.get("end", total))
        if is_image(osrc):
            inputs += ["-loop", "1", "-framerate", f"{fps}", "-t", f"{total:.3f}", "-i", str(osrc)]
        else:
            inputs += ["-i", str(osrc)]
        oidx = len([x for x in inputs if x == "-i"]) - 1
        if "x" in o or "y" in o:
            ochain = f"[{oidx}:v]format=rgba,setpts=PTS-STARTPTS+{start}/TB[o{j}]"
            pos = f"{o.get('x', 0)}:{o.get('y', 0)}"
        else:
            # fit without distortion; overlays should normally be rendered at the output size anyway
            ochain = (f"[{oidx}:v]format=rgba,scale={W}:{H}:force_original_aspect_ratio=decrease,"
                      f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x00000000,setpts=PTS-STARTPTS+{start}/TB[o{j}]")
            pos = "0:0"
        graph.append(ochain)
        graph.append(f"{vcur}[o{j}]overlay={pos}:eof_action=pass:enable='between(t,{start},{end})'[vo{j}]")
        vcur = f"[vo{j}]"

    cwd = None
    cap = e.get("captions")
    if cap:
        cap = {"file": cap} if isinstance(cap, str) else cap
        cfile = p(cap["file"])
        cwd = str(cfile.parent)  # libass paths are hard to escape on Windows; run next to the file instead
        opts = [f"filename={cfile.name}"]
        if cap.get("fonts_dir"):
            fdir = p(cap["fonts_dir"])
            try:
                fonts_rel = fdir.relative_to(cfile.parent).as_posix()
            except ValueError:
                fonts_rel = fdir.as_posix().replace(":", "\\\\:")
            opts.append(f"fontsdir={fonts_rel}")
        graph.append(f"{vcur}subtitles={':'.join(opts)}[vsub]")
        vcur = "[vsub]"

    audio = e.get("audio") or {"mode": "clips"}
    mode = audio.get("mode", "clips")
    if mode in ("replace", "mix"):
        afile = p(audio["file"])
        inputs += ["-i", str(afile)]
        aidx = len([x for x in inputs if x == "-i"]) - 1
        graph.append(f"[{aidx}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad,atrim=duration={total:.4f}[ext]")
        if mode == "replace":
            graph.append(f"{acur}anullsink")
            acur = "[ext]"
        else:
            gain = float(audio.get("clip_gain_db", 0))
            graph.append(f"{acur}volume={gain}dB[clipa]")
            graph.append("[clipa][ext]amix=inputs=2:duration=first:normalize=0[amix]")
            acur = "[amix]"
    if audio.get("loudness") is not None:
        # single-pass loudnorm; for a mixed soundtrack prefer mix.py's two-pass result with mode "replace"
        graph.append(f"{acur}loudnorm=I={float(audio['loudness'])}:TP=-1.5:LRA=11,aresample=48000[anorm]")
        acur = "[anorm]"

    graph_text = ";\n".join(graph)
    out.parent.mkdir(parents=True, exist_ok=True)
    crf = str(e.get("crf", 18))
    tmp = Path(tempfile.mkdtemp(prefix="dailies_graph_")) / "graph.txt"
    tmp.write_text(graph_text, encoding="utf-8")
    graph_flag = ["-/filter_complex", str(tmp)] if ffmpeg_major() >= 7 else ["-filter_complex_script", str(tmp)]
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, *graph_flag,
           "-map", vcur, "-map", acur, "-c:v", "libx264", "-preset", "medium", "-crf", crf, "-pix_fmt", "yuv420p",
           "-r", f"{fps}", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{total:.3f}", str(out)]

    if args.print:
        print(subprocess.list2cmdline(cmd))
        print("\n# filter graph\n" + graph_text)
        return
    print(f"Assembling {len(clips)} clips -> {out.name} ({W}x{H} @ {fps} fps, {total:.2f}s)")
    proc = subprocess.run(cmd, cwd=cwd)
    if proc.returncode != 0:
        print("\n# filter graph that failed\n" + graph_text, file=sys.stderr)
        sys.exit(proc.returncode)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
