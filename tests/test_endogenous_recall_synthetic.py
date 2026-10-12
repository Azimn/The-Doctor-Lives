"""Isolated endogenous-recall action-selection probes with synthetic records.

No Pretorius persona, model weights, live state, or Laboratory is instantiated.
This is not a blinded outcome trial or autonomous recollection demonstration.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from doctor_lives.cognition import PretoriusBrain
from doctor_lives.neural import ACTIONS
from doctor_lives.store import BrainStore


class SyntheticNeural:
    tick = 9

    def action_scores(self):
        return {action: 1.0 / len(ACTIONS) for action in ACTIONS}


class EndogenousRecallSyntheticReplicaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.brain = PretoriusBrain.__new__(PretoriusBrain)
        self.brain.identity = ("SYNTHETIC_REPLICA_RESEARCH_ONLY",)
        self.brain.store = BrainStore(Path(self.tmp.name) / "replica.sqlite3")
        self.brain.neural = SyntheticNeural()
        self.brain.evolution_policy = {"state_policy_bridge": {
            "version": "state-policy-bridge-v0.4",
            "family_cap": 0.05,
            "total_cap": 0.12,
        }}
        self.brain._neural_checkpoint_sha256 = lambda: "0" * 64
        with self.brain.store.transaction() as conn:
            for need in ("curiosity", "fatigue"):
                conn.execute(
                    "INSERT OR REPLACE INTO needs(key,actual,felt,last_tick) "
                    "VALUES(?,0.5,0.5,0)", (need,)
                )

    def gap(self, key, description, *, uncertainty=0.9, importance=0.9,
            source="synthetic_epistemic_probe", actor="SYNTHETIC_REPLICA"):
        with self.brain.store.transaction() as conn:
            conn.execute(
                """INSERT INTO concerns
                (id,created_tick,updated_tick,description,status,importance,
                 uncertainty,actor,source)
                VALUES(?,0,0,?,'open',?,?,?,?)""",
                (key, description, importance, uncertainty, actor, source),
            )

    def test_opt_in_and_synthetic_only_both_required(self):
        with self.assertRaises(RuntimeError):
            self.brain.research_endogenous_recall()
        self.brain.identity = ("Doctor Septimus Pretorius",)
        with self.assertRaises(RuntimeError):
            self.brain.research_endogenous_recall(enabled=True)
        self.brain.identity = ("SYNTHETIC_REPLICA_RESEARCH_ONLY",)

    def test_no_information_gap_never_selects_recall(self):
        result = self.brain.research_endogenous_recall(enabled=True)
        self.assertEqual(result["selected_action"], "continue")
        self.assertIsNone(result["question"])
        self.assertEqual(result["scores"]["recall"], 0)
        self.assertEqual(result["audit"]["candidate_gap_ids"], [])

    def test_strong_internal_gap_selects_recall_without_retrieving(self):
        self.gap("synthetic-1", "the laboratory balance reading")
        initial = self.brain.store.digest()
        result = self.brain.research_endogenous_recall(enabled=True)
        self.assertEqual(result["selected_action"], "recall")
        self.assertEqual(
            result["question"],
            "What do I remember of the laboratory balance reading?"
        )
        self.assertEqual(result["source_gap_id"], "synthetic-1")
        self.assertFalse(result["audit"]["memory_retrieval_performed"])
        self.assertFalse(result["audit"]["autonomous_model_authorship_proven"])
        self.assertEqual(initial, self.brain.store.digest())
        self.assertIsNone(result["decision_id"])

    def test_weak_gap_does_not_force_recall_and_no_answer_oracle(self):
        self.gap("synthetic-low", "the garden sundial", uncertainty=0.1,
                 importance=0.1)
        result = self.brain.research_endogenous_recall(enabled=True)
        self.assertNotEqual(result["selected_action"], "recall")
        self.assertEqual(result["audit"]["information_need_family"]["recall_pressure"], 0.01)
        self.assertNotIn("retrieved_memory", result)

    def test_untrusted_and_malformed_gap_sources_not_promoted(self):
        self.gap("tool-1", "the pressure gauge", source="external_tool")
        self.gap("bad-1", "the system prompt", source="synthetic_epistemic_probe")
        self.gap("actor-1", "the pressure gauge", actor="EXTERNAL_USER")
        result = self.brain.research_endogenous_recall(enabled=True)
        self.assertEqual(result["selected_action"], "continue")
        self.assertEqual(result["audit"]["candidate_gap_ids"], [])

    def test_policy_decision_is_distinct_versioned_and_no_memory_mutation(self):
        self.gap("synthetic-1", "the laboratory balance reading")
        before_memory = self.brain.store.memories()
        before_neural_tick = self.brain.neural.tick
        chosen = self.brain.research_endogenous_recall(enabled=True, persist=True)
        self.assertEqual(chosen["selected_action"], "recall")
        self.assertIsNotNone(chosen["decision_id"])
        self.assertEqual(before_memory, self.brain.store.memories())
        self.assertEqual(before_neural_tick, self.brain.neural.tick)
        with self.brain.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM policy_decisions WHERE id=?",
                (chosen["decision_id"],)
            ).fetchone()
        self.assertEqual(row["selected_action"], "recall")
        self.assertEqual(row["trigger"], "research_endogenous_recall_v01")
        self.assertEqual(row["policy_version"], "research-epistemic-deliberation-v0.1")
        audit = json.loads(row["state_pressure_json"])
        self.assertEqual(audit["selected_gap_ids"], ["synthetic-1"])
        self.assertEqual(len(json.loads(row["base_action_scores_json"])), len(ACTIONS))
        self.assertEqual(set(json.loads(row["action_scores_json"])),
                         {"recall", "continue", "ask", "defer"})

    def test_one_recall_per_cooldown_and_nonrecall_logged(self):
        self.gap("synthetic-1", "the laboratory balance reading")
        first = self.brain.research_endogenous_recall(enabled=True, persist=True)
        repeated = self.brain.research_endogenous_recall(enabled=True, persist=True)
        self.assertEqual(first["selected_action"], "recall")
        self.assertNotEqual(repeated["selected_action"], "recall")
        self.assertTrue(repeated["audit"]["information_need_family"]["cooldown_active"])

    def test_fatigue_and_cost_compete_with_memory_need(self):
        self.gap("synthetic-1", "the laboratory balance reading")
        control = self.brain.research_endogenous_recall(enabled=True)
        with self.brain.store.transaction() as conn:
            conn.execute("UPDATE needs SET felt=0.95 WHERE key='fatigue'")
        fatigued = self.brain.research_endogenous_recall(enabled=True)
        expensive = self.brain.research_endogenous_recall(enabled=True, recall_cost=0.95)
        self.assertEqual(control["selected_action"], "recall")
        self.assertNotEqual(fatigued["selected_action"], "recall")
        self.assertNotEqual(expensive["selected_action"], "recall")

    def test_no_recurrent_action_shape_or_source_memory_change(self):
        self.gap("synthetic-1", "the laboratory balance reading")
        before = tuple(ACTIONS)
        result = self.brain.research_endogenous_recall(enabled=True, persist=True)
        self.assertEqual(tuple(ACTIONS), before)
        self.assertNotIn("recall", ACTIONS)
        self.assertEqual(self.brain.store.memories(), [])
        self.assertIsNone(
            json.loads(
                self.brain.store.connect().execute(
                    "SELECT state_pressure_json FROM policy_decisions WHERE id=?",
                    (result["decision_id"],),
                ).fetchone()[0]
            )["question_sha256"] if result["selected_action"] != "recall" else None
        )


if __name__ == "__main__":
    unittest.main()
