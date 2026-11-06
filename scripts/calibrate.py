#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure every detect.py rule on a human folder and an AI folder, side by side.

Usage:
    python3 scripts/calibrate.py --human <dir> [<dir> ...] --ai <dir> [<dir> ...] [--write] [--paired]

Why: the Chinese original kept only rules that survived a human-vs-AI comparison, and demoted
rules whose direction reversed. This English port ships without such data. Run this on your own
corpus (ideally PAIRED: same topic and facts, one human-written and one AI-written file each, with
matching file names in both folders, then pass --paired) to see which rules actually separate
human from AI writing in your genre.

Output: per metric, human mean, AI mean (per 1000 words, or the raw measure), ratio, and a verdict.
Paired mode adds counts of pairs where AI > human, AI < human, ties, and a two-sided sign-test p;
the verdict is then "AI higher"/"AI lower" at p < 0.05, "too rare" under 6 non-tied pairs, else "no diff".
Unpaired verdicts use the ratio:
    AI higher  (ratio >= 1.5 and AI median > 0)
    AI lower   (ratio <= 0.67)
    no diff    (otherwise)
For R/F rules, "AI higher" supports the rule, "AI lower" means move it to the X list, and
"no diff" means do not rewrite for it. For C measures read the direction yourself (a LOWER
sentence-length CV in AI text is the expected AI direction).
--write saves medians to references/calibration.json; detect.py then prints them as references.

Each file must have >= 300 words. Standard library only.
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from detect import (CALIB_PATH, CHAR_HITS, MIN_WORDS, REGEX_HITS, load_docs,  # noqa: E402
                    measure_docs)

STRUCT_KEYS = ["sentence_len_cv", "section_len_cv", "headings_per_1k", "list_line_share",
               "iso2_per_100p", "iso3_per_100p", "mtld", "nominalizations_per_1k"]


def per_file(dirs):
    rows = {}
    for d in dirs:
        for name, text in load_docs(Path(d)):
            r = measure_docs([(name, text)])
            if r["meta"]["words"] < MIN_WORDS:
                continue
            row = dict(r["density"])
            row.update(r["char_density"])
            row.update({k: v for k, v in r["structure"].items() if k in STRUCT_KEYS and v is not None})
            rows[Path(name).stem] = row
    return rows


def sign_test(pos, neg):
    """Two-sided exact binomial sign test p-value (ties excluded)."""
    n, k = pos + neg, min(pos, neg)
    if n == 0:
        return 1.0
    from math import comb
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def med(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.median(vals), 3) if vals else None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--human", nargs="+", required=True)
    ap.add_argument("--ai", nargs="+", required=True)
    ap.add_argument("--paired", action="store_true", help="match files by name; report median per-pair difference")
    ap.add_argument("--write", action="store_true", help="save medians to references/calibration.json")
    a = ap.parse_args()

    H, A = per_file(a.human), per_file(a.ai)
    if not H or not A:
        sys.exit("Need at least one file of >= 300 words on each side.")
    pairs = sorted(set(H) & set(A)) if a.paired else []
    if a.paired and not pairs:
        sys.exit("--paired: no matching file names between the two sides.")

    names = {rid: f"{rid} {nm}" for _, rid, nm, *_ in REGEX_HITS}
    names.update({nm: f"F {nm}" for _, nm, *_ in CHAR_HITS})
    names.update({k: f"C {k}" for k in STRUCT_KEYS})

    out, lines = {}, []
    hdr = (f"{'metric':42} {'hum mean':>8} {'AI mean':>8} {'AI/hum':>7}"
           + (f" {'AI>':>4} {'AI<':>4} {'tie':>4} {'p':>6}" if pairs else "") + "  verdict")
    lines += [f"human files: {len(H)}   AI files: {len(A)}" + (f"   pairs: {len(pairs)}" if pairs else ""), hdr, "-" * len(hdr)]
    for key, label in names.items():
        hv = [r[key] for r in H.values() if r.get(key) is not None]
        xv = [r[key] for r in A.values() if r.get(key) is not None]
        if not hv or not xv:
            continue
        h, x = round(statistics.mean(hv), 3), round(statistics.mean(xv), 3)
        ratio = (x / h) if h else (float("inf") if x else 1.0)
        verdict = "AI higher" if ratio >= 1.5 and x > 0 else "AI lower" if ratio <= 0.67 else "no diff"
        extra = ""
        if pairs:
            diffs = [A[p][key] - H[p][key] for p in pairs if A[p].get(key) is not None and H[p].get(key) is not None]
            pos, neg = sum(d > 0 for d in diffs), sum(d < 0 for d in diffs)
            p = sign_test(pos, neg)
            extra = f" {pos:>4} {neg:>4} {len(diffs) - pos - neg:>4} {p:>6.3f}"
            # paired mode: two-sided sign test on non-tied pairs decides
            if pos + neg < 6:
                verdict = "too rare"
            elif p < 0.05:
                verdict = "AI higher" if pos > neg else "AI lower"
            else:
                verdict = "no diff"
        r_s = "inf" if ratio == float("inf") else f"{ratio:.2f}"
        lines.append(f"{label[:42]:42} {h:>8} {x:>8} {r_s:>7}{extra}  {verdict}")
        out[key] = {"human": h, "ai": x, "verdict": verdict}

    print("\n".join(lines))
    print("\nVerdicts are descriptive for YOUR corpus. Small samples (<30 per side) are noisy;"
          " an R/F rule that comes out 'AI lower' should go to the X list in SKILL.md.")
    if a.write:
        CALIB_PATH.write_text(json.dumps({"n_human": len(H), "n_ai": len(A), "paired": bool(pairs),
                                          "metrics": out}, indent=1), encoding="utf-8")
        print(f"Saved {CALIB_PATH}")


if __name__ == "__main__":
    main()
