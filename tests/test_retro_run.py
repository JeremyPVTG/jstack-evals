"""The retro loop run driver, with a fake `claude` and a fake checker: no paid runs.

Each test builds a small jstack repository (incumbent on main, candidates on branches), frozen
cases with their hashes, and a plan as `retro_loop.py next` prints it, then drives one step and
checks the plugins, the claude invocations, the manifest and the gate's decision.
"""
import importlib.util
import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'harness' / 'retro-loop' / 'run.py'
FIXTURES = Path(__file__).resolve().parent / 'fixtures' / 'retro-loop'
FAKE_CLAUDE, FAKE_CHECKER = FIXTURES / 'fake_claude.py', FIXTURES / 'fake_checker.py'
spec = importlib.util.spec_from_file_location('retro_run', SCRIPT)
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
gate = run.gate

TARGET, HOLDOUT, CONTROLS = 'stale', 'stale-reworded', ['control-fresh', 'control-one-stale']
INCUMBENT_TEXT = '---\nname: j-build\ndescription: build\n---\n' + 'Build, review, verify, report.\n' * 6
FLAGS = ['--ablation', 'none', '--threshold', '0', '--trust-plugin', '--no-publish', '--keep-temp', '--scaffold']


class DriverFixture(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.jstack = self.root / 'jstack'
        self.git('init', '-q', '-b', 'main', str(self.jstack))
        self.write('skills/j-build/SKILL.md', INCUMBENT_TEXT)
        self.write('skills/j-build/references/review.md', 'Run each lens.\n')
        self.write('skills/j-other/SKILL.md', 'not under test\n')
        self.commit('incumbent')
        self.main = self.sha('main')
        self.branch('loop/j-build/26', INCUMBENT_TEXT + 'FIXED: rerun stale lenses.\n')
        self.branch('loop-weak', INCUMBENT_TEXT + 'Mention reviews.\n')
        self.case_dir, self.holdout_dir = self.root / 'cases', self.root / 'holdout'
        for name in [TARGET] + CONTROLS:
            self.case(self.case_dir, name)
        self.case(self.holdout_dir, HOLDOUT)
        self.cases = self.root / 'cases.json'
        freeze = lambda where, name: {'name': name, 'sha256': gate.case_hash(where / name)}
        self.cases.write_text(json.dumps({'target': freeze(self.case_dir, TARGET),
                                          'holdout': freeze(self.holdout_dir, HOLDOUT),
                                          'controls': [freeze(self.case_dir, name) for name in CONTROLS]}))
        self.runs = self.root / 'runs'
        self.log = self.root / 'calls.jsonl'
        self.env = {'FAKE_CLAUDE_LOG': str(self.log), 'FAKE_CLAUDE_TRACES': str(self.root / 'tmp')}

    def git(self, *args, repo=None):
        base = ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com', '-c', 'core.hooksPath=/dev/null',
                '-c', 'commit.gpgsign=false']
        return subprocess.run(base + (['-C', str(repo)] if repo else []) + list(args), check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, rel, text):
        path = self.jstack / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, message):
        self.git('add', '-A', repo=self.jstack)
        self.git('commit', '-q', '--no-verify', '-m', message, repo=self.jstack)

    def sha(self, rev):
        return self.git('rev-parse', rev, repo=self.jstack)

    def branch(self, name, skill_text):
        self.git('checkout', '-q', '-b', name, 'main', repo=self.jstack)
        self.write('skills/j-build/SKILL.md', skill_text)
        self.commit(name)
        self.git('checkout', '-q', 'main', repo=self.jstack)

    @staticmethod
    def case(where, name):
        (where / name / 'graders').mkdir(parents=True)
        (where / name / 'prompt.md').write_text(f'---\nname: {name}\n---\nWrap up and report.\n')
        (where / name / 'fixture.sh').write_text('#!/bin/sh\ngit init -q\n')
        (where / name / 'graders' / 'status.md').write_text('---\ntype: regex\n---\nblocked\n')

    def plan(self, mode, **fields):
        body = {'finding': 26, 'state': 'Ready' if mode == 'reproduce' else 'In progress', 'step': mode,
                'refused': None, 'owning_skill': 'j-build', 'attempt': 0 if mode == 'reproduce' else 1,
                'infra_retry_used': False, 'max_cost_usd': 100.0, 'branch': 'loop/j-build/26'}
        body.update(fields)
        return body

    def argv(self, mode, plan_file, *extra):
        argv = [mode, '--plan', plan_file, '--cases', str(self.cases), '--case-dir', str(self.case_dir),
                '--checker', str(FAKE_CHECKER), '--jstack', str(self.jstack), '--run-root', str(self.runs),
                '--claude-command', f'{shlex.quote(sys.executable)} {shlex.quote(str(FAKE_CLAUDE))}']
        if mode == 'gate':
            argv += ['--holdout-dir', str(self.holdout_dir)]
        return argv + list(extra)

    def drive(self, mode, *extra, env=None, **plan):
        plan_file = self.root / 'plan.json'
        plan_file.write_text(json.dumps(self.plan(mode, **plan)))
        out = io.StringIO()
        with redirect_stdout(out), mock.patch.dict(os.environ, {**self.env, **(env or {})}):
            code = run.main(self.argv(mode, str(plan_file), *extra))
        return code, json.loads(out.getvalue())

    def calls(self):
        """Fake claude argv lists since the last call to this method."""
        if not self.log.exists():
            return []
        lines = self.log.read_text().splitlines()
        self.log.unlink()
        return [json.loads(line) for line in lines]

    @staticmethod
    def flag(argv, name, count=1):
        i = argv.index(name)
        return argv[i + 1] if count == 1 else argv[i + 1:i + 1 + count]

    def manifest(self, report):
        return json.loads(Path(report['manifest']).read_text())

    def condition_of(self, manifest, argv):
        """Which condition's plugin an invocation's target prompt.md sits in."""
        plugin = Path(argv[2]).parents[2].name
        return next(c for c, path in manifest['skill_md'].items() if path and path.startswith(plugin + '/'))


