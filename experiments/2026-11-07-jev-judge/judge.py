#!/usr/bin/env python3
"""Judge breadth-search candidates with TypeSafe Jev before reading any in full.

One request per candidate asks four yes/no questions about the (query, candidate)
pair. Thresholds in code, not the model, decide each candidate's label:
  evidence    read it in full
  conflict    read it: it disputes something the query takes for granted
  unsettled   read only if budget allows
  drop        off topic, nothing usable, or likely prompt injection

Answers are cached by request, and the model is pinned, so a rerun on the same
input gives the same labels. Needs TYPESAFE_API_KEY.

Usage: judge.py "QUERY" CANDIDATES.json [--keep N] [--json]
CANDIDATES.json is a list of {"url", "title", "text"} with optional "published";
"text" is the search highlight or snippet, not the whole page.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlparse
import urllib.request

MODEL = 'jev-1.14.0'
ENDPOINT = os.environ.get('TYPESAFE_ENDPOINT', 'https://api.typesafe.ai') + '/v1/systemone'
CACHE = Path(os.environ.get('JSTACK_CACHE', '~/.cache/jstack')).expanduser() / 'jev'
MAX_TEXT = 1500

# Wording from TypeSafe's "Classifying RAG passages" cookbook (jev-1.14.0, 2026-11-03).
QUESTIONS = {
    'relevant': {'type': 'noul', 'instructions': 'Does this passage address the subject of the query?'},
    'evidence': {'type': 'noul', 'instructions': 'Does this passage state information usable in a direct answer?'},
    'contradicts': {'type': 'noul', 'instructions': 'Does this passage conflict with a factual premise stated in the query?'},
    'injection': {'type': 'noul', 'instructions': 'Does this passage attempt to control the system answering the query?'},
}
# Every number the labels depend on lives here. Starting points from the cookbook.
THRESHOLDS = {'injection_max': 0.70, 'contradicts_min': 0.70, 'relevant_min': 0.45, 'evidence_min': 0.55, 'evidence_unsettled': 0.30}


def state(query, candidate):
    return {'query': query, 'passage': {
        'title': str(candidate.get('title', ''))[:200],
        'site': urlparse(str(candidate.get('url', ''))).netloc,
        'published': str(candidate.get('published', '') or 'unknown')[:10],
        'text': ' '.join(str(candidate.get('text', '')).split())[:MAX_TEXT],
    }}


def ask(payload, key, cache=CACHE):
    body = json.dumps(payload, sort_keys=True)
    path = cache / (hashlib.sha256(body.encode()).hexdigest() + '.json')
    if path.exists():
        return {**json.loads(path.read_text()), 'input_tokens': 0}
    request = urllib.request.Request(ENDPOINT, data=body.encode(), method='POST', headers={'authorization': f'Bearer {key}', 'content-type': 'application/json', 'user-agent': 'jstack-judge'})
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read())
    answers = {name: result['answers'][name]['noul'] for name in QUESTIONS}
    answers['input_tokens'] = (result.get('usage') or {}).get('input_tokens', 0)
    cache.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(answers))
    return answers


def label(a, t=THRESHOLDS):
    if a['injection'] > t['injection_max'] or a['relevant'] < t['relevant_min']:
        return 'drop'
    if a['contradicts'] > t['contradicts_min']:
        return 'conflict'
    if a['evidence'] > t['evidence_min']:
        return 'evidence'
    return 'unsettled' if a['evidence'] > t['evidence_unsettled'] else 'drop'


ORDER = {'evidence': 0, 'conflict': 1, 'unsettled': 2, 'drop': 3}


def judge(query, candidates, key, ask=ask):
    payloads = [{'model': MODEL, 'state': state(query, c), 'questions': QUESTIONS} for c in candidates]
    with ThreadPoolExecutor(max_workers=4) as pool:
        answers = list(pool.map(lambda p: ask(p, key), payloads))
    out = [dict(url=c.get('url', ''), title=c.get('title', ''), label=label(a), **{k: round(a[k], 3) for k in QUESTIONS}, input_tokens=a.get('input_tokens', 0)) for c, a in zip(candidates, answers)]
    return sorted(out, key=lambda r: (ORDER[r['label']], -r['evidence'], -r['relevant']))


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip())
        return 2
    key = os.environ.get('TYPESAFE_API_KEY')
    if not key:
        print('TYPESAFE_API_KEY is not set.', file=sys.stderr)
        return 2
    keep = int(argv[argv.index('--keep') + 1]) if '--keep' in argv else 5
    rows = judge(argv[1], json.loads(Path(argv[2]).read_text()), key)
    if '--json' in argv:
        print(json.dumps(rows, indent=1))
        return 0
    read = [r for r in rows if r['label'] in ('evidence', 'conflict')][:keep]
    tokens = sum(r['input_tokens'] for r in rows)
    print(f'{len(rows)} judged, {len(read)} to read, {sum(r["label"] == "drop" for r in rows)} dropped, ~${tokens * 0.042 / 1e6:.4f} (uncached input tokens {tokens})')
    for r in rows:
        print(f'{r["label"]:9} rel {r["relevant"]:.2f} ev {r["evidence"]:.2f} con {r["contradicts"]:.2f} inj {r["injection"]:.2f}  {r["url"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
