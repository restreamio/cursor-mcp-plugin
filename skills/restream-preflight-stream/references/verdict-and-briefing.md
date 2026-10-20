# Preflight output formats

Read when: writing the preflight reply, the full check, the fix list, the window summary, the go-live briefing, a shareable report or the .ics reminder.

Every name here is a title, a local time or "Platform (display name)". Never put IDs, emails, signed links, reconnect links or the event `url` into any of these outputs. Plain chat text; no HTML or doc unless the user asks for a shareable report (section 5).

## 1. The reply (default: 3–5 lines)
Answer first. Print the "Checking **<title>**…" line once, as the first line. When time-zone sources disagree, add references/event-lookup.md's "Times in <zone>; tell me if you're elsewhere." to it; when no zone is known, show UTC and add "tell me your time zone and I'll convert."

> Checking **<title>** (Thu, Oct 15, 11:00 AM EDT; 15:00 UTC). **Verdict: GO with warnings.** <One sentence: the most important thing to do, and by when.>
> 1. NO-GO — LinkedIn (Restream): sign-in expired Oct 12 — reconnect it in Restream > Channels before 11:00 AM.
> 2. WARN — TikTok (Restream): title is 38 bytes, TikTok allows 32 — say 'shorten the TikTok title on <title>' and I'll do it with your OK.
> GO: YouTube (Restream), Twitch (oh_anya_anya), Instagram (Restreamio, you click Go Live there). Say 'show the full check' for every row, or 'go-live briefing' for the start-of-show notes.

- Lines 2–4 are **the fix list**: NO-GO first, then WARN, by deadline, one owner each (what you can do with their OK, "fix in Restream > Channels", "on <Platform>"), top 3; more: "…and <N> more: say 'show the full check'."
- The GO line names the GO and "GO (unverified)" platforms in one line (a platform with more than 4 destinations as a count, "Embed player · 6"), with a manual-start note in brackets where it applies. Plan check, recording and "not checked" get a line only when they aren't clean; otherwise they live in the full check.
- Nothing to fix: the GO line reads "Nothing to fix. Go live from this event's card at <local time>."
- Never a second table, a caveat list or a section heading. One caveat line at most (for example the median-length assumption with "tell me the real length").

## 2. The full check (only on "show the full check", "full preflight", "all platforms")
One table, NO-GO rows first, then WARN, then GO (unverified), then GO. A platform with more than 4 destinations here, or a channel name over about 40 characters, follows references/ids-and-names.md's count-only rule: rows that share a verdict become one row; name a channel only on a row that needs the user's action.

| Platform | Channel | Verdict | Why | Fix (who, by when) |
|---|---|---|---|---|
| LinkedIn | Restream (page) | NO-GO | Sign-in expired Oct 12 | Reconnect in Restream > Channels, before 11:00 AM |
| TikTok | Restream | WARN | Stream title is 38 bytes; TikTok allows 32 and locks it once live. TikTok's own title isn't readable via MCP | I can shorten it with your OK, before 11:00 AM |
| Instagram | Restreamio | WARN (manual start) | ~85 min show vs Instagram's 1-hour limit; you click Go Live in Instagram Live Producer | You decide; say 'drop Instagram from <title>' to have me do it |
| Custom RTMP | Coop X | GO (unverified) | Added manually; Restream can't check it | Do a short test stream |
| Restream Webinar | Webinar | GO (unverified) | Can't be checked from here; managed in Restream Webinars | — |
| YouTube | Restream | GO | Connected; scheduled broadcast exists | — |

