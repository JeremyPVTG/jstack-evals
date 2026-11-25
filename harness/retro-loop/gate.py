#!/usr/bin/env python3
"""Retro loop gate: decide one gate step for a retro finding from recorded results.

Usage:
  gate.py decide MANIFEST.json   print the decision as one JSON object
  gate.py hash CASE_DIR          print the sha256 of one frozen case

The manifest and output shapes are the retro loop contract (jstack#17, #18).
No model is called: the decision comes from `claude plugin eval --json` result
files and optional checker output named in the manifest.

Gate rules, first match wins (ADR 0005 in jstack):
  a frozen case hash changed                    -> rejected
  infrastructure fault, retry not yet used      -> retry (attempt not used)
  infrastructure fault, retry already used      -> inconclusive
  SKILL.md grew more than 20%                   -> rejected
  any model: a critical failure, or a control drops more than 1 of 3 -> rejected
  per model pass: candidate target 5/5, incumbent target at most 1/5, holdout at least 3/5
  every model passes -> accepted; none -> rejected; some -> inconclusive
Reproduce mode: 3 incumbent target runs per model; 2 or more passes on any
model -> not_reproduced, otherwise reproduced. The hash and infrastructure
rules apply first in both modes.

Frozen case hashes are rechecked under `case_dir`, except the soft holdout,
which is rechecked under `holdout_dir` when the manifest names one. Reproduce
mode rechecks the target and controls only: the holdout is not needed before
its gate runs.
"""
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

TARGET_RUNS, HOLDOUT_RUNS, CONTROL_RUNS, REPRODUCE_RUNS = 5, 5, 3, 3
TASK_FAILURE = re.compile(r'maximum number of turns|timed out|timeout', re.I)
MAX_INCUMBENT_TARGET, MIN_HOLDOUT = 1, 3
MAX_CONTROL_DROP, MAX_GROWTH_PCT = 1, 20
NOT_REPRODUCED_AT = 2  # incumbent target passes out of REPRODUCE_RUNS, on any model
SKIPPED_DIRS = {'results', '__pycache__'}


class ManifestError(ValueError):
    """The manifest or a file it names cannot be read as the contract describes."""


def case_hash(case_dir):
    """Hex sha256 of a case directory, as the contract's "Case hash" section defines.

    Every regular file, sorted by POSIX path relative to the case directory,
    feeds its path, a NUL, its bytes and a NUL. Directories named `results`
    or `__pycache__` are skipped.
    """
    case_dir = Path(case_dir)
    files = []
    for root, dirs, names in os.walk(case_dir):
        dirs[:] = [d for d in dirs if d not in SKIPPED_DIRS]
        for name in names:
            path = Path(root) / name
            if stat.S_ISREG(path.lstat().st_mode):
                files.append((path.relative_to(case_dir).as_posix(), path))
    digest = hashlib.sha256()
    for rel, path in sorted(files):
        digest.update(rel.encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()


def load_json(path, what):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError) as error:
        raise ManifestError(f'cannot read {what} {path}: {error}')


def need(condition, message):
    if not condition:
        raise ManifestError(message)


def validate(m, base):
    """Refuse a manifest the contract does not describe, before anything is decided."""
    need(isinstance(m, dict), 'the manifest must be a JSON object')
    mode = m.get('mode')
    need(mode in ('gate', 'reproduce'), f'mode must be gate or reproduce, not {mode!r}')
    is_gate = mode == 'gate'
    models = m.get('models')
    need(isinstance(models, list) and models and all(isinstance(x, str) for x in models)
         and len(set(models)) == len(models), 'models must be a non-empty list of distinct names')
    need(isinstance(m.get('infra_retry_used', False), bool), 'infra_retry_used must be true or false')
    cases = m.get('cases')
    need(isinstance(cases, dict) and 'target' in cases, 'cases.target is required')
    if is_gate:
        need(cases.get('holdout') and isinstance(cases.get('controls'), list),
             'a gate needs cases.holdout and a cases.controls list')
    named = all_cases(m)
    need(all(isinstance(c, dict) and isinstance(c.get('name'), str) and isinstance(c.get('sha256'), str)
             for c in named), 'each case needs a name and a sha256')
    need(len({c['name'] for c in named}) == len(named), 'case names must be distinct')
    need(isinstance(m.get('case_dir'), str) and (base / m['case_dir']).is_dir(),
         f"case_dir {m.get('case_dir')!r} is not a directory")
    holdout_dir = m.get('holdout_dir')
    need(holdout_dir is None or isinstance(holdout_dir, str), 'holdout_dir must be a path or null')
    if is_gate and holdout_dir is not None:
        need((base / holdout_dir).is_dir(), f'holdout_dir {holdout_dir!r} is not a directory')
    revisions, skill_md = m.get('revisions') or {}, m.get('skill_md') or {}
    need(isinstance(revisions.get('incumbent'), str), 'revisions.incumbent is required')
    if is_gate:
        need(isinstance(revisions.get('candidate'), str), 'a gate needs revisions.candidate')
        for which in ('incumbent', 'candidate'):
            need(isinstance(skill_md.get(which), str) and (base / skill_md[which]).is_file(),
                 f'skill_md.{which} is not a file: {skill_md.get(which)!r}')
        need((base / skill_md['incumbent']).stat().st_size > 0, 'skill_md.incumbent is empty')
    else:
        need(not m.get('reuse_incumbent_from'), 'reproduce mode does not reuse incumbent runs')
    results = m.get('results')
    need(isinstance(results, list), 'results must be a list')
    conditions = ('incumbent', 'candidate') if is_gate else ('incumbent',)
    seen = set()
    for entry in results:
        need(isinstance(entry, dict) and entry.get('condition') in conditions,
             f'each result condition must be one of {", ".join(conditions)} in {mode} mode')
        need(entry.get('model') in models, f"result model {entry.get('model')!r} is not in models")
        need(isinstance(entry.get('path'), str), 'each result needs a path')
        path = (base / entry['path']).resolve()
        need(path not in seen, f"result file {entry['path']} is listed twice")
        seen.add(path)


