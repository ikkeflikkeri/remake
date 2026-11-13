import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from scripts.workflow import STAGES, WorkflowError, initial, read, save, transition, validate

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.state = initial("https://example.com", "web")

    def test_initial_valid(self):
        self.assertEqual(validate(self.state), self.state)
        self.assertEqual(len(self.state["stages"]), 11)

    def test_requires_reference(self):
        with self.assertRaises(WorkflowError):
            initial("", "web")

    def test_cannot_skip_prerequisites(self):
        with self.assertRaises(WorkflowError):
            transition(self.state, "build", "in_progress")

    def test_complete_requires_evidence(self):
        started = transition(self.state, "recon", "in_progress")
        with self.assertRaises(WorkflowError):
            transition(started, "recon", "completed")

    def test_progression_and_checkpoint(self):
        started = transition(self.state, "recon", "in_progress")
        completed = transition(started, "recon", "completed", ".remake/recon.md")
        self.assertEqual(completed["stages"]["recon"]["status"], "completed")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".remake" / "workflow.json"
            save(path, completed)
            self.assertEqual(read(path), completed)
            next_state = transition(read(path), "architect", "in_progress")
            self.assertEqual(next_state["stages"]["architect"]["status"], "in_progress")

    def test_block_and_resume(self):
        started = transition(self.state, "recon", "in_progress")
        blocked = transition(started, "recon", "blocked", "missing permission")
        resumed = transition(blocked, "recon", "in_progress")
        self.assertEqual(resumed["stages"]["recon"]["status"], "in_progress")
        with self.assertRaises(WorkflowError):
            transition(resumed, "recon", "completed")
        self.assertEqual(transition(resumed, "recon", "completed", "result.md")["stages"]["recon"]["status"], "completed")

    def test_block_requires_reason_and_start_rejects_evidence(self):
        with self.assertRaises(WorkflowError):
            transition(self.state, "recon", "in_progress", "premature")
        started = transition(self.state, "recon", "in_progress")
        with self.assertRaises(WorkflowError):
            transition(started, "recon", "blocked")

    def test_create_does_not_replace_existing_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            save(path, self.state, create=True)
            with self.assertRaises(WorkflowError):
                save(path, initial("other", "web"), create=True)
            self.assertEqual(read(path), self.state)

    def test_invalid_encoding_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_bytes(b"\xff")
            with self.assertRaises(WorkflowError):
                read(path)

    def test_no_simultaneous_active_stages(self):
        started = transition(self.state, "recon", "in_progress")
        with self.assertRaises(WorkflowError):
            transition(started, "architect", "in_progress")

    def test_completed_stage_immutable(self):
        completed = transition(transition(self.state, "recon", "in_progress"),
                               "recon", "completed", "recon.md")
        with self.assertRaises(WorkflowError):
            transition(completed, "recon", "in_progress")

    def test_reject_malformed_state(self):
        self.state["stages"]["recon"]["status"] = "completed"
        with self.assertRaises(WorkflowError):
            validate(self.state)

    def test_cli_init_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "workflow.json")
            command = [sys.executable, str(ROOT / "scripts/workflow.py"), "init",
                       "--file", path, "--reference", "example.com", "--target", "web"]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual(read(path)["reference"], "example.com")


if __name__ == "__main__":
    unittest.main()
