# Providers

A neutral directory of third-party tools that can supply what you can't make yourself: natural voices, avatars, photoreal images, generated footage, music, Foley, dubbing.

## How to present options (fairness rules)

- **Recommend by need, not by brand.** Start from what the user needs (language, budget, offline or cloud, commercial rights, consent, quality bar), then name 2–4 tools that fit, with the reason each fits. Include at least one free or open-source option when one exists.
- **No favorites, no affiliation.** You have no relationship with any of these companies. Don't rank by popularity alone, and don't repeat marketing claims.
- **Things change fast.** Pricing, free tiers, model names, language support and terms change monthly. Present this list as "options to check", and tell the user to confirm current pricing and commercial-use terms on the provider's site. If you can browse, check them.
- **The user's choice is final.** If they already use a tool, work with it.
- **Keys and accounts:** if a provider has an API and the user wants you to call it, ask them to put the key in an environment variable (for example `ELEVENLABS_API_KEY`, `SARVAM_API_KEY`). Never ask for a key in chat, and never write keys into project files. Without API access, prepare everything (script, settings, prompts, file names) for them to use in the provider's web app.
- **Consent and disclosure** apply to every tool here (`ethics.md`).

## Voice / text-to-speech

| Tool | Notably good for |
|---|---|
| ElevenLabs | Very natural English and many other languages, voice design, voice cloning (with consent), dubbing |
| Sarvam AI | Indian languages (Hindi, Tamil, Telugu, Bengali, Marathi, Kannada, Malayalam, Gujarati, Punjabi, Odia and more) and code-mixed Indian English. Also offers speech-to-text and translation for Indian languages |
| OpenAI (TTS models) | Simple API, steerable delivery through instructions, good default voices |
| Google Cloud Text-to-Speech / Gemini TTS | Very wide language coverage, multi-speaker dialogue options |
| Microsoft Azure AI Speech | Very wide language and locale coverage, detailed SSML control, custom neural voice (with a consent process) |
| Amazon Polly | Inexpensive at volume, SSML, AWS-native |
| Cartesia | Low latency, expressive voices |
| Hume AI | Emotionally expressive delivery from text descriptions |
| Murf, WellSaid Labs | Studio-style voiceover workflows for corporate and training videos |
| Resemble AI | Voice cloning with built-in watermarking and consent tooling |
| **Open / local:** Piper, Kokoro, Chatterbox, AI4Bharat Indic TTS models | Offline, free, private. Check each model's license: some open models are non-commercial only (for example Coqui XTTS's model license) |

## Speech-to-text (when local Whisper isn't enough)

Local first: faster-whisper, openai-whisper, whisper.cpp (free, private; `ingest.py` uses whichever is installed). Cloud: Deepgram, AssemblyAI, OpenAI, ElevenLabs Scribe, Google, Azure, and Sarvam AI for Indian languages. Cloud services help with long files, speaker labels (diarization), or languages local models handle poorly.

## Speech enhancement (noisy or echoey recordings)

Adobe Podcast (Enhance Speech), Auphonic, Descript (Studio Sound), and open-source DeepFilterNet or RNNoise. Try the ffmpeg chain in `audio.md` first. Use these when it isn't enough.

## Avatars / digital presenters

HeyGen, Synthesia, D-ID, Hedra, Colossyan, Tavus, Captions. They differ on avatar realism, custom avatar creation (all require consent from the person), language support, and API access. Check whether the user's plan allows commercial use and custom avatars.

## Video generation

| Tool | Notes to check |
|---|---|
| Google Veo | High fidelity, native audio on some versions |
| OpenAI Sora | Strong scene coherence; availability varies by region |
| Runway | Many editing tools beyond generation (inpainting, background removal, motion brush) |
| Kling | Strong motion and longer clips |
| Luma (Dream Machine / Ray) | Fast iteration, camera control |
| Pika, MiniMax Hailuo | Fast, stylized options |
| **Open weights:** Wan, HunyuanVideo, LTX-Video | Run locally or on rented GPUs. Check each license |

All of them: generated clips vary from take to take, so plan for 2–4 takes per shot. Commercial terms depend on the plan. Add platform AI labels.

## Image generation

Midjourney (aesthetic range), OpenAI GPT Image (instruction-following, text in images), Google Gemini / Imagen (editing, consistency), Black Forest Labs FLUX (quality, open variants), Ideogram (typography in images), Recraft (vector and brand-consistent illustration), Adobe Firefly (trained on licensed content, which suits brand-safe commercial work), Stable Diffusion (open, local, controllable with LoRAs and ControlNet), Leonardo.

## Music

- **Generators:** Suno, Udio, ElevenLabs Music, Stable Audio, Beatoven.ai, Soundraw, Mubert. Check that the plan grants commercial rights and what attribution, if any, it requires.
- **Libraries:** YouTube Audio Library and Pixabay Music (free; terms per track), Free Music Archive (Creative Commons; license varies per track), Epidemic Sound, Artlist, Musicbed, Uppbeat (subscriptions or free tiers with attribution).

## Sound effects and Foley

ElevenLabs Sound Effects and Stable Audio (generated), Freesound (Creative Commons; license per sound, often attribution required), Pixabay SFX, Zapsplat, the Sonniss GDC bundles (free, royalty-free), and BBC Sound Effects (check its license: much of it is personal or educational use only). Simple synthetic effects: `scripts/sfx.py`.

## Dubbing and lip sync

ElevenLabs Dubbing, HeyGen video translation, Rask AI, Sync (lip-sync models). For Indian languages, pair a strong Indian-language TTS (for example Sarvam AI) with your own timing alignment.

## Stock footage and images

Free: Pexels, Pixabay, Unsplash (images), Mixkit, Coverr. Paid: Storyblocks, Artgrid, Shutterstock, Getty Images, Adobe Stock. Check model and property releases for commercial use, especially for ads.

## Finishing in an editor (if the user wants to continue by hand)

DaVinci Resolve (free tier is very capable), CapCut, Adobe Premiere Pro, Final Cut Pro, Descript (text-based editing). You can export an EDL or FCPXML-style cut list on request, or just deliver the assets in an organized folder with a timeline description.
