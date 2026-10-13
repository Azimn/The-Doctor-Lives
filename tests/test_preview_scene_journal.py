"""Durable three-organ preview journal invariants, no donor installations needed."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from doctor_lives.preview_scene_journal import PreviewSceneConflict, PreviewSceneJournal


class SceneJournalAtomicityTests(unittest.TestCase):
    def test_scene_and_sensus_snapshot_commit_or_roll_back_together(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "three-organ-preview"
            with PreviewSceneJournal(root) as journal:
                # The scene payload serializes and is INSERTed first. The
                # snapshot fails while serializing the second statement.
                # An autocommit connection without explicit BEGIN would leave
                # a permanent orphan scene behind.
                with self.assertRaises(TypeError):
                    journal.begin(
                        {"scene_tick": 1, "operations": []},
                        {"last_tick": 1, "files": [object()]},
                    )
                self.assertIsNone(journal.active())
                self.assertIsNone(journal.snapshot())
                good = journal.begin(
                    {"scene_tick": 1, "operations": []},
                    {"last_tick": 1, "next_id": 2, "files": []},
                )
                self.assertEqual(good["stage"], "scene_built")
                self.assertEqual(journal.snapshot()["last_tick"], 1)
            with PreviewSceneJournal(root) as reopened:
                self.assertEqual(reopened.active()["id"], good["id"])
                self.assertEqual(reopened.snapshot()["next_id"], 2)

    def test_failed_journal_cursor_is_not_advanced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "three-organ-preview"
            with PreviewSceneJournal(root) as journal:
                row = journal.begin(
                    {"scene_tick": 1, "operations": [{"kind": "ingest"}]},
                    {"last_tick": 1, "next_id": 2, "files": []},
                )
                with self.assertRaises(PreviewSceneConflict):
                    journal.step(row["id"], 3)
                self.assertEqual(journal.active()["op_index"], 0)
                journal.prepare_ingress(row["id"], 0, 8)
                self.assertEqual(journal.active()["op_before_neural"], 8)
                journal.step(row["id"], 0)
                self.assertEqual(journal.active()["op_index"], 1)
                self.assertIsNone(journal.active()["op_before_neural"])

    def test_tampered_scene_payload_fails_closed_on_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "three-organ-preview"
            with PreviewSceneJournal(root) as journal:
                journal.begin(
                    {"scene_tick": 1, "operations": [{"kind": "ingest", "event": {"text": "safe"}}]},
                    {"last_tick": 1, "next_id": 2, "files": []},
                )
            with sqlite3.connect(root / "preview_scene_journal.sqlite3") as db:
                db.execute("UPDATE scenes SET payload=REPLACE(payload,'safe','forged')")
            with PreviewSceneJournal(root) as reopened:
                with self.assertRaisesRegex(PreviewSceneConflict, "scene payload integrity"):
                    reopened.active()

    def test_tampered_sensus_snapshot_fails_closed_on_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "three-organ-preview"
            with PreviewSceneJournal(root) as journal:
                journal.begin(
                    {"scene_tick": 1, "operations": []},
                    {"last_tick": 1, "next_id": 2, "files": []},
                )
            with sqlite3.connect(root / "preview_scene_journal.sqlite3") as db:
                db.execute("UPDATE sensus_state SET snapshot_json='{}'")
            with PreviewSceneJournal(root) as reopened:
                with self.assertRaisesRegex(PreviewSceneConflict, "Sensus snapshot integrity"):
                    reopened.snapshot()

    def test_tampered_persisted_decision_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "three-organ-preview"
            with PreviewSceneJournal(root) as journal:
                row = journal.begin(
                    {"scene_tick": 1, "operations": []},
                    {"last_tick": 1, "next_id": 2, "files": []},
                )
                journal.stage(row["id"], "scene_built", "admitted")
                journal.set_decision(row["id"], {"selected_action": "defer"})
            with sqlite3.connect(root / "preview_scene_journal.sqlite3") as db:
                db.execute(
                    "UPDATE scenes SET decision_json=?",
                    ('{"selected_action":"recall"}',),
                )
            with PreviewSceneJournal(root) as reopened:
                with self.assertRaisesRegex(PreviewSceneConflict, "policy decision integrity"):
                    reopened.active()

    def test_missing_integrity_hash_in_legacy_active_scene_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "three-organ-preview"
            with PreviewSceneJournal(root) as journal:
                row = journal.begin(
                    {"scene_tick": 1, "operations": []},
                    {"last_tick": 1, "next_id": 2, "files": []},
                )
            with sqlite3.connect(root / "preview_scene_journal.sqlite3") as db:
                db.execute(
                    "UPDATE scenes SET payload_sha256=NULL WHERE id=?", (row["id"],)
                )
            with PreviewSceneJournal(root) as reopened:
                with self.assertRaisesRegex(PreviewSceneConflict, "scene payload integrity"):
                    reopened.active()

    def test_one_preview_writer_owns_the_mutex(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "three-organ-preview"
            with PreviewSceneJournal(root):
                with self.assertRaises(sqlite3.OperationalError):
                    with PreviewSceneJournal(root):
                        pass


if __name__ == "__main__":
    unittest.main()
