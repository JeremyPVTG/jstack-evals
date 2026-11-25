#!/usr/bin/env python3
"""Retro loop experiment record: copy one decided reproduce or gate run into the public record.

Usage:
  record.py RUN_DIR --cases CASES_DIR --ledger LEDGER.json [--holdout HOLDOUT_DIR] [--out RECORDS]

RUN_DIR is a run directory the run driver wrote (manifest.json and decision.json). CASES_DIR holds
the frozen target and controls plus the eval author's top-level files (checker.py, cases.json,
FROZEN.md). LEDGER.json is `retro_loop.py ledger --finding N` for this finding. A gate record needs
HOLDOUT_DIR, the soft holdout, which joins the record only after its gate: a reproduce record
refuses it. RECORDS defaults to harness/retro-loop/records in this checkout.

Layout under RECORDS/<finding>/:

  cases/<freeze>/      the frozen target and controls, and the eval author's top-level files
  holdout/<freeze>/    the soft holdout, added by a gate record
  runs/<run>/          manifest.json (paths made relative to the record), decision.json,
                       ledger.json (the extract at this step), results/*.json, checker/*.json,
                       skill-incumbent.md and, for a gate, skill-candidate.md

<freeze> is the first 12 hex digits of the sha256 of the manifest's frozen cases (canonical JSON),
so each freeze of a finding has its own folder. A second attempt's record also copies the
incumbent runs it reused, without their ledger extract. Plugins, logs, traces and the judge
bundle stay in the run directory. The home directory is written as ~ in copied results, checker
output and the ledger extract; case files are copied byte for byte, as they are now, since their
hashes are checked.

Records are append-only: a file already in the record must have the same bytes, so recording a
run again changes nothing, and two record pull requests that copy the same run merge cleanly.
Before anything is written, gate.py decides every copied manifest and must give the recorded
decision again. That catches cases edited since the run, and still records a step the gate
rejected because a frozen case had changed or gone missing.

Prints one JSON report. Exits 0 when the record is written and rechecked, and 1 on an error.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate  # noqa: E402

RECORDS = HERE / 'records'


class RecordError(Exception):
    pass


def load(path, what):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as error:
        raise RecordError(f'cannot read {what} {path}: {error}')


def dumps(data):
    return json.dumps(data, indent=2) + '\n'


def redact(text):
    home = str(Path.home())
    return text.replace(home, '~') if home not in ('', '/') else text


def freeze_id(cases):
    return hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest()[:12]


class Record:
    """Files to add, as {path under the finding's record: bytes}, gathered before anything is written."""

    def __init__(self, cases_dir, holdout_dir, ledger):
        self.cases_dir = cases_dir
        self.holdout_dir = holdout_dir
        self.ledger = ledger
        self.files = {}
        self.freezes = set()
        self.runs = []

    def add(self, rel, data):
        if isinstance(data, str):
            data = data.encode()
        if self.files.get(rel, data) != data:
            raise RecordError(f'{rel} would be written twice with different bytes')
        self.files[rel] = data

    def add_case(self, case, source, dest):
        """Copy a case as it is now. A case missing or changed since freezing is the recheck's to judge."""
        for root, dirs, names in os.walk(source / case['name']):
            dirs[:] = sorted(d for d in dirs if d not in gate.SKIPPED_DIRS)
            for name in names:
                path = Path(root) / name
                if path.is_file() and not path.is_symlink():
                    self.add(f"{dest}/{path.relative_to(source).as_posix()}", path.read_bytes())

    def add_cases(self, cases, freeze, with_holdout):
        if freeze in self.freezes:
            return
        self.freezes.add(freeze)
        for case in [cases['target']] + list(cases.get('controls', [])):
            self.add_case(case, self.cases_dir, f'cases/{freeze}')
        for path in sorted(self.cases_dir.iterdir()):
            if path.is_file() and not path.is_symlink():
                self.add(f'cases/{freeze}/{path.name}', path.read_bytes())
        if with_holdout:
            self.add_case(cases['holdout'], self.holdout_dir, f'holdout/{freeze}')

    def add_run(self, run_dir, finding, ledger=True, seen=()):
        """The run's files; then, for a reused incumbent, the earlier run's. Returns the run name."""
        manifest = load(run_dir / 'manifest.json', 'manifest')
        decision = load(run_dir / 'decision.json', 'decision')
        if not isinstance(manifest, dict) or manifest.get('finding') != finding:
            raise RecordError(f'{run_dir} is not a run for finding #{finding}')
        mode, cases = manifest.get('mode'), manifest.get('cases')
        if mode not in ('reproduce', 'gate') or not isinstance(cases, dict):
            raise RecordError(f'{run_dir}/manifest.json is not a run driver manifest')
        if mode == 'gate' and self.holdout_dir is None:
            raise RecordError('a gate record needs --holdout: the soft holdout joins the record after its gate')
        freeze = freeze_id(cases)
        self.add_cases(cases, freeze, mode == 'gate')
        name = run_dir.name
        out = f'runs/{name}'
        copy = dict(manifest)
        copy['case_dir'] = f'../../cases/{freeze}'
        copy['holdout_dir'] = f'../../holdout/{freeze}' if mode == 'gate' else None
        copy['skill_md'] = {}
        for condition in ('incumbent', 'candidate'):
            source = (manifest.get('skill_md') or {}).get(condition)
            copy['skill_md'][condition] = f'skill-{condition}.md' if source else None
            if source:
                self.add(f'{out}/skill-{condition}.md', (run_dir / source).read_bytes())
        checker = manifest.get('checker')
        if isinstance(checker, dict) and checker.get('path'):
            given = Path(checker['path'])
            inside = given.parent.resolve() == self.cases_dir
            copy['checker'] = dict(checker, path=f'../../cases/{freeze}/{given.name}' if inside else given.name)
        for entry in manifest.get('results') or []:
            for key in ('path', 'checker'):
                if entry.get(key):
                    rel = Path(entry[key])
                    if rel.is_absolute() or '..' in rel.parts:
                        raise RecordError(f'{run_dir}: result file {rel} is outside the run directory')
                    self.add(f'{out}/{rel.as_posix()}', redact((run_dir / rel).read_text()))
        if manifest.get('reuse_incumbent_from'):
            earlier = Path(manifest['reuse_incumbent_from'])
            earlier = (earlier if earlier.is_absolute() else run_dir / earlier).resolve().parent
            if earlier in seen:
                raise RecordError(f'{run_dir} reuses incumbent runs in a loop')
            copy['reuse_incumbent_from'] = f'../{earlier.name}/manifest.json'
        self.add(f'{out}/manifest.json', dumps(copy))
        self.add(f'{out}/decision.json', dumps(decision))
        if ledger:
            self.add(f'{out}/ledger.json', redact(dumps(self.ledger)))
        self.runs.append((name, mode, decision.get('outcome')))
        if manifest.get('reuse_incumbent_from'):
            self.add_run(earlier, finding, ledger=False, seen=(*seen, run_dir.resolve()))
        return freeze


def recheck(staged, runs):
    """Decide every staged manifest that holds what it needs; each must give its recorded decision again."""
    rechecked = []
    for name, mode, _ in runs:
        manifest = staged / 'runs' / name / 'manifest.json'
        decision = gate.decide(manifest)
        recorded = json.loads((manifest.parent / 'decision.json').read_text())
        if decision != recorded:
            raise RecordError(f'gate.py decides the copied {name} as {decision["outcome"]}, not as recorded '
                              f'({recorded.get("outcome")}): {" ".join(decision["reasons"])}')
        rechecked.append({'run': name, 'outcome': decision['outcome']})
    return rechecked


def write(record, dest):
    """Check the staged files against the record, recheck them in a scratch copy, then add the new ones."""
    clashes = sorted(rel for rel, data in record.files.items()
                     if (dest / rel).exists() and (dest / rel).read_bytes() != data)
    if clashes:
        raise RecordError('records are append-only, and these files already hold other bytes: ' + ', '.join(clashes))
    with tempfile.TemporaryDirectory() as scratch:
        staged = Path(scratch) / 'record'
        if dest.is_dir():
            shutil.copytree(dest, staged)
        for rel, data in record.files.items():
            (staged / rel).parent.mkdir(parents=True, exist_ok=True)
            (staged / rel).write_bytes(data)
        rechecked = recheck(staged, record.runs)
    added = 0
    for rel, data in sorted(record.files.items()):
        path = dest / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            added += 1
    return rechecked, added


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('run_dir', help='the run directory that holds manifest.json and decision.json')
    p.add_argument('--cases', required=True, help='the frozen target and controls, with checker.py and FROZEN.md')
    p.add_argument('--ledger', required=True, help='retro_loop.py ledger --finding N output')
    p.add_argument('--holdout', help='the soft holdout directory; required for a gate record, refused for reproduce')
    p.add_argument('--out', default=str(RECORDS), help=f'records root (default: {RECORDS})')
    args = p.parse_args(argv)
    report = {'record': None, 'freeze': None, 'runs': [], 'added': 0, 'rechecked': [], 'error': None}
    try:
        run_dir = Path(args.run_dir).expanduser().resolve()
        manifest = load(run_dir / 'manifest.json', 'manifest')
        finding = manifest.get('finding') if isinstance(manifest, dict) else None
        if not isinstance(finding, int) or isinstance(finding, bool):
            raise RecordError(f'{run_dir}/manifest.json names no finding')
        if args.holdout and manifest.get('mode') != 'gate':
            raise RecordError('the soft holdout joins the record only after its gate, not in a reproduce record')
        ledger = load(args.ledger, 'ledger extract')
        if not (isinstance(ledger, list) and all(isinstance(e, dict) and e.get('finding') == finding for e in ledger)):
            raise RecordError(f'the ledger extract must be the entries for #{finding} only')
        cases_dir = Path(args.cases).expanduser().resolve()
        holdout_dir = Path(args.holdout).expanduser().resolve() if args.holdout else None
        for path, flag in ((cases_dir, '--cases'), (holdout_dir, '--holdout')):
            if path is not None and not path.is_dir():
                raise RecordError(f'{flag} {path} is not a directory')
        record = Record(cases_dir, holdout_dir, ledger)
        report['freeze'] = record.add_run(run_dir, finding)
        dest = Path(args.out).expanduser().resolve() / str(finding)
        report['record'] = str(dest)
        report['runs'] = [name for name, _, _ in record.runs]
        report['rechecked'], report['added'] = write(record, dest)
        code = 0
    except (RecordError, gate.ManifestError, OSError, ValueError) as error:
        report['error'], code = str(error), 1
    print(json.dumps(report, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
