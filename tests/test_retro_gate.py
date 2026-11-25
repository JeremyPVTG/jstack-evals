"""The retro loop gate command, over small recorded result files.

Each test freezes the fixture cases, writes a manifest that points at copies
of recorded `claude plugin eval` result files, and checks the decision the
gate returns. Every run in the fixtures costs $0.50 (agent plus judge).
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'harness' / 'retro-loop' / 'gate.py'
FIXTURES = Path(__file__).resolve().parent / 'fixtures' / 'retro-loop'
spec = importlib.util.spec_from_file_location('retro_gate', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

TARGET, HOLDOUT, CONTROLS = 'stale-receipts', 'stale-receipts-reworded', ['fresh-receipts', 'one-stale-lens']
MODELS = ['opus', 'sonnet']
INCUMBENT_SHA, CANDIDATE_SHA = 'a' * 40, 'b' * 40


class GateFixture(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)
        self.cases = self.dir / 'cases'
        shutil.copytree(FIXTURES / 'cases', self.cases)
        self.copies = 0
        self.skill('incumbent', 1000)
        self.skill('candidate', 1080)

    def skill(self, condition, size):
        (self.dir / f'SKILL-{condition}.md').write_text('x' * size)

    def copy(self, kind, name):
        """Copy one recorded file next to the manifest, as a runner would save it."""
        self.copies += 1
        target = self.dir / 'runs' / f'{self.copies:02d}-{name}.json'
        target.parent.mkdir(exist_ok=True)
        shutil.copy(FIXTURES / kind / f'{name}.json', target)
        return str(target.relative_to(self.dir))

    def runs(self, condition, model, *names, checker=None):
        return [{'condition': condition, 'model': model, 'path': self.copy('results', name),
                 'checker': self.copy('checkers', checker) if checker and name.startswith('target') else None}
                for name in names]

    def incumbent(self, model, target='target-fail-0of5', controls='controls-pass-3of3'):
        return self.runs('incumbent', model, target, controls)

    def candidate(self, model, target='target-pass-5of5', holdout='holdout-pass-4of5',
                  controls='controls-pass-3of3', checker=None):
        return self.runs('candidate', model, target, holdout, controls, checker=checker)

    def freeze(self, name):
        return {'name': name, 'sha256': gate.case_hash(self.cases / name)}

    def manifest(self, results, file='manifest.json', mode='gate', **fields):
        body = {
            'mode': mode,
            'finding': 21,
            'owning_skill': 'j-build',
            'attempt': 1,
            'infra_retry_used': False,
            'models': MODELS,
            'revisions': {'incumbent': INCUMBENT_SHA, 'candidate': CANDIDATE_SHA if mode == 'gate' else None},
            'skill_md': {'incumbent': 'SKILL-incumbent.md',
                         'candidate': 'SKILL-candidate.md' if mode == 'gate' else None},
            'cases': {'target': self.freeze(TARGET), 'holdout': self.freeze(HOLDOUT),
                      'controls': [self.freeze(name) for name in CONTROLS]},
            'case_dir': 'cases',
            'results': results,
            'reuse_incumbent_from': None,
        }
        body.update(fields)
        path = self.dir / file
        path.write_text(json.dumps(body, indent=2))
        return path

    def full_gate(self, **per_model):
        """Incumbent and candidate runs for both models; per_model overrides one model's files."""
        results = []
        for model in MODELS:
            override = per_model.get(model, {})
            results += self.incumbent(model, **override.get('incumbent', {}))
            results += self.candidate(model, **override.get('candidate', {}))
        return results

    def decide(self, path):
        return gate.decide(path)


