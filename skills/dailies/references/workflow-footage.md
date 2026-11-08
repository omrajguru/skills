# Workflow B: the user's footage

For camera clips, phone videos, screen recordings, gameplay, podcasts and webinars. The pattern: **ingest → understand → edit plan → mockups on real frames → assemble → QA.**

## Contents
- Ingest
- Understanding footage (what you can and can't know)
- Edit plan and edit.json
- Mockups on real frames (the approval step)
- Overlays (lower thirds, callouts, facecam frames)
- Captions
- Common operations (ffmpeg recipes)
- Reframing 16:9 → 9:16
- Troubleshooting

## Ingest

```bash
python <skill>/scripts/ingest.py footage/raw/A001.mp4 --out footage/A001
# add --normalize when the report says the file is VFR, HDR or rotated
# add --no-transcribe to skip speech-to-text, --model small|medium to change the whisper model
```

This writes to `footage/A001/`:

| File | Contents |
|---|---|
| `probe.json` | Container, codecs, resolution, fps (average vs nominal), rotation, color transfer (HDR), audio layout |
| `report.md` | Human-readable summary, problems found, and recommended actions |
| `audio16k.wav` | Mono 16 kHz audio for transcription |
| `scenes.json` | Times of shot changes (ffmpeg scene detection) |
| `silences.json` | Silent spans, plus suggested `keep_ranges` for jump cuts |
| `transcript.json` | Word-level transcript (when a whisper backend is installed) |
| `frames/` + `contact.jpg` | Frames at shot changes and regular intervals, as a labelled contact sheet |
| `<name>.cfr.mp4` | With `--normalize`: constant frame rate, SDR, upright, edit-friendly keyframes |

Read `report.md`, view `contact.jpg`, and skim the transcript before planning anything.

**Why normalize:** phone footage is usually variable frame rate (VFR), which drifts audio out of sync after cuts. iPhone HDR (HLG/Dolby Vision) looks washed out when composited with SDR graphics. Rotation flags confuse filters. The normalized copy fixes all three, and keeps the original untouched.

**Several clips:** ingest each one. For multi-camera shoots, line them up by audio. If the user can give the clap or slate times, that's the simplest. Otherwise transcribe each and match phrases.

## Understanding footage (what you can and can't know)

You understand footage through **frames + transcript + scene and silence data**. That covers content, framing, what is said, where the cuts are, and dead air. It *misses* motion quality (shake, focus hunting between sampled frames), audio quality nuances (hum, echo, clipping), and comedic or emotional timing. When those matter:

- Extract more frames in the region in question: `contact_sheet.py <video> --start 30 --end 40 --every 0.5`.
- Run audio stats: `ffmpeg -i in.mp4 -af astats -f null -` (peak, RMS, DC offset), or `ebur128` for loudness.
- Ask the user about the parts only a person watching can judge ("Does the joke at 2:14 land better with the pause?").

## Edit plan and edit.json

First write a human-readable plan (`storyboard.md`, using the motion format but with source timestamps). Then encode it as `edit.json` for `scripts/assemble.py`:

```json
{
  "output": "renders/v1/video.mp4",
  "width": 1080, "height": 1920, "fps": 30,
  "fit": "cover",
  "clips": [
    { "src": "footage/A001/A001.cfr.mp4", "in": 3.20, "out": 9.85 },
    { "src": "footage/A001/A001.cfr.mp4", "in": 11.40, "out": 18.10, "punch": 1.12, "focus": [0.52, 0.38] },
    { "src": "footage/B002.mp4", "in": 0, "out": 4.5, "speed": 1.5, "audio": false },
    { "src": "assets/photo.jpg", "duration": 3.5, "kenburns": [1.0, 1.08], "focus": [0.5, 0.45] }
  ],
  "transition": { "type": "none" },
  "overlays": [ { "src": "renders/v1/overlay.mov", "start": 0 } ],
  "captions": { "file": "footage/A001/captions.ass", "fonts_dir": "assets/fonts" },
  "audio": { "mode": "clips" },
  "crf": 18
}
```

| Field | Meaning |
|---|---|
| `fit` | `cover` (crop to fill, the default) or `contain` (letterbox or pillarbox on black) |
| `clips[].in/out` | Source seconds. Cuts are frame-accurate (everything is re-encoded) |
| `punch` | Static zoom for the clip (1.1–1.2 hides jump cuts) |
| `focus` | `[x, y]` 0..1 center of the crop. For moving subjects: `focus_keys: [[t, x, y], …]` (clip-local seconds, linearly interpolated) |
| `speed` | 0.25–4. Audio is pitch-preserved with `atempo` |
| `audio` | `false` mutes the clip (B-roll under a voiceover) |
| `duration`, `kenburns` | For still images: hold time and `[startZoom, endZoom]` |
| `transition` | `none`, or `{ "type": "fade" or any ffmpeg xfade name, "duration": 0.4 }` applied between all clips |
| `overlays` | Alpha videos or PNGs composited on top: `{src, start, end?, x?, y?}` |
| `captions` | An `.ass`/`.srt` file to burn in. `fonts_dir` makes custom fonts available to libass |
| `audio.mode` | `clips` (keep clip audio), `replace` (use `audio.file` only), or `mix` (clip audio + `audio.file`, with `audio.clip_gain_db`) |
| `audio.loudness` | Optional LUFS target (for example `-14`) applied to the final soundtrack. For anything with music or effects, mix with `mix.py` and use `replace` instead, because its two-pass normalization is more accurate |

Run `python <skill>/scripts/assemble.py edit.json` (add `--print` to see the ffmpeg command without running it). It applies short audio fades at every cut, so cuts don't click.

**Jump cuts from silences:** `silences.json` contains `keep_ranges`, the spoken spans with a little padding. Turn each into a clip entry. Remove filler words ("um", "you know") with the word timestamps in `transcript.json`, but check each cut in context. Removing every pause makes speech sound breathless, so leave about 0.15–0.25 s around words.

## Mockups on real frames (the approval step)

Show the user *their* shot with *your* graphics before rendering everything:

1. Pick the timestamps where overlays appear, and extract those frames from the edit (or source):
   ```bash
   python <skill>/scripts/contact_sheet.py renders/v1/video_nooverlay.mp4 --times 2.5,8,15 --frames-dir review/bg --no-sheet
   ```
   (For a quick mockup before assembling, extract from the source clip at the matching source times.)
2. Build the overlay composition (`comp/`, with a transparent stage) and render stills over each frame:
   ```bash
   node <skill>/scripts/render.mjs comp/index.html --stills 2.5 --still-dir review/frames --query "bg=../review/bg/t2.50.png"
   ```
   `?bg=` draws the image under the stage, so the still shows exactly how the final will look.
3. Put them on the review page (`review_page.py`) and ask.

## Overlays (lower thirds, callouts, facecam frames)

Build overlays as a composition with a transparent background (`?alpha=1` is set automatically by `--alpha`), render to ProRes 4444 or VP9-alpha, and composite with `edit.json` `overlays`. One overlay composition can cover the whole timeline. Hide elements outside their time ranges with `scene()`.

- **Lower third:** name plus role, safe-area aware, on screen for 4–6 s on first appearance. Keep it off the mouth in 9:16.
- **Callouts and arrows:** draw-on paths pointing at UI or objects. Position them using the frame you inspected.
- **Facecam frame (gaming, screencast):** mask the webcam with a rounded rect or circle. Do it in ffmpeg (`alphamerge` with a mask PNG) or put the webcam clip *inside* the composition as a `<video data-start>` with `border-radius`, which is simpler and keeps everything in one place.
- **Progress bar, chapter markers, stat counters:** all composition elements driven by `t`.

## Captions

```bash
python <skill>/scripts/captions.py footage/A001/transcript.json --style words --res 1080x1920 --out footage/A001/captions
# writes captions.srt (sidecar, for platforms and accessibility) and captions.ass (styled, to burn in)
```

- `--style sentence`: one or two lines, bottom, max 42 characters per line. Readable, accessible, and good for long content.
- `--style words`: 1–3 words at a time with the current word highlighted. The social-video look.
- Options: `--font "<family>"`, `--size`, `--color`, `--highlight`, `--outline`, `--position bottom|center|top`, `--margin-v`, `--uppercase`, `--max-words`, `--offset` (seconds, when the edit shifted timing).

**Cuts shift timing.** Caption the *edited* audio: transcribe the assembled video again (`ingest.py renders/v1/video.mp4 --out footage/edit --no-normalize`), or build captions with `--offset` per clip. The first is simpler and always right.

Always give the user the `.srt` too. Platforms index it, and it's the accessible option. Check names and jargon in the transcript before burning anything in. Speech recognition gets proper nouns wrong.

## Common operations (ffmpeg recipes)

All of these can go in `edit.json` or run standalone. Re-encode for accuracy, keep the original files untouched, and write to new files.

```bash
# frame-accurate trim
ffmpeg -ss 12.0 -to 18.5 -i in.mp4 -c:v libx264 -crf 18 -c:a aac out.mp4
# stabilize (two passes; requires libvidstab, included in most full builds)
ffmpeg -i in.mp4 -vf vidstabdetect=shakiness=6:result=t.trf -f null -
ffmpeg -i in.mp4 -vf vidstabtransform=input=t.trf:smoothing=20:zoom=2,unsharp=5:5:0.6 -c:a copy out.mp4
# color: gentle contrast/saturation, or apply a .cube LUT
ffmpeg -i in.mp4 -vf "eq=contrast=1.06:saturation=1.08:gamma=0.98" out.mp4
ffmpeg -i in.mp4 -vf lut3d=grade.cube out.mp4
# speed ramp segment (2x), pitch-preserved
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=PTS/2[v];[0:a]atempo=2[a]" -map [v] -map [a] out.mp4
# freeze frame for 2 s at the end of a clip
ffmpeg -i in.mp4 -vf tpad=stop_mode=clone:stop_duration=2 -af apad=pad_dur=2 out.mp4
# green screen
ffmpeg -i fg.mp4 -i bg.mp4 -filter_complex "[0:v]chromakey=0x00FF00:0.12:0.08[k];[1:v][k]overlay" out.mp4
# picture-in-picture (webcam bottom-right at 28% width)
ffmpeg -i main.mp4 -i cam.mp4 -filter_complex "[1:v]scale=iw*0.28:-1[c];[0:v][c]overlay=W-w-48:H-h-48" out.mp4
# side by side
ffmpeg -i a.mp4 -i b.mp4 -filter_complex hstack=inputs=2 out.mp4
# audio cleanup chain for voice (see audio.md for details)
ffmpeg -i in.mp4 -af "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5:LRA=11" -c:v copy out.mp4
```

## Reframing 16:9 → 9:16

1. **Static or slow subjects (talking heads, podcasts):** look at the contact sheet, estimate the subject's horizontal center per shot, and set `focus` per clip. That's usually enough.
2. **Moving subjects:** set `focus_keys` from frames sampled every 1–2 s. Smooth the path (few keyframes, eased by spacing) so the virtual camera doesn't jitter.
3. **Automatic face tracking:** if `mediapipe` or `opencv-python` is installed, detect faces on sampled frames and fill in `focus_keys` from the detections. Otherwise suggest it as an optional install, and fall back to step 1 or 2.
4. **Two people talking:** cut between crops on the active speaker (from the transcript), or stack the two crops vertically (two 1080×960 halves).
5. **Wide shots that won't crop:** use `fit: contain` on a blurred, scaled-up copy of the same footage as the background (a composition with two `<video>` layers does this cleanly).

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Audio drifts after cuts | VFR source. Use `--normalize` and edit from the `.cfr.mp4` |
| Washed-out grey colors | HDR source composited as SDR. Use `--normalize` (tone-maps to Rec.709) |
| Sideways video | Rotation metadata. `--normalize` bakes it in |
| Clicks at cuts | Missing audio fades. `assemble.py` adds 15 ms fades, so check you're using it |
| Captions burn fails on Windows | Path escaping in the `ass` filter. `assemble.py` works around it by running ffmpeg in the captions folder |
| Embedded video in a composition stutters | Sparse keyframes. Normalize (`-g 15`) before embedding |
