#!/usr/bin/env python3
"""Clean a Restream transcript and report how much of the show it covers.

Usage:
  python3 transcript_prep.py INPUT [--out CLEAN.txt] [--duration-seconds N]

INPUT is one of:
  - the saved result of Restream MCP get_event_transcript (JSON with a "transcript" field),
  - a transcript text file (the full download, or one the user uploaded).

What it does (the 100k-cap and duplicate-file workaround from transcript-access.md):
  1. Splits on "=== <file> ===" header lines. A later part that starts at the same
     first timestamp with the same opening words is a duplicate (video + audio of the
     same speech): it and everything after it are dropped.
     When the cap cuts the last part before its first full line of speech (or inside
     its header line), what is left is compared as a prefix of part 1's opening. If it
     matches, or is too short to compare, it is a cut duplicate and is dropped; part 1
     is then complete. A non-matching fragment with no full line of speech is a
     separate recording cut before any speech: it is dropped and reported.
  2. Detects the 100,000-character cap (the truncation notice, or exactly 100,000
     characters with no duplicate removed) and trims the cut: the notice, then the
     last segment from the final line that starts with HH:MM:SS onwards.
  3. Removes header lines (they hold recording file names, which are never shown).
  4. Prints a JSON summary: parts, first/last timestamp per part, whether the text was
     capped, and the coverage line in the skill's one format ("Covers the whole show." /
     "Covers the first ~71 of 86 minutes (to 1:11:12)." / "Covers the pasted transcript,
     to 58:02." / "Covers the pasted text, which has no timestamps.").

It never prints file names, links or IDs. Writes the cleaned text only to --out.
No-script fallback: apply the same rules by hand (references/transcript-access.md).
"""
import argparse
import json
import re
import sys

CAP = 100_000
NOTICE = "[Transcript truncated. Use list_event_transcriptions to get download URLs for the full transcripts.]"
HEADER_RE = re.compile(r"^=== .* ===[ \t]*$", re.M)
# The cap cut inside a header line: "\n\n=", "\n\n=== audio-2026-09", "\n\n=== audio-x.m4a ==".
PARTIAL_HEADER_RE = re.compile(r"\n\n={1,3}(?: [^\n]*)?\Z")
OPENING_CHARS = 40
TS_LINE_RE = re.compile(r"^(\d{2}):(\d{2}):(\d{2}) \[Speaker (\d+)\][ \t]*$", re.M)
STARTS_WITH_TS_RE = re.compile(r"^\d{2}:\d{2}:\d{2}", re.M)