class GateDecision(GateFixture):
    def test_candidate_that_fixes_the_target_on_both_models_is_accepted(self):
        out = self.decide(self.manifest(self.full_gate()))
        self.assertEqual(out['outcome'], 'accepted')
        self.assertEqual(out['mode'], 'gate')
        for model in MODELS:
            self.assertEqual(
                {k: out['per_model'][model][k] for k in
                 ('target_candidate', 'target_incumbent', 'holdout', 'max_control_drop', 'critical', 'pass')},
                {'target_candidate': '5/5', 'target_incumbent': '0/5', 'holdout': '4/5',
                 'max_control_drop': 0, 'critical': 0, 'pass': True})
        self.assertEqual(out['skill_growth_pct'], 8.0)
        self.assertEqual(out['runs'], 54)
        self.assertAlmostEqual(out['cost_usd'], 27.0)
        self.assertFalse(out['infra_retry_used'])
        self.assertTrue(out['reasons'])

    def test_case_edited_after_freezing_is_rejected_whatever_the_scores(self):
        path = self.manifest(self.full_gate())
        with open(self.cases / TARGET / 'graders' / 'status.md', 'a') as grader:
            grader.write('|Status: complete\n')
        out = self.decide(path)
        self.assertEqual(out['outcome'], 'rejected')
        self.assertIn(TARGET, out['reasons'][0])
        self.assertIn('changed after freezing', out['reasons'][0])

    def test_case_deleted_after_freezing_is_rejected(self):
        path = self.manifest(self.full_gate())
        shutil.rmtree(self.cases / 'one-stale-lens')
        out = self.decide(path)
        self.assertEqual(out['outcome'], 'rejected')
        self.assertIn('one-stale-lens is missing', out['reasons'][0])

    def test_first_infrastructure_fault_asks_for_a_retry_that_uses_no_attempt(self):
        # opus candidate target: two runs hit API errors (2 of 5 not graded)
        results = self.full_gate(opus={'candidate': {'target': 'target-infra-2of5'}})
        out = self.decide(self.manifest(results))
        self.assertEqual(out['outcome'], 'retry')
        self.assertTrue(out['infra_retry_used'])
        self.assertIn('opus candidate stale-receipts: 2 of 5', out['reasons'][0])

    def test_second_infrastructure_fault_in_the_same_attempt_is_inconclusive(self):
        results = self.full_gate(opus={'candidate': {'target': 'target-infra-2of5'}})
        out = self.decide(self.manifest(results, infra_retry_used=True))
        self.assertEqual(out['outcome'], 'inconclusive')
        self.assertTrue(out['infra_retry_used'])
        self.assertIn('Second infrastructure fault', out['reasons'][0])

    def break_one_run(self, results, condition, model, file_prefix, error='exit 1: API Error: 529 Overloaded',
                      case_index=0):
        entry = next(r for r in results if r['condition'] == condition and r['model'] == model
                     and Path(r['path']).name[3:].startswith(file_prefix))
        path = self.dir / entry['path']
        data = json.loads(path.read_text())
        data['cases'][case_index]['arms']['with'][0].update(passed=False, error=error, graders=[])
        path.write_text(json.dumps(data))

    def test_one_ungraded_run_in_a_target_or_holdout_case_is_an_infrastructure_fault(self):
        for condition, prefix, case in (('candidate', 'target', TARGET), ('incumbent', 'target', TARGET),
                                        ('candidate', 'holdout', 'soft holdout')):
            with self.subTest(f'{condition} {prefix}'):
                results = self.full_gate()
                self.break_one_run(results, condition, 'sonnet', prefix)
                out = self.decide(self.manifest(results, file=f'{condition}-{prefix}.json'))
                self.assertEqual(out['outcome'], 'retry')
                self.assertTrue(out['infra_retry_used'])
                self.assertIn(f'sonnet {condition} {case}: 1 of 5', out['reasons'][0])

    def test_one_ungraded_run_in_a_reproduce_target_is_an_infrastructure_fault(self):
        results = self.runs('incumbent', 'opus', 'reproduce-fail-1of3') + self.runs('incumbent', 'sonnet',
                                                                                    'reproduce-fail-1of3')
        self.break_one_run(results, 'incumbent', 'opus', 'reproduce')
        out = self.decide(self.manifest(results, mode='reproduce'))
        self.assertEqual(out['outcome'], 'retry')
        self.assertIn(f'opus incumbent {TARGET}: 1 of 3', out['reasons'][0])

    def test_one_ungraded_control_run_of_three_is_not_an_infrastructure_fault(self):
        results = self.full_gate()
        self.break_one_run(results, 'candidate', 'opus', 'controls')
        out = self.decide(self.manifest(results))
        self.assertEqual(out['outcome'], 'accepted')
        self.assertFalse(out['infra_retry_used'])
        self.assertEqual(out['per_model']['opus']['max_control_drop'], 1)

    def test_turn_limit_and_timeout_are_task_failures_not_infrastructure(self):
        results = self.full_gate()
        entry = next(r for r in results if r['condition'] == 'candidate' and r['model'] == 'opus'
                     and 'target' in r['path'])
        path = self.dir / entry['path']
        data = json.loads(path.read_text())
        runs = data['cases'][0]['arms']['with']
        for run, error in zip(runs, ['Reached maximum number of turns (40)', 'Run timed out after 600s']):
            run.update(passed=False, error=error, graders=[])
        path.write_text(json.dumps(data))
        out = self.decide(self.manifest(results))
        self.assertEqual(out['outcome'], 'inconclusive')
        self.assertFalse(out['infra_retry_used'])
        self.assertEqual(out['per_model']['opus']['target_candidate'], '3/5')

    def test_skill_md_growth_above_twenty_percent_is_rejected(self):
        self.skill('candidate', 1201)
        out = self.decide(self.manifest(self.full_gate()))
        self.assertEqual(out['outcome'], 'rejected')
        self.assertEqual(out['skill_growth_pct'], 20.1)
        self.assertIn('SKILL.md grew 20.1%', out['reasons'][0])

    def test_skill_md_growth_of_exactly_twenty_percent_is_allowed(self):
        self.skill('candidate', 1200)
        self.assertEqual(self.decide(self.manifest(self.full_gate()))['outcome'], 'accepted')

    def test_critical_failure_on_one_model_rejects_rather_than_disagrees(self):
        # The checker fails one opus target run the harness passed, and marks it critical.
        results = self.full_gate(opus={'candidate': {'checker': 'target-critical'}})
        out = self.decide(self.manifest(results))
        self.assertEqual(out['outcome'], 'rejected')
        self.assertEqual(out['per_model']['opus']['critical'], 1)
        self.assertEqual(out['per_model']['opus']['target_candidate'], '4/5')
        self.assertTrue(out['per_model']['sonnet']['pass'])
        self.assertIn('opus: 1 critical failure(s) in candidate runs.', out['reasons'])
        self.assertTrue(any('without rerunning' in n for n in out['per_model']['opus']['critical_notes']))

    def test_control_dropping_two_runs_of_three_on_one_model_rejects(self):
        results = self.full_gate(sonnet={'candidate': {'controls': 'controls-drop-1of3'}})
        out = self.decide(self.manifest(results))
        self.assertEqual(out['outcome'], 'rejected')
        self.assertEqual(out['per_model']['sonnet']['max_control_drop'], 2)
        self.assertIn('sonnet: control fresh-receipts dropped from 3/3 to 1/3', ' '.join(out['reasons']))

    def test_control_dipping_one_run_of_three_is_allowed(self):
        results = self.full_gate(sonnet={'candidate': {'controls': 'controls-dip-2of3'}})
        out = self.decide(self.manifest(results))
        self.assertEqual(out['outcome'], 'accepted')
        self.assertEqual(out['per_model']['sonnet']['max_control_drop'], 1)

    def test_target_miss_on_one_model_is_inconclusive(self):
        results = self.full_gate(sonnet={'candidate': {'target': 'target-pass-4of5'}})
        out = self.decide(self.manifest(results))
        self.assertEqual(out['outcome'], 'inconclusive')
        self.assertEqual([out['per_model'][m]['pass'] for m in MODELS], [True, False])
        self.assertIn('Models disagree', out['reasons'][0])
        self.assertIn('sonnet: candidate passed the target 4/5, needs 5/5', out['reasons'][0])

    def test_holdout_miss_on_both_models_is_rejected(self):
        miss = {'candidate': {'holdout': 'holdout-fail-2of5'}}
        out = self.decide(self.manifest(self.full_gate(opus=miss, sonnet=miss)))
        self.assertEqual(out['outcome'], 'rejected')
        self.assertEqual(out['reasons'], ['opus: soft holdout not passed.', 'sonnet: soft holdout not passed.'])
        self.assertEqual([out['per_model'][m]['holdout'] for m in MODELS], ['2/5', '2/5'])

    def test_incumbent_above_one_of_five_is_baseline_drift_and_fails_that_model(self):
        drift = {'incumbent': {'target': 'target-drift-2of5'}}
        one = self.decide(self.manifest(self.full_gate(opus=drift)))
        self.assertEqual(one['outcome'], 'inconclusive')
        self.assertEqual(one['per_model']['opus']['target_incumbent'], '2/5')
        self.assertIn('opus: incumbent passed the target 2/5 (baseline drifted)', one['reasons'][0])
        both = self.decide(self.manifest(self.full_gate(opus=drift, sonnet=drift), file='both.json'))
        self.assertEqual(both['outcome'], 'rejected')


