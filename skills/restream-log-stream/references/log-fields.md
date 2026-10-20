# Stream log fields

Read when: you create a new Stream Log, map this skill's columns onto an existing log, build entries without the row-builder script, check a preview, or the user asks what a column means.

`scripts/stream_log_rows.py` applies everything below. Use this page when the host can't run code, and to check what the script produced.

## The Stream key (the dedupe key)
- Per stream (Notion page or doc): `<title> · <UTC start YYYY-MM-DD HH:MM>`. Example: `Build a Webinar Stack in One Hour · 2026-09-30 20:04`.
- Sheets or Airtable "All platforms" row: add ` · All platforms`. Example: `… · 2026-09-30 20:04 · All platforms`.
- Per platform row: add ` · <Platform> (<channel display name>)`. Example: `… · 2026-09-30 20:04 · X (Restreamio)`. The display name is needed: one account can have 4 X channels, and two YouTube channels with the same name.
- Title: curly quotes become straight, en and em dashes become hyphens, runs of spaces collapse, ends are trimmed. Compare keys ignoring case.
- The UTC start to the minute tells same-title streams on the same day apart ("Restream Studio for ETN" ran 3 times on Sep 3).
- It is a label, not an RTMP stream key. Never build it from an event, channel or recording ID.
- Two channels with the same platform and display name: sort them by `channelUrl`, then by their order in `list_channels` when `channelUrl` is empty (Custom RTMP, Embed player, Facebook Groups), and number the second "(2)" inside the Stream key only (`… · YouTube (Show (2))`), so keys stay stable between runs. The Channel cell keeps the display name verbatim and both rows get Note "same name as another <Platform> channel". When the user asks about these channels, tell them apart as ids-and-names describes.

## Rows (Google Sheets, Airtable, CSV)
One "All platforms" row per stream first, then one row per platform. Columns, in this order:

| Column | Value |
|---|---|
| Date | Local start date, `YYYY-MM-DD`, in the zone recorded for the log |
| Start (UTC) | `YYYY-MM-DD HH:MM` |
| Title | As Restream shows it (normalised as above) |
| Kind | Live, Replay (`upload_and_stream` + `recording`), or Pre-recorded (file event or Studio playlist) |
| Duration (min) | `finishedAt − startedAt`, rounded |
| Platform | `platform` label (Custom RTMP, Embed player, Restream Webinar…). The Webinar page is in `list_channels` as platform `unknown`, platformId 85 → "Restream Webinar". "Unknown platform" for a key not in `list_channels`, or listed as `unknown` with another platformId |
| Channel | `displayName` verbatim; "total" on the All platforms row; "Webinar page" for Restream Webinar; "a channel not in your channel list" for Unknown platform |
| Avg watching | `mean` |
| Peak watching | `max` |
| Views (as platform counts) | `viewsTotal`. Not people; X counts very differently |
| Watch time (viewer-minutes) | `watchedTime` |
| Chat messages | `messagesTotal` |
| Chatters | `chattersTotal` (one person on two platforms counts twice) |
| Recording kept until | Local date from the recording's `expiresAt`; "not in Restream recordings" when the list was read and has none; empty with Note "Recording not checked" when the list didn't load |
| Clips | `clipsCount` of the stream's Clips project; "none" when the list was read and has none; empty with Note "Clips not checked" when the list didn't load |
| Note | Why a cell says "not reported", plus flags |
| Stream key | As above |

- Tell the user once: "Filter Platform to 'All platforms' for one row per stream. Don't add up the Views column: each platform counts views its own way."
- Write values as plain values, never formulas. A title starting with `=`, `+`, `-` or `@` gets a leading apostrophe in CSV.
- Dates stay ISO strings. "not reported", "under 1" and "too small to measure" stay text, so averages skip them.

## Cell rules (apply per row, in order)
0. Analytics that didn't load (an error other than a plan error, after one retry): no entry at all for that stream; list it for the user. A plan or add-on error: every number "not reported", totals Note "Restream returned no analytics for this stream" (never a plan guess). On an update, a cell this run didn't check keeps its old value.
1. TikTok, Instagram, Custom RTMP/SRT/WHIP/HLS, LinkedIn, and a Facebook channel with an empty `channelUrl` (a Group): viewer cells are "not reported". LinkedIn's Note adds its chat count: "LinkedIn doesn't report viewers to Restream; it had 3 chat messages".
2. `mean`, `max`, `viewsTotal` and `peakTime` all 0: viewer cells "not reported". All 0 except `peakTime`: "not reported" if that channel had chat, else 0 with Note "0 counted".
3. `mean` and `max` 0 but views > 0: Avg, Peak and Watch time "not reported"; Note "<platform> counted views but reported no concurrent viewers".
4. `viewsTotal` 0 while `max` > 0: Views "not reported" (Restream Webinar, Slack).
5. `mean` 0 with `max` > 0: Avg "under 1". `watchedTime` 0 there: "too small to measure".
6. Chat: TikTok, Instagram, Custom RTMP/SRT/HLS/WHIP, Embed player and Facebook Groups are "not reported". A chat-capturing channel (YouTube, X, Twitch, Facebook Page, LinkedIn, Slack, Restream Webinar) with no messages row is a real 0. Any other channel without a positive count is "not reported".
7. A platform from the draft clone with no analytics key: every number "not reported", Note "on (from the saved platform list); Restream returned no numbers".
8. All platforms row: the `total` values as returned (never re-added from rows), then rules 3–5 applied to those totals: `viewsTotal` 0 with `max` > 0 → Views "not reported", Note "none of these platforms reported views" (a show whose only channel is Restream Webinar); `mean` and `max` 0 with views > 0 → Avg, Peak and Watch time "not reported", Note "views were counted but no concurrent viewers were reported". Note "Totals cover only the platforms that report numbers", plus the X views warning when X is in the set, plus "platforms without analytics may be missing" when no draft clone was found, plus "platform list saved after the show; may have changed since" when clone destinations created more than a minute after the clone were ignored, plus "Recording not checked" or "Clips not checked" when those lists didn't load. An Unknown platform row whose Webinar chat check stopped early gets Note "Webinar check incomplete".
9. Totals all 0 on a real show: viewer cells "not reported". Never write a plan guess into the log. Whether to tell the user about a possible restricted view (only when every viewer-reporting row is all-zero while chat from those platforms was active) or that none of the platforms report viewers follows analytics-coverage.md, "Free plan and the restricted view".

