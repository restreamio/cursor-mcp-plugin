# Diagnose the actual streaming route

Use this reference for Restream method, destination, chat, eligibility, encoding, scheduling, or plan problems. The accompanying [streaming catalog](streaming-catalog.json) is a dated documentation snapshot, not observed account state. It covers four primary streaming families, 18 method/protocol/production variants, 36 named services, four custom destination types, and operational extensions. Ten services have catalog evidence only. Do not imply all 36 were tested or are available to every user.

## Retrieve only the relevant entries

Run the dependency-free lookup helper. Without Python, search the JSON for just the affected service's entry if your host can; otherwise use the symptom table below and the platform rules reference. Never load the whole JSON:

```bash
python3 <this skill's folder>/scripts/lookup_route.py instagram
python3 <this skill's folder>/scripts/lookup_route.py zoom
python3 <this skill's folder>/scripts/lookup_route.py srt
python3 <this skill's folder>/scripts/lookup_route.py --list
```

The helper returns route facts and their source records. `facebook` includes Profile/Page/Group variants. `zoom`, `srt`, `whip` and `rtmp` can have multiple directions; select the route the user actually has. Never choose the first match arbitrarily. `null` means unknown from reviewed documentation, not unsupported. The source access flag is a retrieval fact, not proof of a successful stream.

## Establish the route before changing it

Capture only information relevant to the failure:

1. **Production:** browser Studio, software/hardware encoder, uploaded video/playlist, or Live Webinar. For a mixed production, identify the encoder-to-Studio source separately.
2. **Input:** RTMP/RTMPS, SRT, WHIP, or browser/file production. Source credentials belong to a specific stream card or Studio source. Authorized OBS/vMix/LiveU/XSplit integrations can target Default RTMP rather than a separately scheduled card.
3. **Delivery:** exact destination, Profile/Page/Group variant, orientation, own versus paired channel, authorized versus manual connection, event identity and privacy.
4. **Control:** which product starts the feed, which control makes it public, and which product ends it. Restream preview is not proof a destination is public.

Do not ask the user to fill out all four categories when evidence already resolves them. While live, use observations and preserve working outputs. Existing authorization for a specific interruption persists; do not introduce repeated confirmation prompts.

## Choose the first discriminating observation

| Symptom | Useful first observation | Interpretation boundary |
|---|---|---|
| All destinations fail | Is the correct Restream card receiving the intended feed? | A healthy unrelated Default RTMP card does not establish the scheduled event is receiving video. |
| One destination has a preview but is offline | Its own producer controls, privacy and event state | Instagram, Telegram, Amazon Live, Facebook Groups and incoming Zoom have documented platform-side start steps. Manual TikTok differs from authorized access. |
| “Streaming not allowed” or no Live option | Platform eligibility and connection route | TikTok app access does not imply third-party access. Instagram Live Producer has public/follower/professional requirements. |
| Slack absent or won't attach | The exact error from the activation check or attach | Slack destinations are observed on Studio events too, so the catalog's "webinar add-on required" is not settled. Only when the error names a plan or add-on, send the Slack gate copy from [plans and paywalls](plans-and-paywalls.md) ("may need a paid plan or the Webinars add-on", read-only ending) and stop. Changing OBS bitrate will not expose it. |
| HLS link will not connect | Is it a provider ingest endpoint or a playback URL? | Custom HLS is an output destination, not proof of m3u8 source ingestion. |
| SRT encryption settings missing | Is this incoming or outgoing SRT? | Incoming AES capabilities do not establish per-destination output controls; the docs disagree about output passphrase fields. |
| Portrait looks landscape | Are portrait input and destination assignment both present? | OBS falls back to landscape without a vertical feed; paired Studio destinations use the primary landscape feed. |
| Chat missing but video works | Route-specific read/reply/relay matrix | Manual custom channels and several named channels have no integrated chat. Restream Facebook Profile chat is read-only; Groups differ. |
| Pre-recorded session fails | Cloud processing, file properties, event timezone, active destinations | The laptop can be offline during playout. Do not demand an OBS log or blame current laptop upload speed. |
| Recording is missing or partial | Cloud versus local, entitlement, retention, source inclusion, upload completion | Studio RTMP sources and graphics are excluded from local individual-source tracks. |
| Stream ends near a fixed duration | App, platform, file/playlist, recording and fallback limits separately | Larix app limits, Instagram session limits, expired fallback and recording truncation are different mechanisms. |
| New Teams event cannot be created | Legacy Live Event versus current Teams RTMP-In | The old Teams Live Events creation path retired June 30, 2026, with an exception for previously scheduled events. |

