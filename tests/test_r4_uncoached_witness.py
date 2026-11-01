"""No donor dependencies: independent witness must not mutate world or brain."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone

from tools.observe_uncoached_r4 import inspect_neural_origins, inspect_native_policy_pressure, sample


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

    def test_no_situated_goal_retains_source_tendency_without_r4_credit(self):
        # The installed operator must not erase Noesis's actual tendency on
        # a failed goal opportunity. This is a forwarding test, NOT evidence
        # of autonomous goal creation, physical action, or a real donor run.
        from unittest.mock import patch
        from doctor_lives.preview_native import native_step

        source = {
            "receipts": [{
                "status": "no_situated_goal", "kind": None, "goal_id": None,
                "memory_id": None, "selected_tendency": "persist",
            }],
            "same_original_brain": True,
            "original_world_epoch_unchanged": True,
        }
        with patch("doctor_lives.lab_runtime.run_native_laboratory",
                   return_value=source) as native:
            record = native_step(
                self.root / "state", self.root / "laboratory.sqlite3",
                self.root / "unopened-affectus-source")
        native.assert_called_once()
        self.assertEqual(record["status"], "no_situated_goal")
        self.assertEqual(record["selected_tendency"], "persist")
        self.assertIsNone(record["goal_id"])
        self.assertIsNone(record["kind"])
        self.assertFalse(record["source_attestation_independent"])
        self.assertIsNone(record["operator_supplied_goal"])

    def test_external_neural_origin_snapshot_is_read_only_and_not_causal_credit(self):
        # A consistent canonical goal is only an observed database fact.
        # A coordinated rewrite can satisfy strings and hashes; independent
        # temporal and original-world custody must still be evaluated.
        import hashlib
        with sqlite3.connect(self.root / "state/brain.sqlite3") as db:
            db.execute("ALTER TABLE policy_decisions ADD COLUMN id TEXT")
            db.execute("UPDATE policy_decisions SET id='p-real'")
            db.execute("CREATE TABLE thoughts(id TEXT,generated_by TEXT)")
            db.execute("INSERT INTO thoughts VALUES('t-real','neural_policy:p-real')")
            db.execute("CREATE TABLE meta(key TEXT,value TEXT)")
            goal = {
                "id": "g-real", "phase": "travel",
                "origin_policy_id": "p-real", "origin_thought_id": "t-real",
            }
            digest = hashlib.sha256(json.dumps(
                goal, sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False,
            ).encode("utf-8")).hexdigest()
            db.execute("INSERT INTO meta VALUES(?,?)", (
                "six_organ_native_work_intention_v1",
                json.dumps({"payload": goal, "sha256": digest}),
            ))
        before = (self.root / "state/brain.sqlite3").read_bytes()
        snapshot = inspect_neural_origins(self.root)
        self.assertEqual(snapshot["work"]["goal_id"], "g-real")
        self.assertTrue(snapshot["work"]["record_consistency_only"])
        self.assertEqual((self.root / "state/brain.sqlite3").read_bytes(), before)
        with sqlite3.connect(self.root / "state/brain.sqlite3") as db:
            db.execute("UPDATE policy_decisions SET trigger='host_scheduled'")
        self.assertFalse(inspect_neural_origins(self.root)["work"]["record_consistency_only"])

    def test_original_neural_policy_pressure_is_read_only_and_never_r4_credit(self):
        # Synthetic fixture mirrors the exact original BrainStore policy_decisions
        # column layout and stores scores in canonical top-level JSON columns.
        # This tests read-only formatting, NEVER grants autonomous R4 credit.
        with sqlite3.connect(self.root / "state/brain.sqlite3") as db:
            db.execute("DROP TABLE policy_decisions")
            db.execute("""CREATE TABLE policy_decisions(
                id TEXT PRIMARY KEY, tick INTEGER, created_at TEXT, trigger TEXT,
                selected_action TEXT, base_action_scores_json TEXT,
                state_pressure_json TEXT, action_scores_json TEXT,
                candidate_record_ids_json TEXT, selected_record_ids_json TEXT,
                neural_tick INTEGER, neural_checkpoint_sha256 TEXT,
                policy_version TEXT)""")
            rows = [
                ("p1", "explore",
                 {"avoid": 0.2, "explore": 0.7, "private_thought": "never forward"},
                 {"avoid": 0.45, "explore": 0.45},
                 {"combined": {"avoid": -0.03, "explore": 0.05},
                  "private_thought": "secret"}),
                ("p2", "avoid",
                 {"avoid": 0.8, "persist": 0.1},
                 {"avoid": 0.5, "persist": 0.5},
                 {"combined": {"avoid": 0.03, "persist": -0.02}}),
            ]
            for pid, chosen, scores, base, pressure in rows:
                db.execute("""INSERT INTO policy_decisions(
                    id,trigger,selected_action,action_scores_json,
                    base_action_scores_json,state_pressure_json)
                    VALUES(?,?,?,?,?,?)""",
                    (pid, "six_organ_lab_cycle", chosen,
                     json.dumps(scores), json.dumps(base), json.dumps(pressure)))
        before = (self.root / "state/brain.sqlite3").read_bytes()
        diagnostic = inspect_native_policy_pressure(self.root, limit=2)
        self.assertTrue(diagnostic["available"])
        self.assertEqual([x["selected_tendency"] for x in diagnostic["recent_decisions"]],
                         ["explore", "avoid"])
        self.assertEqual(diagnostic["recent_decisions"][0]["candidate_scores"],
                         {"action_scores": {"avoid": 0.2, "explore": 0.7},
                          "base_action_scores": {"avoid": 0.45, "explore": 0.45},
                          "pressure_combined": {"avoid": -0.03, "explore": 0.05}})
        self.assertFalse(diagnostic["autonomy_credit"])
        self.assertFalse(diagnostic["causal_neural_origin_proven"])
        self.assertNotIn("private_thought", json.dumps(diagnostic))
        self.assertEqual((self.root / "state/brain.sqlite3").read_bytes(), before)
        witness = sample(self.root, process_alive=True, elapsed_seconds=30,
                         baseline_world_receipts=1)
        self.assertEqual(witness["brain"]["native_policy_pressure_diagnostic"],
                         diagnostic)
        with self.assertRaises(ValueError):
            inspect_native_policy_pressure(self.root, limit=1000)

    def test_real_archived_brainstore_nonempty_candidate_scores(self):
        """Regression against exact archived real BrainStore, never a synthetic database.

        Set PRETORIUS_ARCHIVED_BRAINSTORE to the extracted canonical-brain.sqlite3
        from GitHub Actions artifact 13085736490 (PR #108 run 41310421608).
        Ordinary CI without that real archive skips this check, never fabricates it.
        """
        import hashlib
        import os
        import shutil
        archive = os.environ.get("PRETORIUS_ARCHIVED_BRAINSTORE")
        if not archive:
            self.skipTest("Real archived BrainStore required: set PRETORIUS_ARCHIVED_BRAINSTORE")
        archived = Path(archive)
        self.assertTrue(archived.is_file(), "Missing genuine archived BrainStore")
        with sqlite3.connect(archived.absolute().as_uri() + "?mode=ro", uri=True) as db:
            columns = {row[1] for row in db.execute("PRAGMA table_info(policy_decisions)")}
            self.assertTrue({"action_scores_json", "base_action_scores_json"}.issubset(columns))
            self.assertGreater(db.execute(
                "SELECT COUNT(*) FROM policy_decisions WHERE trigger='six_organ_lab_cycle'"
            ).fetchone()[0], 0)
        target = self.root / "state" / "brain.sqlite3"
        shutil.copyfile(archived, target)
        source_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        diagnostic = inspect_native_policy_pressure(self.root, limit=16)
        self.assertTrue(diagnostic["available"])
        self.assertTrue(diagnostic["recent_decisions"])
        self.assertTrue(all(
            item["candidate_scores"].get("action_scores")
            and item["candidate_scores"].get("base_action_scores")
            for item in diagnostic["recent_decisions"]
        ), "Original BrainStore candidate score columns yielded empty observer results")
        self.assertFalse(diagnostic["autonomy_credit"])
        self.assertFalse(diagnostic["causal_neural_origin_proven"])
        self.assertNotIn("private_thought", json.dumps(diagnostic))
        self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), source_hash)

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



class R4GracefulStopObservationTests(unittest.TestCase):
    def test_late_authentic_completion_is_observed_before_process_exit(self):
        """A real change during stop must be sampled LIVE, not posthumously."""
        from unittest.mock import patch
        from tools.run_uncoached_r4_trial import _stop_with_live_origin_sampling

        clock = {"tick": 0}
        class Operator:
            def poll(self):
                return None if clock["tick"] < 5 else 0
        class Stop:
            returncode = None
            def poll(self):
                if clock["tick"] >= 4:
                    self.returncode = 0
                return self.returncode
            def communicate(self, timeout=None):
                return ("stopped", "")
            def kill(self):
                self.returncode = -9

        observed = []
        def capture(alive):
            observed.append((clock["tick"] >= 2, alive))
        def advance(_):
            clock["tick"] += 1

        with patch("tools.run_uncoached_r4_trial.subprocess.Popen", return_value=Stop()), \
             patch("tools.run_uncoached_r4_trial.time.monotonic",
                   side_effect=lambda: float(clock["tick"])), \
             patch("tools.run_uncoached_r4_trial.time.sleep", side_effect=advance):
            code, error = _stop_with_live_origin_sampling(
                Operator(), ["preview-stop"], capture, timeout_seconds=20
            )
        self.assertEqual((code, error), (0, ""))
        self.assertIn((True, True), observed)
        # The last sample is taken after the actual process exit.
        self.assertEqual(observed[-1][1], False)

    def test_postmortem_change_is_never_reported_alive(self):
        """An event appearing only after exit cannot earn an alive witness."""
        from unittest.mock import patch
        from tools.run_uncoached_r4_trial import _stop_with_live_origin_sampling
        clock = {"tick": 0}
        class Operator:
            def poll(self):
                return None if clock["tick"] < 2 else 0
        class Stop:
            returncode = None
            def poll(self):
                if clock["tick"] >= 4:
                    self.returncode = 0
                return self.returncode
            def communicate(self, timeout=None):
                return ("stopped", "")
            def kill(self):
                self.returncode = -9
        observed = []
        with patch("tools.run_uncoached_r4_trial.subprocess.Popen", return_value=Stop()), \
             patch("tools.run_uncoached_r4_trial.time.monotonic",
                   side_effect=lambda: float(clock["tick"])), \
             patch("tools.run_uncoached_r4_trial.time.sleep",
                   side_effect=lambda _: clock.__setitem__("tick", clock["tick"] + 1)):
            code, error = _stop_with_live_origin_sampling(
                Operator(), ["preview-stop"],
                lambda alive: observed.append((clock["tick"] >= 3, alive)),
                timeout_seconds=20,
            )
        self.assertEqual((code, error), (0, ""))
        self.assertFalse(any(complete and alive for complete, alive in observed))


if __name__ == "__main__":
    unittest.main()
