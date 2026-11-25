#!/usr/bin/env python3
"""Retro loop gate: decide one gate step for a retro finding from recorded results.

Usage:
  gate.py decide MANIFEST.json   print the decision as one JSON object
  gate.py hash CASE_DIR          print the sha256 of one frozen case

The manifest and output shapes are the retro loop contract (jstack#17, #18).
No model is called: the decision comes from `claude plugin eval --json` result
files and optional checker output named in the manifest.
"""
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

TARGET_RUNS, HOLDOUT_RUNS, CONTROL_RUNS, REPRODUCE_RUNS = 5, 5, 3, 3
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


def collect(entries, base):
    """Runs per (condition, model, case) as (passed, graded, critical, note), plus run count and cost.

    A run passes only if it was graded, the harness passed it and the checker
    (when the entry names one) passes it too. Critical comes from the checker.
    """
    groups, count, cost = {}, 0, 0.0
    for entry in entries:
        result = load_json(base / entry['path'], 'result file')
        checker = load_json(base / entry['checker'], 'checker output') if entry.get('checker') else {}
        for case in result['cases']:
            runs = case['arms']['with']
            checks = checker.get(case['name'])
            if checks is not None and len(checks) != len(runs):
                raise ManifestError(f"checker {entry['checker']} has {len(checks)} entries for {case['name']}, "
                                    f"the result file has {len(runs)} runs")
            for i, run in enumerate(runs):
                count += 1
                cost += run.get('costUsd', 0) + run.get('judgeCostUsd', 0)
                graded = not run.get('error') and bool(run.get('graders')) and not run.get('skippedPaidGraders')
                check = checks[i] if checks is not None else {'pass': True}
                groups.setdefault((entry['condition'], entry['model'], case['name']), []).append(
                    (bool(run['passed']) and graded and bool(check.get('pass')), graded,
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
    if prev.get('mode') != 'gate':
        raise ManifestError(f'reuse_incumbent_from {ref} is not a gate manifest')
    if prev['revisions']['incumbent'] != m['revisions']['incumbent']:
        raise ManifestError(f'incumbent commit changed since {ref}: run the incumbent again instead of reusing its runs')
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
    case_dir = base / m['case_dir']
    reasons = []
    for case in all_cases(m):
        actual = case_hash(case_dir / case['name'])
        if actual != case['sha256']:
            reasons.append(f"Frozen case {case['name']} changed after freezing (sha256 {actual[:12]}, "
                           f"frozen {case['sha256'][:12]}): treated as gaming the eval.")
    return reasons


def all_cases(m):
    cases = m['cases']
    return [cases['target']] + ([cases['holdout']] if cases.get('holdout') else []) + list(cases.get('controls', []))


def main(argv):
    if len(argv) == 2 and argv[0] == 'decide':
        print(json.dumps(decide(argv[1]), indent=2))
        return 0
    if len(argv) == 2 and argv[0] == 'hash':
        print(case_hash(argv[1]))
        return 0
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