class Reproduce(DriverFixture):
    def test_reproduce_runs_the_incumbent_target_three_times_per_model(self):
        code, report = self.drive('reproduce')
        self.assertEqual(code, 0, report)
        self.assertEqual(report['decision']['outcome'], 'reproduced')
        calls = self.calls()
        self.assertEqual([self.flag(c, '--model') for c in calls], ['opus', 'sonnet'])
        for argv in calls:
            self.assertEqual(argv[:2], ['plugin', 'eval'])
            self.assertTrue(argv[2].endswith(f'/evals/{TARGET}/prompt.md'))
            self.assertEqual(argv[3:3 + len(FLAGS)], FLAGS)
            self.assertEqual(self.flag(argv, '--runs'), '3')
            self.assertEqual(self.flag(argv, '--allow-tools', 3), ['Write', 'Edit', 'Bash'])
            self.assertGreater(argv.index('--json'), argv.index('--allow-tools'))
        self.assertEqual([self.flag(c, '--max-cost-usd') for c in calls], ['100.00', '98.50'])
        self.assertEqual(report['spent_usd'], 3.0)

        manifest = self.manifest(report)
        run_dir = Path(report['run_dir'])
        self.assertTrue(run_dir.is_relative_to(self.runs / '26'))
        self.assertEqual((manifest['mode'], manifest['finding'], manifest['owning_skill'], manifest['attempt']),
                         ('reproduce', 26, 'j-build', 0))
        self.assertEqual(manifest['revisions'], {'incumbent': self.main, 'candidate': None})
        self.assertIsNone(manifest['skill_md']['candidate'])
        self.assertEqual([(r['condition'], r['model']) for r in manifest['results']],
                         [('incumbent', 'opus'), ('incumbent', 'sonnet')])
        self.assertTrue(all((run_dir / r['checker']).is_file() for r in manifest['results']))
        plugin = (run_dir / manifest['skill_md']['incumbent']).parents[2]
        self.assertEqual((plugin / 'skills' / 'j-build' / 'SKILL.md').read_text(), INCUMBENT_TEXT)
        self.assertTrue((plugin / 'skills' / 'j-build' / 'references' / 'review.md').is_file())
        self.assertEqual(sorted(p.name for p in (plugin / 'skills').iterdir()), ['j-build'])
        self.assertEqual(sorted(p.name for p in (plugin / 'evals').iterdir() if p.name != 'results'), [TARGET])
        self.assertEqual(json.loads((plugin / '.claude-plugin' / 'plugin.json').read_text())['name'], 'jstack')
        self.assertFalse([p for p in run_dir.rglob('*') if HOLDOUT in p.name], 'the holdout must stay out of reproduce')
        self.assertEqual(len(list((run_dir / 'traces').iterdir())), 6)
        checks = json.loads((run_dir / manifest['results'][0]['checker']).read_text())[TARGET]
        self.assertEqual({c['note'] for c in checks}, {'trace read'})
        self.assertEqual(json.loads((run_dir / 'decision.json').read_text())['outcome'], 'reproduced')

    def test_command_line_reads_the_plan_from_stdin(self):
        done = subprocess.run([sys.executable, str(SCRIPT), *self.argv('reproduce', '-')],
                              input=json.dumps(self.plan('reproduce')), capture_output=True, text=True,
                              env={**os.environ, **self.env})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)['decision']['outcome'], 'reproduced')

    def test_saved_results_are_reused_so_nothing_is_paid_twice(self):
        _, first = self.drive('reproduce')
        self.assertEqual(len(self.calls()), 2)
        code, again = self.drive('reproduce')
        self.assertEqual(code, 0)
        self.assertEqual(self.calls(), [])
        self.assertEqual(again['run_dir'], first['run_dir'])
        self.assertEqual({i['status'] for i in again['invocations']}, {'saved'})
        self.assertEqual(again['decision']['outcome'], 'reproduced')

    def test_an_infrastructure_retry_gets_its_own_run_directory(self):
        _, first = self.drive('reproduce')
        _, retry = self.drive('reproduce', infra_retry_used=True)
        self.assertEqual(len(self.calls()), 4)
        self.assertNotEqual(retry['run_dir'], first['run_dir'])
        self.assertIn('-retry-', retry['run_dir'])

    def test_a_case_changed_after_freezing_runs_nothing_and_is_rejected(self):
        with open(self.case_dir / 'control-fresh' / 'prompt.md', 'a') as prompt:
            prompt.write('Also bump the version.\n')
        code, report = self.drive('reproduce')
        self.assertEqual(code, 0, report)
        self.assertEqual(self.calls(), [])
        self.assertEqual(report['decision']['outcome'], 'rejected')
        self.assertIn('control-fresh changed after freezing', report['decision']['reasons'][0])
        self.assertEqual(self.manifest(report)['results'], [])

    def test_the_budget_left_goes_to_each_invocation(self):
        code, report = self.drive('reproduce', max_cost_usd=2.0)
        self.assertEqual(code, 0, report)
        self.assertEqual([self.flag(c, '--max-cost-usd') for c in self.calls()], ['2.00', '0.50'])
        sonnet = report['invocations'][1]
        self.assertEqual((sonnet['exit'], sonnet['recorded'], sonnet['partial']), (2, 1, True))
        self.assertEqual(report['decision']['outcome'], 'retry')
        self.assertIn('sonnet incumbent stale: 2 of 3', report['decision']['reasons'][0])

    def test_a_spent_budget_skips_the_remaining_invocations(self):
        code, report = self.drive('reproduce', max_cost_usd=1.5)
        self.assertEqual(code, 0, report)
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual([i['status'] for i in report['invocations']], ['ran', 'skipped'])
        self.assertTrue(any('budget is spent' in note for note in report['notes']))
        self.assertEqual(report['decision']['outcome'], 'retry')

    def test_an_invocation_without_a_results_file_counts_as_missing_runs_and_runs_again_next_time(self):
        code, report = self.drive('reproduce', env={'FAKE_CLAUDE_MODE': 'nojson'})
        self.assertEqual(code, 0, report)
        self.assertEqual(self.manifest(report)['results'], [])
        self.assertEqual(report['decision']['outcome'], 'retry')
        self.assertTrue(any('without a results file' in note for note in report['notes']))
        self.calls()
        _, again = self.drive('reproduce')
        self.assertEqual(len(self.calls()), 2)
        self.assertEqual(again['decision']['outcome'], 'reproduced')


