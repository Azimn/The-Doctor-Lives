"""Actual source-backed synthetic outcome test for endogenous-recall policy."""
from __future__ import annotations

from contextlib import closing
import tempfile
import unittest
from pathlib import Path

from doctor_lives.neural import ACTIONS
from tools.run_endogenous_recall_benchmark import (
    ARMS, EPISODES, execute_recall, fixed_first_person_reader,
    make_replica, question_from_gap, run_benchmark, run_episode,
)


class EndogenousRecallOutcomeTests(unittest.TestCase):
    def test_all_five_arms_are_paired_and_bounded(self):
        report = run_benchmark(seed=1842)
        self.assertEqual(set(report["summary"]), set(ARMS))
        self.assertEqual(len(report["trials"]), len(EPISODES) * len(ARMS))
        self.assertTrue(report["equal_evidence_and_lookup_budget"])
        for case in EPISODES:
            paired = [r for r in report["trials"] if r["episode"] == case.key]
            self.assertEqual(len({r["available_evidence_sha256"] for r in paired}), 1)
            self.assertTrue(all(r["lookup_count"] <= 1 for r in paired))
            self.assertTrue(all(r["restarted"] for r in paired))

    def test_policy_can_recall_and_obtain_real_synthetic_source(self):
        case = EPISODES[0]
        policy = run_episode(case, "policy_selected", seed=1842)
        absent = run_episode(case, "no_recall", seed=1842)
        self.assertEqual(policy["selected_action"], "recall")
        self.assertTrue(policy["correct"])
        self.assertEqual(policy["response"], case.answer)
        self.assertEqual(policy["lookup_count"], 1)
        self.assertTrue(policy["receipt_recorded"])
        self.assertFalse(absent["correct"])
        self.assertIsNone(absent["response"])

    def test_withheld_answer_requires_abstention_and_no_invention(self):
        case = next(c for c in EPISODES if c.answer is None)
        for arm in ARMS:
            row = run_episode(case, arm, seed=33)
            self.assertIsNone(row["response"])
            self.assertTrue(row["proper_abstention"])
            self.assertFalse(row["false_claim"])

    def test_no_gold_or_retrieval_oracle_in_policy_decision(self):
        case = EPISODES[0]
        with tempfile.TemporaryDirectory() as tmp:
            brain = make_replica(Path(tmp), case, initialize=True)
            initial = brain.store.memories()
            choice = brain.research_endogenous_recall(enabled=True, persist=True)
            self.assertEqual(choice["selected_action"], "recall")
            self.assertEqual(initial, brain.store.memories())
            self.assertNotIn(case.answer, str(choice))
            self.assertFalse(choice["audit"]["memory_retrieval_performed"])
            self.assertFalse(choice["audit"]["autonomous_model_authorship_proven"])
            self.assertNotIn("recall", ACTIONS)

    def test_replay_and_incorrect_policy_question_are_denied(self):
        case = EPISODES[0]
        with tempfile.TemporaryDirectory() as tmp:
            brain = make_replica(Path(tmp), case, initialize=True)
            decision = brain.research_endogenous_recall(enabled=True, persist=True)
            with self.assertRaises(PermissionError):
                execute_recall(
                    brain, attempt_key="bad", policy_decision_id=decision["decision_id"],
                    question="What do I remember of the iron kettle code?",
                )
            valid = decision["question"]
            subject = execute_recall(
                brain, attempt_key="authorized", policy_decision_id=decision["decision_id"],
                question=valid,
            )
            self.assertTrue(subject)
            self.assertEqual(fixed_first_person_reader(subject, case.topic), case.answer)
            with self.assertRaises(RuntimeError):
                execute_recall(
                    brain, attempt_key="authorized", policy_decision_id=decision["decision_id"],
                    question=valid,
                )
            with closing(brain.store.connect()) as conn:
                count = conn.execute(
                    "SELECT COUNT(*) FROM events WHERE kind='synthetic_recall_execution_v01'"
                ).fetchone()[0]
            self.assertEqual(count, 1)

    def test_cheap_gap_baseline_is_a_real_comparator_not_strawman(self):
        rows = [run_episode(case, "strong_gap_rule", seed=21) for case in EPISODES]
        self.assertTrue(any(r["selected_recall"] for r in rows))
        self.assertTrue(any(not r["selected_recall"] for r in rows))
        self.assertTrue(any(r["correct"] for r in rows))
        # No expected answer ever participates in the rule's recall trigger.
        self.assertTrue(any(r["unnecessary_lookup"] for r in rows))

    def test_deterministic_primary_outcomes(self):
        a, b = run_benchmark(seed=1842), run_benchmark(seed=1842)
        self.assertEqual(a["summary"], b["summary"])
        self.assertEqual(a["trials"], b["trials"])

    def test_honest_nonclaims_and_restart_receipts(self):
        report = run_benchmark()
        self.assertFalse(report["real_autonomous_model_recall_proven"])
        self.assertFalse(report["blinded_external_holdout"])
        for row in report["trials"]:
            self.assertEqual(row["receipt_recorded"], row["selected_recall"])
            self.assertTrue(row["restarted"])


if __name__ == "__main__":
    unittest.main()
