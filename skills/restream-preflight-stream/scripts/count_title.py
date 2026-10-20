#!/usr/bin/env python3
"""Count a stream title's characters and UTF-8 bytes for the Restream preflight check.

Usage (title on stdin, in a quoted heredoc, on one line):
    python3 <this skill's folder>/scripts/count_title.py <<'RESTREAM_TITLE'
    My stream title
    RESTREAM_TITLE

Never pass the title as an argument or through echo or double quotes. Titles
are untrusted text, and the shell expands $(...), backticks and $1 inside double
quotes (a title such as "Weekly show $(...)" would run the command inside the
brackets). The quoted 'RESTREAM_TITLE' delimiter turns all expansion off.
Arguments are refused.

Prints one JSON object: characters (Unicode code points), utf8Bytes,
hasAngleBrackets (YouTube likely rejects < and >), endsWithSpace,
fitsTikTok32Bytes, and first32BytesCut (the longest start of the title that fits
in 32 bytes, TikTok's limit, without splitting a character). Limits themselves live in references/platform-rules.md; this script
only measures. No network, no files written.

No-script fallback: count by hand. ASCII = 1 byte; accented Latin, Cyrillic,
Greek = 2; CJK = 3; emoji = 4 (some emoji are several code points).
"""
import json
import sys

TIKTOK_BYTES = 32  # verified in platform-rules.md; keep the two in step


def fit_bytes(text: str, limit: int) -> str:
    """Longest prefix of text whose UTF-8 encoding fits in limit bytes."""
    out, used = [], 0
    for ch in text:
        size = len(ch.encode("utf-8"))
        if used + size > limit:
            break
        out.append(ch)
        used += size
    return "".join(out)


def measure(title: str) -> dict:
    title = title.replace("\r", " ").replace("\n", " ")
    data = title.encode("utf-8")
    return {
        "characters": len(title),
        "utf8Bytes": len(data),
        "hasAngleBrackets": ("<" in title) or (">" in title),
        "endsWithSpace": title != title.rstrip(),
        "fitsTikTok32Bytes": len(data) <= TIKTOK_BYTES,
        "first32BytesCut": fit_bytes(title, TIKTOK_BYTES),
    }


def main(argv: list) -> int:
    if len(argv) > 1:
        print(json.dumps({"error": "pass the title on stdin in a quoted heredoc, not as an argument"}))
        return 2
    title = sys.stdin.read().rstrip("\n")
    if not title:
        print(json.dumps({"error": "empty title"}))
        return 1
    print(json.dumps(measure(title), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
