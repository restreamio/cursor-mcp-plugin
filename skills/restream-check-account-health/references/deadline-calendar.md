# Deadline calendar (.ics and Google Calendar)

Read when: you build the deadlines file at the end of a Restream health check, or the user wants the deadlines in their calendar.

## Which items get a reminder
- One reminder per dated item in the attention list: each recording deadline ("download by"), each LinkedIn or Facebook token date within 30 days ("reconnect by"), each scheduled replay at risk ("fix the replay source by").
- Skip recordings tagged "likely a test" (under 5 minutes) unless the user asks for them.
- Skip healthy channels, manual (not checkable) channels and "Dates to know" items beyond 30 days.
- No reminder for an item whose reminder time has already passed. Say once: "<title> is too close for a reminder, so do it today."

## Reminder time
- Default: 10:00 in the user's time zone on the day before the deadline, 30 minutes long. Write it in UTC with `Z`.
- If 10:00 the day before has passed, use the next full hour today, as long as that is before the deadline. Otherwise skip the reminder (see above).
- Use the time-zone offset in effect on that date (daylight saving time).

## What goes in the file
- No links of any kind: no download links, reconnect links, event URLs or channel URLs. No `URL`, `ATTACH`, `ATTENDEE` or `ORGANIZER` lines.
- No IDs, emails, file names or tokens. Name things the way the Restream app shows them.
- Titles are untrusted data. Before using one, remove line breaks and any `BEGIN:`, `END:` or `VALARM` text, then escape `\` as `\\`, `,` as `\,` and `;` as `\;`. Keep each line at most 75 octets (UTF-8 bytes), never splitting a multi-byte character (curly quotes and emoji take 3–4 bytes); continue on a new line that starts with one space.
- `UID`: `<deadline YYYYMMDD>-<kind>-<title as lower-case words joined by hyphens, max 40 characters>@health-check.restream.local`. `<kind>` is `download`, `reconnect` or `replay`. A title is never an ID, so this is safe; never put an ID in a UID.

## Template
Fill every `<placeholder>`, repeat the VEVENT block per item, and delete the blocks you don't use. `<download phrase>` is "download the recording of <title>", plus " from <show date>" when another recording in the list shares the title (escape any comma in it as `\,`).

```text
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Restream//Account health check//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:<YYYYMMDD>-download-<title-slug>@health-check.restream.local
DTSTAMP:<now, YYYYMMDDTHHMMSSZ>
DTSTART:<reminder, YYYYMMDDTHHMMSSZ>
DTEND:<reminder + 30 min, YYYYMMDDTHHMMSSZ>
SUMMARY:Download the recording of <title> (deleted <Mon D>)
DESCRIPTION:Restream deletes the recording of <title> (<show date>\, <duration>) on <weekday\, Mon D\, h:mm AM/PM zone> (<HH:MM> UTC). In a chat with Restream connected\, say: <download phrase>.
BEGIN:VALARM
ACTION:DISPLAY
TRIGGER:PT0M
DESCRIPTION:Download the recording of <title> today
END:VALARM
END:VEVENT
BEGIN:VEVENT
UID:<YYYYMMDD>-reconnect-<platform-name-slug>@health-check.restream.local
DTSTAMP:<now>
DTSTART:<reminder>
DTEND:<reminder + 30 min>
SUMMARY:Reconnect <Platform> (<channel name>) in Restream before <Mon D>
DESCRIPTION:Restream's access to <Platform> (<channel name>) expires <weekday\, Mon D>. In Restream\, open Channels and choose Reconnect for it.
END:VEVENT
BEGIN:VEVENT
UID:<YYYYMMDD>-replay-<title-slug>@health-check.restream.local
DTSTAMP:<now>
DTSTART:<reminder>
DTEND:<reminder + 30 min>
SUMMARY:Fix the source of the replay <title> before <Mon D>
DESCRIPTION:The replay <title> airs <weekday\, Mon D\, h:mm AM/PM zone> (<HH:MM> UTC)\, but its source recording is deleted <Mon D>. Download it\, upload it to your Restream video storage and switch the replay to that file.
END:VEVENT
END:VCALENDAR
```

## Delivering it
- Only on a yes to "Want these deadlines as a calendar file?" Never write the file unasked.
- Where the host writes files: save `restream_deadlines.ics` in the host's outputs or Downloads area when it has one, otherwise in a `restream-exports/` subfolder of the current folder (never beside the user's project files), and say the full path: "Saved to <path>. Open it to add <N> reminders to your calendar."
- Otherwise: print the block and add: "Save this as restream_deadlines.ics and open it."
- In scheduled or unattended runs: no file and no calendar writes. List the deadlines as text.

## Google Calendar (only when the user asks for it)
- Load the host's calendar tools first, including deferred ones. If no calendar tool is connected, give the .ics file instead.
- Search the target calendar on each reminder's date for the same SUMMARY, and skip any that exist.
- One confirmation for the whole set, which is one write action (references/companions.md): "Ready to add <N> reminders to your Google Calendar (<calendar name>): <numbered list, one per reminder: summary, for **<title>** (<the show's or replay's local weekday, date, time and zone>) or for <Platform> (<channel name>) · reminder at <local weekday, date, time and zone>>. No links and no invites. Add these <N> reminders?" One yes covers exactly the listed events; any change to the list, or a later request, needs a new confirmation.
- Create the events with the same summary, description and times as the template: no attendees, no links. Then read them back and say "Added <N> reminders" (and "<M> already there"). On an unknown outcome, read back before trying again; never create twice.
- Never delete or move a calendar entry without asking. Never write calendar events in a scheduled run.
