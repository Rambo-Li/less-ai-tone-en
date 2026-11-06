---
name: less-ai-tone-en
description: Remove AI tone from finished English prose in three layers. A script grades candidates (A mechanical / B suggested / C report-only / H human review / X do-not-touch / F fingerprint), the model labels four semantic checks (elegant variation, cohesion chains, conclusion colons, isomorphic triples), and the user first gets a readable pre-edit report with counts, evidence strength, quoted sentences and concrete fixes. Only after the user replies does it rewrite by whitelisted rules, re-run detection and produce a before/after report (Markdown by default). English port of lieflat-less-ai-tone; use for cleaning up a finished draft, not for writing one.
---

# Less AI Tone (English)

Find and rewrite AI writing patterns in English text. The order is fixed: **detect, explain the findings with numbers and quoted sentences, wait for the user's reply, then rewrite, re-test and deliver.** The report should be professional and easy to read: what the evidence says about each pattern, how often it occurs in this draft, and why those spots are worth changing. The model does the triage; it does not hand the user forty candidates and a metaphor list to decide one by one. "Go ahead" / "apply the suggestions" is enough to continue; the user can also narrow the scope in one sentence.

This is an adaptation of [lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone), whose rules were kept or dropped by two rounds of measurement on Chinese (629 essays, then 270 same-topic same-facts pairs). **This English version has one round of measurement so far:** 43 pre-2022 human blog essays paired with 43 Claude essays written from neutral outlines of the same essays (same topic and facts, never the wording; see "Calibration results" below and [RESEARCH.md](./RESEARCH.md)). No GPT side yet. Every rule carries an evidence tag, and the report must use it honestly:

