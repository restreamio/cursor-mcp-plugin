#!/usr/bin/env python3
"""Turn Restream MCP read results into duplicate-free stream-log rows and pages.

Reads ONE JSON object on stdin (never from a file, so IDs never land on disk) and
prints JSON (default), CSV or Markdown on stdout. Standard library only.

Input shape (raw tool results can be pasted as they are):
{
  "timezone": "America/New_York",          # IANA name; UTC if missing
  "mode": "rows" | "pages",                # rows = Sheets/Airtable, pages = Notion/Docs
  "channels": <list_channels result or its "channels" list>,
  "streams": [{
      "event": <one event from list_user_events>,
      "viewers": <get_event_analytics_viewers result> | "plan" | "unchecked",
      "messages": <get_event_analytics_messages result> | "plan" | "unchecked",
      "destinations": [<destinations of the same-title draft clone>] | null,   # null = no clone found
      "cloneCreatedAt": "<the draft clone's createdAt ISO>" | null,
      "webinarChat": true | false | "incomplete",   # optional, older data only: chat had channelName "Webinar" (the
                                                   # Webinar page is normally in list_channels as platform "unknown",
                                                   # platformId 85; no chat read is needed then)
      "recordingKeptUntil": "<expiresAt ISO>" | "none" | "unchecked",
      "recordingNote": "original show's recording" | null,
      "clipsCount": 15 | "none" | "unchecked",
      "clips": [<clips from get_user_clips_project_details>] | null,
      "named": true | false                # the user named this exact stream
  }],
  "existing": [{"Stream key": "...", "Avg watching": ..., ...}]   # rows/pages already in the log
}

With no app connected, pass the user's uploaded or pasted sheet (or just its Stream key column) as
"existing" and use --new-only: the CSV then holds only keys the sheet doesn't have, so appending it
never adds a copy. A keys-only "existing" can't show changed numbers; use --only-changes only with
full rows.

"plan" = the tool returned a plan or add-on error (numbers become "not reported").
"none" = the list was read and has nothing for this stream.
"unchecked", null or a missing key = the read failed or wasn't made. A failed read is never a fact:
analytics that didn't load skip the stream (try again later); an unchecked recording or clips
list leaves that cell empty with a Note, and an update never overwrites it.
Clone destinations created more than 60 s after the clone are ignored (the list was edited later).
"warnings" also carries chat-only notices (restricted view, no viewer-reporting platform, columns the
log doesn't have): tell the user, never write them into the log.
"plan" compares only the columns present in each existing entry; columns the log lacks are listed
under "columnsNotInLog" (per item and overall), never counted as changes.

Output never contains IDs, page tokens or links: the run stops with an error if one leaks.
"""
import argparse
import csv
import io
import json
import re
import sys
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None

