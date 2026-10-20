# Design presets: exact values

Read when: the user asks for anything other than the default black card (a color, a look, a font, a logo change), or asks what the presets look like or cost to render.

`scripts/render_cards.py` (`resolve_design()`) is the source of truth for every value below. Don't hand-write CSS for a card; set `design` in the spec.

## Presets

| Preset | Look | Frame | Logo | Questions to ask |
|---|---|---|---|---|
| `black` (default) | Flat black `#000000`, white text, dim text `rgba(255,255,255,0.72)` | Full-bleed | None by default; `logo: "restream"` adds the mark | None |
| `white` | Flat white `#ffffff`, text `#0a0a0a`, dim text `rgba(10,10,10,0.62)` | Full-bleed | None (the mark is white-only; use `logo_path`) | None |
| `aurora` | Blurred color glow + fine grain on a rounded card | Rounded card (inset 38 px, radius 44) on black | None by default; `logo: "restream"` adds the mark | Which color (or suggest blue) |
| `grainy` | Dark procedural smoke lit by one soft light, real film grain | Full-bleed | None by default; `logo: "restream"` adds the mark | Optional tint |
| `custom` | The user's own solid color or gradient | Full-bleed, or `framed: true` for aurora's rounded frame | None | Only when the colors are unclear |

### aurora
Six hand-tuned hues; any `hue` snaps to the nearest one, because each has its own composition, not just a recolor.

| Name | `hue` | Say it when the user says |
|---|---|---|
| Blue | 228 | blue, navy, Restream blue, nothing specific |
| Violet | 268 | purple, violet, lavender |
| Teal | 172 | teal, turquoise, aqua |
| Amber | 28 | orange, amber, warm, gold |
| Magenta | 322 | pink, magenta, red, berry |
| Forest | 148 | green, forest, emerald |

### grainy
WebGL smoke shader plus per-pixel film grain added after the downsample. No `hue` → neutral cool-grey smoke. Any `hue` (0–360) tints it softly; it should still read as smoke, never a saturated glow. Each render draws a new random smoke pattern and light position, shared by every card in that pack, so re-rendering changes the look. If the user liked a pack, keep its files instead of re-rendering everything for one text edit when possible, and warn that a re-render will look slightly different.

Older Restream card packs called this look "smoke", "smoky" or "gradient" (dark smoke lit by a color). Treat those words as `grainy` with that color's hue; their old default blue glow is about `hue: 235`.

### custom
- **Exactly one color, no direction or motion word** ("plain blue", "green cards", "solid #1a3a8f") → solid: `card_bg: "#1a3a8f"`. If the shade is ambiguous ("blue": navy, sky, Restream's own?), pick a sensible hex and name it in the delivery.
- **Two colors, or any direction/motion word** ("orange to purple, diagonal", "blue fading to black") → gradient: `card_bg: "linear-gradient(135deg, #ff7a18 0%, #6a11cb 100%)"` or a `radial-gradient(...)`.
- Text color: a solid hex brighter than mid-grey automatically gets dark text (YIQ brightness > 128). For a light gradient, set `text_color`, `text_dim_color` and `accent_color` yourself (dark values), or ask.
- Plain CSS colors and gradients only. The renderer rejects `url(...)`, `;`, `{`, `}`, `<` and `>`, so background images aren't supported.
- "Glow" or "aurora" wording means `aurora`, not custom. "Smoke", "fog", "film grain" means `grainy`.

## Typography and layout (locked)

| Element | Start size | Weight | Line height | Floor |
|---|---|---|---|---|
| Quote / takeaway headline | 110 px | 600 | 1.22, letter-spacing −0.015em | 44 px |
| Q&A question (quiet line, dim color) | 62 px | 400 | 1.5 | 44 px |
| Q&A answer (the payload, full color) | 84 px | 600 | 1.22, letter-spacing −0.015em | 40 px |
| Eyebrow (off unless asked) | 22 px uppercase | 700 | — | — |

- The headline or question starts at the top of the safe box. A Q&A answer is anchored to the bottom, 60 px above the logo row (120 px on Stories); open space falls between question and answer.
- Autofit shrinks long text in 3 px steps down to the floors. Mild shrink is normal. A card listed in `overflowed_even_at_min_size` needs shorter text or a split, never a smaller floor.
- Word ceilings: headline or question under 18 words; answer under 40 words. The renderer lists offenders in `over_word_limit`.
- No eyebrow ("QUOTE", "TAKEAWAY", "Q&A"), no attribution line, no quotation marks and no timestamp on the card unless the user asks. A requested eyebrow goes in the card's `eyebrow` field.
- Every card is captured at 2x and downsampled to its exact size for crisp text.

## Fonts
- Default: bundled Inter 400/600/700 (`assets/fonts`, SIL Open Font License 1.1, see `assets/fonts/OFL.txt`), embedded in the page. Nothing is fetched from the network, so it renders the same in sandboxes that block Google Fonts.
- The bundled Inter covers Latin scripts (accents, curly quotes, dashes included). Cyrillic, Greek, CJK, Arabic and other scripts fall back to the computer's system font. For those, ask for a font file.
- A brand font: the user uploads a `.woff2`, `.woff`, `.ttf` or `.otf` file → `design.font_path` (absolute path). One file is used for every weight, so a regular-only file renders headlines at regular weight too; ask for the semibold or bold file if the user wants bold headlines.
- A font name only (`design.font_family`, e.g. "Georgia"): works only if that font is installed where the renderer runs, and silently falls back to Inter otherwise. Say so: "Font names only work if that font is installed here. Send me the font file to be sure."
- Google Fonts names are not downloaded. Ask for the file instead.

## Logo
- No preset carries a logo by default. `design.logo: "restream"` adds the bundled outlined RESTREAM mark (`assets/restream-logo-outline-white.svg`, white, so only on dark presets) at 50% opacity: 52 px tall, bottom-right on square and 4:5; 76 px tall, bottom-left on Stories.
- `design.logo_path` (absolute path to the user's PNG, JPG or SVG) places their own logo at the same size and position on any preset.
- With no logo there is no footer row, and the text gets that space back.

## Render cost (measured, Playwright + Chromium)

| Preset | 1 card | 5 cards | Each extra card |
|---|---|---|---|
| black, white, custom | about 1.5 s | about 5 s | about 0.8 s |
| grainy | about 6 s | about 22 s | about 4 s |
| aurora | about 6 s | about 23 s | about 4.3 s |

The setup questions cost more than rendering. Ask none for the default, and at most one otherwise.
