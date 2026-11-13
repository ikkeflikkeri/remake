import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import validate_suite

ROOT = Path(__file__).resolve().parent


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.suite = json.loads((ROOT / 'fixtures' / 'sample.json').read_text(encoding='utf-8'))

    def test_samples_are_valid_and_cover_both_kinds(self):
        self.assertEqual(validate_suite(self.suite), [])
        self.assertEqual({c['kind'] for c in self.suite['cases']}, {'routing', 'execution'})

    def test_version_and_unknown_fields_are_rejected(self):
        self.suite['schema_version'] = '2.0'
        self.suite['result'] = 'pass'
        errors = validate_suite(self.suite)
        self.assertTrue(any('schema_version' in e for e in errors))
        self.assertTrue(any('result' in e for e in errors))

    def test_duplicate_ids_and_missing_rubric_are_rejected(self):
        self.suite['cases'][1]['id'] = self.suite['cases'][0]['id']
        self.suite['cases'][0]['criteria'] = []
        errors = validate_suite(self.suite)
        self.assertTrue(any('duplicate' in e for e in errors))
        self.assertTrue(any('criteria' in e for e in errors))

    def test_routing_and_execution_expectations_are_distinct(self):
        case = self.suite['cases'][0]
        case['expected'] = {'deliverables': ['report']}
        self.assertTrue(any('expected' in e for e in validate_suite(self.suite)))

    def test_wrong_types_and_blank_text_are_rejected(self):
        self.suite['cases'][0]['prompt'] = '  '
        self.suite['cases'][1]['criteria'] = [True]
        self.assertGreaterEqual(len(validate_suite(self.suite)), 2)
        self.assertTrue(validate_suite(None))

    def test_cli_reports_invalid_json_and_failure_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            path.write_text('{', encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'validate.py'), str(path)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid', result.stderr.lower())

    def test_cli_success_is_only_validation(self):
        result = subprocess.run([sys.executable, str(ROOT / 'validate.py'), str(ROOT / 'fixtures' / 'sample.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('not run', result.stdout.lower())


if __name__ == '__main__':
    unittest.main()
