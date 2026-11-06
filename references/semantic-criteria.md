# Semantic-layer criteria (four checks)

Detection has three layers. Anything you can count as symbols goes to the script (`detect.py`). Anything that needs the meaning of a sentence goes here, judged item by item by the model in the session. Anything models cannot agree on (metaphor aptness) goes to the human (see the human-review zone in SKILL.md).

How to use: run `python3 scripts/detect.py <file> --candidates --out candidates.json`. For every item, add three fields: `label` (from that check's closed set only), `confidence` (high / medium / low) and `reason` (one sentence). Save the JSON; `report.py --semantic` summarizes it.

**Judging discipline** (carried over from the original project's ~500,000 labelling runs):
- Judge by the criterion, never by "does this sound like AI". Overall impressions are fooled by style.
- Judge each item on its own. Candidates deliberately omit the full text so you cannot guess from the overall voice.
- When unsure, pick the fallback label. Do not force a verdict.
- Use only the labels listed. Never invent one.

**Evidence status for English.** All four checks and their thresholds come from the Chinese paired study (270 same-topic, same-facts pairs). They have not been re-measured on English. "Elegant variation" has a long history as an English style fault (Fowler, 1926), which is some independent support; the other three are unverified in English. Report them as "flagged by the borrowed threshold", never as "statistically significant".

---

## 1. Elegant variation (per paragraph)

**What it is:** the same entity or concept gets renamed with a different content word inside one paragraph, so the reader has to work out "X is the same thing as Y". Example: one paragraph calls the same project "the initiative", "the program", "the effort" and "the undertaking"; or rotates "improve / enhance / boost / elevate" for one action. Chinese study: AI 0.83–0.86 per paragraph vs human 0.49; paragraphs with ≥2 renamings AI ~21% vs human 8%.

**Candidate:** one per paragraph (`para`).

| Label | Criterion |
|---|---|
| 0 sets | Every entity/concept keeps one name (or a near-identical one) throughout, or appears once |
| 1 set | One entity/concept is renamed once with a different content word |
| 2 sets | Two entities are each renamed, or one is renamed twice |
| 3+ sets | Three or more renamings |
| Cannot judge | Paragraph cannot be analysed |

Pronouns, ellipsis and "it/this/they" do not count. Different entities that happen to have similar names do not count. A formal "also called X" on first introduction does not count.

**Rewrite direction (after the user agrees):** bring the chain back to the original noun. Zero information loss; repeating the plain name is what human writers do.

---

## 2. Cohesion (paragraph junctions)

**What it is:** every paragraph opens by grabbing the last idea of the one before ("This also explains why…", "Building on this…", "With that in mind…"), so there is never a jump. Chinese study: AI essays have a median longest chain of 7 clear continuations vs 2 for humans; 93% of AI essays had a chain of ≥6. The problem is not connective words (rare on both sides); it is the zero chance of a jump. The reader never has to infer anything.

**Candidate:** one per junction (`prev_tail` = last sentence of paragraph a, `next_head` = first sentence of paragraph b).

| Label | Criterion |
|---|---|
| Connective without real relation | b opens with a connective (However / Therefore / As a result / Meanwhile …) but the relation it signals does not actually hold, or barely holds. **Check this first** |
| Clear continuation | Both sides develop the same object or argument; synonyms, pronouns and ellipsis allowed; any connective is logically valid |
| Related but abrupt | Same topic area, but a step is missing; the reader must fill in the jump |
| Topic jump without signal | b moves to a largely unrelated topic with no signal |
| Cannot judge | Not enough context |

**Summary:** longest run of consecutive "Clear continuation" junctions. Flag at ≥6.

**Rewrite direction:** in a long chain, turn 1–2 junctions into a natural jump: let the topic follow the material without pre-announcing it. Fix "Connective without real relation" first. Never break a junction that carries cause or setup.

---

## 3. Colon type

**What it is:** in the Chinese study, colons overall were used *more* by humans; only the "conclusion announcement" type was an AI signal (2.1–2.2×), and the "empty lead-in to a list" type was reversed (humans far more). English needs the same split: "Here's the thing:" style colons are the suspected tell; "Three options:" before a list is normal.

**Candidate:** one per prose colon (`colon_before`, `colon_after`, `sentence`).

Judge top to bottom; stop at the first match.

| Label | Criterion |
|---|---|
| Quotation or speaker | Introduces someone's words (name + colon in an interview, or "said / wrote / announced:"). **Takes priority** |
| Metadata or layout | Title structure, timestamps, ratios, source/author, labels like "Note:" or "Example:" |
| Definition or content | Before the colon is a term or name; after it, its definition or contents |
| Empty lead-in | Before the colon only announces that something follows ("There are three reasons:"), no claim; after it, a plain list. **Do-not-touch type** |
| Conclusion announcement | Before the colon is a complete, standalone verdict or a teaser for one ("The lesson is clear:", "This reveals a harsh truth:"); after it, the argument or reveal. **The only signal** |
| Other prose colon | Anything else |
| Cannot judge | Not enough context. Do not overuse |

**Rewrite direction (only "Conclusion announcement"):** delete the teaser and state the content, or, if the first half links back to earlier text, keep it and change only the punctuation.

---

## 4. Isomorphic triples (fingerprint tier, weaker evidence)

**What it is:** three consecutive sentences on one syntactic skeleton with only the words swapped ("Each handoff introduces delay. Each delay introduces cost. Each cost introduces risk."). A loose definition (sentences that are merely similar) did not separate AI from humans in the Chinese study; only the *fully isomorphic* tier did (AI 29% vs human 11% of triples).

**Candidate:** consecutive three-sentence groups caught by a coarse signature (`sents`). The filter is loose; judge strictly.

| Label | Criterion |
|---|---|
| Fully isomorphic | Subject, verb, object and modifiers sit in matching positions in all three; same frame, different words |
| Partly isomorphic | Clearly similar structure but not every slot matches, or one sentence adds/loses a part |
| Repeated words, different syntax | Shared words or phrases, but the sentences are built differently |
| Parallel content, different syntax | Same kind of content (three examples), different structures |
| No isomorphism | Neither syntactic nor content parallelism |
| Cannot judge | Fragments or not enough context |

**Rewrite direction:** break the skeleton in one of the three (merge, split, reorder, or shorten). Do not delete an item of content. Deliberate rhetoric (speeches, poetry), lists and narrative sequence ("first this happened, then that") stay.

---

## Summary used in the report

| Measure | How | Borrowed flag threshold |
|---|---|---|
| Elegant variation per paragraph | Σ(label values) / paragraphs | ≥0.7, or >15% of paragraphs at "2 sets" or more |
| Cohesion chain | longest run of "Clear continuation" | ≥6 |
| Conclusion-colon share | "Conclusion announcement" / prose colons | relatively high → B |
| Isomorphic triples | count of "Fully isomorphic" | ≥2 → B |
