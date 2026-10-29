"""Real-time offline host controls against the pinned ORIGINAL Laboratory."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
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

    def test_second_process_denied_and_crashed_holder_releases_lease(self):
        # A distinct process holds the original BrainStore lease without
        # touching either authority. The real CLI must fail before LOOK.
        ready = Path(self.temp.name) / "lease-ready"
        script = """
import sys
import time
from pathlib import Path
from doctor_lives.lab_runtime import _exclusive_host
with _exclusive_host(Path(sys.argv[1])):
    Path(sys.argv[2]).write_text("ready", encoding="utf-8")
    time.sleep(30)
"""
        holder = subprocess.Popen(
            [sys.executable, "-c", script, str(self.state), str(ready)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            for _ in range(200):
                if ready.is_file():
                    break
                if holder.poll() is not None:
                    self.fail("lease holder exited: " + holder.stderr.read())
                time.sleep(0.05)
            self.assertTrue(ready.is_file(), "lease holder did not start")
            before = self._receipt_and_observation_counts()
            denied = self._cli("--seconds", "0.3", "--interval-seconds", "0.1")
            self.assertNotEqual(denied.returncode, 0)
            self.assertEqual(denied.stdout, "")
            self.assertIn("host already active", denied.stderr)
            self.assertEqual(self._receipt_and_observation_counts(), before)
        finally:
            holder.terminate()
            holder.communicate(timeout=10)
        # OS lock ownership dies with the process. A stale lockfile must not
        # prevent a fresh, genuine Laboratory session or its source receipts.
        resumed = self._cli("--seconds", "0.3", "--interval-seconds", "0.1")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        report = json.loads(resumed.stdout)
        self.assertEqual(report["status"], "completed")
        self.assertTrue(report["subject_frames"])
        after = self._receipt_and_observation_counts()
        self.assertGreater(after[0], before[0])
        self.assertGreater(after[1], before[1])


    def test_two_actual_hosts_and_shared_world_alias_are_excluded(self):
        # Both contenders are real lab-run CLI processes, not a synthetic
        # helper holding the canonical state lease.
        before = self._receipt_and_observation_counts()
        command = [
            sys.executable, "-m", "doctor_lives.cli", "--state",
            str(self.state), "lab-run", "--world", str(self.world_path),
            "--seconds", "5", "--interval-seconds", "0.25",
        ]
        first = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if first.poll() is not None:
                    self.fail("first real host exited before lease test: "
                              + first.stderr.read())
                current = self._receipt_and_observation_counts()
                if all(after > old for old, after in zip(before, current)):
                    break
                time.sleep(0.05)
            else:
                self.fail("first real host did not admit its genuine LOOK")
            self.assertIsNone(first.poll())
            stable = self._receipt_and_observation_counts()
            denied = self._cli("--seconds", "0.3", "--interval-seconds", "0.1")
            self.assertNotEqual(denied.returncode, 0)
            self.assertEqual(denied.stdout, "")
            self.assertIn("host already active", denied.stderr)
            self.assertEqual(self._receipt_and_observation_counts(), stable)

            # A second real CLI has an EMPTY state, not another Doctor mind.
            # Its world lock must deny the symlink alias before brain startup.
            alternate = Path(self.temp.name) / "alias-contender-empty-state"
            alternate.mkdir()
            def alias_cli(path):
                return subprocess.run(
                    [sys.executable, "-m", "doctor_lives.cli", "--state",
                     str(alternate), "lab-run", "--world", str(path),
                     "--seconds", "0.3", "--interval-seconds", "0.1"],
                    capture_output=True, text=True, timeout=25,
                )
            if os.name != "nt":
                symlink = Path(self.temp.name) / "symlink-world.sqlite3"
                symlink.symlink_to(self.world_path)
                try:
                    denied_symlink = alias_cli(symlink)
                    self.assertNotEqual(denied_symlink.returncode, 0)
                    self.assertEqual(denied_symlink.stdout, "")
                    self.assertIn("world host already active", denied_symlink.stderr)
                    self.assertEqual(self._receipt_and_observation_counts(), stable)
                finally:
                    symlink.unlink()

            # The same SQLite inode under a different hardlink name previously
            # acquired a different pathname sidecar. Both paths must now fail
            # closed, with zero new LOOK receipts or lived memories.
            hardlink = Path(self.temp.name) / "hardlink-world.sqlite3"
            hardlink.hardlink_to(self.world_path)
            try:
                self.assertTrue(hardlink.samefile(self.world_path))
                self.assertGreater(self.world_path.stat().st_nlink, 1)
                denied_hardlink = alias_cli(hardlink)
                self.assertNotEqual(denied_hardlink.returncode, 0)
                self.assertEqual(denied_hardlink.stdout, "")
                self.assertIn("hardlinks are unsupported", denied_hardlink.stderr)
                self.assertEqual(self._receipt_and_observation_counts(), stable)
            finally:
                hardlink.unlink()
        finally:
            if first.poll() is None:
                first.terminate()
            stdout, stderr = first.communicate(timeout=15)
        self.assertEqual(first.returncode, 0, stderr)
        self.assertEqual(json.loads(stdout)["status"], "interrupted")

        # No second Pretorius mind is created. Hold only the WORLD lease
        # using an otherwise empty alternate state directory. A real
        # canonical lab-run must refuse the shared world before LOOK.
        from doctor_lives.lab_runtime import _exclusive_host
        alternate = Path(self.temp.name) / "alternate-state"
        alternate.mkdir()
        stable = self._receipt_and_observation_counts()
        with _exclusive_host(alternate, self.world_path):
            denied = self._cli("--seconds", "0.3", "--interval-seconds", "0.1")
            self.assertNotEqual(denied.returncode, 0)
            self.assertEqual(denied.stdout, "")
            self.assertIn("world host already active", denied.stderr)
            self.assertEqual(self._receipt_and_observation_counts(), stable)
        resumed = self._cli("--seconds", "0.3", "--interval-seconds", "0.1")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(json.loads(resumed.stdout)["status"], "completed")


    def test_hardlinked_world_is_denied_without_holder_and_recovers(self):
        # Fail closed even when no competing lease exists. Do not silently
        # admit a world inode whose sidecar can be bypassed by another name.
        alias = Path(self.temp.name) / "hardlink-unlocked-world.sqlite3"
        alias.hardlink_to(self.world_path)
        before = self._receipt_and_observation_counts()
        try:
            for path in (self.world_path, alias):
                with self.subTest(path=path):
                    denied = subprocess.run(
                        [sys.executable, "-m", "doctor_lives.cli", "--state",
                         str(self.state), "lab-run", "--world", str(path),
                         "--seconds", "0.3", "--interval-seconds", "0.1"],
                        capture_output=True, text=True, timeout=25,
                    )
                    self.assertNotEqual(denied.returncode, 0)
                    self.assertEqual(denied.stdout, "")
                    self.assertIn("hardlinks are unsupported", denied.stderr)
                    self.assertEqual(self._receipt_and_observation_counts(), before)
        finally:
            alias.unlink()
        resumed = self._cli("--seconds", "0.3", "--interval-seconds", "0.1")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(json.loads(resumed.stdout)["status"], "completed")
        after = self._receipt_and_observation_counts()
        self.assertGreater(after[0], before[0])
        self.assertGreater(after[1], before[1])

    def test_operator_sleep_is_physical_idempotent_and_wake_is_real(self):
        # This is explicitly OPERATOR requested, not a self-authored goal.
        # The original world must physically locate Pretorius in the bedroom.
        def sleep_cli(event_id="operator-sleep-001"):
            return subprocess.run(
                [sys.executable, "-m", "doctor_lives.cli", "--state",
                 str(self.state), "lab-sleep", "--world",
                 str(self.world_path), "--event-id", event_id],
                capture_output=True, text=True, timeout=25,
            )

        initial = self._receipt_and_observation_counts()
        denied = sleep_cli()
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(denied.stdout, "")
        self.assertIn("requires the actual Laboratory bedroom", denied.stderr)
        self.assertEqual(self._receipt_and_observation_counts(), initial)

        from doctor_lives.organs import SixOrganRuntime
        from doctor_lives.lab_runtime import _exclusive_host
        from pretorius_lab.subject_port import SubjectPort
        runtime = SixOrganRuntime.open(self.state)
        bridge = runtime.bind_laboratory(
            SubjectPort(SpatialHabitat(self.world_path)), authorized=True,
        )
        for index, station in enumerate(("station:hall", "station:bedroom")):
            bridge.act("walk", event_id=f"operator-bedroom-walk-{index}",
                       station=station)
        runtime.checkpoint()
        self.assertEqual(bridge.subject.embodied.verify()["station"],
                         "station:bedroom")
        with _exclusive_host(self.state, self.world_path):
            locked = sleep_cli()
            self.assertNotEqual(locked.returncode, 0)
            self.assertEqual(locked.stdout, "")
            self.assertIn("host already active", locked.stderr)

        before = self._receipt_and_observation_counts()
        first = sleep_cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        report = json.loads(first.stdout)
        self.assertEqual(report["schema"], "doctor-laboratory-offline-sleep.v1")
        self.assertEqual(report["status"], "admitted")
        self.assertEqual(report["physical_sleep_minutes"], 480)
        self.assertEqual(report["recovered"], 0)
        self.assertTrue(report["subject_frames"][-1]["inner"].startswith("I "))
        self.assertRegex(report["clock"]["beat"], r"^@[0-9]{3}$")
        with self.world._open() as db:
            sleep_rows = db.execute(
                "SELECT envelope FROM rhythm_events WHERE event_id=?",
                ("operator-sleep-001",),
            ).fetchall()
        self.assertEqual(len(sleep_rows), 1)
        self.assertEqual(json.loads(sleep_rows[0][0])["op"], "sleep")
        after = self._receipt_and_observation_counts()
        self.assertGreater(after[1], before[1])
        memories = PretoriusBrainPort(self.state).brain.store.memories(False)
        sleep_memories = [m for m in memories
                          if m["source"].startswith("laboratory-home:action:")
                          and "slept for the night" in m["text"]]
        self.assertEqual(len(sleep_memories), 1)
        self.assertEqual(sleep_memories[0]["evidence_class"],
                         "lived_runtime_memory")

        replay = sleep_cli()
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertEqual(json.loads(replay.stdout)["status"], "already_admitted")
        self.assertEqual(self._receipt_and_observation_counts(), after)
        with self.world._open() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM rhythm_events WHERE event_id=?",
                ("operator-sleep-001",),
            ).fetchone()[0], 1)

        # A new real elapsed host process wakes the SAME brain/world. It
        # observes authentic post-sleep conditions; no invented wake receipt.
        waking = self._cli("--seconds", "0.3", "--interval-seconds", "0.1")
        self.assertEqual(waking.returncode, 0, waking.stderr)
        woke = json.loads(waking.stdout)
        self.assertEqual(woke["status"], "completed")
        self.assertTrue(woke["subject_frames"])
        self.assertEqual(self.world.verify()["verified"], True)

    def test_sleep_world_commit_crash_replay_and_historical_room_change(self):
        # Kill a REAL child after the original rhythm receipt is committed,
        # before the original BrainStore can admit its first-person memory.
        from doctor_lives.organs import SixOrganRuntime
        from pretorius_lab.subject_port import SubjectPort
        runtime = SixOrganRuntime.open(self.state)
        bridge = runtime.bind_laboratory(
            SubjectPort(SpatialHabitat(self.world_path)), authorized=True,
        )
        for index, station in enumerate(("station:hall", "station:bedroom")):
            bridge.act("walk", event_id=f"sleep-crash-approach-{index}",
                       station=station)
        runtime.checkpoint()
        self.assertEqual(bridge.subject.embodied.verify()["station"],
                         "station:bedroom")
        minute_before = DailyRhythm(self.world).verify()["minute"]
        crash_script = """