class Gate(DriverFixture):
    def test_gate_alternates_conditions_and_runs_what_gate_py_plans(self):
        code, report = self.drive('gate')
        self.assertEqual(code, 0, report)
        self.assertEqual(report['decision']['outcome'], 'accepted')
        manifest = self.manifest(report)
        self.assertEqual(manifest['revisions'], {'incumbent': self.main, 'candidate': self.sha('loop/j-build/26')})
        self.assertEqual(manifest['holdout_dir'], str(self.holdout_dir))
        calls = self.calls()
        seen = [(self.condition_of(manifest, c), self.flag(c, '--model'), Path(c[2]).parent.name,
                 int(self.flag(c, '--runs'))) for c in calls]
        expected = []
        for case, runs in [(TARGET, 5)] + [(name, 3) for name in CONTROLS]:
            for model in ('opus', 'sonnet'):
                expected += [('incumbent', model, case, runs), ('candidate', model, case, runs)]
        expected += [('candidate', 'opus', HOLDOUT, 5), ('candidate', 'sonnet', HOLDOUT, 5)]
        self.assertEqual(seen, expected)
        planned = sorted((cond, model, case, runs) for model in ('opus', 'sonnet')
                         for cond, case, runs in gate.planned(manifest))
        self.assertEqual(sorted(seen), planned)
        self.assertTrue(all(self.flag(c, '--allow-tools', 3) == ['Write', 'Edit', 'Bash'] for c in calls))

        run_dir = Path(report['run_dir'])
        evals = {c: sorted(p.name for p in ((run_dir / path).parents[2] / 'evals').iterdir() if p.name != 'results')
                 for c, path in manifest['skill_md'].items()}
        self.assertEqual(evals['incumbent'], sorted([TARGET] + CONTROLS))
        self.assertEqual(evals['candidate'], sorted([TARGET, HOLDOUT] + CONTROLS))
        self.assertIn('FIXED', (run_dir / manifest['skill_md']['candidate']).read_text())
        self.assertNotIn('FIXED', (run_dir / manifest['skill_md']['incumbent']).read_text())
        self.assertFalse([p for p in run_dir.glob('plugin-*') if 'candidate' in p.name or 'incumbent' in p.name],
                         'plugin directory names must not reveal the condition')

        judges = report['judges']
        self.assertEqual(judges['traces'], report['decision']['runs'])
        index = json.loads((run_dir / 'judges' / 'index.json').read_text())
        self.assertEqual(len(index), judges['traces'])
        self.assertEqual({tuple(v) for v in index.values()}, {('case',)})
        key = json.loads(Path(judges['key']).read_text())
        self.assertEqual({v['condition'] for v in key.values()}, {'incumbent', 'candidate'})

    def test_second_attempt_runs_only_the_candidate_against_the_saved_incumbent(self):
        code, first = self.drive('gate', '--candidate', 'loop-weak')
        self.assertEqual(code, 0, first)
        self.assertEqual(first['decision']['outcome'], 'rejected')
        self.calls()
        code, second = self.drive('gate', '--reuse-incumbent-from', first['manifest'], attempt=2)
        self.assertEqual(code, 0, second)
        self.assertEqual(second['decision']['outcome'], 'accepted')
        self.assertTrue(second['decision']['incumbent_reused'])
        manifest = self.manifest(second)
        self.assertEqual({self.condition_of(manifest, c) for c in self.calls()}, {'candidate'})
        self.assertEqual(manifest['reuse_incumbent_from'], first['manifest'])
        self.assertEqual(manifest['revisions']['incumbent'], self.main)
        self.assertEqual({r['condition'] for r in manifest['results']}, {'candidate'})

    def test_reuse_is_refused_when_the_incumbent_differs_from_the_previous_attempt(self):
        _, first = self.drive('gate', '--candidate', 'loop-weak')
        self.calls()
        code, report = self.drive('gate', '--reuse-incumbent-from', first['manifest'], '--incumbent', 'loop-weak',
                                  attempt=2)
        self.assertEqual(code, 3)
        self.assertIn('incumbent differs', report['refused'])
        self.assertEqual(self.calls(), [])