class PublicReasons(GateFixture):
    """The runner posts reasons on the public finding, which the implementer could read: no assertion text there.

    Checker notes, holdout scores, the holdout's name and local paths stay in per_model and the manifest.
    """

    def assert_public(self, out):
        text = ' '.join(out['reasons'])
        self.assertNotIn(HOLDOUT, text)
        self.assertNotIn(str(self.dir), text)
        self.assertNotRegex(text, r'holdout \d/\d')
        for note in ('rerunning the lens', 'receipts rerun at HEAD'):
            self.assertNotIn(note, text)

    def test_a_critical_failure_reason_leaves_out_the_checker_note(self):
        out = self.decide(self.manifest(self.full_gate(opus={'candidate': {'checker': 'target-critical'}})))
        self.assertEqual(out['outcome'], 'rejected')
        self.assert_public(out)

    def test_holdout_misses_and_faults_leave_out_its_scores_and_name(self):
        miss = {'candidate': {'holdout': 'holdout-fail-2of5'}}
        self.assert_public(self.decide(self.manifest(self.full_gate(opus=miss), file='miss.json')))
        results = self.full_gate()
        holdout = next(r for r in results if r['condition'] == 'candidate' and 'holdout' in r['path'])
        data = json.loads((self.dir / holdout['path']).read_text())
        data['cases'][0]['arms']['with'][0].update(error='exit 1: API Error: 529 Overloaded', graders=[])
        (self.dir / holdout['path']).write_text(json.dumps(data))
        out = self.decide(self.manifest(results, file='fault.json'))
        self.assertEqual(out['outcome'], 'retry')
        self.assertIn('soft holdout', out['reasons'][0])
        self.assert_public(out)

    def test_a_changed_or_missing_holdout_is_named_by_role(self):
        path = self.manifest(self.full_gate(), holdout_dir=str(self.dir / 'holdout'))
        (self.dir / 'holdout').mkdir()
        out = self.decide(path)
        self.assertIn('soft holdout is missing', out['reasons'][0])
        self.assert_public(out)
        shutil.copytree(self.cases / HOLDOUT, self.dir / 'holdout' / HOLDOUT)
        with open(self.dir / 'holdout' / HOLDOUT / 'prompt.md', 'a') as prompt:
            prompt.write('Status: complete is fine.\n')
        out = self.decide(path)
        self.assertIn('soft holdout changed after freezing', out['reasons'][0])
        self.assert_public(out)


