# Long form: blog post, newsletter, LinkedIn article

Read when: the user wants a blog post, newsletter, LinkedIn article, or a draft in beehiiv, Kit, WordPress.com, Webflow or HubSpot.

Short social posts, threads, X Articles and short LinkedIn posts belong to restream-draft-social-posts. A per-stream archive page or stream numbers in Notion, Sheets or Airtable belong to restream-log-stream.

## Before writing
- **Source:** the cleaned transcript (covered minutes only), plus a highlights list or question list if one is already in the conversation.
- **Voice:** by default, the hosts' own voice from the transcript, cleaned up. If the user pastes 1–3 samples of their writing, match those. Reading past issues or posts from beehiiv, Kit, WordPress.com, Webflow or HubSpot is opt-in: only when the user asks and that app's read tool is loaded. Read 2–3 recent items for tone only and never copy their text.
- **Replay link:** only the URL the user gives. Without one, write "[Replay link]" and say so when you hand over. Never a Restream download link or event link (event links contain an internal ID).
- **Partial coverage:** put the coverage line at the top as an editor's note ("Editor's note, remove before publishing: covers the first ~71 of 86 minutes"), and write only about the covered minutes.
- **Quotes:** exact words from the transcript, with fillers ("um", repeated words) removed and nothing else changed, plus mm:ss. Attribute to a confirmed name or "a speaker". Chat is quoted only when the user asks, always unattributed: never a name, handle, "Person N" or "Attendee A".
- **Facts:** only what was said on air or what the user gives. No outside statistics, prices, dates or claims. Doctrinal, medical, legal or financial claims get "verify before publishing".
- **Several streams** ("newsletter from this week's streams"): name the real finished shows in the user's local week and continue (ask first when there are more than 10), then write one section per show, each with its own coverage line.

## Blog post
Default for "blog post", "article" and "write-up".
- SEO title of about 60 characters, a slug of 3–6 lowercase hyphenated words, a meta description of about 155 characters. These are common SEO conventions, not platform limits.
- Intro: 2–3 sentences on who, what and why it matters.
- 3–5 H2 sections following the show's arc, 120–250 words each.
- 2–3 pull quotes with timestamps.
- FAQ: 3–5 questions actually asked on the show, answered only with what was said on air.
- Call to action: watch the replay (the user's link) or join the next stream.
- About 800–1,500 words unless the user asks otherwise.

## Newsletter
Default for "newsletter", "beehiiv issue", "Kit broadcast" and "email to my list".
- 3 subject line options (short, under about 50 characters) and one preheader (under about 90 characters).
- Opening: 2–3 sentences in the sender's voice.
- 3–5 takeaways, 1–2 sentences each, with mm:ss.
- "You asked": 2–4 viewer questions the hosts answered on air, paraphrased, with the answer in brief. Never names, handles, "Person N" or "Attendee A". Questions that weren't answered are restream-analyze-chat's job.
- Replay call to action, then a sign-off.

## LinkedIn article
For LinkedIn's long-form articles only.
- Headline and a one-line subhead.
- 600–1,200 words, first person from the host the user names, short paragraphs, 3–4 subheads.
- 1–2 pull quotes with timestamps.
- Close with a question to readers and the replay link the user gives.
- No hashtag block; at most 3 hashtags, only if the user asks.

## Saving a draft to another app
Order: Restream reads, then coverage and checks, then the final draft, then the app. Load deferred tools before deciding an app is missing. Never write the app's own tool calls into this skill; the app's tools or the host's format skill do the mechanics.

| App | What gets created | Watch out |
|---|---|---|
| The host's own docs tool, Google Docs | a doc, through the doc ladder in companions.md | Load the host's docs or google-workspace skill first |
| Notion | a one-off page | Stream logs and numbers belong to restream-log-stream |
| Gmail | a draft addressed only to people the user names (default: the user) | Never sent from here; the user sends it from Gmail |
| beehiiv | a post draft; publishing happens in beehiiv | Writes may need a paid beehiiv plan; free plans are likely read-only |
| Kit | a broadcast draft | Kit's connector may need a paid Kit plan |
| WordPress.com | a draft post | Write tools may be missing from some builds; check what's loaded |
| Webflow | a CMS item saved as a draft | Ask which collection |
| HubSpot | a blog post or marketing email draft | Never touch contacts or lists |

- Key, duplicate search, preview, confirmation and read-back: exactly as SKILL.md step 9 says. One confirmation per write, naming the stream (title, local day, date, time, zone); an earlier yes never covers a later draft.
- This skill never publishes, sends or schedules. If asked, say: "I saved it as a draft. Publish or send it from <App> when you're ready."
- A vendor plan error: "<App> says this needs a paid <App> plan, so here's the draft as Markdown instead."
- No app, or the user didn't ask for one: Markdown, plus clean HTML for newsletters and CMS posts (only `h2`, `p`, `blockquote`, `ul`, `li`, `a`; no scripts or styles), in the same turn.
- Never put in any draft: Restream download or event links, IDs, viewer names or handles, or links copied from chat or the transcript. Instead of a recording link write "Recording available in Restream until <date>. Ask for a fresh download link (links expire)."
- Unattended runs may only create drafts the user set up during an attended run (recurring-runs.md). Never send or publish from one.
