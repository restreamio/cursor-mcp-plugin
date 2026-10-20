#!/usr/bin/env python3
"""Draw a Restream stream report as charts. Standard library only; SVG inline in one light, phone-width HTML page.

Usage:
    python3 chart.py report    spec.json out_dir   # the full page: tiles + 5 charts -> report.html, *.svg, report.md
    python3 chart.py text      spec.json           # the same report as Markdown with text bars (hosts that render nothing)
    python3 chart.py trend     spec.json out_dir   # one chart: average and peak per show        -> chart.svg, chart.html
    python3 chart.py platforms spec.json out_dir   # one chart: average per platform (share)     -> chart.svg, chart.html

Every number comes from the spec, and the spec is filled only from Restream tool results. The script never invents,
estimates or interpolates a value. It only adds arithmetic the page labels as calculated: deltas vs the previous show,
shares of the average, viewer-hours from viewer-minutes, messages per minute from the counts given.

Value rules (every numeric field):
    a number      reported by Restream
    null          not reported by the platform; drawn as a labelled gap, never as 0, never in totals or averages
    "not on"      the platform was not attached to that show (only in `previous_avg`)
    0             a real zero (for example 0 chat messages on a chat-capturing platform)

Report spec (`report` and `text` modes):
{
  "workspace": "My Workspace",
  "timezone": "EDT",                                   # the zone every local time in the spec is written in
  "show": {"title": "Build a Webinar Stack in One Hour", "date_local": "Wed, Sep 30, 2026",
           "start_local": "4:04 PM", "duration_min": 86},
  "previous": {"title": "Grok Bot for streaming: 7 must-try templates", "date_local": "Wed, Sep 16, 2026",
               "duration_min": 91} | null,            # the previous comparable show; null = no delta anywhere
  "headline": {                                        # from analytics `total` (never rebuilt from rows)
    "avg": 233, "peak": 385, "peak_time_local": "4:44 PM", "peak_min": 39,
    "chat_events": 137,                                # messagesTotal as Restream counts it (includes X likes/follows)
    "chat_messages": 100,                              # optional: live-phase messages after paging (reactions, host and pre-show out)
    "x_reactions": null,                               # X likes/follows counted while paging; null = chat not paged, 0 = none
    "watch_minutes": 20038,                            # watchedTime in viewer-minutes; the page shows viewer-hours
    "previous": {"avg": 312, "peak": 575, "chat_events": 80, "x_reactions": null, "watch_minutes": 28392} | null
  },
  "trend": [                                           # the last N real live shows, oldest first, N <= 8; `current` marks the show
    {"date": "Aug 19", "title": "Professional Live Video, As Easy As a Video Call", "avg": 31, "peak": 59},
    {"date": "Sep 30", "title": "Build a Webinar Stack in One Hour", "avg": 233, "peak": 385, "current": true}
  ],
  "platforms": [                                       # one row per analytics key, biggest average first
    {"label": "X (Restreamio)", "avg": 214, "peak": 367, "chat": 70, "previous_avg": 294},
    {"label": "LinkedIn (Restream)", "avg": null, "peak": null, "chat": 3, "previous_avg": null},
    {"label": "Restream Webinar", "avg": 6, "peak": 9, "chat": 18, "previous_avg": "not on"}
  ],
  "chat_timeline": {                                   # from paging the chat, or from chat_file.py; omit or null when the chat was not read
    "bucket_min": 1,                                   # 1 for shows up to 90 min, else 2
    "counts": [1, 7, 2, ...],                          # messages per bucket from startedAt; reactions, host and pre-show excluded
                                                       # Hand-off for long chats (over 300 messages, shell hosts): run
                                                       #   python3 <restream-analyze-chat folder>/scripts/chat_file.py <chat file> \
                                                       #       --start <startedAt> --end <finishedAt> --json
                                                       # and copy its per_minute.counts, per_minute.bucket_min and per_minute.excluded
                                                       # here unchanged; its totals give chat_messages and x_reactions above.
    "peak_min": 39,                                    # the viewer peak, minutes into the show (null = no viewer peak)
    "on_air": "the hosts opened the webinar page" | null,  # what was on air at the peak, only when a transcript was read
    "excluded": {"reactions": 37, "x_reactions": 0, "host": 3, "pre_show": 3, "post_show": 0}
  } | null,
  "takeaway": "X carried 92% of the audience; chat was busiest in the first 10 minutes.",
  "notes": ["Views are not people: X counted 19,002 views against 214 watching at once."],   # at most 3 one-liners
  "skipped_tests": 4                                   # short test streams passed over while listing (0 = none)
}

Single-chart specs (`trend` and `platforms` modes) take either the report spec above (the matching section is used)
or the short form {"title": "...", "rows": [{"label": "Sep 16", "avg": 312, "peak": 575}, ...]}.

Outputs (report mode), all inside out_dir: report.html (everything inline), report.md (the text version),
trend.svg, platform-share.svg, chat-over-time.svg, chat-vs-viewers.svg, vs-last-time.svg (only the charts that had data).
Prints the paths as JSON.
"""
import html
import json
import os
import sys

