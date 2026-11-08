#!/usr/bin/env python3
"""Generate simple, royalty-free sound effects procedurally (no samples involved).

    python scripts/sfx.py list
    python scripts/sfx.py whoosh --duration 0.6 --out audio/sfx/whoosh.wav
    python scripts/sfx.py ding --pitch 880 --gain -3 --out audio/sfx/ding.wav

Sounds: whoosh, riser, swell, pop, click, tick, impact, ding, room, rain.
Every sound takes --seed for variations, --gain in dB, and --duration where it makes sense.
Pure Python (standard library only); output is 48 kHz 16-bit stereo WAV.
"""
from __future__ import annotations

import argparse
import math
import random
import struct
import sys
import wave
from pathlib import Path

SR = 48000


def noise(n: int, rng: random.Random) -> list[float]:
    return [rng.uniform(-1.0, 1.0) for _ in range(n)]


def lowpass(x: list[float], cutoffs) -> list[float]:
    """One-pole low-pass; cutoffs is a float or a per-sample sequence in Hz."""
    out, y = [], 0.0
    per_sample = not isinstance(cutoffs, (int, float))
    for i, s in enumerate(x):
        fc = cutoffs[i] if per_sample else cutoffs
        a = 1 - math.exp(-2 * math.pi * fc / SR)
        y += a * (s - y)
        out.append(y)
    return out


def highpass(x: list[float], fc: float) -> list[float]:
    lp = lowpass(x, fc)
    return [a - b for a, b in zip(x, lp)]


def envelope(n: int, attack: float, release: float, curve: float = 2.0) -> list[float]:
    a, r = max(1, int(attack * SR)), max(1, int(release * SR))
    env = []
    for i in range(n):
        if i < a:
            v = (i / a) ** curve
        elif i > n - r:
            v = ((n - i) / r) ** curve
        else:
            v = 1.0
        env.append(v)
    return env


def normalize(x: list[float], peak: float = 0.89) -> list[float]:
    m = max((abs(v) for v in x), default=0) or 1.0
    return [v * peak / m for v in x]


def whoosh(d: float, rng: random.Random, **_) -> list[float]:
    n = int(d * SR)
    # band of noise sweeping up then down, loudest at ~60% (where the motion peaks)
    cut = [400 + 5200 * math.sin(math.pi * min(1, i / n)) ** 1.5 for i in range(n)]
    x = highpass(lowpass(noise(n, rng), cut), 180)
    env = [math.sin(math.pi * (i / n) ** 0.8) ** 2 for i in range(n)]
    return [a * b for a, b in zip(x, env)]


def riser(d: float, rng: random.Random, **_) -> list[float]:
    n = int(d * SR)
    cut = [300 + 9000 * (i / n) ** 2 for i in range(n)]
    x = lowpass(noise(n, rng), cut)
    tone = [0.35 * math.sin(2 * math.pi * (120 * t + 260 * t * t / d)) for t in (i / SR for i in range(n))]
    env = [(i / n) ** 2.2 for i in range(n)]
    return [(a + b) * e for a, b, e in zip(x, tone, env)]


def swell(d: float, rng: random.Random, pitch: float = 110.0, **_) -> list[float]:
    n = int(d * SR)
    out = []
    for i in range(n):
        t = i / SR
        v = sum(math.sin(2 * math.pi * pitch * h * t + rng.random() * 0.0) / h for h in (1, 1.5, 2, 3))
        out.append(v)
    env = [math.sin(math.pi * i / n) ** 1.5 for i in range(n)]
    return lowpass([a * b for a, b in zip(out, env)], 1800)


def pop(d: float, rng: random.Random, pitch: float = 520.0, **_) -> list[float]:
    d = min(d, 0.25)
    n = int(d * SR)
    out = []
    for i in range(n):
        t = i / SR
        f = pitch * (1 + 1.6 * math.exp(-t * 60))
        out.append(math.sin(2 * math.pi * f * t) * math.exp(-t * 38))
    return out


def click(d: float, rng: random.Random, **_) -> list[float]:
    n = int(0.03 * SR)
    x = highpass(noise(n, rng), 2000)
    return [v * math.exp(-i / SR * 320) for i, v in enumerate(x)]


