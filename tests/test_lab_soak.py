"""Actual pinned-Laboratory offline soak evidence and restart controls."""
from __future__ import annotations

import gc
import importlib.util
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_soak import _digest, read_soak_log, soak_laboratory, verify_soak_sources
from doctor_lives.neural import DEFAULT_CONFIG

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None
if HAS_LAB:
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife


@unittest.skipUnless(HAS_LAB, "Requires pinned original Laboratory")
class SoakEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(gc.collect)
        root = Path(self.temp.name)
        self.state = root / "doctor"
        self.world = root / "world.sqlite3"
        self.log = root / "evidence.jsonl"
        habitat = SpatialHabitat.create(self.world)
        HomeLife(habitat).initialize()
        DailyRhythm(habitat).initialize()
        config = dict(DEFAULT_CONFIG)
        config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                      input_degree=4, action_population_size=8, seed=1842)
        PretoriusBrainPort(self.state, neural_config=config)

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "doctor_lives.cli", "--state", str(self.state),
             *args], capture_output=True, text=True, timeout=25,
        )

    def test_real_elapsed_segments_resume_and_do_not_fake_24h(self):
        first = self.cli(
            "lab-soak", "--world", str(self.world),
            "--evidence-log", str(self.log), "--seconds", "0.5",
            "--segment-seconds", "0.25", "--interval-seconds", "0.1",
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        report = json.loads(first.stdout)
        self.assertEqual(report["status"], "target_reached")
        self.assertGreaterEqual(report["segments"], 2)
        self.assertGreaterEqual(report["active_seconds"], 0.5)
        self.assertFalse(report["qualified_24h_candidate"])
        self.assertTrue(report["continuous"])
        self.assertEqual(report["work_event_ids"], 0)
        self.assertFalse(report["independent_source_attestation"])
        self.assertEqual(len(self.log.read_text().splitlines()), report["segments"])
        self.assertTrue(all(re.fullmatch(r"@[0-9]{3}", json.loads(line)["beat"])
                            for line in self.log.read_text().splitlines()))

        second = self.cli(
            "lab-soak", "--world", str(self.world),
            "--evidence-log", str(self.log), "--seconds", "0.8",
            "--segment-seconds", "0.25", "--interval-seconds", "0.1",
        )
        self.assertEqual(second.returncode, 0, second.stderr)
        resumed = json.loads(second.stdout)
        self.assertGreater(resumed["segments"], report["segments"])
        self.assertGreaterEqual(resumed["active_seconds"], 0.8)
        self.assertEqual(resumed["world_epoch"], report["world_epoch"])
        checked = self.cli("lab-soak-verify", "--evidence-log", str(self.log))
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(checked.stdout)["last_sha256"],
                         resumed["last_sha256"])

        # The original world may have legitimate LOOKs, but an off-bench
        # elapsed host cannot invent work, motor decisions, or lived actions.
        with SpatialHabitat(self.world)._open() as db:
            events = [json.loads(x[0]) for x in db.execute(
                "SELECT envelope FROM rhythm_events"
            )]
        self.assertTrue(events)
        self.assertFalse(any(x.get("op") in ("experiment", "repair") for x in events))
        brain = PretoriusBrainPort(self.state)
        lived = [m for m in brain.brain.store.memories(False)
                 if m["source"].startswith("laboratory-home:observe:")]
        self.assertEqual(len(lived), 1)

    def test_torn_or_rehashed_wrong_sequence_denied(self):
        first = self.cli(
            "lab-soak", "--world", str(self.world),
            "--evidence-log", str(self.log), "--seconds", "0.2",
            "--segment-seconds", "0.2", "--interval-seconds", "0.1",
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        row = json.loads(self.log.read_text().splitlines()[0])
        row["sequence"] = 7
        self.log.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            read_soak_log(self.log)
        denied = self.cli(
            "lab-soak", "--world", str(self.world),
            "--evidence-log", str(self.log), "--seconds", "0.4",
            "--segment-seconds", "0.2", "--interval-seconds", "0.1",
        )
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(len(self.log.read_text().splitlines()), 1)

    def test_engineering_log_cannot_become_brain_or_world_state(self):
        with self.assertRaises(ValueError):
            soak_laboratory(
                self.state, self.world, self.state / "soak.jsonl",
                target_seconds=0.2, segment_seconds=0.2, interval_seconds=0.1,
            )
        with self.assertRaises(ValueError):
            soak_laboratory(
                self.state, self.world, self.world,
                target_seconds=0.2, segment_seconds=0.2, interval_seconds=0.1,
            )
        self.assertFalse((self.state / "soak.jsonl").exists())

    def test_reserved_world_sidecars_denied_without_look_or_mutation(self):
        # The world lock is persistent authority, not an engineering log.
        world_lock = self.world.with_name(
            self.world.name + ".laboratory-host.lock"
        )
        world_lock.write_bytes(b"original-world-lock-sentinel")
        with SpatialHabitat(self.world)._open() as db:
            before_receipts = {
                table: db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
                for table in ("embodied_events", "rhythm_events")
            }
        before_memories = len(
            PretoriusBrainPort(self.state).brain.store.memories(False)
        )
        before_world = self.world.read_bytes()
        before_lock = world_lock.read_bytes()
        suffixes = (
            "-wal", "-shm", "-journal", "-stmtjrnl",
            "-super-journal", "-mj012345", ".laboratory-host.lock",
        )
        for suffix in suffixes:
            with self.subTest(suffix=suffix):
                candidate = self.world.with_name(self.world.name + suffix)
                prior = candidate.read_bytes() if candidate.exists() else None
                with self.assertRaises(ValueError):
                    soak_laboratory(
                        self.state, self.world, candidate,
                        target_seconds=0.2, segment_seconds=0.2,
                        interval_seconds=0.1,
                    )
                self.assertEqual(
                    candidate.read_bytes() if candidate.exists() else None, prior
                )
        self.assertEqual(self.world.read_bytes(), before_world)
        self.assertEqual(world_lock.read_bytes(), before_lock)
        with SpatialHabitat(self.world)._open() as db:
            after_receipts = {
                table: db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
                for table in ("embodied_events", "rhythm_events")
            }
        self.assertEqual(after_receipts, before_receipts)
        self.assertEqual(
            len(PretoriusBrainPort(self.state).brain.store.memories(False)),
            before_memories,
        )
        self.assertFalse(self.log.exists())

        # A normal external log still permits real elapsed observation.
        result = soak_laboratory(
            self.state, self.world, self.log,
            target_seconds=0.2, segment_seconds=0.2,
            interval_seconds=0.1,
        )
        self.assertEqual(result["status"], "target_reached")
        self.assertEqual(read_soak_log(self.log)["segments"], 1)

    def test_world_lock_aliases_and_hardlinks_denied_before_host(self):
        world_lock = self.world.with_name(
            self.world.name + ".laboratory-host.lock"
        )
        world_lock.write_bytes(b"world-lock-must-remain-unchanged")
        before_world = self.world.read_bytes()
        before_lock = world_lock.read_bytes()
        # This evidence path is not itself reserved, but its companion .lock
        # would overwrite the original world's persistent host lock.
        collision = self.world.with_name(
            self.world.name + ".laboratory-host"
        )
        with self.assertRaises(ValueError):
            soak_laboratory(
                self.state, self.world, collision,
                target_seconds=0.2, segment_seconds=0.2,
                interval_seconds=0.1,
            )
        alias = Path(self.temp.name) / "alias-of-world-lock.jsonl"
        os.link(world_lock, alias)
        self.addCleanup(lambda: alias.unlink(missing_ok=True))
        with self.assertRaises(ValueError):
            soak_laboratory(
                self.state, self.world, alias,
                target_seconds=0.2, segment_seconds=0.2,
                interval_seconds=0.1,
            )
        # A hardlink outside the state directory must not become a second
        # writable name for the canonical BrainStore.
        brain_alias = Path(self.temp.name) / "alias-of-brain.jsonl"
        os.link(self.state / "brain.sqlite3", brain_alias)
        self.addCleanup(lambda: brain_alias.unlink(missing_ok=True))
        with self.assertRaises(ValueError):
            soak_laboratory(
                self.state, self.world, brain_alias,
                target_seconds=0.2, segment_seconds=0.2,
                interval_seconds=0.1,
            )
        self.assertEqual(self.world.read_bytes(), before_world)
        self.assertEqual(world_lock.read_bytes(), before_lock)
        self.assertFalse(collision.exists())
        self.assertFalse(self.log.exists())

    def test_preexisting_stop_never_creates_world_look(self):
        stop = threading.Event()
        stop.set()
        result = soak_laboratory(
            self.state, self.world, self.log,
            target_seconds=0.2, segment_seconds=0.2,
            interval_seconds=0.1, stop=stop,
        )
        self.assertEqual(result["status"], "interrupted")
        self.assertEqual(result["segments"], 0)
        self.assertFalse(self.log.exists())
        with SpatialHabitat(self.world)._open() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM embodied_events"
            ).fetchone()[0], 0)


    def test_real_soak_work_requires_original_world_noesis_and_lived_memory(self):
        from doctor_lives.organs import SixOrganRuntime
        from pretorius_lab.subject_port import SubjectPort

        # Setup is an explicit operator action, not credited as Doctor initiative.
        runtime = SixOrganRuntime.open(self.state)
        bridge = runtime.bind_laboratory(
            SubjectPort(SpatialHabitat(self.world)), authorized=True,
        )
        bridge.act("walk", event_id="soak-setup-center", station="station:center")
        bridge.act("walk", event_id="soak-setup-bench", station="station:bench")
        bridge.act("experiment", event_id="soak-setup-wear")
        runtime.checkpoint()
        result = soak_laboratory(
            self.state, self.world, self.log, target_seconds=2.0,
            segment_seconds=2.0, interval_seconds=0.2,
            work_interval_seconds=0.15,
        )
        self.assertGreaterEqual(result["work_event_ids"], 1)
        verified = verify_soak_sources(self.state, self.world, self.log)
        self.assertTrue(verified["original_world_epoch_verified"])
        self.assertEqual(verified["original_noesis_work_events_verified"],
                         result["work_event_ids"])
        self.assertFalse(verified["independent_source_attestation"])
        self.assertFalse(verified["qualified_24h_candidate"])
        via_cli = self.cli(
            "lab-soak-verify", "--world", str(self.world),
            "--evidence-log", str(self.log),
        )
        self.assertEqual(via_cli.returncode, 0, via_cli.stderr)
        self.assertEqual(json.loads(via_cli.stdout)[
            "original_noesis_work_events_verified"], result["work_event_ids"])

        # Rehashing a locally writable engineering log cannot manufacture
        # original Laboratory receipts or an original-Noesis motor binding.
        lines = self.log.read_text(encoding="utf-8").splitlines()
        first = json.loads(lines[0])
        first["work_event_ids"] = ["forged-physical-work"]
        first.pop("sha256")
        first["sha256"] = _digest(first)
        lines[0] = json.dumps(first, sort_keys=True)
        self.log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaises((RuntimeError, PermissionError)):
            verify_soak_sources(self.state, self.world, self.log)

    def test_rehashed_clock_only_24h_is_not_qualified_life(self):
        # This is deliberately NOT a real 24-hour test. A privileged writer
        # can rehash a fabricated engineering log; no world, neural activity
        # or independent approval may be inferred from its timestamps.
        row = {
            "schema": "doctor-laboratory-soak-segment.v1",
            "sequence": 1, "previous_sha256": "0" * 64,
            "started_utc": "2026-10-30T00:00:00Z",
            "ended_utc": "2026-10-31T00:00:01Z",
            "active_seconds": 86401.0,
            "host_elapsed_seconds": 86401.0,
            "status": "completed", "beat": "@000",
            "world_epoch": "invented-world",
            "pulses": 0, "recovered": 0, "abandoned": 0,
            "work_event_ids": [], "subject_frame_count": 0,
            "lab_source_pin_expected": "6e49795752835d64fa6fd63d16359669a1ca2ba7",
        }
        row["sha256"] = _digest(row)
        self.log.write_text(json.dumps(row) + "\n", encoding="utf-8")
        report = read_soak_log(self.log)
        self.assertTrue(report["elapsed_24h_candidate"])
        self.assertFalse(report["activity_observed"])
        self.assertFalse(report["qualified_24h_candidate"])
        self.assertFalse(report["independent_source_attestation"])
        with self.assertRaises(RuntimeError):
            verify_soak_sources(self.state, self.world, self.log)
        row["pulses"] = -1
        row.pop("sha256")
        row["sha256"] = _digest(row)
        self.log.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            read_soak_log(self.log)


if __name__ == "__main__":
    unittest.main()
