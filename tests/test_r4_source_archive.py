"""Source archive regressions, independent of installed Pretorius donors."""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from tools.archive_r4_source_evidence import capture


class SourceArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        (self.workspace / "state").mkdir(parents=True)
        self.archive = self.root / "source-evidence"
        self.connections = []
        for name in ("laboratory.sqlite3", "state/brain.sqlite3"):
            db = sqlite3.connect(self.workspace / name)
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE events (id TEXT PRIMARY KEY)")
            db.execute("INSERT INTO events VALUES ('original-source-event')")
            db.commit()
            self.connections.append(db)
        (self.workspace / "preview-activity.jsonl").write_text(
            '{"event":"operator_start","external_input":true}\n', encoding="utf-8")
        self.addCleanup(lambda: [db.close() for db in self.connections])

    def test_captures_committed_wal_and_original_operator_ledger(self):
        before = (self.workspace / "preview-activity.jsonl").read_bytes()
        result = capture(self.workspace, self.archive)
        self.assertFalse(result["autonomy_credit"])
        self.assertFalse(result["independent_qa_review_performed"])
        self.assertEqual(len(result["files"]), 3)
        for filename in ("original-laboratory.sqlite3", "canonical-brain.sqlite3"):
            with sqlite3.connect(self.archive / filename) as db:
                self.assertEqual(db.execute("SELECT id FROM events").fetchone(),
                                 ("original-source-event",))
            self.assertEqual(result["files"][filename]["sha256"],
                             hashlib.sha256((self.archive / filename).read_bytes()).hexdigest())
        self.assertEqual((self.archive / "preview-activity.jsonl").read_bytes(), before)
        self.assertEqual(json.loads((self.archive / "manifest.json").read_text()), result)
        with self.assertRaises(FileExistsError):
            capture(self.workspace, self.archive)

    def test_missing_original_source_fails_without_fabrication(self):
        (self.workspace / "preview-activity.jsonl").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "preview-activity.jsonl"):
            capture(self.workspace, self.archive)
        self.assertFalse(self.archive.exists())

    def test_rejects_archive_inside_live_workspace(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            capture(self.workspace, self.workspace / "evidence")


if __name__ == "__main__":
    unittest.main()
