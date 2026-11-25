#!/usr/bin/env python3
"""Retro loop run driver: run one reproduce or gate step's evals, then decide it with gate.py.

Usage:
  run.py reproduce --plan PLAN --cases CASES --case-dir DIR --checker FILE [options]
  run.py gate --plan PLAN --cases CASES --case-dir DIR --holdout-dir DIR --checker FILE [options]

PLAN is the JSON that jstack's `scripts/retro_loop.py next --finding N` printed ('-' reads
stdin). It supplies the finding, owning skill, attempt, whether the free infrastructure retry
is used, the loop branch and max_cost_usd, the whole budget of this step. The driver refuses a
plan the runner refused and a plan for another step. CASES is the frozen cases JSON that was
given to `retro_loop.py freeze`.

For each condition the driver builds a plugin named jstack from `git archive <rev>
skills/<owning skill>` of the jstack checkout, plus the frozen cases that condition runs. The
soft holdout goes into the candidate's plugin only, and only in gate mode. It runs `claude
plugin eval` once per case, model and condition, with the run counts gate.py plans (target 5,
holdout 5, controls 3, reproduce 3), alternating incumbent and candidate. Each invocation gets
what is left of the budget as --max-cost-usd. Then it runs the checker on each results file,
copies the traces, writes manifest.json, asks gate.py for the decision and, in gate mode,
writes a bundle of traces for the advisory judges with the condition hidden. The runner
records the step afterwards: `retro_loop.py reproduce|gate N --manifest <run dir>/manifest.json`.

Raw results stay in a run directory outside both repositories, named from the step's inputs
(revisions, case hashes, checker hash, models, attempt, retry). Running the driver again with
the same inputs reuses the saved results and pays for nothing twice. When a frozen case hash
has changed, nothing is run: the gate rejects on the hashes alone. The jstack kill switch
(loop.disabled) is checked before each paid invocation.

Prints one JSON report. Exits 0 when the gate decided, 3 when the driver refused or stopped
before deciding, and 1 on an error.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import random
import shlex
import shutil
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import gate  # noqa: E402

# The environment wrapper of harness/j-build/run_eval.sh: bill the Platform key at Infisical /research and keep the
# owner's proxy and tool keys out of the runs. tests/test_retro_run.py fails when the two drift apart.
CLAUDE = ['/Users/jeremy/.local/bin/infisical', 'run', '--silent', '--projectId', 'dbb4c6c1-6800-4479-8cfd-fd65c2d5966d',
          '--env', 'prod', '--path', '/research', '--',
          'env', '-u', 'CLAUDE_CONFIG_DIR', '-u', 'ANTHROPIC_BASE_URL', '-u', 'ANTHROPIC_AUTH_TOKEN', '-u', 'EXA_API_KEY',
          '-u', 'FIRECRAWL_API_KEY', '-u', 'OPENROUTER_API_KEY', '-u', 'TAVILY_API_KEY', '-u', 'TYPESAFE_API_KEY',
          'claude']
EVAL_FLAGS = ['--ablation', 'none', '--threshold', '0', '--trust-plugin', '--no-publish', '--keep-temp', '--scaffold',
              '-j', '4']
# The j-build harness grant. Without it agents cannot run tests or write receipts, which voided the first reproduce run.
TOOLS = ['--allow-tools', 'Write', 'Edit', 'Bash']
KILL_SWITCH = 'loop.disabled'
RUN_ROOT = '~/.local/share/jstack-retro-loop/runs'
MIN_BUDGET = 0.01


class DriverError(Exception):
    pass


class Refused(Exception):
    pass


def money(value):
    return round(max(value, 0), 2)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def read_json(name, what):
    try:
        text = sys.stdin.read() if name == '-' else Path(name).expanduser().read_text()
        return json.loads(text)
    except (OSError, ValueError) as error:
        raise DriverError(f'cannot read {what} {name}: {error}')


def write_json(path, data):
    tmp = path.with_name(f'.{path.name}.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    os.replace(tmp, path)


def git(repo, *args, binary=False):
    proc = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=not binary)
    if proc.returncode != 0:
        err = proc.stderr.decode(errors='replace') if binary else proc.stderr
        raise DriverError(f"git {' '.join(args)} failed in {repo}: {err.strip() or 'no message'}")
    return proc.stdout


def resolve(repo, rev):
    proc = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', '--quiet', f'{rev}^{{commit}}'],
                          capture_output=True, text=True)
    if proc.returncode != 0 or not rev:
        raise DriverError(f'{rev or "(no revision)"} is not a commit in {repo}')
    return proc.stdout.strip()


def check_plan(plan, mode):
    if not isinstance(plan, dict):
        raise DriverError('the plan is not the JSON object retro_loop.py next prints')
    if plan.get('refused'):
        raise Refused(f"the runner refused this step: {plan['refused']}")
    if plan.get('step') != mode:
        raise Refused(f"the runner's next step for #{plan.get('finding')} is {plan.get('step')}, not {mode}")
    kinds = {'finding': int, 'owning_skill': str, 'attempt': int, 'infra_retry_used': bool, 'max_cost_usd': float}
    for key, kind in kinds.items():
        value = plan.get(key)
        ok = isinstance(value, bool) if kind is bool else (
            not isinstance(value, bool) and isinstance(value, (int, float) if kind is float else kind))
        if not ok:
            raise DriverError(f'the plan has no usable {key}')


def check_cases(cases):
    def ok(case):
        return isinstance(case, dict) and isinstance(case.get('name'), str) and case['name'] \
            and isinstance(case.get('sha256'), str) and len(case['sha256']) == 64
    if not (isinstance(cases, dict) and ok(cases.get('target')) and ok(cases.get('holdout'))
            and isinstance(cases.get('controls'), list) and cases['controls'] and all(map(ok, cases['controls']))):
        raise DriverError('cases must be the frozen {target, holdout, controls} JSON with a name and sha256 each')


def directory(value, flag):
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise DriverError(f'{flag} {value} is not a directory')
    return path


def inside(path, repo):
    return path == repo or repo in path.parents


def previous_attempt(value, finding, skill):
    path = Path(value).expanduser().resolve()
    prev = read_json(str(path), 'previous manifest')
    if not (isinstance(prev, dict) and prev.get('mode') == 'gate' and prev.get('finding') == finding
            and prev.get('owning_skill') == skill and isinstance(prev.get('revisions'), dict)
            and isinstance(prev['revisions'].get('incumbent'), str)
            and any(e.get('condition') == 'incumbent' for e in prev.get('results') or [])):
        raise Refused(f'{value} is not a gate manifest with incumbent runs for #{finding} ({skill})')
    return path, prev


def alternate(planned, models, reuse):
    """One invocation per case, model and condition: case by case, model by model, incumbent then candidate."""
    cases = list(dict.fromkeys(case for _, case, _ in planned))
    order = []
    for case in cases:
        for model in models:
            for condition in ('incumbent', 'candidate'):
                if reuse and condition == 'incumbent':
                    continue
                order += [{'condition': condition, 'model': model, 'case': case, 'runs': runs}
                          for cond, name, runs in planned if cond == condition and name == case]
    return order


def build_plugin(jstack, rev, skill, cases, dest, description):
    """plugin.json, skills/<skill> from git archive at rev, and evals/<case> per case. Kept when already built."""
    if dest.is_dir():
        return
    tmp = dest.with_name(f'.{dest.name}.tmp')
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp / '.claude-plugin').mkdir(parents=True)
    (tmp / '.claude-plugin' / 'plugin.json').write_text(
        json.dumps({'name': 'jstack', 'version': '0.0.0', 'description': description}) + '\n')
    archive = git(jstack, 'archive', '--format=tar', rev, f'skills/{skill}', binary=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(tmp, filter='data')
    if not (tmp / 'skills' / skill / 'SKILL.md').is_file():
        raise DriverError(f'skills/{skill}/SKILL.md is not in jstack {rev[:12]}')
    (tmp / 'evals').mkdir()
    for name, source in cases:
        shutil.copytree(source / name, tmp / 'evals' / name)
    os.replace(tmp, dest)


def read_results(path, case):
    """(runs, cost) from one claude plugin eval --json file that must hold exactly this case."""
    data = json.loads(path.read_text())
    names = [c.get('name') for c in data.get('cases', [])] if isinstance(data, dict) else []
    if names != [case]:
        raise ValueError(f'{path.name} holds cases {names}, expected [{case!r}]')
    runs = data['cases'][0].get('arms', {}).get('with')
    if not isinstance(runs, list):
        raise ValueError(f'{path.name} has no with-arm runs')
    return data, runs, float(data.get('costUsd') or 0)


class Driver:
    def __init__(self, args, report):
        self.args = args
        self.report = report
        self.notes = report['notes']

    def run(self):
        args, mode = self.args, self.args.mode
        plan = read_json(args.plan, 'plan')
        check_plan(plan, mode)
        finding, skill = plan['finding'], plan['owning_skill']
        self.report['finding'] = finding
        jstack = Path(args.jstack).expanduser().resolve()
        top = Path(git(jstack, 'rev-parse', '--show-toplevel').strip()).resolve()
        self.kill = Path(args.kill_switch).expanduser() if args.kill_switch else top / KILL_SWITCH
        if self.kill.exists():
            raise Refused(f'the kill switch ({self.kill}) is on')
        cases = read_json(args.cases, 'cases')
        check_cases(cases)
        case_dir = directory(args.case_dir, '--case-dir')
        holdout_dir = directory(args.holdout_dir, '--holdout-dir') if args.holdout_dir else None
        checker = Path(args.checker).expanduser().resolve()
        if not checker.is_file():
            raise DriverError(f'--checker {args.checker} is not a file')
        if mode == 'gate' and holdout_dir is None:
            raise Refused('a gate needs --holdout-dir: the soft holdout runs for the candidate')
        if mode == 'reproduce' and (args.candidate or args.reuse_incumbent_from):
            raise Refused('reproduce runs the incumbent alone: no --candidate or --reuse-incumbent-from')
        previous = previous_attempt(args.reuse_incumbent_from, finding, skill) if args.reuse_incumbent_from else None
        incumbent = resolve(jstack, args.incumbent or (previous[1]['revisions']['incumbent'] if previous else 'main'))
        if previous and incumbent != previous[1]['revisions']['incumbent']:
            raise Refused('the incumbent differs from the previous attempt, so its runs cannot be reused: '
                          'run without --reuse-incumbent-from')
        candidate = None
        if mode == 'gate':
            candidate = resolve(jstack, args.candidate or plan.get('branch') or '')
            if candidate == incumbent:
                raise Refused(f'the candidate is the incumbent ({incumbent[:12]}): nothing to compare')
        revisions = {'incumbent': incumbent, 'candidate': candidate}
        checker_sha = hashlib.sha256(checker.read_bytes()).hexdigest()
        key = digest(json.dumps({
            'mode': mode, 'finding': finding, 'attempt': plan['attempt'], 'retry': plan['infra_retry_used'],
            'models': args.models, 'revisions': revisions, 'cases': cases, 'checker': checker_sha,
            'reuse': str(previous[0]) if previous else None}, sort_keys=True))
        run_dir = self.run_dir(plan, key)
        for repo in (top, ROOT):
            if inside(run_dir, repo):
                raise Refused(f'the run directory {run_dir} is inside {repo}; keep raw results outside both repositories')
        self.report['run_dir'] = str(run_dir)
        (run_dir / 'results').mkdir(parents=True, exist_ok=True)
        (run_dir / 'checker').mkdir(exist_ok=True)
        (run_dir / 'traces').mkdir(exist_ok=True)

        conditions = ('incumbent', 'candidate') if mode == 'gate' else ('incumbent',)
        plugins = {c: f'plugin-{digest(key + c)[:6]}' for c in conditions}  # neutral names: traces show the path
        manifest = {
            'mode': mode, 'finding': finding, 'owning_skill': skill, 'attempt': plan['attempt'],
            'infra_retry_used': plan['infra_retry_used'], 'models': list(args.models), 'revisions': revisions,
            'skill_md': {c: f'{plugins[c]}/skills/{skill}/SKILL.md' if c in plugins else None
                         for c in ('incumbent', 'candidate')},
            'cases': cases, 'case_dir': str(case_dir), 'holdout_dir': str(holdout_dir) if holdout_dir else None,
            'results': [], 'reuse_incumbent_from': str(previous[0]) if previous else None,
            'checker': {'path': str(checker), 'sha256': checker_sha},
            'max_cost_usd': plan['max_cost_usd'],
            'runner': 'claude plugin eval ' + ' '.join(EVAL_FLAGS + TOOLS),
            'evals_revision': git(ROOT, 'rev-parse', 'HEAD').strip(),
        }
        planned = gate.planned(manifest)
        changed = gate.frozen_case_changes(manifest, run_dir)
        if changed:
            self.notes.extend(changed)
            self.notes.append('A frozen case changed or is missing: nothing was run, the gate decides on hashes alone.')
        holdout = cases['holdout']['name']
        for condition in conditions:
            names = [] if changed else list(dict.fromkeys(case for cond, case, _ in planned if cond == condition))
            sources = [(name, holdout_dir if name == holdout else case_dir) for name in names]
            build_plugin(jstack, revisions[condition], skill, sources, run_dir / plugins[condition],
                         f'retro loop finding {finding}')

        self.claude = shlex.split(args.claude_command) if args.claude_command else CLAUDE
        records = [] if changed else alternate(planned, args.models, bool(previous))
        self.report['invocations'] = records
        spent = 0.0
        for record in records:
            spent += self.invoke(record, run_dir, plugins, plan['max_cost_usd'] - spent)
            self.report['spent_usd'] = money(spent)
        for record in records:
            if record.get('recorded'):
                manifest['results'].append(self.check(record, run_dir, checker))
        manifest['invocations'] = records
        manifest_path = run_dir / 'manifest.json'
        write_json(manifest_path, manifest)
        self.report['manifest'] = str(manifest_path)
        decision = gate.decide(manifest_path)
        write_json(run_dir / 'decision.json', decision)
        self.report['decision'] = decision
        if mode == 'gate':
            self.judges(run_dir, records, key)
        return 0

    def run_dir(self, plan, key):
        if self.args.run_dir:
            return Path(self.args.run_dir).expanduser().resolve()
        root = Path(self.args.run_root or os.environ.get('JSTACK_RETRO_RUNS') or RUN_ROOT).expanduser().resolve()
        retry = '-retry' if plan['infra_retry_used'] else ''
        return root / str(plan['finding']) / f"{self.args.mode}-a{plan['attempt']}{retry}-{key[:8]}"

    def invoke(self, record, run_dir, plugins, budget):
        """Run one invocation unless its results are saved; return the cost of its results file."""
        stem = f"{record['condition']}-{record['model']}-{record['case']}"
        results, log = run_dir / 'results' / f'{stem}.json', run_dir / 'results' / f'{stem}.log'
        record.update(results=str(results.relative_to(run_dir)), log=str(log.relative_to(run_dir)), status='saved',
                      exit=None, max_cost_usd=None, cost_usd=None, recorded=0)
        if not results.exists():
            if self.kill.exists():
                raise Refused(f'the kill switch ({self.kill}) was turned on during the step. Saved results are kept; '
                              'run the driver again with the same inputs once it is off.')
            budget = money(budget)
            if budget < MIN_BUDGET:
                record['status'] = 'skipped'
                self.notes.append(f'{stem}: not run, the step budget is spent.')
                return 0.0
            target = run_dir / plugins[record['condition']] / 'evals' / record['case'] / 'prompt.md'
            argv = self.claude + ['plugin', 'eval', str(target), *EVAL_FLAGS, '--runs', str(record['runs']),
                                  '--model', record['model'], '--max-cost-usd', f'{budget:.2f}', *TOOLS,
                                  '--json', str(results)]
            with open(log, 'w') as out:
                proc = subprocess.run(argv, stdout=out, stderr=subprocess.STDOUT, cwd=run_dir)
            record.update(status='ran', exit=proc.returncode, max_cost_usd=budget)
            if not results.exists():
                self.notes.append(f'{stem}: claude plugin eval exited {proc.returncode} without a results file; '
                                  f'see {record["log"]}.')
                return 0.0
        try:
            data, runs, cost = read_results(results, record['case'])
        except (OSError, ValueError, KeyError, AttributeError) as error:
            self.notes.append(f'{stem}: results file not used: {error}')
            return 0.0
        record.update(cost_usd=round(cost, 4), recorded=len(runs), partial=bool(data.get('partial')))
        return cost

    def check(self, record, run_dir, checker):
        """Copy the traces, run the checker over the results with the saved traces, and return the manifest entry."""
        stem = Path(record['results']).stem
        results = run_dir / record['results']
        data = json.loads(results.read_text())
        runs = data['cases'][0]['arms']['with']
        for i, run in enumerate(runs, 1):
            source = Path(run.get('tracePath') or '')
            saved = run_dir / 'traces' / f'{stem}-{i}{source.suffix or ".jsonl"}'
            if not saved.exists() and run.get('tracePath'):
                try:
                    shutil.copyfile(source, saved)
                except OSError as error:
                    self.notes.append(f'{stem} run {i}: trace not saved: {error}')
            if saved.exists():
                run['tracePath'] = str(saved)
        entry = {'condition': record['condition'], 'model': record['model'], 'path': record['results'], 'checker': None}
        if not runs:
            return entry
        given = run_dir / 'checker' / f'.{stem}.input.json'
        given.write_text(json.dumps(data))
        try:
            proc = subprocess.run([sys.executable, str(checker), record['case'], str(given)],
                                  capture_output=True, text=True)
        finally:
            given.unlink()
        if proc.returncode != 0:
            raise DriverError(f"checker exited {proc.returncode} on {record['results']}: {proc.stderr.strip()}. "
                              'Saved results are kept: fix the cause and run the driver again.')
        try:
            checks = json.loads(proc.stdout).get(record['case'])
        except (ValueError, AttributeError):
            checks = None
        if not isinstance(checks, list) or len(checks) != len(runs):
            raise DriverError(f"checker output for {record['results']} does not hold one entry per run")
        out = run_dir / 'checker' / f'{stem}.json'
        write_json(out, {record['case']: checks})
        entry['checker'] = str(out.relative_to(run_dir))
        return entry

    def judges(self, run_dir, records, key):
        """Traces under neutral ids for the advisory judges; judge-key.json maps ids back to condition and model."""
        bundle = run_dir / 'judges'
        shutil.rmtree(bundle, ignore_errors=True)
        bundle.mkdir()
        traces = []
        for record in records:
            stem = Path(record['results']).stem
            for i in range(1, record.get('recorded', 0) + 1):
                saved = next(iter(sorted((run_dir / 'traces').glob(f'{stem}-{i}.*'))), None)
                if saved:
                    traces.append((record, i, saved))
        random.Random(key).shuffle(traces)
        index, secret = {}, {}
        for n, (record, i, saved) in enumerate(traces, 1):
            name = f'T{n:03d}{saved.suffix}'
            shutil.copyfile(saved, bundle / name)
            index[name] = {'case': record['case']}
            secret[name] = {'condition': record['condition'], 'model': record['model'], 'case': record['case'], 'run': i}
        write_json(bundle / 'index.json', index)
        write_json(run_dir / 'judge-key.json', secret)
        self.report['judges'] = {'bundle': str(bundle), 'key': str(run_dir / 'judge-key.json'), 'traces': len(traces)}


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('mode', choices=['reproduce', 'gate'])
    p.add_argument('--plan', required=True, help="JSON from retro_loop.py next --finding N ('-' reads stdin)")
    p.add_argument('--cases', required=True, help='the frozen cases JSON given to retro_loop.py freeze')
    p.add_argument('--case-dir', required=True, help='directory holding the target and control cases')
    p.add_argument('--holdout-dir', help='directory holding the soft holdout; required in gate mode')
    p.add_argument('--checker', required=True, help="the eval author's checker: checker.py CASE RESULTS prints JSON")
    p.add_argument('--jstack', default=str(ROOT.parent / 'jstack'), help='jstack checkout (default: ../jstack)')
    p.add_argument('--incumbent', help="jstack revision (default: main, or the reused attempt's incumbent)")
    p.add_argument('--candidate', help="gate: jstack revision under test (default: the plan's loop branch)")
    p.add_argument('--reuse-incumbent-from', help="gate: the previous attempt's manifest.json, to run only the candidate")
    p.add_argument('--models', nargs='+', default=['opus', 'sonnet'])
    p.add_argument('--run-root', help=f'parent of per-finding run directories (default: $JSTACK_RETRO_RUNS or {RUN_ROOT})')
    p.add_argument('--run-dir', help='exact run directory, instead of one named from the inputs')
    p.add_argument('--kill-switch', help=f'stop file (default: {KILL_SWITCH} in the jstack checkout)')
    p.add_argument('--claude-command', help='command that replaces the Infisical-wrapped claude, such as a fake for tests')
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    report = {'mode': args.mode, 'finding': None, 'run_dir': None, 'manifest': None, 'decision': None,
              'spent_usd': 0.0, 'invocations': [], 'notes': [], 'refused': None, 'error': None}
    try:
        code = Driver(args, report).run()
    except Refused as refusal:
        report['refused'], code = str(refusal), 3
    except (DriverError, gate.ManifestError, OSError, ValueError, tarfile.TarError) as error:
        report['error'], code = str(error), 1
    print(json.dumps(report, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