NR = "not reported"
COLUMNS = [
    "Date", "Start (UTC)", "Title", "Kind", "Duration (min)", "Platform", "Channel",
    "Avg watching", "Peak watching", "Views (as platform counts)", "Watch time (viewer-minutes)",
    "Chat messages", "Chatters", "Recording kept until", "Clips", "Note", "Stream key",
]
PAGE_PROPERTIES = [
    "Date", "Start (UTC)", "Kind", "Duration (min)", "Platforms", "Avg watching", "Peak watching",
    "Views (as platform counts)", "Watch time (viewer-minutes)", "Chat messages", "Chatters",
    "Recording kept until", "Clips", "Stream key",
]
COMPARE = [
    "Duration (min)", "Avg watching", "Peak watching", "Views (as platform counts)",
    "Watch time (viewer-minutes)", "Chat messages", "Chatters", "Recording kept until", "Clips",
]
LABELS = {
    "CustomRTMP": "Custom RTMP", "CustomSRT": "Custom SRT", "CustomWHIP": "Custom WHIP",
    "CustomHLSPush": "Custom HLS", "EmbedPlayer": "Embed player", "XPlatform": "X",
}
NO_VIEWERS = {"TikTok", "Instagram", "Custom RTMP", "Custom SRT", "Custom WHIP", "Custom HLS", "LinkedIn"}
NO_CHAT = {"TikTok", "Instagram", "Custom RTMP", "Custom SRT", "Custom WHIP", "Custom HLS", "Embed player"}
# "Facebook" below means a Facebook Page; Groups (no channelUrl) report neither viewers nor chat.
CHAT_CAPTURING = {"YouTube", "X", "Twitch", "Facebook", "LinkedIn", "Slack", "Restream Webinar"}
VIEWER_REPORTING = {"YouTube", "X", "Twitch", "Facebook", "Restream Webinar", "Embed player"}
UNKNOWN_PLATFORM = "Unknown platform"
NOT_LISTED = "a channel not in your channel list"
MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
DEFAULT_TITLES = [
    re.compile(r"^studio default draft$"),
    re.compile(r"^on-air with restream, (%s) \d{1,2}$" % MONTHS),
    re.compile(r"^live with restream, (%s) \d{1,2}$" % MONTHS),
    re.compile(r"^live (%s) \d{1,2}$" % MONTHS),
]
LATE_EDIT_SECONDS = 60
UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
LINK_MARKERS = ("x-amz-", "signature=", "restream.io/streams/", "studio.restream.io/", "token=")


def norm_title(text):
    text = (text or "").replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub("[–—]", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def match_key(key):
    return norm_title(str(key)).casefold()


def parse_time(value):
    if not value:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000 if value > 1e11 else value, tz=timezone.utc)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)


def get_zone(name, warnings):
    if not name or name.upper() == "UTC" or ZoneInfo is None:
        return timezone.utc, "UTC"
    try:
        return ZoneInfo(name), name
    except Exception:
        warnings.append("Unknown time zone '%s'; dates are in UTC." % name)
        return timezone.utc, "UTC"


def kind_of(event):
    source = event.get("source") or {}
    if source.get("type") == "upload_and_stream" and source.get("videoSourceType") == "recording":
        return "Replay"
    if source.get("videoSourceType") == "file" or source.get("playlistFileIds"):
        return "Pre-recorded"
    return "Live"


def skip_reason(event, seconds, named):
    if event.get("status") not in (None, "finished"):
        return "not finished"
    if seconds is None:
        return "never started"
    if named:
        return None
    if seconds < 300:
        return "test (under 5 min)"
    if any(p.match(norm_title(event.get("title")).casefold()) for p in DEFAULT_TITLES):
        return "default title (likely a test)"
    return None


def channel_map(raw):
    items = raw.get("channels", []) if isinstance(raw, dict) else (raw or [])
    return {str(c.get("id")): dict(c, _order=i) for i, c in enumerate(items)}


def analytics(value):
    """A result object, "plan" (plan or add-on error) or anything else = unchecked."""
    if isinstance(value, dict):
        return value, "ok"
    if value == "plan":
        return None, "plan"
    return None, "unchecked"


def on_destinations(dests, clone_created):
    """Workaround (review when: get_event returns destinations for finished events).

    Drop clone destinations added more than a minute after the clone: the user edited the draft later."""
    stamps = [parse_time(d.get("createdAt")) for d in dests if d.get("createdAt")]
    ref = parse_time(clone_created) or (min(stamps) if stamps else None)
    kept, late = [], 0
    for d in dests:
        made = parse_time(d.get("createdAt"))
        if ref and made and (made - ref).total_seconds() > LATE_EDIT_SECONDS:
            late += 1
        else:
            kept.append(d)
    return kept, late


def watch_divisor(total, minutes):
    """Workaround (review when: Restream documents the watchedTime unit).

    watchedTime is viewer-minutes today (about mean x minutes). If it is ever ~60x that,
    it is viewer-seconds, so divide by 60."""
    mean, watched = total.get("mean") or 0, total.get("watchedTime") or 0
    return 60 if mean > 0 and minutes > 0 and watched > 30 * mean * minutes else 1


