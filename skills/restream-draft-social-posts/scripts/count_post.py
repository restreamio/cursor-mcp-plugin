#!/usr/bin/env python3
"""Count social post drafts the way each platform counts them (offline, stdlib only).

Input (one of):
  - a JSON array on stdin or in a file: [{"label": "1", "platform": "x", "text": "..."}]
  - --platform <name> --text "<text>"   (or the text on stdin)

Platforms: x, x_premium, linkedin, threads, bluesky, instagram, tiktok,
youtube_title, youtube_description, facebook, x_article.

Output: a JSON array, one object per draft:
  label, platform, count, unit, limit, over_by, fits, hashtags, urls,
  hook_chars, fold, notes[]

X uses weighted counting (twitter-text v3): code points in U+0000-U+10FF,
U+2000-U+200D, U+2010-U+201F and U+2032-U+2037 weigh 1, everything else 2;
an emoji sequence counts 2 in total; every URL, and a placeholder such as
{watch link} or {replay link}, counts 23. Text is NFC-normalised
first. Bluesky counts graphemes. Other platforms count code points.
Grapheme and URL detection are approximations that err on the long side.
The script never opens a URL and never runs anything from the text.
"""
import argparse
import json
import re
import sys
import unicodedata

LIMITS = {
    "x": (280, "weighted characters"),
    "x_premium": (25000, "weighted characters"),
    "x_article": (100000, "characters"),
    "linkedin": (3000, "characters"),
    "threads": (500, "characters"),
    "bluesky": (300, "graphemes"),
    "instagram": (2200, "characters"),
    "tiktok": (4000, "characters"),
    "youtube_title": (100, "characters"),
    "youtube_description": (5000, "characters"),
    "facebook": (63206, "characters"),
}

# Characters visible before the platform's "see more" fold (approximate).
FOLD = {"linkedin": 140, "instagram": 125, "tiktok": 100, "facebook": 125}

# Hashtag ceilings: the platform's hard cap or this skill's house rule (2).
HASHTAG_CAP = {"instagram": 5, "threads": 1}
HOUSE_HASHTAGS = 2

ALIASES = {
    "twitter": "x", "x_post": "x", "x_thread": "x", "thread": "x",
    "li": "linkedin", "linkedin_post": "linkedin",
    "bsky": "bluesky", "ig": "instagram", "instagram_reels": "instagram",
    "reels": "instagram", "shorts_title": "youtube_title",
    "youtube_shorts": "youtube_title", "yt_title": "youtube_title",
    "yt_description": "youtube_description", "fb": "facebook",
    "article": "x_article",
}

X_WEIGHT_1 = ((0x0000, 0x10FF), (0x2000, 0x200D), (0x2010, 0x201F), (0x2032, 0x2037))
URL_WEIGHT = 23

EMOJI_RANGES = (
    (0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2300, 0x23FF), (0x2B00, 0x2BFF),
    (0x1F1E6, 0x1F1FF), (0x3030, 0x3030), (0x303D, 0x303D), (0x3297, 0x3297),
    (0x3299, 0x3299),
)
RI = (0x1F1E6, 0x1F1FF)

TLDS = (
    "com|net|org|io|co|ai|tv|gg|app|dev|me|ly|us|uk|de|fr|es|it|nl|ca|au|in|"
    "jp|link|live|news|info|biz|edu|gov|so|xyz|fm|to|be|site|online|store|blog|page"
)
URL_RE = re.compile(
    r"(?:\{[a-z ]*link\})"
    r"|(?:https?://[^\s]+)"
    r"|(?:(?<![@\w.])(?:[a-z0-9-]+\.)+(?:" + TLDS + r")\b(?:/[^\s]*)?)",
    re.IGNORECASE,
)
HASHTAG_RE = re.compile(r"(?<![\w&])#(\w+)")
TRAILING_PUNCT = ".,;:!?)]}'\""


def in_ranges(cp, ranges):
    return any(lo <= cp <= hi for lo, hi in ranges)


def is_extender(cp):
    if cp == 0x200D or 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF:
        return True
    if 0x1F3FB <= cp <= 0x1F3FF or 0xE0020 <= cp <= 0xE007F or cp == 0x20E3:
        return True
    return unicodedata.category(chr(cp)) in ("Mn", "Me", "Mc")


def graphemes(text):
    """Approximate extended grapheme clusters without third-party modules."""
    clusters = []
    prev_zwj = False
    ri_open = False
    for ch in text:
        cp = ord(ch)
        is_ri = RI[0] <= cp <= RI[1]
        join = False
        if clusters:
            if is_extender(cp) or prev_zwj:
                join = True
            elif is_ri and ri_open:
                join = True
            elif ch == "\n" and clusters[-1] == "\r":
                join = True
        if join:
            clusters[-1] += ch
            if is_ri:
                ri_open = False
        else:
            clusters.append(ch)
            ri_open = is_ri
        prev_zwj = cp == 0x200D
    return clusters


