#!/usr/bin/env python3
"""Check the toolchain the dailies skill relies on and print how to install what is missing.

    python scripts/doctor.py
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _media import SKILL_DIR, has_filter  # noqa: E402

PLATFORM = "windows" if sys.platform.startswith("win") else "mac" if sys.platform == "darwin" else "linux"

INSTALL = {
    "ffmpeg": {"windows": "winget install Gyan.FFmpeg   (the 'full' build includes libass, vidstab, zimg)",
               "mac": "brew install ffmpeg", "linux": "sudo apt install ffmpeg   (or your distro's package)"},
    "node": {"windows": "winget install OpenJS.NodeJS.LTS", "mac": "brew install node", "linux": "install Node 18+ from nodejs.org or your package manager"},
    "playwright-core": {"all": ""},  # filled in by playwright_hint()
    "browser": {"all": "install Google Chrome or Microsoft Edge, or run: npx playwright install chromium"},
    "Pillow": {"all": "python -m pip install Pillow"},
    "whisper": {"all": "python -m pip install faster-whisper   (or openai-whisper, or whisper.cpp's whisper-cli)"},
}


def package_root() -> Path | None:
    """The repository or plugin root that ships package.json, when the skill sits inside one."""
    for parent in (SKILL_DIR, *SKILL_DIR.parents):
        if (parent / "package.json").exists() and (parent / "package-lock.json").exists():
            return parent
    return None


def find_playwright() -> Path | None:
    # Node resolves packages by walking up from the script, so any ancestor's node_modules works.
    for parent in (SKILL_DIR / "scripts", *SKILL_DIR.parents, SKILL_DIR):
        candidate = parent / "node_modules" / "playwright-core"
        if candidate.exists():
            return candidate
    return None


def playwright_hint() -> str:
    root = package_root()
    if root:
        return f"cd \"{root}\" && npm install"
    # Installed as a bare skill folder (no package.json alongside it).
    return f"npm install --prefix \"{SKILL_DIR}\" playwright-core@1.64.1"


def hint(key: str) -> str:
    if key == "playwright-core":
        return playwright_hint()
    table = INSTALL[key]
    return table.get(PLATFORM) or table.get("all", "")


def version(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def find_browser() -> str | None:
    candidates = {
        "windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"],
        "mac": ["/Applications/Google Chrome.app", "/Applications/Microsoft Edge.app", "/Applications/Chromium.app"],
        "linux": [],
    }[PLATFORM]
    for c in candidates:
        if Path(c).exists():
            return c
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"):
        if shutil.which(name):
            return shutil.which(name)
    pw_cache = Path.home() / ("AppData/Local/ms-playwright" if PLATFORM == "windows" else "Library/Caches/ms-playwright" if PLATFORM == "mac" else ".cache/ms-playwright")
    if pw_cache.exists() and any(pw_cache.glob("chromium*")):
        return str(pw_cache)
    return None


def main() -> int:
    rows: list[tuple[str, bool, str, str]] = []  # name, ok, detail, fix
    required_ok = True

    def check(name: str, ok: bool, detail: str, fix_key: str | None, required: bool) -> None:
        nonlocal required_ok
        rows.append((name + ("" if required else " (optional)"), ok, detail, "" if ok or not fix_key else hint(fix_key)))
        if required and not ok:
            required_ok = False

    ff = version(["ffmpeg", "-version"])
    check("ffmpeg", bool(ff), ff or "not found", "ffmpeg", True)
    fp = version(["ffprobe", "-version"])
    check("ffprobe", bool(fp), fp or "not found", "ffmpeg", True)
    if ff:
        for flt, why in (("ass", "burned-in captions"), ("vidstabdetect", "stabilization"), ("zscale", "HDR tone-mapping"),
                         ("loudnorm", "loudness normalization"), ("sidechaincompress", "music ducking")):
            check(f"ffmpeg filter '{flt}'", has_filter(flt), f"for {why}", "ffmpeg", flt in ("loudnorm", "sidechaincompress"))

    nd = version(["node", "--version"])
    check("node", bool(nd), nd or "not found", "node", True)
    pw = find_playwright()
    check("playwright-core", bool(pw), str(pw.parent.parent) if pw else "not installed", "playwright-core", True)
    br = find_browser()
    check("Chromium-family browser", bool(br), br or "not found", "browser", True)

    pil = importlib.util.find_spec("PIL") is not None
    check("Pillow", pil, "contact sheets, review images", "Pillow", True)

    whisper = next((n for n in ("faster_whisper", "whisper") if importlib.util.find_spec(n)), None)
    wcpp = shutil.which("whisper-cli") or shutil.which("whisper-cpp")
    check("speech-to-text", bool(whisper or wcpp), whisper or wcpp or "none (captions and word sync need it)", "whisper", False)
    for mod, why in (("librosa", "beat detection"), ("mediapipe", "face tracking for reframing"), ("rembg", "background removal")):
        check(mod, importlib.util.find_spec(mod) is not None, why, None, False)
    for exe, why in (("piper", "local TTS"),):
        check(exe, bool(shutil.which(exe)), why, None, False)

    width = max(len(r[0]) for r in rows)
    for name, ok, detail, fix in rows:
        mark = "ok " if ok else "-- "
        print(f"{mark} {name.ljust(width)}  {detail}")
        if fix:
            print(f"    {''.ljust(width)}  install: {fix}")
    print()
    print("Ready." if required_ok else "Some required tools are missing; install them before rendering.")
    return 0 if required_ok else 1


if __name__ == "__main__":
    sys.exit(main())
