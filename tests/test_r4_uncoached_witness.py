"""No donor dependencies: independent witness must not mutate world or brain."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone

from tools.observe_uncoached_r4 import sample


class R4WitnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "state").mkdir()
        with sqlite3.connect(self.root / "laboratory.sqlite3") as db:
            for table in ("books_events", "rhythm_events", "embodied_events"):
                db.execute(f"CREATE TABLE {table}(event_id TEXT,event_hash TEXT)")
            db.execute("INSERT INTO rhythm_events VALUES ('act1','hash1')")
        with sqlite3.connect(self.root / "state/brain.sqlite3") as db:
            db.execute("CREATE TABLE policy_decisions(trigger TEXT,selected_action TEXT)")
            db.execute("CREATE TABLE memories(evidence_class TEXT,external INTEGER,source TEXT)")
            db.execute("INSERT INTO policy_decisions VALUES ('six_organ_lab_cycle','explore')")
            db.execute("INSERT INTO memories VALUES ('lived_runtime_memory',0,'laboratory-home:action:hash1')")
        self.status = self.root / "preview-status.json"
        self.status.write_text(json.dumps({
            "schema": "doctor-laboratory-preview-operator.v1", "status": "running",
            "last_heartbeat": "2026-10-31T17:00:00Z",
        }))
        (self.root / "preview-activity.jsonl").write_text(json.dumps({
            "event": "native_goal_goal_created",
            "fields": {"kind": "read_book", "goal_phase": "search"},
        }) + "\n")

    def test_independent_read_only_and_no_autonomy_credit(self):
        world = (self.root / "laboratory.sqlite3").read_bytes()
        brain = (self.root / "state/brain.sqlite3").read_bytes()
        result = sample(self.root, process_alive=True, elapsed_seconds=30,
                        baseline_world_receipts=1)
        self.assertEqual(result["world_receipt_delta_from_initial"], 0)
        self.assertEqual(result["brain"]["unverified_lived_action_rows"], 1)
        self.assertEqual(result["brain"]["policy_counts"]["six_organ_lab_cycle:explore"], 1)
        self.assertEqual(result["operator_ledger_diagnostic_only"]["last_native_event"]["goal_phase"], "search")
        self.assertFalse(result["source_authentication_performed"])
        self.assertFalse(result["autonomy_credit"])
        self.assertEqual((self.root / "laboratory.sqlite3").read_bytes(), world)
        self.assertEqual((self.root / "state/brain.sqlite3").read_bytes(), brain)

    def test_crash_stall_silent_skip_distinguished(self):
        self.assertEqual(sample(self.root, process_alive=False, elapsed_seconds=100,
                                baseline_world_receipts=1)["failure_class_candidate"], "crash")
        self.assertEqual(sample(self.root, process_alive=True, elapsed_seconds=100,
                                baseline_world_receipts=1)["failure_class_candidate"], "stall")
        status = json.loads(self.status.read_text())
        status["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        self.status.write_text(json.dumps(status))
        self.assertEqual(sample(self.root, process_alive=True, elapsed_seconds=650,
                                baseline_world_receipts=1)["failure_class_candidate"],
                         "silent_skip_candidate")

    def test_missing_original_world_table_fails_closed(self):
        with sqlite3.connect(self.root / "laboratory.sqlite3") as db:
            db.execute("DROP TABLE books_events")
        with self.assertRaisesRegex(RuntimeError, "Missing authoritative world table"):
            sample(self.root, process_alive=True, elapsed_seconds=1)

    def test_receipt_delta_is_not_provenance(self):
        result = sample(self.root, process_alive=True, elapsed_seconds=5,
                        baseline_world_receipts=0)
        self.assertEqual(result["world_receipt_delta_from_initial"], 1)
        self.assertFalse(result["source_authentication_performed"])
        self.assertFalse(result["autonomy_credit"])


if __name__ == "__main__":
    unittest.main()
