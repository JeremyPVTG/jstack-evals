"""The retro loop experiment record: one decided run copied into harness/retro-loop/records/<finding>/.

Each test drives a real reproduce or gate step with the run driver's fakes (no paid runs), then records it and
checks the layout, the relative paths, the redacted home directory and that gate.py decides the copy the same way.
"""
import importlib.util
import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest import mock

from test_retro_run import CONTROLS, FAKE_CHECKER, HOLDOUT, TARGET, DriverFixture

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'harness' / 'retro-loop' / 'record.py'
spec = importlib.util.spec_from_file_location('retro_record', SCRIPT)
record = importlib.util.module_from_spec(spec)
spec.loader.exec_module(record)


class RecordFixture(DriverFixture):
    def setUp(self):
        super().setUp()
        shutil.copy(FAKE_CHECKER, self.case_dir / 'checker.py')
        shutil.copy(self.cases, self.case_dir / 'cases.json')
        (self.case_dir / 'FROZEN.md').write_text('Frozen by the eval author.\n')
        self.out = self.root / 'evals-records'
        self.ledger = self.root / 'ledger.json'
        self.ledger.write_text(json.dumps([{'finding': 26, 'step': 'freeze', 'usd': 0},
                                           {'finding': 26, 'step': 'reproduce', 'usd': 3.0, 'outcome': 'reproduced'}]))

    def step(self, mode, *extra, **plan):
        code, report = self.drive(mode, '--checker', str(self.case_dir / 'checker.py'), *extra,
                                  env={'HOME': str(self.root)}, **plan)
        self.assertEqual(code, 0, report)
        self.calls()
        return Path(report['run_dir'])

    def record(self, run_dir, *extra, holdout=False):
        argv = [str(run_dir), '--cases', str(self.case_dir), '--ledger', str(self.ledger), '--out', str(self.out)]
        argv += ['--holdout', str(self.holdout_dir)] if holdout else []
        out = io.StringIO()
        with redirect_stdout(out), mock.patch.dict(os.environ, {'HOME': str(self.root)}):
            code = record.main(argv + list(extra))
        return code, json.loads(out.getvalue())

    def tree(self):
        return sorted(str(p.relative_to(self.out)) for p in self.out.rglob('*') if p.is_file())


class ReproduceRecord(RecordFixture):
    def test_a_reproduce_record_holds_the_run_the_frozen_cases_and_the_ledger_but_no_holdout(self):
        run_dir = self.step('reproduce')
        code, report = self.record(run_dir)
        self.assertEqual(code, 0, report)
        freeze = report['freeze']
        run = f'26/runs/{run_dir.name}'
        cases = f'26/cases/{freeze}'
        expected = [f'{run}/{name}' for name in ('decision.json', 'ledger.json', 'manifest.json', 'skill-incumbent.md')]
        expected += [f'{run}/results/incumbent-{m}-{TARGET}.json' for m in ('opus', 'sonnet')]
        expected += [f'{run}/checker/incumbent-{m}-{TARGET}.json' for m in ('opus', 'sonnet')]
        expected += [f'{cases}/{name}' for name in ('FROZEN.md', 'cases.json', 'checker.py')]
        expected += [f'{cases}/{case}/{f}' for case in [TARGET] + CONTROLS
                     for f in ('fixture.sh', 'graders/status.md', 'prompt.md')]
        self.assertEqual(self.tree(), sorted(expected))
        self.assertFalse([p for p in self.tree() if HOLDOUT in p])
        self.assertEqual(report['rechecked'], [{'run': run_dir.name, 'outcome': 'reproduced'}])

        manifest = json.loads((self.out / run / 'manifest.json').read_text())
        self.assertEqual(manifest['case_dir'], f'../../cases/{freeze}')
        self.assertIsNone(manifest['holdout_dir'])
        self.assertEqual(manifest['skill_md'], {'incumbent': 'skill-incumbent.md', 'candidate': None})
        self.assertEqual(manifest['checker']['path'], f'../../cases/{freeze}/checker.py')
        self.assertEqual(json.loads((self.out / run / 'ledger.json').read_text())[-1]['outcome'], 'reproduced')

    def test_no_local_path_reaches_the_record(self):
        code, report = self.record(self.step('reproduce'))
        self.assertEqual(code, 0, report)
        for path in self.out.rglob('*'):
            if path.is_file():
                self.assertNotIn(str(self.root), path.read_text(), path)
        result = next((self.out / '26' / 'runs').glob('*/results/*.json'))
        self.assertIn('~/', result.read_text())

    def test_recording_again_changes_nothing_and_a_record_is_never_overwritten(self):
        run_dir = self.step('reproduce')
        self.record(run_dir)
        before = {p: p.read_bytes() for p in self.out.rglob('*') if p.is_file()}
        code, _ = self.record(run_dir)
        self.assertEqual(code, 0)
        self.assertEqual({p: p.read_bytes() for p in self.out.rglob('*') if p.is_file()}, before)
        self.ledger.write_text(json.dumps([{'finding': 26, 'step': 'spend', 'usd': 1.0}]))
        code, report = self.record(run_dir)
        self.assertEqual(code, 1)
        self.assertIn('append-only', report['error'])
        self.assertEqual({p: p.read_bytes() for p in self.out.rglob('*') if p.is_file()}, before)

    def test_the_holdout_never_joins_a_reproduce_record(self):
        code, report = self.record(self.step('reproduce'), holdout=True)
        self.assertEqual(code, 1)
        self.assertIn('gate', report['error'])
        self.assertFalse(self.out.exists())

    def test_cases_edited_after_the_run_are_refused(self):
        run_dir = self.step('reproduce')
        with open(self.case_dir / TARGET / 'prompt.md', 'a') as prompt:
            prompt.write('Edited after the run.\n')
        code, report = self.record(run_dir)
        self.assertEqual(code, 1)
        self.assertIn('not as recorded', report['error'])
        self.assertIn(TARGET, report['error'])
        self.assertFalse(self.out.exists())

    def test_a_step_rejected_for_a_changed_or_missing_case_is_still_recorded(self):
        with open(self.case_dir / CONTROLS[0] / 'prompt.md', 'a') as prompt:
            prompt.write('Also bump the version.\n')
        shutil.rmtree(self.case_dir / CONTROLS[1])
        run_dir = self.step('reproduce')
        code, report = self.record(run_dir)
        self.assertEqual(code, 0, report)
        self.assertEqual(report['rechecked'], [{'run': run_dir.name, 'outcome': 'rejected'}])
        cases = self.out / '26' / 'cases' / report['freeze']
        self.assertIn('bump the version', (cases / CONTROLS[0] / 'prompt.md').read_text())
        self.assertFalse((cases / CONTROLS[1]).exists())

    def test_a_ledger_extract_for_another_finding_is_refused(self):
        run_dir = self.step('reproduce')
        self.ledger.write_text(json.dumps([{'finding': 27, 'step': 'freeze', 'usd': 0}]))
        code, report = self.record(run_dir)
        self.assertEqual(code, 1)
        self.assertIn('#26', report['error'])


