---
name: dailies
description: Make finished videos (MP4) from an idea, a script, or the user's own footage, with a visual approval step before anything renders. Use this skill whenever the user wants to create, animate, edit, cut, caption, reframe, dub, or add voiceover, music or sound effects to a video. That includes explainers, Vox-style or cinematic video essays, kinetic typography, product demos and screencasts, YouTube Shorts / Reels / TikToks, talking-head and vlog edits, gaming or reaction layouts, lo-fi loops, storyboards and animatics, photo montages, data animations, logo stingers and intros. Trigger even on casual phrasing like "make a video about X", "turn this clip into a reel", "add captions to my recording", "I need a voiceover for this", "cut the silences out", or "what AI tool should I use for the voice", and when the user wants prompts for AI image, video, music or voice generators for a video project.
---

# Dailies

In film, *dailies* are the frames a director reviews before anything is locked. This skill works the same way. You turn an idea or raw footage into a finished video, and the user approves real frames before you spend time rendering.

There are two main paths:

- **Built from nothing** (motion graphics, explainers, kinetic type): brief → style → styleframes the user approves → build → MP4.
- **Built on the user's footage** (camera clips, screen recordings, gameplay): ingest → edit plan → their own frames with your overlays drawn on for approval → build → MP4.

Everything else (audio, captions, AI tools, platform exports) plugs into one of those two.

## Principles, and why they matter

