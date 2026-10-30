"""Source-backed causal memory ablation for situated book preference.

A REAL Laboratory physically holds both volumes in the SAME shelf scene. One
actual physical read enters the original Doctor BrainStore. Memory toggling
without any further world actions tests if autobiographical continuity changes
which still-visible book attracts his next exploratory attention.

No host-supplied 'choose book 007' action or post-hoc success definition.
This is only a bounded exploration-target selection mechanism, not an
autonomously invented goal or a superiority result against an equal ledger.
"""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path
import unittest

from doctor_lives.autobiographical_book_preference import choose_visible_book
from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.neural import DEFAULT_CONFIG

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


def config():
    c = dict(DEFAULT_CONFIG)
    c.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    return c


@unittest.skipUnless(HAS_LAB, "Requires real pinned physical Laboratory")
class AutobiographicalBookSelectionTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        from pretorius_lab.book_library import BookLibrary

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.world = SpatialHabitat.create(root / "world.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.port = PretoriusBrainPort(root / "brain", neural_config=config())
        self.subject = SubjectPort(self.world)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        self.library = BookLibrary(self.world)
        self.library.initialize()
        for number in (1, 7):
            self.library.install(
                f"book:{number:03d}",
                edition_id=f"original-book-{number}",
                title=f"Research Volume {number}",
                author="Lab Fixture Author",
                pages=[f"This is the actual page of volume {number}."],
                source_class="original_fixture",
                source_reference="research causal ablation, physically installed",
                event_id=f"install-preference-{number}",
            )
        # No exercise may inspect an unvisited shelf to select a target.
        self.bridge.act(
            "walk", event_id="preference-to-center", station="station:center"
        )
        self.bridge.act(
            "walk", event_id="preference-to-shelf", station="station:shelf:3"
        )
        self.scene = self.subject.embodied.look()
        self.options = sorted(
            item["object_id"] for item in self.scene["offered_payload"]["nearby_objects"]
            if item["object_id"] in ("book:001", "book:007")
        )
        self.assertEqual(self.options, ["book:001", "book:007"])

    def selection(self, **kwargs):
        return choose_visible_book(
            self.options, store=self.port.brain.store,
            world=self.world, **kwargs,
        )

    def read_first(self):
        self.bridge.act(
            "book", event_id="preference-open-001",
            book_id="book:001", operation="open",
        )
        result = self.bridge.act(
            "book", event_id="preference-read-001",
            book_id="book:001", operation="read",
        )
        memory = self.port.brain.store.get_memory(result["memory_id"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        self.assertIn("This is the actual page of volume 1.", memory["text"])
        return result["memory_id"]

    def test_recalled_read_changes_selection_then_lesion_restores_baseline(self):
        self.assertEqual(self.selection(), "book:001")
        read_id = self.read_first()
        before_world = self.subject.verify()["world_epoch"]
        with self.world._open() as db:
            before_book_events = db.execute(
                "SELECT count(*) FROM books_events WHERE "
                "json_extract(payload, '$.action.op')='read'"
            ).fetchone()[0]
        self.assertEqual(before_book_events, 1)
        self.assertEqual(self.selection(), "book:007")
        self.assertEqual(self.selection(memory_enabled=False), "book:001")
        self.port.save()
        reopened = PretoriusBrainPort(self.port.brain.state_dir)
        self.port = reopened
        self.assertEqual(self.selection(), "book:007")
        # Archived memory is a controlled research lesion, never a real
        # Doctor forgetting or a change to the actual physical world.
        with self.port.brain.store.transaction() as db:
            self.port.brain.store.archive_memory(
                db, read_id, self.port.brain.store.tick,
                "experimental reversible memory lesion",
            )
            self.port.brain.store.bump_state_version(db)
        self.assertEqual(self.selection(), "book:001")
        with self.port.brain.store.transaction() as db:
            db.execute("UPDATE memories SET active=1 WHERE id=?", (read_id,))
            self.port.brain.store.bump_state_version(db)
        self.assertEqual(self.selection(), "book:007")
        self.assertEqual(self.subject.verify()["world_epoch"], before_world)
        with self.world._open() as db:
            after = db.execute(
                "SELECT count(*) FROM books_events WHERE "
                "json_extract(payload, '$.action.op')='read'"
            ).fetchone()[0]
        self.assertEqual(after, 1)
        print("AUTOBIOGRAPHICAL_BOOK_PREFERENCE_ABLATION="
              "physical_read_001=1; observed_books=2; "
              "memory=007; no_memory=001; lesioned=001; restored=007; "
              "unchanged_world=True")

    def test_reported_fake_read_cannot_bias_selection(self):
        # A projected report is remembered as a report, not a physical READ.
        statement = self.port.ingest({
            "channel": "world",
            "text": "Someone claims I read volume one already.",
            "source": "unverified-told-book-history",
        })
        self.assertEqual(
            self.port.brain.store.get_memory(statement["memory_id"])["evidence_class"],
            "external_statement",
        )
        self.assertEqual(self.selection(), "book:001")
        with self.assertRaises(ValueError):
            choose_visible_book(["book:001", "hidden:world"], 
                                store=self.port.brain.store, world=self.world)

    def test_repeated_read_is_not_a_second_cognitive_preference_event(self):
        read_id = self.read_first()
        self.assertEqual(self.selection(), "book:007")
        same = self.bridge.act(
            "book", event_id="preference-read-001",
            book_id="book:001", operation="read",
        )
        self.assertEqual(same["status"], "already_admitted")
        self.assertEqual(same["memory_id"], read_id)
        self.assertEqual(self.selection(), "book:007")


if __name__ == "__main__":
    unittest.main()
