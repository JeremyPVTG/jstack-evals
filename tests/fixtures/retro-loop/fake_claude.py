#!/usr/bin/env python3
"""Stands in for `claude plugin eval` in the run driver tests. It calls no model.

It writes a results file shaped like `claude plugin eval --json` for the one case its target
prompt.md names. A run passes when the case name starts with "control", or when the plugin's
SKILL.md contains FIXED. Each run costs $0.50, and a run starts only while the cost so far is
below --max-cost-usd, as the real ceiling does (exit 2 and partial when runs are left).

Environment: FAKE_CLAUDE_LOG gets one JSON line per call (its argv); FAKE_CLAUDE_TRACES is
where trace files go; FAKE_CLAUDE_MODE=nojson exits 1 without a results file.
"""
import json
import math
import os
from pathlib import Path
import sys
import uuid

COST = 0.5

argv = sys.argv[1:]
if os.environ.get('FAKE_CLAUDE_LOG'):
    with open(os.environ['FAKE_CLAUDE_LOG'], 'a') as log:
        log.write(json.dumps(argv) + '\n')
if argv[:2] != ['plugin', 'eval']:
    sys.exit(f'fake claude: expected plugin eval, got {argv[:2]}')
if os.environ.get('FAKE_CLAUDE_MODE') == 'nojson':
    sys.exit(1)


def value(flag):
    return argv[argv.index(flag) + 1]


target = Path(argv[2])
case, plugin = target.parent.name, target.parents[2]
skill = next((plugin / 'skills').glob('*/SKILL.md')).read_text()
passed = case.startswith('control') or 'FIXED' in skill
planned = int(value('--runs'))
started = min(planned, math.ceil(float(value('--max-cost-usd')) / COST))
traces = Path(os.environ.get('FAKE_CLAUDE_TRACES', '/nonexistent'))
runs = []
for _ in range(started):
    trace = traces / uuid.uuid4().hex / 'trace.jsonl'
    trace.parent.mkdir(parents=True)
    trace.write_text(json.dumps({'type': 'assistant', 'message': {'role': 'assistant', 'content': [
        {'type': 'text', 'text': f'{case}: ' + ('blocked, stale review' if passed else 'complete')}]}}) + '\n')
    runs.append({'score': 1 if passed else 0, 'passed': passed, 'turns': 3, 'costUsd': COST, 'judgeCostUsd': 0,
                 'durationSeconds': 1, 'error': None, 'tracePath': str(trace), 'skippedPaidGraders': False,
                 'graders': [{'name': 'status', 'passed': passed, 'weight': 1}]})
result = {'schemaVersion': 1, 'claudeVersion': 'fake', 'costUsd': COST * started, 'durationSeconds': 1,
          'partial': started < planned, 'suite': {'root': str(plugin), 'modelOverride': value('--model')},
          'cases': [{'name': case, 'arms': {'with': runs}, 'aggregates': {}}], 'aggregates': {}}
Path(value('--json')).write_text(json.dumps(result))
sys.exit(2 if started < planned else 0)
