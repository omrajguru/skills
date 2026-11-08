# Workflow A: motion graphics

How to build a video from nothing with an HTML composition: a deterministic web page that `scripts/render.mjs` captures frame by frame and encodes with ffmpeg.

HTML is the engine because you can write it fluently, it handles typography, SVG, canvas, WebGL, video, and every CSS effect, and it needs no license. Remotion or Motion Canvas are fine alternatives when the user already uses them (see the end of this file).

## Contents
- Scaffold a project
- The composition contract
- Runtime API
- Storyboard format
- Building scenes well
- Transitions
- Embedding images, video, charts, 3D, Lottie, GSAP
- UI motion vs video motion
- Rendering: stills, drafts, finals, partial ranges
- Performance
- Using Remotion or Motion Canvas instead

## Scaffold a project

```bash
mkdir -p <slug>/{assets/fonts,assets/incoming,audio,review/frames,renders}
cp -r <skill>/templates/composition <slug>/comp
```

`comp/` contains `index.html` (a working three-scene example to replace), `runtime.js` (don't edit it; it's shared) and `style.css`. Write `tokens.json` in `<slug>/` before building scenes.

To preview while building:

```bash
node <skill>/scripts/render.mjs <slug>/comp/index.html --serve
```

This prints a local URL. Open it in a browser, or in the built-in browser pane if the environment has one. Opening `index.html` directly from disk also works, but `tokens.json` and fonts only load when served. The preview has play/pause (space), a scrubber, frame stepping (← →), `?t=12.5` to jump to a time, and `?guides=1` for safe areas.

## The composition contract

A composition is a **pure function of time**. `render(t)` must put the page into the exact state for second `t`, whatever was rendered before. Never accumulate state between frames, never use `Date.now()`, `Math.random()` or CSS transitions/animations that run on the wall clock, and never wait on timers. Deterministic rendering is what makes styleframes match the final video, lets the renderer capture frames in any order, and allows partial re-renders.

- Use `Dailies.wiggle()` / `Dailies.noise()` for organic randomness. They're deterministic per time and seed.
- If you use a CSS animation, pause it and drive it from `t`: `el.style.animationDelay = -t + 's'` with `animation-play-state: paused`.
- A `<canvas>` must be redrawn from scratch for each `t`.
- Particles: derive each particle's position from `t` and its index (seeded), not from velocity integration across frames.

```html
<script src="runtime.js"></script>
<script>
const D = Dailies;
D.composition({
  width: 1920, height: 1080, fps: 30, duration: 24,
  async setup() { /* optional: load data, split text, build SVG */ },
  render(t) {
    const local = D.scene('#s1', t, 0, 6);
    if (local !== null) {
      D.animate('#s1 h1', local, [[0.2, { opacity: 0, y: 60 }], [0.9, { opacity: 1, y: 0 }, 'outExpo']]);
    }
    // ...
  },
});
</script>
```

## Runtime API

All functions are on `window.Dailies`. Time arguments are in seconds.

| Function | What it does |
|---|---|
| `composition({width, height, fps, duration, setup, render})` | Registers the composition and exposes `window.__dailies` for the renderer |
| `scene(el, t, start, end)` | Shows `el` only during `[start, end)`. Returns local time, or `null` when hidden |
| `kf(t, frames)` | Keyframe interpolation. `frames = [[time, {props}], [time, {props}, ease], …]`. Returns the values |
| `animate(el, t, frames)` | `apply(el, kf(t, frames))` |
| `apply(el, values)` | `x`, `y`, `scale`, `scaleX`, `scaleY`, `rotate`, `skewX` → transform; `opacity`; `blur` (px); `clip` (0..1 wipe from left); any other key is set as a style property |
| `range(t, start, dur)` | 0..1 progress, clamped |
| `ease.*` | `linear`, `in/out/inOut` `Quad/Cubic/Quart/Expo`, `outBack`, `inOutSine` |
| `spring(stiffness, damping)` or `'spring(170,18)'` | Physical spring easing that works in seconds |
| `draw(pathEl, p)` | SVG stroke draw-on, 0..1 |
| `typewriter(el, text, p)` | Reveals characters |
| `countUp(el, from, to, p, fmt?)` | Animated number |
| `split(el, 'word' or 'char')` | Wraps words or letters in spans once. Returns the spans for staggering |
| `stepped(t, rate)` | Quantizes time for a stop-motion feel (`stepped(t, 12)` ≈ on twos at 24 fps) |
| `wiggle(t, freq, amp, seed)`, `noise(x, seed)` | Deterministic organic motion |
| `clamp`, `lerp` | Math helpers |

