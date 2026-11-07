import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'subject.py'
spec = importlib.util.spec_from_file_location('subject', SCRIPT)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


class SubjectPins(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git('init', '-q')
        (self.repo / 'skills').mkdir()
        (self.repo / 'skills' / 'sample.md').write_text('original')
        (self.repo / 'packs.json').write_text('{}')
        self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', *args], stderr=subprocess.PIPE)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')

    def test_exact_clean_subject_verifies(self):
        pin = subject.snapshot(self.repo)
        self.assertEqual(len(pin['commit']), 40)
        self.assertEqual(len(pin['files_sha256']['packs.json']), 64)
        subject.verify(self.repo, pin)
        self.assertNotIn(str(self.repo), json.dumps(pin))

    def test_dirty_and_untracked_rejected(self):
        (self.repo / 'extra').write_text('untracked')
        with self.assertRaises(ValueError):
            subject.snapshot(self.repo)
        (self.repo / 'extra').unlink()
        (self.repo / 'packs.json').write_text('{"changed":true}')
        with self.assertRaises(ValueError):
            subject.snapshot(self.repo)

    def test_new_commit_does_not_match(self):
        pin = subject.snapshot(self.repo)
        (self.repo / 'packs.json').write_text('{"changed":true}')
        self.commit()
        with self.assertRaises(ValueError):
            subject.verify(self.repo, pin)

    def test_tampered_hash_does_not_match(self):
        pin = subject.snapshot(self.repo)
        pin['files_sha256']['packs.json'] = '0' * 64
        with self.assertRaises(ValueError):
            subject.verify(self.repo, pin)


if __name__ == '__main__':
    unittest.main()
