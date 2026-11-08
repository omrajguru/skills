# Cases

Specific formats and what's particular to each. Every case still follows the main loop (brief → style → approval → build → QA). Only the details differ.

## Contents
- Shorts / Reels / TikToks from a long video
- Screencast and product demo
- Talking-head / vlog edit
- Explainer with voiceover (Mode A)
- Photo montage (travel, wedding, memorial, event recap)
- Data animation
- Kinetic typography and lyric videos
- Reaction / commentary
- Gaming highlights
- Seamless loops (lo-fi, ambient, backgrounds)
- Storyboard or animatic as the deliverable
- AI-generated footage assembly
- AI avatar presenter
- Dubbing and translation
- Logo stingers, intros, outros, end screens
- Thumbnails
- Ads and app previews
- Multi-format export

## Shorts / Reels / TikToks from a long video

1. Ingest the long video (transcript included).
2. Find candidate moments in the transcript: a self-contained point, a strong opinion, a surprising fact, a story with a turn, a funny exchange. Each needs a **hook in the first 1–2 seconds** that works without context. Rank 3–8 candidates, giving each a start/end, a hook line and a reason, and let the user choose before you cut.
3. Tighten: cut dead air and false starts. The target is usually 20–60 s.
4. Reframe to 9:16 (`workflow-footage.md` § Reframing).
5. Captions `--style words` with the speaker's key words highlighted, sitting above the bottom UI zone.
6. Optional: a top title bar with the hook as text, a progress bar, a subtle punch-in on emphasis.
7. Deliver each short as its own file, with a suggested caption or description and the SRT.

## Screencast and product demo

- Ingest the recording. If the user has a cursor/click log (some recorders export one), use it. Otherwise find action moments from scene changes plus your frame inspection.
- Composition approach (recommended): put the recording inside the composition as `<video data-start data-in>` inside a rounded "window" on a stage background derived from the project's design system. Animate a `.camera` wrapper to zoom in on each action region (0.6–1.0 s ease-in-out, hold, zoom out between actions). Every zoom, callout and caption is then deterministic and in one place.
- Zoom limit: don't magnify beyond the recording's native resolution, or UI text blurs. A 1080p recording supports about 1.5× on a 1080p output. Ask for a higher-resolution recording if deep zooms matter.
- Cursor: you can't remove a baked-in cursor. You can add click ripples at click times.
- Voiceover: script it after seeing the recording, timed to the actions. A recorded VO with long pauses can be tightened with jump cuts on the *audio* while freezing or slowing the video.
- Facecam: rounded corner cam, or a side-by-side presenter (style 07 refs 01, 09). Never over the UI being demonstrated.

## Talking-head / vlog edit

- Jump cuts from `keep_ranges`, alternating `punch` 1.0 / 1.12 on consecutive cuts from the same angle to hide them.
- B-roll: when the speaker mentions a thing, show it. Plan B-roll slots in the storyboard. Sources are the user's clips, stock (`providers.md`), generated clips (`prompts.md`), or composition graphics.
- Lower third on first appearance. Chapter titles for long videos (and matching YouTube chapter timestamps in the description).
- Audio: the voice cleanup chain (`audio.md`), a music bed ducked under speech, loudness to the platform target.

## Explainer with voiceover (Mode A)

- Script first (about 150 spoken words per minute, so a 90 s explainer is about 220 words). Read it aloud in your head: short sentences, one idea each, concrete examples.
- VO first, visuals second. Get the VO (recorded, TTS or user-supplied), transcribe it for word timestamps, and set scene boundaries on sentence ends and animations on key words.
- No VO? Use on-screen text with music, and be stricter about reading time.

## Photo montage (travel, wedding, memorial, event recap)

- Use `edit.json` clips with still images: `duration` 2.5–5 s, `kenburns` `[1.0, 1.06–1.12]`, with `focus` on the subject (faces) so the slow zoom moves toward what matters.
- Order by story (arrival → moments → closing) or chronology. Group similar shots. Alternate wide and close.
- Cut on the music's beat or phrase (`audio.md` § Cutting to music). Use cross-dissolves (`transition: fade`) for tender pieces and hard cuts for energetic ones.
- Memorials: be gentle in tone, pacing and word choice. Ask before adding any text about the person. Use the names and dates exactly as the user writes them.
- Portrait photos in a 16:9 video: `fit: contain` over a blurred copy, or pair two portraits side by side.

## Data animation

- Load the data in `setup()`. Validate it, and show the user the numbers you'll display. Never invent or "round for drama".
- One chart per point. Animate in the order of the argument: axes → context series (neutral) → focus series (accent) → annotation.
- Count-ups end on the exact value. Label units and sources on screen (small, 28+ px). Data sources *do* belong in the video, unlike reference-library credits.
- Avoid dual axes, 3D charts and rainbow palettes.

## Kinetic typography and lyric videos

