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

    def test_one_preview_writer_owns_the_mutex(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "three-organ-preview"
            with PreviewSceneJournal(root):
                with self.assertRaises(sqlite3.OperationalError):
                    with PreviewSceneJournal(root):
                        pass


if __name__ == "__main__":
    unittest.main()
