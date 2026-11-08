#!/usr/bin/env python3
"""Compare two classifiers for a UserPromptSubmit hook that reminds the agent to use j-research.

The hook should fire when a good answer depends on facts that change (versions,
prices, limits, which tools exist, whether a claim holds) or when the user asks
how to build, set up or choose something. It should stay quiet on edits,
writing and explanations of material the user supplies.

- Jev (TypeSafe jev-1.14.0): four yes/no judgements about the message; code decides.
- Haiku (claude-haiku-5-5): one direct yes/no question.

Labelled prompts come from the harness trigger sets and held-out set 1, plus
NEGATIVES below (written before any run). Held-out set 2 is not used.
Needs TYPESAFE_API_KEY and ANTHROPIC_API_KEY. Writes results.json.
"""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import time
import urllib.request

HARNESS = Path(__file__).resolve().parents[2] / "harness" / "j-research" / "source"
SETS = ["trigger-evals", "heldout-evals", "trigger-evals-2", "heldout-cases"]
NEGATIVE_PREFIXES = ("notrigger", "n-", "n2-")
NEGATIVES = [
    "Fix the failing test in src/auth/session.test.ts",
    "Rename getUser to fetchUser everywhere in this repo",
    "Write a commit message for the staged changes",
    "Summarise this thread for me",
    "Why am I getting: Type 'string | undefined' is not assignable to type 'string'?",
    "Add a loading spinner to the dashboard page",
    "Make the button on the landing page use the brand colour",
    "Turn these notes into a short email to the team: launch moved to Friday, demo at 3pm",
    "What does this function do? def f(xs): return sorted(set(xs))[-2]",
    "Run the tests and tell me what fails",
]

JEV_MODEL = "jev-1.14.0"
JEV_URL = "https://api.typesafe.ai/v1/systemone"
QUESTIONS = {
    "changing_facts": {"type": "noul", "instructions": "Would a good answer to `message` rely on current facts about products or services outside the person's own project?",
        "criteria": {"true": "The answer depends on current versions, prices, limits, recent releases, or which outside products and services exist.",
                     "false": "The answer depends only on the person's own code, files, tests or text, or on stable knowledge, such as how a language feature works."}},
    "build_or_choose": {"type": "noul", "instructions": "Does `message` ask how to build, set up, or choose a tool, service, or approach?",
        "criteria": {"true": "The person wants a recommendation on how to build or set something up, or which option to pick.",
                     "false": "The person wants existing code or text changed, written, run, or explained."}},
    "reliance": {"type": "noul", "instructions": "Does `message` ask whether a claim, product, or release can be relied on?",
        "criteria": {"true": "The person asks if something is safe, ready, true, or dependable before acting on it.",
                     "false": "The person does not ask whether anything can be trusted."}},
    "self_contained": {"type": "noul", "instructions": "Can `message` be answered fully from the message itself and the person's own files?",
        "criteria": {"true": "Everything needed is in the message or the project, such as fixing a given error or rewriting given text.",
                     "false": "Answering well needs information from outside sources."}},
}
YES, NO = 0.70, 0.30  # Noul thresholds; the band between counts as unsettled


def jev_decide(a):
    """Truth table: a clear research signal fires. An unsettled signal (between NO and YES)
    fires only when the task is not clearly self-contained. No signal does not fire."""
    signal = max(a["changing_facts"], a["build_or_choose"], a["reliance"])
    if signal > YES:
        return True
    if signal > NO:
        return a["self_contained"] < YES
    return False


HAIKU_MODEL = "claude-haiku-5-5"
HAIKU_PROMPT = """Classify the user's message for a coding agent. Answer YES if a good answer depends on facts that change over time (versions, prices, limits, recent releases, which tools or services exist, whether a claim or product can be relied on) or if the user asks how to build, set up or choose something. Answer NO if the task is to change, write, run or explain code or text the user supplies, or it needs only stable knowledge. Reply with exactly YES or NO.

Message:
{message}"""


def post(url, payload, headers):
    request = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST", headers={"content-type": "application/json", **headers})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read())
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def jev(message):
    start = time.time()
    result = post(JEV_URL, {"model": JEV_MODEL, "state": {"message": message}, "questions": QUESTIONS},
                  {"authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}", "user-agent": "jstack-trigger"})
    answers = {name: result["answers"][name]["noul"] for name in QUESTIONS}
    return {"fire": jev_decide(answers), "answers": answers, "ms": int((time.time() - start) * 1000),
            "input_tokens": (result.get("usage") or {}).get("input_tokens", 0)}


def haiku(message):
    start = time.time()
    result = post("https://api.anthropic.com/v1/messages",
                  {"model": HAIKU_MODEL, "max_tokens": 5, "messages": [{"role": "user", "content": HAIKU_PROMPT.format(message=message)}]},
                  {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"})
    text = "".join(block.get("text", "") for block in result["content"]).strip().upper()
    return {"fire": text.startswith("YES"), "raw": text, "ms": int((time.time() - start) * 1000), "usage": result.get("usage")}


def prompts():
    items = []
    for name in SETS:
        for case in sorted((HARNESS / name).glob("*/prompt.md")):
            body = case.read_text().split("---", 2)[2].strip()
            items.append({"set": name, "case": case.parent.name, "message": body, "should": not case.parent.name.startswith(NEGATIVE_PREFIXES)})
    items += [{"set": "negatives", "case": f"neg-{i}", "message": m, "should": False} for i, m in enumerate(NEGATIVES)]
    seen, unique = set(), []
    for item in items:  # several sets share prompts; score each message once
        if item["message"] not in seen:
            seen.add(item["message"]); unique.append(item)
    return unique


def main():
    import sys
    if "--validation" in sys.argv:  # fresh prompts, written before the revised run
        items = [{"set": "validation", "case": f"val-{i}", **v} for i, v in enumerate(json.loads(Path(__file__).with_name("validation.json").read_text()))]
        out = "results-validation.json"
    else:
        items, out = prompts(), "results.json"
    with ThreadPoolExecutor(8) as pool:
        jevs = list(pool.map(lambda it: jev(it["message"]), items))
        haikus = list(pool.map(lambda it: haiku(it["message"]), items))
    rows = [{**it, "jev": j, "haiku": h} for it, j, h in zip(items, jevs, haikus)]
    Path(__file__).with_name(out).write_text(json.dumps(rows, indent=1))
    for clf in ("jev", "haiku"):
        tp = sum(r[clf]["fire"] and r["should"] for r in rows); fn = sum(not r[clf]["fire"] and r["should"] for r in rows)
        fp = sum(r[clf]["fire"] and not r["should"] for r in rows); tn = sum(not r[clf]["fire"] and not r["should"] for r in rows)
        ms = sorted(r[clf]["ms"] for r in rows)
        print(f"{clf:6} recall {tp}/{tp + fn}  false fires {fp}/{fp + tn}  median {ms[len(ms) // 2]} ms  p90 {ms[int(len(ms) * 0.9)]} ms")
        for r in rows:
            if r[clf]["fire"] != r["should"]:
                print(f"   {'MISS' if r['should'] else 'FALSE'} {r['case']}: {r['message'][:90]}")


if __name__ == "__main__":
    main()
