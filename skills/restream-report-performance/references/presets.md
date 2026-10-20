# Report presets

Read when: the report is for someone other than the user (a client, a boss, a church board, a webinar series review, a team channel), or you write any CSV, including the default inline block.

Every preset uses the same numbers and labels as the main report: average and peak watching at once, views as each platform counts them, watch time in viewer-minutes, chat messages and chatters, and the text `not reported` where a platform gives nothing. A preset changes the framing and the length, never a number.

## The same page, reframed
Every preset starts from the report page the main flow already built (`scripts/chart.py report`): the tiles, the trend, who brought the audience, chat over time, chat vs viewers and vs last time. Reframe it through the spec, never by editing numbers: `show.title` becomes the document title ("<Show or series>: stream performance, <date or period>"), `takeaway` becomes the one-line summary for that reader, `notes` carry only what the reader should know (no plan talk, no internal steps). Where the host renders HTML (claude.ai, Claude Code, Cursor) the page is the shareable report; a document for someone else gets the same tables through the doc ladder (below) with the chart SVGs attached when the format allows images. In ChatGPT the charts are the matplotlib PNGs from the same spec; everywhere else `chart.py text`.

## Rules for any document written for someone else
- No IDs, page tokens, download links, event `url` values or Restream dashboard links.
- No viewer names or @handles. Restream Webinar chat returns real names: never carry them into a report.
- No plan guesses, plans links or plan-limit messages. Paywall copy belongs in the chat with the user, never inside the document.
- No internal notes. Tell the user in chat which tests or short sessions you skipped, and leave that out of the document.
- Private channels keep their display names out: write "Internal Slack channel", "Custom RTMP" (or "Custom SRT", "Custom HLS", "Custom WHIP") and "Embed player", numbered if there are several ("Custom RTMP 1"). Use the real names only if the user asks for them.
- Slack is internal viewing. In a sponsor or client reach section, give it its own row labelled "internal viewing" and, when its average is 1 or more, add under the totals: "Totals include about <n> watching at once in an internal Slack channel."
- Every document ends with "How to read these numbers" (below).
- The document holds the full tables; the chat reply stays 3–5 lines (what the reader will see, plus the link or file). Deliver through the doc ladder in [companions](companions.md): the tool the user names, then the host's own docs tool, then Google Docs, then Markdown. An HTML page only where the host renders it (claude.ai, Claude Code, Cursor), never in ChatGPT. A write into another app (doc, email draft) gets one preview and one confirmation per write action that names the stream, as companions describes.
- Chat totals from Restream include X likes and follows (they arrive as chat rows). Write "chat events" when X was on; write "messages" only for a count where the chat was paged and reactions split off.

### How to read these numbers (paste as the last section)
- **Average / peak watching at once**: how many were watching at the same time, on average and at the busiest minute, as each platform reports it.
- **Views**: counted differently by every platform (X counts far more than other platforms), so views are never added up as people.
- **Watch time**: total viewer-minutes, as reported.
- **Not reported**: the platform doesn't share that number with Restream (LinkedIn viewers, TikTok, Instagram, custom RTMP). It is not zero.
- Totals cover only the platforms that report numbers.

## Client or boss report
1. Name the workspace once per conversation. Call Restream MCP `get_current_user` and say: "This covers the Restream workspace **<workspaceName>**; tell me if the client's streams live in another one." Agencies and teams often have several. If they do: "I can only see **<workspaceName>** through this connection. To report on another workspace, reconnect Restream in this app's connector settings and choose it, then ask again." Stop until they do.
2. Scope: the stream or period they named. One stream → single-stream numbers; "this month" or "this quarter" → trend numbers.
3. Structure (the page already has this order; a written document mirrors it):
   - Title: "<Show or series>: stream performance, <date or period>"
   - **Summary** (at most 3 bullets): reach (average and peak watching at once), engagement (chat messages, chatters, chatters per 100 average viewers when the average is 5 or more), and one comparison (vs the previous comparable show or period).
   - **Charts**: the trend and "who brought the audience" always; chat over time and chat vs viewers when the chat was paged; vs last time when a previous show exists.
   - **By platform**: the KPI table (single) or the show table plus platform table (trend).
   - **What stood out**: the peak with the platform that drove it, and at most one more fact.
   - **Next time** (trend only): 1–3 items, each with its evidence.
   - **How to read these numbers.**
