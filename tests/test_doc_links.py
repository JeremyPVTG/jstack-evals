"""Fail when a doc points to a file that does not exist.

Checks every tracked Markdown file except saved run output (anything under a
`results/` directory), eval fixtures (`harness/<skill>/source/`, which copy
another repository's files, so their links point into that repository) and
retro loop experiment records (`harness/retro-loop/records/`, verbatim copies
of a skill's SKILL.md and frozen cases whose links point into jstack).

Two kinds of reference are checked:
- relative Markdown links, `[text](path)`;
- paths that go through `results/` or `subjects/`, written in prose or code
  spans, such as `harness/j-build/results/staged-*.json`. They resolve from the
  doc's own directory or from the repository root; globs and `{a,b}` braces
  must match at least one file. A bare `results/` naming the directory in
  general, and placeholders such as `<skill>`, are not file references.
"""
import glob
import re
import subprocess
import unittest
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LINK = re.compile(r'\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
DATA_PATH = re.compile(r'(?<![\w./{}*-])((?:\.{1,2}/)?(?:[\w.@+*{},-]+/)*(?:results|subjects)/[\w.@+/*{},-]*)')
SCHEME = re.compile(r'^[a-z][a-z0-9+.-]*:', re.I)


def tracked_docs(root):
    out = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z', '*.md'], text=True)
    for name in filter(None, out.split('\0')):
        parts = Path(name).parts
        if 'results' in parts[:-1]:
            continue
        if len(parts) > 2 and parts[0] == 'harness' and parts[2] in ('source', 'records'):
            continue
        yield root / name


def expand_braces(pattern):
    match = re.search(r'\{([^{}]*)\}', pattern)
    if not match:
        return [pattern]
    head, tail = pattern[:match.start()], pattern[match.end():]
    return [p for option in match.group(1).split(',') for p in expand_braces(head + option + tail)]


def exists(base, reference):
    for pattern in expand_braces(reference):
        if any(ch in pattern for ch in '*?['):
            if glob.glob(str(base / pattern)):
                return True
        elif (base / pattern).exists():
            return True
    return False


def broken_references(doc, root):
    """Each broken reference in one doc, as 'path:line: reference'."""
    problems = []
    rel = doc.relative_to(root).as_posix()
    for number, line in enumerate(doc.read_text(encoding='utf-8').splitlines(), 1):
        for target in LINK.findall(line):
            if SCHEME.match(target) or target.startswith('#'):
                continue
            path = urllib.parse.unquote(target.split('#')[0].split('?')[0])
            if not path:
                continue
            base = root if path.startswith('/') else doc.parent
            if not exists(base, path.lstrip('/')):
                problems.append(f'{rel}:{number}: link {target}')
        for reference in DATA_PATH.findall(line):
            reference = reference.rstrip('.,;:')
            if '<' in reference or re.fullmatch(r'(?:\./)?(?:results|subjects)/', reference):
                continue
            if not (exists(doc.parent, reference) or exists(root, reference)):
                problems.append(f'{rel}:{number}: path {reference}')
    return problems


class DocLinks(unittest.TestCase):
    def test_docs_point_to_files_that_exist(self):
        problems = [p for doc in tracked_docs(ROOT) for p in broken_references(doc, ROOT)]
        self.assertEqual(problems, [], '\n'.join(problems))


class Checker(unittest.TestCase):
    """The checker itself, on a throwaway repository."""

    def setUp(self):
        import tempfile

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'docs').mkdir()
        (self.root / 'docs' / 'real.md').write_text('# Real\n')
        (self.root / 'harness' / 'x' / 'results').mkdir(parents=True)
        (self.root / 'harness' / 'x' / 'results' / 'full-new.json').write_text('{}')
        (self.root / 'harness' / 'x' / 'results' / 'full-old.json').write_text('{}')
        (self.root / 'subjects').mkdir()
        (self.root / 'subjects' / 'jstack.json').write_text('{}')

    def check(self, text, where='docs/page.md'):
        doc = self.root / where
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text(text)
        return broken_references(doc, self.root)

    def test_good_references_pass(self):
        self.assertEqual(self.check(
            '[real](real.md) [anchor](real.md#top) [web](https://example.com) [here](#x)\n'
            'Saved in `harness/x/results/full-new.json` and harness/x/results/full-*.json.\n'
            'Pins: subjects/jstack.json. Layout: `results/` holds output; `harness/<skill>/results/`.\n'
        ), [])

    def test_doc_relative_and_brace_paths(self):
        self.assertEqual(self.check('Sources: `results/full-{new,old}.json`.\n', 'harness/x/RESULTS.md'), [])

    def test_broken_link_fails(self):
        self.assertEqual(self.check('[gone](missing.md)\n'), ['docs/page.md:1: link missing.md'])

    def test_broken_data_paths_fail(self):
        self.assertEqual(self.check(
            'See harness/x/results/full-none.json.\n'
            'And `harness/x/results/staged-*.json`, `results/full-{new,gone}.json`, subjects/old.json\n'
        ), [
            'docs/page.md:1: path harness/x/results/full-none.json',
            'docs/page.md:2: path harness/x/results/staged-*.json',
            'docs/page.md:2: path results/full-{new,gone}.json',
            'docs/page.md:2: path subjects/old.json',
        ])


if __name__ == '__main__':
    unittest.main()