W = 680
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Arial, sans-serif"
INK, DIM, GRID, PAPER = "#1b1b1f", "#6b6b73", "#e8e8ec", "#ffffff"
C_AVG, C_PEAK, C_CHAT, C_PREV, C_NOW, C_GAP = "#2f6df6", "#aac2fb", "#f08c2e", "#c9ccd6", "#2f6df6", "#f2f2f5"

NOT_ON = "not on"


def esc(s):
    return html.escape(str(s), quote=True)


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def hrs(minutes):
    """Viewer-minutes to viewer-hours: whole hours from 10 up, one decimal below."""
    if not num(minutes):
        return None
    h = minutes / 60
    return round(h) if h >= 10 else round(h, 1)


def fmt(v, unit=""):
    if num(v):
        s = f"{v:,.1f}" if isinstance(v, float) and v != int(v) else f"{int(round(v)):,}"
        return s + unit
    return NOT_ON if v == NOT_ON else "not reported"


def avg_word(avg, peak):
    """Restream rounds `mean` down: 0 with a peak above 0 is 'under 1', never '0'."""
    if num(avg) and avg == 0 and num(peak) and peak > 0:
        return "under 1"
    return fmt(avg)


def share_text(avg, total_avg):
    """'92%' of the total average; '<1%' for tiny rows; '' when either side is missing. Calculated, never reported."""
    if num(avg) and num(total_avg) and total_avg > 0 and avg > 0:
        pct = avg / total_avg * 100
        return f" · {round(pct)}%" if pct >= 0.5 else " · <1%"
    return ""


def delta(now, before):
    """Percent change, or None when either side is missing. Labelled 'calculated' on the page."""
    if num(now) and num(before) and before > 0:
        return round((now - before) / before * 100)
    return None


def delta_text(d, suffix=""):
    if d is None:
        return ""
    arrow = "▲" if d > 0 else ("▼" if d < 0 else "▬")
    return f"{arrow} {abs(d)}%{suffix}"


def svg_open(h, title, caption=None):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
           f'font-family="{FONT}" role="img" aria-label="{esc(title)}">',
           f'<rect width="{W}" height="{h}" fill="{PAPER}"/>',
           f'<text x="20" y="30" font-size="17" font-weight="600" fill="{INK}">{esc(title)}</text>']
    if caption:
        out.append(f'<text x="20" y="50" font-size="12" fill="{DIM}">{esc(caption)}</text>')
    return out


def legend(out, x, y, items):
    for color, name in items:
        out.append(f'<rect x="{x}" y="{y - 9}" width="11" height="11" rx="2" fill="{color}"/>')
        out.append(f'<text x="{x + 16}" y="{y}" font-size="11" fill="{DIM}">{esc(name)}</text>')
        x += 16 + 7 * len(name) + 14


