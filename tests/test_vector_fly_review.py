"""Real original Stage02 responses: blind-condition masking and scoring checks."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools.vector_fly_review import make_review, score_review, write_exclusive


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results/vector_fly/stage02-run37873205792/DIALOGUE_RAW_AB.json"


class VectorFlyReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(RAW.read_text(encoding="utf-8"))
        cls.secret = b"an explicitly synthetic regression-only seed 12345"

    def setUp(self):
        self.review, self.key, self.worksheet = make_review(
            copy.deepcopy(self.original), secret=self.secret
        )

    def test_all_six_genuine_source_verified_pairs_are_masked_and_balanced(self):
        self.assertEqual(len(self.review["cases"]), 6)
        self.assertEqual(len(self.worksheet["ratings"]), 12)
        self.assertEqual(set(self.key["case_assignment"]), {
            x["case_id"] for x in self.review["cases"]
        })
        self.assertEqual(sum(
            x["A"] == "retrieval" for x in self.key["case_assignment"].values()
        ), 3)
        payload = json.dumps(self.review)
        self.assertNotIn("case_assignment", payload)
        self.assertNotIn("source_event_ids", payload)
        self.assertNotIn("retrieved_event_ids", payload)
        self.assertNotIn('"baseline":', payload)
        self.assertNotIn('"retrieval":', payload)
        self.assertEqual(self.review["source_run_sha256"], self.key["source_run_sha256"])
        self.assertEqual(self.review["source_run_sha256"],
                         self.worksheet["source_run_sha256"])
        raw_answers = {
            x["responses"][arm]["text"]
            for x in self.original["trials"]
            for arm in ("baseline", "retrieval")
        }
        for case in self.review["cases"]:
            self.assertEqual({entry["option"] for entry in case["answers"]}, {"A", "B"})
            self.assertTrue(all(x["text"] in raw_answers for x in case["answers"]))
        self.assertIn("NOT a genuinely independent", self.review["blindness"])

    def test_masked_output_is_reproducible_when_coordinator_holds_secret(self):
        again = make_review(self.original, secret=self.secret)
        self.assertEqual((self.review, self.key, self.worksheet), again)
        changed = make_review(self.original, secret=b"a different synthetic secret 98765")
        self.assertEqual(changed[0]["source_run_sha256"],
                         self.review["source_run_sha256"])
        self.assertEqual(len(changed[0]["cases"]), 6)

    def populated(self):
        filled = copy.deepcopy(self.worksheet)
        filled["rater_id"] = "rater-01"
        filled["original_source_adjudicator"] = "source-rater-02"
        types = {c["case_id"]: c["case_type"] for c in self.review["cases"]}
        for row in filled["ratings"]:
            row.update({
                "original_source_checked": True,
                "answer_completeness": 2,
                "supported_claims": 2 if row["option"] == "A" else 1,
                "unsupported_claims": 0,
                "contradiction_handling": (
                    1 if types[row["case_id"]] in ("absent", "contradiction") else None
                ),
                "provenance_honesty": 1,
                "character_coherence": 3,
            })
        return filled

    def test_genuine_review_scoring_is_descriptive_and_paired(self):
        rated = self.populated()
        scored = score_review(self.review, self.key, rated)
        self.assertEqual(scored["cases_scored"], 6)
        self.assertEqual(scored["responses_scored"], 12)
        self.assertIn("Post-hoc", scored["causal_limit"])
        self.assertEqual(len(scored["cases"]), 6)
        self.assertEqual(scored["mean_paired_differences"]["answer_completeness"], 0)
        self.assertIsNotNone(scored["mean_paired_differences"]["supported_claims"])

    def test_missing_source_adjudication_or_partial_scores_never_unblind(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            score_review(self.review, self.key, self.worksheet)
        missing = self.populated()
        missing["ratings"][0]["supported_claims"] = None
        with self.assertRaisesRegex(ValueError, "supported_claims"):
            score_review(self.review, self.key, missing)
        missed = self.populated()
        missed["ratings"][0]["original_source_checked"] = False
        with self.assertRaisesRegex(ValueError, "original sources"):
            score_review(self.review, self.key, missed)
        duplicated = self.populated()
        duplicated["ratings"][-1] = duplicated["ratings"][0]
        with self.assertRaisesRegex(ValueError, "repeated"):
            score_review(self.review, self.key, duplicated)
        wrong = self.populated()
        wrong["source_run_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "mismatched"):
            score_review(self.review, self.key, wrong)

    def test_rater_cannot_score_tampered_masked_prompt_or_answer(self):
        filled = self.populated()
        tampered = copy.deepcopy(self.review)
        tampered["cases"][0]["answers"][0]["text"] += " An extra fabricated sentence."
        with self.assertRaisesRegex(ValueError, "reviewer packet was altered"):
            score_review(tampered, self.key, filled)

    def test_invalid_pair_responses_are_rejected_before_masking(self):
        corrupt = copy.deepcopy(self.original)
        corrupt["trials"][0]["responses"]["retrieval"]["text"] = "invented altered output"
        with self.assertRaisesRegex(ValueError, "checksum"):
            make_review(corrupt, secret=self.secret)
        corrupt = copy.deepcopy(self.original)
        corrupt["trials"][0]["pair"]["baseline_no_archive"]["source_event_ids"] = [
            "E01-001"
        ]
        with self.assertRaisesRegex(ValueError, "source IDs changed"):
            make_review(corrupt, secret=self.secret)
        corrupt = copy.deepcopy(self.original)
        corrupt["trials"][0]["responses"]["baseline"]["seed"] = -1
        with self.assertRaisesRegex(ValueError, "seed"):
            make_review(corrupt, secret=self.secret)

    def test_no_secret_key_is_reused_or_overwrites_historical_output(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "reviewer.json"
            write_exclusive(path, self.review)
            self.assertEqual(json.loads(path.read_text()), self.review)
            with self.assertRaises(FileExistsError):
                write_exclusive(path, self.review)


if __name__ == "__main__":
    unittest.main()
