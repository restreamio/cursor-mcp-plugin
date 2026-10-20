# What the Restream connector can't do

Read when: the user asks whether Restream can do something through this connector ("can Restream post to TikTok for me?", "can you pin a chat message?"), asks for something it can't do ("set up a Live Webinar with a registration page"), or gets the "what can I do" overview (Short list below).

Answer with the matching row, word for word. Never improvise a workaround yourself, and don't suggest other products unprompted; if the user asks for or names another tool, help as asked.

| Ask | Answer |
|---|---|
| Publish social posts | "I can't publish posts from here, but I can draft them: say 'write LinkedIn and X posts from my stream'. Restream Clips can post clips automatically with Autopost (250-clip tier): [See Restream Clips](https://restream.io/clips)." |
| Send or pin chat | "I can read the chat Restream collects (TikTok and Instagram chat isn't included), but I can't send or pin messages. Reply from Restream Chat or Restream Studio's chat panel." |
| Studio scenes, overlays, guests | "Studio controls aren't in the connector yet. Set them up in Restream Studio." |
| Ingest health, bitrate | "I can't see your encoder's live health; Restream's live health monitor shows it during the stream. To diagnose a problem, say 'my stream keeps dropping frames'." |
| Upload a video | "Uploads happen in Restream's video storage ([how to](https://support.restream.io/en/articles/13626308-schedule-your-video-as-a-pre-recorded-event)). Then say 'stream this uploaded video at 9am'." |
| Stream keys, connecting a channel | "Stream keys stay in your Restream dashboard. I can't see or share them. Connect channels in your Restream dashboard under Channels." |
| Create a webinar, read registrants | "I can't set up webinars or read registrants from here; that happens in Restream Webinars (an add-on). [See Restream Webinars](https://restream.io/webinars). Registrations export as a CSV there; follow-up from that CSV isn't available as a skill yet. For the webinar's chat questions, say 'which questions didn't we answer on my stream'." |
| Billing, plan changes | "Billing and plan changes happen in Restream's account settings. [See plans](https://restream.io/pricing)." |
| Team members, roles | "Members and roles are managed in Restream's workspace settings ([how it works](https://support.restream.io/en/articles/11003688))." |

- "Stream live to TikTok" is a destination, not a post: route it to restream-schedule-stream (new stream) or restream-manage-stream (existing stream).
- A capability that depends on the plan ("can I loop a video?", "can I get transcripts?"): answer from references/plans-and-paywalls.md "Workaround (review when: get_current_user returns plan and add-ons)": "<feature> comes with <unlock>. I can't see your plan from here; if Restream says no when we try, I'll tell you."
- If the named sibling isn't installed, say what it would do in one line and "that skill isn't installed in this app", then end on one thing this chat can do here with the connector (SKILL.md step 11). Never end the reply on the not-installed line.

## Short list (overview route)
Used word for word under **What I can't do from here** in the "what can I do" overview. One line each, no routing phrases:
- Control Studio scenes, overlays or guests (that's in Restream Studio).
- Send or pin chat messages.
- See or share stream keys, or connect new channels (that's in your Restream dashboard).
- See your encoder's live health or bitrate.
- Publish social posts for you.