def hbars(out, rows, top, row_h, label_w, series, vmax, right_pad=20):
    """Horizontal grouped bars. rows: list of (label, [values per series], [display text per series]).
    series: list of (color, name). Each series scales to vmax[i]. None values get a labelled gap."""
    x0 = 20 + label_w
    bar_w = W - x0 - right_pad - 110
    n = len(series)
    bh = max(10, (row_h - 8) // n)
    for i, (label, values, texts) in enumerate(rows):
        y = top + i * row_h
        out.append(f'<text x="20" y="{y + row_h / 2 + 4:.1f}" font-size="12.5" fill="{INK}">{esc(label)}</text>')
        for j, v in enumerate(values):
            by = y + 4 + j * bh
            color = series[j][0]
            if num(v):
                w = max(2, round(bar_w * v / vmax[j])) if vmax[j] else 2
                out.append(f'<rect x="{x0}" y="{by}" width="{w}" height="{bh - 2}" rx="3" fill="{color}"/>')
                out.append(f'<text x="{x0 + w + 6}" y="{by + bh / 2 + 3:.1f}" font-size="11" fill="{INK}">{esc(texts[j])}</text>')
            else:
                out.append(f'<rect x="{x0}" y="{by}" width="{bar_w}" height="{bh - 2}" rx="3" fill="{C_GAP}" stroke="{GRID}" stroke-dasharray="3 3"/>')
                out.append(f'<text x="{x0 + 8}" y="{by + bh / 2 + 3:.1f}" font-size="11" fill="{DIM}" font-style="italic">{esc(fmt(v))}</text>')


# ---------------------------------------------------------------- charts

def trend_svg(rows, title="Last shows: watching at once"):
    h, top, bottom, left, right = 300, 70, 56, 56, 24
    pw, ph = W - left - right, h - top - bottom
    vals = [r.get(k) for r in rows for k in ("avg", "peak") if num(r.get(k))]
    vmax = max(vals) if vals else 1
    n = max(1, len(rows) - 1)

    def xy(i, v):
        return left + pw * i / n, top + ph - ph * v / vmax

    out = svg_open(h, title, "Average and peak watching at once per show (real live shows only)")
    legend(out, W - 200, 30, [(C_AVG, "average"), (C_PEAK, "peak")])
    for g in range(5):
        v = vmax * g / 4
        y = top + ph - ph * g / 4
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="{GRID}"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" font-size="11" fill="{DIM}" text-anchor="end">{round(v):,}</text>')
    for key, color in (("peak", C_PEAK), ("avg", C_AVG)):
        segs, seg = [], []
        for i, r in enumerate(rows):
            if num(r.get(key)):
                seg.append((i, r[key]))
            else:
                segs.append(seg)
                seg = []
        segs.append(seg)
        for seg in segs:
            if len(seg) >= 2:
                d = " ".join(f"{'M' if j == 0 else 'L'}{xy(i, v)[0]:.1f},{xy(i, v)[1]:.1f}" for j, (i, v) in enumerate(seg))
                out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.5"/>')
    for i, r in enumerate(rows):
        x = xy(i, 0)[0]
        cur = bool(r.get("current"))
        if cur:
            out.append(f'<rect x="{x - 16:.1f}" y="{top - 6}" width="32" height="{ph + 12}" rx="6" fill="{C_NOW}" opacity="0.07"/>')
        for key, color in (("peak", C_PEAK), ("avg", C_AVG)):
            v = r.get(key)
            if num(v):
                px, py = xy(i, v)
                out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{6 if cur else 4}" fill="{color}" stroke="{PAPER}" stroke-width="1.5">'
                           f'<title>{esc(r.get("title", ""))} · {esc(r.get("date", ""))}: {key} {fmt(v)}</title></circle>')
                if key == "avg":
                    out.append(f'<text x="{px:.1f}" y="{py - 10:.1f}" font-size="11" font-weight="{600 if cur else 400}" fill="{INK}" text-anchor="middle">{fmt(v)}</text>')
            elif key == "avg":
                out.append(f'<text x="{x:.1f}" y="{top + ph / 2:.1f}" font-size="10" fill="{DIM}" text-anchor="middle" font-style="italic">not reported</text>')
        out.append(f'<text x="{x:.1f}" y="{h - bottom + 20}" font-size="11" font-weight="{600 if cur else 400}" fill="{INK if cur else DIM}" text-anchor="middle">{esc(r.get("date", ""))}</text>')
        if cur:
            out.append(f'<text x="{x:.1f}" y="{h - bottom + 34}" font-size="10" fill="{C_NOW}" text-anchor="middle">this show</text>')
    out.append(f'<text x="20" y="{h - 10}" font-size="10.5" fill="{DIM}">Hover a point for the show title. Source: Restream Analytics.</text>')
    out.append("</svg>")
    return "\n".join(out)


