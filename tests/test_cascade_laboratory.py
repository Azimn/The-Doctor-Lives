"""Real host and Laboratory consequences, not evidence-boolean fixtures."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

AVAILABLE = all(importlib.util.find_spec(x) is not None for x in
                ("pretorius_lab", "sensus_artificialis", "synthetic_ipseity"))


@unittest.skipUnless(AVAILABLE, "Pinned Laboratory and organ donors required")
class LaboratoryLoop(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.book_library import BookLibrary
        from pretorius_lab.embodied_access import EmbodiedAccess
        from tools.run_cascade_articles_pilot import open_host
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.lab = SpatialHabitat.create(self.root / "world.sqlite3")
        library = BookLibrary(self.lab)
        library.initialize()
        library.install("book:007", edition_id="loop-fixture-v1", title="Task Reference",
                        author="Synthetic Fixture", pages=["Copper conducts electricity."],
                        source_class="original_fixture", source_reference="authored engineering case")
        self.port = EmbodiedAccess(self.lab)
        self.port.initialize(station="station:center")
        self.path = self.root / "three-organ-preview"
        self.host, _ = open_host(self.path, "cascade")
        self.addCleanup(lambda: self.host.close())

    def witness(self):
        from doctor_lives.cascade_laboratory import remember_look
        self.port.move("station:shelf:3")
        receipt = self.port.look()
        ids = remember_look(self.host, self.port, receipt)
        self.port.move("station:center")
        return receipt, ids

    def run_task(self, name="read", budget=4, **kwargs):
        return self.host.laboratory_read(self.port, task_id=name, book_id="book:007",
                                         max_actions=budget, authorized=True, **kwargs)

    def test_restart_changes_real_action_and_source_read_with_lesion_restoration(self):
        from tools.run_cascade_articles_pilot import open_host
        _, ids = self.witness()
        self.host.close()
        self.host, _ = open_host(self.path, "cascade")
        store = self.host._doctor.brain.store
        target = next(i for i in ids if store.get_memory(i)["source"].endswith("book:007"))
        with store.transaction() as db:
            store.archive_memory(db, target, store.tick, "engineering memory intervention")
            store.bump_state_version(db)
        missing = self.run_task("lesion")
        self.assertFalse(missing["success"])
        self.assertEqual(missing["actions"][0]["argument"], "station:shelf:1")
        with store.transaction() as db:
            db.execute("UPDATE memories SET active=1 WHERE id=?", (target,))
            store.bump_state_version(db)
        self.port.move("station:center")
        restored = self.run_task("restored")
        self.assertTrue(restored["success"])
        self.assertEqual(restored["actions"][0]["argument"], "station:shelf:3")
        self.assertEqual(restored["actions_used"], 4)
        self.assertEqual(restored["page_text"], "Copper conducts electricity.")
        outcome = store.get_memory(restored["outcome_memory_id"])
        self.assertIn("Copper conducts electricity", outcome["text"])
        self.assertTrue(outcome["source"].startswith("laboratory-read:"))

    def test_budget_and_replay_are_persistent(self):
        from tools.run_cascade_articles_pilot import open_host
        self.witness()
        first = self.run_task()
        revision = self.port.verify()["revision"]
        self.host.close()
        self.host, _ = open_host(self.path, "cascade")
        self.assertEqual(self.run_task(), first)
        self.assertEqual(self.port.verify()["revision"], revision)
        with self.assertRaises(PermissionError):
            self.run_task(budget=5)

    def test_authorization_and_invalid_budgets_cannot_move_actor(self):
        before = self.port.verify()
        with self.assertRaises(PermissionError):
            self.host.laboratory_read(self.port, task_id="x", book_id="book:007", max_actions=4)
        for value in (True, 0, 41, 4.0):
            with self.assertRaises(ValueError):
                self.run_task(budget=value)
        self.assertEqual(self.port.verify(), before)

    def test_forged_receipt_and_text_cannot_create_a_sighting(self):
        from doctor_lives.cascade_laboratory import remember_look, remembered_shelf
        self.port.move("station:shelf:3")
        view = self.port.look()
        forged = copy.deepcopy(view)
        forged["offered_payload"]["nearby_objects"] = []
        with self.assertRaises(PermissionError):
            remember_look(self.host, self.port, forged)
        self.assertIsNone(remembered_shelf(self.host, self.port, "book:007"))
        remember_look(self.host, self.port, view)
        memory = remembered_shelf(self.host, self.port, "book:007")["memory_id"]
        with self.host._doctor.brain.store.transaction() as db:
            db.execute("UPDATE memories SET text='I see research volume 7 on shelf 1.' WHERE id=?", (memory,))
        self.assertIsNone(remembered_shelf(self.host, self.port, "book:007"))

    def test_stale_memory_requires_new_local_evidence_and_updates_search_prior(self):
        from doctor_lives.cascade_laboratory import remembered_shelf
        self.witness()
        self.lab.commit({"op": "place", "object_id": "book:007", "anchor_id": "shelf:1/slot:1"})
        failed = self.run_task("stale", budget=2)
        self.assertFalse(failed["success"])
        self.assertIsNone(remembered_shelf(self.host, self.port, "book:007"))
        self.port.move("station:center")
        found = self.run_task("search", budget=4)
        self.assertTrue(found["success"])
        self.assertEqual(remembered_shelf(self.host, self.port, "book:007")["station"], "station:shelf:1")

    def test_same_policy_handles_a_different_book_and_page(self):
        from pretorius_lab.book_library import BookLibrary
        BookLibrary(self.lab).install(
            "book:006", edition_id="other-fixture-v1", title="Another Reference",
            author="Synthetic Fixture", pages=["Glass transmits light."],
            source_class="original_fixture", source_reference="authored transfer regression")
        self.witness()
        result = self.host.laboratory_read(self.port, task_id="other-book", book_id="book:006",
                                           max_actions=4, authorized=True)
        self.assertTrue(result["success"])
        self.assertEqual(result["page_text"], "Glass transmits light.")

    def test_replaying_archived_sighting_never_reactivates_memory(self):
        from doctor_lives.cascade_laboratory import remember_look, remembered_shelf
        receipt, ids = self.witness()
        store = self.host._doctor.brain.store
        for memory in ids:
            with store.transaction() as db:
                store.archive_memory(db, memory, store.tick, "controlled archival")
        count = len(store.memories(False))
        remember_look(self.host, self.port, receipt)
        self.assertEqual(len(store.memories(False)), count)
        self.assertIsNone(remembered_shelf(self.host, self.port, "book:007"))

    def test_external_failure_blocks_retry_and_new_task(self):
        self.witness()
        with patch.object(self.port, "move", side_effect=RuntimeError("connection interrupted")):
            with self.assertRaises(RuntimeError):
                self.run_task()
        with self.assertRaises(RuntimeError):
            self.host._cascade_background.assert_reconciled()
        for name in ("read", "new-task"):
            with self.assertRaises(RuntimeError):
                self.run_task(name)


if __name__ == "__main__":
    unittest.main()