def collect(entries, base):
    """Runs per (condition, model, case) as (passed, graded, critical, note), plus run count and cost.

    A run passes only if it was graded, the harness passed it and the checker
    (when the entry names one) passes it too. Critical comes from the checker.
    """
    groups, count, cost = {}, 0, 0.0
    for entry in entries:
        result = load_json(base / entry['path'], 'result file')
        checker = load_json(base / entry['checker'], 'checker output') if entry.get('checker') else {}
        need(isinstance(result, dict) and isinstance(result.get('cases'), list),
             f"{entry['path']} has no cases list: not a claude plugin eval --json file")
        for case in result['cases']:
            runs = (case.get('arms') or {}).get('with')
            need(isinstance(runs, list), f"{entry['path']}: case {case.get('name')!r} has no arms.with runs")
            checks = checker.get(case['name'])
            if checks is not None and len(checks) != len(runs):
                raise ManifestError(f"checker {entry['checker']} has {len(checks)} entries for {case['name']}, "
                                    f"the result file has {len(runs)} runs")
            for i, run in enumerate(runs):
                count += 1
                cost += (run.get('costUsd') or 0) + (run.get('judgeCostUsd') or 0)
                # A turn limit or timeout is the task's own failure (PROTOCOL.md), so it counts as graded and failed.
                task_failure = bool(TASK_FAILURE.search(str(run.get('error') or '')))
                graded = task_failure or (not run.get('error') and bool(run.get('graders'))
                                          and not run.get('skippedPaidGraders'))
                check = checks[i] if checks is not None else {'pass': True}
                groups.setdefault((entry['condition'], entry['model'], case['name']), []).append(
                    (bool(run.get('passed')) and graded and bool(check.get('pass')), graded,
                     bool(check.get('critical')), check.get('note', '')))
    return groups, count, cost


def planned(m):
    """(condition, case name, runs) that each model must have for this decision."""
    cases = m['cases']
    if m['mode'] == 'reproduce':
        return [('incumbent', cases['target']['name'], REPRODUCE_RUNS)]
    target, controls = cases['target']['name'], [c['name'] for c in cases['controls']]
    return ([('incumbent', target, TARGET_RUNS)] + [('incumbent', c, CONTROL_RUNS) for c in controls]
            + [('candidate', target, TARGET_RUNS), ('candidate', cases['holdout']['name'], HOLDOUT_RUNS)]
            + [('candidate', c, CONTROL_RUNS) for c in controls])


def tally(groups, condition, model, case, runs):
    got = groups.get((condition, model, case), [])
    need(len(got) <= runs, f'{model} {condition} {case}: {len(got)} runs recorded, {runs} planned')
    return {
        'passes': sum(1 for r in got if r[0]),
        'not_graded': sum(1 for r in got if not r[1]) + runs - len(got),
        'critical': sum(1 for r in got if r[2]),
        'notes': [r[3] for r in got if r[2] and r[3]],
        'runs': runs,
    }


def infra_faults(m, groups):
    """A case is faulty when more than a third of a condition's runs errored, were not graded or are missing."""
    reasons = []
    for model in m['models']:
        for condition, case, runs in planned(m):
            bad = tally(groups, condition, model, case, runs)['not_graded']
            if bad * 3 > runs:
                reasons.append(f'{model} {condition} {case}: {bad} of {runs} runs errored, '
                               'were not graded or are missing.')
    return reasons


