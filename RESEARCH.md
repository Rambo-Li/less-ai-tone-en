# Evidence notes

This file records where each rule's justification comes from and how strong it is. The short version: **the English port has no measured corpus of its own.** It combines (a) results from the Chinese original that are assumed to transfer, (b) a few published English corpus studies, and (c) editors' field observations. Run `scripts/calibrate.py` on your own material to replace guesses with numbers.

## Sources

**Chinese original:** lieflat-less-ai-tone by shiujan (CC BY-NC 4.0), https://github.com/larashero3-dotcom/lieflat-less-ai-tone. Round 1: 629 essays (5 models × 60 vs 329 human, unpaired). Round 2: 270 same-topic, same-facts pairs (GPT and Opus vs human), plus ~430,000 semantic labels. Its key methodological lesson, which this port keeps: unpaired comparisons are confounded by topic; several "AI tells" from round 1 *reversed* when paired, and were moved to a never-change list.

**English corpus studies used:**
- Kobak, González-Márquez, Horvát, Lause. "Delving into LLM-assisted writing in biomedical publications through excess vocabulary." *Science Advances*, 2025 (arXiv 2406.07016). Measured words whose frequency in PubMed abstracts jumped after 2023 (e.g. "delves", "underscores", "showcasing", "pivotal"). → rule 6.
- Liang et al. "Monitoring AI-Modified Content at Scale: A Case Study on the Impact of ChatGPT on AI Conference Peer Reviews." ICML 2024. Adjectives such as "commendable", "meticulous", "intricate" rose in peer reviews. → rule 6.
- Reinhart, Markey, Laudenbach, et al. "Do LLMs write like humans? Variation in grammatical and rhetorical styles." *PNAS*, 2025. Instruction-tuned models used present participial clauses and nominalizations well above human rates and agentless passives below them. → rule 7; X3 (passive voice stays); nominalization density is reported in C only.