def share_svg(platforms, total_avg):
    reporting = [p for p in platforms if num(p.get("avg")) or num(p.get("peak"))]
    silent = [p for p in platforms if p not in reporting]
    row_h, top = 30, 66
    h = top + row_h * max(1, len(reporting)) + 34 + 16 * len(silent) + 26
    out = svg_open(h, "Who brought the audience", "Average watching at once per platform, with its share of the total average")
    vmax = max([p["avg"] for p in reporting if num(p.get("avg"))] or [1])
    rows = []
    for p in reporting:
        avg = p.get("avg")
        share = share_text(avg, total_avg)
        rows.append((p["label"], [f"{avg_word(avg, p.get('peak'))}{share}" if num(avg) else None]))
    # hbars wants numbers to size the bar and strings to print: pass both
    sized = [(lbl, [p.get("avg") if num(p.get("avg")) else None]) for (lbl, _), p in zip(rows, reporting)]
    x0, bar_w = 20 + 190, W - 20 - 190 - 20 - 110
    for i, ((label, vals), (_, texts)) in enumerate(zip(sized, rows)):
        y = top + i * row_h
        out.append(f'<text x="20" y="{y + 19}" font-size="12.5" fill="{INK}">{esc(label)}</text>')
        v = vals[0]
        if num(v):
            w = max(3, round(bar_w * v / vmax))
            out.append(f'<rect x="{x0}" y="{y + 6}" width="{w}" height="18" rx="3" fill="{C_AVG}"/>')
            out.append(f'<text x="{x0 + w + 6}" y="{y + 19}" font-size="11" fill="{INK}">{esc(texts[0])}</text>')
        else:
            out.append(f'<rect x="{x0}" y="{y + 6}" width="{bar_w}" height="18" rx="3" fill="{C_GAP}" stroke="{GRID}" stroke-dasharray="3 3"/>')
            out.append(f'<text x="{x0 + 8}" y="{y + 19}" font-size="11" fill="{DIM}" font-style="italic">not reported</text>')
    y = top + row_h * max(1, len(reporting)) + 14
    if silent:
        out.append(f'<text x="20" y="{y}" font-size="11.5" fill="{DIM}">Not reported by the platform (not 0):</text>')
        for p in silent:
            y += 16
            chat = p.get("chat")
            chat_txt = f"{fmt(chat)} chat messages" if num(chat) else "chat not reported"
            out.append(f'<text x="32" y="{y}" font-size="11.5" fill="{INK}">{esc(p["label"])} <tspan fill="{DIM}">· {esc(chat_txt)}</tspan></text>')
    out.append(f'<text x="20" y="{h - 10}" font-size="10.5" fill="{DIM}">Shares are calculated from the average (not views). Totals cover only the platforms that report numbers.</text>')
    out.append("</svg>")
    return "\n".join(out)


def chat_time_svg(ct, peak_time_local=None, timezone=""):
    counts = ct.get("counts") or []
    bucket = ct.get("bucket_min") or 1
    h, top, bottom, left, right = 300, 70, 66, 44, 20
    pw, ph = W - left - right, h - top - bottom
    n = max(1, len(counts))
    vmax = max([c for c in counts if num(c)] or [1])
    title = "Chat over time"
    out = svg_open(h, title, f"Messages per {bucket} min from the start of the show · reactions, host links and pre-show chat left out")
    for g in range(4):
        v = vmax * g / 3
        y = top + ph - ph * g / 3
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="{GRID}"/>')
        out.append(f'<text x="{left - 6}" y="{y + 4:.1f}" font-size="11" fill="{DIM}" text-anchor="end">{round(v)}</text>')
    bw = pw / n
    for i, c in enumerate(counts):
        x = left + i * bw
        if num(c):
            bh = ph * c / vmax
            out.append(f'<rect x="{x + 0.5:.1f}" y="{top + ph - bh:.1f}" width="{max(1, bw - 1):.1f}" height="{bh:.1f}" fill="{C_CHAT}">'
                       f'<title>{i * bucket}–{(i + 1) * bucket} min: {c} messages</title></rect>')
        else:
            out.append(f'<rect x="{x + 0.5:.1f}" y="{top}" width="{max(1, bw - 1):.1f}" height="{ph}" fill="{C_GAP}"><title>{i * bucket}–{(i + 1) * bucket} min: not read</title></rect>')
    span = n * bucket
    step = 10 if span <= 120 else 20
    m = 0
    while m <= span:
        x = left + pw * m / span
        out.append(f'<text x="{x:.1f}" y="{h - bottom + 18}" font-size="11" fill="{DIM}" text-anchor="middle">{m}</text>')
        m += step
    out.append(f'<text x="{W - right}" y="{h - bottom + 34}" font-size="10.5" fill="{DIM}" text-anchor="end">minutes into the show</text>')
    pk = ct.get("peak_min")
    if num(pk):
        x = left + pw * min(pk, span) / span
        out.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{top + ph}" stroke="{C_AVG}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        label = f"viewer peak · {pk} min" + (f" · {peak_time_local} {timezone}".rstrip() if peak_time_local else "")
        anchor = "end" if x > W * 0.6 else "start"
        dx = -6 if anchor == "end" else 6
        out.append(f'<text x="{x + dx:.1f}" y="{top + 12}" font-size="11" font-weight="600" fill="{C_AVG}" text-anchor="{anchor}">{esc(label)}</text>')
        if ct.get("on_air"):
            out.append(f'<text x="{x + dx:.1f}" y="{top + 26}" font-size="10.5" fill="{DIM}" text-anchor="{anchor}">on air: {esc(ct["on_air"])}</text>')
    out.append(f'<text x="20" y="{h - 10}" font-size="10.5" fill="{DIM}">Chat is a stand-in for activity: Restream returns no viewer timeline, and TikTok and Instagram chat isn\'t captured.</text>')
    out.append("</svg>")
    return "\n".join(out)


