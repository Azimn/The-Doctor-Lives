"""Real-time offline host controls against the pinned ORIGINAL Laboratory."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_runtime import run_laboratory
from doctor_lives.neural import DEFAULT_CONFIG
HAS_ORIGINAL_LAB = importlib.util.find_spec("pretorius_lab") is not None
if HAS_ORIGINAL_LAB:
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife


@unittest.skipUnless(HAS_ORIGINAL_LAB, "Requires the pinned original Laboratory")
class OfflineLaboratoryRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.state = root / "brain"
        self.world_path = root / "world.sqlite3"
        self.world = SpatialHabitat.create(self.world_path)
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        config = dict(DEFAULT_CONFIG)
        config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                      input_degree=4, action_population_size=8, seed=1842)
        PretoriusBrainPort(self.state, neural_config=config)

    def _cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "doctor_lives.cli", "--state",
             str(self.state), "lab-run", "--world", str(self.world_path),
             *args], capture_output=True, text=True, timeout=25,
        )

    def test_elapsed_host_resumes_same_brain_without_authoring_world_actions(self):
        before = self.world.verify()["world_epoch"]
        first = self._cli("--seconds", "0.8", "--interval-seconds", "0.1")
        self.assertEqual(first.returncode, 0, first.stderr)
        result = json.loads(first.stdout)
        self.assertEqual(result["schema"], "doctor-laboratory-offline-run.v1")
        self.assertEqual(result["status"], "completed")
        self.assertGreaterEqual(result["elapsed_seconds"], 0.7)
        self.assertGreaterEqual(result["pulses"], 1)
        self.assertEqual(result["recovered"], 0)
        self.assertTrue(result["subject_frames"][0]["inner"].startswith(("I ", "My ", "Mine ", "Me ")))
        self.assertRegex(result["clock"]["beat"], r"^@[0-9]{3}$")
        self.assertTrue(result["clock"]["utc"].endswith("Z"))
        self.assertNotIn("world_epoch", first.stdout)
        self.assertNotIn("action_scores", first.stdout)

        second = self._cli("--seconds", "0.5", "--interval-seconds", "0.1")
        self.assertEqual(second.returncode, 0, second.stderr)
        again = json.loads(second.stdout)
        self.assertEqual(again["status"], "completed")
        self.assertGreaterEqual(again["pulses"], 1)
        self.assertEqual(self.world.verify()["world_epoch"], before)
        with self.world._open() as db:
            body = [json.loads(row[0]) for row in db.execute("SELECT envelope FROM embodied_events")]
            rhythm = [json.loads(row[0]) for row in db.execute("SELECT envelope FROM rhythm_events")]
            self.assertTrue(body and all(e["kind"] == "look" for e in body))
            self.assertTrue(rhythm and all(e["op"] == "look" for e in rhythm))
        port = PretoriusBrainPort(self.state)
        observations = [m for m in port.brain.store.memories(False)
                        if m["source"].startswith("laboratory-home:observe:")]
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]["evidence_class"], "lived_runtime_memory")

    def _receipt_and_observation_counts(self):
        with self.world._open() as db:
            embodied = db.execute("SELECT COUNT(*) FROM embodied_events").fetchone()[0]
            rhythm = db.execute("SELECT COUNT(*) FROM rhythm_events").fetchone()[0]
        port = PretoriusBrainPort(self.state)
        observations = sum(
            memory["source"].startswith("laboratory-home:observe:")
            for memory in port.brain.store.memories(False)
        )
        return embodied, rhythm, observations

    def test_sigterm_immediately_after_handler_install_does_not_observe(self):
        # Deliver a real OS SIGTERM immediately after the CLI registers its
        # handler. This avoids a scheduler-dependent kill-before-handler race.
        script = """
import os
import signal
import sys
from doctor_lives.cli import main

original_signal = signal.signal
fired = False
def install(signum, handler):
    global fired
    previous = original_signal(signum, handler)
    if signum == signal.SIGTERM and not fired:
        fired = True
        os.kill(os.getpid(), signal.SIGTERM)
    return previous
signal.signal = install
raise SystemExit(main(sys.argv[1:]))
"""
        before = self._receipt_and_observation_counts()
        proc = subprocess.run(
            [sys.executable, "-c", script, "--state", str(self.state),
             "lab-run", "--world", str(self.world_path),
             "--seconds", "1", "--interval-seconds", "0.1"],
            capture_output=True, text=True, timeout=25,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(report["status"], "interrupted")
        self.assertEqual(report["pulses"], 0)
        self.assertEqual(report["recovered"], 0)
        self.assertEqual(report["subject_frames"], [])
        self.assertEqual(self._receipt_and_observation_counts(), before)

    def test_interrupt_and_invalid_interval_fail_closed(self):
        stop = threading.Event()
        stop.set()
        before = self._receipt_and_observation_counts()
        report = run_laboratory(
            self.state, self.world_path, duration_seconds=1.0,
            interval_seconds=0.1, stop=stop,
        )
        self.assertEqual(report["status"], "interrupted")
        self.assertEqual(report["pulses"], 0)
        self.assertEqual(report["recovered"], 0)
        self.assertEqual(report["subject_frames"], [])
        self.assertEqual(self._receipt_and_observation_counts(), before)
        for args in (("--seconds", "0"),
                     ("--seconds", "0.5", "--interval-seconds", "0"),
                     ("--seconds", "nan")):
            with self.subTest(args=args):
                denied = self._cli(*args)
                self.assertNotEqual(denied.returncode, 0)
                self.assertEqual(denied.stdout, "")


if __name__ == "__main__":
    unittest.main()
