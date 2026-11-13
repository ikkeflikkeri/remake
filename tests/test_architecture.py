import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.workflow import initial, save, transition

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'verify_architecture.py'

class ArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.recon = {'reference': 'ref', 'target': 'web', 'scope': 'Public pages',
                      'observations': ['Home page'], 'unknowns': ['Private pages'], 'sources': ['ref']}
        self.recon_path = self.root / 'recon.json'
        self.recon_path.write_text(json.dumps(self.recon), encoding='utf-8')
        state = transition(initial('ref', 'web'), 'recon', 'in_progress')
        state = transition(state, 'recon', 'completed', 'recon.json')
        self.state_path = self.root / 'workflow.json'
        save(self.state_path, state)
        self.data = {'version': 1, 'reference': 'ref', 'target': 'web',
                     'recon_evidence': 'recon.json',
                     'recon_sha256': hashlib.sha256(self.recon_path.read_bytes()).hexdigest(),
                     **{key: [key + ' detail'] for key in ('requirements', 'components', 'interfaces',
                         'decisions', 'risks', 'unknowns', 'evidence', 'assumptions', 'limitations')}}
        self.artifact = self.root / 'architecture.json'

    def run_verify(self):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.artifact), '--workflow',
                               str(self.state_path)], cwd=self.root, capture_output=True, text=True)

    def write(self):
        self.artifact.write_text(json.dumps(self.data), encoding='utf-8')

    def test_valid(self):
        self.write()
        result = self.run_verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('sha256:', result.stdout)

    def test_invalid_fields_and_identity(self):
        for key, value in [('version', True), ('version', 2), ('reference', 'other'),
                           ('target', 'other'), ('requirements', []), ('components', [' ']),
                           ('interfaces', [3]), ('decisions', None), ('risks', []),
                           ('unknowns', []), ('evidence', []), ('assumptions', []),
                           ('limitations', []), ('recon_sha256', '0' * 64),
                           ('recon_sha256', None), ('recon_evidence', './recon.json')]:
            with self.subTest(key=key, value=value):
                original = self.data[key]
                self.data[key] = value
                self.write()
                self.assertEqual(self.run_verify().returncode, 2)
                self.data[key] = original
        del self.data['risks']
        self.write()
        self.assertEqual(self.run_verify().returncode, 2)

    def test_recon_must_be_completed_and_valid(self):
        self.write()
        save(self.state_path, initial('ref', 'web'))
        self.assertEqual(self.run_verify().returncode, 2)
        state = transition(initial('ref', 'web'), 'recon', 'in_progress')
        save(self.state_path, transition(state, 'recon', 'completed', 'recon.json'))
        self.recon_path.unlink()
        self.assertEqual(self.run_verify().returncode, 2)
        self.recon_path.write_text('{"target":"web","target":"web"}', encoding='utf-8')
        self.data['recon_sha256'] = hashlib.sha256(self.recon_path.read_bytes()).hexdigest()
        self.write()
        self.assertEqual(self.run_verify().returncode, 2)
        self.recon['target'] = 'mobile'
        self.recon_path.write_text(json.dumps(self.recon), encoding='utf-8')
        self.data['recon_sha256'] = hashlib.sha256(self.recon_path.read_bytes()).hexdigest()
        self.write()
        self.assertEqual(self.run_verify().returncode, 2)

    def test_rejects_duplicate_keys_in_artifact_and_checkpoint(self):
        self.write()
        original = self.artifact.read_text(encoding='utf-8')
        for duplicate in ('"target":"web",', '"tar\\u0067et":"other",', '"nested":{"x":1,"x":2},'):
            self.artifact.write_text('{' + duplicate + original[1:], encoding='utf-8')
            self.assertEqual(self.run_verify().returncode, 2)
        self.write()
        state = self.state_path.read_text(encoding='utf-8')
        self.state_path.write_text('{"version":1,' + state[1:], encoding='utf-8')
        self.assertEqual(self.run_verify().returncode, 2)

if __name__ == '__main__':
    unittest.main()
