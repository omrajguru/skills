# Style library

Text notes for the 11 reference folders in `image/`. Read these first: they are much cheaper than opening images, and they work even when the images haven't been downloaded. The images are fetched on demand with `scripts/refs.py fetch <style>`, which also builds a contact sheet at `image/_boards/<folder>.jpg`. Open a contact sheet when you need to see a style or show it to the user. Open a single image only when one detail matters.

Each entry has the same shape:

- **Borrow:** the principles worth taking.
- **Motion:** how it moves and paces.
- **Build:** how to make it with this skill's tools.
- **Don't:** what would turn inspiration into copying, or common failures.
- **Signature refs:** good files to show, by number.

Credits for every file are in `image/sources.json`. Print them with `scripts/refs.py credits <file>` whenever you show one. Logos, channel branding, game HUDs and product UIs in these references belong to their owners. Never reproduce them.

## Contents
1. Vox-style video essays
2. Cinematic video essays
3. Talking-head explainer
4. Storyboarding and animatic previews
5. Mixed-media collage
6. Typography and kinetic text
7. Screencast walkthrough
8. Let's-play gaming capture
9. POV
10. Reaction and commentary
11. Lo-fi aesthetic B-roll
12. Combining styles, and going beyond the library

---

## 1. Vox-style video essays (`01-vox-style-video-essays`)

**What it is:** Editorial explainers. An argument carried by diagrams, maps, archival cutouts and annotation.

**Borrow:**
- One loud accent (a saturated yellow is the classic) against paper white or near-black. The accent marks *the thing you should look at*.
- Flat information graphics: icons in grids, nodes joined by lines, blueprint linework.
- Archival photos cut out with a torn or white paper border. Hand-drawn arrows and circles as annotation.
- Satellite or line maps with routes drawn on, and a magnifier lens to zoom into a region.
- Textured, grainy illustration for abstract or emotional ideas.
- Big serif pull-quotes on top of the illustration.

**Motion:**
- Every move explains something: lines draw on, items count up, a map pushes in to where the voiceover is talking about.
- Steady, conversational pacing, with a new visual beat every 3–6 s.
- Hold on the key diagram long enough to read it.

**Build:**
- SVG with `stroke-dashoffset` draw-ons.
- Paper texture as an SVG noise filter or a grain overlay.
- Cutouts as PNGs with an outline made by stacking `drop-shadow`s.
- Maps: open data (Natural Earth, OpenStreetMap-derived tiles), with routes animated in SVG.

**Don't:**
- Use the Vox wordmark or the "Vox yellow + Vox serif" pairing as a brand.
- Make the user look like a Vox imitation. Pick their own accent and type.
- Over-annotate. Use one arrow per idea.

**Signature refs:** 01 (diagram), 03 (archival cutout + arrow), 05 (blueprint), 09 (satellite map), 10 (map + magnifier).

## 2. Cinematic video essays (`02-cinematic-video-essays`)

**What it is:** Essays about film and image-making that argue through *composition*: split screens, symmetry, frames within frames, analysis lines drawn over a shot.

**Borrow:**
- Letterboxing (2.39:1 inside 16:9).
- Restrained titles in white sans or serif.
- Side-by-side frames that rhyme visually.
- Thin white overlay lines for perspective or centering analysis.
- Subtitles as poetry: lowercase or sentence case, sitting low in the frame.
- Long dissolves and superimposition.

**Motion:**
- Slow and patient. Shots hold for 4–10 s, with gentle push-ins. Cuts land on the music.
- Silence is a tool.

**Build:**
- Mostly footage plus overlays (Mode C).
- Analysis lines as SVG drawn over a frame: render with `?bg=` for the mockup, and as an alpha overlay for the final.
- Split screens with ffmpeg `hstack` or with CSS.

**Don't:**
- Pile on graphics. The image carries the argument.
- Use copyrighted film footage the user hasn't cleared. Fair use depends on transformative commentary; see `ethics.md`.

**Signature refs:** 01 (title card), 05 (split-screen rhyme), 06 (frames within frames), 09 (centering line), 10 (one-point perspective grid).

## 3. Talking-head explainer (`03-talking-head-explainer`)

**What it is:** A presenter on camera in a designed space, with B-roll and graphics cut in.

**Borrow:**
- A set that tells you the topic (maps, props, desk, monitors).
- Practical lights and color accents: blue/green, red/black, warm/teal.
- Shallow depth of field.
- Eye-level framing with headroom.
- Props as visual punctuation (holding up a printed page).

**Motion:**
- Punch-in zooms (100% → 115%) on emphasis to hide jump cuts.
- Lower thirds on first appearance.
- B-roll every 5–15 s to reset attention.
- Captions for social cuts.

**Build:**
- Mode B/C.
- Jump cuts from silence detection.
- Punch-ins with `crop` + `scale`.
- Lower-third and callout overlays made in the composition and rendered with alpha.
- When a recording is poor, fix the color with an `eq`/`curves` LUT.

**Don't:**
- Zoom on every cut (it gets dizzying).
- Put captions over the face.
- Let the lower third cover the mouth in 9:16 crops.