## An existing log with different columns
Read the log's header row, fields or properties before the first write of a conversation, then map by name:
- Match ignoring case, spaces and punctuation ("avg_watching" = Avg watching). Accept plain synonyms: Average viewers / Avg viewers = Avg watching; Peak viewers / Max viewers = Peak watching; Views = Views (as platform counts); Watch time = Watch time (viewer-minutes); Messages = Chat messages; Key / Dedupe key = Stream key; Notes = Note; Recording expires = Recording kept until.
- Say the mapping once in the preview when any name differs. Write only into mapped columns; the script's `columnsNotInLog` lists the rest.
- A skill column with no match goes into Note as "<column>: <value>" (left out when there is no Note column, and the preview says so). Columns the log has that this skill doesn't know are never touched or filled.
- No Stream key column: ask once to add a text column named "Stream key". Declined: append only, no updates, and the preview says "duplicates not checked".
- Notion: a number property can't take "not reported" (rule below); a select property only accepts existing options, so an unknown Kind or Platform value goes into Note instead of creating an option.
- Never add, rename or retype a column without the user's yes.

## Notion pages and docs (one per stream)
- Notion database "Stream Log", one page per stream. Page title: the stream title. Properties: Date (date), Start (UTC) (text), Kind (select), Duration (min) (number), Platforms (multi-select of platform labels), Avg watching, Peak watching, Views (as platform counts), Watch time (viewer-minutes), Chat messages, Chatters (numbers, from the All platforms row), Recording kept until (date), Clips (number; 0 when the list was read and the stream has no Clips project; empty when the list didn't load), Note (text), Stream key (text).
- Notion number and date fields can't hold text. When a total is "not reported", there's no recording, or a list wasn't checked, leave that field empty and say it in Note ("Viewer numbers not reported by Restream", "No recording in Restream", "Recording not checked", "Clips not checked"). Never put 0 there. The per-platform table in the body keeps the full "not reported" text.
- Google Docs or the host's own docs tool: one doc per stream titled "Stream log · <title> · <local date>", with the same fields as a short list at the top.
- Body, in this order:
  1. One line: "<title> · <local weekday, date, time, zone> · <duration> · <Kind>".
  2. Per-platform table: Platform, Channel, Avg watching, Peak, Views (as platform counts), Chat messages, Chatters, Note.
  3. The totals line and its notes.
  4. "Recording available in Restream until <date>. Ask for a fresh download link (links expire)." Replay: "Uses the original show's recording, available in Restream until <date>." List didn't load: "Recording not checked on this run."
  5. Top clips: up to 5 as "“<name>”, score <N>/100", favourites first, near-duplicates merged. Write "No Restream Clips for this stream." when the list was read and there are none, or "Clips not checked on this run." when it didn't load. No times, thumbnails or links.
  6. Only if this conversation already has them for this stream: a "Highlights" section from the highlights list, with its coverage line copied as the first line (e.g. "Covers the first ~71 of 86 minutes"); if the list has no coverage line, leave the section out. Or "Questions from chat" from the question list. Viewer names and handles never appear.
- Long text (a pasted transcript) goes in a child page, never the page body.

## The log's About text
At creation, write this once: "Stream log from Restream. Dates in <IANA zone>. One entry per Stream key: edit anything except the key. Download links are never stored; ask for a fresh one when you need it." Read the zone back from the same place on later runs.
- Notion database or Airtable table: its description.
- Google Sheets: an "About" tab created with the log (same yes), text in cell A1. Read the Stream key column only from the log tab, never the About tab.
- Google Docs or the host's own docs tool: no shared description. Each doc's first line carries the zone; read it from the newest log doc.

Never write the event `url` anywhere in the log: it contains the event's internal ID, even when the user asks for it.

## Example (from a real 86-minute show, New York time)
| Date | Title | Kind | Duration (min) | Platform | Channel | Avg watching | Peak watching | Views (as platform counts) | Chat messages | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-30 | Build a Webinar Stack in One Hour | Live | 86 | All platforms | total | 233 | 385 | 19127 | 137 | Totals cover only the platforms that report numbers; views are as each platform counts them (X counts very differently), not people |
| 2026-09-30 | Build a Webinar Stack in One Hour | Live | 86 | LinkedIn | Restream | not reported | not reported | not reported | 3 | LinkedIn doesn't report viewers to Restream; it had 3 chat messages |
| 2026-09-30 | Build a Webinar Stack in One Hour | Live | 86 | Restream Webinar | Webinar page | 6 | 9 | not reported | 18 | |
| 2026-09-30 | Build a Webinar Stack in One Hour | Live | 86 | Slack | Restream: #live-team | under 1 | 1 | not reported | 3 | |
| 2026-09-30 | Build a Webinar Stack in One Hour | Live | 86 | X | Restreamio | 214 | 367 | 19002 | 70 | |