def chat_vs_viewers_svg(platforms):
    rows = [p for p in platforms if num(p.get("avg")) or num(p.get("chat"))]
    row_h, top = 44, 66
    h = top + row_h * max(1, len(rows)) + 30
    out = svg_open(h, "Chat vs viewers, per platform", "Average watching at once next to chat messages; each bar is scaled to its own column")
    legend(out, W - 250, 30, [(C_AVG, "avg watching"), (C_CHAT, "chat messages")])
    vmax = [max([p["avg"] for p in rows if num(p.get("avg"))] or [1]), max([p["chat"] for p in rows if num(p.get("chat"))] or [1])]
    data = [(p["label"], [p.get("avg"), p.get("chat")], [avg_word(p.get("avg"), p.get("peak")), fmt(p.get("chat"))]) for p in rows]
    hbars(out, data, top, row_h, 190, [(C_AVG, "avg"), (C_CHAT, "chat")], vmax)
    out.append(f'<text x="20" y="{h - 10}" font-size="10.5" fill="{DIM}">A small platform with lots of chat is worth a look. Chat counts can include reactions where Restream counts them.</text>')
    out.append("</svg>")
    return "\n".join(out)


def vs_last_svg(platforms, previous):
    rows = [p for p in platforms if "previous_avg" in p and (num(p.get("avg")) or num(p.get("previous_avg")))]
    row_h, top = 44, 66
    h = top + row_h * max(1, len(rows)) + 30
    out = svg_open(h, "vs last time, per platform", f"Average watching at once · this show vs {previous.get('title', 'the previous show')} ({previous.get('date_local', '')})")
    legend(out, W - 230, 30, [(C_AVG, "this show"), (C_PREV, "last time")])
    vmax = max([v for p in rows for v in (p.get("avg"), p.get("previous_avg")) if num(v)] or [1])
    data = [(p["label"], [p.get("avg"), p.get("previous_avg")], [avg_word(p.get("avg"), p.get("peak")), fmt(p.get("previous_avg"))]) for p in rows]
    hbars(out, data, top, row_h, 190, [(C_AVG, "now"), (C_PREV, "before")], [vmax, vmax])
    out.append(f'<text x="20" y="{h - 10}" font-size="10.5" fill="{DIM}">"not on" = the platform wasn\'t attached that time. Averages only; views and watch time grow with show length.</text>')
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------- page

def tiles_html(hd, previous, tz=""):
    prev = hd.get("previous") or {}
    hours = hrs(hd.get("watch_minutes"))
    prev_hours = hrs(prev.get("watch_minutes"))
    pk_sub = ""
    if num(hd.get("peak")):
        bits = [b for b in (f"{hd.get('peak_time_local')} {tz}".strip() if hd.get("peak_time_local") else None,
                            f"{hd['peak_min']} min in" if num(hd.get("peak_min")) else None) if b]
        pk_sub = " · ".join(bits)
    chat_sub = "chat events, as Restream counts them"
    if num(hd.get("chat_messages")):
        chat_sub = f"{fmt(hd['chat_messages'])} messages during the show"
    tiles = [
        ("Average watching at once", fmt(hd.get("avg")), "", delta(hd.get("avg"), prev.get("avg"))),
        ("Peak watching at once", fmt(hd.get("peak")), pk_sub, delta(hd.get("peak"), prev.get("peak"))),
        ("Chat", fmt(hd.get("chat_events")), chat_sub, delta(hd.get("chat_events"), prev.get("chat_events"))),
        ("Watch time", f"{hours:,} viewer-hours" if hours is not None else "not reported", "", delta(hours, prev_hours)),
    ]
    if num(hd.get("x_reactions")) and hd["x_reactions"] > 0:
        tiles.insert(3, ("X likes and follows", fmt(hd["x_reactions"]), "arrive as chat rows; counted apart", delta(hd["x_reactions"], prev.get("x_reactions"))))
    out = ['<section class="tiles">']
    for name, value, sub, d in tiles:
        cls = "up" if (d or 0) > 0 else ("down" if (d or 0) < 0 else "flat")
        dtxt = delta_text(d) if previous else ""
        out.append(f'<div class="tile"><div class="k">{esc(name)}</div><div class="v">{esc(value)}</div>'
                   f'<div class="s">{esc(sub)}</div><div class="d {cls}">{esc(dtxt)}</div></div>')
    out.append("</section>")
    if previous:
        out.append(f'<p class="note">Arrows are calculated vs <b>{esc(previous.get("title", ""))}</b> ({esc(previous.get("date_local", ""))}, {esc(previous.get("duration_min", "?"))} min).</p>')
    return "\n".join(out)


