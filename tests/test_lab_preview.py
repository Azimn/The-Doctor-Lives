"""Standalone original-Laboratory genesis and cold-start acceptance candidates."""
from __future__ import annotations

import gc
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from doctor_lives import lab_preview
from doctor_lives.lab_preview import initialize_preview


class RefusalTests(unittest.TestCase):
    def test_kernel_publish_refuses_competing_empty_destination(self):
        # This is the exact POSIX race missed by Path.exists() + rename().
        # It runs without any Laboratory import, including on cold installs.
        with tempfile.TemporaryDirectory() as root:
            staging = Path(root) / "staged"
            staging.mkdir()
            (staging / "brain.sqlite3").write_bytes(b"new canonical brain")
            destination = Path(root) / "claimed"
            destination.mkdir()  # Competing process wins before publication.
            with self.assertRaises(FileExistsError):
                lab_preview._publish_noreplace(staging, destination)
            self.assertTrue(staging.is_dir())
            self.assertEqual((staging / "brain.sqlite3").read_bytes(),
                             b"new canonical brain")
            self.assertEqual(list(destination.iterdir()), [])

    def test_existing_workspace_is_never_reseeded(self):
        with tempfile.TemporaryDirectory() as root:
            destination = Path(root) / "inhabited"
            destination.mkdir()
            marker = destination / "brain.sqlite3"
            marker.write_bytes(b"existing personal data")
            with self.assertRaises(FileExistsError):
                initialize_preview(destination)
            self.assertEqual(marker.read_bytes(), b"existing personal data")


@unittest.skipUnless(importlib.util.find_spec("pretorius_lab"),
                     "Original pinned Laboratory distribution required")
class OriginalLaboratoryGenesisTests(unittest.TestCase):
    def test_atomic_genesis_two_fresh_process_starts_and_no_reseed(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        with tempfile.TemporaryDirectory() as root:
            destination = Path(root) / "standalone"
            result = initialize_preview(destination)
            self.assertEqual(result["schema"], "doctor-laboratory-experimental-genesis.v1")
            self.assertFalse(result["release_accepted"])
            self.assertFalse(result["three_task_autonomy_proven"])
            self.assertFalse(result["subject_experienced_initialization"])
            self.assertTrue((destination / "state" / "brain.sqlite3").is_file())
            self.assertTrue((destination / "state" / "pretorius_recurrent.npz").is_file())
            self.assertEqual(SpatialHabitat(destination / "laboratory.sqlite3").verify()["world_epoch"],
                             result["world_epoch"])
            args = [sys.executable, "-m", "doctor_lives.cli", "--state",
                    str(destination / "state"), "lab-start", "--world",
                    str(destination / "laboratory.sqlite3")]
            for _ in range(2):
                result = subprocess.run(args, capture_output=True, text=True, timeout=180)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('"status": "ready"', result.stdout)
            with self.assertRaises(FileExistsError):
                initialize_preview(destination)
            # Original Laboratory `with sqlite3.Connection` commits without
            # closing readers; release verification-only handles before the
            # Windows TemporaryDirectory removes the world database.
            gc.collect()

    def test_competing_empty_workspace_at_publish_is_never_clobbered(self):
        # Deterministically create the competing directory AFTER full genesis
        # and the final existence check, at the actual publication boundary.
        with tempfile.TemporaryDirectory() as root:
            destination = Path(root) / "contested"
            real_publish = lab_preview._publish_noreplace

            def competitor_wins(staging, target):
                self.assertEqual(target, destination)
                target.mkdir()
                return real_publish(staging, target)

            with patch("doctor_lives.lab_preview._publish_noreplace",
                       side_effect=competitor_wins):
                with self.assertRaises(FileExistsError):
                    initialize_preview(destination)
            self.assertTrue(destination.is_dir())
            self.assertEqual(list(destination.iterdir()), [])
            self.assertFalse(list(Path(root).glob(".pretorius-preview-*")))

    @unittest.skipUnless(sys.platform == "win32", "Windows directory-lock regression")
    def test_windows_five_independent_clean_genesis_processes(self):
        # Each CLI process starts with a new world+brain, without retries.
        # The original Lab's verification readers must not pin the staging
        # directory when the initializer atomically publishes it on Windows.
        import json
        from pretorius_lab.habitat_v2 import SpatialHabitat

        with tempfile.TemporaryDirectory() as root:
            for attempt in range(1, 6):
                workspace = Path(root) / f"cold-genesis-{attempt}"
                created = subprocess.run(
                    [sys.executable, "-m", "doctor_lives.cli",
                     "preview-init", "--workspace", str(workspace)],
                    capture_output=True, text=True, timeout=180,
                )
                self.assertEqual(
                    created.returncode, 0,
                    f"clean genesis attempt {attempt}: {created.stderr}",
                )
                genesis = json.loads(created.stdout)
                self.assertEqual(genesis["status"], "ready_for_operator_start")
                self.assertFalse(genesis["release_accepted"])
                self.assertEqual(
                    SpatialHabitat(workspace / "laboratory.sqlite3").verify()[
                        "world_epoch"
                    ], genesis["world_epoch"],
                )
                started = subprocess.run(
                    [sys.executable, "-m", "doctor_lives.cli",
                     "--state", str(workspace / "state"),
                     "lab-start", "--world",
                     str(workspace / "laboratory.sqlite3")],
                    capture_output=True, text=True, timeout=180,
                )
                self.assertEqual(
                    started.returncode, 0,
                    f"cold start attempt {attempt}: {started.stderr}",
                )
                self.assertEqual(json.loads(started.stdout)["status"], "ready")
                print(
                    f"WINDOWS_CLEAN_GENESIS_RECEIPT attempt={attempt}/5 "
                    f"world_epoch={genesis['world_epoch']} "
                    f"genesis=ready_for_operator_start cold_start=ready",
                    flush=True,
                )
            # Parent-side original-world verification also opens SQLite readers.
            # Do not mistake Windows test teardown locks for genesis failures.
            gc.collect()

    def test_failed_world_genesis_leaves_no_published_authority(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as root:
            destination = Path(root) / "failure"
            with patch("pretorius_lab.habitat_v2.SpatialHabitat.create",
                       side_effect=RuntimeError("injected world failure")):
                with self.assertRaisesRegex(RuntimeError, "injected world failure"):
                    initialize_preview(destination)
            self.assertFalse(destination.exists())
            self.assertFalse(list(Path(root).glob(".pretorius-preview-*")))
