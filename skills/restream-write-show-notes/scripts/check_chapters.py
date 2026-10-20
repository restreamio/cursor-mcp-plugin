#!/usr/bin/env python3
"""Check a chapter list against YouTube's chapter rules before it is handed over.

Usage:
  python3 check_chapters.py CHAPTERS.txt [--covered H:MM:SS] [--duration H:MM:SS]
  (or pipe the chapter block on stdin with "-" as the file name)

Each chapter line is "<timestamp> <title>", e.g. "0:00 Welcome" or "1:02:15 Q&A".
Lines without a leading timestamp are ignored (headings, notes).

Checks:
  - at least 3 chapters
  - the first one is at 0:00 (00:00 and 0:00:00 are fine)
  - times strictly increase
  - every chapter is at least 10 seconds long (the last one too, when --duration is given)
  - no chapter starts after the covered point of the transcript (--covered)
  - every chapter has a title
Exit code 0 = passes, 1 = problems (listed one per line).
No-script fallback: check the same rules by eye.
"""
import argparse
import re
import sys

LINE_RE = re.compile(r"^\s*(?:[-*]\s*)?((?:\d{1,2}:)?\d{1,2}:\d{2})\b\s*[-–—:]?\s*(.*)$")


def parse_ts(ts):
    parts = [int(p) for p in ts.split(":")]
    if len(parts) == 2:
        m, s = parts
        h = 0
    else:
        h, m, s = parts
    if s > 59 or (len(parts) == 3 and m > 59):
        raise ValueError(ts)
    return h * 3600 + m * 60 + s


def fmt(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--covered", help="last timestamp the transcript covers, e.g. 1:11:12")
    ap.add_argument("--duration", help="video length, e.g. 1:25:35")
    args = ap.parse_args()

    src = sys.stdin if args.file == "-" else open(args.file, encoding="utf-8")
    chapters = []
    problems = []
    for n, line in enumerate(src, 1):
        m = LINE_RE.match(line)
        if not m:
            continue
        try:
            sec = parse_ts(m.group(1))
        except ValueError:
            problems.append(f"line {n}: '{m.group(1)}' is not a valid time")
            continue
        chapters.append((sec, m.group(2).strip(), n))

    if len(chapters) < 3:
        problems.append(f"only {len(chapters)} chapter(s); YouTube needs at least 3")
    if chapters and chapters[0][0] != 0:
        problems.append(f"first chapter starts at {fmt(chapters[0][0])}; it must start at 0:00")
    for (a, _, na), (b, _, nb) in zip(chapters, chapters[1:]):
        if b <= a:
            problems.append(f"line {nb}: {fmt(b)} is not after {fmt(a)} (line {na})")
        elif b - a < 10:
            problems.append(f"line {na}: chapter at {fmt(a)} lasts {b - a} s; each must last at least 10 s")
    for sec, title, n in chapters:
        if not title:
            problems.append(f"line {n}: chapter at {fmt(sec)} has no title")
    if args.duration and chapters:
        dur = parse_ts(args.duration)
        last = chapters[-1][0]
        if last >= dur:
            problems.append(f"last chapter at {fmt(last)} starts after the video ends ({fmt(dur)})")
        elif dur - last < 10:
            problems.append(f"last chapter at {fmt(last)} lasts {dur - last} s; it must last at least 10 s")
    if args.covered and chapters:
        cov = parse_ts(args.covered)
        late = [c for c in chapters if c[0] > cov]
        for sec, _, n in late:
            problems.append(f"line {n}: chapter at {fmt(sec)} is past the covered transcript ({fmt(cov)})")

    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print(f"OK: {len(chapters)} chapters, 0:00 to {fmt(chapters[-1][0])}")


if __name__ == "__main__":
    main()
