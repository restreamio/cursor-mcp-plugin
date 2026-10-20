# Official source register

The 2026-09-07 streaming-route expansion is in [streaming-catalog.json](streaming-catalog.json): 106 cited source records with URLs, retrieval metadata, method/destination facts and a documentation-conflict ledger. Read [route diagnosis](route-diagnosis.md) for applying it. The audit inventoried 238 help articles across 14 streaming-related collections and retrieved all 240 planned Restream sources, then cross-checked material issues with platform-owner documentation. Retrieval is distinct from fact extraction and operational verification. No customer telemetry or live-stream success measurements were collected.

This skill ships no troubleshooting modules for other production apps. Once the user names one, use that product's own official help pages; for a recording that didn't show up or finish uploading there, point to the vendor's own upload-recovery article in one line and keep the preserve-unfinished-recordings gate.

Reviewed 2026-09-06. Refresh applicable pages before numerical or OS/version-specific prescriptions. These sources explain mechanisms; the skill's selection of one controlled test and its live/rehearsal guard are product design decisions. No user stream was inspected during development.

| Source | What it supports / limitation |
|---|---|
| [OBS: stream connection troubleshooting](https://obsproject.com/kb/stream-connection-troubleshooting) | Delivery drops, route and upload constraints, dynamic bitrate tradeoff. Several listed actions interrupt streams or change security settings; do not copy its entire checklist into a live workflow. |
| [OBS: encoding performance](https://obsproject.com/kb/encoding-performance-troubleshooting) | GPU compositing load, game frame caps, scene complexity and output workload. Windows administrator launch requires restarting OBS; older Windows advice is not universal. |
| [OBS output implementation](https://github.com/obsproject/obs-studio/blob/master/libobs/obs-output.c) | Network/render metric wording, different denominators and conditional emission. Moving source branch; does not prove every historical/plugin log format. |
| [OBS: multiple audio tracks](https://obsproject.com/kb/multiple-audio-track-recording-guide) | Source-to-track assignment. Audibility on one recorded track does not prove that a different streaming track includes the source. |
| [Restream: encoder has no audio](https://support.restream.io/en/articles/3928640-my-encoder-s-stream-has-no-audio) | Local versus streamed audio isolation. A recording must use the relevant source/track to be a meaningful comparison. |
| [Restream: encoder echo](https://support.restream.io/en/articles/3928642-my-encoder-s-stream-has-an-echo) | Playback return and headphone checks. The skill additionally investigates duplicate routes rather than assuming all echo is acoustic. |
| [Restream: audio/video sync](https://support.restream.io/en/articles/3928645-my-encoder-s-audio-and-video-aren-t-synced) | Local comparison and offset controls. Its device/service caveat about 48 kHz is not evidence that all 48 kHz streaming is invalid. Measure direction and drift first. |
| [Restream: Studio camera](https://support.restream.io/en/articles/2784907-my-camera-doesn-t-work-in-studio) | Browser and OS permission diagnosis. Reload/restart recommendations are deferred during a live show. |
| [Restream: Studio microphone](https://support.restream.io/en/articles/4354617-my-microphone-doesn-t-work-in-studio) | Permission and device-access checks, separate from OBS track routing. |
| [Restream: platform-specific quality](https://support.restream.io/en/articles/2972717-my-quality-is-bad-on-some-platforms) | Destination requirements can differ. One working destination is a useful comparison, not a guarantee about others. |
| [YouTube: encoder settings](https://support.google.com/youtube/answer/2853702?hl=en) | Bitrate recommendations vary with codec, resolution and FPS; audio guidance varies by channel layout. Direct ingestion support does not guarantee support through Restream. |
| [YouTube: latency](https://support.google.com/youtube/answer/7444635?hl=en) | Distinguishes end-to-end latency from audio/video synchronization. Consult live for current options. |
| [Restream MCP](https://developers.restream.io/mcp-server) | Account/event/destination reads and their limits; no documented local-device diagnosis. |

## Research conclusions

A useful skill does more than phrase an MCP call: it chooses evidence, separates output scopes, controls the order of experiments, preserves a live broadcast, and verifies the original symptom. Local diagnosis works without account connection. Restream adds value specifically when the first failed link is an account, event or destination configuration.

Do not describe synthetic examples as customer cases, successful parser tests as proven real-world resolution, or suggested search topics as Google Trends findings. No Google Trends dataset or calibrated adoption/viral prediction informs this diagnostic tool.