def viewer_cells(platform, group, row, chat_count, watch_div):
    if row is None:
        return [NR] * 4, ["on (from the saved platform list); Restream returned no numbers"]
    mean, peak = row.get("mean") or 0, row.get("max") or 0
    views, peak_time = row.get("viewsTotal") or 0, row.get("peakTime") or 0
    watch = round((row.get("watchedTime") or 0) / watch_div)
    if group:
        return [NR] * 4, ["Facebook Groups don't report numbers to Restream"]
    if platform in NO_VIEWERS:
        note = "%s doesn't report viewers to Restream" % platform
        if isinstance(chat_count, int) and chat_count > 0:
            note += "; it had %d chat message%s" % (chat_count, "" if chat_count == 1 else "s")
        return [NR] * 4, [note]
    if mean == 0 and peak == 0 and views == 0:
        if peak_time == 0 or (isinstance(chat_count, int) and chat_count > 0):
            return [NR] * 4, ["no viewer numbers returned"]
        return [0, 0, 0, 0], ["0 counted"]
    notes = []
    if mean == 0 and peak == 0:
        avg_cell = peak_cell = watch_cell = NR
        notes.append("%s counted views but reported no concurrent viewers" % platform)
    else:
        avg_cell = mean if mean > 0 else "under 1"
        peak_cell = peak
        watch_cell = watch if watch > 0 else "too small to measure"
    views_cell = NR if views == 0 else views  # views 0 while concurrency > 0 = views not reported
    return [avg_cell, peak_cell, views_cell, watch_cell], notes


def chat_cells(platform, group, key, messages):
    """A chat-capturing channel with no messages row (or 0) is a real 0; any other channel
    without a positive count is "not reported" (analytics-coverage, rule 5)."""
    if group or platform in NO_CHAT or messages is None:
        return NR, NR
    found = (messages.get("byChannel") or {}).get(key) or {}
    count = found.get("messagesTotal") or 0
    if count > 0:
        return count, found.get("chattersTotal") or 0
    if platform in CHAT_CAPTURING:
        return 0, 0
    return NR, NR


def resolve_platforms(keys, channels, dests, webinar_chat):
    unknown = [k for k in keys if k not in channels]
    resolved = {}
    for key in keys:
        ch = channels.get(key)
        info = {"group": False, "url": "", "order": 10 ** 6, "note": ""}
        if ch and ch.get("platform") == "unknown":
            # ids-and-names: platform "unknown" with platformId 85 is the Restream Webinar page (listed since
            # 2026-10); "unknown" with any other platformId is a channel not in the user's channel list.
            if ch.get("platformId") == 85:
                info.update(platform="Restream Webinar", channel="Webinar page", order=ch["_order"])
            else:
                info.update(platform=UNKNOWN_PLATFORM, channel=NOT_LISTED, order=ch["_order"])
        elif ch:
            platform = LABELS.get(ch.get("platform"), ch.get("platform") or UNKNOWN_PLATFORM)
            info.update(platform=platform, channel=ch.get("displayName") or "", url=ch.get("channelUrl") or "",
                        group=platform == "Facebook" and not ch.get("channelUrl"), order=ch["_order"])
        elif (dests.get(key) or {}).get("platformId") == 85 or (not dests and len(unknown) == 1
                                                                and webinar_chat is True):
            info.update(platform="Restream Webinar", channel="Webinar page")
        else:
            info.update(platform=UNKNOWN_PLATFORM, channel=NOT_LISTED)
            if not dests and len(unknown) == 1 and webinar_chat == "incomplete":
                info["note"] = "Webinar check incomplete"
        info["key_channel"] = info["channel"]
        resolved[key] = info
    # Same platform + same display name: the channel cell stays verbatim, and only the Stream key
    # numbers the second one "(2)", in a stable order: by channel page, then by list_channels order
    # (Custom RTMP, Embed player and Facebook Groups have no channel page).
    seen = {}
    for key in sorted(keys, key=lambda k: (resolved[k]["platform"], resolved[k]["channel"], resolved[k]["url"],
                                           resolved[k]["order"], k)):
        info = resolved[key]
        pair = (info["platform"], info["channel"])
        seen[pair] = seen.get(pair, 0) + 1
        if seen[pair] > 1:
            info["key_channel"] = "%s (%d)" % (info["channel"], seen[pair])
    for info in resolved.values():
        if seen[(info["platform"], info["channel"])] > 1 and info["platform"] != UNKNOWN_PLATFORM:
            same = "same name as another %s channel" % info["platform"]
            info["note"] = "; ".join(n for n in (info["note"], same) if n)
    return resolved


