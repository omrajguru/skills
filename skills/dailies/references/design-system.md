# Design system

There is no default design system. Every video gets one that belongs to it: the user's brand, a system built from the style and subject chosen in Step 2, or one the user picks from rendered variants. A fixed house look applied to every video would make every video look the same, so this file covers how to *arrive at* a design system and the video-specific rules any system must satisfy. It does not supply one.

The result always lives in `tokens.json`, which the composition runtime turns into CSS variables. Changing the look is then a one-file change.

## Contents
- Where the design system comes from
- Intake: using the user's design system
- Deriving one from the style and subject
- Design variants
- Rules every video design system must satisfy
- tokens.json format

## Where the design system comes from

In order of priority:

1. **The user's own system** (brand kit, Figma, website, guidelines). It wins whenever it exists. If the brief mentions a brand or product and no system was given, ask for one before designing.
2. **A design reference the user supplies for this video** ("make it feel like this", screenshots, a link).
3. **A system derived from the chosen style and the subject**, built fresh for this project (see below).
4. **Variants.** When the user has no preference and nothing above settles it, render 2–3 directions and let them choose. Do this instead of asking abstract questions about colors and fonts.

Tell the user, in a few lines, where each part of the system came from. Include anything you derived because their input didn't cover it.

## Intake: using the user's design system

| Source | How |
|---|---|
| **Figma file / URL** | With the Figma MCP: variables via `get_variable_defs`, a screenshot of key frames via `get_screenshot`. Map color and text styles to tokens. |
| **Website URL** | Fetch the page and its CSS, and read the CSS custom properties, `font-family` declarations and the most-used colors. Screenshot the hero for the overall feel. Logos must come from the user, never scraped. |
| **Brand PDF / guidelines** | Read it. Take the palettes, typefaces, logo clear space, and the do/don't rules. |
| **`DESIGN.md` / tokens JSON / Tailwind config** | Map directly. |
| **Canva brand kit** | With the Canva MCP, `list-brand-kits`, then map colors and fonts. |
| **A few screenshots or "like this"** | Pull out the palette (sample 5–7 dominant colors), the type category (geometric sans, grotesque, serif, mono), corner radius, shadow style and texture. |
| **Licensed or commercial fonts** | Ask the user for the font files. Don't substitute silently. If you must, use the closest openly licensed match and say which. |

Web design systems are built for screens people interact with at arm's length. Before using one for video, check it against the rules below. Brand body sizes, UI motion timings and thin hairline borders usually need adapting for video, while colors, typefaces and shape language carry over as they are.

Logos: only use files the user provides. Keep the clear space and minimum size from their guidelines. Never redraw or "improve" a logo.

## Deriving one from the style and subject

When the system has to be built for this video:

- **Palette:** start from the subject's world (materials, places, era, the emotional register of the topic) and the structural principles of the chosen style (for example "one loud accent on paper" or "warm practicals against night blue"). Choose the neutrals first, then one accent that marks *what to look at*. Add a second accent only if the content has two series to compare.
- **Type:** pick a display face whose character fits the subject, and a text face that stays readable at caption sizes. Prefer openly licensed fonts (OFL) and download the files into `assets/fonts/` so renders work offline. For scripts other than Latin, check glyph coverage early, for example with the Noto family. Many display faces are Latin-only.
- **Shape and texture:** corner radius, stroke weight, grain or paper texture, and shadow style, all taken from the style's principles rather than copied from a reference frame.
- **Motion character:** precise and fast, soft and slow, or stop-motion stepped. This sets the easing and duration choices below.

Write down the reasoning in one or two lines per decision, in `tokens.json` under `"notes"`. It makes revisions faster and shows the user that the choices were deliberate.

## Design variants

When the user hasn't picked a direction, show instead of asking:

1. Choose the most representative moment (usually the densest information frame or the hook).
2. Make 2–3 token sets that differ meaningfully in type, palette *and* texture. Variants that differ only in color aren't worth the user's time.
3. Render the same timestamp with each, using the template's `?tokens=variant-b.json` option.
4. Put them side by side on the review page with a one-line rationale each, and ask which to build. Mixing is fine ("A's type with C's colors").

