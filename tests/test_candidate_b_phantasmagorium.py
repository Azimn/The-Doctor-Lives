"""Regression checks for Candidate B's opt-in Phantasmagorium boundary."""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from doctor_lives.store import BrainStore
from doctor_lives.phantasmagorium_bridge import PhantasmagoriumBridge, verify_archive


class PinnedOrganoidBoundaryTests(unittest.TestCase):
    def test_refuse_missing_or_unreviewed_zip_and_disabled_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = BrainStore(root / "brain.sqlite3")
            bad = root / "donor.zip"
            bad.write_bytes(b"unreviewed")
            with self.assertRaises((PermissionError, ValueError)):
                verify_archive(bad)
            with self.assertRaises(PermissionError):
                PhantasmagoriumBridge(store, bad, enabled=False)
            with self.assertRaises(FileNotFoundError):
                PhantasmagoriumBridge(store, root / "missing.zip", enabled=True)

    @unittest.skipUnless(os.environ.get("PRETORIUS_PHANTA_DONOR"),
                         "Exact v0.5 donor must be explicitly provided")
    def test_real_original_donor_fancy_and_dream_source_boundary(self):
        archive = Path(os.environ["PRETORIUS_PHANTA_DONOR"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = BrainStore(root / "brain.sqlite3")
            organoid = PhantasmagoriumBridge(store, archive, enabled=True)
            scene = {"entities": [
                {"id": "raven", "kind": "bird", "properties": {"color": "black"}},
                {"id": "stone", "kind": "rock", "properties": {"material": "granite"}},
            ], "relations": []}
            imagination = organoid.fancy(scene, seed=7, max_fragments=2)
            dream = organoid.single_night_probe(
                day=1, seed=7, experience={"place": "study", "person": "a scholar"})
            self.assertFalse(imagination["lived_fact"])
            self.assertFalse(dream["lived_fact"])
            self.assertFalse(dream["longitudinal_dream_continuity_proven"])
            self.assertEqual(dream["result"]["epistemic_status"], "dreamed_not_lived")
            self.assertFalse(dream["result"]["factual_memory_eligible"])
            reopened = BrainStore(root / "brain.sqlite3")
            self.assertIsNotNone(reopened.meta(
                "phantasmagorium:probe:" + imagination["record_id"]))
            self.assertIsNotNone(reopened.meta(
                "phantasmagorium:probe:" + dream["record_id"]))


if __name__ == "__main__":
    unittest.main()
