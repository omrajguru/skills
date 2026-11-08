#!/usr/bin/env python3
"""Check a finished video before delivery: format, duration, black or frozen
frames, loudness and true peak. Also builds a contact sheet of the final file.

    python scripts/qa.py renders/v1/video.mp4 --platform youtube --expect-duration 45
Platforms: youtube, shorts, reels, tiktok, instagram-feed, linkedin, x, podcast, broadcast-eu, broadcast-us, web
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _media import fmt_time, media_info, require, run  # noqa: E402
from contact_sheet import build_sheet, extract_frame  # noqa: E402

PLATFORMS = {
    # name: (aspect ratios accepted, loudness target, true-peak ceiling)
    "youtube": (["16:9"], -14, -1.0),
    "shorts": (["9:16"], -14, -1.0),
    "reels": (["9:16"], -14, -1.0),
    "tiktok": (["9:16"], -14, -1.0),
    "instagram-feed": (["4:5", "1:1"], -14, -1.0),
    "linkedin": (["16:9", "1:1", "4:5", "9:16"], -14, -1.0),
    "x": (["16:9", "1:1", "9:16"], -14, -1.0),
    "podcast": (["16:9", "1:1", "9:16"], -16, -1.0),
    "broadcast-eu": (["16:9"], -23, -1.0),
    "broadcast-us": (["16:9"], -24, -2.0),
    "web": (["16:9", "1:1", "4:5", "9:16", "21:9"], -14, -1.0),
}
RATIOS = {"16:9": 16 / 9, "9:16": 9 / 16, "1:1": 1.0, "4:5": 0.8, "21:9": 21 / 9}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--platform", default="web", choices=sorted(PLATFORMS))
    ap.add_argument("--expect-duration", type=float)
    ap.add_argument("--no-sheet", action="store_true")
    args = ap.parse_args()
    require("ffmpeg")

    path = Path(args.video)
    info = media_info(path)
    ratios, target_lufs, tp_limit = PLATFORMS[args.platform]
    results: list[tuple[str, str, str]] = []  # level, check, detail

    def add(level: str, check: str, detail: str) -> None:
        results.append((level, check, detail))

    if not info.get("has_video"):
        sys.exit("No video stream.")
    w, h = info["display_width"], info["display_height"]
    ar = w / h
    match = [r for r in ratios if abs(RATIOS[r] - ar) < 0.01]
    add("PASS" if match else "WARN", "aspect ratio", f"{w}x{h} ({ar:.3f}); {args.platform} expects {', '.join(ratios)}")
    add("PASS" if info["vcodec"] == "h264" else "WARN", "video codec", f"{info['vcodec']} (H.264 plays everywhere)")
    add("PASS" if info["pix_fmt"] == "yuv420p" else "WARN", "pixel format", f"{info['pix_fmt']} (yuv420p is the safe choice)")
    add("PASS" if not info.get("vfr") else "WARN", "frame rate", f"{info['fps']} fps" + (" (variable)" if info.get("vfr") else " constant"))
    add("PASS" if w % 2 == 0 and h % 2 == 0 else "FAIL", "even dimensions", f"{w}x{h}")
    dur = info["duration"]
    if args.expect_duration:
        off = abs(dur - args.expect_duration)
        add("PASS" if off <= 0.5 else "WARN", "duration", f"{dur:.2f}s (expected {args.expect_duration}s)")
    else:
        add("INFO", "duration", f"{dur:.2f}s ({fmt_time(dur)})")
    mb = info["size_bytes"] / 1e6
    add("INFO", "file size", f"{mb:.1f} MB, {mb * 8 / max(dur, 0.01):.1f} Mbit/s average")

    # One pass over the file: black and frozen frames on a downscaled copy, loudness on the audio.
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vf", "scale=480:-2,blackdetect=d=0.1:pix_th=0.04,freezedetect=n=-60dB:d=1.5"]
    if info.get("has_audio"):
        cmd += ["-af", "ebur128=peak=true"]
    cmd += ["-f", "null", "-"]
    log = run(cmd, capture=True, check=False).stderr or ""

    blacks = [(float(s), float(e)) for s, e in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)]
    issues = [b for b in blacks if not (b[0] < 0.05 and b[1] < 0.5) and not (b[1] > dur - 0.05 and b[1] - b[0] < 1.0)]
    if issues:
        add("WARN", "black frames", "; ".join(f"{s:.2f}-{e:.2f}s" for s, e in issues[:8]) + " (intentional fades are fine)")
    else:
        add("PASS", "black frames", "none unexpected")
    fstarts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", log)]
    fends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", log)] + [dur] * 10
    freezes = list(zip(fstarts, fends))
    if freezes:
        add("WARN", "frozen frames", "; ".join(f"{s:.2f}-{e:.2f}s" for s, e in freezes[:8]) + " (holds on stills/end cards are fine)")
    else:
        add("PASS", "frozen frames", "none over 1.5s")

    if info.get("has_audio"):
        integ = re.findall(r"I:\s+(-?[\d.]+) LUFS", log)
        peaks = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", log)
        lra = re.findall(r"LRA:\s+([\d.]+) LU", log)
        if integ:
            i_val = float(integ[-1])
            level = "PASS" if abs(i_val - target_lufs) <= 1.0 else "WARN"
            add(level, "loudness", f"{i_val:.1f} LUFS integrated (target {target_lufs}){', LRA ' + lra[-1] + ' LU' if lra else ''}")
        if peaks and peaks[-1] != "-inf":
            p_val = float(peaks[-1])
            add("PASS" if p_val <= tp_limit + 0.1 else "FAIL", "true peak", f"{p_val:.1f} dBTP (limit {tp_limit})")
        add("PASS" if info.get("sample_rate") in (44100, 48000) else "WARN", "audio format", f"{info.get('acodec')} {info.get('sample_rate')} Hz {info.get('channels')} ch")
    else:
        add("WARN", "audio", "no audio stream (fine for silent loops; most platforms expect audio)")

    sheet = None
    if not args.no_sheet:
        n = 12
        times = [dur * (i + 0.5) / n for i in range(n)]
        tmp = path.parent / f".{path.stem}_qa_frames"
        frames = [(t, extract_frame(path, t, tmp / f"t{t:.2f}.jpg", 640)) for t in times]
        sheet = build_sheet(frames, path.with_name(path.stem + "_qa.jpg"), title=f"QA · {path.name} · {w}x{h} · {fmt_time(dur)}")
        for _, f in frames:
            f.unlink(missing_ok=True)
        try:
            tmp.rmdir()
        except OSError:
            pass

    width = max(len(r[1]) for r in results)
    print(f"QA: {path}  (platform: {args.platform})")
    for level, check, detail in results:
        print(f"  {level:4s}  {check.ljust(width)}  {detail}")
    if sheet:
        print(f"Contact sheet: {sheet}")
    sys.exit(1 if any(r[0] == "FAIL" for r in results) else 0)


if __name__ == "__main__":
    main()