**Field observation:**
- Wikipedia: WikiProject AI Cleanup, "Signs of AI writing" (a living editors' guide). Lists negative parallelisms, rule of three, superficial -ing analyses, undue emphasis on significance, promotional words, em dash overuse, chatbot residue and more. Observational, not a controlled study. → tags [EN-observed].
- Fowler, *A Dictionary of Modern English Usage* (1926), "elegant variation": a style fault long before LLMs, which is some support for rule 12 independent of AI.

**Check before relying on these:** the citations above were written from memory when this skill was created (November 2026). Verify the exact findings before quoting them to a reader.

## Round 1 calibration: human vs Claude (November 2026)

**Corpus.** 43 human essays from 8 tech/startup bloggers (Joel Spolsky 8, Dan Luu 9, Julia Evans 6, Jeff Atwood 7, Patrick McKenzie 5, Ben Kuhn 5, Paul Graham 2, Derek Sivers 1), all published before ChatGPT (Nov 2022), each cut to its first ~1200 words at a paragraph break. Fetched with `calibration/fetch_human.py` and cleaned of comments and navigation with `clean_human.py`. Not redistributed (git-ignored).

**AI side.** For each essay a Claude Sonnet helper wrote a neutral brief (own-words outline + fact list, no quotes, no style notes). A separate Claude Opus 5.5 helper, which saw only the brief, wrote a post of matching length ("Write a blog post of about N words based on the brief below. Write it in the first person as the blog's author. Use Markdown."). Lengths matched: mean ratio 0.97, none outside ±30%. One writer run was stopped by a content filter (likely the well-known 12-question list in one brief) and was rerun with "write everything in your own words".

**Test.** Per-file densities from `detect.py`; for each metric, a two-sided sign test over the 43 pairs, ties excluded.

```
human files: 43   AI files: 43   pairs: 43
metric                                     hum mean  AI mean  AI/hum  AI>  AI<  tie      p  verdict
---------------------------------------------------------------------------------------------------
R1 Not-X-but-Y reframe                        0.099    0.275    2.78   10    2   31  0.039  AI higher
R2 Announcement colon                          0.02      0.0    0.00    0    1   42  1.000  too rare
R3 Throat-clearing phrase                       0.0      0.0    1.00    0    0   43  1.000  too rare
R4 Paragraph-opening signpost                 0.061      0.0    0.00    0    3   40  0.250  too rare
R5 Chatbot residue                            0.084    0.046    0.55    2    3   38  1.000  too rare
R6 Inflated vocabulary                        0.296    0.107    0.36    4   11   28  0.118  no diff
R7 Trailing -ing clause                         0.0      0.0    1.00    0    0   43  1.000  too rare
R8 Significance inflation                       0.0      0.0    1.00    0    0   43  1.000  too rare
R9 Stacked triad                              1.384    1.564    1.13   22   17    4  0.522  no diff
R10 Hedge stacking                              0.0    0.022     inf    1    0   42  1.000  too rare
R11 Personified tool / grand metaphor           0.0      0.0    1.00    0    0   43  1.000  too rare
X1 Numbered headings (do not touch)            0.02    0.628   31.40    3    1   39  0.625  too rare
X2 'This means' restatement (do not touch)    0.169    0.211    1.25    6    5   32  1.000  no diff
X3 Passive voice (do not touch)               4.247    2.767    0.65   13   30    0  0.014  AI lower
X4 Questions in prose (do not touch)          3.744    2.599    0.69   14   25    4  0.108  no diff
F Em dash                                     2.623    0.065    0.02    1   31   11  0.000  AI lower
F Semicolon                                   0.586    0.682    1.16   15   12   16  0.701  no diff
F Bold in prose                                 0.0    0.592     inf    7    0   36  0.016  AI higher
F Emoji                                       0.117      0.0    0.00    0    3   40  0.250  too rare
C sentence_len_cv                             0.592    0.553    0.93   14   29    0  0.032  AI lower
C section_len_cv                              0.626    0.376    0.60    2   11    0  0.022  AI lower
C headings_per_1k                             1.612    6.822    4.23   43    0    0  0.000  AI higher
C list_line_share                             0.147    0.102    0.69    6   17   20  0.035  AI lower
C iso2_per_100p                               2.313    4.724    2.04   20   10   13  0.099  no diff
C iso3_per_100p                                 0.0    0.303     inf    2    0   41  0.500  too rare
C mtld                                       98.023  104.163    1.06   28   15    0  0.066  no diff
C nominalizations_per_1k                     17.412   15.877    0.91   15   26    2  0.117  no diff
```

**Reading it.**
- Strong, consistent: Claude sections its posts far more (headings in all 43 pairs) and makes sections more even. This matches the Chinese study (headings per 1000 characters AI 1.26 vs human 0.32; section CV AI 0.31 vs 0.83).
- Supported: not-X-but-Y reframes (also the Chinese study's strongest signal), bold inside prose.
- Reversed versus folk wisdom: em dashes (humans 40× more here) and passive voice (humans more, matching Reinhart et al.).
- Not supported for Claude: the inflated-vocabulary list, stacked triads.
- Most phrase rules never fired on either side. These essays have almost none of the stock AI phrases, so those rules can't be judged from this data.

**Caveats.** One model; one genre (programmer blogs, mostly 2000–2021); 43 pairs; the human side is pre-2022 writing by skilled professional bloggers, not average writers. The Claude essays were written by agents inside Claude Code, whose system instructions may discourage some habits (the near-total absence of dashes and stock phrases suggests that). Results describe this setup, not "AI writing" in general.

## Known gaps

- Only one model calibrated (Claude). GPT side pending: `calibration/generate.py essays --model gpt` once the Codex CLI is installed.
- The four semantic checks have not been calibrated in English (they need model labelling of both sides).
- Em dash: popular claim, no controlled English measurement included here; treated as a per-writer fingerprint.
- Sanity check done at build time: three 19th-century human texts from Project Gutenberg (~76k words) gave R6 inflated vocabulary at 0.1–0.6 per 1000 words, against 54 per 1000 in a deliberately AI-styled sample, and near-zero A-grade hits. That is a false-positive check, not a calibration: old prose is a poor match for modern blogs.

## How to calibrate (recommended)

1. Collect 30+ human pieces in your genre (your own writing before 2022 is ideal).
2. For each, have one or more models write a piece on the **same topic with the same facts** (give it the outline and facts, not the text). Save with the **same file name** in an `ai/` folder.
3. Run `python3 scripts/calibrate.py --human human/ --ai ai/ --paired --write`.
4. R/F rules marked "AI lower" go to the X list in SKILL.md; "no diff" rules get lower priority; "AI higher" rules get the [calibrated] tag. `detect.py` will show your medians automatically.
