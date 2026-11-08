#!/usr/bin/env python3
"""Classify harness rejections (council round 5, option B).

A run rejected with "a result in the trace is not one the harness gave" is a
known infrastructure fault only if some tool result in its trace equals the
mock's recorded output exactly, followed by exactly Claude Code's schema hint
(HINT_PREFIX ...). Such runs are excluded from averages and counted per variant.
Every other rejection follows the protocol's general rule.

The match is frozen: HINT_PREFIX is Claude Code's wording as seen on 2026-11-08.

Usage: rejections.py RESULTS.json... ; or import classify(run) -> "ok" | "hint" | "other".
"""
import json
import os
import sys

REJECTION = "a result in the trace is not one the harness gave"
HINT_PREFIX = "\n\nThis tool's input schema was not in your prompt when you called it. The input schema is: "


def tool_results(trace_path):
    """Text of each tool result in the trace, by tool_use_id."""
    out = {}
    for line in open(trace_path):
        event = json.loads(line)
        if event.get("type") != "user":
            continue
        content = event["message"]["content"]
        for block in content if isinstance(content, list) else []:
            if block.get("type") != "tool_result":
                continue
            body = block.get("content")
            if isinstance(body, list):
                body = "".join(part.get("text", "") for part in body if isinstance(part, dict))
            out[block.get("tool_use_id")] = body or ""
    return out


def classify(run):
    error = run.get("error") or ""
    if not error:
        return "ok"
    if REJECTION not in error:
        return "other"
    trace = run.get("tracePath", "")
    mocks = os.path.join(os.path.dirname(trace), "mock-calls.jsonl")
    if not (os.path.exists(trace) and os.path.exists(mocks)):
        return "other"
    outputs = [json.loads(line).get("output", "") for line in open(mocks)]
    for text in tool_results(trace).values():
        for output in outputs:
            if output and text.startswith(output + HINT_PREFIX):
                return "hint"
    return "other"


if __name__ == "__main__":
    for path in sys.argv[1:]:
        for case in json.load(open(path))["cases"]:
            kinds = [classify(r) for r in case["arms"]["with"]]
            print(f"{os.path.basename(path)} {case['name']}: " + ", ".join(f"{k}={kinds.count(k)}" for k in ("ok", "hint", "other") if kinds.count(k)))
