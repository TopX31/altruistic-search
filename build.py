#!/usr/bin/env python3
"""Build the Altruistic Righteousness transcript search site.

Usage:  python build.py
Reads every .srt in ./srt, applies ./corrections.txt, adds YouTube IDs from
./episodes.json, and writes ./index.html from ./template.html.

Transcript filenames must contain "Episode <number> - <title>", e.g.
"Episode 45 - Group Massage.srt" (underscores are fine too).
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRT_DIR = ROOT / "srt"
TIME = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")
NAME = re.compile(r"episode[\s_]*(\d+)[\s_]*-[\s_]*(.+)", re.I)


def secs(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_srt(path):
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    segs, end = [], 0
    for block in re.split(r"\n\s*\n", text):
        lines = block.strip().split("\n")
        for i, line in enumerate(lines):
            m = TIME.search(line)
            if m:
                start = secs(*m.groups()[:4])
                end = max(end, secs(*m.groups()[4:]))
                body = " ".join(l.strip() for l in lines[i + 1:] if l.strip())
                body = re.sub(r"\s+", " ", body).replace("’", "'").replace("‘", "'")
                if body:
                    segs.append([round(start, 1), body])
                break
    return segs, end


def load_corrections():
    """Read corrections.txt: 'wrong => right' and 'DELETE: text' lines."""
    path = ROOT / "corrections.txt"
    replace, delete = [], []
    if not path.exists():
        return replace, delete
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper().startswith("DELETE:"):
            delete.append(line[7:].strip().lower())
        elif "=>" in line:
            wrong, right = (part.strip() for part in line.split("=>", 1))
            if wrong:
                pattern = re.compile(r"(?<![\w'])" + re.escape(wrong) + r"(?!\w)", re.I)
                replace.append((pattern, right))
        else:
            print(f"Ignoring corrections line (no '=>'): {line}")
    return replace, delete


INLINE_LOOP = re.compile(r"\b((?:[\w'-]+[,.!?]?\s+){1,6}?)\1{4,}", re.I)
CHAR_LOOP = re.compile(r"(.{1,6}?)\1{8,}")


def trim_inline(text):
    """Cut 'word, word, word, ...' loops inside one line down to 3 repeats."""
    text = INLINE_LOOP.sub(lambda m: m.group(1) * 3, text + " ").strip()
    return CHAR_LOOP.sub(lambda m: m.group(1) * 3, text)


def trim_repeats(segs, limit=8, keep=3):
    """Whisper sometimes gets stuck and writes one line dozens of times.
    Any run of `limit`+ identical lines in a row is cut down to `keep`."""
    segs = [[s, trim_inline(t)] for s, t in segs]
    out, removed, i = [], 0, 0
    while i < len(segs):
        j = i
        key = segs[i][1].strip().lower()
        while j + 1 < len(segs) and segs[j + 1][1].strip().lower() == key:
            j += 1
        run = segs[i:j + 1]
        if len(run) >= limit:
            out.extend(run[:keep])
            removed += len(run) - keep
        else:
            out.extend(run)
        i = j + 1
    return out, removed


def apply_corrections(segs, replace, delete):
    out, changes = [], 0
    for start, text in segs:
        if any(d and d in text.lower() for d in delete):
            changes += 1
            continue
        for pattern, right in replace:
            text, n = pattern.subn(right, text)
            changes += n
        out.append([start, text])
    return out, changes


def main():
    replace, delete = load_corrections()
    total_changes = total_trimmed = 0
    yt = {}
    cfg = ROOT / "episodes.json"
    if cfg.exists():
        for k, v in json.loads(cfg.read_text(encoding="utf-8")).items():
            v = (v or "").strip()
            # Accept a full YouTube link or just the video ID.
            m = re.search(r"(?:v=|youtu\.be/|/live/|/shorts/)([\w-]{11})", v)
            yt[str(k)] = m.group(1) if m else v

    titles = {}
    tpath = ROOT / "titles.txt"
    if tpath.exists():
        for line in tpath.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=>" in line:
                num, title = (p.strip() for p in line.split("=>", 1))
                if num.isdigit() and title:
                    titles[int(num)] = title

    episodes = []
    seen = {}
    for path in sorted(SRT_DIR.glob("*.srt")):
        m = NAME.search(path.stem)
        if not m:
            print(f"Skipping (name doesn't match 'Episode N - Title'): {path.name}")
            continue
        num = int(m.group(1))
        if num in seen:
            print(f"WARNING: two files for episode {num}: {seen[num]} and {path.name}. Using the first.")
            continue
        seen[num] = path.name
        title = titles.get(num) or m.group(2).replace("_", " ").strip(" -")
        segs, end = parse_srt(path)
        segs, changes = apply_corrections(segs, replace, delete)
        segs, trimmed = trim_repeats(segs)
        total_changes += changes
        total_trimmed += trimmed
        episodes.append({"n": num, "t": title, "d": round(end), "yt": yt.get(str(num), ""), "s": segs})
        print(f"Episode {num}: {title}  ({len(segs)} lines, {int(end // 60)} min)")

    episodes.sort(key=lambda e: e["n"])
    data = json.dumps({"episodes": episodes}, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")  # safe inside <script>
    html = (ROOT / "template.html").read_text(encoding="utf-8").replace("/*__DATA__*/null", data)
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"Applied {total_changes} corrections, trimmed {total_trimmed} repeated lines")
    print(f"Built index.html with {len(episodes)} episodes ({len(html) // 1024} KB)")


if __name__ == "__main__":
    sys.exit(main())
