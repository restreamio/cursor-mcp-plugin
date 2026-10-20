#!/usr/bin/env python3
"""Turn a Restream transcript into SRT or VTT subtitles. Standard library only, no network.

Input format (Restream transcript, MCP text or downloaded file):
    === <file name> ===          (MCP text only; optional)
    HH:MM:SS [Speaker N]
    <utterance text>
                                 (blank line between speaker turns)
The MCP result saved by a host as JSON ({"transcript": "...", "files": [...]}) also works.

Commands:
    convert TRANSCRIPT --out-dir DIR [--base NAME] [--format srt|vtt|both|json]
            [--speaker-labels] [--names-file F] [--shift SECONDS] [--duration SECONDS] [--part N]
    render  CUES.json --out-dir DIR [--base NAME] [--format srt|vtt|both]
            (re-wraps edited cue text, e.g. a translation, keeping every cue's timing)
    check   FILE.srt|FILE.vtt
            (validates numbering, timing, line length; exit 1 on hard errors)
    transcript TRANSCRIPT --out-dir DIR [--base NAME] [--format txt|md] [--title-file F]
            [--names-file F] [--duration SECONDS] [--part N]
            (clean verbatim transcript: headers, cap notice, duplicate file and cut line removed)

Titles and speaker names come from Restream or the user, so pass them through files
(--title-file, --names-file with one "1=Anya" per line), never inside a shell command.
--title and --name still work for plain values typed by hand.
With --duration, text whose last line is more than 3 minutes before the end of the
recording is labelled "May be incomplete" and a WARNING is printed.

Cue rules: at most 2 lines of 42 characters, 1-7 seconds, cues never overlap, each cue ends
where the next starts unless that would pass 7 s. Long transcript lines are split across their
own [start, next start] window in proportion to text length (timing within them is approximate).
Times never come from anywhere but the transcript's own timestamps.
"""
import argparse
import json
import math
import os
import re
import sys

MAX_LINE = 42
MAX_LINES = 2
MIN_DUR = 1.0
MAX_DUR = 7.0
CHARS_PER_SEC = 15.0  # only used to time the very last line, which has no "next start"
CAP = 100000
END_GAP = 180  # last line more than 3 min before the recording ends -> may be incomplete
NOTICE_RE = re.compile(r"\n*\[Transcript truncated\.[^\]]*\]\s*$")
HEADER_RE = re.compile(r"^=== .* ===\s*$")
SEG_RE = re.compile(r"^(\d{1,2}):(\d{2}):(\d{2})(?:[.,](\d{1,3}))?\s*\[([^\]\n]+)\]\s*$")
TS_START_RE = re.compile(r"^\d{1,2}:\d{2}:\d{2}")
PUNCT = (".", ",", "?", "!", ";", ":", "…")


def fail(msg, code=2):
    print("error: " + msg, file=sys.stderr)
    sys.exit(code)


