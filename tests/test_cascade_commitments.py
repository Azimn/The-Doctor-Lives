"""Real-host regression tests for the durable Laboratory commitment dispatcher."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

AVAILABLE = all(importlib.util.find_spec(x) is not None for x in
                ("pretorius_lab", "sensus_artificialis", "synthetic_ipseity"))


@unittest.skipUnless(AVAILABLE, "Pinned Laboratory and donor organs required")
class PersistentCommitmentLoop(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.book_library import BookLibrary
        from pretorius_lab.embodied_access import EmbodiedAccess
        from tools.run_cascade_articles_pilot import open_host

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.lab = SpatialHabitat.create(root / "world.sqlite3")
        library = BookLibrary(self.lab)
        library.initialize()
        library.install("book:007", edition_id="commitment-fixture-v1",
                        title="Task Reference", author="Synthetic Fixture",
                        pages=["Copper conducts electricity."],
                        source_class="original_fixture",
                        source_reference="authored commitment engineering case")
        self.port = EmbodiedAccess(self.lab)
        self.port.initialize(station="station:center")
        self.path = root / "three-organ-preview"
        self.host, _ = open_host(self.path, "cascade")
        self.addCleanup(lambda: self.host.close())

    def accept(self, **kwargs):
        return self.host.accept_laboratory_commitment(
            self.port, task_id="read-volume", book_id="book:007",
            expires_ms=100_000, max_actions=4, authorized=True, **kwargs)

    def service(self, **kwargs):
        return self.host.service_laboratory_commitment(
            self.port, task_id="read-volume", now_ms=10, authorized=True, **kwargs)

    def witness(self):
        from doctor_lives.cascade_laboratory import remember_look
        self.port.move("station:shelf:3")
        receipt = self.port.look()
        ids = remember_look(self.host, self.port, receipt)
        self.port.move("station:center")
        return receipt, ids

    def reopen(self):
        from tools.run_cascade_articles_pilot import open_host
        self.host.close()
        self.host, _ = open_host(self.path, "cascade")

    def doctor_row(self, commitment_id):
        with self.host._doctor.brain.store.connect() as db:
            row = db.execute(
                "SELECT status,outcome FROM commitments WHERE id=?", (commitment_id,)
            ).fetchone()
            return dict(row)

    def test_accept_wait_restart_unrelated_activity_and_complete_once(self):
        accepted = self.accept()
        self.assertEqual(accepted["status"], "waiting")
        self.reopen()
        self.host._doctor.brain.heartbeat(ticks=1)
        self.host._doctor.brain.save()
        body = self.port.verify()
        self.assertEqual(self.service()["status"], "waiting_prerequisite")
        self.assertEqual(self.port.verify(), body)
        self.assertIn(self.doctor_row(accepted["doctor_commitment_id"])["status"],
                      ("open", "overdue"))
        self.witness()
        self.reopen()
        result = self.service()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["actions"], 4)
        self.assertEqual(self.doctor_row(accepted["doctor_commitment_id"])["status"], "kept")
        revision = self.port.verify()["revision"]
        self.reopen()
        replay = self.service()
        self.assertEqual(replay["status"], "completed")
        self.assertTrue(replay["replayed"])
        self.assertEqual(self.port.verify()["revision"], revision)

    def test_memory_lesion_then_restoration_changes_dispatch(self):
        accepted = self.accept()
        _, ids = self.witness()
        store = self.host._doctor.brain.store
        mid = next(i for i in ids if store.get_memory(i)["source"].endswith("book:007"))
        self.reopen()
        store = self.host._doctor.brain.store
        with store.transaction() as db:
            store.archive_memory(db, mid, store.tick, "matched lesion")
            store.bump_state_version(db)
        self.assertEqual(self.service()["status"], "waiting_prerequisite")
        with store.transaction() as db:
            db.execute("UPDATE memories SET active=1 WHERE id=?", (mid,))
            store.bump_state_version(db)
        self.assertEqual(self.service()["status"], "completed")
        self.assertEqual(self.doctor_row(accepted["doctor_commitment_id"])["status"], "kept")

    def test_finite_permission_and_unforgeable_task_identity(self):
        before = self.port.verify()
        with self.assertRaises(PermissionError):
            self.host.accept_laboratory_commitment(
                self.port, task_id="read-volume", book_id="book:007",
                expires_ms=100_000, max_actions=4)
        accepted = self.accept()
        replay = self.accept()
        self.assertEqual(replay["doctor_commitment_id"], accepted["doctor_commitment_id"])
        self.assertTrue(replay["replayed"])
        with self.assertRaises(PermissionError):
            self.host.accept_laboratory_commitment(
                self.port, task_id="read-volume", book_id="book:006",
                expires_ms=100_000, max_actions=4, authorized=True)
        with self.assertRaises(PermissionError):
            self.host.service_laboratory_commitment(self.port, task_id="read-volume",
                                                    now_ms=10)
        self.assertEqual(self.port.verify(), before)

    def test_expiry_prevents_action_not_goal_erasure(self):
        accepted = self.accept()
        self.witness()
        old_revision = self.port.verify()["revision"]
        result = self.host.service_laboratory_commitment(
            self.port, task_id="read-volume", now_ms=100_000, authorized=True)
        self.assertEqual(result["status"], "authorization_expired")
        self.assertEqual(self.port.verify()["revision"], old_revision)
        self.assertIn(self.doctor_row(accepted["doctor_commitment_id"])["status"],
                      ("open", "overdue"))

    def test_changed_world_fails_closed_with_outstanding_commitment(self):
        accepted = self.accept()
        self.witness()
        self.lab.commit({"op": "place", "object_id": "book:007",
                         "anchor_id": "shelf:1/slot:1"})
        result = self.service()
        self.assertEqual(result["status"], "needs_review")
        self.assertIn(self.doctor_row(accepted["doctor_commitment_id"])["status"],
                      ("open", "overdue"))
        with self.assertRaises(RuntimeError):
            self.service()

    def test_interrupted_action_never_marks_commitment_complete(self):
        accepted = self.accept()
        self.witness()
        with patch.object(self.port, "move", side_effect=RuntimeError("disconnect")):
            with self.assertRaises(RuntimeError):
                self.service()
        self.assertIn(self.doctor_row(accepted["doctor_commitment_id"])["status"],
                      ("open", "overdue"))
        with self.assertRaises(RuntimeError):
            self.service()


if __name__ == "__main__":
    unittest.main()
