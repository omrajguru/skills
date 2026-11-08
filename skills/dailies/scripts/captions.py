#!/usr/bin/env python3
"""Turn a word-level transcript into captions: an .srt sidecar and a styled .ass to burn in.

    python scripts/captions.py transcript.json --style sentence --res 1920x1080 --out footage/captions
    python scripts/captions.py transcript.json --style words --res 1080x1920 --highlight "#FFD54A" --out footage/captions

transcript.json is the format ingest.py writes: {"segments": [{"start","end","text","words":[{"word","start","end"}]}]}.
Colors are #RRGGBB. Fonts must be installed or passed to assemble.py via captions.fonts_dir.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _media import parse_size  # noqa: E402


def srt_time(t: float) -> str:
    t = max(0.0, t)
    h, rem = divmod(int(round(t * 1000)), 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ass_time(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_color(hex_color: str, alpha: int = 0) -> str:
    """#RRGGBB -> &HAABBGGRR (ASS stores blue-green-red with inverted alpha)."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Expected #RRGGBB, got {hex_color}")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def load_words(path: Path, offset: float) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    words = []
    for seg in data.get("segments", []):
        seg_words = seg.get("words") or []
        if not seg_words:  # segment-level only: spread words evenly
            toks = seg["text"].split()
            dur = (seg["end"] - seg["start"]) / max(1, len(toks))
            seg_words = [{"word": w, "start": seg["start"] + i * dur, "end": seg["start"] + (i + 1) * dur} for i, w in enumerate(toks)]
        for w in seg_words:
            text = w["word"].strip()
            if text:
                words.append({"word": text, "start": w["start"] + offset, "end": w["end"] + offset})
    return words


def group_sentences(words: list[dict], max_chars: int, max_lines: int, max_gap: float) -> list[list[dict]]:
    """Caption blocks of up to max_lines lines, breaking at punctuation and pauses."""
    groups, cur = [], []
    limit = max_chars * max_lines
    for w in words:
        text_len = len(" ".join(x["word"] for x in cur + [w]))
        gap = w["start"] - cur[-1]["end"] if cur else 0
        if cur and (text_len > limit or gap > max_gap):
            groups.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.!?]$", w["word"]) and len(" ".join(x["word"] for x in cur)) > max_chars * 0.5:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def group_words(words: list[dict], max_words: int, max_gap: float) -> list[list[dict]]:
    groups, cur = [], []
    for w in words:
        gap = w["start"] - cur[-1]["end"] if cur else 0
        if cur and (len(cur) >= max_words or gap > max_gap or re.search(r"[.!?,]$", cur[-1]["word"])):
            groups.append(cur)
            cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    return groups