def hms(sec):
    sec = max(0, int(round(sec)))
    return "%02d:%02d:%02d" % (sec // 3600, sec % 3600 // 60, sec % 60)


def read_small_file(path, what):
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return fh.read()
    except OSError as exc:
        fail("cannot read %s file %s (%s)" % (what, path, exc.strerror))


def parse_names(args):
    """Speaker names from --name N=Label and --names-file (one N=Label per line)."""
    items = list(args.name or [])
    if getattr(args, "names_file", None):
        for line in read_small_file(args.names_file, "names").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                items.append(line)
    names = {}
    for item in items:
        if "=" not in item:
            fail("speaker names must look like N=Label, e.g. 1=Anya")
        k, v = item.split("=", 1)
        k = re.sub(r"(?i)^speaker\s*", "", k.strip())
        if not k.isdigit() or not v.strip():
            fail("speaker names must look like N=Label, e.g. 1=Anya")
        names["Speaker " + k] = re.sub(r"\s+", " ", v).strip()
    return names


def read_title(args):
    if getattr(args, "title_file", None):
        title = read_small_file(args.title_file, "title")
    else:
        title = args.title or ""
    return re.sub(r"\s+", " ", title).strip()


def end_gap(duration, last):
    """Seconds between the last transcript line and the end of the recording (0 if unknown)."""
    if not duration:
        return 0.0
    return max(0.0, duration - last)


# ---------------------------------------------------------------- reading the transcript

def load_text(path):
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        fail("cannot read %s (%s)" % (path, exc.strerror))
    text = raw.decode("utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            data = json.loads(stripped)
        except ValueError:
            return text
        found = find_transcript(data)
        if found is None:
            fail("JSON input has no 'transcript' text")
        return found.replace("\r\n", "\n")
    return text


def find_transcript(data):
    if isinstance(data, dict):
        if isinstance(data.get("transcript"), str):
            return data["transcript"]
        if isinstance(data.get("text"), str):
            try:
                return find_transcript(json.loads(data["text"]))
            except ValueError:
                return None
        for value in data.values():
            got = find_transcript(value)
            if got is not None:
                return got
    if isinstance(data, list):
        for item in data:
            got = find_transcript(item)
            if got is not None:
                return got
    return None


def split_parts(text):
    """Split on '=== file ===' headers. Returns list of line lists."""
    parts, cur, saw_header = [], [], False
    for line in text.split("\n"):
        if HEADER_RE.match(line):
            if cur and (saw_header or any(l.strip() for l in cur)):
                parts.append(cur)
            cur, saw_header = [], True
            continue
        cur.append(line)
    if cur:
        parts.append(cur)
    return parts or [[]]


def parse_segments(lines):
    segs, cur, skipped, blank = [], None, 0, True
    for line in lines:
        m = SEG_RE.match(line.strip())
        if m:
            if cur is not None:
                segs.append(cur)
            h, mi, s, frac, spk = m.groups()
            t = int(h) * 3600 + int(mi) * 60 + int(s) + (int(frac.ljust(3, "0")) / 1000.0 if frac else 0.0)
            cur = {"t": t, "speaker": spk.strip(), "text": [], "para": blank}
            blank = False
        elif line.strip():
            if cur is None:
                skipped += 1
            else:
                cur["text"].append(line.strip())
        else:
            blank = True
    if cur is not None:
        segs.append(cur)
    out = []
    for seg in segs:
        txt = re.sub(r"\s+", " ", " ".join(seg["text"])).strip()
        if txt:
            out.append({"t": seg["t"], "speaker": seg["speaker"], "text": txt, "para": seg["para"]})
    return out, skipped


def first_words(segs, n=6):
    if not segs:
        return ""
    return " ".join(re.sub(r"[^\w\s]", "", segs[0]["text"].lower()).split()[:n])


def read_transcript(path, part_no):
    text = load_text(path)
    capped = len(text) == CAP
    notice = bool(NOTICE_RE.search(text))
    text = NOTICE_RE.sub("", text)
    raw_parts = split_parts(text)
    parsed = [parse_segments(p) for p in raw_parts]
    notes = []
    # Duplicate second file: same first timestamp and same opening words as part 1.
    keep, dup_dropped = [], 0
    for idx, (segs, _) in enumerate(parsed):
        if not segs:
            if idx > 0:
                notes.append("skipped a transcript part with no complete lines (likely cut by the cap)")
            continue
        if idx > 0 and parsed[0][0] and segs[0]["t"] == parsed[0][0][0]["t"] \
                and first_words(segs) == first_words(parsed[0][0]):
            dup_dropped += 1
            continue
        keep.append(idx)
    if dup_dropped:
        notes.append("dropped %d duplicate transcript file(s) (same speech, second recording file)" % dup_dropped)
    truncated_flag = capped or notice
    last_idx = len(raw_parts) - 1
    if not keep:
        fail("no transcript segments found (expected lines like '00:03:04 [Speaker 1]')")
    if part_no < 1 or part_no > len(keep):
        fail("--part %d requested, but the transcript has %d part(s)" % (part_no, len(keep)))
    chosen = keep[part_no - 1]
    if len(keep) > 1:
        notes.append("transcript has %d separate parts (timestamps restart in each); using part %d" % (len(keep), part_no))
    partial = False
    if truncated_flag and chosen == last_idx:
        # The cap cuts mid-line, sometimes inside the timestamp line: drop the final segment.
        lines = raw_parts[chosen]
        cut = None
        for i in range(len(lines) - 1, -1, -1):
            if TS_START_RE.match(lines[i].strip()):
                cut = i
                break
        if cut is not None:
            lines = lines[:cut]
        segs, skipped = parse_segments(lines)
        partial = True
        notes.append("transcript was cut at Restream's 100,000-character cap; last line dropped")
    else:
        segs, skipped = parsed[chosen]
        if truncated_flag and chosen != last_idx:
            notes.append("the 100,000-character cap only cut a later part; part %d is complete" % part_no)
    if skipped:
        notes.append("ignored %d line(s) before the first timestamp" % skipped)
    if not segs:
        fail("no transcript segments found in the chosen part")
    for i in range(1, len(segs)):
        if segs[i]["t"] < segs[i - 1]["t"]:
            segs[i]["t"] = segs[i - 1]["t"]
    return segs, partial, notes


# ---------------------------------------------------------------- wrapping and chunking

def explode_words(text):
    words = []
    for w in text.split():
        while len(w) > MAX_LINE:
            words.append(w[:MAX_LINE])
            w = w[MAX_LINE:]
        if w:
            words.append(w)
    return words


def wrap2(words):
    """Best 1- or 2-line layout (each <= MAX_LINE), or None if impossible."""
    text = " ".join(words)
    if len(text) <= MAX_LINE:
        return [text]
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) <= MAX_LINE and len(b) <= MAX_LINE:
            score = abs(len(a) - len(b)) - (10 if words[i - 1].endswith(PUNCT) else 0)
            if best is None or score < best[0]:
                best = (score, [a, b])
    return best[1] if best else None


def chunk_words(words):
    """Split words into the fewest cues that fit 2x42, balanced, preferring punctuation breaks."""
    n = len(words)
    if n == 0:
        return []
    inf = float("inf")
    best = [(inf, None)] * (n + 1)
    best[0] = (0.0, None)
    fits = {}
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            length = len(" ".join(words[i:j]))
            if length > MAX_LINE * MAX_LINES + 1:
                break
            if best[i][0] == inf:
                continue
            key = (i, j)
            if key not in fits:
                fits[key] = wrap2(words[i:j]) is not None
            if not fits[key]:
                continue
            slack = MAX_LINE * MAX_LINES - length
            cost = 10000.0 + slack * slack / 10.0
            if j < n and not words[j - 1].endswith(PUNCT):
                cost += 40.0
            total = best[i][0] + cost
            if total < best[j][0]:
                best[j] = (total, i)
    if best[n][0] == inf:  # should not happen after explode_words; fall back to greedy
        out, cur = [], []
        for w in words:
            if cur and wrap2(cur + [w]) is None:
                out.append(cur)
                cur = []
            cur.append(w)
        return out + ([cur] if cur else [])
    out, j = [], n
    while j > 0:
        i = best[j][1]
        out.append(words[i:j])
        j = i
    return out[::-1]


# ---------------------------------------------------------------- timing

def build_cues(segs, labels, names, duration):
    """Return cue dicts: start, end, words, turn (int), approx (bool)."""
    cues = []
    n = len(segs)
    prev_speaker = None
    turn = 0
    # group consecutive segments that share a start second
    i = 0
    while i < n:
        j = i
        while j + 1 < n and segs[j + 1]["t"] == segs[i]["t"]:
            j += 1
        start = segs[i]["t"]
        group = segs[i:j + 1]
        texts = []
        for seg in group:
            text = seg["text"]
            if seg["speaker"] != prev_speaker:
                turn += 1
                if labels:
                    label = names.get(seg["speaker"], seg["speaker"]).upper()
                    text = "%s: %s" % (label, text)
            prev_speaker = seg["speaker"]
            texts.append((text, turn))
        chunked = [(chunk_words(explode_words(t)), tn) for t, tn in texts]
        total_chars = sum(len(" ".join(c)) for chunks, _ in chunked for c in chunks) or 1
        n_cues = sum(len(chunks) for chunks, _ in chunked)
        if j + 1 < n:
            end = segs[j + 1]["t"]
        else:
            end = start + max(MIN_DUR * n_cues, min(total_chars / CHARS_PER_SEC, MAX_DUR * n_cues))
            if duration and duration > start:
                end = min(end, duration)
        window = max(end - start, 0.0)
        t = start
        for chunks, tn in chunked:
            for words in chunks:
                share = window * len(" ".join(words)) / total_chars
                dur = min(share, MAX_DUR)
                cues.append({"start": t, "end": t + dur, "words": words, "turn": tn,
                             "approx": n_cues > 1})
                t += share if share <= MAX_DUR else MAX_DUR
        i = j + 1
    return cues


def enforce_min(cues):
    """Merge or lengthen cues shorter than MIN_DUR; returns (cues, moved, max_shift)."""
    moved, max_shift = 0, 0.0
    k = 0
    while k < len(cues):
        c = cues[k]
        if c["end"] - c["start"] >= MIN_DUR - 1e-6:
            k += 1
            continue
        nxt = cues[k + 1] if k + 1 < len(cues) else None
        prv = cues[k - 1] if k > 0 else None
        if nxt and nxt["turn"] == c["turn"] and nxt["end"] - c["start"] <= MAX_DUR \
                and wrap2(c["words"] + nxt["words"]):
            nxt["words"] = c["words"] + nxt["words"]
            nxt["start"] = c["start"]
            nxt["approx"] = nxt["approx"] or c["approx"]
            cues.pop(k)
            continue
        if prv and prv["turn"] == c["turn"] and c["end"] - prv["start"] <= MAX_DUR \
                and wrap2(prv["words"] + c["words"]):
            prv["words"] = prv["words"] + c["words"]
            prv["end"] = c["end"]
            prv["approx"] = prv["approx"] or c["approx"]
            cues.pop(k)
            continue
        c["end"] = c["start"] + MIN_DUR
        # push later cues that now overlap
        m = k + 1
        while m < len(cues) and cues[m]["start"] < cues[m - 1]["end"] - 1e-6:
            shift = cues[m - 1]["end"] - cues[m]["start"]
            cues[m]["start"] += shift
            cues[m]["end"] = max(cues[m]["end"], cues[m]["start"])
            moved += 1
            max_shift = max(max_shift, shift)
            m += 1
        k += 1
    return cues, moved, max_shift


def finalize(cues):
    for k, c in enumerate(cues):
        if k + 1 < len(cues):
            c["end"] = min(c["end"], cues[k + 1]["start"])
        c["end"] = min(c["end"], c["start"] + MAX_DUR)
    return [c for c in cues if c["end"] - c["start"] > 0.05]


def apply_shift(cues, shift):
    if not shift:
        return cues
    out = []
    for c in cues:
        c["start"] += shift
        c["end"] += shift
        if c["end"] <= 0:
            continue
        c["start"] = max(0.0, c["start"])
        out.append(c)
    return out


# ---------------------------------------------------------------- output

def stamp(sec, sep):
    ms = int(round(max(sec, 0) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d%s%03d" % (h, m, s, sep, ms)


def cue_lines(c):
    return wrap2(c["words"]) or [" ".join(c["words"])]


def to_srt(cues):
    blocks = []
    for k, c in enumerate(cues, 1):
        blocks.append("%d\n%s --> %s\n%s\n" % (k, stamp(c["start"], ","), stamp(c["end"], ","),
                                              "\n".join(cue_lines(c))))
    return "\n".join(blocks)


def to_vtt(cues, note):
    out = ["WEBVTT", ""]
    if note:
        out += ["NOTE " + note, ""]
    for c in cues:
        out.append("%s --> %s" % (stamp(c["start"], "."), stamp(c["end"], ".")))
        out += [l.replace("-->", "->") for l in cue_lines(c)]
        out.append("")
    return "\n".join(out)


def write_outputs(cues, args, note, meta):
    os.makedirs(args.out_dir, exist_ok=True)
    fmts = ["srt", "vtt"] if args.format == "both" else [args.format]
    written = []
    for fmt in fmts:
        path = os.path.join(args.out_dir, "%s.%s" % (args.base, fmt))
        if fmt == "srt":
            body = to_srt(cues)
        elif fmt == "vtt":
            body = to_vtt(cues, note)
        else:
            body = json.dumps({"meta": meta, "cues": [
                {"n": k, "start": round(c["start"], 3), "end": round(c["end"], 3),
                 "text": " ".join(c["words"]), "turn": c["turn"]}
                for k, c in enumerate(cues, 1)]}, ensure_ascii=False, indent=1)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        written.append(path)
    return written


def stats(cues):
    durs = [c["end"] - c["start"] for c in cues]
    lines = [cue_lines(c) for c in cues]
    return {
        "cues": len(cues),
        "min_s": round(min(durs), 2) if durs else 0,
        "max_s": round(max(durs), 2) if durs else 0,
        "longest_line": max((len(l) for ls in lines for l in ls), default=0),
        "max_lines": max((len(ls) for ls in lines), default=0),
        "under_1s": sum(1 for d in durs if d < MIN_DUR - 0.01),
        "over_7s": sum(1 for d in durs if d > MAX_DUR + 0.01),
        "approx": sum(1 for c in cues if c.get("approx")),
    }


def report(st, extra):
    print("cues: %d | duration %.2f-%.2f s | longest line %d chars | max %d lines"
          % (st["cues"], st["min_s"], st["max_s"], st["longest_line"], st["max_lines"]))
    print("cues under 1 s: %d | over 7 s: %d | cues with approximate timing (split from long lines): %d"
          % (st["under_1s"], st["over_7s"], st["approx"]))
    for line in extra:
        print(line)


def cmd_convert(args):
    names = parse_names(args)
    labels = args.speaker_labels or bool(names)
    segs, partial, notes = read_transcript(args.input, args.part)
    cues = build_cues(segs, labels, names, args.duration)
    cues, moved, max_shift = enforce_min(cues)
    cues = finalize(cues)
    cues = apply_shift(cues, args.shift)
    first, last = segs[0]["t"], segs[-1]["t"]
    gap = end_gap(args.duration, last)
    incomplete = (not partial) and gap > END_GAP
    if partial:
        coverage = "PARTIAL: first %s only (speech %s-%s)" % (hms(last), hms(first), hms(last))
        if args.duration:
            coverage += ", of a %s recording (first ~%d of %d minutes)" % (
                hms(args.duration), round(last / 60.0), math.ceil(args.duration / 60.0))
    elif incomplete:
        coverage = "MAY BE INCOMPLETE: speech %s-%s, but the recording runs %s (%d min after the last line)" % (
            hms(first), hms(last), hms(args.duration), round(gap / 60.0))
    else:
        coverage = "complete transcript: speech %s-%s" % (hms(first), hms(last))
        if args.duration:
            coverage += " of a %s recording" % hms(args.duration)
    if partial or incomplete:
        note = "Partial subtitles: they cover the transcript only up to %s." % hms(last)
    else:
        note = ""
    meta = {"coverage": coverage, "partial": partial or incomplete, "shift_s": args.shift or 0,
            "labels": labels, "segments": len(segs)}
    written = write_outputs(cues, args, note, meta)
    st = stats(cues)
    extra = ["segments read: %d" % len(segs), "coverage: " + coverage]
    if incomplete:
        extra.append("WARNING: the last line is %d min before the end of the recording. Treat these subtitles "
                     "as partial ('first %s only') unless you have the full transcript file."
                     % (round(gap / 60.0), hms(last)))
    if moved:
        extra.append("cues moved later to keep the 1 s minimum: %d (largest move %.2f s)" % (moved, max_shift))
    if args.shift:
        extra.append("all cues shifted by %+.2f s" % args.shift)
    extra += ["note: " + n for n in notes]
    extra += ["wrote: " + p for p in written]
    report(st, extra)
    return 0


def cmd_transcript(args):
    """Clean verbatim transcript: headers, cap notice, duplicate file and cut last line removed."""
    names = parse_names(args)
    title = read_title(args)
    segs, partial, notes = read_transcript(args.input, args.part)
    first, last = segs[0]["t"], segs[-1]["t"]
    gap = end_gap(args.duration, last)
    incomplete = (not partial) and gap > END_GAP
    if partial:
        coverage = "Partial transcript: covers the recording up to %s only" % hms(last)
        if args.duration:
            coverage += " (first ~%d of %d minutes)" % (round(last / 60.0), math.ceil(args.duration / 60.0))
        coverage += ". Restream's connector stops at 100,000 characters."
    elif incomplete:
        coverage = "May be incomplete: speech ends at %s, but the recording runs %d min." % (
            hms(last), math.ceil(args.duration / 60.0))
    else:
        coverage = "Full transcript: speech from %s to %s" % (hms(first), hms(last))
        if args.duration:
            coverage += " (recording: %d min)" % math.ceil(args.duration / 60.0)
        coverage += "."
    os.makedirs(args.out_dir, exist_ok=True)
    path = os.path.join(args.out_dir, "%s.%s" % (args.base, args.format))
    out = []
    if args.format == "txt":
        if partial or incomplete:
            out.append("[%s]" % coverage)
            out.append("")
        prev = None
        for seg in segs:
            if prev is not None and (seg["para"] or seg["speaker"] != prev):
                out.append("")
            label = names.get(seg["speaker"], seg["speaker"])
            out.append("%s [%s]" % (hms(seg["t"]), label))
            out.append(seg["text"])
            prev = seg["speaker"]
    else:
        if title:
            out += ["# " + title, ""]
        out += ["_%s Timestamps count from the start of the recording._" % coverage, ""]
        turn, prev = [], None
        for seg in segs + [None]:
            if turn and (seg is None or seg["para"] or seg["speaker"] != prev["speaker"]):
                label = names.get(turn[0]["speaker"], turn[0]["speaker"])
                out += ["**%s · %s**" % (hms(turn[0]["t"]), label), " ".join(s["text"] for s in turn), ""]
                turn = []
            if seg is not None:
                turn.append(seg)
                prev = seg
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out).rstrip("\n") + "\n")
    print("segments: %d | %s" % (len(segs), coverage))
    if incomplete:
        print("WARNING: the last line is %d min before the end of the recording. Treat this as partial "
              "coverage unless you have the full transcript file." % round(gap / 60.0))
    for n in notes:
        print("note: " + n)
    print("wrote: " + path)
    return 0


def cmd_render(args):
    try:
        with open(args.input, encoding="utf-8-sig") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        fail("cannot read cues JSON: %s" % exc)
    src = data.get("cues") if isinstance(data, dict) else data
    if not isinstance(src, list) or not src:
        fail("cues JSON must contain a non-empty 'cues' list")
    cues = []
    for k, c in enumerate(src):
        try:
            start, end, text = float(c["start"]), float(c["end"]), str(c["text"])
        except (KeyError, TypeError, ValueError):
            fail("cue %d needs start, end and text" % (k + 1))
        if end <= start:
            fail("cue %d ends before it starts" % (k + 1))
        chunks = chunk_words(explode_words(text)) or [[]]
        total = sum(len(" ".join(ch)) for ch in chunks) or 1
        t = start
        for ch in chunks:
            share = (end - start) * len(" ".join(ch)) / total
            cues.append({"start": t, "end": t + share, "words": ch, "turn": c.get("turn", k),
                         "approx": len(chunks) > 1})
            t += share
    cues, moved, max_shift = enforce_min(cues)
    cues = finalize(cues)
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    note = "Partial subtitles." if meta.get("partial") else ""
    written = write_outputs(cues, args, note, meta)
    extra = ["coverage: " + meta.get("coverage", "unknown")]
    if moved:
        extra.append("cues moved later to keep the 1 s minimum: %d (largest move %.2f s)" % (moved, max_shift))
    extra += ["wrote: " + p for p in written]
    report(stats(cues), extra)
    return 0


TIME_RE = re.compile(r"^(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})\s+-->\s+(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})")


def secs(g):
    return int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000.0


def cmd_check(args):
    try:
        with open(args.input, encoding="utf-8-sig") as fh:
            text = fh.read().replace("\r\n", "\n")
    except OSError as exc:
        fail("cannot read %s" % exc)
    is_vtt = text.startswith("WEBVTT")
    errors, warns, cues = [], [], []
    blocks = [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    expected = 1
    for b in blocks:
        lines = b.split("\n")
        if is_vtt and (lines[0].startswith("WEBVTT") or lines[0].startswith("NOTE")):
            continue
        idx = 0
        if not is_vtt:
            if not lines[0].strip().isdigit():
                errors.append("block without a number: %r" % lines[0][:40])
                continue
            if int(lines[0]) != expected:
                errors.append("cue number %s, expected %d" % (lines[0].strip(), expected))
            expected = int(lines[0]) + 1
            idx = 1
        elif not TIME_RE.match(lines[0]) and len(lines) > 1:
            idx = 1  # optional VTT cue identifier
        if idx >= len(lines) or not TIME_RE.match(lines[idx]):
            errors.append("bad timing line near %r" % b[:40])
            continue
        g = TIME_RE.match(lines[idx]).groups()
        start, end = secs(g[:4]), secs(g[4:])
        body = lines[idx + 1:]
        cues.append((start, end, body))
        if end <= start:
            errors.append("cue at %s ends before it starts" % stamp(start, "."))
        if not body or not any(l.strip() for l in body):
            errors.append("empty cue at %s" % stamp(start, "."))
    for k in range(1, len(cues)):
        if cues[k][0] < cues[k - 1][1] - 1e-6:
            errors.append("cue at %s overlaps the previous one" % stamp(cues[k][0], "."))
        if cues[k][0] < cues[k - 1][0]:
            errors.append("cue at %s is out of order" % stamp(cues[k][0], "."))
    for start, end, body in cues:
        if len(body) > MAX_LINES:
            warns.append("cue at %s has %d lines" % (stamp(start, "."), len(body)))
        for l in body:
            if len(l) > MAX_LINE:
                warns.append("cue at %s has a %d-character line" % (stamp(start, "."), len(l)))
        if end - start < MIN_DUR - 0.01 or end - start > MAX_DUR + 0.01:
            warns.append("cue at %s lasts %.2f s" % (stamp(start, "."), end - start))
    print("%s: %d cues, %d errors, %d warnings" % ("VTT" if is_vtt else "SRT", len(cues), len(errors), len(warns)))
    for e in errors[:20]:
        print("ERROR " + e)
    for w in warns[:20]:
        print("warn  " + w)
    if not cues:
        errors.append("no cues")
    return 1 if errors else 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Restream transcript -> SRT/VTT subtitles (no network).")
    sub = p.add_subparsers(dest="cmd")
    c = sub.add_parser("convert", help="transcript -> subtitles")
    c.add_argument("input")
    c.add_argument("--out-dir", required=True)
    c.add_argument("--base", default=None, help="output file name without extension")
    c.add_argument("--format", choices=["srt", "vtt", "both", "json"], default="srt")
    c.add_argument("--speaker-labels", action="store_true", help="prefix 'SPEAKER N:' at each speaker change")
    c.add_argument("--name", action="append", help="confirmed speaker name, e.g. 1=Anya (implies labels)")
    c.add_argument("--names-file", default=None, help="file with one confirmed name per line, e.g. 1=Anya")
    c.add_argument("--shift", type=float, default=0.0, help="seconds to add to every cue (negative = earlier)")
    c.add_argument("--duration", type=float, default=None, help="recording length in seconds, for coverage")
    c.add_argument("--part", type=int, default=1, help="which separate transcript part to use")
    r = sub.add_parser("render", help="cues JSON (e.g. translated) -> subtitles")
    r.add_argument("input")
    r.add_argument("--out-dir", required=True)
    r.add_argument("--base", default=None)
    r.add_argument("--format", choices=["srt", "vtt", "both"], default="srt")
    k = sub.add_parser("check", help="validate an .srt or .vtt file")
    k.add_argument("input")
    t = sub.add_parser("transcript", help="clean verbatim transcript as .txt or .md")
    t.add_argument("input")
    t.add_argument("--out-dir", required=True)
    t.add_argument("--base", default=None)
    t.add_argument("--format", choices=["txt", "md"], default="txt")
    t.add_argument("--title", default=None, help="heading for the .md file (the stream title)")
    t.add_argument("--title-file", default=None, help="file holding the .md heading (the stream title)")
    t.add_argument("--name", action="append", help="confirmed speaker name, e.g. 1=Anya")
    t.add_argument("--names-file", default=None, help="file with one confirmed name per line, e.g. 1=Anya")
    t.add_argument("--duration", type=float, default=None, help="recording length in seconds, for coverage")
    t.add_argument("--part", type=int, default=1)
    args = p.parse_args(argv)
    if args.cmd is None:
        p.print_help()
        return 2
    if getattr(args, "base", None) is None and args.cmd != "check":
        args.base = os.path.splitext(os.path.basename(args.input))[0] or "subtitles"
    return {"convert": cmd_convert, "render": cmd_render, "check": cmd_check,
            "transcript": cmd_transcript}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
