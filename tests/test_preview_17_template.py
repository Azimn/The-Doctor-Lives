"""Fail-closed template validation and no existing-workspace replacement."""
from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import tempfile
import unittest

from doctor_lives.lab_preview import initialize_preview
from doctor_lives.preview_17_books import verify_unread_seventeen


@unittest.skipUnless(importlib.util.find_spec("pretorius_lab") is not None,
                     "Original Laboratory donor not installed in brain-only CI")
class SeventeenTemplateContract(unittest.TestCase):
    def test_empty_world_rejected_before_genesis(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            world = SpatialHabitat.create(root / "empty.sqlite3")
            HomeLife(world).initialize()
            DailyRhythm(world).initialize()
            target = root / "new-doctor"
            with self.assertRaises(ValueError):
                initialize_preview(target, world_template=world.path)
            self.assertFalse(target.exists())

    def test_no_occupied_workspace_replacement(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "existing"
            target.mkdir()
            marker = target / "already-has-a-life.txt"
            marker.write_text("leave this alone")
            with self.assertRaises((FileExistsError, FileNotFoundError)):
                initialize_preview(target, world_template=root / "missing.sqlite3")
            self.assertEqual(marker.read_text(), "leave this alone")


if __name__ == "__main__":
    unittest.main()
