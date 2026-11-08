# Prompts for generators

When the user generates assets in another tool, a precise prompt saves them several attempts. Write prompts **from the approved design system and storyboard**, so generated assets fit the video instead of fighting it.

## Contents
- The style block (consistency across shots)
- Image prompts
- Video prompts
- Storyboard frames
- Voice direction
- Music prompts
- Sound-effect prompts
- Handing off and receiving files

## The style block (consistency across shots)

Write one reusable block and paste it into every prompt for the project:

```
STYLE: [medium: e.g. 35mm film photograph / flat vector illustration / clay stop-motion]
LOOK: [lighting: soft overcast, warm practicals; color: palette from tokens.json in words, e.g. muted teal, warm amber accents, deep navy shadows]
LENS: [e.g. 35mm, shallow depth of field, eye level]   (photo/video only)
TEXTURE: [film grain, paper texture, clean]
ERA/PLACE: [contemporary Mumbai street / 1970s American office]
AVOID: text, logos, watermarks, extra fingers, distorted faces, [style-specific failures]
```

Keep the block identical across shots. Change only the subject and action. Some tools also accept reference images or style references for consistency. Use the user's own approved frames or generated keyframes for that, never images from the reference library (those aren't licensed for reuse).

## Image prompts

```
[Subject and action, specific]. [Composition: framing, where the subject sits, negative space for text on the left third]. [Setting]. STYLE block.
Aspect ratio 16:9 (or 9:16).
```

- Ask for empty space where on-screen text will go ("negative space on the right third for a headline").
- Ask for no text in the image. Put text in the composition, so it stays sharp and editable.
- For cutouts (collage style), ask for "isolated on plain white background", then remove the background (`rembg`, or the tool's own background removal).
- For vector or illustration systems, specify "flat vector, limited palette of N colors: …, no gradients".

## Video prompts

One shot per prompt. Describe it the way a cinematographer would:

```
Shot S03 (4 s, 16:9): [Subject] [action, one clear motion] in [setting].
Camera: [static / slow push-in / lateral track left / handheld subtle], [lens], [height].
Lighting: [ ]. Mood: [ ].
STYLE block.
Start frame: [describe, or attach the approved keyframe]. End frame: [optional].
```

- One action per shot. Generators struggle with sequences of actions inside one clip.
- Specify the camera move explicitly. "Cinematic" alone means nothing.
- Keep shots short (3–6 s) and plan cuts between them, which is how real films are built anyway.
- For consistent characters: describe the same character identically every time (age, hair, clothing, distinctive feature), and use the tool's character reference feature with the user's own reference image.
- Ask for 2–4 takes per shot.

## Storyboard frames

```
Storyboard panel, rough pencil sketch on white paper, loose confident lines, grey marker shading, [shot type: wide / medium / close-up], [subject + action], camera arrow showing [move], panel number [N] in the corner.
```

You can also draw boards yourself in the composition (SVG) when exact layout matters more than sketchiness.

## Voice direction

For TTS tools that accept style instructions, or for a human voice actor:

```
Voice: [age range, gender if relevant, accent: e.g. neutral Indian English / General American]
Delivery: [warm, conversational, curious; not salesy]. Pace: ~150 wpm with natural pauses.
Emphasis: [list key words]. Pronunciation: [Name] = [phonetic respelling].
Context: explainer for [audience], heard over animated graphics.
```

Then the script, with pauses marked in the provider's syntax.

## Music prompts

```
[Genre/instrumentation], [tempo: e.g. 96 BPM], [mood arc: e.g. curious and light, building gently, resolving warm at the end], [length: 75 s], [structure: intro 8 bars, main, quiet break at 0:40, final lift at 0:55, clean ending].
Instrumental, no vocals. Leaves space for voiceover (no busy lead melody in the 1–4 kHz range).
```

Ask for a clean ending rather than a fade, and for stems if the tool provides them (separate drums or pads make ducking and editing easier).

## Sound-effect prompts

```
[Sound], [material/source], [perspective: close, dry / roomy], [duration], [character: soft / punchy / airy].
e.g. "Paper sheet sliding quickly across a wooden desk, close and dry, 0.6 s, soft."
```

## Handing off and receiving files

Give the user a checklist:

```
Generate and save into <slug>/assets/incoming/:
  S01_take1.mp4  — prompt 1 (4 s, 16:9)
  S02_take1.mp4  — prompt 2 (5 s, 16:9)
  vo.wav         — voice script below, WAV 48 kHz if available
  music.mp3      — music prompt below, 75 s
```

When the files arrive: ingest them, check them against the storyboard, pick takes, and tell the user which (if any) need regenerating and why ("S02's hand distorts at 3.1 s; regenerate, or I'll cut at 2.9 s").
