# Diagnostic playbook

Use the relevant branch only. Tests below are practical diagnostic experiments; source links substantiate the underlying behavior, not a promise that a specific test will solve a case.

| Symptom / evidence | First discriminating observation | Appropriate next experiment | What remains unknown |
|---|---|---|---|
| Network-drop counter increasing | Same interval, actual ingest route, competing upload | Pause a known nonessential upload; compare. Wired connection or lower compatible bitrate is a rehearsal test. | Which segment is constrained. A fast generic speed test does not settle this. |
| Rendering lag increasing | Same scene, game/GPU workload | Rehearse a game FPS cap or one simpler scene element; record original value. | Exact hardware bottleneck; do not diagnose defective GPU. |
| Encoding lag increasing in Stats | Confirm streaming encoder and concurrent recording/replay | Rehearse lower encoder workload compatible with hardware and destination. Change one variable. | Global log summary alone may belong to another output. |
| Multiple counters increase | Matched Stats snapshots during the fault | Isolate network and rendering separately; measure again after each change. | Whether one fault causes another. |
| Blurry video, stable counters | Source → full-size local program → actual player resolution | Test source focus/scaling first if blur is local; output configuration only if blur begins after encoding. | Motion complexity, transcoding, viewer adaptation; bitrate is not always the remedy. |
| Black local OBS picture | Source visible? Correct target? Covered? Minimized? Which OS/capture method? | Correct one source selection/visibility issue. Research the current capture guide for OS-specific failures. | A bitrate change cannot restore a missing source. |
| Browser camera/mic denied | Site permission, OS permission, selected device | Correct the denied permission; postpone any required reload until appropriate. | Another app may occupy device; missing hardware support is not proven. |
| No audio | Meter → mute → intended streaming track → player volume | Correct one missing route. Compare an existing matching-track recording if available. | A good recording using another track does not clear the streaming route. |
| Echo | Outgoing program or only monitor? Playback audible? Duplicate capture? | Mute playback return first. Then isolate duplicate sources one at a time; preserve intended program. | Acoustic echo and duplicated electronic routes need different fixes. |
| Constant A/V offset | Clap: identify earlier path and measure time difference | Delay the earlier path in rehearsal; verify clap alignment. Tool-specific offset signs require checking. | Not all software supports the same offset semantics. |
| Growing A/V drift | Clap at beginning and later; device path; changing load | Investigate timing/sample-rate configuration and capture path. | A fixed offset does not correct growing drift. Do not universally change 48 to 44.1 kHz. |
| One destination offline or degraded | Working destination; affected event/channel; exact platform error | Read enabled state, authorization, activation limits, then platform ingest notice. | Healthy local preview does not prove platform receipt. |
| All destinations offline | Is local sending active? Restream shows ingest? Exact error? | Locate first failed link before inspecting each destination. | Restream event tools do not expose the entire transport path. |
| Delay, but smooth audio/video | End-to-end delay versus A/V mismatch; platform latency mode | Compare source timestamp with player, then verify platform latency tradeoffs. | Ordinary player delay is not automatically encoding failure. |

## Evidence to collect

- OBS frames: View → Stats during the problem, or the affected attempt's local log (Help → Log Files), never a startup log or a published link. Never stop a live show for a final summary.
- Audio: input meter, mute, intended source, streaming track, monitoring paths. Sync: a visible clap and its sound at two points in time.
- Browser studio: selected device, site and OS permissions, participant role, stage inclusion, exact error text; no OBS Stats. A producer backstage may be off-program on purpose.
- Recording recovery: the original participant, device and profile, and each track's Recording, Uploading, Processing or Ready status. Local track quality is not livestream quality; a missing destination feed gets no recovery steps.
- Platform-only failures: the exact channel and the platform's control-room error beat audience analytics. Review excerpts before sharing; redaction is never guaranteed.

## Counter rules

- Network drops, rendering lag and encoding lag are different signals and can coexist. Never combine recording, replay-buffer, session, global and stream counters; missing metrics are unknown; old counters don't prove the current show is failing. No averaged percentages or "stream health score".
- Match the attempt to the problem time; with several, show their line ranges and ask which matters. Encoding summaries without a verified output mapping stay unattributed, even "Video stopped"; confirm streaming encoding lag in OBS Stats.
- Before any numeric encoder setting or OS control, verify current official requirements for that destination, codec, resolution/FPS, device and version; without browsing, give a conditional test and the doc link. No blanket "6000 kbps", "always 48 kHz", driver reinstalls or disabling security software. Several pass-through outputs or conflicting docs: follow route diagnosis (compatible profile, documentation conflicts), never a universal preset.
- Compare cumulative counters' increases over matched intervals: an old percentage can stay high after a fix, and an idle counter proves nothing. Pair counter changes with audio and video at the destination.

## Live constraints

Inspection comes first. Muting a playback tab is different from muting the program microphone. Changing network adapter, restarting a browser/router/OBS, editing capture devices, or reconnecting a channel may interrupt the show. A settings reset is not a first-line diagnostic. Do not suggest firewall/antivirus disablement from a generic network symptom.

Record original values before a change. Do not apply “fix bundles.” If a user has explicitly authorized an interruption, work within that scope. If not, prepare the concrete change for their review while completing read-only investigation.

## More discriminating comparisons

- Local recording: use matching source/track/output characteristics; recording itself can add load. A recorded file and a platform VOD are not interchangeable measurements.
- Counter comparison: collect start and end counts over an equal workload window. Do not subtract percentages or add rendering and encoding loss percentages.
- One viewer: test another device/network before changing the broadcaster's healthy setup.
- Mitigation versus cause: dynamic bitrate can reduce network drops by sacrificing image detail. If used, report the quality tradeoff; it does not identify the failed network segment.
- Escalation: give support enough context to reproduce, including time/timezone and which output was affected, without leaking stream credentials or private media URLs.
