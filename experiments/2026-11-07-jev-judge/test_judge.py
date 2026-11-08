from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parent / 'judge.py'
spec = importlib.util.spec_from_file_location('judge', SCRIPT)
judge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(judge)


def answers(relevant=0.9, evidence=0.9, contradicts=0.1, injection=0.05):
    return {'relevant': relevant, 'evidence': evidence, 'contradicts': contradicts, 'injection': injection}


class JudgeTest(unittest.TestCase):
    def test_labels_follow_the_threshold_table(self):
        self.assertEqual(judge.label(answers()), 'evidence')
        self.assertEqual(judge.label(answers(injection=0.8)), 'drop')
        self.assertEqual(judge.label(answers(relevant=0.3)), 'drop')
        self.assertEqual(judge.label(answers(contradicts=0.8, evidence=0.2)), 'conflict')
        self.assertEqual(judge.label(answers(evidence=0.4)), 'unsettled')
        self.assertEqual(judge.label(answers(evidence=0.1)), 'drop')

    def test_state_is_short_and_names_the_site(self):
        s = judge.state('q', {'url': 'https://docs.example.com/a', 'title': 'T', 'text': 'word ' * 1000})
        self.assertEqual(s['passage']['site'], 'docs.example.com')
        self.assertLessEqual(len(s['passage']['text']), judge.MAX_TEXT)
        self.assertEqual(s['passage']['published'], 'unknown')

    def test_orders_evidence_first_and_sends_pinned_model(self):
        sent = []
        replies = {'a': answers(evidence=0.6), 'b': answers(relevant=0.1), 'c': answers(evidence=0.95)}
        def fake(payload, key):
            sent.append(payload)
            return {**replies[payload['state']['passage']['title']], 'input_tokens': 100}
        rows = judge.judge('q', [{'title': t, 'url': f'https://{t}.dev'} for t in 'abc'], 'k', ask=fake)
        self.assertEqual([r['title'] for r in rows], ['c', 'a', 'b'])
        self.assertEqual({p['model'] for p in sent}, {'jev-1.14.0'})
        self.assertEqual(set(sent[0]['questions']), {'relevant', 'evidence', 'contradicts', 'injection'})

    def test_cache_hit_skips_the_network_and_reports_no_new_tokens(self):
        cache = Path(tempfile.mkdtemp())
        reply = {'answers': {k: {'type': 'noul', 'noul': 0.5} for k in judge.QUESTIONS}, 'usage': {'input_tokens': 321}}
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(reply).encode()
        payload = {'model': judge.MODEL, 'state': {'query': 'q'}, 'questions': judge.QUESTIONS}
        with mock.patch.object(judge.urllib.request, 'urlopen', return_value=response) as urlopen:
            first = judge.ask(payload, 'k', cache)
            second = judge.ask(payload, 'k', cache)
        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual((first['input_tokens'], second['input_tokens']), (321, 0))


if __name__ == '__main__':
    unittest.main()
