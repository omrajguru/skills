# Audio

Sound decides how a video feels more than most visuals do. Every layer (voiceover, music, sound effects) gets the same three options: **the user provides it**, **you make it**, or **a tool the user chooses, with a prompt you write**.

## Contents
- Voiceover: writing for the ear
- Voiceover sources
- Cleaning a recorded voice
- Syncing to words
- Music: choosing, licensing, cutting to music
- Sound effects
- Mixing: levels, ducking, loudness
- mix.py cue sheet

## Voiceover: writing for the ear

- About 150 words per minute for explainers, 170+ for energetic social content, 120–130 for calm or meditative pieces. Work out the length from the word count before recording.
- Short sentences, one idea each. Put the key word at the end of the sentence, where stress falls naturally.
- Write numbers the way they're spoken ("thirty-one percent") in the VO script, and as numerals on screen.
- Mark pauses with `[pause 0.5]` and emphasis with *italics* in the script. Translate these into each provider's own syntax (SSML `<break time="500ms"/>`, provider-specific tags, or punctuation) when you prepare the final text.
- Give pronunciation notes for names, brands and non-English words (phonetic respelling, or the provider's phoneme or lexicon feature).

## Voiceover sources

| Option | When | How |
|---|---|---|
| **The user records it** | Best authenticity. Required for personal or brand voices | Give recording tips: a quiet small room with soft furnishings, mouth 10–15 cm from the mic, record a 5 s room-tone sample, WAV 48 kHz. Then clean it (below) |
| **Local TTS (offline, free)** | Drafts, scratch VO, privacy-sensitive content, or a user with no API account | If installed: Piper (`piper --model <voice>.onnx --output_file vo.wav < script.txt`) or Kokoro. Quality is decent but noticeably synthetic. Check each voice model's license |
| **A cloud TTS provider** | Natural quality, many languages | Present options from `providers.md`. If the user has an API key in their environment, you can call the API. Never ask them to paste a key into chat; ask them to set an environment variable. Otherwise prepare the script and settings for them to paste into the provider's web app |
| **Voice cloning** | Consistent brand or creator voice | Only the user's own voice, or a voice whose owner has given documented consent (`ethics.md`) |

Save files as `audio/vo/vo_01.wav`, … (one per scene or paragraph makes re-takes easy), or as a single `audio/vo/vo.wav`.

## Cleaning a recorded voice

A chain that's safe to start with, applied in order:

```bash
ffmpeg -i raw.wav -af "highpass=f=80,afftdn=nf=-25,deesser=i=0.4,acompressor=threshold=-20dB:ratio=3:attack=5:release=100:makeup=2,alimiter=limit=0.95" vo_clean.wav
```

- `highpass` removes rumble, `afftdn` reduces steady noise (hiss, fans), `deesser` softens harsh "s" sounds, and the compressor evens out level. Loudness normalization happens at the final mix, not here.
- Strong noise or echo: if `arnndn` with an RNNoise model file is available, it's stronger than `afftdn`. Otherwise suggest a dedicated speech-enhancement tool from `providers.md`.
- Always compare before and after on a 10 s excerpt. Over-processing sounds worse than mild noise.

## Syncing to words

Transcribe the final VO with word timestamps:

```bash
python <skill>/scripts/ingest.py audio/vo/vo.wav --out audio/vo/analysis
```

`transcript.json` gives you `segments[].words[] = {word, start, end}`. Use it to:

- set scene boundaries on sentence ends (plus 0.2–0.4 s of breathing room),
- trigger key animations on key words (start the motion about 0.1 s *before* the word, so it lands with it),
- drive kinetic type word by word.

Load it in the composition's `setup()` (`fetch('../audio/vo/analysis/transcript.json')`) and look up times by word index instead of hard-coding numbers. A re-recorded VO then re-times the whole video automatically.

## Music: choosing, licensing, cutting to music

- **Mood and tempo first:** describe what the music should do (build curiosity, stay out of the way, energize) and the BPM range (calm 60–80, explainer 90–110, energetic 120–140).
- **Sources:** the user's own or licensed tracks; libraries (YouTube Audio Library and Pixabay are free, with terms per track; Epidemic Sound, Artlist and Musicbed are subscriptions); AI music generators (Suno, Udio, ElevenLabs Music, Stable Audio; check whether the user's plan allows commercial use); or a simple ambient bed you make in code (pads and drones are passable; melodic music generally isn't).
- **Never** use commercial songs the user hasn't licensed, even briefly. Content ID will flag them, and it's not the user's to use.
- **Cutting to music:** find the BPM (ask, check the track's metadata, or use `librosa` if installed: `librosa.beat.beat_track`). Beat interval = 60 / BPM. Put cuts and major motion hits on beats, and section changes on phrase boundaries (every 4 or 8 bars). End the video on the music's resolution: trim the track to end on a phrase, or fade over 1.5–3 s.
- **Editing music length:** cut at a phrase boundary and crossfade (`acrossfade=d=0.5`). Loop sections with `aloop` or by concatenating, crossfading the joins.

## Sound effects

Sound effects work when they're sparse and synced. Rough guide: one per major visual event, never constant.

`scripts/sfx.py` generates clean, royalty-free sounds procedurally (no samples, no licenses involved):

```bash
python <skill>/scripts/sfx.py list
python <skill>/scripts/sfx.py whoosh --duration 0.6 --out audio/sfx/whoosh.wav
python <skill>/scripts/sfx.py riser --duration 2.0 --out audio/sfx/riser.wav
python <skill>/scripts/sfx.py pop --out audio/sfx/pop.wav
python <skill>/scripts/sfx.py click --out audio/sfx/click.wav
python <skill>/scripts/sfx.py impact --out audio/sfx/impact.wav
python <skill>/scripts/sfx.py ding --pitch 880 --out audio/sfx/ding.wav
python <skill>/scripts/sfx.py tick --out audio/sfx/tick.wav
python <skill>/scripts/sfx.py swell --duration 3 --out audio/sfx/swell.wav
python <skill>/scripts/sfx.py room --duration 30 --out audio/sfx/roomtone.wav
python <skill>/scripts/sfx.py rain --duration 30 --out audio/sfx/rain.wav
```

Each accepts `--seed` for variations and `--gain` in dB. For realistic Foley (footsteps, paper, keyboards, crowds), use a library or generator from `providers.md`.

Placement: start whooshes about 0.1–0.2 s before the movement peaks, put impacts exactly on the frame the motion lands, and pops on the frame an element appears. Under VO, keep effects 6–12 dB below the voice.

## Mixing: levels, ducking, loudness

| Element | Typical level relative to the voice |
|---|---|
| Voice | Reference (0 dB) |
| Music under voice | −18 to −24 dB (ducked) |
| Music without voice | −6 to −10 dB |
| SFX | −6 to −12 dB |
| Ambience / room tone | −24 to −30 dB |

**Ducking:** music automatically drops when the voice speaks, using sidechain compression in `mix.py`.

**Loudness targets** (integrated, measured over the whole video):

| Destination | Target | True peak |
|---|---|---|
| YouTube, Instagram, TikTok, most streaming | −14 LUFS | −1 dBTP |
| Podcasts / spoken word | −16 LUFS | −1 dBTP |
| Broadcast (EBU R128) | −23 LUFS | −1 dBTP |
| Broadcast (US, ATSC A/85) | −24 LKFS | −2 dBTP |

## mix.py cue sheet

```json
{
  "duration": 45.0,
  "sample_rate": 48000,
  "voice": [ { "file": "audio/vo/vo.wav", "start": 0.6 } ],
  "music": [ { "file": "audio/music/bed.mp3", "start": 0, "in": 12.0, "gain_db": -8, "fade_in": 1.0, "fade_out": 2.5 } ],
  "sfx": [
    { "file": "audio/sfx/whoosh.wav", "start": 5.9, "gain_db": -8 },
    { "file": "audio/sfx/impact.wav", "start": 13.2, "gain_db": -6 }
  ],
  "ambience": [ { "file": "audio/sfx/roomtone.wav", "start": 0, "gain_db": -28, "loop": true } ],
  "duck": { "enabled": true, "amount_db": -14, "attack_ms": 40, "release_ms": 400 },
  "target_lufs": -14,
  "true_peak": -1.5,
  "output": "audio/mix.wav"
}
```

```bash
python <skill>/scripts/mix.py audio/cues.json          # writes audio/mix.wav and prints the measured loudness
python <skill>/scripts/mix.py audio/cues.json --print  # show the ffmpeg command only
```

The mix targets −1.5 dBTP rather than −1.0 because AAC encoding adds a few tenths of a dB of overshoot, and platforms measure the delivered file, not the WAV.

Fields: `start` is the timeline position in seconds, `in` the offset into the source file, `gain_db` the level, `fade_in`/`fade_out` in seconds, and `loop` repeats the file to the end of `duration`. Ducking compresses `music` (and `ambience`) using `voice` as the sidechain. Normalization is two-pass `loudnorm` for accurate targets.
