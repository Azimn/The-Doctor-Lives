"""Adversarial contract tests for scripts/verify_day.py.

All fixture world bytes are synthetic and independently *cannot* pass the
production world verifier. Only these isolated tests patch the Lab checker.
The CI day witness must use actual source-pinned Laboratory implementations.
"""
import json
import pathlib
import shutil
import sqlite3
import tempfile
import unittest
from hashlib import sha256
from unittest.mock import patch

from scripts.verify_day import judge, stable, LAB_PIN, SCHEMA
from doctor_lives.neural import DEFAULT_CONFIG, PretoriusRecurrentSubstrate


def sqlite_file(p, ddl):
    db = sqlite3.connect(p)
    db.executescript(ddl)
    db.commit()
    return db


def canonical_policy(pid, selected, *, event_id=None, enabled=False, outcome=None):
    evidence = {
        "selector_authority": "original_noesis",
        "physical_authority": "none",
        "motor_authorization": "authorized" if event_id else "not_granted",
        "motor_event_id": event_id,
        "outcome_learning_enabled": enabled,
        "native_abstract_scores": {"explore": 0.4, "persist": 0.5},
        "used_outcome_memory_ids": [outcome] if outcome else [],
    }
    return (pid, "noesis_situated_choice", selected, "f" * 64,
            json.dumps(evidence), json.dumps({"experiment": 0.5, "repair": 0.7}))


class DayJudgeContractTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = pathlib.Path(temp.name)
        self.bundle = self.root / "day"
        self.bundle.mkdir()
        self.world = self.bundle / "world.sqlite3"
        self.brain = self.bundle / "brain.sqlite3"
        self.intents = self.bundle / "intent.sqlite3"
        self.world_db = sqlite_file(self.world, """
            CREATE TABLE rhythm_events(event_id TEXT PRIMARY KEY,envelope TEXT,event_hash TEXT);
        """)
        self.brain_db = sqlite_file(self.brain, """
            CREATE TABLE policy_decisions(id TEXT PRIMARY KEY,trigger TEXT,
              selected_action TEXT,neural_checkpoint_sha256 TEXT,
              state_pressure_json TEXT,action_scores_json TEXT);
            CREATE TABLE thoughts(id TEXT PRIMARY KEY,generated_by TEXT);
            CREATE TABLE memories(id TEXT PRIMARY KEY,source TEXT,active INTEGER,
              evidence_class TEXT,external INTEGER);
            CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT);
        """)
        self.intent_db = sqlite_file(self.intents, """
            CREATE TABLE doctor_action_intents(event_id TEXT PRIMARY KEY,
              request_json TEXT,status TEXT);
        """)
        self.addCleanup(self.world_db.close)
        self.addCleanup(self.brain_db.close)
        self.addCleanup(self.intent_db.close)
        self.events = []
        self.ids = []
        for i, action in enumerate(("experiment", "repair", "rest")):
            eid = "day-" + str(i)
            event = {"op": action, "args": {}, "subject": {"inner": "I did " + action}}
            digest = sha256(stable(event).encode()).hexdigest()
            self.world_db.execute("INSERT INTO rhythm_events VALUES (?,?,?)",
                                  (eid, stable(event), digest))
            self.intent_db.execute("INSERT INTO doctor_action_intents VALUES (?,?,?)",
                                   (eid, stable({"op": action, "args": {}}), "complete"))
            pid = "policy-" + str(i)
            self.brain_db.execute("INSERT INTO policy_decisions VALUES (?,?,?,?,?,?)",
                                  canonical_policy(pid, action, event_id=eid))
            self.brain_db.execute("INSERT INTO thoughts VALUES (?,?)",
                                  ("thought-" + str(i), "noesis_situated_choice:" + pid))
            self.brain_db.execute("INSERT INTO memories VALUES (?,?,?,?,?)",
                                  ("memory-" + str(i), "laboratory-home:action:" + digest,
                                   1, "lived_runtime_memory", 0))
            self.events.append(digest)
            self.ids.append(pid)
        goal = {"schema": "pretorius.native-rest-intention.v1",
                "id": "abcde01234567890abcdef12", "phase": "travel",
                "origin_policy_id": "policy-goal", "origin_thought_id": "thought-goal"}
        envelope = {"payload": goal, "sha256": sha256(stable(goal).encode()).hexdigest()}
        self.brain_db.execute("INSERT INTO meta VALUES (?,?)",
                              ("six_organ_native_rest_intention_v1", stable(envelope)))
        self.brain_db.execute("INSERT INTO policy_decisions VALUES (?,?,?,?,?,?)",
                              canonical_policy("policy-goal", "avoid"))
        self.brain_db.execute("INSERT INTO thoughts VALUES (?,?)",
                              ("thought-goal", "neural_policy:policy-goal"))
        self.ablation = []
        for i in range(20):
            a, b = "with-" + str(i), "without-" + str(i)
            self.brain_db.execute("INSERT INTO policy_decisions VALUES (?,?,?,?,?,?)",
                                  canonical_policy(a, "repair", enabled=True,
                                                   outcome="memory-0"))
            self.brain_db.execute("INSERT INTO policy_decisions VALUES (?,?,?,?,?,?)",
                                  canonical_policy(b, "experiment", enabled=False))
            self.ablation.append({"seed": i, "with_memory": a, "without_memory": b})
        self.world_db.commit()
        self.intent_db.commit()
        self.brain_db.commit()
        # The real judge requires a different ORIGINAL neural checkpoint and
        # original BrainStore per seed, not twenty labels on the same policy.
        for pair in self.ablation:
            seed = pair["seed"]
            directory = self.bundle / "trials" / str(seed)
            directory.mkdir(parents=True)
            (directory / "brain").mkdir()
            shutil.copy2(self.world, directory / "world.sqlite3")
            shutil.copy2(self.brain, directory / "brain" / "brain.sqlite3")
            cfg = dict(DEFAULT_CONFIG)
            cfg.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                       input_degree=4, action_population_size=8, seed=7500 + seed)
            neural_path = directory / "brain" / "pretorius_recurrent.npz"
            PretoriusRecurrentSubstrate(cfg).save(neural_path)
            checkpoint = sha256(neural_path.read_bytes()).hexdigest()
            with sqlite3.connect(directory / "brain" / "brain.sqlite3") as d:
                d.execute("UPDATE policy_decisions SET neural_checkpoint_sha256=?",
                          (checkpoint,))
            pair["trial_dir"] = "trials/" + str(seed)
            pair["seed"] = 7500 + seed
        self.world_db.commit()
        self.restart = {"signal": "SIGKILL", "exit_code": -9, "first_pid": 101,
                        "second_pid": 202, "before_goal": goal, "after_goal": goal,
                        "duplicate_world_receipts": 0, "duplicate_lived_memories": 0}
        self.manifest = {
            "schema": SCHEMA, "lab_pin": LAB_PIN,
            "world_db": "world.sqlite3", "brain_db": "brain.sqlite3",
            "intent_db": "intent.sqlite3", "host_opportunities": [{"tick": 1}],
            "restart": self.restart, "ablation": self.ablation,
            "random_baseline": "random",
        }
        baseline = self.bundle / "random"
        baseline.mkdir()
        shutil.copy2(self.world, baseline / "world.sqlite3")
        shutil.copy2(self.intents, baseline / "intent.sqlite3")
        # Genuine physical receipts but the random controller has no original
        # Noesis decision rows. It must fail the original mind's criterion.
        bd = sqlite_file(baseline / "brain.sqlite3", """
            CREATE TABLE policy_decisions(id TEXT,trigger TEXT,selected_action TEXT,
              neural_checkpoint_sha256 TEXT,state_pressure_json TEXT,action_scores_json TEXT);
            CREATE TABLE thoughts(id TEXT,generated_by TEXT);
            CREATE TABLE memories(id TEXT,source TEXT,active INTEGER,
              evidence_class TEXT,external INTEGER);
            CREATE TABLE meta(key TEXT,value TEXT);
        """)
        bd.close()
        (baseline / "day.json").write_text(json.dumps({
            **self.manifest, "random_baseline": None,
            "host_opportunities": [{"tick": 1}],
        }))
        self.save()

    def save(self):
        (self.bundle / "day.json").write_text(json.dumps(self.manifest))

    def evaluate(self):
        # Fixture-only. Production judge ALWAYS verifies pinned Git source and
        # calls real Lab own cross-ledger validators before reading rows.
        with patch("scripts.verify_day.verified_lab"):
            return judge(self.bundle, self.root)

    def test_complete_contract_fixture_passes(self):
        self.assertTrue(self.evaluate()["pass"], self.evaluate())

    def test_lab_read_only_look_does_not_require_motor_policy(self):
        # Real Laboratory's DailyRhythm.look() writes a hash-chained LOOK
        # receipt even though no action was submitted to DoctorHomeBridge.
        event = {"op": "look", "args": {}, "subject": {"inner": "I observe"}}
        hash_value = sha256(stable(event).encode()).hexdigest()
        self.world_db.execute(
            "INSERT INTO rhythm_events VALUES (?,?,?)",
            ("source-read-only-look", stable(event), hash_value),
        )
        self.world_db.commit()
        self.assertTrue(self.evaluate()["pass"], self.evaluate())

    def test_unclaimed_real_lab_physical_action_still_fails(self):
        event = {"op": "experiment", "args": {}, "subject": {"inner": "I act"}}
        hash_value = sha256(stable(event).encode()).hexdigest()
        self.world_db.execute(
            "INSERT INTO rhythm_events VALUES (?,?,?)",
            ("unowned-experiment", stable(event), hash_value),
        )
        self.world_db.commit()
        result = self.evaluate()
        self.assertFalse(result["pass"])
        self.assertIn("b", result["failures"])

    def test_host_feeding_next_action_cannot_pass(self):
        self.manifest["host_opportunities"] = [{"tick": 1, "next_action": "repair"}]
        self.save()
        result = self.evaluate()
        self.assertFalse(result["pass"])
        self.assertIn("b", result["failures"])

    def test_nested_host_goal_and_destination_are_rejected(self):
        self.manifest["host_opportunities"] = [{"next": [{"destination": "station:bench"}]}]
        self.save()
        self.assertIn("b", self.evaluate()["failures"])

    def test_missing_noesis_row_fails_even_with_genuine_world_receipt(self):
        self.brain_db.execute("DELETE FROM policy_decisions WHERE id=?", (self.ids[0],))
        self.brain_db.commit()
        self.assertIn("b", self.evaluate()["failures"])

    def test_relabelled_world_hash_fails(self):
        self.world_db.execute("UPDATE rhythm_events SET event_hash=? WHERE event_id=?",
                              ("0" * 64, "day-0"))
        self.world_db.commit()
        with self.assertRaisesRegex(Exception, "tampered world receipt"):
            self.evaluate()

    def test_duplicate_lived_memory_fails(self):
        self.brain_db.execute("INSERT INTO memories VALUES (?,?,?,?,?)",
                              ("duplicate", "laboratory-home:action:" + self.events[0],
                               1, "lived_runtime_memory", 0))
        self.brain_db.commit()
        self.assertIn("d", self.evaluate()["failures"])

    def test_no_hard_kill_fails_goal_gate(self):
        self.manifest["restart"]["exit_code"] = 0
        self.save()
        self.assertIn("c", self.evaluate()["failures"])

    def test_twenty_seed_ablation_cannot_be_faked_by_repeated_seed(self):
        self.manifest["ablation"][1]["seed"] = 0
        self.save()
        self.assertIn("e", self.evaluate()["failures"])

    def test_memory_lesion_must_change_distribution(self):
        for pair in self.ablation:
            trial = self.bundle / pair["trial_dir"] / "brain" / "brain.sqlite3"
            with sqlite3.connect(trial) as db:
                db.execute("UPDATE policy_decisions SET selected_action='repair' WHERE id=?",
                           (pair["without_memory"],))
        self.assertIn("e", self.evaluate()["failures"])

    def test_missing_random_controller_bundle_is_not_a_successful_baseline(self):
        self.manifest["random_baseline"] = "nonexistent"
        self.save()
        self.assertIn("g", self.evaluate()["failures"])

    def test_two_task_kinds_do_not_pass(self):
        self.world_db.execute("DELETE FROM rhythm_events WHERE event_id='day-2'")
        self.intent_db.execute("DELETE FROM doctor_action_intents WHERE event_id='day-2'")
        self.world_db.commit()
        self.intent_db.commit()
        self.assertIn("a", self.evaluate()["failures"])

    def test_rest_or_verified_conflict_is_required(self):
        self.world_db.execute("UPDATE rhythm_events SET envelope=?,event_hash=? WHERE event_id='day-2'",
                              (stable({"op": "clean", "args": {}}),
                               sha256(stable({"op": "clean", "args": {}}).encode()).hexdigest()))
        self.intent_db.execute("UPDATE doctor_action_intents SET request_json=? WHERE event_id='day-2'",
                               (stable({"op": "clean", "args": {}}),))
        self.brain_db.execute("UPDATE policy_decisions SET selected_action='clean' WHERE id=?",
                              (self.ids[2],))
        self.brain_db.execute("UPDATE memories SET source=? WHERE id='memory-2'",
                              ("laboratory-home:action:" +
                               sha256(stable({"op": "clean", "args": {}}).encode()).hexdigest(),))
        self.world_db.commit()
        self.intent_db.commit()
        self.brain_db.commit()
        self.assertIn("f", self.evaluate()["failures"])


if __name__ == "__main__":
    unittest.main()
