"""Audit does not substitute empty/model-generated prose for independent efficacy."""
import unittest

from research_prototypes.character_state.audit_chronological_1b import summarize
from research_prototypes.character_state.run_chronological_1b import (
    SCHEMA, ARM_NAMES,
)


def fake():
    return {
        "schema": SCHEMA,
        "native": {
            "external_world_outcomes": 0,
            "cases": [
                {"case_id": f"case-{i}",
                 "equal_evidence_flat_phase": True}
                for i in range(8)
            ],
        },
        "responses": [
            {"case_id": f"case-{i}", "arm": arm, "response": "A short reply.",
             "usable_dialogue": True, "generation_seconds": 2.0,
             "model_usage": {"prompt_tokens": 100, "completion_tokens": 12}}
            for i in range(8) for arm in ARM_NAMES
        ],
    }


class SummarizationControls(unittest.TestCase):
    def test_counts_without_claiming_independent_efficacy(self):
        result = summarize(fake())
        self.assertFalse(result["claims_verified"]["independent_behavioral_scores"])
        self.assertFalse(result["claims_verified"]["independent_world_outcomes"])
        self.assertEqual(len(result["arms"]), 4)
        for arm in ARM_NAMES:
            self.assertEqual(result["arms"][arm]["n"], 8)
            self.assertEqual(result["arms"][arm]["mean_prompt_tokens"], 100)
            self.assertEqual(result["arms"][arm]["usable"], 8)

    def test_duplicate_response_and_source_leakage_detected(self):
        value = fake()
        value["responses"][0]["response"] = "canon_rank=4"
        result = summarize(value)
        self.assertIn("case-0", result["arms"]["static_flat"]["literal_forbidden_diagnostic_leaks"])
        value["responses"][1]["case_id"] = "case-0"
        value["responses"][1]["arm"] = "static_flat"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            summarize(value)

    def test_missing_and_fabricated_world_rows_fail_closed(self):
        value=fake()
        value["responses"].pop()
        with self.assertRaisesRegex(ValueError, "32"):
            summarize(value)
        value=fake()
        value["native"]["external_world_outcomes"]=1
        with self.assertRaisesRegex(ValueError, "witness"):
            summarize(value)


if __name__ == "__main__":
    unittest.main()
