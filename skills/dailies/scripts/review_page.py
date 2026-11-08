#!/usr/bin/env python3
"""Build a local review page for an approval step: styleframes or mockups, design
variants, the references that shaped them (with credits), notes and questions.

    python scripts/review_page.py review/manifest.json --open

manifest.json (paths relative to the manifest):
{
  "title": "Parking explainer",
  "step": "Styleframes",
  "summary": "Three moments from the 45 s cut, in the approved blueprint direction.",
  "sections": [
    {"heading": "Styleframes", "items": [
      {"image": "frames/t1.00.png", "caption": "0:01 hook"},
      {"video": "../renders/v1/draft.mp4", "caption": "Animatic, half resolution"}
    ]},
    {"heading": "Direction A vs B", "layout": "compare", "items": [
      {"image": "frames/a/t6.50.png", "caption": "A: editorial serif on paper"},
      {"image": "frames/b/t6.50.png", "caption": "B: grotesque on black, one shock color"}
    ]}
  ],
  "references": ["01-vox-style-video-essays/05-parking-blueprint-graphic.jpg"],
  "questions": ["Is the accent too strong on the map frame?"]
}

References are shown with their credits from image/sources.json. The page is for
the user only; nothing on it goes into the video.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _media import SKILL_DIR, open_path  # noqa: E402

CSS = """
:root { color-scheme: light dark; --bg:#f6f6f4; --fg:#151515; --muted:#6b6b6b; --line:#dcdcd8; --card:#fff; }
@media (prefers-color-scheme: dark) { :root { --bg:#0e0e0f; --fg:#ededed; --muted:#9a9a9a; --line:#2a2a2c; --card:#161618; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width:1280px; margin:0 auto; padding:40px 24px 80px; }
header p { color:var(--muted); margin:6px 0 0; max-width:70ch; }
.step { font:600 13px/1 ui-monospace, monospace; color:var(--muted); letter-spacing:.04em; }
h1 { font-size:34px; line-height:1.1; margin:10px 0 0; letter-spacing:-.01em; }
h2 { font-size:20px; margin:44px 0 14px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(360px, 1fr)); gap:18px; }
.grid.compare { grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); }
figure { margin:0; background:var(--card); border:1px solid var(--line); border-radius:12px; overflow:hidden; }
figure img, figure video { display:block; width:100%; height:auto; background:#000; cursor:zoom-in; }
figcaption { padding:10px 14px 12px; font-size:14px; }
figcaption .note { color:var(--muted); display:block; margin-top:2px; }
.refs figcaption { font-size:13px; }
.refs a { color:inherit; }
ol.q { padding-left:20px; } ol.q li { margin:6px 0; }
.disclaimer { margin-top:48px; color:var(--muted); font-size:13px; max-width:80ch; }
dialog { border:0; padding:0; background:transparent; max-width:96vw; max-height:96vh; }
dialog img { max-width:96vw; max-height:96vh; display:block; }
dialog::backdrop { background:rgba(0,0,0,.85); }
"""

JS = """
const d = document.querySelector('dialog'), di = d.querySelector('img');
document.querySelectorAll('figure img').forEach(i => i.addEventListener('click', () => { di.src = i.src; d.showModal(); }));
d.addEventListener('click', () => d.close());
"""


def rel_src(target: Path, page_dir: Path) -> str:
    try:
        return Path(os.path.relpath(target, page_dir)).as_posix()
    except ValueError:  # different drive on Windows
        return target.resolve().as_uri()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("--out", help="output html (default: index.html next to the manifest)")
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    mpath = Path(args.manifest).resolve()
    m = json.loads(mpath.read_text(encoding="utf-8"))
    base = mpath.parent
    out = Path(args.out).resolve() if args.out else base / "index.html"
    page_dir = out.parent
    esc = html.escape
    parts = [f"<header><div class='step'>{esc(m.get('step', 'Review'))}</div><h1>{esc(m.get('title', 'Review'))}</h1>"]
    if m.get("summary"):
        parts.append(f"<p>{esc(m['summary'])}</p>")
    parts.append("</header>")

    missing = []
    for sec in m.get("sections", []):
        parts.append(f"<h2>{esc(sec.get('heading', ''))}</h2><div class='grid {esc(sec.get('layout', ''))}'>")
        for it in sec.get("items", []):
            media = ""
            if it.get("image"):
                f = (base / it["image"]).resolve()
                if not f.exists():
                    missing.append(str(f))
                media = f"<img loading='lazy' src='{esc(rel_src(f, page_dir))}' alt='{esc(it.get('caption', ''))}'>"
            elif it.get("video"):
                f = (base / it["video"]).resolve()
                if not f.exists():
                    missing.append(str(f))
                media = f"<video controls preload='metadata' src='{esc(rel_src(f, page_dir))}'></video>"
            cap = esc(it.get("caption", ""))
            note = f"<span class='note'>{esc(it['note'])}</span>" if it.get("note") else ""
            parts.append(f"<figure>{media}<figcaption>{cap}{note}</figcaption></figure>")
        parts.append("</div>")

    refs = m.get("references") or []
    if refs:
        sources = {e["file"]: e for e in json.loads((SKILL_DIR / "image" / "sources.json").read_text(encoding="utf-8"))}
        parts.append("<h2>References that shaped this direction</h2><div class='grid refs'>")
        for r in refs:
            f = SKILL_DIR / "image" / r
            e = sources.get(r, {})
            credit = esc(e.get("creator_credit") or "Creator not established")
            title = esc(e.get("title") or "")
            src = e.get("source") or ""
            link = f"<a href='{esc(src)}' target='_blank' rel='noopener'>{esc(src.split('//')[-1].split('/')[0] or 'source')}</a>" if src else ""
            parts.append(f"<figure><img loading='lazy' src='{esc(rel_src(f, page_dir))}' alt='reference'><figcaption>{credit}<span class='note'>{title} · {link}</span></figcaption></figure>")
        parts.append("</div>")

    if m.get("questions"):
        parts.append("<h2>Questions</h2><ol class='q'>" + "".join(f"<li>{esc(q)}</li>" for q in m["questions"]) + "</ol>")
    if refs:
        parts.append("<p class='disclaimer'>Reference images are shown for direction only and credited to their creators. "
                     "They are not used in the video, and none of their credits or content appear in it.</p>")

    doc = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
           f"<title>{esc(m.get('title', 'Review'))}</title><style>{CSS}</style></head><body><main>{''.join(parts)}</main>"
           f"<dialog><img alt=''></dialog><script>{JS}</script></body></html>")
    out.write_text(doc, encoding="utf-8")
    print(out)
    for f in missing:
        hint = "  (reference not downloaded yet: run scripts/refs.py fetch)" if "image" in Path(f).parts else ""
        print(f"  missing: {f}{hint}", file=sys.stderr)
    if args.open:
        open_path(out)


if __name__ == "__main__":
    main()
