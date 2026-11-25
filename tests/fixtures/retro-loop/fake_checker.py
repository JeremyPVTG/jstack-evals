#!/usr/bin/env python3
"""Stands in for an eval author's checker in the run driver tests: checker.py CASE RESULTS.

Passes each run the harness passed whose trace file exists, and prints one entry per run.
"""
import json
from pathlib import Path
import sys

case, results = sys.argv[1], json.loads(Path(sys.argv[2]).read_text())
runs = next(c for c in results['cases'] if c['name'] == case)['arms']['with']
checks = []
for run in runs:
    trace = Path(run.get('tracePath') or '/nonexistent')
    checks.append({'pass': bool(run['passed']) and trace.is_file(), 'critical': False,
                   'note': 'trace read' if trace.is_file() else 'no trace'})
print(json.dumps({case: checks}))