## Rules every video design system must satisfy

These are properties of the medium, not a house style. Check any system, whether the user's or derived, against them.

**Legibility.** Video is watched at a distance or on a phone, and only for as long as the text is on screen.

| Role | 1920×1080 (16:9) | 1080×1920 (9:16) |
|---|---|---|
| Hero / hook | 120–180 px | 110–150 px |
| Title | 72–96 px | 80–100 px |
| Body / bullet | 44–56 px | 52–64 px |
| Caption / subtitle | 44–52 px | 56–72 px |
| Smallest text of any kind | 28 px | 34 px |

- At most about 7 words per line for headlines and 42 characters per line for subtitles. One idea per frame.
- Reading time: on screen for at least `words × 0.3 s + 1 s`.
- Contrast: at least 4.5:1 for text, 3:1 for large display type and essential graphics. Over footage, put a scrim behind text (a gradient or a 40–60% dark box) instead of relying on a drop shadow alone.
- Hairlines thinner than 2 px shimmer after compression. Use 2 px or more at 1080p.
- Color never carries meaning on its own. Pair it with position, a label or a shape.

**On-screen text discipline.** No pseudo labels or filler labels (see the principle in SKILL.md). Before adding any label, tag, badge or kicker, ask what the viewer would lose without it. If the answer is nothing, leave it out. Keep the functional ones: units, axes, legends, sources, names and roles, step numbers the narration uses. Never ship placeholder or template text, and don't use emoji as decoration unless the brand uses them.

**Photosensitivity.** No more than three flashes in any one-second period, and avoid large saturated red flashes and high-contrast strobing patterns (WCAG 2.3.1). This matters for glitch transitions, strobe cuts and kinetic type that flips between colors. If the user asks for strobing, warn them and keep it under the limit.

**Motion timing.** Video motion runs slower than UI motion because the viewer is watching, not acting. See `workflow-motion.md` § "UI motion vs video motion".

| Purpose | Typical range |
|---|---|
| Small state change, highlight | 0.2–0.3 s |
| Most entrances and exits | 0.4–0.6 s (exits about 70% of the entrance) |
| Hero entrance, camera move | 0.7–1.0 s |
| Scene transition | 0.6–1.0 s |
| Stagger between list items or letters | 0.04–0.08 s |

Entrances usually ease *out*, exits ease *in*, and movement across the frame eases *in-out*. Springs and overshoot suit playful systems only.

**Safe areas.**
- 16:9: text inside the central 90% (title-safe), important action inside 93%. Leave the bottom-right corner clear in the last 5–20 s if the user will add YouTube end screens.
- 9:16: platform UI covers roughly the top 12%, the bottom 20–25% and the right 15%. Exact numbers are in `platforms.md`.
- The template draws these guides with `?guides=1`. Use them while building and in your own review stills. Never render them into the final.

**Compression.** Large flat gradients band and very fine noise turns to mush at streaming bitrates. Add slight grain to big gradients, and keep texture scale coarse enough to survive H.264.

## tokens.json format

The values below are placeholders that show the *shape* of the file. They aren't a palette to reuse.

```json
{
  "name": "Project or brand name",
  "notes": {
    "palette": "why these colors",
    "type": "why these faces"
  },
  "color": { "bg": "<hex>", "fg": "<hex>", "accent": "<hex>", "muted": "<hex>" },
  "font": {
    "display": { "family": "<family>", "weight": 800, "file": "assets/fonts/<display>.ttf" },
    "body": { "family": "<family>", "weight": 500, "file": "assets/fonts/<body>.ttf" },
    "mono": { "family": "<family>", "weight": 500, "file": "assets/fonts/<mono>.ttf" }
  },
  "radius": 0,
  "motion": { "base": 0.5, "emph": 0.8, "stagger": 0.06 },
  "texture": { "grain": 0 }
}
```

You can name color keys however suits the project. Each `color.<name>` becomes `--color-<name>`, each `font.<role>` becomes `--font-<role>` and `--font-<role>-weight`, `radius` becomes `--radius`, each `motion.<name>` becomes `--dur-<name>`, and `texture.grain` becomes `--grain`. Font `file` paths are resolved relative to `tokens.json`.