def overview_names(infos):
    """ids-and-names overview rule for chat: a platform with more than 4 channels, or any name over
    about 40 characters, is shown as a count only ("Embed player · 6")."""
    by_platform = {}
    for info in infos:
        by_platform.setdefault(info["platform"], []).append(info["channel"])
    out = []
    for platform in sorted(by_platform):
        channels = by_platform[platform]
        names = sorted(set(channels))
        if len(channels) > 4 or any(len(n) > 40 for n in names):
            out.append("%s · %d" % (platform, len(channels)))
        else:
            out.extend("%s (%s)" % (platform, n) for n in names)
    return out


def viewer_notice(title, local_date, minutes, resolved, viewers, messages):
    """analytics-coverage, Free plan section. Chat-only notices: never written into the log."""
    if viewers is None or minutes < 10:
        return None
    by = viewers.get("byChannel") or {}

    def reporting(key):
        info = resolved.get(key)
        return bool(info) and info["platform"] in VIEWER_REPORTING and not info["group"]

    def all_zero(row):
        return not any((row or {}).get(f) for f in ("mean", "max", "viewsTotal", "peakTime"))

    if any(reporting(k) and not all_zero(v) for k, v in by.items()):
        return None
    chat_rows = (messages or {}).get("byChannel") or {}
    vr_chat = sum((v or {}).get("messagesTotal") or 0 for k, v in chat_rows.items() if reporting(k))
    m_total = (messages or {}).get("total") or {}
    if vr_chat > 0:
        return ("Restream returned no viewer numbers for '%s' (%s) while chat came through (%s messages from %s "
                "chatters). Tell the user with the restricted-view copy; never write a plan guess into the log."
                % (title, local_date, m_total.get("messagesTotal", vr_chat), m_total.get("chattersTotal", "?")))
    if resolved and not any(reporting(k) for k in resolved) and all(
            i["platform"] in NO_VIEWERS or i["group"] for i in resolved.values()):
        names = ", ".join(overview_names(resolved.values()))
        return ("None of the platforms '%s' (%s) went to (%s) report viewer numbers to Restream. "
                "Tell the user with the 'None report viewers' copy (not a plan limit)." % (title, local_date, names))
    return None


def top_clips(clips, limit=5):
    kept = []
    ordered = sorted(clips or [], key=lambda c: (not c.get("favouritedAt"), -(c.get("viralityScore") or 0)))
    for clip in ordered:
        s, e = clip.get("sourceStartSeconds") or 0, clip.get("sourceEndSeconds") or 0
        dup = False
        for other in kept:
            if (other.get("name") or "").casefold() == (clip.get("name") or "").casefold():
                dup = True
            elif other.get("createdAt") == clip.get("createdAt"):
                os_, oe = other.get("sourceStartSeconds") or 0, other.get("sourceEndSeconds") or 0
                overlap = min(e, oe) - max(s, os_)
                shorter = max(1, min(e - s, oe - os_))
                if abs(s - os_) <= 5 or overlap > 0.5 * shorter:
                    dup = True
        if not dup:
            kept.append(clip)
    return [{"name": c.get("name"), "score": c.get("viralityScore"), "favourite": bool(c.get("favouritedAt"))}
            for c in kept[:limit]], len(clips or []) - len(kept)