def wrap_lines(text: str, max_chars: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    # balance two lines so the bottom one is not a single orphan word
    if len(lines) == 2 and len(lines[1]) < len(lines[0]) * 0.4:
        words = text.split()
        best = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
        lines = [" ".join(words[:best]), " ".join(words[best:])]
    return lines


def ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript")
    ap.add_argument("--out", required=True, help="output path without extension")
    ap.add_argument("--style", choices=["sentence", "words"], default="sentence")
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--size", type=int, help="font size in px (default depends on --res and --style)")
    ap.add_argument("--bold", type=int, default=1)
    ap.add_argument("--color", default="#FFFFFF")
    ap.add_argument("--highlight", default="#FFD54A", help="current-word color for --style words")
    ap.add_argument("--outline-color", default="#000000")
    ap.add_argument("--outline", type=float, default=3)
    ap.add_argument("--shadow", type=float, default=0)
    ap.add_argument("--box", action="store_true", help="opaque box behind text instead of outline")
    ap.add_argument("--position", choices=["bottom", "center", "top"], default="bottom")
    ap.add_argument("--margin-v", type=int, help="vertical margin in px")
    ap.add_argument("--max-chars", type=int, default=42)
    ap.add_argument("--max-lines", type=int, default=2)
    ap.add_argument("--max-words", type=int, default=3)
    ap.add_argument("--max-gap", type=float, default=0.8, help="start a new caption after a pause this long")
    ap.add_argument("--uppercase", action="store_true")
    ap.add_argument("--offset", type=float, default=0.0, help="shift all times by this many seconds")
    args = ap.parse_args()

    W, H = parse_size(args.res)
    vertical = H > W
    words = load_words(Path(args.transcript), args.offset)
    if not words:
        sys.exit("Transcript has no words.")
    if args.uppercase:
        for w in words:
            w["word"] = w["word"].upper()

    size = args.size or (
        (round(H * 0.042) if vertical else round(H * 0.048)) if args.style == "sentence" else (round(W * 0.075) if vertical else round(H * 0.075)))
    if args.margin_v is not None:
        margin_v = args.margin_v
    elif args.position == "bottom":
        # 9:16 platforms cover the bottom ~22% with UI; sit just above it.
        margin_v = round(H * 0.26) if vertical else round(H * 0.07)
    elif args.position == "top":
        margin_v = round(H * 0.14) if vertical else round(H * 0.07)
    else:
        margin_v = 0
    align = {"bottom": 2, "center": 5, "top": 8}[args.position]
    margin_h = round(W * (0.08 if vertical else 0.1))

    groups = group_sentences(words, args.max_chars, args.max_lines, args.max_gap) if args.style == "sentence" else group_words(words, args.max_words, args.max_gap)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # SRT sidecar: always sentence-style blocks, which read best for accessibility.
    srt_groups = groups if args.style == "sentence" else group_sentences(words, args.max_chars, args.max_lines, args.max_gap)
    srt = []
    for i, g in enumerate(srt_groups, 1):
        text = " ".join(w["word"] for w in g)
        end = g[-1]["end"]
        if i < len(srt_groups):
            end = min(max(end, g[0]["start"] + 1.0), srt_groups[i][0]["start"] - 0.01)
        srt.append(f"{i}\n{srt_time(g[0]['start'])} --> {srt_time(end)}\n" + "\n".join(wrap_lines(text, args.max_chars)) + "\n")
    out.with_suffix(".srt").write_text("\n".join(srt), encoding="utf-8")

    border_style = 3 if args.box else 1
    back = ass_color("#000000", 0x60) if args.box else ass_color("#000000", 0x80)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{args.font},{size},{ass_color(args.color)},{ass_color(args.highlight)},{ass_color(args.outline_color)},{back},{-1 if args.bold else 0},0,0,0,100,100,0,0,{border_style},{args.outline},{args.shadow},{align},{margin_h},{margin_h},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    hl = ass_color(args.highlight)
    base = ass_color(args.color)
    for gi, g in enumerate(groups):
        next_start = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else None
        g_end = g[-1]["end"] + 0.15
        if next_start is not None:
            g_end = min(g_end, next_start)
        if args.style == "sentence":
            text = "\\N".join(ass_escape(l) for l in wrap_lines(" ".join(w["word"] for w in g), args.max_chars))
            events.append(f"Dialogue: 0,{ass_time(g[0]['start'])},{ass_time(g_end)},Default,,0,0,0,,{text}")
        else:
            # one event per word so the current word is highlighted while the group stays on screen
            for wi, w in enumerate(g):
                start = g[0]["start"] if wi == 0 else w["start"]
                end = g[wi + 1]["start"] if wi + 1 < len(g) else g_end
                parts = [(f"{{\\c{hl}}}" if i == wi else f"{{\\c{base}}}") + ass_escape(x["word"]) for i, x in enumerate(g)]
                events.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{' '.join(parts)}")
    out.with_suffix(".ass").write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    print(out.with_suffix(".srt"))
    print(out.with_suffix(".ass"))
    print(f"{len(groups)} caption blocks, {len(words)} words, style={args.style}, font {args.font} {size}px")


if __name__ == "__main__":
    main()