def load(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    try:
        data = json.loads(raw)
    except ValueError:
        return raw, "text"
    if isinstance(data, dict) and isinstance(data.get("transcript"), str):
        return data["transcript"], "mcp-json"
    raise SystemExit("Input is JSON but has no 'transcript' field.")


def split_parts(text):
    """Return a list of part bodies (header lines removed)."""
    heads = list(HEADER_RE.finditer(text))
    if not heads:
        return [text]
    parts = []
    lead = text[: heads[0].start()].strip()
    if lead:
        parts.append(lead)
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        parts.append(text[h.end():end].strip("\n"))
    return parts


def opening(body):
    """First timestamp and the first ~40 characters of speech in a part."""
    m = TS_LINE_RE.search(body)
    if not m:
        return None
    rest = body[m.end():].lstrip("\n")
    first_line = rest.split("\n", 1)[0]
    return (m.group(1), m.group(2), m.group(3), first_line[:OPENING_CHARS].strip().lower())


def has_full_opening(body):
    """True when the part has a whole "HH:MM:SS [Speaker N]" line followed by at least
    40 characters of speech, or by a whole (newline-terminated) first line of speech."""
    m = TS_LINE_RE.search(body)
    if not m:
        return False
    rest = body[m.end():].lstrip("\n")
    first_line, sep, _ = rest.partition("\n")
    return len(first_line.strip()) >= OPENING_CHARS or bool(sep and first_line.strip())


def _norm(text):
    return " ".join(text.split()).lower()


def is_cut_duplicate(fragment, first_part):
    """A fragment cut before its first full line of speech is a duplicate when it is a
    prefix of part 1's opening, or too short to compare (empty)."""
    frag = _norm(fragment)
    if not frag:
        return True
    m = STARTS_WITH_TS_RE.search(first_part)
    ref = _norm(first_part[m.start():] if m else first_part)
    return ref.startswith(frag)


def to_seconds(h, m, s):
    return int(h) * 3600 + int(m) * 60 + int(s)


def fmt(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


PARTIAL_TS_RE = re.compile(r"^\d{1,2}(:\d{0,2}){0,2}( \[[^\]\n]*\]?)?[ \t]*$")


def trim_cut(body):
    """Remove what the cap cut.

    Cut inside a timestamp line ("01:11:12 [Speaker 1", "02:1"): drop only that line;
    the segment before it is whole. Cut inside speech: drop the last segment, from the
    final line starting with HH:MM:SS onwards.
    """
    lines = body.rstrip("\n").split("\n")
    if len(lines) > 1 and PARTIAL_TS_RE.match(lines[-1]) and not TS_LINE_RE.match(lines[-2]):
        return "\n".join(lines[:-1]).rstrip()
    starts = list(STARTS_WITH_TS_RE.finditer(body))
    if not starts:
        return body
    return body[: starts[-1].start()].rstrip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--out", help="write the cleaned transcript here")
    ap.add_argument("--duration-seconds", type=int, help="recording durationSeconds, or finishedAt - startedAt")
    args = ap.parse_args()

    text, source = load(args.input)
    raw_len = len(text)
    notice = text.rstrip().endswith(NOTICE)
    if notice:
        text = text.rstrip()[: -len(NOTICE)].rstrip()

    at_cap = notice or raw_len == CAP
    duplicate_removed = False
    later_part_cut_early = False

    # The cap cut inside a later file's header line: nothing of that file survived, so
    # it is too short to compare and counts as a cut duplicate. Part 1 is whole.
    if at_cap:
        m = PARTIAL_HEADER_RE.search(text.rstrip(" \t"))
        if m and HEADER_RE.search(text) and not HEADER_RE.match(m.group(0).strip("\n")):
            text = text.rstrip(" \t")[: m.start()].rstrip()
            duplicate_removed = True

    parts = split_parts(text)
    if len(parts) > 1:
        first = opening(parts[0])
        for i in range(1, len(parts)):
            cut_early = at_cap and i == len(parts) - 1 and not has_full_opening(parts[i])
            if not cut_early and first is not None and opening(parts[i]) == first:
                parts = parts[:i]
                duplicate_removed = True
                break
            if cut_early:
                # The cap cut this part before its first full line of speech.
                if is_cut_duplicate(parts[i], parts[0]):
                    duplicate_removed = True
                else:
                    later_part_cut_early = True
                parts = parts[:i]
                break

    # The cap only cut text we dropped (a duplicate, or a later recording with no full
    # line of speech): what is kept is whole.
    capped = at_cap and not duplicate_removed and not later_part_cut_early
    if capped:
        parts[-1] = trim_cut(parts[-1])
        if len(parts) > 1 and not TS_LINE_RE.search(parts[-1]):
            parts = parts[:-1]
            later_part_cut_early = True
            capped = False

    summary_parts = []
    for body in parts:
        stamps = TS_LINE_RE.findall(body)
        if stamps:
            first_s = to_seconds(*stamps[0][:3])
            last_s = to_seconds(*stamps[-1][:3])
            speakers = sorted({int(s[3]) for s in stamps})
        else:
            first_s = last_s = None
            speakers = []
        summary_parts.append({
            "first_timestamp": fmt(first_s) if first_s is not None else None,
            "last_timestamp": fmt(last_s) if last_s is not None else None,
            "last_seconds": last_s,
            "speakers": [f"Speaker {n}" for n in speakers],
            "chars": len(body),
        })

    if len(parts) > 1:
        cleaned = "\n\n".join(f"[Part {i}]\n" + p.strip("\n") for i, p in enumerate(parts, 1)).strip()
    else:
        cleaned = parts[0].strip() if parts else ""
    has_ts = any(p["last_seconds"] is not None for p in summary_parts)

    coverage = None
    complete = None
    last = summary_parts[-1]["last_seconds"] if summary_parts else None
    if not has_ts:
        coverage = "Covers the pasted text, which has no timestamps."
    elif len(summary_parts) > 1:
        n = len(summary_parts)
        ends = "; ".join(
            f"Part {i} runs to {p['last_timestamp']}" if p["last_timestamp"] else f"Part {i} has no timestamped speech"
            for i, p in enumerate(summary_parts, 1))
        coverage = f"{n} recordings (Part 1 to Part {n}); timestamps restart in each part. {ends}."
        if capped:
            coverage += f" The text was cut by Restream's 100,000-character limit inside Part {n}."
    elif args.duration_seconds and last > args.duration_seconds + 60:
        coverage = (f"Speech runs to {fmt(last)}, past the {fmt(args.duration_seconds)} length given; "
                    f"check the show's length before stating coverage.")
    elif args.duration_seconds:
        dur = args.duration_seconds
        complete = (dur - last) <= 180 and not capped
        if complete:
            coverage = "Covers the whole show."
        else:
            coverage = f"Covers the first ~{last // 60} of {round(dur / 60)} minutes (to {fmt(last)})."
    elif source == "text":
        coverage = f"Covers the pasted transcript, to {fmt(last)}."
    else:
        coverage = f"Covers up to {fmt(last)}" + ("; the text was cut by Restream's 100,000-character limit." if capped else ".")

    if later_part_cut_early and coverage:
        coverage += (" Another recording follows, but Restream's 100,000-character limit cut it "
                     "before any complete line of speech, so it isn't covered.")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(cleaned)

    json.dump({
        "source": source,
        "chars_in": raw_len,
        "chars_out": len(cleaned),
        "capped": capped,
        "duplicate_removed": duplicate_removed,
        "later_part_cut_before_speech": later_part_cut_early,
        "parts": summary_parts,
        "complete": complete,
        "coverage_line": coverage,
    }, sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