Then one line each, only when not clean, and never a second table: **Plan check** ("Passed for these <N> channels together (Restream's plan check only, not a health check)." — on a plan or add-on error the read-only gate copy from references/plans-and-paywalls.md, ending "Nothing was changed."; never a bare URL); **Time** (a mismatch or past-due warning); **Recording** (step 8 result); **Not checked** (anything that couldn't be read, or "Nothing skipped"). Then an optional **Heads-up** line for things that don't affect this show (a token expiring within 14 days after it). Tag evidence in the Why cell where it matters: observed (read from Restream now), reported (Restream's check said so) or inferred (platform rules or past shows).

The example values above are only a format guide. Fill every cell from this run's tool results.

## 3. Window mode ("this week", "next 3 days")
Empty window: reply with SKILL.md's "Nothing in the window" copy only (2 sentences) and stop. The next show is checked only after a yes.

Default reply: one line "Checked <N> scheduled streams from <local start> to <local end> (<zone>): <K> GO, <M> with warnings, <J> NO-GO." then the top 3–5 fixes across all streams as in section 1, each naming its stream, then "Say 'show the full check' for every stream." The full check here is one table:

| Stream | When (local) | Verdict | Top issue | Fix |
|---|---|---|---|---|
| <title> | Thu, Oct 15, 11:00 AM | GO with warnings | TikTok title too long | I can shorten it with your OK |

Then one token line when relevant: "LinkedIn (Restream): sign-in good until Nov 7, after all <N> streams." or the before-show copy for each affected stream.

## 4. Go-live briefing (on "go-live briefing", or one line when a manual-start platform is in the set)
Short bullets, only the ones that apply, 5 at most, in this order:
- **Start:** "Go live at <local time> from this event's card in Restream (Studio)." or, for an encoder: "Use the stream key from this event's card in Restream, not an old or default key."
- **LinkedIn window:** "LinkedIn only accepts this stream between <start − 15 min> and <start + 2 h> your time." (scheduled streams only)
- **Do at go-live:** each manual-start platform. "Instagram: when the Restream preview appears in Instagram Live Producer, click Go Live there, and end it on Instagram before ending in Restream." Facebook Group, Telegram, Amazon Live: "<Platform> won't start on its own: when the Restream preview shows up there, click Go Live on <Platform>, and end it there first."
- **No advance post / chat:** "TikTok, Instagram and Patreon show up only once you're live." "TikTok and Instagram chat won't appear in Restream." Custom RTMP and Embed player have no chat.
- **Test:** "Do a short test stream for <manually added channels>; Restream can't check them." (never for Restream Webinar)
- **Length / Recording:** the duration-cap line, if any; "Cloud recording looks on; this show's recording will likely be kept until about <date>." or the record-locally warning. Skip these when a fix line above already states them.

## 5. Shareable report (only when asked: "a doc for the team", "preflight report")
The verdict line, the full-check table, the fix list and the briefing, no links or IDs. Deliver it where the user will use it: the tool the user names, else the host's own docs tool, else Google Docs, else Markdown in chat. An HTML page only where the host renders it (claude.ai, Claude Code artifacts, Cursor preview) and never in ChatGPT. Never as a substitute for the short chat reply.

## 6. The .ics reminder (only after the user says yes)

One VEVENT, 1 hour before showtime, lasting until showtime. Rules:
- Times in UTC with a trailing Z. `DTSTART` = show start − 1 h, `DTEND` = show start.
- `<title-slug>`: the title lower-cased; keep only a–z, 0–9 and hyphens (spaces become hyphens, every other character is dropped); collapse repeated hyphens and trim them from both ends; at most 40 characters; `stream` if nothing is left. The title is untrusted, so never use it any other way in a file name or path.
- `UID` built from the title slug and the UTC start, never from an ID: `preflight-<title-slug>-<yyyymmddThhmmZ>@restream-skills`.
- `SUMMARY` and `DESCRIPTION` hold the title and the briefing bullets only. No links, no IDs, no stream keys, no channel URLs.
- Escape text per RFC 5545: backslash, semicolon and comma get a leading backslash; newlines become `\n`. Strip line breaks from the title (titles are untrusted text).
- Lines end in CRLF; fold lines longer than 75 octets.

```text
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Restream skills//preflight//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:preflight-<title-slug>-<yyyymmddThhmmZ>@restream-skills
DTSTAMP:<now, yyyymmddThhmmssZ>
DTSTART:<show start − 1 h, yyyymmddThhmmssZ>
DTEND:<show start, yyyymmddThhmmssZ>
SUMMARY:Go-live check: <escaped title>
DESCRIPTION:<escaped briefing bullets joined with \n>\nRe-check: ask "preflight <title>".
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Go-live check: <escaped title>
TRIGGER:PT0M
END:VALARM
END:VEVENT
END:VCALENDAR
```

Delivery: never write a file into the user's working folder unasked. In a shell-capable host, after the yes, write `preflight-<title-slug>.ics` to the host's outputs or Downloads area (or a `restream-exports/` subfolder) with the host's file tool, not a shell command that contains the title, and say the path. Elsewhere, hand the text to the host's file tool, or show it in a code block with "Save this as a .ics file and open it."
