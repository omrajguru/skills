# Difficult situations

Situations that come up in real projects, and how to handle each one well. Read the section that matches what's in front of you.

## Contents
- The brief is unclear, contradictory or keeps changing
- Language, scripts and localization
- Problem files and footage
- Audio problems in the source
- The environment can't do something
- Renders that look wrong
- Third-party tools and generated assets
- Requests that need care or a different approach
- Delivery constraints

## The brief is unclear, contradictory or keeps changing

| Situation | What to do |
|---|---|
| Very vague ("make a video about my startup") | Don't send a questionnaire. Propose one concrete direction (length, platform, structure, style) in a few lines, render one styleframe, and let the reaction drive the next step. People find reacting easier than specifying. |
| The numbers don't add up ("60 s covering 12 features") | Do the arithmetic (about 150 spoken words per minute, reading time per text card) and offer real options: 60 s on the 3 strongest features, 2–3 min for all 12, or a series of short videos. |
| "Make it exactly like <creator/publisher/reference>" | Borrow the principles that make the reference work (pacing, structure, type behavior, palette logic) and say why a replica isn't on offer: their identity and assets are theirs, and a lookalike reflects poorly on the user. Show a direction that is close in spirit. |
| The user rejects two rounds of styleframes | Stop guessing. Show an A/B that changes *one* variable at a time (type, then color, then density) to find what they're reacting to, and ask for any example they like, even from an unrelated field. |
| A change of direction after the final render | Confirm the scope of the change, keep everything that still applies (VO, footage selection, approved scenes), and say how much has to be redone before starting. |
| "Just deliver it", but something essential is missing (no logo, unknown platform) | Use sensible defaults, build, and list every assumption at the top of the delivery message so the user can correct them in one reply. |
| Brand guidelines that fail video legibility (thin type, low-contrast palette) | Keep the brand's identity but adapt for the medium: a heavier weight from the same family, the brand color on a contrasting background, larger sizes. Explain the change in one line. |
| Very long target (30–90 min) or very short (6 s bumper) | Long: build per chapter, render in ranges, and review a chapter at a time. Short: one idea, no setup, logo or payoff by second 4. |

## Language, scripts and localization

- **Glyph coverage:** check that the chosen fonts contain every character in the script before styling (render a test still with the real words). Missing glyphs show as boxes or silently fall back to a different font.
- **Right-to-left scripts (Arabic, Hebrew, Urdu):** set `dir="rtl"` on text containers, mirror layouts where reading order matters (timelines, arrows, progress bars), and right-align captions. Word-by-word animation must follow the reading order.
- **Complex scripts (Devanagari, Tamil, Bengali, Thai…):** split by word, never by character. Character splitting breaks conjuncts and combining marks. libass handles shaping for captions. Check the burned result anyway.
- **CJK:** no spaces between words, so wrap captions by character count with sensible break points, and use a font with full coverage (Noto Sans CJK).
- **Mixed languages in one video (Hinglish, code-switching):** transcription may need a model or provider that handles code-mixing (see Sarvam AI and others in `providers.md`). Check proper nouns by hand.
- **Numbers, dates, currency:** format them for the audience's locale (`toLocaleString` with a locale argument in compositions). Lakh/crore grouping for Indian audiences when appropriate.
- **Emoji in on-screen text:** headless Chrome needs a color emoji font installed (Noto Color Emoji on Linux). Test-render before relying on it, and remember the label discipline (no decorative emoji).

## Problem files and footage