def tick(d: float, rng: random.Random, pitch: float = 2400.0, **_) -> list[float]:
    n = int(0.05 * SR)
    return [math.sin(2 * math.pi * pitch * i / SR) * math.exp(-i / SR * 140) for i in range(n)]


def impact(d: float, rng: random.Random, pitch: float = 55.0, **_) -> list[float]:
    d = max(d, 0.8)
    n = int(d * SR)
    body = []
    for i in range(n):
        t = i / SR
        f = pitch * (1 + 2.5 * math.exp(-t * 18))
        body.append(math.sin(2 * math.pi * f * t) * math.exp(-t * 4.5))
    crack = lowpass(noise(n, rng), 3500)
    crack = [v * math.exp(-i / SR * 30) * 0.6 for i, v in enumerate(crack)]
    return [a + b for a, b in zip(body, crack)]


def ding(d: float, rng: random.Random, pitch: float = 880.0, **_) -> list[float]:
    d = max(d, 1.2)
    n = int(d * SR)
    partials = [(1.0, 1.0, 2.2), (2.76, 0.45, 3.5), (5.4, 0.25, 6.0), (8.93, 0.12, 9.0)]  # bell-like ratios
    out = []
    for i in range(n):
        t = i / SR
        out.append(sum(a * math.sin(2 * math.pi * pitch * r * t) * math.exp(-t * dec) for r, a, dec in partials) * min(1, t * 400))
    return out


def room(d: float, rng: random.Random, **_) -> list[float]:
    n = int(d * SR)
    x = lowpass(noise(n, rng), 900)
    x = highpass(x, 40)
    return [v * 0.3 for v in x]


def rain(d: float, rng: random.Random, **_) -> list[float]:
    n = int(d * SR)
    bed = highpass(lowpass(noise(n, rng), 6000), 400)
    bed = [v * 0.25 for v in bed]
    for _ in range(int(d * 90)):  # individual drops
        at = rng.randrange(0, max(1, n - 2000))
        f = rng.uniform(1800, 5200)
        amp = rng.uniform(0.05, 0.25)
        for k in range(1200):
            bed[at + k] += amp * math.sin(2 * math.pi * f * k / SR) * math.exp(-k / SR * 160)
    return bed


SOUNDS = {
    "whoosh": (whoosh, 0.6, "air movement for things flying in or out"),
    "riser": (riser, 2.0, "build-up into a reveal"),
    "swell": (swell, 3.0, "soft tonal swell under a title"),
    "pop": (pop, 0.15, "element appears"),
    "click": (click, 0.03, "UI click, cursor"),
    "tick": (tick, 0.05, "counter, timer, list item"),
    "impact": (impact, 1.0, "something lands, a hard cut, a big number"),
    "ding": (ding, 1.5, "notification, success, chapter"),
    "room": (room, 10.0, "room tone to fill gaps"),
    "rain": (rain, 10.0, "rain ambience for lo-fi pieces"),
}


def write_wav(path: Path, mono: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for v in mono:
            s = int(max(-1.0, min(1.0, v)) * 32767)
            frames += struct.pack("<hh", s, s)
        w.writeframes(bytes(frames))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sound", choices=["list", *SOUNDS])
    ap.add_argument("--duration", type=float)
    ap.add_argument("--pitch", type=float)
    ap.add_argument("--gain", type=float, default=0.0, help="dB relative to a -1 dBFS peak")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out")
    args = ap.parse_args()

    if args.sound == "list":
        for name, (_, d, desc) in SOUNDS.items():
            print(f"{name:8s} default {d:>4}s  {desc}")
        return
    fn, default_d, _ = SOUNDS[args.sound]
    rng = random.Random(args.seed)
    kwargs = {"pitch": args.pitch} if args.pitch else {}
    x = normalize(fn(args.duration or default_d, rng, **kwargs))
    g = 10 ** (args.gain / 20)
    x = [v * g for v in x]
    # 5 ms fades so nothing clicks at the edges
    f = int(0.005 * SR)
    for i in range(min(f, len(x))):
        x[i] *= i / f
        x[-1 - i] *= i / f
    out = Path(args.out or f"{args.sound}.wav")
    write_wav(out, x)
    print(out)


if __name__ == "__main__":
    sys.exit(main())
