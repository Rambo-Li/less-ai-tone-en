#!/usr/bin/env python3
"""Build the AI side of a paired calibration corpus.

Step 1 (outlines): for each human essay, ask a model for a neutral outline + fact list,
    so the AI writer gets the same topic and facts but never sees the human wording.
        python generate.py outlines
Step 2 (essays): write one essay per outline with a given model, same file names as human/.
        python generate.py essays --model claude      -> ai-claude/
        python generate.py essays --model gpt         -> ai-gpt/     (needs the `codex` CLI)

Existing outputs are skipped, so the script can be re-run after a failure.
Paths are relative to this folder.
"""
import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent

OUTLINE_PROMPT = """Below is a blog essay. Write a brief for another writer who will write a NEW essay on the same topic.

Output, in Markdown:
1. Working title (your own words, not the original title).
2. Audience and purpose, one line.
3. Outline: the sections in order, each with its main claim stated in your own words.
4. Facts: every concrete fact, example, anecdote, name, number and date the essay relies on, as terse bullet points.

Do NOT quote or closely paraphrase sentences. Do NOT describe the author's style, tone or voice. Output only the brief.

ESSAY:
"""

ESSAY_PROMPT = """Write a blog post of about {words} words based on the brief below. Write it in the first person as the blog's author. Use Markdown. Output only the post.

BRIEF:
"""


def words(t):
    return len(re.findall(r"[A-Za-z]+", t))


def run(cmd, prompt, timeout=900):
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError((r.stderr or r.stdout)[-400:])
    return r.stdout.strip()


def model_cmd(model, out_file):
    if model == "claude":
        return ["claude", "-p", "--output-format", "text", "--max-turns", "1", "--tools", ""], None
    if model == "gpt":
        return ["codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only", "-o", str(out_file), "-"], out_file
    raise SystemExit(f"unknown model {model}")


def call(model, prompt, out_file):
    cmd, last = model_cmd(model, out_file)
    text = run(cmd, prompt)
    if last:  # codex writes its final message to -o; stdout carries logs
        text = Path(last).read_text(encoding="utf-8").strip()
    return re.sub(r"^```(?:markdown|md)?\s*\n|\n```\s*$", "", text)


def outlines(a):
    src, dst = HERE / "human", HERE / "outlines"
    dst.mkdir(exist_ok=True)
    jobs = [f for f in sorted(src.glob("*.md")) if not (dst / f.name).exists()]

    def one(f):
        body = re.sub(r"<!--.*?-->", "", f.read_text(encoding="utf-8"), flags=re.S).strip()
        try:
            brief = call(a.outline_model, OUTLINE_PROMPT + body, dst / f.name)
            (dst / f.name).write_text(f"<!-- words: {words(body)} -->\n\n{brief}\n", encoding="utf-8")
            return f"OK   {f.name}"
        except Exception as e:
            return f"FAIL {f.name}: {e}"

    with ThreadPoolExecutor(a.jobs) as ex:
        for line in ex.map(one, jobs):
            print(line, flush=True)


def essays(a):
    src, dst = HERE / "outlines", HERE / f"ai-{a.model}"
    dst.mkdir(exist_ok=True)
    jobs = [f for f in sorted(src.glob("*.md")) if not (dst / f.name).exists()]

    def one(f):
        t = f.read_text(encoding="utf-8")
        n = int(re.search(r"words: (\d+)", t).group(1))
        brief = re.sub(r"<!--.*?-->", "", t, flags=re.S).strip()
        try:
            text = call(a.model, ESSAY_PROMPT.format(words=round(n, -1)) + brief, dst / (f.stem + ".last.txt"))
            (dst / f.name).write_text(text + "\n", encoding="utf-8")
            (dst / (f.stem + ".last.txt")).unlink(missing_ok=True)
            return f"OK   {words(text):5} words (target {n})  {f.name}"
        except Exception as e:
            return f"FAIL {f.name}: {e}"

    with ThreadPoolExecutor(a.jobs) as ex:
        for line in ex.map(one, jobs):
            print(line, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["outlines", "essays"])
    ap.add_argument("--model", default="claude", choices=["claude", "gpt"])
    ap.add_argument("--outline-model", default="claude", choices=["claude", "gpt"])
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    outlines(a) if a.step == "outlines" else essays(a)


if __name__ == "__main__":
    main()