1. **Approve what will ship.** Make styleframes and overlay mockups with the *same renderer* that makes the final video. Approval only means something if the approved frame and the final frame are the same pixels. Never show a hand-made mock that the real video won't match.
2. **References are a springboard, not a template.** The library in `image/` shows directions that work. Borrow the *principles* (how the palette is built, composition, pacing, texture, how type behaves) and make something new for this user's content. Never trace a frame, never put a reference image or any of its parts into the output, and never reproduce a logo or a publisher's identity (for example the Vox wordmark, a game HUD, or a product's UI that isn't the user's). If no reference fits, design from first principles. The library is a floor, not a ceiling.
3. **Credit in chat, never in the video.** Every time you show a reference image, tell the user where it came from, using the credits in `image/sources.json` (`scripts/refs.py credits …` prints them). Credits never go into the rendered video: no source text, watermarks, or end-card attributions from the reference library. Attribution the user needs for *assets that actually appear in the video* (licensed music, CC sound effects) is different. Report that in the delivery message, and add it to the video description, not the picture.
4. **"Just make it" is a valid answer.** Some users want to pick everything, others want a finished video. If they say "surprise me" or "you decide", choose the style, design system and audio yourself and stop only at the styleframe approval. Make reasonable defaults, say what you chose, and keep going.
5. **Ask only what changes the result.** Ask a question if the answer changes the video. Batch your questions into one message. Don't ask about anything you can infer or safely default.
6. **Every word on screen carries information.** Never add pseudo labels or filler labels: text that names what the viewer can already see, or that decorates without informing. That rules out tags like "FACT", "STAT", "DID YOU KNOW?", "KEY TAKEAWAY", "BREAKING", "NEW", "TIP", a "QUOTE" badge over a quote, "Chapter 1" over a title that already names the topic, category chips, decorative pills, "Subscribe!" stickers nobody asked for, and placeholder or template text left in. Labels stay when they do a job: units, axis labels, legends, data sources, a speaker's name and role, step numbers the narration refers to, chapter titles in a video the viewer actually navigates by chapter. When unsure, delete the label and see whether the frame loses meaning. Clean frames read faster.
7. **Be honest about limits.** You "watch" footage through extracted frames and a transcript, not by viewing it, so say so when it matters (for example, judging comedic timing). You can draw anything with code (type, shapes, diagrams, charts, illustration-like SVG, 3D with three.js), and you can make simple sound effects and basic ambient audio with code. You can't produce photoreal imagery, natural human voices, or real music on your own. For those, use the user's assets, a tool they choose, or a local model if one is installed, and offer to write the prompt.

## First run in a session: check the toolchain

```bash
python <skill>/scripts/doctor.py
```

It checks ffmpeg/ffprobe, Node, `playwright-core` and a Chromium-family browser (an installed Chrome or Edge works, so no browser download is needed), Pillow, and optional transcription (faster-whisper / whisper / whisper.cpp). It prints install commands for anything missing. If something is missing and installing it is reasonable, ask once, then install. Don't silently skip a capability.

`<skill>` means this skill's directory throughout.

## Step 0: Classify the request

| Mode | Signals | Go to |
|---|---|---|
| **A. Motion graphics** | No footage; "explain", "animate", "explainer", "kinetic", "intro", "promo", "data" | `references/workflow-motion.md` |
| **B. Footage edit** | User has clips, screen recordings, gameplay, or podcast video | `references/workflow-footage.md` |
| **C. Hybrid** | Footage plus graphics: talking head with animated B-roll, screencast with callouts, gameplay with facecam | Both: footage ingest first, then motion for the overlays |
| **D. Single asset** | Only captions, only a voiceover, only prompts, only a thumbnail, only a sound effect | The matching reference: `audio.md`, `prompts.md`, `workflow-footage.md` (captions) |

If the request matches a pattern in `references/cases.md` (Shorts from a long video, screencast polish, photo montage, lyric video, reaction layout, seamless loop, storyboard-only, data animation, multi-format export), read that section too. It covers the details specific to that pattern.

## Step 1: Brief

Get these in **one** message, and fill in defaults for whatever the user skips:

- **Purpose and audience.** What should the viewer think, feel or do afterwards?
- **Platform and aspect ratio.** YouTube 16:9, Shorts/Reels/TikTok 9:16, feed 4:5 or 1:1. See `references/platforms.md` for specs and safe zones.
- **Length.** Default: 30–60 s for social, 2–5 min for explainers.
- **Content.** Script, key points, data, or footage. If there's no script, offer to write one.
- **Voice and audio.** Voiceover or not, whose voice, music mood. Details in Step 7.
- **Must-haves and must-nots.** Brand, words, faces, deadlines.

Save the result as `brief.md` in the project folder (layout below). When the user's first message already answers most of this, confirm in one line and move on.

## Step 2: Style

Offer three paths. The user can pick one or mix them.

1. **From the library.** Read `references/style-library.md` (text notes on all 11 styles). Then:
   ```bash
   python <skill>/scripts/refs.py list
   python <skill>/scripts/refs.py match "explain economics maps playful"
   ```
   The images aren't shipped with the skill, only their credits. On first use, download the styles you need (`refs.py fetch 01 05`, or `fetch --all`, about 50 MB). This fetches each image from its original URL and builds a contact sheet per style in `image/_boards/`. If an image is no longer online, describe that reference from the style notes and give its source link instead.

   Show the user 2–3 matching **contact sheets** (`refs.py board <style>` prints the path, fetching first if needed). They're cheap to view; open individual images only when a detail matters. How to show images is covered below. With every image, give its credit:
   ```bash
   python <skill>/scripts/refs.py credits 01-vox-style-video-essays/05-parking-blueprint-graphic.jpg
   ```
2. **The user's own style.** A link, screenshots, a video they love, or "like Kurzgesagt". Pull out the same principles you'd pull from the library (palette logic, type, pacing, texture), and confirm them in a few bullets.
3. **Your own direction.** Propose an original direction in two or three sentences, and show it in Step 6.

Mixing styles is often the best answer, for example "Vox-style information graphics with collage texture and kinetic type for the hook". Say which principles come from which reference.

## Step 3: Design system

There is no house style. Every video gets a design system of its own, built in this order (details in `references/design-system.md`):

- **The user's own:** a brand kit, a Figma file, colors and fonts from a website, a `DESIGN.md`, tokens JSON, or a Canva brand kit. Ask for one if the brief mentions a brand and none was given.
- **A design reference they supply** for this video.
- **Derived for this project** from the chosen style's principles and the subject's world.
- **Variants instead of asking:** when nothing above settles it, render the same key frame in 2–3 directions and let the user pick (see Step 6). Showing is faster than describing.

Whatever the source, check it against the video rules in `design-system.md` (legibility sizes, reading time, contrast, safe areas, motion timing). Write the result to `tokens.json` before rendering any styleframe, so a later change to a color or font is a one-line edit.

## Step 4: Bring in motion and design skills

Other skills improve the taste of the video. Load whichever are available, and translate their UI rules into video timing (the table in `workflow-motion.md` § "UI motion vs video motion" explains how):

```bash
npx ui-skills start
npx ui-skills categories
npx ui-skills list --category motion
npx ui-skills get baseline-ui
```

Also use Emil Kowalski's skills (for example `emil-design-eng`, plus any others installed), `apple-design`, and `animation-vocabulary` (turns "make it bouncy" into a precise motion term) when they're installed. If one isn't available, carry on without it. They improve taste; they aren't required.

## Step 5: Script and storyboard

Write `storyboard.md`: one block per scene, with timing, what's on screen, the voiceover line, the motion idea, and the sound. The format is in `workflow-motion.md` § Storyboard (for footage, `workflow-footage.md` § Edit plan). Keep text on screen long enough to read: about `words × 0.3 s + 1 s`, minimum 1.5 s.

## Step 6: Approval gate (styleframes or overlay mockups)

This is the step that makes the skill worth using.

- **Mode A:** build the composition far enough to render 3–6 representative moments: the hook, a dense information frame, a transition midpoint, and the end card. Render them as stills:
  ```bash
  node <skill>/scripts/render.mjs comp/index.html --stills 0.8,4.2,9.5,14 --still-dir review/frames
  ```
- **Mode B/C:** pull frames from the user's footage at the moments where overlays appear, then render the overlay composition *over those frames* (`?bg=` mode, see `workflow-footage.md` § Mockups). The user sees their own shot with your lower third, captions or callouts on top.
- **Variants:** render the same timestamp from 2–3 design directions next to each other.

**Review them yourself first.** Open the PNGs and check: text is readable at phone size, nothing sits outside the safe areas, hierarchy is clear, contrast is enough, nothing looks like a copied reference, nothing is cut off, no pseudo or filler labels and no leftover placeholder text. Fix problems before the user sees them.

Then build the review page and open it:

```bash
python <skill>/scripts/review_page.py review/manifest.json --open
```

The manifest lists your frames, the references that shaped them (shown with credits), notes, and the specific questions you want answered. Give the user the file path too, and if the environment has a tool for showing files or images to the user, use it as well. Ask focused questions: "Is the yellow too loud?" gets a better answer than "Thoughts?"

For videos longer than about 60 s, offer an **animatic** before the final render: a low-resolution draft (`--scale 0.5 --fps 15`). The user can also open `comp/index.html` in a browser to scrub through the live preview.

Respect the user's pace. If they said "just deliver", show the styleframes in one message and only wait for a yes.

## Step 7: Audio

For each audio layer (voiceover, music, sound effects), offer three options: **the user provides it**, **you make it**, or **a tool of their choice, with a prompt you write**.

- `references/audio.md`: writing VO scripts, cleaning recorded VO, picking music, ducking, loudness targets, timing animation to VO words, and the sound effects you can generate (`scripts/sfx.py`).
- `references/providers.md`: a neutral directory of voice, avatar, image, video, music and SFX tools (Sarvam AI, ElevenLabs, OpenAI, Google, Azure, HeyGen, Synthesia, Veo, Runway, Suno and more), organized by what the user needs. Present the options fairly. Don't steer toward one vendor, note when a tool is the best fit for a need (for example Indian languages, offline use, or commercially safe training data), and remind the user to check current pricing and terms.
- `references/prompts.md`: prompt templates for every generator type, plus how to keep a look consistent across many generated shots.

When the user will generate assets elsewhere, give them the prompts, a file naming scheme, and the folder to drop files into (`assets/incoming/`). Then carry on once the files arrive.

## Step 8: Build and render

- **Motion:** finish the composition, then:
  ```bash
  node <skill>/scripts/render.mjs comp/index.html --out renders/v1/video.mp4 --audio audio/mix.wav
  ```
- **Footage:** write `edit.json` (cuts, overlays, captions, audio) and run `python <skill>/scripts/assemble.py edit.json`.
- **Audio:** `python <skill>/scripts/mix.py audio/cues.json` produces one mixed, loudness-normalized WAV with music ducked under the voice.

Renders longer than about 2 minutes should run in the background.

## Step 9: QA and delivery

```bash
python <skill>/scripts/qa.py renders/v1/video.mp4 --platform youtube --expect-duration 45
```

It checks codec, resolution, fps, duration, black or frozen frames, loudness and true peak, and builds a contact sheet of the final file. Look at the contact sheet yourself, fix anything it flags, then deliver:

- the file path, plus format, resolution, duration and size
- what is AI-generated or synthetic, and a reminder to turn on the platform's AI-content label where it applies (`references/ethics.md`)
- licenses and attributions for any third-party audio or footage *in* the video, for the video description
- which library references shaped the look, with credits (in chat, not in the video)
- an offer for useful extras: other aspect ratios, a captions file (SRT), a thumbnail, shorter cuts

## Revisions

Keep each version: `renders/v1/`, `renders/v2/`… Map feedback to scenes, re-render only the affected time range (`--from/--to`) when you're checking a fix, then do a full render for delivery. If feedback contradicts an approved styleframe, point that out gently and confirm before changing direction.

## Project layout

Create this in the user's working directory (folder name = short slug):

```
<slug>/
  brief.md  storyboard.md  tokens.json
  comp/            composition (copied from <skill>/templates/composition)
  assets/          user-provided media, fonts; assets/incoming/ for generated files
  footage/         ingest output (probe, transcript, frames, contact sheets)
  audio/           vo/, music/, sfx/, cues.json, mix.wav
  review/          manifest.json, frames/, index.html
  renders/v1/ …    finals and drafts
```

## Showing images to the user

The terminal can't show images inline, so the review page (`scripts/review_page.py --open`) is the main way to show them. It opens in the default browser. Also:

- give the absolute path
- use any tool the environment offers for showing or sending files to the user
- open individual images yourself with your file-reading tool to judge them, so you're never describing a frame you haven't looked at

## Reference map

| File | Read when |
|---|---|
| `references/style-library.md` | Picking or combining styles (Step 2) |
| `references/design-system.md` | Taking in a brand, deriving a system, design variants, video legibility and motion rules (Step 3) |
| `references/workflow-motion.md` | Building any composition: runtime API, storyboard format, transitions, embedding media, UI → video motion |
| `references/workflow-footage.md` | Any user footage: ingest, edit.json, cuts, reframing, overlays, captions, mockups |
| `references/cases.md` | Specific formats: Shorts from long video, screencast, montage, lyric, reaction, loop, storyboard-only, data, multi-format |
| `references/audio.md` | Voiceover, music, SFX, mixing, loudness |
| `references/providers.md` | The user asks which tool to use, or needs something generated elsewhere |
| `references/prompts.md` | Writing prompts for image, video, voice, music or SFX generators |
| `references/platforms.md` | Export specs, safe zones, platform limits |
| `references/ethics.md` | Voice/likeness consent, copyrighted source material, AI disclosure, reference credits |
| `references/difficult-situations.md` | Vague or contradictory briefs, other languages and scripts, problem files and audio, missing tools, renders that look wrong, paid APIs, sensitive requests, file-size limits |