def model_result(m, groups, model):
    """One model's gate figures, whether it passes, and why not."""
    cases = m['cases']
    t = lambda condition, case, runs: tally(groups, condition, model, case, runs)
    cand = t('candidate', cases['target']['name'], TARGET_RUNS)
    inc = t('incumbent', cases['target']['name'], TARGET_RUNS)
    hold = t('candidate', cases['holdout']['name'], HOLDOUT_RUNS)
    controls = {c['name']: (t('incumbent', c['name'], CONTROL_RUNS)['passes'],
                            t('candidate', c['name'], CONTROL_RUNS)['passes']) for c in cases['controls']}
    drops = [before - after for before, after in controls.values()]
    candidate_runs = [t(condition, case, runs) for condition, case, runs in planned(m) if condition == 'candidate']
    critical = sum(x['critical'] for x in candidate_runs)
    notes = [n for x in candidate_runs for n in x['notes']]
    reasons = [f'{model}: control {name} dropped from {before}/{CONTROL_RUNS} to {after}/{CONTROL_RUNS}.'
               for name, (before, after) in controls.items() if before - after > MAX_CONTROL_DROP]
    if critical:
        reasons.append(f'{model}: {critical} critical failure(s) in candidate runs'
                       + (f" ({'; '.join(notes)})." if notes else '.'))
    why = []
    if inc['passes'] > MAX_INCUMBENT_TARGET:
        why.append(f"incumbent passed the target {inc['passes']}/{TARGET_RUNS} (baseline drifted)")
    if cand['passes'] < TARGET_RUNS:
        why.append(f"candidate passed the target {cand['passes']}/{TARGET_RUNS}, needs {TARGET_RUNS}/{TARGET_RUNS}")
    if hold['passes'] < MIN_HOLDOUT:
        why.append(f"soft holdout {hold['passes']}/{HOLDOUT_RUNS}, needs {MIN_HOLDOUT}/{HOLDOUT_RUNS}")
    if why:
        reasons.append(f"{model}: {'; '.join(why)}.")
    return {
        'target_candidate': f"{cand['passes']}/{TARGET_RUNS}",
        'target_incumbent': f"{inc['passes']}/{TARGET_RUNS}",
        'holdout': f"{hold['passes']}/{HOLDOUT_RUNS}",
        'max_control_drop': max([0] + drops),
        'critical': critical,
        'pass': not reasons,
        'reasons': reasons,
    }


def reproduce_result(m, groups, model):
    passes = tally(groups, 'incumbent', model, m['cases']['target']['name'], REPRODUCE_RUNS)['passes']
    return {'target_incumbent': f'{passes}/{REPRODUCE_RUNS}', 'reproduced': passes < NOT_REPRODUCED_AT}


def reproduced(models, per_model):
    """Reproduced only if the incumbent fails the target on every model."""
    passing = [f"{model} ({per_model[model]['target_incumbent']})" for model in models
               if not per_model[model]['reproduced']]
    if passing:
        return 'not_reproduced', [f"Incumbent passed the target on {' and '.join(passing)}: "
                                  'the case does not capture the failure.']
    figures = ', '.join(f"{model} {per_model[model]['target_incumbent']}" for model in models)
    return 'reproduced', [f'Failure reproduced: incumbent passed the target {figures}.']


def stored_incumbent(m, base, seen):
    """Incumbent result entries from the previous attempt, and reasons when a frozen case changed since then.

    Reuse needs the same incumbent commit and the same frozen case hashes.
    Entry paths come back absolute, so they read the same from any manifest.
    """
    ref = m.get('reuse_incumbent_from')
    if not ref:
        return [], []
    path = (base / ref).resolve()
    if path in seen:
        raise ManifestError(f'reuse_incumbent_from loops back to {ref}')
    prev = load_json(path, 'previous manifest')
    need(isinstance(prev, dict) and prev.get('mode') == 'gate' and isinstance(prev.get('revisions'), dict)
         and isinstance(prev.get('cases'), dict) and isinstance(prev.get('results'), list),
         f'reuse_incumbent_from {ref} is not a gate manifest')
    need(prev['revisions'].get('incumbent') == m['revisions']['incumbent'],
         f'incumbent commit changed since {ref}: run the incumbent again instead of reusing its runs')
    old, new = frozen_hashes(prev), frozen_hashes(m)
    changed = sorted(name for name in set(old) | set(new) if old.get(name) != new.get(name))
    if changed:
        return [], [f'Frozen case {name} changed since the previous attempt ({ref}): incumbent runs not reused; '
                    'treated as gaming the eval.' for name in changed]
    entries = [dict(e, path=str(path.parent / e['path']),
                    checker=str(path.parent / e['checker']) if e.get('checker') else None)
               for e in prev['results'] if e['condition'] == 'incumbent']
    earlier, refused = stored_incumbent(prev, path.parent, seen | {path})
    return entries + earlier, refused