4. Keep it to one page. If they want a deck, hand the finished tables and the chart SVGs to the host's slides tool.

## Church board: weekly online attendance
1. One row per service (a real show). Several services on one Sunday stay separate rows, named by start time.
2. Table: Date · Service · Online attendance (peak watching at once) · Average watching at once · Platforms · Chat messages.
3. Say once, under the table: "Online attendance is the highest number watching at the same time, as the platforms report it. It isn't a count of people or households."
4. Month summary: the average of the weekly peaks, the strongest Sunday, and which platform carries most of the average audience. The page's trend chart is the attendance chart (one point per service, `date` = the Sunday, `title` = the service name); no chat charts unless the board asks.
5. Never write "people reached", "unique viewers" or a head-count. A Facebook Group reports nothing, and a Facebook profile likely has no views: "not reported".

## Webinar series
1. The Restream Webinar row is the webinar page: average and peak watching at once, chat messages and chatters. Its views are "not reported".
2. Show the webinar page next to the other platforms for each session, plus a series row (average of the session averages). On the page, "Restream Webinar" is one platform row like any other, and the series is the trend chart.
3. Registrations, attendee lists and no-shows are not available through Restream's MCP. Say: "I can't set up webinars or read registrants from here; that happens in Restream Webinars (an add-on). [See Restream Webinars](https://restream.io/webinars)." Never estimate attendance from chat.
4. Webinar chat authors are real names: report counts and paraphrased themes only. If the user asks for exact quotes, label authors "Attendee A", "Attendee B", … (per stream), never their names.

## Team digest (Slack text)
Default delivery is text in the chat, ready to paste. Posting is the user's choice.

1. At most 15 lines. Slack formatting: `*bold*`, bullets with `•`. No tables.
2. Single-stream template:
   ```
   *<Title>* · <Wed, Sep 30>, <86> min
   • <233> watching at once on average, peak <385> (<4:44 PM EDT>, about <39> min in)
   • Biggest platform: <X (Restreamio)>, <214> on average
   • Chat: <137> chat events from <68> chatters
   • vs <previous title>: average <down 25%>
   • Not reported: <LinkedIn viewers (3 chat messages)>
   ```
3. Weekly template: a "*Week of <Mon, Oct 5>*" line, one line per real show (title, average, peak, chat events), then one total line and the "not reported" line.
4. If the conversation already produced takeaways (a highlights list, a recap), add at most 2 lines from them. Never fetch a transcript just for the digest.
5. Never include @channel, @here, viewer names or handles, links, IDs or plan talk.
6. Posting, only when the user explicitly asks and Slack is connected:
   - Confirm the channel by name, name the stream, and show the exact text: "This will post now to <#channel>, about **<title>** (<Wed, Sep 30, 4:04 PM EDT>), and it can't be undone: <exact text>. Post it?" A weekly digest names each stream the same way.
   - Post once after a clear yes. Read it back if the connector can; on an unknown outcome, check the channel before anything else and never post twice.
   - A different channel or edited text needs a new confirmation.
7. Scheduled digests (see [recurring runs](recurring-runs.md)) go only to the user's own DM or run notification: "Scheduled runs can't post to #<channel> on their own, so each run sends the post to you, ready to forward."

## CSV
One row per show per channel, plus one "All platforms (reported)" row per show from `total`.

```
show_title,start_local,timezone,duration_min,platform,channel,avg_at_once,peak_at_once,views_as_counted,watch_time_viewer_min,chat_messages,chatters,note
```
- `start_local` as ISO 8601 with offset (`2026-09-30T16:04-04:00`), `timezone` as the IANA name.
- Write the text `not reported` or `not on` in number columns; never 0 or blank for them.
- `note` holds the labels: "views counted differently on X", "under 1 on average", "Restream Webinar", "a channel not in your channel list", "replay".
- No IDs, links, viewer names or stream keys. Quote any field that contains a comma.
- Writing these rows into a live Google Sheet, Airtable or Notion is restream-log-stream's job.
