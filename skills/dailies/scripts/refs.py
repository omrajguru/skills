#!/usr/bin/env python3
"""Browse the reference image library and print credits for anything shown to the user.

    python scripts/refs.py list
    python scripts/refs.py match "explain economics with maps, playful"
    python scripts/refs.py fetch 05            # download one style's images and build its contact sheet
    python scripts/refs.py fetch --all
    python scripts/refs.py board 05            # path to the contact sheet (fetches first if needed)
    python scripts/refs.py show 01-vox-style-video-essays
    python scripts/refs.py credits 01-vox-style-video-essays/05-parking-blueprint-graphic.jpg [more files...]

The images are not distributed with the skill. `fetch` downloads each one from the
direct image URL recorded in image/sources.json, on the user's machine, the same way
a browser would when visiting the source page. Credits come from the same file. They
are for telling the user where a reference came from; they never go into a rendered video.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _media import SKILL_DIR  # noqa: E402

LIB = SKILL_DIR / "image"

# Words a brief might use, mapped to each style folder (by number prefix).
KEYWORDS = {
    "01": "explainer explain essay vox news politics economics policy history map maps diagram infographic annotation archival editorial journalism data argument",
    "02": "cinematic film movie essay criticism analysis composition symmetry split screen letterbox poetic art cinema director",
    "03": "talking head presenter youtube creator vlog explainer camera studio interview face host educational",
    "04": "storyboard animatic pitch film previs color script boards sketch pre-production shot planning",
    "05": "collage mixed media paper torn cutout halftone music video energetic retro zine texture punk art",
    "06": "typography kinetic type text quote lyric lyrics title motion poster bold words promo festival",
    "07": "screencast screen recording demo product saas software app tutorial walkthrough ui onboarding feature launch",
    "08": "gaming game gameplay let's play stream twitch facecam esports speedrun highlights",
    "09": "pov first person gopro cooking cycling travel action sports hands vlog immersive",
    "10": "reaction commentary react review podcast clip picture in picture duet analysis",
    "11": "lofi lo-fi ambient calm cozy rain loop study relax aesthetic background broll b-roll mood coffee",
}


def load_sources() -> list[dict]:
    path = LIB / "sources.json"
    if not path.exists():
        sys.exit(f"Missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def style_folders() -> list[Path]:
    return sorted(p for p in LIB.iterdir() if p.is_dir() and re.match(r"\d\d-", p.name))


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
MAX_BYTES = 40 * 1024 * 1024
MAX_SIDE = 3000


def download_image(entry: dict, dest: Path) -> str | None:
    """Download one reference and save it as JPEG. Returns an error message, or None on success."""
    try:
        from PIL import Image
    except ImportError:
        return "Pillow is required: python -m pip install Pillow"
    url = entry.get("url")
    if not url or not url.startswith("https://"):
        return "no https image URL recorded"
    # No AVIF in Accept: many CDNs negotiate it, and Pillow often can't decode it.
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/webp,image/jpeg,image/png,image/gif;q=0.9,*/*;q=0.5",
                                               "Referer": entry.get("source") or url})
    data, last_error = None, None
    for _ in range(2):  # one retry for slow hosts
        try:
            with urllib.request.urlopen(req, timeout=45) as res:
                data = res.read(MAX_BYTES + 1)
            break
        except Exception as e:  # network errors, 403/404 from hosts that moved the file
            last_error = e
    if data is None:
        return f"download failed ({last_error.__class__.__name__}: {last_error})"
    if len(data) > MAX_BYTES:
        return "file too large"
    try:
        im = Image.open(io.BytesIO(data))
        im.seek(0)  # animated GIFs: use the first frame
        im = im.convert("RGB")
    except Exception as e:
        return f"not a readable image ({e.__class__.__name__})"
    im.thumbnail((MAX_SIDE, MAX_SIDE))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=90)
    return None


def build_board(folder: str, entries: list[dict], images_root: Path, out: Path) -> Path | None:
    """Two-column contact sheet with number, slug and creator under each image."""
    from PIL import Image, ImageDraw, ImageFont
    cells = [(e, images_root / e["file"]) for e in entries if (images_root / e["file"]).exists()]
    if not cells:
        return None
    W, cols, pad, cell_w, cell_h, label_h, head = 1600, 2, 18, 772, 434, 56, 64
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (W, head + rows * (cell_h + label_h + pad) + pad), (17, 18, 20))
    draw = ImageDraw.Draw(sheet)
    try:
        title_font, font, small = (ImageFont.truetype("arial.ttf", s) for s in (30, 20, 16))
    except OSError:
        title_font = font = small = ImageFont.load_default()
    draw.text((pad + 10, 18), folder.split("-", 1)[1].replace("-", " ").upper() if "-" in folder else folder, fill=(240, 240, 240), font=title_font)
    for i, (e, img_path) in enumerate(cells):
        r, c = divmod(i, cols)
        x, y = pad + c * (cell_w + pad), head + r * (cell_h + label_h + pad)
        im = Image.open(img_path).convert("RGB")
        im.thumbnail((cell_w, cell_h))
        sheet.paste(im, (x + (cell_w - im.width) // 2, y + (cell_h - im.height) // 2))
        name = Path(e["file"]).stem
        draw.text((x, y + cell_h + 6), name.replace("-", "  ", 1), fill=(235, 235, 235), font=font)
        credit = (e.get("creator_credit") or "").split(";")[0][:90]
        draw.text((x, y + cell_h + 32), credit, fill=(150, 150, 150), font=small)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=85)
    return out


def fetch_style(folder: str, sources: list[dict], force: bool = False, dest_root: Path | None = None) -> tuple[int, list[str]]:
    root = dest_root or LIB
    entries = [e for e in sources if e.get("folder") == folder]
    todo = [e for e in entries if force or not (root / e["file"]).exists()]
    ok, failures = len(entries) - len(todo), []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for e, err in zip(todo, pool.map(lambda x: download_image(x, root / x["file"]), todo)):
            if err:
                failures.append(f"{e['file']}: {err}. Source page: {e.get('source')}")
            else:
                ok += 1
    build_board(folder, entries, root, root / "_boards" / f"{folder}.jpg")
    return ok, failures


def resolve_style(token: str) -> Path:
    for p in style_folders():
        if p.name == token or p.name.startswith(token.zfill(2) + "-") or p.name.startswith(token):
            return p
    sys.exit(f"No style folder matches {token!r}. Try: refs.py list")


def credit_line(entry: dict) -> str:
    creator = entry.get("creator_credit") or "creator not established"
    title = entry.get("title") or ""
    src = entry.get("source") or entry.get("url") or ""
    rtype = entry.get("reference_type") or ""
    ai = " (marked AI-generated by its source)" if "ai-generated" in (title + creator + rtype).lower() else ""
    return f"{entry['file']}: {creator}. \"{title}\". Source: {src}{ai}"


def cmd_list(_: argparse.Namespace) -> None:
    sources = load_sources()
    for p in style_folders():
        total = sum(1 for e in sources if e.get("folder") == p.name)
        have = len(list(p.glob("*.jpg")))
        board = LIB / "_boards" / f"{p.name}.jpg"
        state = f"board: {board}" if board.exists() else "not downloaded yet (refs.py fetch)"
        print(f"{p.name:40s} {have:2d}/{total} images   {state}")
    print(f"\nStyle notes: {SKILL_DIR / 'references' / 'style-library.md'}")


def cmd_fetch(args: argparse.Namespace) -> None:
    sources = load_sources()
    folders = [p.name for p in style_folders()] if args.all else [resolve_style(s).name for s in args.styles]
    if not folders:
        sys.exit("Name one or more styles, or pass --all.")
    dest = Path(args.dest).resolve() if args.dest else None
    any_fail = False
    for folder in folders:
        ok, failures = fetch_style(folder, sources, args.force, dest)
        total = sum(1 for e in sources if e.get("folder") == folder)
        board = (dest or LIB) / "_boards" / f"{folder}.jpg"
        print(f"{folder}: {ok}/{total} images" + (f", board: {board}" if board.exists() else ""))
        for f in failures:
            any_fail = True
            print(f"  unavailable  {f}")
    if any_fail:
        print("\nUnavailable references can still be described from references/style-library.md and linked by their source page.")


def cmd_match(args: argparse.Namespace) -> None:
    words = set(re.findall(r"[a-z0-9']+", args.text.lower()))
    sources = load_sources()
    scored = []
    for p in style_folders():
        num = p.name[:2]
        vocab = set(KEYWORDS.get(num, "").split()) | set(p.name.split("-")[1:])
        titles = " ".join((e.get("title") or "") + " " + e["file"] for e in sources if e.get("folder") == p.name).lower()
        score = sum(3 for w in words if w in vocab) + sum(1 for w in words if len(w) > 3 and w in titles)
        scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    top = [s for s in scored if s[0] > 0][: args.top] or scored[: args.top]
    for score, p in top:
        print(f"{p.name:40s} score {score:2d}   board: {LIB / '_boards' / (p.name + '.jpg')}")
    if not any(s for s, _ in scored):
        print("\nNo keyword overlap. Read references/style-library.md and choose by judgment, or design from first principles.")


def cmd_board(args: argparse.Namespace) -> None:
    p = resolve_style(args.style)
    board = LIB / "_boards" / f"{p.name}.jpg"
    if not board.exists():
        fetch_style(p.name, load_sources())
    if not board.exists():
        sys.exit(f"No images could be downloaded for {p.name}; describe it from references/style-library.md instead.")
    print(board)


def cmd_show(args: argparse.Namespace) -> None:
    p = resolve_style(args.style)
    by_file = {e["file"]: e for e in load_sources()}
    for e in (x for x in by_file.values() if x.get("folder") == p.name):
        img = LIB / e["file"]
        print(img if img.exists() else f"{img}  (not downloaded; refs.py fetch {p.name[:2]})")
        print("   " + credit_line(e).split(": ", 1)[1])


def cmd_credits(args: argparse.Namespace) -> None:
    by_file = {e["file"]: e for e in load_sources()}
    missing = 0
    for f in args.files:
        rel = Path(f).as_posix()
        if rel.startswith(LIB.as_posix()):
            rel = rel[len(LIB.as_posix()) + 1:]
        rel = rel.split("image/", 1)[-1]
        if rel.startswith("_boards/"):
            folder = Path(rel).stem
            print(f"{rel}: contact sheet of {folder}; credit each image shown on it:")
            for e in (x for x in by_file.values() if x.get("folder") == folder):
                print("  " + credit_line(e))
            continue
        e = by_file.get(rel)
        if e:
            print(credit_line(e))
        else:
            missing += 1
            print(f"{rel}: no entry in sources.json")
    if args.json:
        print(json.dumps([by_file.get(Path(f).as_posix().split("image/", 1)[-1]) for f in args.files], indent=2, ensure_ascii=False))
    sys.exit(1 if missing else 0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    m = sub.add_parser("match")
    m.add_argument("text")
    m.add_argument("--top", type=int, default=3)
    m.set_defaults(fn=cmd_match)
    f = sub.add_parser("fetch")
    f.add_argument("styles", nargs="*")
    f.add_argument("--all", action="store_true")
    f.add_argument("--force", action="store_true", help="download again even if the file exists")
    f.add_argument("--dest", help="download somewhere other than the skill's image folder")
    f.set_defaults(fn=cmd_fetch)
    b = sub.add_parser("board")
    b.add_argument("style")
    b.set_defaults(fn=cmd_board)
    s = sub.add_parser("show")
    s.add_argument("style")
    s.set_defaults(fn=cmd_show)
    c = sub.add_parser("credits")
    c.add_argument("files", nargs="+")
    c.add_argument("--json", action="store_true")
    c.set_defaults(fn=cmd_credits)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
