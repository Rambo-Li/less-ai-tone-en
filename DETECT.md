# Detection protocol (step 1)

What detection does and what it never changes. Rewrite rules are in [SKILL.md](./SKILL.md).

## Why detect before rewriting

1. Many "AI tone" features are **distributions** (even rhythm, equal-length sections, never repeating a word). One sentence shows nothing, and fixing them sentence by sentence wrecks the text. They get a whole-document decision or no change.
2. The original project's v1 lesson: in a one-shot rewrite the model "fixes" everything that *feels* AI, including features that measured as *more* human (ordinal headings, questions, metaphors). A report with numbers, quotes and fixes, followed by a wait for the user, is the brake on over-cleaning.

## Three layers

| Layer | Handles | Who | Where |
|---|---|---|---|
| Script | countable symbols: phrase regexes, punctuation density, structure CV, MTLD | `detect.py` | this file |
| Semantic | needs meaning: elegant variation, cohesion chains, colon types, isomorphic triples | the session's model | [references/semantic-criteria.md](./references/semantic-criteria.md) |
| Human | models can't agree: metaphor aptness, personification | the user | SKILL.md human-review zone |

Regexes only catch fixed surface forms. Models catch paraphrases but carry their own "sounds like AI" bias, so the semantic layer uses closed label sets judged item by item, never an overall score.

## Running

```bash
python3 scripts/detect.py <file-or-dir> [--max-hits 5] [--json] [--out file]   # script layer
python3 scripts/detect.py <file> --candidates --out candidates.json             # semantic candidates
python3 scripts/report.py original revised before.json after.json \
    [--semantic labeled.json] --out report.md                                  # before/after report
python3 scripts/calibrate.py --human <dir> --ai <dir> [--paired] [--write]     # build your own baseline
```

## Grades

Grade = **rewrite risk**, not how strong the signal is.

| Grade | Meaning | Strategy |
|---|---|---|
| **A mechanical** | Fixed phrase or punctuation; deleting it doesn't touch meaning ("Let's dive in") | Review for false positives, propose, rewrite after reply |
| **B suggested** | Needs a sentence rebuilt or a word swapped (trailing -ing clause, inflated word) | Review each hit, propose with examples, rewrite after reply |
| **C report only** | Whole-document structure and rhythm | No change by default; only on explicit request |
| **H human review** | Metaphor / personification aptness | Keep by default; list only on request |
| **X do not touch** | Folk "AI tells" that evidence contradicts (passive voice, numbered headings) | Never rewrite; counts must be unchanged after the rewrite |
| **F fingerprint** | Per-model habits (em dash, semicolon, bold, emoji) | Locatable, safely rewritable hits are proposed; keep needs a reason |

## Script rules

| ID | Grade | Pattern | Evidence |
|---|---|---|---|
| R1 | A | Not-X-but-Y reframe | ZH-borrowed + EN-observed |
| R2 | A | Announcement colon ("The bottom line:") | ZH-borrowed + EN-observed |
| R3 | A | Throat-clearing ("It's worth noting", "Let's dive in") | EN-observed |
| R4 | A | Paragraph-opening signpost ("Moreover,") | ZH-borrowed + EN-observed |
| R5 | A | Chatbot residue ("I hope this helps") | EN-observed |
| R6 | B | Inflated vocabulary ("delve", "pivotal") | EN-corpus (Kobak 2025; Liang 2024) |
| R7 | B | Trailing -ing commentary | EN-corpus (Reinhart 2025) + EN-observed |
| R8 | B | Significance inflation ("serves as", "a testament to") | EN-observed |
| R9 | B | Stacked triads | ZH-borrowed + EN-observed |
| R10 | B | Hedge stacking ("may potentially") | EN-observed |
| R11 | H | Personified tool / grand metaphor | EN-observed |
| R12 | B | Elegant variation (synonym rotation, heuristic) | semantic layer decides |
| X1–X4 | X | Numbered headings, "this means", passive voice, questions | see SKILL.md X list |
| F | F | Em dash, semicolon, bold in prose, emoji | per-model; contested |
| C | C | Sentence-length CV, section CV, headings/1k, list share, adjacent isomorphism, MTLD, nominalizations | report only |

Thresholds marked [tunable] in `detect.py` are guesses until `calibrate.py` gives you medians for your genre.

## Reading the output

Script output is **candidate data for the model, not a verdict for the user.** The model reviews every hit and the pre-edit report connects "pattern → this draft's count → evidence → quote → fix". Review never silently deletes a candidate: for each locatable rule report raw hits, valid hits, to-change and kept; false positives and negative semantic labels keep a count and reason. Whole-document measures get a value, not invented per-sentence counts. A pattern being more frequent in LLM text across a corpus is not a significance test on this draft, and never evidence about the author.

Common false positives to strip during review:
- R6 technical senses (robust estimator, crucial experiment, vital signs, a legal "landscape" of cases is still flagged but may be literal geography)
- R9 ordinary single triads and enumerations of facts
- R1 real rebuttals of a claim the article quotes
- R2 "The result?" in a genuine Q&A layout
