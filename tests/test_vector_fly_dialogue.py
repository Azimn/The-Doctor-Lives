"""Small, synthetic tests for an honest, renderer-output-only structural summary.

Tests use invented responses ONLY to verify analysis code, not claim model quality.
"""
import copy
import hashlib
import unittest
from tools.summarize_vector_fly_dialogue import summarize


def response(text: str):
    return {
        "renderer": "local-ollama", "model": "qwen2.5:0.5b-instruct",
        "seed": 1842, "text": text,
        "response_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def fixture():
    base = {
        "case_id": "case-x", "case_type": "specific_reconstructed_event",
        "counterbalanced_first_arm": "baseline",
        "gold_hit_at_k": True,
        "retrieved_event_ids": ["E01-001"],
        "pair": {
            "brain_mutated": False, "matched_subject_frame": True,
            "baseline_no_archive": {
                "subject_frame_sha256": "abc", "source_event_ids": []
            },
            "retrieval_archive": {
                "subject_frame_sha256": "abc", "source_event_ids": ["E01-001"]
            },
        },
        "responses": {
            "baseline": response("I do not recall."),
            "retrieval": response("I encountered a beetle in a cabinet."),
        },
    }
    cases = []
    for i in range(6):
        e = copy.deepcopy(base)
        e["case_id"] = str(i)
        cases.append(e)
    return {
        "state_unchanged": True,
        "renderer": "qwen2.5:0.5b-instruct",
        "renderer_seed": 1842,
        "source_scope": "all",
        "trials": cases,
    }


class RendererReportTests(unittest.TestCase):
    def test_actual_renderer_output_hashes_and_counts_are_reported(self):
        r = summarize(fixture(), {
            "digest": "sha256:example",
            "ollama_version": "ollama version v0.34.0",
        })
        self.assertEqual(r["responses_expected"], 12)
        self.assertEqual(r["responses_generated"], 12)
        self.assertEqual(r["cases_with_different_responses"], 6)
        self.assertFalse(r["behavioral_accuracy_scored"])
        self.assertFalse(r["human_review_complete"])
        self.assertEqual(r["model_digest"], "sha256:example")
        self.assertTrue(r["brain_state_unchanged"])

    def test_no_false_result_if_missing_renderer_reply(self):
        trial = fixture()
        trial["trials"][0]["responses"] = None
        with self.assertRaisesRegex(ValueError, "actual A/B"):
            summarize(trial, {})

    def test_no_false_result_if_modified_brain_or_control_archive(self):
        for key in ("brain_mutated", "matched_subject_frame"):
            trial = fixture()
            trial["trials"][0]["pair"][key] = key == "brain_mutated"
            with self.assertRaisesRegex(ValueError, "Nonmatched"):
                summarize(trial, {})
        trial = fixture()
        trial["trials"][0]["pair"]["baseline_no_archive"]["source_event_ids"] = ["E01-001"]
        with self.assertRaisesRegex(ValueError, "Nonmatched"):
            summarize(trial, {})

    def test_model_seed_and_response_integrity_rejected_when_mismatched(self):
        trial = fixture()
        trial["trials"][2]["responses"]["retrieval"]["response_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            summarize(trial, {})
        trial = fixture()
        trial["trials"][2]["responses"]["retrieval"]["seed"] = 7
        with self.assertRaisesRegex(ValueError, "Nonmatching"):
            summarize(trial, {})
        trial = fixture()
        trial["renderer"] = "none_packets_only"
        with self.assertRaisesRegex(ValueError, "real six-case"):
            summarize(trial, {})


if __name__ == "__main__":
    unittest.main()