def build_charts(spec):
    charts = []
    hd = spec.get("headline") or {}
    show = spec.get("show") or {}
    tz = spec.get("timezone", "")
    trend = spec.get("trend") or []
    if len(trend) >= 2:
        charts.append(("trend", trend_svg(trend), "Trend"))
    platforms = spec.get("platforms") or []
    if platforms:
        charts.append(("platform-share", share_svg(platforms, hd.get("avg")), "Platform share"))
    ct = spec.get("chat_timeline")
    if ct and ct.get("counts"):
        charts.append(("chat-over-time", chat_time_svg(ct, hd.get("peak_time_local"), tz), "Chat over time"))
    if platforms and any(num(p.get("chat")) for p in platforms):
        charts.append(("chat-vs-viewers", chat_vs_viewers_svg(platforms), "Chat vs viewers"))
    if spec.get("previous") and platforms and any("previous_avg" in p for p in platforms):
        charts.append(("vs-last-time", vs_last_svg(platforms, spec["previous"]), "vs last time"))
    return charts


def page_html(spec, charts):
    show, hd = spec.get("show") or {}, spec.get("headline") or {}
    tz = spec.get("timezone", "")
    title = show.get("title", "Stream report")
    sub = " · ".join(str(b) for b in (spec.get("workspace") and f"Workspace: {spec['workspace']}", show.get("date_local"),
                                      f"{show.get('start_local')} {tz}".strip() if show.get("start_local") else None,
                                      f"{show.get('duration_min')} min" if show.get("duration_min") else None) if b)
    css = (f"body{{margin:0;padding:16px;background:{PAPER};color:{INK};font-family:{FONT};line-height:1.35}}"
           ".wrap{max-width:720px;margin:0 auto}h1{font-size:22px;margin:0 0 4px}.sub{color:#6b6b73;font-size:13px;margin:0 0 14px}"
           ".take{font-size:16px;font-weight:600;margin:0 0 16px;padding:12px 14px;border-left:4px solid #2f6df6;background:#f4f7ff;border-radius:6px}"
           ".tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:0 0 8px}"
           ".tile{border:1px solid #e8e8ec;border-radius:10px;padding:10px 12px}.k{font-size:11.5px;color:#6b6b73;text-transform:uppercase;letter-spacing:.03em}"
           ".v{font-size:24px;font-weight:650;margin:2px 0}.s{font-size:11.5px;color:#6b6b73;min-height:15px}.d{font-size:12.5px;font-weight:600;margin-top:4px}"
           ".up{color:#1a8f4e}.down{color:#c93c3c}.flat{color:#6b6b73}"
           ".note{font-size:12px;color:#6b6b73;margin:6px 0 18px}figure{margin:0 0 22px}svg{width:100%;height:auto;display:block}"
           "ul.notes{font-size:12.5px;color:#6b6b73;padding-left:18px}footer{font-size:11.5px;color:#6b6b73;margin-top:20px;border-top:1px solid #e8e8ec;padding-top:10px}")
    out = ["<!doctype html>", "<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
           f"<title>{esc(title)}</title><style>{css}</style></head><body><div class=\"wrap\">",
           f"<h1>{esc(title)}</h1><p class=\"sub\">{esc(sub)}</p>"]
    if spec.get("takeaway"):
        out.append(f'<p class="take">{esc(spec["takeaway"])}</p>')
    out.append(tiles_html(hd, spec.get("previous"), tz))
    for _, svg, _ in charts:
        out.append(f"<figure>{svg}</figure>")
    notes = list(spec.get("notes") or [])
    if spec.get("skipped_tests"):
        notes.append(f"Skipped {spec['skipped_tests']} short test streams while listing shows.")
    if notes:
        out.append("<ul class=\"notes\">" + "".join(f"<li>{esc(n)}</li>" for n in notes[:4]) + "</ul>")
    out.append("<footer>Source: Restream Analytics and chat. \"Not reported\" means the platform doesn't share that number with Restream; it is not 0. "
               "Views are not people. Totals cover only the platforms that report numbers.</footer></div></body></html>")
    return "\n".join(out)