**Signature refs:** 01 (map-backed presenter), 02 (moody desk), 05 (colored studio light), 09 (warm minimal).

## 4. Storyboarding and animatic previews (`04-storyboarding-animatic-previews`)

**What it is:** Pre-production material: color scripts (a grid of thumbnails showing the emotional color arc), rough boards with notes, animatics.

**Borrow:**
- The **color script** idea for planning *any* video: one swatch or thumbnail per scene, so the color arc is visible at a glance.
- Rough pencil-style frames with red action notes. Arrows for camera moves.

**Motion:**
- Animatics hold each board for its scene's duration, with simple pans and zooms, temp audio, and timecode.

**Build:**
- Two uses. (a) A *deliverable* for users pitching a film or ad: boards as SVG/HTML or generated images, assembled with timing and a scratch voiceover. (b) A *planning aid* inside this skill: a color-script strip in the review page lets the user approve the arc of a long video.
- Pencil look: an SVG turbulence filter on strokes, on a paper background.

**Don't:**
- Present rough boards as final quality.
- Copy studio boards. Draw the user's shots.

**Signature refs:** 01 and 03 (color scripts), 06 (animatic frame), 08 (annotated boards).

## 5. Mixed-media collage (`05-mixed-media-collage`)

**What it is:** Torn paper, halftone photos, cut-out figures, bold shapes and type, layered with texture. Energetic and tactile.

**Borrow:**
- Torn edges and paper grain.
- Halftone or duotone photo treatment.
- A limited palette of 3–5 flat colors on top of black-and-white photography.
- Type set as cut paper.
- Floating cutouts arranged around one focal figure.
- Strip-cut portraits (a photo sliced into offset bands).

**Motion:**
- Stop-motion feel: animate on twos or threes (hold each pose for 2–3 frames at 24/30 fps).
- Small jitter (±1–2 px, ±0.5°) on held elements.
- Pieces slide or pop in with overshoot. Paper "tears" reveal the next scene.

**Build:**
- A `stepped(t, fps/2)` time quantizer in the runtime for the on-twos feel.
- SVG masks with a rough path for torn edges.
- Halftone as an SVG pattern mask or a canvas shader.
- Textures made in code (noise), or from licensed or CC0 texture packs.

**Don't:**
- Use cutouts of real people the user has no rights to.
- Let everything jitter. Keep the focal element stable.

**Signature refs:** 01 (layered silhouette), 03 (torn-paper lettering), 04 (strip cut), 08 (paper shapes), 10 (floating cutouts).

## 6. Typography and kinetic text (`06-typography-kinetic-text`)

**What it is:** Type *is* the visual. Spirals, extrusions, repeated words in waves, perspective type, outline-versus-solid contrast, festival-poster grids.

**Borrow:**
- One idea per frame.
- Tension between scale contrast and repetition.
- Outline and solid versions of the same word.
- Text on paths (circles, sine waves).
- Extreme scale (letters bigger than the frame).
- A strict 2–3 color system with one shock color.
- Monospaced annotations as a texture.

**Motion:**
- Synced to the voiceover or the beat, word by word. Use word timestamps (`audio.md` § Syncing to words).
- Moves are fast (0.2–0.4 s) with hard ease-out, then a hold.
- Loops and repeated waves with staggered timing.

**Build:**
- HTML/CSS with variable fonts: animate `font-variation-settings` for weight and width.
- SVG `textPath` for orbits.
- `transform: perspective()` for 3D tilt.
- Canvas or three.js for true extrusion.
- Keep text as real text, not images, so it stays sharp at any scale.

**Don't:**
- Use fonts without a license for video. Prefer OFL fonts.
- Animate text too fast to read when it carries meaning. Repetition can be decoration; key words must be readable.

**Signature refs:** 02 (dimensional pop), 05 (repeating wave), 07 (outline/solid), 08 (perspective), 09 (festival grid).

## 7. Screencast walkthrough (`07-screencast-walkthrough`)

**What it is:** A product or software demo, polished: the recording floats in a rounded window on a gradient or blurred wallpaper, with auto-zoom to where the action is, highlighted clicks, a corner facecam, and captions.

**Borrow:**
- Rounded window with a soft shadow on a gradient stage.
- Zoom in on the active area and zoom back out between actions.
- Callout tooltips with step numbers.
- Pill-shaped captions.
- Facecam in a rounded rectangle or circle in a corner, or a side-by-side presenter layout.

**Motion:**
- Smooth camera moves (0.6–1.0 s, ease-in-out).
- Hold steady while the user reads UI.
- Cursor smoothing. Click ripples about 300 ms.

**Build:**
- Mode C. Ingest the screen recording.
- Find action moments from mouse/click logs if the user has them. Otherwise use scene-change detection plus your own reading of the frames.
- Put the recording inside the composition as a `<video>` (frame-synced by the runtime), so zoom, framing and callouts are all one deterministic composition.
- Detail: `cases.md` § Screencast.

**Don't:**
- Zoom so far that UI text gets blurry. Check the source resolution.
- Put the facecam over the UI being demonstrated.

**Signature refs:** 01 (captions + facecam), 03 (floating window on gradient), 06 (guided-tour callout), 09 (side-by-side presenter).

