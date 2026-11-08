# Platforms

Export specs and safe zones. Platform limits change often. Treat the duration and size limits below as a starting point, and confirm current limits when they matter (for example a video close to a duration cap).

## Universal export settings

Safe for every platform below:

- Container MP4, video H.264 High profile, `yuv420p`, constant frame rate (24, 25, 30 or 60 fps), `-movflags +faststart`
- Audio AAC-LC 48 kHz stereo, 192–320 kbps
- `-crf 18` for archival or upload masters (platforms re-encode anyway; a cleaner upload survives that better)
- Loudness −14 LUFS integrated, −1 dBTP true peak for social and YouTube (`audio.md`)

`render.mjs` and `assemble.py` produce these by default.

## Specs

| Destination | Resolution | Aspect | Notes |
|---|---|---|---|
| YouTube (standard) | 1920×1080 or 3840×2160 | 16:9 | Chapters from description timestamps (first at 0:00). End screens: last 5–20 s. Upload a custom thumbnail 1280×720 |
| YouTube Shorts | 1080×1920 | 9:16 | Up to about 3 minutes. Square also accepted |
| Instagram Reels | 1080×1920 | 9:16 | Up to about 3 minutes. The profile grid crops to about 3:4 (1080×1440) in the center, so keep the cover text there |
| Instagram feed video | 1080×1350 or 1080×1080 | 4:5 or 1:1 | 4:5 takes the most screen space in the feed |
| TikTok | 1080×1920 | 9:16 | Long uploads allowed, but short content performs differently. Check current limits |
| Facebook feed / Reels | 1080×1350 / 1080×1920 | 4:5 / 9:16 | |
| LinkedIn | 1920×1080, 1080×1080, 1080×1350, 1080×1920 | 16:9, 1:1, 4:5, 9:16 | Most viewing is muted, so captions are essential |
| X | 1920×1080 or 1080×1080 (9:16 supported) | 16:9, 1:1 | Duration limits depend on account tier |
| Vimeo / websites | 1920×1080 or higher | Any | For a site background loop: also export a small WebM/MP4 (no audio, 4–8 Mbps) and a poster image |
| Presentations | 1920×1080 | 16:9 | Embed-friendly H.264. Avoid 60 fps |
| App Store / Google Play previews | Device-specific | — | Strict specs per device class. Check current Apple and Google documentation before building |

## Safe zones for vertical video

The platform UI covers parts of a 9:16 frame: account name and caption at the bottom, action buttons on the right, search or tabs at the top. Approximate safe area for 1080×1920, for text and faces:

```
top:    ~ 220 px (12%)  keep clear
bottom: ~ 420 px (22%)  keep clear (captions sit just above this)
right:  ~ 160 px (15%)  keep clear (like/comment/share column)
left:   ~  60 px        margin
```

The template's `?guides=1` draws this box. When one video goes to several platforms, design to the strictest (TikTok and Reels are similar). Captions go just above the bottom zone, roughly 60–70% down the frame.

## Safe areas for 16:9

Title-safe: the central 90%. Action-safe: the central 93%. For YouTube end screens, keep the end-screen region free of essential content during the last 5–20 s (the layout is chosen by the creator, so ask which elements they plan to add).

## Delivery checklist per platform

- Correct resolution and aspect ratio, and nothing essential outside the safe zones
- Captions burned in (social, muted autoplay) and/or SRT uploaded (YouTube, LinkedIn, accessibility)
- Loudness at target
- Thumbnail or cover frame chosen
- Description text: what it is, plus credits and licenses for third-party audio or footage, chapters (YouTube), and an AI-content disclosure where needed (`ethics.md`)