# ---------------------------------------------------------------- text

def bar(v, vmax, width=16):
    if not num(v) or vmax <= 0:
        return " " * width
    return ("█" * max(1 if v > 0 else 0, round(width * v / vmax))).ljust(width)


def text_report(spec):
    show, hd, prev = spec.get("show") or {}, spec.get("headline") or {}, spec.get("previous")
    tz = spec.get("timezone", "")
    L = [f"## {show.get('title', 'Stream report')}",
         " · ".join(str(b) for b in (spec.get("workspace") and f"Workspace: {spec['workspace']}", show.get("date_local"),
                                     f"{show.get('start_local')} {tz}".strip() if show.get("start_local") else None,
                                     f"{show.get('duration_min')} min" if show.get("duration_min") else None) if b), ""]
    if spec.get("takeaway"):
        L += [f"**{spec['takeaway']}**", ""]
    p = hd.get("previous") or {}
    hours = hrs(hd.get("watch_minutes"))
    phours = hrs(p.get("watch_minutes"))
    L += ["| | This show | vs last time |", "|---|---|---|",
          f"| Average watching at once | {fmt(hd.get('avg'))} | {delta_text(delta(hd.get('avg'), p.get('avg')))} |",
          f"| Peak watching at once | {fmt(hd.get('peak'))}" + (f" ({hd.get('peak_time_local')} {tz}, {hd.get('peak_min')} min in)" if num(hd.get("peak_min")) else "") + f" | {delta_text(delta(hd.get('peak'), p.get('peak')))} |",
          f"| Chat events | {fmt(hd.get('chat_events'))}" + (f" ({fmt(hd['chat_messages'])} messages during the show)" if num(hd.get("chat_messages")) else "") + f" | {delta_text(delta(hd.get('chat_events'), p.get('chat_events')))} |"]
    if num(hd.get("x_reactions")) and hd["x_reactions"] > 0:
        L.append(f"| X likes and follows | {fmt(hd['x_reactions'])} | {delta_text(delta(hd['x_reactions'], p.get('x_reactions')))} |")
    L.append(f"| Watch time | {f'{hours:,} viewer-hours' if hours is not None else 'not reported'} | {delta_text(delta(hours, phours))} |")
    if prev:
        L.append(f"\nArrows are calculated vs **{prev.get('title', '')}** ({prev.get('date_local', '')}, {prev.get('duration_min', '?')} min).")
    trend = spec.get("trend") or []
    if len(trend) >= 2:
        vmax = max([r["avg"] for r in trend if num(r.get("avg"))] or [1])
        L += ["", "**Trend: average watching at once (peak in brackets)**", ""]
        for r in trend:
            mark = " ← this show" if r.get("current") else ""
            L.append(f"`{bar(r.get('avg'), vmax)}` {r.get('date', '')}: {fmt(r.get('avg'))} ({fmt(r.get('peak'))}) {r.get('title', '')}{mark}")
    platforms = spec.get("platforms") or []
    if platforms:
        vmax = max([pf["avg"] for pf in platforms if num(pf.get("avg"))] or [1])
        L += ["", "**Who brought the audience (average watching at once, share of the total average)**", ""]
        for pf in platforms:
            avg = pf.get("avg")
            if num(avg) or num(pf.get("peak")):
                share = share_text(avg, hd.get("avg"))
                L.append(f"`{bar(avg, vmax)}` {pf['label']}: {avg_word(avg, pf.get('peak'))} avg, peak {fmt(pf.get('peak'))}{share}")
        silent = [pf for pf in platforms if not (num(pf.get("avg")) or num(pf.get("peak")))]
        for pf in silent:
            L.append(f"`{' ' * 16}` {pf['label']}: not reported" + (f" · {fmt(pf['chat'])} chat messages" if num(pf.get("chat")) else ""))
    ct = spec.get("chat_timeline")
    if ct and ct.get("counts"):
        counts, b = ct["counts"], ct.get("bucket_min") or 1
        group = max(1, round(10 / b))
        grouped = [sum(c for c in counts[i:i + group] if num(c)) for i in range(0, len(counts), group)]
        vmax = max(grouped or [1])
        L += ["", f"**Chat over time (messages per {group * b} min; reactions, host links and pre-show left out)**", ""]
        for i, c in enumerate(grouped):
            m0 = i * group * b
            flag = ""
            if num(ct.get("peak_min")) and m0 <= ct["peak_min"] < m0 + group * b:
                flag = f" ← viewer peak at {ct['peak_min']} min" + (f": {ct['on_air']}" if ct.get("on_air") else "")
            L.append(f"`{bar(c, vmax)}` {m0:>3}–{m0 + group * b:<3} min: {c}{flag}")
    if platforms and any(num(pf.get("chat")) for pf in platforms):
        L += ["", "**Chat vs viewers**", "", "| Platform | Avg watching | Chat messages |", "|---|---|---|"]
        for pf in platforms:
            if num(pf.get("avg")) or num(pf.get("chat")):
                L.append(f"| {pf['label']} | {avg_word(pf.get('avg'), pf.get('peak'))} | {fmt(pf.get('chat'))} |")
    if prev and platforms and any("previous_avg" in pf for pf in platforms):
        L += ["", f"**vs last time (average watching at once, vs {prev.get('title', '')}, {prev.get('date_local', '')})**", "",
              "| Platform | This show | Last time |", "|---|---|---|"]
        for pf in platforms:
            if "previous_avg" in pf and (num(pf.get("avg")) or num(pf.get("previous_avg"))):
                L.append(f"| {pf['label']} | {avg_word(pf.get('avg'), pf.get('peak'))} | {fmt(pf.get('previous_avg'))} |")
    notes = list(spec.get("notes") or [])
    if spec.get("skipped_tests"):
        notes.append(f"Skipped {spec['skipped_tests']} short test streams while listing shows.")
    L += [""] + [f"- {n}" for n in notes[:4]]
    L.append("- Source: Restream Analytics and chat. \"Not reported\" is not 0. Views are not people. Totals cover only the platforms that report numbers.")
    return "\n".join(L)


