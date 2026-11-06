#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI-tone detection report for English prose (step 1 of less-ai-tone-en; detects only, never rewrites).

Usage:
    python3 scripts/detect.py <file-or-dir> [--json] [--max-hits 5]
    python3 scripts/detect.py <file> --candidates [--out candidates.json]

--candidates extracts semantic-layer candidates (elegant-variation paragraphs, paragraph
junctions, colon sentences, isomorphic triples) for the in-session model to label with
references/semantic-criteria.md.

Grades (by *rewrite risk*, not by how "AI" a feature feels):
    A  mechanical   fixed phrase or punctuation; deleting/replacing it does not touch meaning
    B  suggested    needs a sentence rebuilt or a word swapped; review each hit
    C  report only  whole-document distribution (rhythm, sectioning); never fixed sentence by sentence
    H  human review metaphor / personification aptness; models disagree, so the user decides
    X  do not touch looks "AI" in folk lists but evidence says no (or the reverse); shown to prevent over-cleaning
    F  fingerprint  per-model habits (em dash, semicolon, bold); direction depends on the model

Reference values: this English port has NO measured corpus of its own yet. Rows show
"uncalibrated" until you run scripts/calibrate.py on your own human-vs-AI folders, which
writes references/calibration.json; detect.py then shows those medians.
Evidence notes per rule are in SKILL.md and RESEARCH.md.

