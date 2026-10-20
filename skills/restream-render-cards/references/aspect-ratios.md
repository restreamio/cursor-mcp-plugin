# Platforms, sizes and safe zones

Read when: the user names a platform or several, names one not in the table, asks for a LinkedIn carousel, or asks why a format uses the margins it does.

Resolve the platform the user names to a format; never ask for a raw ratio. `scripts/render_cards.py` (`ASPECTS`, `PLATFORM_ALIASES`) holds the same values and accepts the platform name directly as `aspect`.

## Platform → format

| The user says | `aspect` | Pixels | Deliverable |
|---|---|---|---|
| Nothing, "square", "just the images" | `square` | 1080×1080 (1:1) | PNGs, plus cards.zip for 2+ |
| LinkedIn | `vertical` | 1080×1350 (4:5) | PNGs, plus **cards.pdf** for 2+ cards (set `make_pdf: true`) |
| Instagram feed, X/Twitter, Facebook feed, "feed", "portrait" | `vertical` | 1080×1350 (4:5) | PNGs, plus cards.zip |
| Instagram or Facebook Stories, Reels, TikTok, YouTube Shorts | `stories` | 1080×1920 (9:16) | PNGs, plus cards.zip |

- Width is always 1080, so line breaks and type scale stay the same across formats.
- X: 4:5 is a supported in-feed size that survives the crop; X's own most-cited size is landscape 16:9, which this renderer doesn't make. If the user insists on 16:9, say the cards come in square or 4:5.
- A platform not in the table (Pinterest, Threads, Bluesky, a newer app): ask "Should these be square (1:1), portrait (4:5) or full-screen vertical (9:16)?" A wrong guess means re-rendering the whole pack.
- Several platforms in one request: render one pack per format into its own folder (for example `out/linkedin`, `out/stories`). The card text stays the same; only `aspect` and `make_pdf` change.

## LinkedIn needs a PDF
LinkedIn removed native image carousels in December 2023. A multi-page PDF uploaded as a document post is what swipes like a carousel; several images upload as a static grid. So for LinkedIn with 2 or more cards, set `make_pdf: true`: the renderer writes `cards.pdf`, one page per card in order, at 1080×1350. Tell the user to upload the PDF as a document post and give it a title. A single LinkedIn card is a normal image post, no PDF.

## Safe zones

| Format | Full-bleed presets (black, white, grainy, custom) | Framed presets (aurora, custom framed) |
|---|---|---|
| `square`, `vertical` | 70 px on every side | 76 px on every side, inside the 38 px frame |
| `stories` | 250 px top and bottom, 70 px sides | 250 px top and bottom (from the canvas edge), 76 px sides |

- Square and 4:5 margins are breathing room: smaller on full-bleed cards, larger on framed ones so the gap reads in proportion to the frame.
- Stories' 250 px top and bottom are a platform rule: Instagram, TikTok, Reels and Shorts draw the profile row, close button and reply bar there. It is measured from the true canvas edge whatever the preset.
- Stories also get a larger logo (76 px, bottom-left, only when a logo is set) and a 120 px gap above it, because the format is viewed full-screen.
- The renderer builds the safe box from these numbers and shrinks text before it can cross them. Never place text or a logo outside it.