class NoModelJudges(GateFixture):
    """Claude models never judge: a result graded by a model makes the manifest malformed."""

    def edit_first(self, results, edit):
        path = self.dir / results[0]['path']
        data = json.loads(path.read_text())
        edit(data['cases'][0])
        path.write_text(json.dumps(data))

    def test_an_llm_or_baseline_grader_is_refused(self):
        for kind in ('llm', 'baseline'):
            with self.subTest(kind):
                results = self.full_gate()
                self.edit_first(results, lambda case: case['graders'].append(
                    {'name': 'judge', 'type': kind, 'weight': 1, 'config': {'criteria': 'PASS if correct.'}}))
                with self.assertRaisesRegex(gate.ManifestError, kind):
                    self.decide(self.manifest(results, file=f'{kind}.json'))

    def test_a_run_with_a_judge_cost_is_refused(self):
        results = self.full_gate()
        self.edit_first(results, lambda case: case['arms']['with'][0].update(judgeCostUsd=0.05))
        with self.assertRaisesRegex(gate.ManifestError, 'judgeCostUsd'):
            self.decide(self.manifest(results))

    def test_reused_incumbent_runs_are_checked_too(self):
        first = self.full_gate()
        self.edit_first(first, lambda case: case['arms']['with'][0].update(judgeCostUsd=0.05))
        self.manifest(first, file='attempt-1.json')
        second = self.candidate('opus') + self.candidate('sonnet')
        with self.assertRaisesRegex(gate.ManifestError, 'judgeCostUsd'):
            self.decide(self.manifest(second, file='attempt-2.json', attempt=2, reuse_incumbent_from='attempt-1.json'))

    def test_the_command_exits_2_on_a_model_judged_manifest(self):
        results = self.full_gate()
        self.edit_first(results, lambda case: case['graders'].append({'name': 'judge', 'type': 'llm', 'weight': 1}))
        done = subprocess.run([sys.executable, str(SCRIPT), 'decide', str(self.manifest(results))],
                              capture_output=True, text=True)
        self.assertEqual((done.returncode, done.stdout), (2, ''))
        self.assertIn('llm', done.stderr)