def build(data):
    warnings, skipped, rows, pages = [], [], [], []
    zone, zone_name = get_zone(data.get("timezone"), warnings)
    channels = channel_map(data.get("channels"))
    for item in data.get("streams") or []:
        event = item.get("event") or {}
        title = norm_title(event.get("title"))
        start, end = parse_time(event.get("startedAt")), parse_time(event.get("finishedAt"))
        seconds = (end - start).total_seconds() if start and end else None
        reason = skip_reason(event, seconds, item.get("named"))
        local_date = start.astimezone(zone).strftime("%Y-%m-%d") if start else ""
        if reason:
            skipped.append({"title": title, "date": local_date, "reason": reason})
            continue
        viewers, v_state = analytics(item.get("viewers"))
        messages, m_state = analytics(item.get("messages"))
        if "unchecked" in (v_state, m_state):
            skipped.append({"title": title, "date": local_date, "reason": "Restream didn't return numbers (try again later)"})
            warnings.append("Restream didn't return numbers for '%s' (%s); nothing is written for it. "
                            "List it for the user and log it on a later run." % (title, local_date))
            continue
        minutes = max(1, round(seconds / 60))
        base_key = "%s · %s" % (title, start.strftime("%Y-%m-%d %H:%M"))
        total = (viewers or {}).get("total") or {}
        watch_div = watch_divisor(total, minutes)
        if viewers is None:
            warnings.append("No viewer analytics for '%s' (%s) (plan or add-on error); its numbers say 'not reported'."
                            % (title, local_date))
        all_dests = item.get("destinations") or []
        on_dests, late = on_destinations(all_dests, item.get("cloneCreatedAt"))
        labels = {str(d.get("channelId")): d for d in all_dests}
        keys = sorted(set(map(str, ((viewers or {}).get("byChannel") or {}).keys()))
                      | {str(d.get("channelId")) for d in on_dests})
        resolved = resolve_platforms(keys, channels, labels, item.get("webinarChat"))
        unchecked, t_extra = [], []
        rec_value = item.get("recordingKeptUntil")
        kept_until = parse_time(rec_value) if rec_value not in (None, "none", "unchecked") else None
        if kept_until:
            recording = kept_until.astimezone(zone).strftime("%Y-%m-%d")
            if item.get("recordingNote"):
                recording += " (%s)" % item["recordingNote"]
        elif rec_value == "none":
            recording = "not in Restream recordings"
        else:
            recording = ""
            unchecked.append("Recording kept until")
            t_extra.append("Recording not checked")
        clips_value = item.get("clipsCount")
        if isinstance(clips_value, int) and not isinstance(clips_value, bool):
            clips_cell = clips_value
        elif clips_value == "none":
            clips_cell = "none"
        else:
            clips_cell = ""
            unchecked.append("Clips")
            t_extra.append("Clips not checked")
        common = {"Date": local_date, "Start (UTC)": start.strftime("%Y-%m-%d %H:%M"), "Title": title,
                  "Kind": kind_of(event), "Duration (min)": minutes, "Recording kept until": recording,
                  "Clips": clips_cell}
        platform_rows, has_x = [], False
        for key in sorted(keys, key=lambda k: (resolved[k]["platform"], resolved[k]["key_channel"])):
            info = resolved[key]
            platform, group = info["platform"], info["group"]
            has_x = has_x or platform == "X"
            chat, chatters = chat_cells(platform, group, key, messages)
            vrow = ((viewers or {}).get("byChannel") or {}).get(key)
            cells, notes = viewer_cells(platform, group, vrow, chat, watch_div)
            if info["note"]:
                notes.append(info["note"])
            row = dict(common, **{"Platform": platform, "Channel": info["channel"], "Avg watching": cells[0],
                                  "Peak watching": cells[1], "Views (as platform counts)": cells[2],
                                  "Watch time (viewer-minutes)": cells[3], "Chat messages": chat,
                                  "Chatters": chatters, "Note": "; ".join(notes),
                                  "Stream key": "%s · %s (%s)" % (base_key, platform, info["key_channel"]),
                                  "unchecked": list(unchecked)})
            platform_rows.append(row)
        notice = viewer_notice(title, local_date, minutes, resolved, viewers, messages)
        if notice:
            warnings.append(notice)
        t_mean, t_max, t_views = total.get("mean") or 0, total.get("max") or 0, total.get("viewsTotal") or 0
        t_notes = ["Totals cover only the platforms that report numbers"]
        if has_x:
            t_notes.append("views are as each platform counts them (X counts very differently), not people")
        if viewers is not None and t_mean == 0 and t_max == 0 and t_views == 0:
            t_cells = [NR] * 4
        elif viewers is None:
            t_cells = [NR] * 4
            t_notes.append("Restream returned no analytics for this stream")
        else:
            # Cell rules 3-5 apply to the totals too: "not reported" is never written as 0.
            watch = round((total.get("watchedTime") or 0) / watch_div)
            if t_mean == 0 and t_max == 0:
                t_cells = [NR, NR, t_views, NR]
                t_notes.append("views were counted but no concurrent viewers were reported")
            else:
                t_cells = [t_mean if t_mean > 0 else "under 1", t_max, t_views,
                           watch if watch > 0 else "too small to measure"]
            if t_views == 0:
                t_cells[2] = NR
                t_notes.append("none of these platforms reported views")
        m_total = dict((messages or {}).get("total") or {})
        if m_total.get("messagesTotal") == 0:
            m_total.setdefault("chattersTotal", 0)
        totals = dict(common, **{"Platform": "All platforms", "Channel": "total", "Avg watching": t_cells[0],
                                 "Peak watching": t_cells[1], "Views (as platform counts)": t_cells[2],
                                 "Watch time (viewer-minutes)": t_cells[3],
                                 "Chat messages": m_total.get("messagesTotal", NR) if messages is not None else NR,
                                 "Chatters": m_total.get("chattersTotal", NR) if messages is not None else NR,
                                 "Note": "; ".join(t_notes), "Stream key": "%s · All platforms" % base_key,
                                 "unchecked": list(unchecked)})
        if item.get("destinations") is None:
            totals["Note"] += "; platforms without analytics may be missing"
        if late:
            totals["Note"] += "; platform list saved after the show; may have changed since"
        if t_extra:
            totals["Note"] += "; " + "; ".join(t_extra)
        rows.append(totals)
        rows.extend(platform_rows)
        clips, merged = top_clips(item.get("clips"))
        props = {k: totals[k] for k in PAGE_PROPERTIES if k in totals and k != "Stream key"}
        props["Platforms"] = sorted({r["Platform"] for r in platform_rows})
        props["Stream key"] = base_key
        pages.append({"title": title, "key": base_key, "properties": props, "platformRows": platform_rows,
                      "totalsNote": totals["Note"], "topClips": clips, "clipsMerged": merged,
                      "unchecked": list(unchecked)})
    return {"timezone": zone_name, "rows": rows, "pages": pages, "skipped": skipped, "warnings": warnings}


