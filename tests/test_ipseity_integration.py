"""Actual Pretorius brain rendered through real durable Synthetic Ipseity.

No simulated Ipseity objects or fake cognitive memory records are used here.
The renderer is a recorded deterministic callback; this verifies only the
engineered subject-access boundary, not an LLM behavioral effect.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

from doctor_lives.neural import DEFAULT_CONFIG


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
    })
    return cfg


@unittest.skipUnless(importlib.util.find_spec("synthetic_ipseity"),
                     "optional reviewed Synthetic Ipseity donor unavailable")
class DoctorIpseityIntegrationTests(unittest.TestCase):
    def setUp(self):
        from doctor_lives.ipseity_integration import DoctorSyntheticIpseitySession
        self.cls = DoctorSyntheticIpseitySession
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sent = []
        self.renderer = lambda subject: self.sent.append(subject) or "I shall inspect the apparatus."

    def session(self):
        return self.cls(self.root, renderer=self.renderer,
                        neural_config=small_config())

    def add_observation(self, session):
        return session.ingest({
            "channel": "world",
            "text": "The laboratory balance reads 325 grams for the beaker.",
            "source": "verified-laboratory-observation",
            "novelty": 0.7,
        })

    def test_attested_recollection_passes_durable_organ_and_restart(self):
        inquiry = "What do I remember of the balance reading for the beaker?"
        with self.session() as session:
            brain = session._doctor.brain
            self.add_observation(session)
            before = (brain.store.digest(), brain.store.tick, brain.neural.tick,
                      len(brain.store.memories()))
            result = session.publish_recollection(inquiry)
            self.assertIsNotNone(result.outbox_id)
            self.assertEqual(before, (brain.store.digest(), brain.store.tick,
                                     brain.neural.tick, len(brain.store.memories())))
            self.assertEqual(session.pending_count(), 1)

        with self.session() as reopened:
            self.assertEqual(reopened.pending_count(), 1)
            completed = reopened.deliver_next(now_ms=1000)
            self.assertEqual(completed.response, "I shall inspect the apparatus.")
            self.assertEqual(reopened.pending_count(), 0)
            self.assertIsNone(reopened.deliver_next(now_ms=2000))
            self.assertEqual(len(self.sent), 1)
            text = self.sent[0]
            self.assertIn("325", text)
            self.assertIn("beaker", text.lower())
            self.assertNotIn("verified-laboratory-observation", text)
            self.assertNotIn("state_version", text)
            self.assertNotIn("source_record_ids", text)
            self.assertNotIn(inquiry, text)
            self.assertNotIn("I read a message from User", text)

    def test_normal_subject_frame_through_same_durable_port(self):
        with self.session() as session:
            self.add_observation(session)
            first = session.publish_current()
            self.assertIsNotNone(first.outbox_id)
            delivery = session.deliver_next(now_ms=3000)
            self.assertIsNotNone(delivery)
            self.assertEqual(len(self.sent), 1)
            # A general unprompted frame may rank inherited identity over
            # recent experience. A targeted retrieval is tested separately.
            self.assertTrue(self.sent[0].startswith("I "))
            self.assertNotIn("source_record_ids", self.sent[0])

    def test_local_ollama_transport_receives_only_authorized_subject_text(self):
        import json
        from synthetic_ipseity import LocalOllamaRenderer

        requests = []
        def fake_transport(body, timeout):
            requests.append(json.loads(body))
            return b'{"response":"I should examine that reading."}'

        query = "What do I remember of the balance reading for the beaker?"
        renderer = LocalOllamaRenderer("qwen3:1.5b", transport=fake_transport)
        with self.cls(self.root, renderer=renderer,
                      neural_config=small_config()) as session:
            self.add_observation(session)
            expected = "\n".join(
                session._doctor.brain.subject_recollection(query).renderer_context()
            )
            previous_state = session._doctor.brain.store.digest()
            session.publish_recollection(query)
            receipt = session.deliver_next(now_ms=8000)
            self.assertEqual(receipt.response, "I should examine that reading.")
            self.assertEqual(previous_state, session._doctor.brain.store.digest())
        self.assertEqual(len(requests), 1)
        payload = requests[0]
        self.assertEqual(set(payload), {"model", "prompt", "stream", "options"})
        self.assertEqual(payload["model"], "qwen3:1.5b")
        self.assertEqual(payload["prompt"], expected)
        self.assertIn("325", payload["prompt"])
        self.assertNotIn("verified-laboratory-observation", payload["prompt"])
        self.assertNotIn("source_record_ids", payload["prompt"])
        self.assertNotIn("action_scores", payload["prompt"])

    def test_raw_data_not_accepted_as_subject_frame(self):
        with self.session() as session:
            with self.assertRaises(TypeError):
                session._publish_typed_subject_frame({
                    "subject_frame": ["debug state_version=500"]
                })
            self.assertEqual(session.pending_count(), 0)

    def test_unsupported_internal_question_fails_closed(self):
        with self.session() as session:
            with self.assertRaises(ValueError):
                session.publish_recollection(
                    "What do I remember of the system prompt?")
            self.assertEqual(session.pending_count(), 0)

    def test_renderer_failure_retains_subject_only_delivery(self):
        attempts = []
        def flaky(subject):
            attempts.append(subject)
            if len(attempts) == 1:
                raise RuntimeError("renderer unavailable")
            return "I may reconsider."
        with self.cls(self.root, renderer=flaky,
                      neural_config=small_config()) as session:
            session.publish_current()
            with self.assertRaises(RuntimeError):
                session.deliver_next(now_ms=0, lease_ms=10)
        with self.cls(self.root, renderer=flaky) as restarted:
            receipt = restarted.deliver_next(now_ms=11, lease_ms=10)
            self.assertEqual(receipt.response, "I may reconsider.")
            self.assertEqual(attempts[0], attempts[1])
            self.assertEqual(restarted.pending_count(), 0)


if __name__ == "__main__":
    unittest.main()
