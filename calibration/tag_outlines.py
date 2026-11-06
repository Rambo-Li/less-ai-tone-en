"""Prepend '<!-- words: N -->' (word count of the matching human essay) to each outline that lacks it."""
import re
from pathlib import Path
H = Path(__file__).resolve().parent
for o in sorted((H / "outlines").glob("*.md")):
    t = o.read_text(encoding="utf-8")
    if "<!-- words:" in t:
        continue
    body = re.sub(r"<!--.*?-->", "", (H / "human" / o.name).read_text(encoding="utf-8"), flags=re.S)
    n = len(re.findall(r"[A-Za-z]+", body))
    o.write_text(f"<!-- words: {n} -->\n\n{t.strip()}\n", encoding="utf-8")
    print(n, o.name)