class IncumbentReuse(GateFixture):
    def first_attempt(self):
        miss = {'candidate': {'holdout': 'holdout-fail-2of5'}}
        return self.manifest(self.full_gate(opus=miss, sonnet=miss), file='attempt-1.json')

    def second_attempt(self, **fields):
        results = self.candidate('opus') + self.candidate('sonnet')
        return self.manifest(results, file='attempt-2.json', attempt=2,
                             reuse_incumbent_from='attempt-1.json', **fields)

    def test_second_attempt_uses_the_stored_incumbent_runs_and_counts_only_new_runs(self):
        self.first_attempt()
        out = self.decide(self.second_attempt())
        self.assertEqual(out['outcome'], 'accepted')
        self.assertEqual(out['per_model']['opus']['target_incumbent'], '0/5')
        self.assertEqual(out['per_model']['sonnet']['max_control_drop'], 0)
        self.assertTrue(out['incumbent_reused'])
        self.assertEqual(out['runs'], 32)
        self.assertAlmostEqual(out['cost_usd'], 16.0)
        self.assertEqual(out['reused_runs'], 22)

    def test_reuse_is_refused_when_a_frozen_case_changed_since_the_previous_attempt(self):
        self.first_attempt()
        with open(self.cases / 'fresh-receipts' / 'prompt.md', 'a') as prompt:
            prompt.write('Also bump the version.\n')
        out = self.decide(self.second_attempt())  # frozen again with the edited case
        self.assertEqual(out['outcome'], 'rejected')
        self.assertFalse(out['incumbent_reused'])
        self.assertIn('fresh-receipts changed since the previous attempt', ' '.join(out['reasons']))

    def test_reuse_is_refused_when_the_incumbent_commit_changed(self):
        self.first_attempt()
        path = self.second_attempt(revisions={'incumbent': 'c' * 40, 'candidate': CANDIDATE_SHA})
        with self.assertRaisesRegex(gate.ManifestError, 'incumbent commit changed'):
            self.decide(path)


class Reproduce(GateFixture):
    def reproduce(self, opus, sonnet):
        results = self.runs('incumbent', 'opus', opus) + self.runs('incumbent', 'sonnet', sonnet)
        return self.decide(self.manifest(results, mode='reproduce'))

    def test_failure_is_reproduced_when_the_incumbent_fails_on_every_model(self):
        out = self.reproduce('reproduce-fail-1of3', 'reproduce-fail-1of3')
        self.assertEqual(out['outcome'], 'reproduced')
        self.assertEqual(out['mode'], 'reproduce')
        self.assertEqual(out['per_model'], {
            'opus': {'target_incumbent': '1/3', 'reproduced': True},
            'sonnet': {'target_incumbent': '1/3', 'reproduced': True}})
        self.assertIsNone(out['skill_growth_pct'])
        self.assertEqual(out['runs'], 6)
        self.assertAlmostEqual(out['cost_usd'], 3.0)

    def test_two_of_three_passes_on_any_model_means_not_reproduced(self):
        out = self.reproduce('reproduce-pass-2of3', 'reproduce-fail-1of3')
        self.assertEqual(out['outcome'], 'not_reproduced')
        self.assertFalse(out['per_model']['opus']['reproduced'])
        self.assertTrue(out['per_model']['sonnet']['reproduced'])
        self.assertIn('opus (2/3)', out['reasons'][0])


class HoldoutDir(GateFixture):
    """The soft holdout lives apart from the other cases, out of the implementer's reach."""

    def move_holdout(self):
        (self.dir / 'holdout').mkdir()
        shutil.move(str(self.cases / HOLDOUT), str(self.dir / 'holdout' / HOLDOUT))

    def reproduce_runs(self):
        return self.runs('incumbent', 'opus', 'reproduce-fail-1of3') + self.runs('incumbent', 'sonnet', 'reproduce-fail-1of3')

    def test_gate_rechecks_the_holdout_under_holdout_dir(self):
        path = self.manifest(self.full_gate(), holdout_dir='holdout')
        self.move_holdout()
        self.assertEqual(self.decide(path)['outcome'], 'accepted')

    def test_holdout_changed_in_holdout_dir_is_rejected(self):
        path = self.manifest(self.full_gate(), holdout_dir='holdout')
        self.move_holdout()
        with open(self.dir / 'holdout' / HOLDOUT / 'prompt.md', 'a') as prompt:
            prompt.write('Status: complete is fine.\n')
        out = self.decide(path)
        self.assertEqual(out['outcome'], 'rejected')
        self.assertIn('The soft holdout changed after freezing', out['reasons'][0])

    def test_without_holdout_dir_the_holdout_is_looked_for_under_case_dir(self):
        path = self.manifest(self.full_gate())
        self.move_holdout()
        out = self.decide(path)
        self.assertEqual(out['outcome'], 'rejected')
        self.assertIn('The soft holdout is missing from the case directory', out['reasons'][0])

    def test_reproduce_needs_no_holdout_anywhere(self):
        path = self.manifest(self.reproduce_runs(), mode='reproduce')  # names the holdout, as the frozen cases do
        shutil.rmtree(self.cases / HOLDOUT)
        self.assertEqual(self.decide(path)['outcome'], 'reproduced')

    def test_reproduce_still_rechecks_the_controls(self):
        path = self.manifest(self.reproduce_runs(), mode='reproduce', holdout_dir='no-such-dir')
        with open(self.cases / 'fresh-receipts' / 'prompt.md', 'a') as prompt:
            prompt.write('Also bump the version.\n')
        out = self.decide(path)
        self.assertEqual(out['outcome'], 'rejected')
        self.assertIn('fresh-receipts changed after freezing', out['reasons'][0])

    def test_gate_with_a_holdout_dir_that_is_not_a_directory_is_malformed(self):
        with self.assertRaisesRegex(gate.ManifestError, 'holdout_dir'):
            self.decide(self.manifest(self.full_gate(), holdout_dir='no-such-dir'))