| Tag | Meaning |
|---|---|
| **[EN-corpus]** | A published English corpus study found the pattern more frequent in LLM text |
| **[EN-observed]** | Widely documented by editors (e.g. Wikipedia's "Signs of AI writing" field guide), not controlled-measured |
| **[ZH-borrowed]** | Measured in the Chinese study; the English analogue is assumed, not verified |
| **[cal: Claude ✓]** | The paired calibration found it significantly more frequent in Claude's essays (sign test p < 0.05) |
| **[cal: Claude ✗]** | The calibration found it *less* frequent in Claude's essays, or no difference: do not present it as a Claude tell |
| **[cal: rare]** | Fewer than 6 of 43 pairs had it at all: no verdict |

Layers: **anything countable goes to the script** (`detect.py`), **anything needing sentence meaning goes to the semantic layer** (this session's model, judging by the closed criteria in [references/semantic-criteria.md](./references/semantic-criteria.md)), **anything models cannot agree on goes to the human** (metaphor aptness, personification).

## Workflow (in this order)

### Step 1: script detection

```bash
python3 scripts/detect.py <file-or-dir> [--max-hits 5]
python3 scripts/detect.py <file> --json --out before.json     # always save the pre-edit JSON; step 4 needs it
```

(`python` instead of `python3` on Windows.) Grade meanings are in [DETECT.md](./DETECT.md). Under 300 words the script refuses: densities mean nothing on short text. For short text, do the semantic and rule review by reading, and say no script numbers were available.

If `references/calibration.json` exists, the script prints the user's own human/AI medians next to each rule. Use those numbers and the [calibrated] tag in the report.

### Step 1.5: semantic layer (always for a single file; optional for folders)

```bash
python3 scripts/detect.py <file> --candidates --out candidates.json
```

Label every candidate (elegant-variation paragraphs, paragraph junctions, colon sentences, isomorphic triples) per [references/semantic-criteria.md](./references/semantic-criteria.md), writing `label` / `confidence` / `reason` back into the JSON. Discipline: judge by the criterion not the overall feel, judge each item alone, take the fallback label when unsure, never invent labels. Then compute the four summary numbers at the end of that file.

### Step 2: report findings and suggestions, then stop

Deliver a **professional, readable pre-edit report** and end the turn. Length follows the article; never a one-line impression, never raw script output. It must include:

1. **Method and scope.** What the script counted, what the semantic layer judged; word count, paragraphs, candidates. Separate "this pattern is more common in LLM text in study X" from "this draft has N hits". No single-document significance test was run, so never say the draft is statistically AI-like, and never conclude the author used AI.
2. **Results and where each hit went.** A compact table of the A/B rules and F fingerprints: for every locatable rule, **raw hits, valid hits, to-change, kept**, density per 1000 words, the reference (calibrated medians if available, else "no English baseline") and the evidence tag. Whole-document measures (sentence-length CV, section CV) get the value and the decision only; do not invent per-sentence counts. Rules with zero hits can be listed briefly. Never drop a rule from the table because you decided to keep its hits.
3. **Examples and fixes.** For each rule you propose to act on, quote 1–2 sentences with line numbers, explain what the pattern does to a reader, and give a concrete fix. A short illustrative rewrite is fine; the full revised text is not, and nothing is written to the draft yet. Keep facts, hedges and information; never write "make it sound more natural".
4. **What you will not touch**, briefly: X items found, H items (default kept), C measures (reported only).
5. **One closing line:** reply "go ahead" to apply these suggestions, or say what to change.

**No silent deletions.** Raw script hits and semantic candidates stay in the JSON. Review only adds a status to each (to-change / keep / false positive / unsure–human) with a reason. A semantic "does not meet the criterion" is a recorded outcome and counts toward the raw → valid difference. If the user gave a file, keep the per-item results file; the main report explains the counts with typical examples, and the user does not tick items.

**Default for valid, locatable A/B hits is "to-change".** A low count or a density below a threshold changes the priority, not the decision. "Keep" is an exception that needs a specific reason: the phrase is a quotation, a term of art, a real logical relation, the author's documented style, or the minimum rewrite would lose information. "Reads fine", "only one" or "humans write this too" are not reasons. If you cannot decide, mark it unsure and show it.

Example paragraph in the right register (one rule only):

> The script found 3 "not X but Y" reframes (7.0 per 1000 words; no calibrated English baseline yet; [ZH-borrowed], the strongest signal in the Chinese paired study, and listed as "negative parallelism" in Wikipedia's field guide [EN-observed]). Two sit at the end of a paragraph as its conclusion: line 7, "Speed isn't about working longer hours — it's about removing the steps that slow decisions down", and line 15, "It is not just a process — it is a mindset." Nobody in the piece claimed speed was about longer hours, so the first half argues with a reader who isn't there. Suggest stating the point directly, "Speed comes from removing the steps that slow decisions down", which keeps both the claim and the "decisions" qualifier.

This report is **the only checkpoint**. After sending it, stop. **Do not rewrite before the user replies.**

When the user says "ok", "go ahead", "apply", go straight to step 3 with no second confirmation. When they adjust the scope, follow it. A question or "wait" is not consent; answer or pause. "Fix everything" means all reviewed to-change items in A + B + semantic + locatable F; not X, not C, not H, unless the user names those explicitly. Quoted material is never edited.

### Step 3: rewrite

Change only the items the user accepted. Follow the rewrite principles below. Log every change as "original → new + rule id" for step 4.

### Step 4: re-test and before/after report

```bash
python3 scripts/detect.py revised.md --json --out after.json
python3 scripts/report.py original.md revised.md before.json after.json \
    --semantic candidates_labeled.json --out less-ai-tone-report.md
```

The report has metrics before/after, the semantic summary, and the full revised text with `<del>old</del><ins>new</ins>` marks (other Markdown untouched, so it can be copied back).

Reading the re-test: every reviewed to-change A/B/semantic/F hit should be gone; kept false positives are explained. **X counts must be unchanged**: a drop means something was over-cleaned; revert it. C measures get numbers but **no target value**. Pushing sentence-length CV up by making sentences randomly long and short is mechanical "burstiness" and worse than leaving it.

## Rewrite principles (why AI rewrites usually go wrong)

**1. Minimal change.** Fix only what the hit requires. No polishing on the side, no swapping words that were fine, no changes to tone or length. When unsure, keep the original. Every extra edit is a new risk to meaning.

**2. Conserve information.** Claims, facts, names, numbers, dates, quotations, sources, causal links and hedges all survive. Every content word in the revision must trace back to the original. Turning "may" into "will" changes the claim; that is not removing AI tone.

**3. Do not manufacture burstiness.** Do not chop and stretch sentences to look human. The Chinese paired study found no human/AI difference in sentence-length spread; the English calibration found Claude only slightly more even (CV 0.55 vs 0.59), far too small to steer a rewrite. Rhythm stays a C-level note.

**4. Keep the structure.** Heading levels, section and paragraph order, lists, tables, block quotes and code blocks stay where they are. Numbered headings stay numbered (X1).

**5. Read the style guide first.** If the folder has a style guide or voice document, read it before rewriting; it wins over these rules. An author who loves dashes keeps them.

**6. Self-check after rewriting.**
- Can every change name its accepted item and rule id? If not, revert it.
- Does every content word have a source in the original? If not, revert it.
- After re-test: are the to-change A/B hits cleared, are kept false positives explained, are X counts unchanged, and did C measures stay roughly where they were?

## Leave alone

- The article's framework (above)
- Dialogue, conversational and deliberately informal writing
- Questions, rhetorical questions and question headings (X4)
- Literary prose: parallelism and metaphor follow the author's style
- Genre conventions: academic, legal, news and technical writing do not need "I/you" added, and passive voice is not a fault (X3)
- Code, quotations, text in other languages
- The whole X list below

---

## Rewrite rules (by priority)

### 1. Not-X-but-Y reframe  [ZH-borrowed] [EN-observed] [cal: Claude ✓]

Set up a misreading the reader never had, then knock it down: "It's not about X, it's about Y", "X isn't Z — it's W", "less about X and more about Y", "not because X, but because Y", "not just X, but Y". Any surface form that performs the same move counts.

Evidence: in the English calibration, 10 of the 12 pairs that differed had more reframes on the Claude side (0.28 vs 0.10 per 1000 words, p = 0.04). It was also the strongest pure-writing signal in the Chinese study (round 1: AI 0.73 vs human 0.22 per 1000 characters; confirmed in the paired round for both GPT and Opus). Listed as "negative parallelism" in Wikipedia's field guide.

Fix: state the claim directly, verdict first, reason after.

> ❌ The real moat isn't technology — it's distribution.
> ✅ The real moat is distribution.

Keep when the misreading is real and named in the text (the article is rebutting a specific claim), and plain "not only… but also" coordination.

### 2. Announcement colon  [ZH-borrowed] [EN-observed] [cal: rare]

A teaser before a colon announces that a conclusion is coming: "Here's the thing:", "The bottom line:", "The takeaway:", "In short:", "The result?", "The answer:".

Evidence: Chinese round 1 AI 3.8×; the semantic "conclusion announcement" colon was 2.1× in the paired round.

Fix: if the teaser carries no information, delete it and write the point. If the first half links back to the previous sentence, keep it and change only the punctuation.

> ❌ The bottom line: fewer people means fewer handoffs.
> ✅ Fewer people means fewer handoffs.

Leave: colons that introduce a quotation or a list ("Three options:", empty lead-ins are X-type: humans use them more), headings, labels, times, URLs.

### 3. Throat-clearing phrases  [EN-observed] [cal: rare]

"Let's dive in", "Let's break it down", "It's worth noting that", "It's important to remember", "Needless to say", "At the end of the day", "In today's fast-paced world", "In the ever-evolving landscape of…". Delete and start with the content. Zero information loss.

### 4. Paragraph-opening signposts  [ZH-borrowed] [EN-observed] [cal: rare]

"Moreover,", "Furthermore,", "Additionally,", "Ultimately,", "In conclusion," at the start of paragraphs, especially several in a row. The Chinese analogue (然而/因此/此外) is one of its four kept translationese patterns. Delete, move the link inside the sentence, or use a plainer one ("But", "So", "Also"). Keep when the argument truly needs the explicit marker.

### 5. Chatbot residue  [EN-observed] [cal: rare]

"I hope this helps", "Feel free to…", "Let me know if you…", "Certainly!", "Great question". Text pasted from a chat window. Delete.

### 6. Inflated vocabulary  [EN-corpus] [cal: Claude ✗]

delve, underscore, showcase, pivotal, intricate, tapestry, testament, realm, landscape, multifaceted, meticulous, commendable, bolster, garner, embark, unwavering, holistic, paramount, seamless, leverage, foster, robust, crucial, nuanced, elevate, unlock, harness, streamline, transformative, empower, myriad, plethora, interplay.

Evidence: Kobak et al. (2025) measured "excess vocabulary" in millions of PubMed abstracts after ChatGPT's release ("delves", "underscores", "showcasing", "pivotal" and others rose sharply); Liang et al. (2024) found the same for "commendable", "meticulous", "intricate" in peer reviews. These are corpus-level shifts in two genres, mostly from 2023–24 ChatGPT. In the English calibration, Claude's essays used these words *less* than the human essays (0.11 vs 0.30 per 1000 words). Treat the list as a ChatGPT-era habit and as plain style advice, never as evidence about the author; one hit in one draft proves nothing.

Fix: swap for the plain word **only where the plain word says the same thing** ("underscores" → "shows", "leverage" → "use", "pivotal" → "key" or cut). Technical senses stay: robust statistics, a crucial experiment in a lab report, a vital sign. Several in one paragraph is the priority. **Do not swap one fancy word for another fancy word**; that is elegant variation (rule 12).

### 7. Trailing -ing commentary  [EN-corpus] [EN-observed] [cal: rare]

A participle tacked onto the end of a factual sentence to add significance: "…shipped in a week, highlighting the power of tight feedback loops." "…, ensuring that everyone stays aligned." "…, paving the way for…".

Evidence: Reinhart et al. (2025, PNAS) report instruction-tuned LLMs use present participial clauses at roughly 2–5× the human rate. Wikipedia's field guide calls the tacked-on version "superficial analysis".

Fix: if the clause only restates or inflates, cut it. If it carries a real claim, give it its own sentence with a real subject, and check the claim is supported.

> ❌ Revenue rose 12% in Q3, underscoring the strength of the new pricing model.
> ✅ Revenue rose 12% in Q3, the first full quarter under the new pricing.  *(only if the article says so; otherwise just cut)*

### 8. Significance inflation  [EN-observed] [cal: rare]

"serves as", "stands as", "plays a crucial role in", "a testament to", "underscores the importance of", "marks a pivotal shift". The verb inflates instead of saying what happens. Fix: use "is"/"does" and say concretely what it does. If you can't say what it does, the sentence had no content; flag it to the user instead of inventing one.

### 9. Stacked triads  [ZH-borrowed] [EN-observed] [cal: Claude ✗ no diff]

Lists of three ("faster, cheaper, and more reliable"; "by embracing autonomy, fostering trust, and streamlining communication") piling up, several per paragraph. The Chinese study found dense in-sentence lists 1.45× in AI text; Wikipedia's guide calls this the "rule of three". Single triads are normal English. Fix only the stack: merge or summarize one list, or change the syntax of one item. Never delete required content, legal lists, specs or Markdown lists.

### 10. Hedge stacking  [EN-observed] [cal: rare]

"may potentially", "could possibly", "it could be argued that". Keep **one** hedge at the strength the evidence supports. Never remove the hedge entirely: that changes the claim (principle 2).

### 11. Personified tools and grand metaphors (human review, never automatic)  [EN-observed]

"like a trusted navigator", "a tireless assistant", "a symphony of ideas", "a rich tapestry of", "a beacon of". Whether a metaphor is apt is exactly what models disagree on (0–40% agreement in the original study). Default: keep. If the user asks for an H review, list the sentences without grading them. If they ask to de-metaphor one, say plainly what the thing actually does.

### 12. Elegant variation (semantic layer)  [ZH-borrowed] [EN-observed: Fowler 1926]

Same entity renamed within a paragraph ("the initiative / the program / the effort"; "improve / enhance / boost"). Fix: bring the chain back to one name. Leave different entities that share similar names, formal "also known as" introductions, and literary variation.

### 13. Cohesion chains (semantic layer)  [ZH-borrowed]

≥6 paragraph junctions in a row that each hook onto the last ("This also explains…", "Building on this…", "With that in mind…"). Fix: turn 1–2 junctions into a natural jump; let the topic follow the material. Check first that the junction carries no cause or setup. Leave tutorials and legal text, where tight chaining is the genre.

### 14. Conclusion-announcement colon (semantic layer)  [ZH-borrowed]

The semantic version of rule 2: only colons where the first half is a standalone verdict or teaser and the second half reveals or argues it. Same fix.

### 15. Isomorphic triples (semantic layer, fingerprint-strength)  [ZH-borrowed]

Three sentences on one skeleton ("Each handoff introduces delay. Each delay introduces cost. Each cost introduces risk."). Only the fully isomorphic tier counts. Fix: break the skeleton in one sentence (merge, split, reorder), keeping every item. Leave speeches, poetry, lists and narrative sequence.

### F. Fingerprints

**Fingerprints are per-model habits in research corpora; they never tell you which model wrote a text,** and the report never says "this was written by model X". Unknown-source text is checked the same way.

- **Em dash** [EN-observed, contested] [cal: Claude ✗]: the famous "ChatGPT dash". In the English calibration the *human* essays had the dashes: 2.6 per 1000 words against 0.07 for Claude, with the human side higher in 31 of 32 pairs that differed. In the Chinese study one model overused them and another underused them. A dash-heavy draft is not evidence of AI writing, and a dash-free one is not evidence of a human. Above ~3 per 1000 words, review each one: decorative pauses and dashes that hold back a verdict ("The answer is simple — focus.") get rewritten as plain sentences or commas; dashes doing real work (an aside, an interruption, a speaker's voice) stay with a reason. Never *add* dashes, and never strip an author's documented habit.
- **Semicolon:** split where one sentence carries too many layers; keep true parallel structure.
- **Bold in running prose** [cal: Claude ✓, 7 vs 0 pairs]: a chat-interface habit. Unbold mid-sentence emphasis unless it marks a real warning or a defined term.
- **Emoji in headings/bullets:** remove unless the venue uses them.

---

## Calibration results (Claude, November 2026)

43 pairs: pre-2022 tech and startup blog essays by 8 authors (Joel Spolsky, Dan Luu, Julia Evans, Jeff Atwood, Patrick McKenzie, Ben Kuhn, Paul Graham, Derek Sivers), each paired with a Claude (Opus 5.5) essay of matched length written from a neutral outline of the same essay. Sign test over pairs; full table in RESEARCH.md.

| Pattern | Human | Claude | Pairs (Claude more / less) | Verdict |
|---|---|---|---|---|
| Headings per 1000 words (C) | 1.6 | 6.8 | 43 / 0 | **strongest signal** |
| Section-length CV (C) | 0.63 | 0.38 | 2 / 11 | Claude sections more even |
| R1 Not-X-but-Y reframe | 0.10 | 0.28 | 10 / 2 | Claude more |
| Bold in running prose (F) | 0 | 0.59 | 7 / 0 | Claude more |
| Em dash (F) | 2.62 | 0.07 | 1 / 31 | **humans more** |
| X3 Passive voice | 4.25 | 2.77 | 13 / 30 | humans more (keeps X3) |
| Sentence-length CV (C) | 0.59 | 0.55 | 14 / 29 | Claude slightly more even |
| R6 Inflated vocabulary | 0.30 | 0.11 | 4 / 11 | no difference |
| R9 Stacked triads, semicolons, questions, MTLD | — | — | — | no difference |
| R2–R5, R7, R8, R10, R11 | ~0 | ~0 | <6 pairs differ | too rare to judge |

How to use this in the report:
- **Over-sectioning is the clearest measured Claude habit:** a heading every ~150 words, sections of near-equal length. It stays a C item (structure is not rewritten without the user's explicit request), but put it first among the C notes, with the numbers.
- Do not present the folk lists (inflated words, em dashes, throat-clearing) as signs of Claude. They are still worth fixing as plain style, under their own rules, but the report says what the calibration found.
- Caveats: one model, one genre, 43 pairs. The Claude essays were written inside an agent harness, whose instructions may suppress some habits that raw chat output shows. ChatGPT-era habits (the -ing tail, "delve") may show on a GPT side that has not been measured yet.

## X list (never rewrite; counted only to prevent over-cleaning)

| Pattern | Why it stays |
|---|---|
| X1 Numbered / "Step 1" headings | Normal in human how-to writing; the Chinese paired study found humans use ordinal headings *more* (8.6% vs 4.9%) |
| X2 "This means" / "In other words" restatement | Reversed in the Chinese paired study (humans more); no English evidence it is an AI tell |
| X3 Passive voice | Reinhart et al. (2025) found instruction-tuned LLMs use *fewer* agentless passives than humans, and the English calibration agrees: Claude 2.8 vs human 4.2 per 1000 words, human higher in 30 of 43 pairs (p = 0.01). Converting passive to active pushes text toward AI style |
| X4 Questions in prose | Common in human prose (calibration: human 3.7 vs Claude 2.6 per 1000 words, not significant); deleting them flattens the text |
| Sentence-length "burstiness" | Detector folklore; no rewrite target. Rhythm stays a C note |
| Contractions, "I/you", Oxford comma | Style and genre choices, not AI tells. Never added or removed for tone |
| Precise numbers, "First/Second/Finally" | Not shown to differ; the Chinese study found no difference for numbers and ordinals |
| Empty colon lead-ins to a list | Humans used them far more in the Chinese study |

When your own `calibrate.py` run shows an R/F rule as "AI lower" for your genre, add it here.

## Human-review only (the skill does not judge)

- Metaphor aptness, mixed metaphors, grandiose imagery
- Personification of tools and systems
- Whether three parallel examples are padding (needs meaning, not pattern)
- Whether rhythm variation is natural or mechanical

---

## Final acceptance

- The pre-edit report listed this draft's counts, the evidence tag and reference for each rule, locatable quotes, concrete fixes and exclusions, and the skill waited for a reply before rewriting
- No claim of single-document significance and no claim about authorship; [ZH-borrowed] and [EN-observed] rules were not presented as measured English facts
- Semantic labels follow the discipline: closed labels only, each item alone, fallback when unsure
- Every change maps to an accepted item and rule id; minimal change; no polishing on the side
- All content words have a source; hedges ("may", "often") survived
- Structure unchanged: headings, paragraph order, lists, tables, quotes, code
- X counts unchanged in the re-test (no passives "fixed", no questions removed, no numbered headings renumbered)
- No manufactured burstiness, no "I/you" added
- Dashes handled only per the fingerprint rule
- Re-test and before/after report delivered; to-change A/B hits cleared; C measures did not swing