def canon(value):
    """Compare what a sink stores with what we would write (Notion dates and numbers can't hold text)."""
    text = str(value if value is not None else "").strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}", text):
        return text[:10]
    low = text.casefold()
    if low in ("", "not reported", "not in restream recordings"):
        return ""
    if low == "none":
        low = "0"
    try:
        return repr(float(low.replace(",", "")))
    except ValueError:
        return low


def same(old, new):
    return canon(old) == canon(new)


def plan(result, existing, mode):
    have = {}
    for entry in existing or []:
        key = entry.get("Stream key") or entry.get("key")
        if key:
            have[match_key(key)] = entry
    items = result["rows"] if mode == "rows" else [dict(p["properties"], **{"Stream key": p["key"], "unchecked": p["unchecked"]})
                                                   for p in result["pages"]]
    out, counts = [], {"new": 0, "update": 0, "unchanged": 0}
    not_in_log = set()
    for item in items:
        old = have.get(match_key(item["Stream key"]))
        if old is None:
            action, changed, missing = "new", [], []
        else:
            # Compare only the columns the log actually has: a column the user's sheet or database
            # lacks (or a keys-only "existing") is reported apart, never as a changed number.
            # A cell this run couldn't check never counts as a change (an update leaves it as it is).
            missing = [c for c in COMPARE if c in item and c not in old]
            changed = [c for c in COMPARE if c in item and c in old and c not in item.get("unchecked", [])
                       and not same(old.get(c, ""), item[c])]
            action = "update" if changed else "unchanged"
            not_in_log.update(missing)
        counts[action] += 1
        out.append({"key": item["Stream key"], "action": action, "changed": changed, "columnsNotInLog": missing})
    return dict(counts, items=out, columnsNotInLog=[c for c in COMPARE if c in not_in_log])