| Situation | What to do |
|---|---|
| HEIC/HEIF photos | Recent ffmpeg builds decode HEIC. For Pillow, `pip install pillow-heif`. Otherwise convert first: `ffmpeg -i a.heic a.jpg`. |
| Photos appear rotated | EXIF orientation. Bake it in first: `python -c "from PIL import Image, ImageOps; ImageOps.exif_transpose(Image.open('in.jpg')).save('out.jpg', quality=95)"`. |
| Camera RAW video (ProRes RAW, BRAW, R3D) | ffmpeg can't decode these. Ask the user to export ProRes 422 or high-bitrate H.264/H.265 from their camera software. |
| Truncated or corrupted file ("moov atom not found") | Usually an interrupted recording. Try `ffmpeg -err_detect ignore_err -i in.mp4 -c copy fixed.mp4`. If that fails, tools like `untrunc` can rebuild it from a healthy file from the same camera. Otherwise ask for another copy. |
| Very large or long files (4K, hours) | Analyze on a proxy (`-vf scale=960:-2`, fast preset) and edit the final from the originals. Check free disk space first: a final at 10 Mbit/s uses about 75 MB per minute, and ProRes overlays use far more. |
| Mixed frame rates, sizes or orientations | `assemble.py` conforms everything to the output format. Choose the output fps of the majority of the footage (or the platform's). Vertical clips in a horizontal edit: `fit: contain` over a blurred fill, or a deliberate split screen. |
| 360° or spherical footage | Reframe to a flat view with ffmpeg's `v360` filter (`v360=e:flat:yaw=…:pitch=…:h_fov=…`). Keyframe the yaw by rendering sections. |
| Screen recordings with odd sizes (1917×1041) | Fine. Scaling handles it, and outputs are forced to even dimensions. Zoom limits depend on the recording's real resolution. |
| Footage with someone else's watermark (stock previews, other creators) | Don't remove it. Ask for the licensed or original file. |
| AI-tool outputs with the tool's watermark | The user's plan determines watermark-free exports. Ask them to export from a plan that allows it. Don't paint it out. |
| Bystanders, children, license plates, screens with personal data | Point them out with timestamps and offer blurs (a `boxblur` region, or a mask in a composition). |
| Files in synced folders (OneDrive, iCloud, Dropbox) | "Online-only" placeholders make ffmpeg stall or fail. Ask the user to make the folder available offline, or copy the media to a local folder. Writing large renders into a synced folder can also lock files mid-write, so render locally and copy afterwards. |
| Paths with spaces or non-ASCII characters | The scripts quote paths correctly. For hand-written ffmpeg filter arguments (`subtitles=`, `lut3d=`), run from the file's folder and use relative names. |

## Audio problems in the source

| Situation | What to do |
|---|---|
| Voice only in the left (or right) channel | Typical lavalier recording. Duplicate it to both channels: `-af "pan=stereo|c0=c0|c1=c0"`. |
| Audio out of sync in the source | Find the offset (a clap, a plosive, or a visible lip closure), then shift it with `-itsoffset` or `adelay`. Check again at the end of the clip. A drift that grows over time means VFR: normalize. |
| Clipped or distorted recording | `adeclip` helps a little. Tell the user plainly that clipping can't be fully repaired, and suggest a re-record for anything important. |
| Wind, traffic, hum | `highpass` for wind rumble, `afftdn` for steady noise, `bandreject` at 50/60 Hz and its harmonics for hum. Strong cases: the speech-enhancement tools in `providers.md`. |
| Two microphones recording the same speech | Use one. Mixing both causes a phasey comb-filter sound. Pick the closer mic per section. |
| Music in the background of the footage (a café, a car radio) | It may trigger Content ID. Point it out, and if it matters, duck it under the voice or replace that section's audio. |

## The environment can't do something

| Situation | What to do |
|---|---|
| ffmpeg or Node missing and the user doesn't want to install them | Say what still works without them (brief, script, storyboard, design system, prompts for generators, the composition source) and what doesn't (no rendering, no edits). Offer the composition as a deliverable they can render elsewhere. |
| The browser won't launch (Linux servers, containers) | `npx playwright install chromium` plus `npx playwright install-deps chromium` on Linux, or install Chrome. `doctor.py` reports it. |
| No display (SSH, cloud, headless sessions) | `review_page.py` without `--open`: give the path, send files with any file-sharing tool available, or serve the project with `render.mjs --serve` and give the URL of `review/index.html` if the user can reach the port. |
| A slow machine | Drafts (`--scale 0.5 --fps 15`), shorter ranges, lighter effects (big blurs and `backdrop-filter` are expensive), and long renders in the background. |
| Offline | Fonts, scripts and media must be local (they should be anyway). Third-party generators aren't available. Local TTS and transcription still work if installed. |
| No transcription engine | Offer to install faster-whisper. Otherwise use a transcript the user has (YouTube auto-captions they own, a script they read from), or timings marked by hand from the waveform. |

## Renders that look wrong

| Symptom | Likely cause |
|---|---|
| A frame differs between renders, or flickers | State leaking between frames. Look for `Math.random`, `Date.now`, CSS transitions or animations running on wall time, or accumulating values in `render(t)`. |
| First frames show fallback fonts or missing images | Assets not ready. Load fonts through `tokens.json` (the runtime waits for them) and keep images as `<img>` elements in the page, or `await` them in `setup()`. |
| Embedded video shows the wrong frame or stutters | Sparse keyframes in the source. Normalize the clip (`ingest.py --normalize`) before embedding. |
| Colors look washed out or shifted | HDR source, or a full/limited range mismatch. Normalize sources. `render.mjs` tags output as BT.709 limited range. |
| Thin lines shimmer, gradients band | Compression. Use 2 px or wider lines, add slight grain to gradients, and raise quality (`--crf 16`). |
| Text looks soft | A scaled-down render (`--scale` below 1), or a camera zoom past 100% on raster content. Keep text as live text and zoom the layout, not screenshots of it. |

## Third-party tools and generated assets

- **Cost:** before calling any paid API on the user's account, estimate the cost (characters for TTS, seconds for video generation, number of images) and get a yes. Small tests first, full runs after the test is approved.
- **No API access:** prepare everything for manual use. Paste-ready text, settings, file names and the folder to save into (`prompts.md` § Handing off).
- **Failures and rate limits:** retry with backoff, save each successful piece as it arrives, and never re-run work that already succeeded.
- **Generated clips with artifacts** (warping hands, melting text, flicker): trim around them, regenerate only the bad shot with a more specific prompt, or cover the moment with a graphic. Say which shot and why.
- **TTS mispronunciations:** phonetic respelling, the provider's phoneme or lexicon feature, or splitting the word with a hyphen. Re-render only the affected line.
- **VO longer or shorter than planned:** re-time the scenes from the VO transcript. Don't speed the voice up beyond about 1.1×, because it starts to sound rushed.

## Requests that need care or a different approach

| Request | Response |
|---|---|
| A commercial song the user hasn't licensed | Explain why (rights, Content ID), and offer licensed library music, a generated track with commercial rights, or the user's own. Don't produce sound-alikes of specific songs. |
| A celebrity's or another real person's voice or face | Decline. Offer the user's own voice or likeness, a stock voice, or a clearly fictional character. |
| Realistic synthetic depictions of real politicians or real events | Decline realistic depictions that could mislead. Commentary and clearly labelled illustration are fine. |
| Removing a watermark or logo from someone else's video | Decline, and ask for the original or licensed file. |
| Fake testimonials, reviews or statistics | Decline. Offer real customer quotes the user provides, or clearly hypothetical framing ("Imagine a team that…"). |
| Health, finance or legal claims in ads | Ask for substantiation, and use the user's own approved disclaimers, readable on screen. |
| Children's content | Gentle pacing, no flashing, simple words, captions. Remind the user about YouTube's "made for kids" setting and the rules that come with it. |
| Memorials and grief | A calm pace and tone, names and dates exactly as given, no upbeat sound effects, and ask before adding any text about the person. |
| Strobing or glitch effects | Keep under three flashes per second (`design-system.md` § Photosensitivity), and warn if the user wants more. |

## Delivery constraints

- **Target file size** (email, chat apps, upload caps): bitrate ≈ `target_MB × 8 / seconds` Mbit/s, minus the audio bitrate. Encode two-pass at that bitrate, and drop the resolution when the bitrate gets too low for it (under ~2 Mbit/s for 1080p).
- **Specific codecs:** ProRes 422 for editors (`-c:v prores_ks -profile:v 2`), H.265 for smaller files on Apple devices (`-c:v libx265 -tag:v hvc1`), WebM VP9 for some web uses.
- **"Can I edit this myself?"** Deliver the project folder (composition source, assets, `edit.json`, audio stems, captions) with a short note on how to re-render. You can't produce Premiere or Final Cut project files, but you can export a cut list with source timecodes.
- **Accessibility:** always offer an SRT. When important information is only visual (a chart with no narration), offer an audio-described version or put the key point in the narration.
