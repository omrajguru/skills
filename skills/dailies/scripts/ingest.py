#!/usr/bin/env python3
"""Ingest a video or audio file: probe it, flag problems, find shots and silences,
transcribe it with word timings, and build a contact sheet.

    python scripts/ingest.py footage/raw/A001.mp4 --out footage/A001
    python scripts/ingest.py footage/raw/A001.mp4 --out footage/A001 --normalize
    python scripts/ingest.py audio/vo/vo.wav --out audio/vo/analysis
Options: --no-transcribe, --model small, --language en, --scene 0.3,
         --silence-db -35, --silence-min 0.6, --pad 0.12
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _media import fmt_time, has_filter, media_info, require, run, write_json  # noqa: E402
from contact_sheet import build_sheet, extract_frame  # noqa: E402

STANDARD_FPS = [23.976, 24, 25, 29.97, 30, 48, 50, 59.94, 60]


def nearest_fps(fps: float) -> float:
    return min(STANDARD_FPS, key=lambda s: abs(s - fps)) if fps else 30


def normalize(src: Path, info: dict, out_dir: Path) -> Path:
    """Constant frame rate, SDR Rec.709, rotation baked in, edit-friendly keyframes."""
    target = out_dir / f"{src.stem}.cfr.mp4"
    fps = nearest_fps(info.get("avg_fps") or info.get("fps") or 30)
    filters = []
    if info.get("hdr"):
        if has_filter("zscale") and has_filter("tonemap"):
            filters.append("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv")
        else:
            print("  ! HDR source but this ffmpeg lacks zscale/tonemap; colors will stay HDR. Install a full ffmpeg build.")
    filters.append("format=yuv420p")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", ",".join(filters),
           "-fps_mode", "cfr", "-r", str(fps), "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-g", str(max(1, round(fps / 2))), "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(target)]
    if not info.get("has_audio"):
        cmd = [c for c in cmd if c not in ("-c:a", "aac", "-b:a", "256k", "-ar", "48000")]
    print(f"  normalizing to {target.name} ({fps} fps CFR, SDR, upright)...")
    run(cmd)
    return target


def detect_scenes(src: Path, threshold: float) -> list[float]:
    proc = run(["ffmpeg", "-hide_banner", "-i", str(src), "-an", "-vf", f"scale=320:-2,select='gt(scene,{threshold})',showinfo",
                "-f", "null", "-"], capture=True, check=False)
    return [round(float(m), 3) for m in re.findall(r"pts_time:([\d.]+)", proc.stderr or "")]


def detect_silences(src: Path, noise_db: float, min_dur: float, duration: float) -> list[list[float]]:
    proc = run(["ffmpeg", "-hide_banner", "-i", str(src), "-vn", "-af", f"silencedetect=noise={noise_db}dB:d={min_dur}",
                "-f", "null", "-"], capture=True, check=False)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", proc.stderr or "")]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", proc.stderr or "")]
    if len(ends) < len(starts):
        ends.append(duration)
    return [[round(s, 3), round(e, 3)] for s, e in zip(starts, ends)]


def keep_ranges(silences: list[list[float]], duration: float, pad: float) -> list[list[float]]:
    """Spoken spans between silences, padded so words are not clipped."""
    ranges, cursor = [], 0.0
    for s, e in silences:
        if s - cursor > 0.05:
            ranges.append([max(0.0, cursor - pad), min(duration, s + pad)])
        cursor = e
    if duration - cursor > 0.05:
        ranges.append([max(0.0, cursor - pad), duration])
    merged: list[list[float]] = []
    for r in ranges:
        if merged and r[0] <= merged[-1][1] + 0.05:
            merged[-1][1] = max(merged[-1][1], r[1])
        else:
            merged.append(r)
    return [[round(a, 3), round(b, 3)] for a, b in merged]


def transcribe(wav: Path, model_name: str, language: str | None) -> dict | None:
    if importlib.util.find_spec("faster_whisper"):
        from faster_whisper import WhisperModel
        print(f"  transcribing with faster-whisper ({model_name})...")
        model = WhisperModel(model_name, compute_type="int8")
        segs, info = model.transcribe(str(wav), word_timestamps=True, vad_filter=True, language=language)
        segments = []
        for s in segs:
            words = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "prob": round(w.probability, 3)} for w in (s.words or [])]
            segments.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": words})
        return {"engine": "faster-whisper", "model": model_name, "language": info.language, "segments": segments}
    if importlib.util.find_spec("whisper"):
        import whisper
        print(f"  transcribing with openai-whisper ({model_name})...")
        model = whisper.load_model(model_name)
        res = model.transcribe(str(wav), word_timestamps=True, language=language)
        segments = [{"start": round(s["start"], 3), "end": round(s["end"], 3), "text": s["text"].strip(),
                     "words": [{"word": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3), "prob": round(w.get("probability", 1), 3)} for w in s.get("words", [])]}
                    for s in res["segments"]]
        return {"engine": "openai-whisper", "model": model_name, "language": res.get("language"), "segments": segments}
    cli = shutil.which("whisper-cli") or shutil.which("whisper-cpp")
    model_path = os.environ.get("WHISPER_CPP_MODEL")
    if cli and model_path:
        print("  transcribing with whisper.cpp...")
        base = wav.with_suffix("")
        cmd = [cli, "-m", model_path, "-f", str(wav), "-ml", "1", "-sow", "-oj", "-of", str(base)]
        if language:
            cmd += ["-l", language]
        run(cmd, capture=True)
        data = json.loads(Path(str(base) + ".json").read_text(encoding="utf-8"))
        words = [{"word": t["text"].strip(), "start": t["offsets"]["from"] / 1000, "end": t["offsets"]["to"] / 1000, "prob": 1.0}
                 for t in data.get("transcription", []) if t["text"].strip()]
        segments, cur = [], []
        for w in words:  # rebuild sentence-ish segments from word stream
            cur.append(w)
            if re.search(r"[.!?]$", w["word"]) or len(cur) >= 18:
                segments.append({"start": cur[0]["start"], "end": cur[-1]["end"], "text": " ".join(x["word"] for x in cur), "words": cur})
                cur = []
        if cur:
            segments.append({"start": cur[0]["start"], "end": cur[-1]["end"], "text": " ".join(x["word"] for x in cur), "words": cur})
        return {"engine": "whisper.cpp", "model": model_path, "language": language, "segments": segments}
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--normalize", action="store_true")
    ap.add_argument("--no-normalize", action="store_true", help="never normalize, even if recommended")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--model", default="small")
    ap.add_argument("--language")
    ap.add_argument("--scene", type=float, default=0.3)
    ap.add_argument("--silence-db", type=float, default=-35)
    ap.add_argument("--silence-min", type=float, default=0.6)
    ap.add_argument("--pad", type=float, default=0.12)
    ap.add_argument("--frames", type=int, default=16, help="evenly spaced frames in addition to shot changes")
    args = ap.parse_args()

    require("ffmpeg")
    src = Path(args.src).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    print(f"Ingesting {src.name}")
    info = media_info(src)
    write_json(out / "probe.json", info)
    duration = info["duration"]

    problems, actions = [], []
    if info.get("has_video"):
        if info.get("vfr"):
            problems.append(f"Variable frame rate (nominal {info['r_fps']} fps, average {info['avg_fps']} fps): audio can drift after cuts.")
        if info.get("hdr"):
            problems.append(f"HDR ({info['color_transfer']}): looks washed out next to SDR graphics.")
        if info.get("rotation"):
            problems.append(f"Rotation metadata ({info['rotation']} degrees): filters see the unrotated frame.")
        if problems:
            actions.append("Normalize: re-run with --normalize and edit from the .cfr.mp4 copy.")
    if info.get("has_audio") and info.get("sample_rate") and info["sample_rate"] < 44100:
        problems.append(f"Low audio sample rate ({info['sample_rate']} Hz).")

    work = src
    if info.get("has_video") and args.normalize and not args.no_normalize:
        work = normalize(src, info, out)

    scenes: list[float] = []
    if info.get("has_video"):
        print("  detecting shot changes...")
        scenes = detect_scenes(work, args.scene)
        write_json(out / "scenes.json", {"threshold": args.scene, "cuts": scenes})

    silences, keeps = [], []
    wav = None
    if info.get("has_audio"):
        print("  detecting silences...")
        silences = detect_silences(work, args.silence_db, args.silence_min, duration)
        keeps = keep_ranges(silences, duration, args.pad)
        spoken = sum(b - a for a, b in keeps)
        write_json(out / "silences.json", {"noise_db": args.silence_db, "min_duration": args.silence_min, "pad": args.pad,
                                          "silences": silences, "keep_ranges": keeps, "kept_seconds": round(spoken, 2)})
        wav = out / "audio16k.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(work), "-vn", "-ac", "1", "-ar", "16000", str(wav)])

    transcript = None
    if wav and not args.no_transcribe:
        transcript = transcribe(wav, args.model, args.language)
        if transcript:
            write_json(out / "transcript.json", transcript)
            (out / "transcript.txt").write_text("\n".join(f"[{fmt_time(s['start'])}] {s['text']}" for s in transcript["segments"]), encoding="utf-8")
        else:
            problems.append("No speech-to-text engine installed; transcript skipped (pip install faster-whisper).")

    sheet = None
    if info.get("has_video"):
        print("  extracting frames...")
        even = [duration * (i + 0.5) / args.frames for i in range(args.frames)]
        times = sorted({round(t, 2) for t in even + [min(c + 0.1, duration - 0.05) for c in scenes[:40]]})
        frames = [(t, extract_frame(work, t, out / "frames" / f"t{t:.2f}.jpg", 640)) for t in times]
        sheet = build_sheet(frames, out / "contact.jpg", title=f"{src.name} · {info['display_width']}x{info['display_height']} · {fmt_time(duration)}")

    lines = [f"# Ingest report: {src.name}", ""]
    if info.get("has_video"):
        lines.append(f"- Video: {info['display_width']}x{info['display_height']}, {info['vcodec']}, {info['fps']} fps, {info['pix_fmt']}, transfer {info['color_transfer'] or 'unspecified'}")
    if info.get("has_audio"):
        lines.append(f"- Audio: {info.get('acodec')}, {info.get('sample_rate')} Hz, {info.get('channels')} ch")
    lines.append(f"- Duration: {fmt_time(duration)} ({duration:.2f}s)")
    if scenes:
        lines.append(f"- Shot changes: {len(scenes)} (scenes.json)")
    if info.get("has_audio"):
        lines.append(f"- Silences over {args.silence_min}s: {len(silences)}; speech kept by keep_ranges: {sum(b - a for a, b in keeps):.1f}s of {duration:.1f}s")
    if transcript:
        words = sum(len(s["words"]) for s in transcript["segments"])
        lines.append(f"- Transcript: {words} words, language {transcript.get('language')} ({transcript['engine']}). Check names and jargon before using it for captions.")
    if work != src:
        lines.append(f"- Normalized copy: {work.name} (edit from this file)")
    lines += ["", "## Problems", *(f"- {p}" for p in problems or ["None found."])]
    if actions and work == src:
        lines += ["", "## Recommended", *(f"- {a}" for a in actions)]
    if sheet:
        lines += ["", f"Contact sheet: {sheet}"]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