class Refusals(DriverFixture):
    def refused(self, mode, *extra, **plan):
        code, report = self.drive(mode, *extra, **plan)
        self.assertEqual(code, 3, report)
        self.assertEqual(self.calls(), [])
        self.assertFalse(self.runs.exists() and any(self.runs.rglob('*.json')))
        return report['refused']

    def test_a_plan_the_runner_refused(self):
        self.assertIn('refused this step: Monthly cap', self.refused('reproduce', refused='Monthly cap reached'))

    def test_a_plan_for_another_step(self):
        self.assertIn('next step for #26 is reproduce, not gate', self.refused('gate', step='reproduce'))

    def test_the_kill_switch(self):
        (self.jstack / 'loop.disabled').write_text('')
        self.assertIn('kill switch', self.refused('reproduce'))

    def test_a_run_directory_inside_either_repository(self):
        self.assertIn('outside both', self.refused('reproduce', '--run-dir', str(self.jstack / 'runs')))
        self.assertIn('outside both', self.refused('reproduce', '--run-dir', str(ROOT / 'workspaces' / 'run')))
        self.assertFalse((ROOT / 'workspaces' / 'run').exists())

    def test_a_gate_without_its_holdout_and_a_reproduce_with_a_candidate(self):
        plan_file = self.root / 'plan.json'
        plan_file.write_text(json.dumps(self.plan('gate')))
        argv = [a for a in self.argv('gate', str(plan_file))]
        i = argv.index('--holdout-dir')
        del argv[i:i + 2]
        with redirect_stdout(io.StringIO()) as out, mock.patch.dict(os.environ, self.env):
            self.assertEqual(run.main(argv), 3)
        self.assertIn('--holdout-dir', json.loads(out.getvalue())['refused'])
        self.assertIn('incumbent alone', self.refused('reproduce', '--candidate', 'loop-weak'))


class Wrapper(unittest.TestCase):
    def test_claude_runs_inside_the_same_wrapper_and_flags_as_the_j_build_harness(self):
        script = (ROOT / 'harness' / 'j-build' / 'run_eval.sh').read_text().replace('\\\n', ' ')
        tokens = shlex.split(next(line for line in script.splitlines() if 'infisical' in line))
        end = tokens.index('claude') + 1
        self.assertEqual(tokens[:end], run.CLAUDE)
        self.assertEqual(tokens[end:end + 3], ['plugin', 'eval', '$target'])
        self.assertEqual(tokens[end + 3:end + 3 + len(FLAGS)], FLAGS)
        self.assertEqual(run.EVAL_FLAGS[:len(FLAGS)], FLAGS)


if __name__ == '__main__':
    unittest.main()
