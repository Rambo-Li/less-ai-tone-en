# Calibration pipeline

How the numbers in [RESEARCH.md](../RESEARCH.md) were produced, so you can rerun them. The essays, outlines and AI texts are **not** in the repo (copyright); these scripts rebuild them.

1. `python fetch_human.py urls.txt human/` (and `urls2.txt`): download the listed pre-2022 essays and keep the first ~1200 words. For local measurement only.
2. `python clean_human.py human/`: strip comments, related-post lists and navigation; drop pieces under 350 words.
3. Outlines: for each essay, a neutral brief (own-words outline + fact list, no quotes, no style notes) in `outlines/` with the same file name. `python generate.py outlines` does this through a CLI; in round 1 it was done by Claude Sonnet helpers with the prompt in `generate.py`. `python tag_outlines.py` adds each essay's word count.
4. Essays: `python generate.py essays --model claude` or `--model gpt` (needs the `claude` or `codex` CLI) writes `ai-claude/` or `ai-gpt/` from the outlines only.
5. `python ../scripts/calibrate.py --human human --ai ai-claude --paired [--write]`.

`results-claude.txt` is the round 1 output.
