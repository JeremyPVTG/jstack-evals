#!/usr/bin/env python3
"""Measure how often j-research fires for a candidate description.
Usage: trigger_test.py LABEL DESCRIPTION_FILE  (runs build/with-skill trigger-evals, 2 runs each)"""
import json, os, re, subprocess, sys
from pathlib import Path
label, desc_file = sys.argv[1], sys.argv[2]
skill = Path('build/with-skill/skills/j-research/SKILL.md')
desc = Path(desc_file).read_text().strip().replace('\n', ' ')
text = skill.read_text()
skill.write_text(re.sub(r'^description: .*$', 'description: ' + desc, text, count=1, flags=re.M))
out = Path(f'results/trigger-{label}.json')
env = {k: v for k, v in os.environ.items() if k != 'CLAUDE_CONFIG_DIR'}
subprocess.run(['claude', 'plugin', 'eval', 'build/with-skill', '--eval-dir', os.environ.get('EVAL_DIR', 'trigger-evals'), '--ablation', 'none', '--runs', '2', '-j', '8', '--model', 'sonnet', '--max-cost-usd', '2', '--threshold', '0', '--trust-plugin', '--no-publish', '--json', str(out)], env=env, capture_output=True)
d = json.loads(out.read_text())
hits = misses = fp = tn = 0; cost = 0.0
for c in d['cases']:
    should = not c['name'].startswith(('notrigger', 'n-'))
    for r in c['arms']['with']:
        cost += r['costUsd'] + r.get('judgeCostUsd', 0)
        fired = r['score'] == 1 if should else r['score'] != 1
        if should: hits += fired; misses += not fired
        else: fp += fired; tn += not fired
print(f'{label}: fired on {hits}/{hits+misses} should-trigger runs, false triggers {fp}/{fp+tn}, cost ${cost:.2f}, desc {len(desc)} chars')