Staggering a list:

```js
D.split('#s2 .headline', 'word').forEach((w, i) =>
  D.animate(w, local, [[0.3 + i * 0.06, { opacity: 0, y: 30 }], [0.8 + i * 0.06, { opacity: 1, y: 0 }, 'outCubic']]));
```

Media (`<video data-start>`) is covered under Embedding below. Query parameters: `?render=1` (used by the renderer), `?t=`, `?guides=1`, `?bg=<image>` (draws an image under the stage, used for footage mockups), `?alpha=1` (transparent background for overlays), and `?tokens=<file>`.

## Storyboard format

Write `storyboard.md` before you build. One block per scene:

```markdown
## 02 · The cost nobody sees (6.0–13.5 s)
- **On screen:** city block plan in blueprint linework; parking areas fill in accent color, count-up "31%"
- **VO:** "In most American downtowns, almost a third of the land is parking."
- **Motion:** lines draw on (1.2 s, outCubic); fills wipe in on "a third"; camera push-in 100→108%
- **Sound:** soft pencil-scratch texture under draw-on; low "thump" on the 31%
- **Reference principle:** blueprint linework + single accent (style 01, refs 05)
```

Add up the durations and check them against the target length and the VO timing. When there is a voiceover, scene timings come *from* the VO (see `audio.md` § Syncing to words), never the other way round.

## Building scenes well

- **One idea per scene, one focal point per frame.** The accent color goes on the focal point.
- **Every animation should explain something:** reveal in the order of the argument, connect related things with movement, and use scale for emphasis. If a move doesn't help understanding or feeling, cut it.
- **Hierarchy through time:** headline first, support 0.2–0.4 s later, detail last.
- **Hold:** after an entrance, hold still long enough to read (`words × 0.3 s + 1 s`). Viewers can't pause a social feed.
- **Camera:** a slow push-in (2–5% over a scene) keeps static frames alive. Wrap scene content in a `.camera` div and animate its scale and position.
- **Texture:** add grain to big gradients (it reduces banding after compression). The template has a `.grain` overlay driven by `--grain`.
- **Real text stays real text.** No text in images, so it stays sharp and editable.
- **Check at phone size:** shrink the preview to about 400 px wide and squint. If it doesn't read, it doesn't work.

## Transitions

Match the transition to the relationship between scenes:

| Relationship | Transition |
|---|---|
| Continuation of the same idea | Match cut or morph: a shared element moves into its new position |
| New chapter | Wipe or push with the accent color (0.6–0.8 s), or a hard cut on a beat |
| Zooming into detail | Scale through: the current frame zooms into an element that becomes the next scene |
| Contrast or reversal | Hard cut, often with a sound hit |
| Calm or mood pieces | Cross-dissolve of 1–2 s |

Implement a transition as overlapping scene ranges in `render(t)` (both scenes visible during the overlap) with complementary keyframes. Keep transitions on beat when there is music.

## Embedding images, video, charts, 3D, Lottie, GSAP

