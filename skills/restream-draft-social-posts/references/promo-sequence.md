# Promo sequence (light preset)

Read when: the user wants to promote, announce or remind people about a scheduled Restream stream, or post that it's live or that the replay is up.

Status: **unvalidated.** The stages and times below are common practice, not measured on Restream data (review when: promo timing is tested on real shows). Say "a common pattern" if the user asks why.

## Stages (default: all four, as one numbered pack grouped by stage)
| Stage | Default post time | Goal | Platforms |
|---|---|---|---|
| Announce | When the user asks (now), or 2–7 days before | What, who, when, why watch | X, LinkedIn, Threads, Bluesky; Instagram and TikTok as story or post text |
| Reminder (T-1h) | `scheduledFor` − 1 hour | "Starting in an hour" + the watch link | X, Threads, Bluesky, Instagram and TikTok stories; on LinkedIn a comment on the LinkedIn event post, not a new post |
| We're live | Right after the stream actually starts, never before | "Live now" + where to watch | X (ask first, below), Threads, Bluesky, Instagram story |
| Replay | After the show, once the user has the replay link | The best moment + the replay link | All platforms the user names |

- Skip a stage whose time has already passed and say so: "It's less than an hour to the show, so I've skipped the announcement and started with the reminder."
- A user asking for one stage ("write the we're-live post") gets that stage only.
- Times: compute from `scheduledFor` (UTC). Show local time with the zone and UTC in brackets: "Thu, Oct 15, 10:00 AM EDT (14:00 UTC)". Use the offset in effect on the event's date. Times in the event description ("11 AM ET") name the audience's zone, not the user's; if they disagree with `scheduledFor`, ask: "The description says 11 AM ET, but Restream has the stream at <time>. Which is right?"
- Rescheduled since drafting: redo every time and say which posts changed.

## What Restream already posts (don't duplicate)
Read each destination's `externalUrl` from Restream MCP `list_event_destinations`, and name it through `list_channels` as "Platform (display name)".

| Platform | Created by Restream before go-live | What the promo does there |
|---|---|---|
| YouTube | Scheduled broadcast page (observed) | Share that page; no separate announcement needed on YouTube |
| Facebook Page | Facebook event (observed) | Share the event; a Group gets nothing (likely) |
| LinkedIn | LinkedIn event post (observed) | Reshare the event post with a hook; reminder as a comment on it |
| X | Broadcast link (observed); Restream may also post at go-live, sources conflict | Ask before writing a "we're live" X post (copy below) |
| Slack | Message in the chosen Slack channel (observed) | Nothing public; Slack links are private |
| TikTok, Instagram, Patreon | Nothing (`externalUrl` null) | These need the promo most: story or post text, and a Patreon post for members |
| Twitch, Kick, others | Likely nothing | Announce elsewhere; see the Twitch rule |

- X question: "Restream may post on X by itself when you go live. Want your own 'we're live' post on X too, or let Restream's stand?" (review when: Restream confirms X go-live posting)
- `externalUrl` null never means no post exists. Say: "Restream has no <Platform> link for this stream yet. Check <Platform> directly."

## Links per stage
- Use one public watch link per post: YouTube, Facebook, LinkedIn or X `externalUrl`, or a link the user typed.
- Two channels on one platform (two YouTube channels both carry the show): ask once, "Your stream has two YouTube pages, on YouTube (<name A>) and YouTube (<name B>). Which one should the posts point to?"
- Never: the event's `url` (it opens Restream Studio or the dashboard), a Slack link, a Restream download link, or a link from chat.
- Replay: ask with the "Replay link missing" copy: "Restream doesn't keep watch links once a show ends. Paste the replay link, or tell me which platform it's on and I'll point people to your channel page there." If the user names a platform, offer that platform's channel page from `list_channels`, as link text: "I'll point people to your channel page, <Platform> (<name>)." Two channels on that platform: ask which. Restream returns only part of the platform list for finished streams, so never pick the platform yourself.
- A "Replay: <title>" event in Restream is a scheduled re-air of a recording, not the on-demand replay. Promote it like any scheduled stream.

## Webinar streams
- A destination with `platform: "unknown"` and platformId 85 is the Restream Webinar page. It has no `externalUrl`. Ask: "This stream also goes to your Restream Webinar page. Paste its public registration link and I'll use it in the posts."
- Say once: "Restream Webinars doesn't send reminder emails yet, and I can't reach your registrants from here. These posts are for your social accounts." (review when: Restream Webinars ships attendee reminders or registrant tools reach the MCP)
- Don't suggest another registration page for a Restream Live Webinar, or creating events or email blasts in other tools, unprompted. If the user names a tool for that, help as asked under the companion rules.

## Twitch rule
When Twitch is in the set, anything written for Twitch itself (stream title, panels, chat messages, overlays) mentions no other platform and links nowhere else while the show is simulcast. Posts on X, LinkedIn and other networks may list Twitch with the rest.

## Output
A numbered pack grouped by stage, never a table (multi-line copy doesn't paste from a cell). Each post's text sits in its own plain-text copy box. Default: one or two posts per stage (X and LinkedIn, plus the story text for Instagram or TikTok when they're on); more only when asked.
````
Promo for "<title>" (<Thu, Oct 15, 11:00 AM EDT>) · watch link: [Watch on YouTube](<link>) · Restream has pages on: <platforms whose externalUrl is set>

Announce · post now
1. X (Restreamio) · 212/280 (weighted)
```text
<post text>
```
2. LinkedIn (Restream page) · reshare the event post · 640/3,000
```text
<post text>
```
Reminder · Thu, Oct 15, 10:00 AM EDT (14:00 UTC)
3. Instagram story · 96
```text
<post text>
```
We're live · right after the stream starts
4. …
Replay · once you have the replay link
5. …

Not posted anywhere. Copy each one at its time, or ask me to save them as Buffer drafts.
````
- In the "Restream has pages" line, list only this event's public destinations (YouTube, Facebook, LinkedIn, X) whose `externalUrl` is non-null. Never list Slack, and never claim a post exists from the generic table above.
- A skipped stage gets one line in its place ("Announce: skipped, the show is in under an hour").

## Copy patterns
- Announce: hook from the description's strongest promise, who's on, when (audience zone as written in the description), one link.
- Reminder: "In one hour: <topic> with <guest>. <one concrete thing they'll see>. {watch link}"
- We're live: "We're live: <topic>. <one line>. {watch link}" Post it only after the stream has started.
- Replay: lead with the best moment from the show (the highlights list or a clip), then "Full replay: {replay link}".
- Church services: service time, "join us live", and no worship-song lyrics quoted in posts.
