#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Before/after report: metric comparison + semantic-layer summary + marked-up revised text.

Usage (run detect.py --json on both versions first):
    python3 scripts/detect.py original.md --json --out before.json
    python3 scripts/detect.py revised.md  --json --out after.json
    python3 scripts/report.py original.md revised.md before.json after.json \
        [--semantic labeled.json] [--out report.md]

Default output is Markdown in the same format as the draft. In the comparison section the
revised text is shown in full; changes are marked <del>old</del><ins>new</ins> and all other
Markdown is left as-is so the text can be copied back into a writing workflow.
Standard library only.
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from detect import CHAR_HITS, REGEX_HITS  # noqa: E402

RENAME_VAL = {"0 sets": 0, "1 set": 1, "2 sets": 2, "3+ sets": 3}


def arrow(b, a, better="low"):
    if b is None or a is None:
        return "–"
    if a == b:
        return "="
    good = (a < b) if better == "low" else (a > b)
    return "↓ better" if (good and a < b) else "↑ better" if good else ("↑ worse" if a > b else "↓ worse")


def metric_table(d0, d1):
    rows = ["| Level | Rule | Before (hits, /1k words) | After | Change |", "|---|---|---|---|---|"]
    for lv, rid, nm, *_ in REGEX_HITS:
        if lv == "X":
            continue
        n0, n1 = len(d0["hits"][rid]), len(d1["hits"][rid])
        if n0 == n1 == 0:
            continue
        rows.append(f"| {lv} | {rid} {nm} | {n0} ({d0['density'][rid]}) | {n1} ({d1['density'][rid]}) | {arrow(n0, n1)} |")
    for _, nm, *_ in CHAR_HITS:
        n0, n1 = len(d0["char_hits"][nm]), len(d1["char_hits"][nm])
        if n0 == n1 == 0:
            continue
        rows.append(f"| F | {nm} | {n0} ({d0['char_density'][nm]}) | {n1} ({d1['char_density'][nm]}) | {arrow(n0, n1)} |")
    rows += ["", "| Structure (report only; no target value) | Before | After |", "|---|---|---|"]
    for k, v0 in d0["structure"].items():
        rows.append(f"| {k} | {v0} | {d1['structure'].get(k)} |")
    xs = [(rid, nm, len(d0["hits"][rid]), len(d1["hits"][rid])) for lv, rid, nm, *_ in REGEX_HITS if lv == "X"]
    rows += ["", "Do-not-touch (X) counts should be unchanged. A change means an X item was rewritten or a "
             "sentence holding one was removed; check it was deliberate:", ""]
    rows += [f"- {rid} {nm}: {b} → {a}" + ("  ⚠ changed, check" if a != b else "") for rid, nm, b, a in xs]
    return "\n".join(rows)


def semantic_summary(sem):
    if not sem:
        return "_No semantic-layer labels supplied._"
    out = []
    ren = [RENAME_VAL[c["label"]] for c in sem.get("rename", []) if c.get("label") in RENAME_VAL]
    if ren:
        heavy = sum(v >= 2 for v in ren) / len(ren)
        out.append(f"- Elegant variation: {sum(ren) / len(ren):.2f} per paragraph; {heavy:.0%} of paragraphs with ≥2 "
                   f"(report threshold borrowed from the Chinese study: ≥0.7 per paragraph or >15% heavy)")
    run = best = 0
    for c in sem.get("cohesion", []):
        run = run + 1 if c.get("label") == "Clear continuation" else 0
        best = max(best, run)
    if sem.get("cohesion"):
        weak = sum(c.get("label") == "Connective without real relation" for c in sem["cohesion"])
        out.append(f"- Cohesion chain: longest run of clear continuations = {best} (flag at ≥6); "
                   f"connectives without a real relation: {weak}")
    cols = [c for c in sem.get("colon", []) if c.get("label")]
    if cols:
        prose = [c for c in cols if c["label"] not in ("Quotation or speaker", "Metadata or layout")]
        concl = sum(c["label"] == "Conclusion announcement" for c in prose)
        out.append(f"- Colons: {concl} conclusion-announcement of {len(prose)} prose colons")
    iso = sum(c.get("label") == "Fully isomorphic" for c in sem.get("iso3", []))
    if sem.get("iso3"):
        out.append(f"- Isomorphic triples: {iso} fully isomorphic of {len(sem['iso3'])} candidates (flag at ≥2)")
    return "\n".join(out) or "_Semantic file has no labels._"


def paras(t):
    return re.split(r"\n\s*\n", t.strip())


def inline_diff(a, b):
    ta, tb = re.findall(r"\s+|[^\s]+", a), re.findall(r"\s+|[^\s]+", b)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        old, new = "".join(ta[i1:i2]), "".join(tb[j1:j2])
        if op == "equal":
            out.append(old)
        else:
            src = old if old.strip() else new
            lead = src[:len(src) - len(src.lstrip())]
            trail = src[len(src.rstrip()):]
            out.append(lead)
            if old.strip():
                out.append(f"<del>{old.strip()}</del>")
            if new.strip():
                out.append(f"<ins>{new.strip()}</ins>")
            out.append(trail)
    return "".join(out)


def diff_section(t0, t1):
    p0, p1 = paras(t0), paras(t1)
    out, changed = [], 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, p0, p1, autojunk=False).get_opcodes():
        if op == "equal":
            out += p1[j1:j2]
        elif op == "replace" and (i2 - i1) == (j2 - j1):
            for a, b in zip(p0[i1:i2], p1[j1:j2]):
                out.append(inline_diff(a, b))
                changed += 1
        else:
            out += [f"<del>{p}</del>" for p in p0[i1:i2]] + [f"<ins>{p}</ins>" for p in p1[j1:j2]]
            changed += max(i2 - i1, j2 - j1)
            if i2 - i1 != j2 - j1:
                out.append("> ⚠ Paragraph count changed here. The rewrite rules say structure stays put; check this.")
    return changed, "\n\n".join(out)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("json_before")
    ap.add_argument("json_after")
    ap.add_argument("--semantic")
    ap.add_argument("--out")
    a = ap.parse_args()
    t0 = Path(a.before).read_text(encoding="utf-8")
    t1 = Path(a.after).read_text(encoding="utf-8")
    d0 = json.loads(Path(a.json_before).read_text(encoding="utf-8"))
    d1 = json.loads(Path(a.json_after).read_text(encoding="utf-8"))
    sem = json.loads(Path(a.semantic).read_text(encoding="utf-8")) if a.semantic else None
    n, body = diff_section(t0, t1)
    md = "\n".join([
        f"# Less-AI-tone report: {Path(a.before).name} → {Path(a.after).name}", "",
        f"{d0['meta']['words']} → {d1['meta']['words']} words · {n} paragraph(s) changed", "",
        "## 1. Metrics before and after", "", metric_table(d0, d1), "",
        "## 2. Semantic layer", "", semantic_summary(sem), "",
        "## 3. Revised text with changes marked", "",
        "<del>struck</del> = removed original, <ins>underlined</ins> = new wording.", "", body, "",
    ])
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
        print(f"Wrote {a.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
