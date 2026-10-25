"""Red acceptance contracts: perception must never become world authority.

Research-only, disposable preview. These tests intentionally FAIL on PR #61's
exact head until Sensus/Doctor ingress preserves uncertainty. No production
state, donor source or Laboratory canonical history is modified.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

DONORS = all(importlib.util.find_spec(module) is not None for module in (
    "pretorius_lab", "sensus_artificialis", "synthetic_ipseity"
))


@unittest.skipUnless(DONORS, "pinned Laboratory, Sensus and Ipseity are required")
class EpistemicAuthorityContracts(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.book_library import BookLibrary
        from pretorius_lab.embodied_access import EmbodiedAccess
        from tools.run_cascade_articles_pilot import open_host
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.lab = SpatialHabitat.create(self.root / "laboratory.sqlite3")
        books = BookLibrary(self.lab)
        books.initialize()
        books.install(
            "book:007", edition_id="epistemic-fixture-v1",
            title="Source Volume", author="Test Fixture",
            pages=["World state is independently verified."],
            source_class="original_fixture",
            source_reference="research acceptance fixture",
        )
        self.actor = EmbodiedAccess(self.lab)
        self.actor.initialize(station="station:center")
        self.host, _ = open_host(self.root / "three-organ-preview", "cascade")
        self.addCleanup(self.host.close)

    def observed(self, event, attribute, value, *, channel="vision",
                 hint="similar-volume", features=(("shape", "rectangular"),)):
        from sensus_artificialis import Percept, Evidence
        return Percept(
            event_id=event, channel=channel, evidence=Evidence.OBSERVED,
            source_ref="trusted:" + event, tick=self.host._scene_tick,
            attribute=attribute, value=value, confidence=0.98,
            object_hint=hint, features=features,
        )

    def cycle(self, *items):
        grant = self.host.make_host_grant(
            permissions=frozenset({"observe"}), max_percepts=len(items),
        )
        return self.host.cycle(
            items, trusted_source_refs=frozenset(x.source_ref for x in items),
            now_ms=self.host._scene_tick * 1000, cascade_grant=grant,
        )

    def sensed_memories(self):
        return [
            m for m in self.host._doctor.brain.store.memories()
            if "trusted:" in m["source"]
            and ("preview-verified-world:" in m["source"]
                 or "preview-sensus-observed:" in m["source"])
        ]

    def assert_subject_observed_not_verified(self, items):
        self.assertTrue(items, "A valid Sensus sighting must remain visible as an observation")
        for memory in items:
            self.assertEqual(
                memory["kind"], "sensory_observation_unverified",
                "A matched/allowlisted Percept is not a Laboratory verified fact",
            )
            self.assertTrue(
                memory["source"].startswith("preview-sensus-observed:"),
                "Perception cannot use a world-verification source marker",
            )

    def test_similar_object_false_identity_changes_belief_not_world_ids(self):
        before = self.lab.verify()
        physical_book = self.lab.locate("book:007")
        first = self.cycle(self.observed(
            "visual-a", "volume location", "shelf three",
            features=(("shape", "rectangular"), ("binding", "brown")),
        ))
        second = self.cycle(self.observed(
            "visual-b", "volume location", "shelf one",
            hint="different-camera-hint",
            features=(("shape", "rectangular"), ("binding", "brown")),
        ))
        # An ambiguous/similar visual association is not an identity authority.
        self.assertEqual(self.lab.verify(), before)
        self.assertEqual(self.lab.locate("book:007"), physical_book)
        self.assertTrue(first["scene_object_ids"])
        self.assertTrue(second["scene_object_ids"])
        self.assert_subject_observed_not_verified(self.sensed_memories())

    def test_admitted_allowlisted_inventory_claim_cannot_create_inventory(self):
        before = self.lab.verify()
        claim = self.observed("six-bottles", "reagent bottle count", "six")
        result = self.cycle(claim)
        self.assertEqual(result["admitted_percepts"], 1)
        self.assertEqual(self.lab.verify(), before)
        self.assert_subject_observed_not_verified(self.sensed_memories())

    def test_cross_channel_shared_calibration_remains_observed_not_verified(self):
        before = self.lab.verify()
        wrong = (
            self.observed("wrong-visual", "research volume count", "six", channel="vision"),
            self.observed("wrong-instrument", "research volume count", "six",
                          channel="instrument"),
        )
        result = self.cycle(*wrong)
        self.assertEqual(result["admitted_percepts"], 2)
        self.assertEqual(self.lab.verify(), before)
        self.assert_subject_observed_not_verified(self.sensed_memories())
        # Distinct channels and source labels do not prove distinct calibration.
        self.assertFalse(any(
            m["kind"] == "world_record_verified" and "six" in m["text"]
            for m in self.host._doctor.brain.store.memories()
        ))


if __name__ == "__main__":
    unittest.main()