class GateRecord(RecordFixture):
    def test_a_gate_record_adds_the_holdout_and_both_skill_copies_and_decides_the_same(self):
        run_dir = self.step('gate')
        code, report = self.record(run_dir, holdout=True)
        self.assertEqual(code, 0, report)
        freeze = report['freeze']
        self.assertTrue((self.out / '26' / 'holdout' / freeze / HOLDOUT / 'prompt.md').is_file())
        run = self.out / '26' / 'runs' / run_dir.name
        self.assertIn('FIXED', (run / 'skill-candidate.md').read_text())
        manifest = json.loads((run / 'manifest.json').read_text())
        self.assertEqual(manifest['holdout_dir'], f'../../holdout/{freeze}')
        self.assertEqual(report['rechecked'], [{'run': run_dir.name, 'outcome': 'accepted'}])

    def test_a_gate_record_needs_the_holdout(self):
        code, report = self.record(self.step('gate'))
        self.assertEqual(code, 1)
        self.assertIn('--holdout', report['error'])

    def test_a_second_attempt_brings_the_incumbent_runs_it_reused(self):
        first = self.step('gate', '--candidate', 'loop-weak')
        second = self.step('gate', '--reuse-incumbent-from', str(first / 'manifest.json'), attempt=2)
        code, report = self.record(second, holdout=True)
        self.assertEqual(code, 0, report)
        runs = sorted(p.name for p in (self.out / '26' / 'runs').iterdir())
        self.assertEqual(runs, sorted([first.name, second.name]))
        manifest = json.loads((self.out / '26' / 'runs' / second.name / 'manifest.json').read_text())
        self.assertEqual(manifest['reuse_incumbent_from'], f'../{first.name}/manifest.json')
        self.assertFalse((self.out / '26' / 'runs' / first.name / 'ledger.json').exists())
        self.assertEqual([r['outcome'] for r in report['rechecked']], ['accepted', 'rejected'])
        # The first attempt's own record, made earlier or later, holds the same bytes, so the two merge cleanly.
        code, _ = self.record(first, holdout=True)
        self.assertEqual(code, 0)

    def test_the_command_line_prints_the_report(self):
        run_dir = self.step('reproduce')
        done = subprocess.run([sys.executable, str(SCRIPT), str(run_dir), '--cases', str(self.case_dir),
                               '--ledger', str(self.ledger), '--out', str(self.out)],
                              capture_output=True, text=True, env={**os.environ, 'HOME': str(self.root)})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)['rechecked'][0]['outcome'], 'reproduced')


if __name__ == '__main__':
    unittest.main()