- **Images:** `<img>` in the composition. The runtime waits for decoding before the first frame. Use PNGs with alpha for cutouts.
- **Video clips inside a composition:** `<video src="../assets/clip.mp4" data-start="4" data-in="12.5" muted playsinline preload="auto">` plays source time 12.5 s at composition time 4 s (`data-rate` changes speed). The runtime seeks frame-exactly during render. Seeking is smoother with a constant frame rate and a dense keyframe interval (`-g 15`). Normalize clips with `ingest.py --normalize` first. Sound from embedded clips is *not* captured. Mix it separately (`audio.md`).
- **Charts / data:** D3 or plain SVG, computing all geometry from `t` (for example, animate a bar's height with `range(t, …)`). Load data in `setup()`.
- **3D:** three.js with `renderer.render(scene, camera)` inside `render(t)`, setting every object transform from `t`. Use `preserveDrawingBuffer: true`.
- **Lottie:** `lottie-web` with `autoplay: false`, then `anim.goToAndStop(t * 1000, false)` in `render(t)`.
- **GSAP:** build a timeline with `paused: true`, then `tl.seek(t)` in `render(t)`. GSAP is deterministic when driven this way.
- **Fonts and libraries:** keep them local in `assets/`. Renders should not depend on network access.

## UI motion vs video motion

Interface motion skills (Emil Kowalski's skills, `ui-skills`, `apple-design`) teach excellent judgment about easing, choreography and restraint. Their timing assumes a person who *triggered* the motion and is waiting for the interface. A video viewer triggered nothing and must follow along, so translate them:

| UI principle | In video |
|---|---|
| UI transitions 150–300 ms | Entrances 400–600 ms, hero moves 700–1000 ms |
| Motion should never block the user | Motion should never outrun comprehension: hold after it lands |
| Ease-out for responsiveness | Still true for entrances. Ease-in-out for anything travelling across the frame |
| Springs for interruptible gestures | Springs for character and playfulness. Nothing interrupts a video, so pick springs for feel |
| Reduce motion, prefer opacity | Valid for calm styles. Energetic styles (kinetic type, collage) can go bigger, but keep the focal text stable while it's being read |
| Stagger 20–30 ms | Stagger 40–80 ms so the order is perceivable |

Keep their deeper rules unchanged: one primary motion at a time, consistent easing families, motion that explains a spatial relationship, and no gratuitous bounce.

## Rendering: stills, drafts, finals, partial ranges

```bash
# styleframes for review
node <skill>/scripts/render.mjs comp/index.html --stills 1.0,6.5,12,20.5 --still-dir review/frames
# the same frames over a design variant
node <skill>/scripts/render.mjs comp/index.html --stills 6.5 --still-dir review/frames/b --query "tokens=../variant-b.json"
# animatic / draft
node <skill>/scripts/render.mjs comp/index.html --out renders/v1/draft.mp4 --scale 0.5 --fps 15
# check one fixed scene
node <skill>/scripts/render.mjs comp/index.html --out renders/v2/s3.mp4 --from 13.5 --to 20
# final with audio
node <skill>/scripts/render.mjs comp/index.html --out renders/v1/video.mp4 --audio audio/mix.wav
# transparent overlay for footage workflows (ProRes 4444 .mov, or .webm VP9 with alpha)
node <skill>/scripts/render.mjs comp/index.html --out renders/v1/overlay.mov --alpha
```

`render.mjs --help` lists all options (`--browser chrome|msedge|chromium`, `--crf`, `--root`, `--query`, `--png`).

## Performance

- Rendering costs roughly 30–150 ms per frame at 1080p, depending on the scene. A 60 s video at 30 fps (1,800 frames) takes about 1–4 minutes. Run long renders in the background.
- Heavy CSS (big `backdrop-filter` blurs, many large shadows) and big canvases are the usual slowdowns. Use drafts (`--scale 0.5 --fps 15`) while iterating.
- To parallelize long renders, render ranges with `--from/--to` in separate processes, then concatenate with ffmpeg (`-f concat -c copy`, using the same encoding settings).

## Using Remotion or Motion Canvas instead

- **Remotion (React):** use it if the user's project already has it, or if they ask for it. It's free for individuals and small companies, but larger companies need a paid company license, so tell organizations about this before choosing it. `npx create-video@latest`, then `npx remotion render`. The same principles apply: frame-driven (`useCurrentFrame`), deterministic, and stills via `npx remotion still --frame=N` for the approval step.
- **Motion Canvas (MIT):** generator-based, code-first animation. Good for diagrams and explanatory motion.

Whichever engine you use, the approval step still comes from that engine's own still renders.