def frozen_hashes(m):
    return {case['name']: case['sha256'] for case in all_cases(m)}


def decide(manifest_path):
    manifest_path = Path(manifest_path)
    m = load_json(manifest_path, 'manifest')
    base = manifest_path.parent
    validate(m, base)
    reused, refused = stored_incumbent(m, base, {manifest_path.resolve()})
    groups, count, cost = collect(m['results'], base)
    stored, reused_count, _ = collect(reused, base)
    for key, runs in stored.items():
        groups.setdefault(key, []).extend(runs)
    reproduce = m['mode'] == 'reproduce'
    if reproduce:
        per_model = {model: reproduce_result(m, groups, model) for model in m['models']}
        growth = None
    else:
        per_model = {model: model_result(m, groups, model) for model in m['models']}
        inc_size = (base / m['skill_md']['incumbent']).stat().st_size
        cand_size = (base / m['skill_md']['candidate']).stat().st_size
        growth = (cand_size - inc_size) * 100 / inc_size
    retry_used = bool(m.get('infra_retry_used', False))
    out = {
        'mode': m['mode'],
        'outcome': None,
        'reasons': [],
        'per_model': per_model,
        'skill_growth_pct': None if growth is None else round(growth, 1),
        'runs': count,
        'cost_usd': round(cost, 4),
        'infra_retry_used': retry_used,
        'incumbent_reused': bool(reused),
        'reused_runs': reused_count,
    }
    changed = frozen_case_changes(m, base) + refused
    faults = infra_faults(m, groups)
    if changed:
        out.update(outcome='rejected', reasons=changed)
    elif faults and not retry_used:
        out.update(outcome='retry', infra_retry_used=True,
                   reasons=['Infrastructure fault: ' + ' '.join(faults) + ' One free retry: the attempt is not used.'])
    elif faults:
        out.update(outcome='inconclusive',
                   reasons=['Second infrastructure fault this attempt: ' + ' '.join(faults)])
    elif reproduce:
        out.update(zip(('outcome', 'reasons'), reproduced(m['models'], per_model)))
    elif growth > MAX_GROWTH_PCT:
        out.update(outcome='rejected', reasons=[f'SKILL.md grew {growth:.1f}% (limit {MAX_GROWTH_PCT}%).'])
    else:
        out.update(zip(('outcome', 'reasons'), compare(m['models'], per_model)))
    return out


def compare(models, per_model):
    """Outcome over models: a regression or critical failure on any model rejects; models must agree to accept."""
    reasons = [r for model in models for r in per_model[model]['reasons']]
    if any(per_model[model]['critical'] or per_model[model]['max_control_drop'] > MAX_CONTROL_DROP
           for model in models):
        return 'rejected', reasons
    passing = [model for model in models if per_model[model]['pass']]
    if len(passing) == len(models):
        return 'accepted', [f"{' and '.join(models)}: target {TARGET_RUNS}/{TARGET_RUNS} against incumbent at most "
                            f'{MAX_INCUMBENT_TARGET}/{TARGET_RUNS}, holdout at least {MIN_HOLDOUT}/{HOLDOUT_RUNS}, '
                            'no regression, no critical failure.']
    if not passing:
        return 'rejected', reasons
    return 'inconclusive', ['Models disagree: ' + ' '.join(reasons)]


def frozen_case_changes(m, base):
    """Reasons for each frozen case that is missing or changed. Reproduce mode never needs the holdout."""
    cases = m['cases']
    checked = [(cases['target'], m['case_dir'])] + [(c, m['case_dir']) for c in cases.get('controls', [])]
    if m['mode'] == 'gate':
        checked.insert(1, (cases['holdout'], m.get('holdout_dir') or m['case_dir']))
    reasons = []
    for case, where in checked:
        case_dir = base / where
        if not (case_dir / case['name']).is_dir():
            reasons.append(f"Frozen case {case['name']} is missing from {where}: treated as gaming the eval.")
            continue
        actual = case_hash(case_dir / case['name'])
        if actual != case['sha256']:
            reasons.append(f"Frozen case {case['name']} changed after freezing (sha256 {actual[:12]}, "
                           f"frozen {case['sha256'][:12]}): treated as gaming the eval.")
    return reasons


def all_cases(m):
    cases = m['cases']
    return [cases['target']] + ([cases['holdout']] if cases.get('holdout') else []) + list(cases.get('controls', []))


def main(argv):
    try:
        if len(argv) == 2 and argv[0] == 'decide':
            print(json.dumps(decide(argv[1]), indent=2))
            return 0
        if len(argv) == 2 and argv[0] == 'hash':
            need(Path(argv[1]).is_dir(), f'{argv[1]} is not a case directory')
            print(case_hash(argv[1]))
            return 0
    except ManifestError as error:
        print(f'gate: {error}', file=sys.stderr)
        return 2
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
