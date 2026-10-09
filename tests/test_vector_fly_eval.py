"""The Doctor Lives and Vector Fly A/B boundary: source external, brain unchanged."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.vector_fly_eval import (
    API_VERSION, PILOT_QUESTIONS, SOURCE_GIT_BLOB,
    make_prompt_packet, prepare_paired_trial, retrieve_evidence,
    invoke_ollama,
)


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
        "plasticity_interval": 2,
        "seed": 1842,
    })
    return cfg


def source_response():
    return {
        "api_version": API_VERSION,
        "scope": "all",
        "source_git_blob": SOURCE_GIT_BLOB,
        "query": "What was in the specimen drawer?",
        "evidence": [{
            "event_id": "E01-001",
            "episode_id": "E01",
            "title": "The Empty Specimen Drawer",
            "provenance": "reconstructed",
            "source_excerpt": "I found a dead beetle in the drawer.",
            "source_sha256": "a" * 64,
            "vector_score": .22,
            "source_type": "external_reconstructed_archive_not_lived",
        }],
    }


def request_fixture(url, payload=None, bearer=None):
    if url.endswith("/v1/info"):
        return {
            "api_version": API_VERSION,
            "database": {
                "scope": "all", "source_git_blob": SOURCE_GIT_BLOB,
                "vector_kind": "lexical-tfidf-not-semantic",
            },
        }
    if url.endswith("/v1/search"):
        return {
            "api_version": API_VERSION,
            "scope": "all",
            "source_git_blob": SOURCE_GIT_BLOB,
            "results": [{
                "event_id": "E01-001", "episode_id": "E01",
                "provenance": "reconstructed", "similarity": .22,
            }],
        }
    if url.endswith("/v1/memories/E01-001"):
        return {
            "api_version": API_VERSION,
            "scope": "all",
            "memory": {
                "event_id": "E01-001",
                "episode_id": "E01",
                "provenance": "reconstructed",
                "title": "The Empty Specimen Drawer",
                "memory_text": "I found a dead beetle in the specimen drawer.",
            },
        }
    raise ValueError("Unexpected URL: " + url)


class VectorFlyEvaluationTests(unittest.TestCase):
    def test_external_archive_source_binding_and_fail_closed_checks(self):
        source = retrieve_evidence(
            "http://127.0.0.1:8765", "What was in the specimen drawer?",
            request=request_fixture,
        )
        self.assertEqual(len(source["evidence"]), 1)
        self.assertEqual(source["evidence"][0]["event_id"], "E01-001")
        self.assertEqual(source["evidence"][0]["provenance"], "reconstructed")
        self.assertIn("dead beetle", source["evidence"][0]["source_excerpt"])

        def wrong_scope(url, payload=None, bearer=None):
            obj = copy.deepcopy(request_fixture(url, payload, bearer))
            if url.endswith("/v1/info"):
                obj["database"]["scope"] = "train"
            return obj

        with self.assertRaisesRegex(ValueError, "scope"):
            retrieve_evidence("http://localhost:8765", "cabinet",
                              request=wrong_scope)

        def wrong_original(url, payload=None, bearer=None):
            obj = copy.deepcopy(request_fixture(url, payload, bearer))
            if url.endswith("/v1/memories/E01-001"):
                obj["memory"]["event_id"] = "E01-999"
            return obj

        with self.assertRaisesRegex(ValueError, "disagree"):
            retrieve_evidence("http://localhost:8765", "cabinet",
                              request=wrong_original)

        def fraudulent_provenance(url, payload=None, bearer=None):
            obj = copy.deepcopy(request_fixture(url, payload, bearer))
            if url.endswith("/v1/memories/E01-001"):
                obj["memory"]["provenance"] = "lived_runtime_memory"
            return obj

        with self.assertRaisesRegex(ValueError, "disagree"):
            retrieve_evidence("http://localhost:8765", "cabinet",
                              request=fraudulent_provenance)

    def test_actual_pretorius_brain_matched_same_state(self):
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrainPort(Path(td) / "isolated", neural_config=small_config())
            original_status = brain.status()
            question = "What was in the specimen drawer?"
            source = source_response()
            trial = prepare_paired_trial(brain, question, source)
            self.assertTrue(trial["matched_subject_frame"])
            self.assertFalse(trial["brain_mutated"])
            self.assertEqual(trial["before_state_digest"], trial["after_state_digest"])
            self.assertEqual(original_status["state_digest"], brain.status()["state_digest"])
            a = trial["baseline_no_archive"]
            b = trial["retrieval_archive"]
            self.assertEqual(a["subject_frame_sha256"], b["subject_frame_sha256"])
            self.assertNotEqual(a["packet_sha256"], b["packet_sha256"])
            self.assertEqual(a["source_event_ids"], [])
            self.assertEqual(b["source_event_ids"], ["E01-001"])
            self.assertIn("dead beetle", b["prompt"])
            self.assertNotIn("dead beetle", a["prompt"])
            self.assertIn("external_reconstructed_archive_not_lived", b["prompt"])
            self.assertEqual(trial["source"]["source_git_blob"], SOURCE_GIT_BLOB)

    def test_archive_never_enters_subject_frame_or_lived_memory(self):
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrainPort(Path(td) / "isolated", neural_config=small_config())
            q = "What was in the specimen drawer?"
            renderer = brain.render_request(q)
            before = brain.status()["state_digest"]
            b = make_prompt_packet(renderer, q, source_response()["evidence"])
            a = make_prompt_packet(renderer, q)
            self.assertNotIn("I found a dead beetle", " ".join(renderer["subject_frame"]))
            self.assertNotIn("I found a dead beetle", " ".join(brain.render_request(q)["subject_frame"]))
            self.assertEqual(brain.status()["state_digest"], before)
            self.assertEqual(b["subject_frame_sha256"], a["subject_frame_sha256"])

    def test_absent_probes_and_unreviewed_status_are_explicit(self):
        self.assertEqual(len(PILOT_QUESTIONS), 6)
        self.assertTrue(any(c["type"] == "absent" and
                            not c["expected_event_ids"]
                            for c in PILOT_QUESTIONS))
        self.assertTrue(any(c["type"] == "contradiction"
                            for c in PILOT_QUESTIONS))
        self.assertEqual(len({c["id"] for c in PILOT_QUESTIONS}), 6)

    def test_local_renderer_endpoint_cannot_be_redirected_off_device(self):
        for url in ("https://api.openai.com", "http://example.com",
                    "http://localhost:11434?key=oops"):
            with self.assertRaisesRegex(ValueError, "local Ollama"):
                invoke_ollama("test", model="test", endpoint=url, seed=1)


if __name__ == "__main__":
    unittest.main()