# ---------------------------------------------------------------- main

def single_rows(spec, mode):
    if "rows" in spec:
        return spec["rows"], spec.get("title")
    if mode == "trend":
        return spec.get("trend") or [], None
    return [{"label": p["label"], "avg": p.get("avg"), "peak": p.get("peak")} for p in spec.get("platforms") or []], None


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mode, spec_path = sys.argv[1], sys.argv[2]
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    if mode == "text":
        print(text_report(spec))
        return
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    out_dir = sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    written = {}
    if mode == "report":
        charts = build_charts(spec)
        for name, svg, _ in charts:
            p = os.path.join(out_dir, f"{name}.svg")
            with open(p, "w", encoding="utf-8") as f:
                f.write(svg)
            written[name] = os.path.abspath(p)
        for name, text in (("report.html", page_html(spec, charts)), ("report.md", text_report(spec))):
            p = os.path.join(out_dir, name)
            with open(p, "w", encoding="utf-8") as f:
                f.write(text)
            written[name] = os.path.abspath(p)
    elif mode in ("trend", "platforms"):
        rows, title = single_rows(spec, mode)
        if mode == "trend":
            rows = [dict(r, date=r.get("date") or r.get("label", "")) for r in rows]
            svg = trend_svg(rows, title or "Last shows: watching at once")
        else:
            svg = share_svg([dict(r, label=r.get("label", "")) for r in rows], (spec.get("headline") or {}).get("avg"))
        p_svg, p_html = os.path.join(out_dir, "chart.svg"), os.path.join(out_dir, "chart.html")
        with open(p_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        with open(p_html, "w", encoding="utf-8") as f:
            f.write(f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
                    f"<title>{esc(title or 'Restream chart')}</title><style>body{{margin:0;padding:16px;background:{PAPER};font-family:{FONT}}}"
                    f"svg{{max-width:720px;width:100%;height:auto;display:block}}</style></head><body>{svg}</body></html>")
        written = {"svg": os.path.abspath(p_svg), "html": os.path.abspath(p_html)}
    else:
        sys.exit(f"Unknown mode {mode!r}.\n" + __doc__)
    print(json.dumps(written, indent=1))


if __name__ == "__main__":
    main()
