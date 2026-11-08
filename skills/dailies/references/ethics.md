# Ethics, rights and disclosure

Video is persuasive and easy to misuse. These rules protect the user, the people who appear in videos, and the people whose work inspired them. Explain the reason when you decline or redirect. The user is almost always acting in good faith and just needs the context.

## Reference library: credit in chat, never in the video

- The images in `image/` are a **visual reference collection, not licensed production assets**. Their `SOURCES.md` files say so: credits don't grant reuse rights. That is also why the skill ships only the credits, and `refs.py fetch` downloads each image from its original source on the user's machine.
- Whenever you show a reference image to the user, say where it came from (creator and source page, from `image/sources.json`; `scripts/refs.py credits <file>` prints it). If the source marks an image as AI-generated, say that too.
- Never put a reference image, any crop of one, or any traced version of one into the output. Never include reference credits, watermarks or source text in the video. The video should show no trace of the reference library except the principles it taught.
- Don't reproduce a referenced publisher's or creator's identity: logos, wordmarks, signature characters, mascots, or a look so close it reads as theirs.

## Voices and likenesses

- **Voice cloning:** only the user's own voice, or a voice whose owner has given clear, documented permission for this use. Don't clone celebrities, politicians, or private people from recordings found online.
- **Avatars and face swaps:** the same rule. Only the user's own likeness, or likenesses with consent. Don't make videos that put words in a real person's mouth they didn't say, even as satire, unless it is obviously and clearly labelled as such and doesn't target a private individual.
- **Real people in footage:** for public posting of footage that shows identifiable people in private settings, suggest getting their consent. For children, be more careful: blur faces when the user is unsure about consent.

## Copyrighted material

- **Music:** only music the user owns, has licensed, or that comes with a license that allows this use. Commercial songs get flagged by Content ID and aren't the user's to use, even for a few seconds.
- **Footage and images:** the user supplies material they have rights to. Don't download films, TV, other creators' videos or stock watermarked previews for them.
- **Reaction and commentary, criticism, education:** fair use (US) or fair dealing (UK, India and elsewhere) can apply when the use is transformative (commentary, critique, analysis), uses only what's needed, and doesn't substitute for the original. You can help structure a video so its commentary is substantive, but you can't promise that a use is legally fair. Suggest checking for anything high-stakes.
- **Fonts:** check the license allows video and embedding. OFL fonts are safe.
- **Trademarks and logos:** use them only to refer to the actual company or product, never in a way that implies endorsement, and never redraw them.

## AI-generated content disclosure

- Tell the user plainly which parts of the delivered video are AI-generated or synthetic (voices, avatars, generated images or footage).
- Remind them about platform rules. YouTube asks creators to disclose realistic altered or synthetic content, and Meta and TikTok apply or require AI labels in many cases. The settings change, so point them to the platform's current upload setting rather than quoting rules.
- Never help pass off synthetic media of real events or real people as authentic.

## Honest content

- Data, quotes and claims shown on screen must come from the user or a cited source. Don't invent statistics, testimonials or quotes to make a video more persuasive. If the script needs a number you don't have, mark it `[SOURCE NEEDED]` and ask.
- Ads: claims must be ones the user can substantiate. Keep the product visible and the disclosures readable (size and duration).

## Privacy

- Footage may contain other people's faces, screens with personal data, license plates, or addresses. Point these out when you notice them in frames, and offer to blur (`boxblur` over a region, or a composition mask).
- Don't upload the user's footage or voice to third-party services unless they choose that provider. Prefer local processing (local Whisper, local TTS) when privacy matters.
