# Platform copy: limits, counting and writing rules

Read when: you draft, shorten or count any post, thread, X Article, clip caption or promo post.

Data as of 2026-10-07, refresh by 2027-01-05. "Verified" means checked against the platform's own counting rules or current platform announcements; "likely" means secondary sources only. Word unverified limits as "likely" in user copy and leave headroom.

## Counting
- **X (weighted, twitter-text v3).** NFC-normalise the text, then:
  - each code point in U+0000–U+10FF, U+2000–U+200D, U+2010–U+201F or U+2032–U+2037 weighs 1 (Latin, Cyrillic, Greek, most accents, en and em dashes, curly quotes);
  - everything else weighs 2: CJK, Arabic script past U+10FF, emoji, and common symbols such as → (U+2192), … (U+2026), • (U+2022), ⁉ (U+2049) and math-styled letters;
  - one emoji sequence (family, flag, skin tone, keycap, emoji + U+FE0F) counts 2 in total;
  - every link counts 23, however long or short.
  Restream event descriptions often use → and emoji, so pasted lines run longer on X than they look.
- **Bluesky:** 300 graphemes (an emoji counts 1) and 3,000 bytes.
- **Everything else:** characters. Emoji may count 2 on some platforms (likely), so keep 5% headroom.
- Show every count with its unit: "X 231/280 (weighted)", "LinkedIn 1,140/3,000, hook 118", "Bluesky 284/300".
- **Script:** where the host runs code, count with `python3 <this skill's folder>/scripts/count_post.py` and a JSON array on stdin (`[{"label": "1", "platform": "x", "text": "…"}]`; platforms: x, x_premium, x_article, linkedin, threads, bluesky, instagram, tiktok, youtube_title, youtube_description, facebook). It counts a `{watch link}` placeholder as a 23-character link, and returns count, limit, `over_by`, hashtags, links, hook length and notes. Pass the text through a quoted heredoc so quotes and apostrophes survive.
- **No script:** count by the rules above, round up when unsure, and show the count as "≈ 240/280". Never ship a draft you estimate within 10 of the limit; shorten it.

