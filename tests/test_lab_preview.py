"""Standalone original-Laboratory genesis and cold-start acceptance candidates."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from doctor_lives.lab_preview import initialize_preview


class RefusalTests(unittest.TestCase):
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
