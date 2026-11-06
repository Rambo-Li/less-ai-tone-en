"""Strip comments, related-post lists and nav lines from fetched essays; drop files under 350 words."""
import re, sys
from pathlib import Path
CUT = re.compile(r"^(?:#+ )?(?:Related posts|Recent Posts|Comments?|Responses?|Leave a (?:reply|comment)|Share this|About the author)\b|^- .{2,60} \(\d{4}-\d\d-\d\d\)$", re.I)
NAV = re.compile(r"^- (?:Top 10|Rock star developer|CEO|News|Reading List)(?:, .*)?$")
for f in sorted(Path(sys.argv[1]).glob("*.md")):
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        if CUT.search(line.strip()):
            break
        if NAV.match(line.strip()):
            continue
        out.append(line)
    text = "\n".join(out).strip() + "\n"
    n = len(re.findall(r"[A-Za-z]+", re.sub(r"<!--.*?-->", "", text)))
    if n < 350:
        f.unlink(); print(f"DROP {n:5} {f.name}")
    else:
        f.write_text(text, encoding="utf-8"); print(f"KEEP {n:5} {f.name}")
