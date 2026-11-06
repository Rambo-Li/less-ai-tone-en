#!/usr/bin/env python3
"""Download pre-2022 blog essays and save the first ~1200 words of each as Markdown.

For local measurement only: the essays are copyrighted and must not be redistributed
(calibration/human/ is git-ignored). Usage: python fetch_human.py urls.txt human/
"""
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

MAX_WORDS, MIN_WORDS = 1200, 400
SKIP = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg", "figure"}
BLOCK = {"p": "", "h1": "# ", "h2": "## ", "h3": "### ", "h4": "### ", "li": "- ", "blockquote": "> "}


class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.cur = None
        self.buf = []
        self.blocks = []
        self.font_p = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        elif tag in BLOCK and not self.skip:
            self.flush()
            self.cur = BLOCK[tag]
        elif tag == "br" and self.cur is not None and self.cur == "" and self.buf:
            # paulgraham.com uses <br><br> inside <font> instead of <p>
            self.buf.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip:
            self.skip -= 1
        elif tag in BLOCK:
            self.flush()

    def handle_data(self, data):
        if not self.skip and self.cur is not None:
            self.buf.append(data)

    def flush(self):
        if self.cur is not None:
            raw = "".join(self.buf)
            for piece in re.split(r"\n\s*\n", raw):
                t = re.sub(r"\s+", " ", piece).strip()
                if len(t.split()) >= 3 or self.cur.startswith("#"):
                    if t:
                        self.blocks.append(self.cur + t)
        self.cur, self.buf = None, []


def pg_blocks(html):
    """paulgraham.com: body text sits in one <font> with <br><br> paragraph breaks."""
    m = re.search(r"<font size=\"?2\"? face=\"?verdana\"?>(.*?)</font>", html, re.S | re.I)
    if not m:
        return None
    body = re.sub(r"<br\s*/?>\s*<br\s*/?>", "\n\n", m.group(1), flags=re.I)
    body = re.sub(r"<[^>]+>", "", body)
    import html as h
    return [re.sub(r"\s+", " ", h.unescape(p)).strip() for p in body.split("\n\n") if len(p.split()) >= 3]


def to_md(url, html):
    blocks = pg_blocks(html) if "paulgraham.com" in url else None
    if not blocks:
        e = Extract()
        e.feed(html)
        e.flush()
        blocks = e.blocks
    out, n = [], 0
    for b in blocks:
        if re.search(r"(?i)^(- )?(share|tweet|subscribe|comments?|posted|filed under|related|previous|next)\b", b):
            continue
        w = len(b.split())
        if n + w > MAX_WORDS and n >= MIN_WORDS:
            break
        out.append(b)
        n += w
    return "\n\n".join(out), n


def main():
    urls = [l.split()[0] for l in Path(sys.argv[1]).read_text().splitlines() if l.strip() and not l.startswith("#")]
    dest = Path(sys.argv[2])
    dest.mkdir(parents=True, exist_ok=True)
    for i, url in enumerate(urls, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", url.lower().split("//")[1]).strip("-")[:60]
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (calibration script)"})
            html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        except Exception as ex:
            print(f"FAIL {url}: {ex}")
            continue
        md, n = to_md(url, html)
        if n < MIN_WORDS:
            print(f"SHORT {n:5} {url}")
            continue
        (dest / f"{i:02d}-{slug}.md").write_text(f"<!-- source: {url} -->\n\n{md}\n", encoding="utf-8")
        print(f"OK    {n:5} {url}")


if __name__ == "__main__":
    main()