## 8. Let's-play gaming capture (`08-lets-play-gaming-capture`)

**What it is:** Gameplay with a facecam: rounded, circular, cut out from the background, or a large reaction cam. Plus stream overlays (goals, timers).

**Borrow:**
- Facecam placement that avoids the game's HUD (check the HUD corners per game).
- Frame styles that match the game's mood: cozy pastel, FPS high-contrast, horror minimal.
- A big speedrun timer as a graphic element.

**Motion:**
- Facecam scales up on big reactions.
- Zoom-ins on key plays.
- Meme or sound-effect punctuation, used sparingly.
- Jump cuts to remove dead time.

**Build:**
- Mode B/C.
- Facecam mask: `alphamerge` with a rounded-rect or circle PNG.
- Background-removed facecam: needs `rembg` or MediaPipe if installed; otherwise suggest the user's capture software or a tool from `providers.md`.

**Don't:**
- Cover the minimap or health bars.
- Use copyrighted music in the edit. Game music rules vary by publisher; check the publisher's video policy.

**Signature refs:** 01 (themed facecam frame), 04 (circular cam), 06 (cutout cam), 09 (large reaction cam), 10 (timer layout).

## 9. POV (`09-pov`)

**What it is:** First-person footage: hands cooking, handlebars, skis, a camera held out in front. Immersion and motion.

**Borrow:**
- Hands in the frame as the subject.
- Wide-angle immersion with the horizon kept steady.
- An overhead "hands at work" angle for process content.
- Low street-level framing.

**Motion:**
- Speed ramps (slow at the peak moment, fast through transit).
- Match cuts on motion.
- Minimal graphics: small location or stat labels, route maps.

**Build:**
- Mode B.
- Stabilize with ffmpeg `vidstab` (two passes).
- Speed ramps with `setpts` segments.
- Lens correction is optional (`lenscorrection`).
- Stats overlays (speed, distance) from GPX if provided.

**Don't:**
- Over-stabilize into warping.
- Make text overlays fight busy, moving backgrounds. Add a subtle scrim behind them.

**Signature refs:** 01 (chef POV), 02 (overhead hands), 03 (cycling vista), 09 (ski descent).

## 10. Reaction and commentary (`10-reaction-commentary`)

**What it is:** A source video plus visible reactors. Layouts: the source dominant with reactors in picture-in-picture, the source above the reactors, a host beside the frame, analysis overlays (waveforms).

**Borrow:**
- A clear hierarchy, either the source *or* the reactor dominant, never 50/50 by accident.
- A thin brand-color frame around the PiP.
- Pausing the source to annotate (freeze frame plus drawing).

**Motion:**
- Swap dominance when the reaction matters.
- Freeze, annotate, resume.
- Waveform or spectrum visuals for music analysis.

**Build:**
- Mode B/C. ffmpeg `overlay` with scale. Freeze frames with `tpad` or a still loop.
- Waveforms with `showwaves` / `showspectrum`, or the composition's own canvas.

**Don't:**
- Download copyrighted source videos for the user. The user supplies what they have rights to or a fair-use basis for.
- Use long uninterrupted stretches of the source with no commentary. That weakens transformative use; see `ethics.md`.

**Signature refs:** 02 (source above reactors), 04 (source-dominant PiP), 07 (analysis overlay), 10 (presenter beside frame).

## 11. Lo-fi aesthetic B-roll (`11-lofi-aesthetic-broll`)

**What it is:** Calm, looping ambience: rain on glass, bokeh city lights, cabins, a coffee pour, an illustrated study room.

**Borrow:**
- Warm practical light against cool night blue.
- Bokeh and rain texture.
- Slow detail shots.
- One small moving element in a still scene (steam, rain, a blinking light).

**Motion:**
- Nearly still. Imperceptible push-ins (100 → 104% over 20 s).
- Seamless loops: the first and last frames match.
- Cross-dissolves of 2 s or longer.

**Build:**
- Mode A with code-generated rain, bokeh and particles (canvas), or the user's or generated footage.
- Seamless-loop technique: `cases.md` § Loops.
- Audio: rain or room tone plus a mellow music bed (`audio.md`).

**Don't:**
- Use anything recognizable as a known channel's character or mascot (the illustrated study-room girl in ref 10 is a brand). Design an original scene.
- Two references (07, 09) are AI-generated per their source. Mention this if you show them.

**Signature refs:** 03 (night rain droplets), 05 (fireplace + forest window), 07 (cabin in the rain), 08 (backlit pour).

## 12. Combining styles, and going beyond the library

- **Combine by role.** Choose one style for *structure* (how information is laid out), one for *texture* (surface treatment), and one for *energy* (motion and type). For example: Vox structure + collage texture + kinetic-type energy for the hook only.
- **When nothing fits** (a children's lullaby video, an architectural fly-through, a scientific visualization), design from first principles. What does the viewer need to understand, and in what order? What one visual idea carries it? What palette and type fit the subject's world? Then present it as an original direction in Step 2.
- **The user's own reference outranks the library.** If they bring one, it becomes the primary reference, and the library only fills gaps.