class Command(GateFixture):
    def run_gate(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)

    def test_decide_prints_one_json_decision_and_exits_zero(self):
        done = self.run_gate('decide', self.manifest(self.full_gate()))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)['outcome'], 'accepted')

    def test_decide_exits_nonzero_with_nothing_on_stdout_for_a_malformed_manifest(self):
        done = self.run_gate('decide', self.manifest(self.full_gate(), mode='promote'))
        self.assertNotEqual(done.returncode, 0)
        self.assertEqual(done.stdout, '')
        self.assertIn('mode', done.stderr)

    def test_hash_prints_the_sha256_the_gate_rechecks(self):
        done = self.run_gate('hash', self.cases / TARGET)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout.strip(), gate.case_hash(self.cases / TARGET))

    def test_malformed_manifests_are_refused(self):
        target_twice = self.full_gate() + self.runs('candidate', 'opus', 'target-pass-5of5')
        bad_checker = self.full_gate()  # [-3] is the sonnet candidate target: 3 runs against 5 checker entries
        bad_checker[-3].update(path=self.copy('results', 'reproduce-fail-1of3'),
                               checker=self.copy('checkers', 'target-critical'))
        cases = {
            'gate without a holdout': (self.full_gate(), {'cases': {'target': self.freeze(TARGET), 'controls': []}}),
            'result for a model not in the manifest': (self.full_gate() + self.runs('candidate', 'haiku', 'target-pass-5of5'), {}),
            'candidate result in reproduce mode': (self.full_gate(), {'mode': 'reproduce'}),
            'missing result file': ([dict(self.full_gate()[0], path='runs/none.json')] + self.full_gate()[1:], {}),
            'missing case directory': (self.full_gate(), {'case_dir': 'no-cases'}),
            'more runs than planned': (target_twice, {}),
            'checker entries that do not match the runs': (bad_checker, {}),
            'reuse in reproduce mode': (self.runs('incumbent', 'opus', 'reproduce-fail-1of3'),
                                        {'mode': 'reproduce', 'reuse_incumbent_from': 'manifest.json'}),
        }
        for i, (name, (results, fields)) in enumerate(cases.items()):
            with self.subTest(name):
                with self.assertRaises(gate.ManifestError):
                    self.decide(self.manifest(results, file=f'malformed-{i}.json', **fields))


class CaseHash(unittest.TestCase):
    def test_hash_covers_files_by_relative_path_and_skips_results_and_pycache(self):
        with tempfile.TemporaryDirectory() as temp:
            case = Path(temp)
            (case / 'sub' / 'results').mkdir(parents=True)
            (case / '__pycache__').mkdir()
            (case / 'a.txt').write_text('x')
            (case / 'sub' / 'b.txt').write_text('y')
            (case / 'sub' / 'results' / 'run.json').write_text('{}')
            (case / '__pycache__' / 'c.pyc').write_text('cache')
            # printf 'a.txt\0x\0sub/b.txt\0y\0' | shasum -a 256
            expected = '052e7ec91c38c2224809ba91adeb47bd42870f97a8db4d768614244afebe98a6'
            self.assertEqual(gate.case_hash(case), expected)


if __name__ == '__main__':
    unittest.main()
