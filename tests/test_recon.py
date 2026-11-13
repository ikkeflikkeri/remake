import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.verify_recon import verify
from scripts.workflow import initial, save


class ReconTests(unittest.TestCase):
    def setUp(self):
        self.data = {"reference": "https://example.com", "target": "web",
                     "scope": "Public pages", "observations": ["Home page: navigation"],
                     "unknowns": ["Authenticated flows"], "sources": ["https://example.com"]}

    def test_valid_and_digest_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recon.json"
            path.write_text(json.dumps(self.data), encoding="utf-8")
            first = verify(path, self.data["reference"], "web")
            self.data["scope"] = "Public home page"
            path.write_text(json.dumps(self.data), encoding="utf-8")
            self.assertNotEqual(first, verify(path, self.data["reference"], "web"))

    def test_rejects_missing_empty_or_wrong_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recon.json"
            for change in ({"sources": []}, {"scope": " "}, {"extra": True}):
                path.write_text(json.dumps({**self.data, **change}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    verify(path, self.data["reference"], "web")
            path.write_text(json.dumps(self.data), encoding="utf-8")
            with self.assertRaises(ValueError):
                verify(path, self.data["reference"], "mobile")

    def test_missing_or_invalid_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            with self.assertRaises(OSError):
                verify(path, "ref", "web")
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify(path, "ref", "web")

    def test_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recon.json"
            valid = json.dumps(self.data)
            for duplicate in ('"target": "mobile", ', '"target": "web", ',
                              '"tar\\u0067et": "mobile", '):
                with self.subTest(duplicate=duplicate):
                    path.write_text("{" + duplicate + valid[1:], encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "duplicate.*target"):
                        verify(path, self.data["reference"], "web")
            path.write_text(valid.replace('"Public pages"', '{"x": 1, "x": 2}'),
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate.*x"):
                verify(path, self.data["reference"], "web")

    def test_cli_checks_checkpoint_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "workflow.json"
            artifact = root / "recon.json"
            save(state, initial(self.data["reference"], "web"))
            artifact.write_text(json.dumps(self.data), encoding="utf-8")
            script = Path(__file__).resolve().parents[1] / "scripts" / "verify_recon.py"
            command = [sys.executable, str(script), str(artifact), "--workflow", str(state)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("sha256:", result.stdout)
            artifact.write_text('{"target": "mobile", ' + json.dumps(self.data)[1:],
                                encoding="utf-8")
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("duplicate", result.stderr)
            self.assertNotIn("PASS", result.stdout)
            self.data["target"] = "mobile"
            artifact.write_text(json.dumps(self.data), encoding="utf-8")
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)


if __name__ == "__main__":
    unittest.main()