- Sync to words: transcribe the VO or the vocal (for songs, transcription works on isolated vocals if the user has stems; otherwise time the lyrics by hand from the waveform and beats).
- One phrase per frame. Vary scale and position with the emphasis of the speech or song. Repeat motifs for choruses.
- Rights: lyric videos need the rights to the song *and* the lyrics. Only make them for the user's own music or music they've licensed (`ethics.md`).

## Reaction / commentary

- The user supplies the source footage (never download it for them) and their camera recording.
- Layout from style 10: source-dominant with a reactor PiP, or reactor-dominant with a source inset. Swap dominance at key moments.
- Freeze, annotate, resume to make the commentary visible. Make sure the commentary transforms the source rather than replaying long stretches.

## Gaming highlights

- Find highlights from audio peaks (`ebur128`/`astats` spikes), scene-change bursts, chat or timestamps the user gives, and the transcript ("no way", laughter).
- Facecam placement avoids the game's HUD. Check the corners in the contact sheet.
- Zoom-ins on key plays, slow-motion replays (`speed` 0.5 with motion-interpolated frames only if `minterpolate` is acceptable quality-wise), and meme sound effects used sparingly.

## Seamless loops (lo-fi, ambient, backgrounds)

- In a composition, make every animated value periodic in the loop length L: use `sin(2π t / L)` or noise sampled on a circle (`noise(cos(2πt/L), sin(2πt/L))`) instead of linear time. Frame 0 then equals frame L.
- For footage, crossfade the end into the start: take the last N seconds and dissolve them over the first N, then trim.
- Check by rendering the last and first frames as stills and comparing. Deliver a loop length the platform likes (10–60 s), and loop it to the target duration with `-stream_loop`.

## Storyboard or animatic as the deliverable

- Boards: one frame per shot. Draw them in the composition (SVG pencil look, or clean shapes) or generate them (`prompts.md` § Storyboard frames), with shot number, camera note and action arrows.
- Animatic: hold each board for its shot's duration, add simple camera moves, a scratch VO or temp music, and a timecode and shot number burned in (on an animatic, that's expected).
- Optional color script: a strip of thumbnails showing the color arc. Put it on the review page.

## AI-generated footage assembly

When the user wants generated shots (Veo, Sora, Runway, Kling, Luma…):

1. Write a shot list with one prompt per shot, using a shared **style block** (look, lens, lighting, palette, era) so the shots match (`prompts.md`).
2. Tell the user exactly what to generate: shot IDs, durations, aspect ratio, and the file naming `S03_take1.mp4`, saved into `assets/incoming/`.
3. When the files arrive: ingest, pick the best takes, trim the bad frames at the start and end (generated clips often wobble in the first and last half-second), grade them toward one look, and assemble.
4. Disclose: the delivery note lists which shots are AI-generated, and reminds the user about platform labels.

## AI avatar presenter

- Write the presenter script for the avatar tool the user chooses (HeyGen, Synthesia, D-ID, Hedra and so on). Keep sentences short, avoid tongue-twisters, and add pronunciation notes for names.
- The user generates the avatar clip (or brings their own consented avatar). Then use Mode C: graphics, B-roll, captions and lower thirds around it.
- Only use avatars or likenesses the user has rights to. Never a real person's likeness without their consent (`ethics.md`).

## Dubbing and translation

- Transcribe → translate (you can do this, but have a native speaker check important content) → generate a voice in the target language with a TTS provider that's strong in that language (Sarvam AI for Indian languages, among others; see `providers.md`) → align to the original timing (fit by adjusting speed slightly, or re-time the video).
- Lip sync won't match unless the user uses a lip-sync tool. Say so upfront.
- Burn in translated captions or ship them as an SRT. On-screen text in compositions can be re-rendered per language from the same composition with a different strings file.

## Logo stingers, intros, outros, end screens

- Use only the user's logo files. Don't redraw them. A stinger is 2–5 s and builds the logo from its own geometry (reveal by mask, assemble its shapes, draw on its stroke). Add a single sound hit or whoosh.
- Intros under 5 s for YouTube (viewers skip long intros). Outros/end screens: 5–20 s, leaving space for YouTube end-screen elements in the layout.

## Thumbnails

- Same design system. Render a 1280×720 still (`--stills` from a dedicated thumbnail composition or the hook frame): a face or the subject large, 3–5 words max, high contrast, readable at 160 px wide.
- Offer 2–3 variants. Thumbnail testing is common on YouTube.

## Ads and app previews

- Ads: hook in 1–2 s, product visible early, captions on (most ads play muted), one clear call to action, and platform specs and duration limits from `platforms.md`.
- App Store / Google Play previews have strict specs (exact resolutions per device, duration limits, real app footage only). Check the current Apple and Google specs before building, and record the app at the matching resolution.

## Multi-format export

- Design the composition to reflow: position elements relative to `--w`/`--h` and the safe areas, not with fixed pixel coordinates. Then render it at each size by changing `width`/`height` (the template reads `?w=&h=` overrides).
- For footage: separate `edit.json` per format, with `focus` adjusted for the narrower crops.
- Check each format's stills on the review page side by side before rendering all of them.
