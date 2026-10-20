# Plans and paywalls

Read when: a step touches a paid feature (channel count or type, transcripts, recordings, full analytics, Clips, looping, webinars), a Restream MCP tool returns a plan, add-on, credit or upgrade error, or the user asks what their plan includes.

## Rules (every skill)
1. You cannot see the user's plan or add-ons. Restream MCP `get_current_user` returns only the user, workspace and organization. Restream's API enforces every gate, so let the tool result decide.
2. Never state the user's plan as fact. Say "looks like your plan doesn't include …" only when a tool error says so. Never write a plan guess into a doc, sheet, log, calendar item or scheduled output.
3. When a tool returns a plan, add-on or credit error: send the gate copy below, then STOP that branch. No retry, no other route to the same result.
4. Never work around a gate yourself (see "Never work around a gate"). Don't suggest other products unprompted (see "Other products").
5. Never probe a gate with a write or a side-effect call. Do not call `create_event`, `toggle_event_channel_on`, `set_event_loop_count` or `create_user_clips_project` to "see if it works". Never call `list_event_transcriptions` on an event with no transcript just to test: it starts transcription, a paid feature.
6. The MCP itself works on every plan, Free included. Free for everyone: cross-platform chat, basic stream analytics, events and scheduling, channel health checks. Plan not stated (claim neither way): AI titles and descriptions, shareable analytics links. The dashboard may also have a CSV chat export; word it "Restream may also have a CSV chat export in the dashboard", never as fact (review when: checked in the dashboard).
7. Links: Markdown link text only, never a bare URL in user copy. For every plan gate link only [See plans](https://restream.io/pricing). Clips gates may link the product page [See Restream Clips](https://restream.io/clips), Webinars gates [See Restream Webinars](https://restream.io/webinars). Never link `upgradeUrl` or any checkout or upgrade flow.
8. Never quote prices, and never list plans with their channel caps. Asked about prices: "Current prices are on Restream's plans page: [See plans](https://restream.io/pricing)." Asked what their own plan allows: "That depends on your plan, which I can't see from here. [See plans](https://restream.io/pricing). Your current plan is in Restream's billing settings."

## Which Restream MCP tools touch which paid feature
| Paid feature | Tools | What unlocks it |
|---|---|---|
| Channels live at once | `check_event_channels_activation`, `toggle_event_channel_on`, `create_event` (channels) | A plan with more channels; see "Plan-limit message: channel limit" |
| Channel types | same tools | Facebook Page/Group and Custom RTMP: a paid plan. Custom SRT/HLS/WHIP and Embed player: Business. Slack: may need a paid plan or the Webinars add-on |
| Transcripts | `list_event_transcriptions` (starts one if none exist), `get_event_transcript` | A paid plan |
| Cloud recordings | `list_user_recordings`, `get_recording_download_url`, `create_event` eventType recording | Paid plans (likely), with a per-stream length cap and a retention period that vary by plan (likely) |
| Full analytics, Ask AI | `get_event_analytics_viewers`, `get_event_analytics_messages` | A paid plan; Free sees a restricted view |
| Clips | `list_user_clips_projects`, `get_user_clips_project_details`, `create_user_clip_download`; `create_user_clips_project` spends credits and is locked in v1 | Clips add-on (credits). Live clipping and auto-posting need its 250-clip tier |
| Looping | `set_event_loop_count`, `create_event` loopCount | Upload & Stream Marathon or Media. At most 10 loops and 40 hours in total, never endless. Never send loopCount 0 or above 10; omit it for one play. Whether it counts total plays or repeats after the first is unverified: confirm the plays you mean, then read back with `get_event` (review when: the write-semantics test reads loopCount back) |
| Pre-recorded video length | `create_event` eventType file, `list_user_storage_files` | Upload & Stream tier |
| Record only (Studio) | `create_event` studio with no channels, then the user picks "Record only" in Studio | Paid plans (likely) |
| Webinars | None. The MCP cannot create or read webinars or registrants. The webinar page is a listed channel ("Restream Webinar": platform "unknown", platformId 85, "Webinar"; references/ids-and-names.md) that can't be toggled from here | Webinars add-on |
| Vertical / dual output | `streamingOrientation` in any destination payload | Professional or higher (may) |
| More workspaces | `get_current_user` (one workspace per connection) | Workspaces add-on |

## Recognising a gate
- **Gate:** the result carries `upgradeUrl`, or its reason or message names a plan, an add-on, credits, a subscription or an upgrade (observed: reason `channels_count_too_much`). Use `upgradeUrl` only as this signal: never show or link it.
- **Not a gate:** "Restream could not complete this request right now. Try again later." It also comes back for a wrong or missing event. Use the calling skill's not-found or retry copy, never paywall copy.
- **Not a gate:** reason `can_not_activate_multiple_linkedin` is a LinkedIn rule. Say: "Restream allows only one LinkedIn channel at a time. Keep LinkedIn (<name A>) or LinkedIn (<name B>)?" No plans link.
- **Empty is not a gate:** no recording, transcript or clips project can mean the feature isn't on the plan, or just that none was made. State the fact with the "empty" copy below; never guess the plan.

## Gate copy
One block, then stop. Skills that write or set things up:
> "This needs <unlock>. <reason>. [<link text>](<link>). I stopped here so nothing was changed."

Read-only skills (reports, lookups, checks, exports):
> "This needs <unlock>. <reason>. [<link text>](<link>). Nothing was changed."

| Gate | <unlock> | <reason> | Link |
|---|---|---|---|
| Channel count | — | — | Use "Plan-limit message: channel limit" below instead of this template |
| Facebook Page or Group | a paid Restream plan | Restream streams to Facebook Pages and Groups on paid plans | [See plans](https://restream.io/pricing) |
| Custom RTMP, SRT, HLS or WHIP | a paid Restream plan (Business for Custom SRT and HLS, likely WHIP too) | Custom destinations come with paid plans | [See plans](https://restream.io/pricing) |
| Embed player | a Restream Business plan or higher | The Embed player is a Business feature | [See plans](https://restream.io/pricing) |
| Transcript | a paid Restream plan | Transcripts are made from cloud recordings, which come with paid plans | [See plans](https://restream.io/pricing) |
| Recording | a paid Restream plan | Restream saves cloud recordings on paid plans | [See plans](https://restream.io/pricing) |
| Full analytics | a paid Restream plan | Full per-platform analytics and Ask AI come with paid plans; free accounts see a restricted view | [See plans](https://restream.io/pricing) |
| Clips | the Restream Clips add-on | Clips finds your best moments and cuts them into short vertical clips with captions | [See Restream Clips](https://restream.io/clips) |
| Clips credits | more Clips credits | Your Clips credits for this period are used up; you can still pick from the clips you already have | [See Restream Clips](https://restream.io/clips) |
| Live clipping, auto-posting | the 250-clip tier of Restream Clips | Live clipping and auto-posting are only in that tier | [See Restream Clips](https://restream.io/clips) |
| Looping | the Upload & Stream Marathon or Media add-on | Looping a video is only included in those two tiers | [See plans](https://restream.io/pricing) |
| Video too long | a bigger Upload & Stream tier | This video is longer than your current tier can stream | [See plans](https://restream.io/pricing) |
| Webinars | the Restream Webinars add-on | Webinars with registration are sold as an add-on | [See Restream Webinars](https://restream.io/webinars) |
| Vertical / dual | a Professional plan or higher | Streaming vertical and horizontal at once is a Professional feature | [See plans](https://restream.io/pricing) |

Slack (wording stays "may"; review when: the write-semantics test runs):
> "Streaming to Slack may need a paid plan or the Webinars add-on; Restream's help lists Slack under Live Webinar. [See plans](https://restream.io/pricing) · [See Restream Webinars](https://restream.io/webinars). I stopped here so nothing was changed." (Read-only: end "Nothing was changed.")

After a channel-type gate (Facebook, Custom, Embed player, Slack) in a write skill, offer the in-plan path as the closing question: "Want me to drop <Platform (name)> and check again?" Re-check the complete new set before any toggle.

After the copy, you may offer ONE sibling job that needs no gated feature and is not a substitute for it. After a transcript gate: "how did my stream do" (numbers). Never: "a recap from chat instead".

Empty copy (no error, nothing found):
- No clips project: "I don't see any Restream Clips for that stream. Restream Clips (an add-on) finds the best moments and cuts short vertical clips with captions. [See Restream Clips](https://restream.io/clips)." Do not follow it with timestamps "to cut in your editor".
- No recording: "I don't see a recording of **<title>** in Restream. Cloud recordings likely come with paid plans and are kept for a limited time. [See plans](https://restream.io/pricing)."
- No recording, when a transcript was wanted: "I don't see a recording of **<title>** in Restream, so there's no transcript to read. Cloud recordings and transcripts likely come with paid plans. [See plans](https://restream.io/pricing)."
- Show ended under 30 minutes ago: no plans link, only "Restream may still be preparing the recording, transcript and clips. Ask me again in about half an hour."
- No viewer numbers on a real show, no error (the restricted view or numbers still settling; the test is in references/analytics-coverage.md): "Restream returned no viewer numbers for **<title>**. If this workspace is on the Free plan, Analytics shows a restricted view and full numbers come with a paid plan: [See plans](https://restream.io/pricing). Otherwise try again in an hour; Restream may still be adding them up." Never say the user is on Free.
- Webinar setup or registrants asked for: "I can't set up webinars or read registrants from here; that happens in Restream Webinars (an add-on). [See Restream Webinars](https://restream.io/webinars)."

## Plan-limit message: channel limit
Use it when `check_event_channels_activation` returns `channels_count_too_much`, or `toggle_event_channel_on` fails the same way.
- Write skills: "Restream won't allow this many channels at once on this account. [See plans](https://restream.io/pricing). Which channel should I drop so I can check again?" Re-check with the complete new set before any toggle.
- Read-only skills: "Restream won't allow this many channels at once on this account. [See plans](https://restream.io/pricing). Nothing was changed."
- Never infer or name the current plan, its cap or a plan that would cover the set: custom plans have other caps. Send the plan-limit message once per gate per conversation, one line, no pressure, and never inside a document written for someone else.

## Never work around a gate
Never work around a paid gate yourself: don't offer, start or build another route to the gated result. If the user pastes or uploads their own transcript, work with it. Forbidden substitutes you must never offer or start on your own:
- **Transcripts:** speech-to-text on a downloaded recording (a speech model, ffmpeg plus any STT, the host model "listening" to audio); another transcription service; platform auto-captions (YouTube, LinkedIn) used as the transcript; asking the user to dictate or re-record.
- **Clips:** a hand-made cut list or timestamps "to cut in your editor" offered in place of Clips; cutting the recording with ffmpeg or a script; sending the recording to another clipping tool; calling `create_user_clips_project` to test for credits.
- **Looping:** several back-to-back file events; telling the user to stitch the video N times into one file; loopCount 0, "continuous" or "24/7".
- **Channel count or type:** splitting channels across two events streamed at once; a Custom RTMP relay into a third-party restreamer to reach more platforms; toggling channels on after the check failed.
- **Analytics:** scraping Restream's dashboard or platform pages (browser or fetch) to fill a restricted view; estimating viewers from chat counts; writing "not reported" as 0.
- **Webinars:** building a registration page or form elsewhere; suggesting another webinar product.
- **Any gate:** another MCP tool or connector that reaches the same paid result; repeating the call hoping it passes; saying the MCP gives a paid feature "for free".
- When there is simply no recording or transcription failed (not a gate), you may offer to work from a transcript the user already has.

## Other products
Don't suggest other products unprompted. If the user asks for or names another tool, help them as asked (it's their data). If they want their own recording, transcript or chat file for it, that's restream-export-files.

## Ask AI overlap
Ask AI sits on one stream's Analytics page (paid plans) with presets "Stream summary", "Unanswered questions", "Areas for improvement" and "Vibe in the chat". It can't be exported and isn't reachable through the MCP.
- Lead with what it can't do: several streams at once, cross-platform comparisons, files and docs for other people, write-back to the user's tools, checking which questions were answered on air.
- Never make a single-stream summary or an unanswered-questions list the headline output. When asked for exactly that, deliver it in the skill's own shape (coverage line, cross-platform counts, answered-on-air check) and you may add once: "For quick follow-ups on this one stream, Ask AI on its Analytics page answers too."
- Chat is free. Whether chat summaries for Free accounts undercut paid Ask AI is undecided, so skills may continue (review when: product decides on chat summarisation for Free accounts).

## Workaround (review when: get_current_user returns plan and add-ons)
- Don't ask the user's plan as a precondition and don't pre-block. Run the read the user asked for and let Restream's answer decide.
- "Can I …?" about a paid feature: answer from the tables: "<feature> comes with <unlock>. I can't see your plan from here; if Restream says no when we try, I'll tell you."
- For writes, put the gate in the confirmation line instead of probing: "Looping is part of the Upload & Stream Marathon and Media add-ons; if your account doesn't have one, Restream will refuse it."

## Workaround (review when: check_event_channels_activation returns the numeric limit, every violation and documented reason codes)
- It reports only the first violation and never the number. After the user fixes that one (drops or swaps a channel), re-run with the complete new set; repeat until `canActivate` is true. Every re-check follows a user-approved change; never drop channels yourself to find the cap.
- It checks plan and platform rules only, not event state or stream health.
- Reason codes for paid Facebook, Custom RTMP/SRT/HLS and Embed player are undocumented. When the reason or message names a plan, an upgrade, or one of those channel types, use that channel-type row. When it names a per-event count for that type (such as a second Embed player), state it as a limit with no plans link.

## Unverified: keep "may" / "likely" wording
- Transcripts: the pricing page says Professional and up, the help center says any paid plan. Say "a paid plan" (review when: the two pages agree).
- Free accounts through the MCP: whether `list_event_transcriptions` refuses or starts transcription, whether analytics return the restricted view, whether `set_event_loop_count` checks the add-on (review when: the free-account test of all 30 tools runs).
- Vertical/dual may need Professional; record only and cloud recordings (and their caps) are likely paid-only; Clips likely needs a paid plan under the add-on; Slack may need a paid plan or the Webinars add-on (review when: pricing page re-check and write-semantics test).
