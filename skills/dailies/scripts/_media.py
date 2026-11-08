"""Shared helpers for the dailies scripts: ffmpeg/ffprobe calls and media facts."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

# Windows consoles default to cp1252; credits and transcripts are full of non-ASCII text.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        sys.exit(f"{tool} not found on PATH. Run scripts/doctor.py for install instructions.")
    return path


def run(cmd: list[str], *, capture: bool = False, check: bool = True, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run a command; on failure print the tail of stderr instead of a traceback."""
    proc = subprocess.run(cmd, cwd=cwd, text=True, encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        tail = "\n".join((proc.stderr or "").strip().splitlines()[-25:])
        sys.exit(f"Command failed ({proc.returncode}): {' '.join(cmd[:6])} ...\n{tail}")
    return proc


def ffprobe(path: str | Path) -> dict:
    require("ffprobe")
    proc = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)], capture=True)
    return json.loads(proc.stdout)


def _rate(value: str | None) -> float:
    try:
        return float(Fraction(value)) if value and value != "0/0" else 0.0
    except (ValueError, ZeroDivisionError):
        return 0.0


def media_info(path: str | Path) -> dict:
    """Summarize the facts editing decisions depend on."""
    data = ffprobe(path)
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video" and s.get("disposition", {}).get("attached_pic") != 1), None)
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    fmt = data.get("format", {})
    info: dict = {"path": str(path), "duration": float(fmt.get("duration") or 0), "size_bytes": int(fmt.get("size") or 0),
                  "container": fmt.get("format_name"), "has_video": v is not None, "has_audio": a is not None}
    if v:
        rotation = 0
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rotation = int(float(sd["rotation"]))
        if not rotation and v.get("tags", {}).get("rotate"):
            rotation = int(v["tags"]["rotate"])
        r_fps, avg_fps = _rate(v.get("r_frame_rate")), _rate(v.get("avg_frame_rate"))
        transfer = v.get("color_transfer") or ""
        info.update({
            "width": v.get("width"), "height": v.get("height"), "vcodec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
            "fps": round(avg_fps or r_fps, 3), "r_fps": round(r_fps, 3), "avg_fps": round(avg_fps, 3),
            # A large gap between nominal and average rate is the usual sign of variable frame rate.
            "vfr": bool(r_fps and avg_fps and abs(r_fps - avg_fps) / r_fps > 0.01),
            "rotation": rotation,
            "color_transfer": transfer, "color_primaries": v.get("color_primaries"),
            "hdr": transfer in ("smpte2084", "arib-std-b67"),
            "bit_depth": int(v.get("bits_per_raw_sample") or 0) or (10 if "10" in (v.get("pix_fmt") or "") else 8),
        })
        if abs(rotation) in (90, 270):
            info["display_width"], info["display_height"] = info["height"], info["width"]
        else:
            info["display_width"], info["display_height"] = info["width"], info["height"]
    if a:
        info.update({"acodec": a.get("codec_name"), "sample_rate": int(a.get("sample_rate") or 0),
                     "channels": a.get("channels"), "channel_layout": a.get("channel_layout")})
    return info


def is_image(path: str | Path) -> bool:
    return Path(path).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic", ".avif"}


def ffmpeg_filters() -> str:
    proc = run(["ffmpeg", "-hide_banner", "-filters"], capture=True, check=False)
    return proc.stdout or ""


def has_filter(name: str, _cache: dict = {}) -> bool:
    if "list" not in _cache:
        _cache["list"] = ffmpeg_filters()
    return re.search(rf"^\s*\S+\s+{re.escape(name)}\s", _cache["list"], re.M) is not None


def parse_size(text: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)[x:](\d+)", text.strip())
    if not m:
        raise ValueError(f"Expected WxH, got {text!r}")
    return int(m.group(1)), int(m.group(2))


def fmt_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}" if h else f"{int(m)}:{s:05.2f}"


def write_json(path: str | Path, data) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def open_path(path: str | Path) -> None:
    """Open a file with the OS default app (used for review pages)."""
    p = str(Path(path).resolve())
    if sys.platform.startswith("win"):
        os.startfile(p)  # noqa: S606 - opening a local file the user asked for
    elif sys.platform == "darwin":
        subprocess.Popen(["open", p])
    else:
        subprocess.Popen(["xdg-open", p])
