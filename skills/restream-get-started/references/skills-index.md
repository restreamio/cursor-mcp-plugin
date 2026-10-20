# Restream skills index

Read when: you build the capability map ("what Restream skills do I have"), or need to know whether a sibling skill exists before routing to it.

This is the full list for Restream skill pack 1.1.0; the whole pack ships together in the Restream plugin. If the host shows its own list of installed skills, that list wins: name only what is installed. Without a listing tool (ChatGPT, Codex, Cursor, Grok), assume the pack is installed, use this index, and close with: "If a phrase doesn't work, that skill isn't installed in this app."

In replies, name each job by what it does and its phrase; the skill names below are for routing and loading, never for the user. Groups are in the order the capability map uses: most asked first.

Marks: **[paid plan]** needs a paid Restream plan for part of its job; **[add-on]** needs a Restream add-on; **[beta]** still being tested live.

## Most asked (content from a finished stream)
| Skill | What it does | Say |
|---|---|---|
| restream-write-show-notes | Recap, YouTube chapters, show notes, replay descriptions, blog or newsletter drafts. Needs a transcript **[paid plan]**, or one the user pastes. | "summarize last night's stream" |
| restream-extract-highlights | The stream's best quotes, takeaways or Q&A said on air, with timestamps: the highlights list. Needs a transcript **[paid plan]**, or one the user pastes. | "takeaways from my stream" |
| restream-draft-social-posts | Posts and threads for X, LinkedIn, Threads and Bluesky, saved as drafts (Buffer where connected). Never publishes. | "write LinkedIn and X posts from my stream" |
| restream-curate-clips | Ranks and delivers the best Restream clips, re-ranked by chat spikes. **[add-on]** Restream Clips. | "best clips from my stream" |
| restream-render-cards | Turns the highlights list into branded image cards and a LinkedIn PDF. | "make cards from my stream" |

## Before the stream
| Skill | What it does | Say |
|---|---|---|
| restream-schedule-stream | Creates a stream, a weekly series, a record-only session, a replay or a looped video, with platform-ready settings. Looping **[add-on]**: Upload & Stream Marathon or Media. Channels at once depend on the plan. | "schedule a stream for Friday at 6pm to YouTube and X" |
| restream-manage-stream | Moves, renames, cancels or deletes a stream; turns platforms on or off; edits per-platform settings. | "move my stream to Friday" |
| restream-preflight-stream | Read-only go/no-go for one stream, or for every stream in the next few days: plan limits, channel sign-ins, titles, timing traps. | "am I ready to go live tonight" |

## While live
| Skill | What it does | Say |
|---|---|---|
| restream-assist-live-stream **[beta]** | Privately catches the host up on chat across platforms while live: new questions, tech flags such as "no audio", a short pulse. | "catch me up on chat while I'm live" |
| restream-manage-stream | Turns a platform on or off, or fixes the title, while live. | "turn off Twitch right now" |

## After the stream
| Skill | What it does | Say |
|---|---|---|
| restream-report-performance | Honest per-platform numbers for one stream or a trend, and reports for a boss, client or sponsor. Full Analytics **[paid plan]**; free accounts see a restricted view. | "how did my stream do" |
| restream-analyze-chat | What viewers asked about and next-show ideas, an FAQ from answered questions, and what to answer next time; a full answered/unanswered table on request. Answered-on-air checks read the transcript **[paid plan]**. | "what did viewers ask on my stream" |
| restream-export-files | Recording download, verbatim transcript, SRT or VTT subtitles, chat log. Recordings and transcripts **[paid plan]**. | "download my stream recording" |
| restream-log-stream | Keeps a duplicate-free stream log in Notion, Google Sheets, Airtable or Docs; also searches that log. Needs that app connected. | "log last night's stream to Notion" |

## Account and troubleshooting
| Skill | What it does | Say |
|---|---|---|
| restream-check-account-health | Read-only sweep: channels that need reconnecting, LinkedIn and Facebook sign-ins about to expire, recordings about to be deleted. | "check all my Restream channels" |
| restream-fix-my-stream | Diagnoses dropped frames, missing audio, a platform that didn't go live, a recording that didn't show up; works from symptoms and logs, even without the connector. | "my stream keeps dropping frames" |
| restream-get-started | Walks the user through connecting the Restream connector or checks it, names the workspace, gives the overview, answers quick lookups. | "check my Restream connection" |

## Not available as skills yet
Say plainly that these aren't available yet, then offer the closest thing (phrase only in the reply):
- Follow-up from a webinar registrations CSV (counts, replay email to registrants). Closest: the webinar's chat questions, "what did viewers ask on my stream" (restream-analyze-chat).
- Automation recipes for n8n, Make, Zapier or scripts. Closest: a confirmed weekly series now, "set up my weekly show for the next 6 weeks" (restream-schedule-stream).
- Full-transcript search across many past streams. Closest: this skill's search of titles, descriptions and clip text ("which episode did I talk about pricing"), or one show's full transcript, "give me the full transcript of my stream" (restream-export-files).