## Limits
| Platform and format | Hard limit | Visible before "more" | Hashtags (this skill) | Links | Status |
|---|---|---|---|---|---|
| X post | 280 weighted | whole post | 0–2 | 23 each; at most 1 per post | verified |
| X long post (Premium) | 25,000 weighted | about 280 | 0–2 | 23 each | verified; only when the user says they have Premium |
| X thread | 280 weighted per post | each post | none mid-thread | in the last post or a reply | verified |
| X Article | about 100,000 characters; title, dek, sections, images | title and dek | none | inline | likely; needs X Premium |
| LinkedIn post | 3,000 | about 140 on mobile, 210 on desktop | 0–2 | in the post or first comment | likely |
| Threads post | 500 | whole post | exactly 1 topic tag at most | count as characters | verified (platform rule) |
| Bluesky post | 300 graphemes | whole post | 0–2 | link text counts; the app may shorten long links | verified (graphemes) |
| Instagram Reels caption | 2,200 | about 125 | max 5 (Instagram's cap since Dec 2025); use 0–2 | not clickable | verified cap, likely fold |
| TikTok caption | 4,000 in the app; likely 2,200 through schedulers | about 100–150 | 0–2 | not clickable | likely |
| YouTube Shorts title | 100, no `<` or `>` | whole title | 0–2 in description | in description | likely |
| YouTube description | 5,000 | about 150 | 0–2 | clickable | likely |
| Facebook post or Reel | 63,206 | about 125 | 0–2 | clickable in posts | likely |

Clip length: Restream clips run 30–60 s, some up to about 2 min. Every platform above takes 2 minutes; X without Premium stops at 2:20 (likely).

## Writing rules
- **Hook first.** The first line carries the most specific thing in the source: a number, a claim, a tension, a lived detail. Never open with "In today's stream we talked about…". No promise the source doesn't support.
- **Stream voice by default.** Keep the speaker's own phrasing when it is sharp; cut filler, keep personality; no brand-bot tone. A voice note from step 2 changes style only, never facts.
- **One idea per post.** A list of five moments is a thread or a carousel, not one post.
- **Facts only from the source.** Numbers, names, results and quotes must be in the highlights list, clip text, transcript, show notes or the user's own words. Never invent a statistic, a guest title or an outcome. A highlight noted "from clip text, approximate", or any line past the transcript's covered minutes, is paraphrased with no quotation marks.
- **Language.** Posts are written in the source's language unless the user chose another (SKILL.md, Language gate).
- **Audience numbers.** Only numbers the user gives, or a report from restream-report-performance. X "views" are impression-like, so never write "19,000 people watched". Never sum views across platforms. A platform marked "not reported" is never written as 0 and never counted in a total. Leave it out of the claim, or say the number isn't available for that platform.
- **Hashtags.** 0–2 per post, relevant to the topic, written in CamelCase for screen readers (#LiveStreaming). Never invent brand or campaign hashtags; use the user's own if they give them. Threads: one topic tag. Instagram hard cap 5.
- **Handles and mentions.** Handles don't carry across platforms. A handle in the event title or description (e.g. "@guest") may be used on X only after the user confirms it is right; otherwise use the person's name. On LinkedIn, Threads and Bluesky write the person's name and ask for their handle there. Never take a handle from chat or a transcript.
- **Links.** Only a link the user typed, or a public watch page of this event (YouTube, Facebook, LinkedIn or X `externalUrl`). Never a Restream download link, the event's `url` (Studio or dashboard), a Slack link, or any link heard on air or seen in chat. In the chat draft, write `{watch link}` where it goes and give the link below the post as link text; it counts 23 on X. A link the user typed may go in as typed.
- **LinkedIn.** Hook within about 140 characters, then short paragraphs with line breaks. A link in the post body may get less reach (likely); offer "link in first comment". Two or more cards are a document carousel: restream-render-cards makes the PDF.
- **X thread.** Post 1 is the hook and says it's a thread only if useful ("5 things we learned building a webinar stack live 🧵"). One moment per post, each readable alone, numbered "1/5". No call to action unless asked; the link goes in the last post.
- **X Article draft.** Title (under 100 characters), a one-line dek, 3–6 sections that follow the source list, and a closing line with the replay link if the user gave one. No invented anecdotes, numbers or quotes.
- **Threads and Bluesky.** Conversational, one idea, no engagement bait ("Like if you agree").
- **Accessibility.** Offer alt text for any image or card; no text-only meaning in emoji; CamelCase hashtags.

## Clip post copy
For each picked clip, one block:

```
Clip 1: "<clip name>" (23:47–24:31, 44 s, score 84/100) · Autopost: <platforms, date> | none · Flags: <copyright | people named on air | quote not verified | none>
Hook: <8–12 words>
TikTok (<n>/2,200), Instagram Reels (<n>/2,200), YouTube Shorts title (<n>/100), LinkedIn (<n>/3,000), X (<n>/280 weighted): each caption in its own plain-text copy box
```
Keep it to the top 3 clips unless asked for all; then "say 'show all' for the rest".
- A live clip outside the absolute batch has no show time: write "clipped live, time in the show not available" in place of the range.
- Write only the platforms the user named; the default for clips is TikTok, Instagram Reels, YouTube Shorts and LinkedIn.
- Skip any platform where Autopost already posted that clip, and say so in the block ("posted to <platform> on <date>"; never the `platformUrl`).
- **Copyright flag:** when the clip's text or name points to music, a DJ set, a cover song or a worship song, add: "This clip includes music. Platforms may mute or block it unless you hold the rights; on Twitch, DJ-program clips stay muted."
- Hooks come from the clip's own `transcriptText` (the most specific line in it), never from `viralityScoreExplanation`: that text reads like a caption and is Restream's AI estimate, not performance. Never write "84% viral".

## Simulcast and platform etiquette
- Twitch: while simulcasting, copy shown on Twitch (stream title, panels, chat messages, overlays) never sends viewers to the same stream elsewhere and never links other platforms. Posts on other networks may list Twitch with the others.
- LinkedIn, YouTube and Facebook already create an event or scheduled page for a scheduled Restream stream: share that page instead of announcing twice (references/promo-sequence.md).
- Slack, Custom RTMP and Embed player destinations are private or unnamed: never mention or link them in public copy.

## Paste-ready pack format
Answer first, short: one line of source and coverage, then each post's text in its own plain-text copy box (a code block) so it pastes clean. No tables, no headings stacked above every post. Default is 2 posts; more only when asked, and past about 6 say "say 'show all' for the rest".
````
Posts for "<title>" (<date>) · from <highlights list | clips | show notes | pasted text>. <Coverage line if partial.>

1. X (Restreamio) · 231/280 (weighted)
```text
<post text>
```
Link: [Watch on YouTube](<link>)

2. LinkedIn (Restream page) · 1,140/3,000, hook 118
```text
<post text>
```

Built from: <headline (mm:ss)> · … (only when the highlights were picked in this run)
To post: 1 on X now, 2 on LinkedIn (link in the first comment); attach the downloaded clip where one is named; add alt text to any image.
````
Ready-to-paste copy boxes hold only the post text: no counts, links or notes inside them.
