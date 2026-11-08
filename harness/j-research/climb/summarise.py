#!/usr/bin/env python3
"""climb/summarise.py TAG VARIANT... : per-case mean score, binary pass rate and grader detail for a screen or confirm run."""
import glob, json, sys
from collections import defaultdict
tag, variants = sys.argv[1], sys.argv[2:]
rows = defaultdict(dict); cost = 0.0
for v in variants:
    for f in glob.glob(f"results/climb-{tag}-{v}-*.json"):
        m = f.split(f"climb-{tag}-{v}-")[1].split("-", 1)[0]
        for c in json.load(open(f))["cases"]:
            rs = c["arms"]["with"]
            cost += sum(r["costUsd"] + r.get("judgeCostUsd", 0) for r in rs)
            ans = [next((g["passed"] for g in r.get("graders", []) if g["name"] == "answer"), False) for r in rs]
            fails = sorted({g["name"] for r in rs for g in r.get("graders", []) if not g["passed"]})
            rows[(c["name"], m)][v] = (sum(r["score"] for r in rs) / len(rs), sum(ans), len(rs), fails)
for (case, m), d in sorted(rows.items()):
    print(f"{case[:28]:28} {m:6} " + "  ".join(f"{v}: {d[v][0]:.2f} pass {d[v][1]}/{d[v][2]} fails {d[v][3]}" for v in variants if v in d))
print(f"cost ${cost:.2f}")