These are routing hypotheses, not proof of the cause. Confirm with the actual error, supplied evidence or account response.

## Build a compatible profile instead of prescribing a universal preset

For each intended output, read its entry and current official sources. Preserve the difference between recommendations, minimums, maximums, examples and undocumented values. Record codec, resolution, FPS, bitrate, keyframes, audio bitrate/sample rate/layout and orientation with units and route scope.

For one pass-through feed, seek the intersection of the applicable destination constraints. Unknown fields prevent a claim that the profile is fully verified. A recommendation mismatch is not proof a provider will reject the stream.

Examples of how the evidence changes the next action:

- **Dailymotion + LinkedIn:** Dailymotion publishes at least 192 Kbps AAC; LinkedIn’s Restream guide specifies at most 128 Kbps. Their sample-rate guidance also differs. No single audio bitrate meets both published values. Consider separately configured outputs or verified per-destination transcoding; confirm sample-rate capability, account eligibility and remaining hours. Do not quietly lower all channels to 128 Kbps or claim an automatic fix exists.
- **YouTube H.264:** use the H.264 recommendation column, not the AV1/HEVC min/max table. Platform-direct AV1 support does not prove the same codec works through Restream RTMP. Studio’s automatic output also differs from a manually configured encoder.
- **Instagram crop:** first identify Studio adaptation, dual orientation, encoder landscape or scheduled file. A bitrate change will not recover content outside a center crop.
- **Encoder load:** faster/lighter settings can reduce processing cost. Do not copy a generic article’s “slower preset” phrase as a way to reduce x264 load. Validate the actual encoder and bottleneck through the existing OBS playbook.

Do not change output encoding mid-show to resolve a documentation mismatch without evidence of a current problem and authorization for the resulting interruption. Prepare the target configuration and rollback for a rehearsal.

## Handle conflicts and refreshes explicitly

The catalog includes a `documentation_conflicts` ledger. Use platform-owner documentation for that platform’s current eligibility/ingest rules and Restream’s dedicated feature docs for Restream-specific behavior. A newer dedicated route can supersede a generic FAQ, but when two explicit claims disagree and dates/route scope do not resolve them, say so and verify with the actual account or provider.

Refresh volatile eligibility, plans, API access, beta status and numerical settings before prescribing them. If current browsing is unavailable, label values as a documentation snapshot dated by the catalog's `audit_date`, give a safe observation and name the missing verification. A source’s retrieval time is not its publication date.

Catalog-only services need the actual Add Channel UI, current provider setup and a non-secret error before specific advice. Do not interpret a redirect or HTTP 200 as verified operational support. Do not claim that a discontinued service is working or closed without authoritative evidence.

## Know what tools can establish

Read [MCP boundaries](mcp.md) for account checks. Restream MCP can discover channels/events, check API access and validate active-channel limits. Its 30-tool surface does not inspect OBS, repair devices, retrieve stream keys or expose detailed live ingest metrics.

Restream separately documents live bitrate/FPS and channel status through its UI and public API; these are not automatically MCP tools. Only use an API if an authorized capability and its real schema are available. Failover/backup state is not documented as available through that API. Do not infer transport health from viewer counts.

Finish with the existing skill’s evidence → one test → observable result → rollback loop. Account preparation, documentation review and simulated exercises are not completed live-stream tests.