def collect_ids(data):
    ids = set()
    for ch in channel_map(data.get("channels")).keys():
        ids.add(ch)
    for item in data.get("streams") or []:
        event = item.get("event") or {}
        if event.get("id"):
            ids.add(str(event["id"]))
        source = event.get("source") or {}
        if source.get("recordingSuid"):
            ids.add(str(source["recordingSuid"]))
        viewers = item.get("viewers") if isinstance(item.get("viewers"), dict) else {}
        ids.update(str(k) for k in (viewers.get("byChannel") or {}))
        for d in item.get("destinations") or []:
            ids.update(str(d.get(f)) for f in ("id", "eventId", "channelId") if d.get(f))
    return {i for i in ids if len(i) >= 6}


def leak_check(result, ids):
    def walk(value, path):
        if isinstance(value, dict):
            for k, v in value.items():
                walk(v, path + "." + str(k))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, "%s[%d]" % (path, i))
        elif isinstance(value, str):
            low = value.lower()
            if UUID_RE.search(value) or any(m in low for m in LINK_MARKERS) or any(i in value for i in ids):
                raise SystemExit("refusing to print: an ID or link would leak at %s" % path)
    walk(result, "output")


def plain(value):
    """Titles and names are untrusted: a leading = + - @ must never become a spreadsheet formula."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def to_csv(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows({k: plain(v) for k, v in r.items()} for r in rows)
    return buf.getvalue()


def to_markdown(rows):
    cols = [c for c in COLUMNS if c not in ("Start (UTC)",)]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(c, "")).replace("|", "/") for c in cols) + " |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--format", choices=["json", "csv", "md"], default="json")
    parser.add_argument("--only-changes", action="store_true", help="CSV/Markdown: only new or updated rows")
    parser.add_argument("--new-only", action="store_true",
                        help="CSV/Markdown: only rows whose key is not in existing (an append-only file; "
                             "existing may hold just the Stream key column)")
    args = parser.parse_args(argv)
    data = json.load(sys.stdin)
    result = build(data)
    mode = data.get("mode") or "rows"
    result["plan"] = plan(result, data.get("existing"), mode)
    if result["plan"]["columnsNotInLog"]:
        result["warnings"].append("Your log has no column for: %s. I compared the columns it does have; "
                                  "add these columns if you want them kept."
                                  % ", ".join(result["plan"]["columnsNotInLog"]))
    leak_check(result, collect_ids(data))
    rows = result["rows"]
    if args.only_changes or args.new_only:
        keep = ("new",) if args.new_only else ("new", "update")
        wanted = {match_key(i["key"]) for i in result["plan"]["items"] if i["action"] in keep}
        rows = [r for r in rows if match_key(r["Stream key"]) in wanted
                or match_key(r["Stream key"].rsplit(" · ", 1)[0]) in wanted]
    if args.format == "csv":
        sys.stdout.write(to_csv(rows))
    elif args.format == "md":
        sys.stdout.write(to_markdown(rows))
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
