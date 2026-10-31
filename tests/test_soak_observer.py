"""Independent stdlib runner-health observer controls; no 24-hour claim."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "observe_soak_runner.py"
spec = importlib.util.spec_from_file_location("pretorius_soak_observer", SCRIPT)
observer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)


@unittest.skipUnless(os.name == "nt" or os.path.exists("/proc/uptime"),
                     "Observer requires Windows or Linux system telemetry")
class ObserverTests(unittest.TestCase):
    def test_real_monotonic_samples_and_nonqualification(self):
        with tempfile.TemporaryDirectory() as root:
            log = Path(root) / "runner.jsonl"
            result = observer.observe(pid=os.getpid(), evidence_log=log,
                                      disk_path=Path(root), seconds=0.12,
                                      interval=0.04)
            rows = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertGreaterEqual(len(rows), 3)
            self.assertEqual(result["samples"], len(rows))
            self.assertGreaterEqual(result["monotonic_elapsed_seconds"], 0.12)
            self.assertFalse(result["r5_qualified"])
            self.assertTrue(all(x["runner_health_only"] and not
                                x["independent_source_attestation"] for x in rows))
            self.assertEqual([x["sequence"] for x in rows], list(range(1, len(rows)+1)))
            self.assertEqual(len({x["boot_identity"] for x in rows}), 1)
            self.assertTrue(all(x["memory_total_bytes"] >= x["memory_available_bytes"]
                                for x in rows))
            with self.assertRaises(FileExistsError):
                observer.observe(pid=os.getpid(), evidence_log=log,
                                 disk_path=Path(root), seconds=0.01, interval=0.01)

    def test_refuses_missing_process_without_creating_log(self):
        with tempfile.TemporaryDirectory() as root:
            log = Path(root) / "runner.jsonl"
            with self.assertRaises(RuntimeError):
                observer.observe(pid=2147483647, evidence_log=log,
                                 disk_path=Path(root), seconds=0.01, interval=0.01)
            self.assertFalse(log.exists())

    def test_observed_process_exit_is_a_fault_not_a_pass(self):
        with tempfile.TemporaryDirectory() as root:
            log = Path(root) / "runner.jsonl"
            child = subprocess.Popen([sys.executable, "-c", "pass"])
            try:
                with self.assertRaisesRegex(RuntimeError, "exited or PID was reused|not alive"):
                    observer.observe(pid=child.pid, evidence_log=log,
                                     disk_path=Path(root), seconds=2.5,
                                     interval=0.1)
                if log.exists():
                    self.assertGreaterEqual(len(log.read_text().splitlines()), 1)
            finally:
                child.wait(timeout=5)

    @unittest.skipUnless(os.name == "nt", "Windows exit-code 259 ambiguity only")
    def test_windows_terminated_process_exit_259_is_not_live(self):
        # Windows STILL_ACTIVE (259) is also a valid final exit code.
        # Keep Popen's process handle alive so OpenProcess can still open
        # the terminated process object, rather than relying on PID absence.
        with tempfile.TemporaryDirectory() as root:
            log = Path(root) / "runner.jsonl"
            child = subprocess.Popen([sys.executable, "-c",
                                      "import sys; sys.exit(259)"])
            try:
                self.assertEqual(child.wait(timeout=15), 259)
                self.assertIsNone(observer._process_identity(child.pid))
                with self.assertRaisesRegex(RuntimeError, "not alive"):
                    observer.observe(pid=child.pid, evidence_log=log,
                                     disk_path=Path(root), seconds=0.1,
                                     interval=0.02)
                self.assertFalse(log.exists())
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=5)

    def test_process_disappearance_after_first_sample_preserves_partial_log(self):
        with tempfile.TemporaryDirectory() as root:
            log = Path(root) / "runner.jsonl"
            actual_identity = observer._process_identity(os.getpid())
            with patch.object(observer, "_process_identity",
                              side_effect=[actual_identity, actual_identity, None]):
                with self.assertRaisesRegex(RuntimeError, "exited or PID was reused"):
                    observer.observe(pid=os.getpid(), evidence_log=log,
                                     disk_path=Path(root), seconds=0.3,
                                     interval=0.02)
            self.assertEqual(len(log.read_text().splitlines()), 1)

    def test_refuses_symlink_and_long_gap_configuration(self):
        with tempfile.TemporaryDirectory() as root:
            log = Path(root) / "runner.jsonl"
            with self.assertRaises(ValueError):
                observer.observe(pid=os.getpid(), evidence_log=log,
                                 disk_path=Path(root), seconds=0.01, interval=61)
            target = Path(root) / "target"
            target.write_text("keep")
            try:
                log.symlink_to(target)
            except (OSError, NotImplementedError):
                return
            with self.assertRaises(ValueError):
                observer.observe(pid=os.getpid(), evidence_log=log,
                                 disk_path=Path(root), seconds=0.01, interval=0.01)
            self.assertEqual(target.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
