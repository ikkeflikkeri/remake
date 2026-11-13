import json
import tempfile
import unittest
from pathlib import Path
from scripts.validate_skills import ROOT, validate

class StructureTests(unittest.TestCase):
    def test_repository_passes(self):
        self.assertEqual(validate(), [])

    def test_plugin_manifest(self):
        manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], "remake")
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")

    def test_missing_skills_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertIn("no SKILL.md files found", validate(Path(directory)))

    def test_invalid_skill_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin/plugin.json").write_text('{"name":"remake","version":"0.1.0"}')
            skill = root / "skills" / "wrong"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: other\ndescription: This is a sufficiently long description for testing.\n---\n")
            self.assertTrue(any("mismatched name" in e for e in validate(root)))

if __name__ == "__main__":
    unittest.main()