import os
import sys
from pathlib import Path
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.lab_runtime import sleep_laboratory

def die_after_world_commit(self, frame, source, **kwargs):
    with self.world._open() as db:
        row = db.execute(
            "SELECT event_hash FROM rhythm_events WHERE event_id=?",
            ("operator-sleep-crash",),
        ).fetchone()
    assert row and source == "laboratory-home:action:" + row[0]
    assert not any(m["source"] == source
                   for m in self.doctor.brain.store.memories(False))
    os._exit(79)

DoctorHomeBridge._admit_verified = die_after_world_commit
sleep_laboratory(Path(sys.argv[1]), Path(sys.argv[2]),
                 event_id="operator-sleep-crash")
raise AssertionError("Sleep did not reach the post-world crash boundary")
"""
        crashed = subprocess.run(
            [sys.executable, "-c", crash_script, str(self.state),
             str(self.world_path)],
            capture_output=True, text=True, timeout=25,
        )
        self.assertEqual(crashed.returncode, 79, crashed.stderr)
        self.assertEqual(crashed.stdout, "")
        self.assertEqual(DailyRhythm(self.world).verify()["minute"] - minute_before, 480)

        def sleep_cli(event_id):
            return subprocess.run(
                [sys.executable, "-m", "doctor_lives.cli", "--state",
                 str(self.state), "lab-sleep", "--world",
                 str(self.world_path), "--event-id", event_id],
                capture_output=True, text=True, timeout=25,
            )

        with self.world._open() as db:
            rows = db.execute(
                "SELECT event_hash FROM rhythm_events WHERE event_id=?",
                ("operator-sleep-crash",),
            ).fetchall()
        self.assertEqual(len(rows), 1)
        source = "laboratory-home:action:" + rows[0][0]
        def sleep_memories():
            return [m for m in PretoriusBrainPort(self.state).brain.store.memories(False)
                    if m["source"] == source]
        self.assertEqual(sleep_memories(), [])

        recovered = sleep_cli("operator-sleep-crash")
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        report = json.loads(recovered.stdout)
        self.assertEqual(report["status"], "already_admitted")
        self.assertEqual(report["recovered"], 1)
        self.assertEqual(len(report["subject_frames"]), 1)
        self.assertIn("slept for the night", report["subject_frames"][0]["inner"])
        self.assertEqual(len(sleep_memories()), 1)
        self.assertEqual(sleep_memories()[0]["evidence_class"],
                         "lived_runtime_memory")

        # A second cold restart must not repeat the physical sleep, memory,
        # or subjective frame, and must not claim another recovery.
        second = sleep_cli("operator-sleep-crash")
        self.assertEqual(second.returncode, 0, second.stderr)
        second_report = json.loads(second.stdout)
        self.assertEqual(second_report["status"], "already_admitted")
        self.assertEqual(second_report["recovered"], 0)
        self.assertEqual(len(second_report["subject_frames"]), 1)
        self.assertEqual(DailyRhythm(self.world).verify()["minute"] - minute_before, 480)
        self.assertEqual(len(sleep_memories()), 1)

        # The body has genuinely left the bedroom. An authenticated old ID
        # must replay, but a NEW sleep ID still fails the bedroom condition.
        runtime = SixOrganRuntime.open(self.state)
        bridge = runtime.bind_laboratory(
            SubjectPort(SpatialHabitat(self.world_path)), authorized=True,
        )
        bridge.act("walk", event_id="sleep-crash-leave-bedroom",
                   station="station:hall")
        runtime.checkpoint()
        self.assertEqual(bridge.subject.embodied.verify()["station"],
                         "station:hall")
        before = self._receipt_and_observation_counts()
        historical = sleep_cli("operator-sleep-crash")
        self.assertEqual(historical.returncode, 0, historical.stderr)
        self.assertEqual(json.loads(historical.stdout)["status"],
                         "already_admitted")
        self.assertEqual(len(json.loads(historical.stdout)["subject_frames"]), 1)
        self.assertEqual(self._receipt_and_observation_counts(), before)
        self.assertEqual(len(sleep_memories()), 1)
        denied = sleep_cli("operator-sleep-new-outside-bedroom")
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(denied.stdout, "")
        self.assertIn("requires the actual Laboratory bedroom", denied.stderr)
        self.assertEqual(self._receipt_and_observation_counts(), before)
        with self.assertRaisesRegex(RuntimeError, "already reserved"):
            bridge.act("walk", event_id="operator-sleep-crash",
                       station="station:center")
        with self.world._open() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM rhythm_events WHERE event_id=?",
                ("operator-sleep-crash",),
            ).fetchone()[0], 1)

    def test_lab_start_obeys_both_live_host_leases_before_opening_authorities(self):
        # The first process is a real running Laboratory host. The alternate
        # lab-start path must not bypass either the brain or world lease.
        before = self._receipt_and_observation_counts()
        active = subprocess.Popen(
            [sys.executable, "-m", "doctor_lives.cli", "--state",
             str(self.state), "lab-run", "--world", str(self.world_path),
             "--seconds", "5", "--interval-seconds", "0.25"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        def start(state):
            return subprocess.run(
                [sys.executable, "-m", "doctor_lives.cli", "--state",
                 str(state), "lab-start", "--world", str(self.world_path)],
                capture_output=True, text=True, timeout=25,
            )
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if active.poll() is not None:
                    self.fail("real host exited before lease probe: "
                              + active.stderr.read())
                current = self._receipt_and_observation_counts()
                if all(after > old for old, after in zip(before, current)):
                    break
                time.sleep(0.05)
            else:
                self.fail("real host did not admit an authenticated LOOK")
            stable = self._receipt_and_observation_counts()

            same_brain = start(self.state)
            self.assertNotEqual(same_brain.returncode, 0)
            self.assertEqual(same_brain.stdout, "")
            self.assertIn("Canonical Doctor Laboratory host already active",
                          same_brain.stderr)
            self.assertEqual(self._receipt_and_observation_counts(), stable)

            # Empty alternate state proves denial by WORLD lease before any
            # other BrainStore can be created or opened.
            alternate = Path(self.temp.name) / "empty-alternate-state"
            alternate.mkdir()
            same_world = start(alternate)
            self.assertNotEqual(same_world.returncode, 0)
            self.assertEqual(same_world.stdout, "")
            self.assertIn("Authoritative Laboratory world host already active",
                          same_world.stderr)
            self.assertFalse((alternate / "brain.sqlite3").exists())
            self.assertEqual(self._receipt_and_observation_counts(), stable)
        finally:
            active.terminate()
            active.communicate(timeout=10)

        # A cold lab-start after OS lock release must resume the ORIGINAL
        # authority without adding a fresh LOOK or lived observation.
        stable = self._receipt_and_observation_counts()
        resumed = start(self.state)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        report = json.loads(resumed.stdout)
        self.assertEqual(report["status"], "ready")
        self.assertEqual(report["recovered"], 0)
        self.assertEqual(report["subject_frames"], [])
        self.assertRegex(report["clock"]["beat"], r"^@[0-9]{3}$")
        self.assertEqual(self._receipt_and_observation_counts(), stable)

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