Adapted from lieflat-less-ai-tone (CC BY-NC 4.0, (c) 2026 shiujan). Standard library only.
"""
import argparse
import json
import re
import statistics
import sys
from pathlib import Path

EXTS = {".md", ".txt", ".markdown"}
HERE = Path(__file__).resolve().parent
CALIB_PATH = HERE.parent / "references" / "calibration.json"
MIN_WORDS = 300

AP = r"['’]"  # straight or curly apostrophe
I = re.IGNORECASE

# ---------------- Regex rules: (level, id, name, pattern, flags, advice) ----------------

REGEX_HITS = [
    # ---- A: mechanical ----
    ("A", "R1", "Not-X-but-Y reframe",
     r"\b(?:it|this|that)(?:" + AP + r"s| is| was)\s+not\s+(?:just |only |merely |simply |really )?(?:about )?"
     r"[^.;:!?\n]{1,60}?(?:,|;|—|–|--)\s*(?:it|this|that)(?:" + AP + r"s| is| was)\b"
     r"|\b(?:isn" + AP + r"t|wasn" + AP + r"t|aren" + AP + r"t|is not|are not|was not)\s+(?:just |only |merely |simply |really )?"
     r"(?:about )?[^.;!?\n]{1,50}?(?:,|;|—|–|--)\s*(?:it" + AP + r"s|they" + AP + r"re|it is|they are|it was)\b"
     r"|\bnot because [^.!?\n]{1,60}?,? but because\b"
     r"|\bless about [^.!?\n]{1,50}? and more about\b"
     r"|\bnot (?:just|merely|simply) (?:a |an |the )?[^.,;!?\n]{1,40}?(?:,|—|–|--)?\s*but\b",
     I, "State the claim directly; drop the straw-man half unless the reader really holds that view. Rule 1"),
    ("A", "R2", "Announcement colon",
     r"\b(?:here" + AP + r"s (?:the (?:thing|kicker|catch|deal|truth|takeaway|bottom line|problem|twist)|why|what (?:matters|happened))"
     r"|the (?:bottom line|key takeaway|takeaway|short answer|upshot|kicker|catch|real story|reality|truth|result|answer|verdict)"
     r"|in short|simply put|put simply|long story short|in a nutshell|the key (?:insight|point|lesson)"
     r"|the real (?:question|problem|issue|lesson)|my (?:take|verdict|answer))\s*[:?]",
     I, "Delete the announcement and say the point; if the clause links to the previous one, keep it and change only the punctuation. Rule 2"),
    ("A", "R3", "Throat-clearing phrase",
     r"\blet" + AP + r"s (?:dive|delve|dig) (?:in|into|deeper)\b|\blet" + AP + r"s (?:break (?:it|this|that) down|unpack (?:this|that|it))\b"
     r"|\bit(?:" + AP + r"s| is) (?:worth (?:noting|mentioning|pointing out|highlighting)|important to (?:note|remember|recognize|understand|emphasize))\b"
     r"|\bneedless to say\b|\bat the end of the day\b"
     r"|\bin today" + AP + r"s (?:fast-paced|digital|ever-changing|rapidly evolving|modern|interconnected)\b"
     r"|\bin (?:the|an|this) (?:ever-evolving|ever-changing|rapidly evolving|fast-moving) (?:world|landscape|space|era)\b",
     I, "Delete; start with the content. Rule 3"),
    ("A", "R4", "Paragraph-opening signpost",
     r"^\s{0,3}(?:Moreover|Furthermore|Additionally|In addition|Consequently|Notably|Importantly|Ultimately|Overall"
     r"|In conclusion|In summary|To summarize|To sum up|Crucially|Interestingly|Indeed),",
     0, "Delete, move inside the sentence, or use a plainer link (But / So / Also). Keep where the argument truly needs the marker. Rule 4"),
    ("A", "R5", "Chatbot residue",
     r"\bI hope (?:this|that) helps\b|\bfeel free to\b|\blet me know if you\b|\bas an AI\b|\bhappy to help\b"
     r"|^\s*(?:Certainly|Absolutely|Great question|Of course)[!.,]|\bI" + AP + r"d be happy to\b",
     I | re.MULTILINE, "Delete. Rule 5"),
    # ---- B: suggested ----
    ("B", "R6", "Inflated vocabulary",
     r"\b(?:delv(?:e|es|ed|ing)|underscor(?:e|es|ed|ing)|showcas(?:e|es|ed|ing)|pivotal|intricate|intricacies"
     r"|tapestry|testament|realm|multifaceted|meticulous(?:ly)?|commendable|bolster(?:s|ed|ing)?|garner(?:s|ed|ing)?"
     r"|embark(?:s|ed|ing)?|unwavering|holistic|paramount|seamless(?:ly)?|leverag(?:e|es|ed|ing)|foster(?:s|ed|ing)?"
     r"|robust|crucial|vital|nuanced|navigat(?:e|es|ing) (?:the|this|these|a|an) (?:complex|complexities|challenges|landscape|world)"
     r"|landscape|game[- ]chang(?:er|ing)|elevat(?:e|es|ed|ing)|unlock(?:s|ed|ing)?|harness(?:es|ed|ing)?"
     r"|streamlin(?:e|es|ed|ing)|cutting[- ]edge|groundbreaking|transformative|empower(?:s|ed|ing)?|resonat(?:e|es|ed|ing)"
     r"|noteworthy|myriad|plethora|interplay|ever-evolving|in the realm of|boast(?:s|ed|ing)?)\b",
     I, "Swap for the plain word only where the plain word says the same thing; technical uses (robust statistics, a vital sign) stay. Rule 6"),
    ("B", "R7", "Trailing -ing clause",
     r",\s+(?:highlighting|underscoring|emphasizing|emphasising|showcasing|reflecting|demonstrating|illustrating|signaling|signalling"
     r"|ensuring|enabling|allowing|paving|cementing|reinforcing|fostering|marking|solidifying|contributing|underlining"
     r"|setting the stage|making it (?:easier|possible|clear))\b[^.!?\n]{0,90}[.!?]",
     I, "Make the commentary its own sentence with a real subject, or cut it if it only restates. Rule 7"),
    ("B", "R8", "Significance inflation",
     r"\b(?:serves as|stands as|acts as) (?:a |an |the )|\bplays? an? (?:crucial|key|pivotal|vital|significant|central|major|important|critical) role\b"
     r"|\ba testament to\b|\b(?:underscores|highlights|emphasizes) the (?:importance|need|significance|value)\b"
     r"|\bmarks? an? (?:significant|pivotal|major|important|key) (?:shift|step|milestone|moment|turning point)\b",
     I, "Use is/does and say what it concretely does. Rule 8"),
    ("B", "R9", "Stacked triad",
     r"\b[A-Za-z][\w-]*(?: [\w-]+){0,2}, [\w-]+(?: [\w-]+){0,2},? and [\w-]+(?: [\w-]+){0,2}\b",
     0, "Where triads stack (several per paragraph), merge or summarize one; keep lists the content really needs. Rule 9"),
    ("B", "R10", "Hedge stacking",
     r"\b(?:may|might|could) (?:potentially|possibly|perhaps|conceivably)\b|\bit could be argued\b"
     r"|\b(?:may|might|could) (?:help (?:to )?)?(?:potentially )?contribute to\b",
     I, "Keep one hedge at the strength the evidence supports; never remove the hedge entirely. Rule 10"),
    # ---- H: human review ----
    ("H", "R11", "Personified tool / grand metaphor",
     r"\blike (?:a|an) (?:tireless|trusted|wise|patient|seasoned|digital|virtual|personal|faithful|skilled) "
     r"(?:assistant|guide|mentor|partner|companion|guardian|coach|navigator|architect|conductor|gatekeeper|co-?pilot)\b"
     r"|\b(?:symphony|tapestry|beacon|north star|double-edged sword|cornerstone|linchpin|dance) of\b",
     I, "Human review only. If the user asks, say what the thing actually does. Rule 11"),
    # ---- X: do-not-touch (counted so nobody 'fixes' them) ----
    ("X", "X1", "Numbered headings (do not touch)",
     r"^\s{0,3}#{1,6}\s*(?:\d+[.)]|Step \d+|Part \d+)", re.MULTILINE,
     "Ordinal headings are normal in human how-to writing; the Chinese paired study found humans use them MORE. Leave."),
    ("X", "X2", "'This means' restatement (do not touch)",
     r"\b(?:this|that) (?:means|suggests|shows|tells us)\b|\bin other words\b", I,
     "Reversed in the Chinese paired study (humans more); no English evidence it is an AI tell. Leave."),
    ("X", "X3", "Passive voice (do not touch)",
     r"\b(?:is|are|was|were|been|being|be)\s+(?:\w+ly\s+)?\w+ed\b(?: by\b)?", I,
     "Instruction-tuned LLMs use FEWER agentless passives than humans (Reinhart et al. 2025). 'Fixing' passives pushes text toward AI. Leave."),
    ("X", "X4", "Questions in prose (do not touch)",
     r"[A-Za-z][^.!?\n]{8,}\?", 0,
     "Rhetorical and real questions are common in human prose; deleting them makes text flatter. Leave."),
]

# Character / span fingerprints: (level, name, pattern, advice)
CHAR_HITS = [
    ("F", "Em dash", r"—|(?<=\w) -- (?=\w)|(?<=\w) – (?=\w)",
     "Popular 'ChatGPT dash' claim; per-model and per-writer. Review each one above ~3/1000 words; keep dashes doing real work."),
    ("F", "Semicolon", r";", "Split where one sentence carries too many layers; keep true parallel structure."),
    ("F", "Bold in prose", r"\*\*[^*\n]{2,80}\*\*", "Bold sprinkled through running prose is a chat-interface habit; keep bold for real warnings/terms."),
    ("F", "Emoji", r"[\U0001F300-\U0001FAFF☀-➿]", "Emoji headings/bullets are a chat habit; keep only if the venue uses them."),
]

# Elegant-variation synonym groups (heuristic; the semantic layer decides)
SYN_GROUPS = [
    ("use", "utilize", "leverage", "employ", "harness"),
    ("improve", "enhance", "boost", "elevate", "optimize", "strengthen"),
    ("show", "demonstrate", "reveal", "highlight", "underscore", "illustrate"),
    ("important", "crucial", "vital", "key", "pivotal", "essential", "critical"),
    ("problem", "challenge", "issue", "hurdle", "obstacle", "pain point"),
    ("help", "assist", "support", "empower", "enable"),
    ("method", "approach", "strategy", "framework", "methodology"),
    ("company", "firm", "organization", "business", "enterprise"),
]

# Thresholds [tunable]: heuristics until calibrated
TH_SENT_CV = 0.45
TH_SECT_CV = 0.45      # calibrated: human mean 0.63 / Claude 0.38
TH_HEAD_KW = 4.0        # headings per 1000 words; calibrated: human 1.6 / Claude 6.8
TH_ISO2_100P = 8.0
TH_LIST_SHARE = 0.35    # share of non-blank lines that are list items

# ---------------- splitting ----------------

HEADING = re.compile(r"^#{1,6}\s")
BOLD_LINE = re.compile(r"^\*\*[^*]{2,80}\*\*:?$")
LIST_LINE = re.compile(r"^\s{0,3}(?:[-*+]|\d+[.)])\s")
QUOTE_LINE = re.compile(r"^>")
FENCE = re.compile(r"^\s*```")
TABLE_LINE = re.compile(r"^\|")
WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
FUNCTION_FIRST = {"the", "a", "an", "it", "this", "that", "these", "they", "we", "you", "i",
                  "but", "and", "so", "if", "when", "what", "how", "why", "each", "every", "no"}


def words(s):
    return WORD.findall(s)


def strip_md(t):
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"`[^`]*`", "code", t)
    t = re.sub(r"[*_#>]", "", t)
    return t.strip()


def split_sents(para):
    para = strip_md(para).replace("\n", " ")
    parts = re.split(r"(?<=[.!?])[\"”’)]*\s+(?=[A-Z\"“(‘'0-9])", para)
    return [p.strip() for p in parts if len(words(p)) >= 3]


def paragraph_blocks(text):
    """Split on blank lines and classify: [(kind, text, first_line_no)]."""
    blocks, cur, cur_kind, start = [], [], None, None
    in_fence = False
    for no, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            if not cur:
                start = no
            cur.append(line)
            cur_kind = "code"
            continue
        if not in_fence and not line.strip():
            if cur:
                blocks.append((cur_kind or "prose", "\n".join(cur), start))
                cur, cur_kind, start = [], None, None
            continue
        if not cur:
            start = no
        cur.append(line)
        if in_fence:
            cur_kind = "code"
        elif HEADING.match(line) or (BOLD_LINE.match(line.strip()) and cur_kind is None and len(cur) == 1):
            cur_kind = "heading"
        elif QUOTE_LINE.match(line):
            cur_kind = cur_kind or "quote"
        elif TABLE_LINE.match(line):
            cur_kind = cur_kind or "table"
        elif LIST_LINE.match(line):
            cur_kind = cur_kind or "list"
    if cur:
        blocks.append((cur_kind or "prose", "\n".join(cur), start))
    return blocks


def signature(sent):
    """Coarse sentence skeleton: commas, colon/semicolon, parentheses, length bucket, opening word."""
    w = words(sent)
    first = w[0].lower() if w else ""
    return (sent.count(","), bool(re.search(r"[:;]", sent)), "(" in sent,
            len(w) // 7, first if first in FUNCTION_FIRST else "*")


def iso_runs(sents, n):
    out = []
    for i in range(len(sents) - n + 1):
        sig = [signature(s) for s in sents[i:i + n]]
        if all(s == sig[0] for s in sig) and (sig[0][0] >= 1 or sig[0][4] != "*"):
            out.append(sents[i:i + n])
    return out


def mtld(toks, threshold=0.72, min_len=10):
    if len(toks) < 100:
        return None

    def factors(seq):
        f, types, count = 0.0, set(), 0
        for t in seq:
            count += 1
            types.add(t)
            if count >= min_len and len(types) / count <= threshold:
                f += 1
                types, count = set(), 0
        if count:
            f += (1 - len(types) / count) / (1 - threshold)
        return max(f, 1e-9)

    return round(len(toks) / 2 * (1 / factors(toks) + 1 / factors(toks[::-1])))


def cv(vals):
    if len(vals) < 2:
        return None
    m = sum(vals) / len(vals)
    return (statistics.pstdev(vals) / m) if m else None


NOMINAL = re.compile(r"\b[a-z]{4,}(?:tion|tions|sion|sions|ment|ments|ness|ity|ities|ance|ence)\b", I)

# ---------------- measuring ----------------

def prose_lines(text):
    """Yield (line_no, line) outside code fences, skipping tables."""
    in_fence = False
    for no, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or TABLE_LINE.match(line):
            continue
        yield no, line


def measure_docs(docs):
    total_words = 0
    regex_hits = {rid: [] for _, rid, *_ in REGEX_HITS}
    char_counts = {name: 0 for _, name, *_ in CHAR_HITS}
    char_hits = {name: [] for _, name, *_ in CHAR_HITS}
    syn_hits = []
    n_para = n_head = n_lines = n_list = 0
    iso2 = iso3 = 0
    sent_lens, sect_lens, toks = [], [], []
    nominal = 0
    compiled = [(lv, rid, nm, re.compile(p, fl | re.MULTILINE), adv) for lv, rid, nm, p, fl, adv in REGEX_HITS]
    ccompiled = [(lv, nm, re.compile(p), adv) for lv, nm, p, adv in CHAR_HITS]

    for fname, text in docs:
        for no, line in prose_lines(text):
            if line.strip():
                n_lines += 1
                if LIST_LINE.match(line):
                    n_list += 1
            is_head = bool(HEADING.match(line))
            for lv, rid, nm, rx, _ in compiled:
                if is_head and lv != "X":
                    continue
                if rid == "X1" and not is_head:
                    continue
                for m in rx.finditer(line):
                    regex_hits[rid].append({"file": fname, "line": no, "excerpt": m.group(0)[:90]})
            for lv, nm, rx, _ in ccompiled:
                if nm == "Bold in prose" and (is_head or LIST_LINE.match(line) or BOLD_LINE.match(line.strip())):
                    continue
                for m in rx.finditer(line):
                    char_counts[nm] += 1
                    char_hits[nm].append({"file": fname, "line": no,
                                          "excerpt": line[max(0, m.start() - 40): m.end() + 40].strip()})

        blocks = paragraph_blocks(text)
        sect = 0
        for kind, body, first_no in blocks:
            if kind == "heading":
                n_head += 1
                if sect:
                    sect_lens.append(sect)
                sect = 0
                continue
            if kind in ("code", "table"):
                continue
            w = words(strip_md(body))
            total_words += len(w)
            sect += len(w)
            if kind != "prose":
                continue
            n_para += 1
            toks.extend(x.lower() for x in w)
            nominal += len(NOMINAL.findall(body))
            sents = split_sents(body)
            sent_lens.extend(len(words(s)) for s in sents)
            iso2 += len(iso_runs(sents, 2))
            iso3 += len(iso_runs(sents, 3))
            low = " " + strip_md(body).lower() + " "
            for group in SYN_GROUPS:
                found = [g for g in group if re.search(r"\b" + re.escape(g) + r"(?:s|es|d|ed|ing)?\b", low)]
                if len(found) >= 2:
                    syn_hits.append({"file": fname, "line": first_no, "excerpt": " / ".join(found),
                                     "context": strip_md(body)[:110]})
        if sect:
            sect_lens.append(sect)

    kw = total_words / 1000 or 1
    sc = cv(sent_lens)
    sec = cv(sect_lens) if len(sect_lens) >= 3 else None
    return {
        "meta": {"files": len(docs), "words": total_words, "paragraphs": n_para,
                 "headings": n_head, "sentences": len(sent_lens)},
        "density": {rid: round(len(v) / kw, 3) for rid, v in regex_hits.items()},
        "char_density": {nm: round(n / kw, 3) for nm, n in char_counts.items()},
        "hits": regex_hits,
        "char_hits": char_hits,
        "syn_hits": syn_hits,
        "structure": {
            "sentence_len_cv": round(sc, 3) if sc else None,
            "mean_sentence_words": round(sum(sent_lens) / len(sent_lens), 1) if sent_lens else None,
            "section_len_cv": round(sec, 3) if sec else None,
            "headings_per_1k": round(n_head / kw, 2),
            "list_line_share": round(n_list / n_lines, 3) if n_lines else None,
            "iso2_per_100p": round(iso2 / n_para * 100, 2) if n_para else None,
            "iso3_per_100p": round(iso3 / n_para * 100, 2) if n_para else None,
            "mtld": mtld(toks),
            "nominalizations_per_1k": round(nominal / kw, 1),
        },
    }


# ---------------- semantic candidates ----------------

CAND_CAPS = {"rename": 60, "cohesion": 60, "colon": 80, "iso3": 60}


def extract_candidates(docs):
    rename, cohesion, colon, iso3 = [], [], [], []
    for fname, text in docs:
        blocks = [(strip_md(b), no) for k, b, no in paragraph_blocks(text) if k == "prose"]
        blocks = [(b, no) for b, no in blocks if len(words(b)) >= 15]
        for b, no in blocks:
            if len(words(b)) >= 40:
                rename.append({"type": "rename", "file": fname, "line": no, "para": b})
        for i in range(len(blocks) - 1):
            a, b = blocks[i][0], blocks[i + 1][0]
            tail = split_sents(a) or [a[-200:]]
            head = split_sents(b) or [b[:200]]
            cohesion.append({"type": "cohesion", "file": fname, "line": blocks[i + 1][1],
                             "prev_tail": tail[-1], "next_head": head[0]})
        for no, line in prose_lines(text):
            if HEADING.match(line) or LIST_LINE.match(line) or re.search(r"https?://", line):
                continue
            clean = strip_md(line)
            for m in re.finditer(r"([^:.!?\n]{3,120}):\s+(\S.{1,160})", clean):
                if re.search(r"\d$", m.group(1)):  # times, ratios
                    continue
                colon.append({"type": "colon", "file": fname, "line": no,
                              "colon_before": m.group(1).strip(), "colon_after": m.group(2)[:160],
                              "sentence": clean[:240]})
        for k, body, no in paragraph_blocks(text):
            if k == "prose":
                for run in iso_runs(split_sents(body), 3):
                    iso3.append({"type": "iso3", "file": fname, "line": no, "sents": run})
    allc = {"rename": rename, "cohesion": cohesion, "colon": colon, "iso3": iso3}
    meta = {f"n_{k}": len(v) for k, v in allc.items()}
    trunc = {k: CAND_CAPS[k] for k, v in allc.items() if len(v) > CAND_CAPS[k]}
    for k, cap in trunc.items():  # even sampling, not head-biased
        step = len(allc[k]) / cap
        allc[k] = [allc[k][int(i * step)] for i in range(cap)]
    meta["truncated"] = trunc or False
    meta["n_candidates"] = sum(len(v) for v in allc.values())
    meta["instructions"] = ("Label each item per references/semantic-criteria.md: add label (closed set only), "
                            "confidence (high/medium/low), reason (one sentence). Judge each item alone.")
    return {"meta": meta, **allc}


# ---------------- report ----------------

def load_calibration():
    try:
        return json.loads(CALIB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def ref_str(calib, key):
    if not calib or key not in calib.get("metrics", {}):
        return "uncalibrated"
    m = calib["metrics"][key]
    return f"human mean {m['human']} / AI mean {m['ai']}, {m['verdict']} (calibration, {calib['n_human']} pairs)"


def fmt_report(r, max_hits):
    calib = load_calibration()
    m = r["meta"]
    out = ["AI-tone detection report (less-ai-tone-en; detects only, rewrites nothing)", "",
           f"Corpus: {m['files']} file(s) / {m['words']} words / {m['paragraphs']} paragraphs / "
           f"{m['sentences']} sentences / {m['headings']} headings", ""]
    if not calib:
        out += ["Note: no calibration file. Densities below have no measured human baseline yet;",
                "treat them as counts to review, not as evidence the text is AI-written.", ""]

    titles = {"A": "Mechanical candidates (review, then propose; rewrite only after the user replies)",
              "B": "Suggested candidates (review each hit; rewrite only after the user replies)",
              "H": "Human-review zone (default keep; list only if the user asks)",
              "X": "Do-not-touch features (counted to prevent over-cleaning; never rewrite)"}
    for level in "ABHX":
        sec = [f"[{level}] {titles[level]}"]
        any_row = False
        for lv, rid, nm, _, _, adv in REGEX_HITS:
            if lv != level:
                continue
            hits = r["hits"][rid]
            if not hits:
                continue
            any_row = True
            sec.append(f"  {rid} {nm}: {len(hits)} hit(s), {r['density'][rid]}/1000 words  [ref: {ref_str(calib, rid)}]")
            sec.append(f"    -> {adv}")
            if level != "X":
                for h in hits[:max_hits]:
                    sec.append(f"      · {h['file']}:{h['line']}  {h['excerpt']}")
        if any_row:
            out += sec + [""]

    if r["syn_hits"]:
        out.append("[B] R12 Elegant variation (heuristic synonym rotation; the semantic layer decides)")
        for h in r["syn_hits"][:max_hits * 2]:
            out.append(f"  · {h['file']}:{h['line']}  rotates: {h['excerpt']}")
            out.append(f"    {h['context']}")
        out.append("")

    out.append("[F] Fingerprints (per-model habits; never infer which model wrote the text)")
    for _, nm, _, adv in CHAR_HITS:
        n = len(r["char_hits"][nm])
        out.append(f"  {nm}: {n} ({r['char_density'][nm]}/1000 words)  [ref: {ref_str(calib, nm)}]")
        out.append(f"    -> {adv}")
        for h in r["char_hits"][nm][:max_hits if n else 0]:
            out.append(f"      · {h['file']}:{h['line']}  …{h['excerpt']}…")
    out.append("")

    s = r["structure"]
    out.append("[C] Structure and rhythm (whole-document; report only, never 'fix' sentence by sentence)")
    flags = []
    if s["sentence_len_cv"] is not None and s["sentence_len_cv"] < TH_SENT_CV:
        flags.append(f"sentence-length CV {s['sentence_len_cv']} (< {TH_SENT_CV}: even rhythm)")
    if s["section_len_cv"] is not None and s["section_len_cv"] < TH_SECT_CV:
        flags.append(f"section-length CV {s['section_len_cv']} (< {TH_SECT_CV}: sections of near-equal length)")
    if s["headings_per_1k"] > TH_HEAD_KW:
        flags.append(f"{s['headings_per_1k']} headings per 1000 words (> {TH_HEAD_KW}: chopped into many sections)")
    if s["list_line_share"] and s["list_line_share"] > TH_LIST_SHARE:
        flags.append(f"{int(s['list_line_share'] * 100)}% of lines are list items (> {int(TH_LIST_SHARE * 100)}%: list-heavy)")
    if s["iso2_per_100p"] is not None and s["iso2_per_100p"] > TH_ISO2_100P:
        flags.append(f"adjacent same-skeleton sentences {s['iso2_per_100p']}/100 paragraphs (> {TH_ISO2_100P})")
    for f_ in flags:
        out.append(f"  ! {f_}")
    if not flags:
        out.append("  (no structure flags at current heuristic thresholds)")
    out.append(f"  raw: sentence CV {s['sentence_len_cv']} / mean sentence {s['mean_sentence_words']} words / "
               f"section CV {s['section_len_cv']} / MTLD {s['mtld']} / nominalizations {s['nominalizations_per_1k']}/1000 "
               f"/ 3-sentence isomorphic runs {s['iso3_per_100p']}/100p")
    out.append("")
    out.append("Order: A first, then B and the semantic layer. C needs structural edits outside the whitelist; "
               "only on explicit request. This output is candidate data for the model, not a report for the user.")
    return "\n".join(out)


def load_docs(p):
    docs = []
    if p.is_file():
        docs.append((p.name, p.read_text(encoding="utf-8", errors="ignore")))
    else:
        for f in sorted(p.rglob("*")):
            if f.is_file() and f.suffix.lower() in EXTS:
                docs.append((str(f.relative_to(p)), f.read_text(encoding="utf-8", errors="ignore")))
    return docs


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="English AI-tone detector (detect only).")
    ap.add_argument("target", help="file or directory (.md/.txt)")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--max-hits", type=int, default=5, help="examples listed per rule")
    ap.add_argument("--candidates", action="store_true", help="extract semantic-layer candidates instead")
    ap.add_argument("--out", help="write output to this path instead of stdout")
    args = ap.parse_args()

    p = Path(args.target)
    if not p.exists():
        sys.exit(f"Path not found: {p}")
    docs = load_docs(p)
    if not docs:
        sys.exit("No .md/.txt files found")

    if args.candidates:
        payload = json.dumps(extract_candidates(docs), ensure_ascii=False, indent=1)
    else:
        r = measure_docs(docs)
        if r["meta"]["words"] < MIN_WORDS:
            sys.exit(f"Too short ({r['meta']['words']} words < {MIN_WORDS}); density measures are meaningless.")
        payload = json.dumps(r, ensure_ascii=False, indent=1) if args.json else fmt_report(r, args.max_hits)

    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
