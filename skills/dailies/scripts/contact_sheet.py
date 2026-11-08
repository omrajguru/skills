#!/usr/bin/env python3
"""Extract frames from a video and lay them out as a labelled contact sheet.

    python scripts/contact_sheet.py video.mp4                       # ~24 evenly spaced frames
    python scripts/contact_sheet.py video.mp4 --count 12
    python scripts/contact_sheet.py video.mp4 --every 2.5
    python scripts/contact_sheet.py video.mp4 --start 30 --end 40 --every 0.5
    python scripts/contact_sheet.py video.mp4 --times 2.5,8,15 --frames-dir review/bg --no-sheet

Frames are named t<seconds>.png (e.g. t2.50.png), matching render.mjs stills.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _media import fmt_time, media_info, require, run  # noqa: E402


def extract_frame(video: str | Path, t: float, out: Path, width: int | None = None) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale={width}:-2" if width else "null"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
         "-frames:v", "1", "-vf", vf, str(out)])
    return out


def build_sheet(frames: list[tuple[float, Path]], out: Path, title: str = "", cols: int = 4, thumb_w: int = 480) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        sys.exit("Pillow is required for contact sheets: python -m pip install Pillow")
    thumbs = []
    for t, p in frames:
        if not p.exists():
            continue
        im = Image.open(p).convert("RGB")
        im.thumbnail((thumb_w, thumb_w * 4))
        thumbs.append((t, im))
    if not thumbs:
        sys.exit("No frames to lay out.")
    cell_h = max(im.height for _, im in thumbs)
    label_h, pad, head = 30, 12, (44 if title else 0)
    cols = min(cols, len(thumbs))
    rows = (len(thumbs) + cols - 1) // cols
    W = cols * thumb_w + (cols + 1) * pad
    H = head + rows * (cell_h + label_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (W, H), (17, 18, 20))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
        tfont = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font = tfont = ImageFont.load_default()
    if title:
        draw.text((pad, 10), title, fill=(235, 235, 235), font=tfont)
    for i, (t, im) in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = head + pad + r * (cell_h + label_h + pad)
        sheet.paste(im, (x + (thumb_w - im.width) // 2, y))
        draw.text((x, y + cell_h + 6), f"{fmt_time(t)}  ({t:.2f}s)", fill=(200, 200, 200), font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--count", type=int, default=24)
    ap.add_argument("--every", type=float, help="seconds between frames")
    ap.add_argument("--times", help="comma-separated timestamps")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float)
    ap.add_argument("--frames-dir", help="keep full-size frames here")
    ap.add_argument("--out", help="contact sheet path (default: <video>_contact.jpg)")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--no-sheet", action="store_true")
    args = ap.parse_args()

    require("ffmpeg")
    info = media_info(args.video)
    duration = info["duration"]
    end = min(args.end or duration, duration)
    if args.times:
        times = [float(x) for x in args.times.split(",") if x.strip()]
    elif args.every:
        n = int((end - args.start) / args.every) + 1
        times = [args.start + i * args.every for i in range(n)]
    else:
        span = end - args.start
        n = max(1, args.count)
        times = [args.start + span * (i + 0.5) / n for i in range(n)]
    times = [min(max(0.0, t), max(0.0, duration - 0.05)) for t in times]

    keep = Path(args.frames_dir) if args.frames_dir else None
    tmp = Path(tempfile.mkdtemp(prefix="dailies_frames_"))
    frames = []
    for t in times:
        target = (keep or tmp) / f"t{t:.2f}.png"
        extract_frame(args.video, t, target, None if keep else 960)
        frames.append((t, target))
        if keep:
            print(target)
    if not args.no_sheet:
        out = Path(args.out) if args.out else Path(args.video).with_name(Path(args.video).stem + "_contact.jpg")
        build_sheet(frames, out, title=f"{Path(args.video).name}  ·  {info.get('width')}x{info.get('height')}  ·  {fmt_time(duration)}", cols=args.cols)
        print(out)


if __name__ == "__main__":
    main()