def is_emoji_cluster(cluster):
    for ch in cluster:
        cp = ord(ch)
        if cp == 0xFE0F or cp == 0x20E3 or in_ranges(cp, EMOJI_RANGES):
            return True
    return False


def find_urls(text):
    spans = []
    for m in URL_RE.finditer(text):
        start, end = m.start(), m.end()
        while end > start and text[start] != "{" and text[end - 1] in TRAILING_PUNCT:
            end -= 1
        if end > start:
            spans.append((start, end))
    return spans


def x_weight(text):
    total = 0
    pos = 0
    for start, end in find_urls(text):
        total += x_weight_plain(text[pos:start])
        raw = text[start:end]
        has_protocol = raw.lower().startswith(("http://", "https://", "{"))
        # X links every protocol URL (and a {... link} placeholder) as 23. Bare domains may stay plain text,
        # so take the longer of the two to stay on the safe side.
        total += URL_WEIGHT if has_protocol else max(URL_WEIGHT, x_weight_plain(raw))
        pos = end
    total += x_weight_plain(text[pos:])
    return total


def x_weight_plain(text):
    total = 0
    for cluster in graphemes(text):
        if is_emoji_cluster(cluster):
            total += 2
            continue
        for ch in cluster:
            total += 1 if in_ranges(ord(ch), X_WEIGHT_1) else 2
    return total


def count_one(label, platform, text):
    key = ALIASES.get(platform.strip().lower(), platform.strip().lower())
    if key not in LIMITS:
        return {"label": label, "platform": platform,
                "error": "unknown platform; use one of: " + ", ".join(sorted(LIMITS))}
    text = unicodedata.normalize("NFC", text)
    limit, unit = LIMITS[key]
    notes = []
    clusters = graphemes(text)
    has_emoji = any(is_emoji_cluster(c) for c in clusters)
    if key in ("x", "x_premium"):
        count = x_weight(text)
    elif key == "bluesky":
        count = len(clusters)
        if len(text.encode("utf-8")) > 3000:
            notes.append("over Bluesky's 3,000-byte ceiling")
    else:
        count = len(text)
        if has_emoji:
            notes.append("emoji may count as 2 here; leave a little headroom")
    over_by = max(0, count - limit)
    if over_by and key == "x":
        notes.append("over 280: shorten, or split into a numbered thread")
    url_spans = find_urls(text)
    no_urls = text
    for s_, e_ in reversed(url_spans):
        no_urls = no_urls[:s_] + " " + no_urls[e_:]
    tags = HASHTAG_RE.findall(no_urls)
    cap = HASHTAG_CAP.get(key)
    if cap is not None and len(tags) > cap:
        notes.append("%d hashtags; %s allows %d" % (len(tags), key, cap))
    elif len(tags) > HOUSE_HASHTAGS:
        notes.append("%d hashtags; keep it to %d" % (len(tags), HOUSE_HASHTAGS))
    urls = [text[s_:e_] for s_, e_ in url_spans]
    if key == "youtube_title" and ("<" in text or ">" in text):
        notes.append("YouTube titles can't contain < or >")
    if key in ("instagram", "tiktok") and urls:
        notes.append("links in %s captions aren't clickable" % key)
    if key == "tiktok" and count > 2200:
        notes.append("schedulers and the posting API likely cap TikTok captions at 2,200")
    first_line = text.split("\n", 1)[0]
    hook_chars = len(first_line)
    fold = FOLD.get(key)
    if fold and hook_chars > fold:
        notes.append("first line is %d characters; the 'see more' fold is about %d" % (hook_chars, fold))
    return {
        "label": label,
        "platform": key,
        "count": count,
        "unit": unit,
        "limit": limit,
        "over_by": over_by,
        "fits": over_by == 0,
        "hashtags": len(tags),
        "urls": len(urls),
        "hook_chars": hook_chars,
        "fold": fold,
        "notes": notes,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Count social post drafts per platform.")
    ap.add_argument("file", nargs="?", help="JSON file: [{label, platform, text}]")
    ap.add_argument("--platform", help="platform for a single text")
    ap.add_argument("--text", help="the text (otherwise read from stdin)")
    args = ap.parse_args(argv)

    if args.platform:
        text = args.text if args.text is not None else sys.stdin.read()
        if args.text is None and text.endswith("\n"):
            text = text[:-1]
        items = [{"label": "1", "platform": args.platform, "text": text}]
    else:
        raw = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
        try:
            items = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(json.dumps({"error": "input is not valid JSON: %s" % exc}))
            return 2
        if isinstance(items, dict):
            items = [items]
    out = []
    for i, item in enumerate(items, 1):
        if not isinstance(item, dict) or "text" not in item or "platform" not in item:
            out.append({"label": str(i), "error": "each item needs platform and text"})
            continue
        out.append(count_one(str(item.get("label", i)), str(item["platform"]), str(item["text"])))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
