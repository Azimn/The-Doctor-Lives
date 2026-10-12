"""Crash-window admission controls for real Pretorius memory and Ipseity."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
                     "reviewed synthetic ipseity donor not installed")
class LocalTurnCrashRecoveryTests(unittest.TestCase):
    def setUp(self):
        from doctor_lives.ipseity_local import local_turn
        self.local_turn = local_turn
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.calls = []

    def render(self, text):
        self.calls.append(text)
        return "I have heard the question."

    def take(self, **kwargs):
        return self.local_turn(
            self.path, renderer=self.render, neural_config=small_config(),
            now_ms=50000 + 40000 * len(self.calls), **kwargs
        )

    def admitted(self):
        from doctor_lives.chassis import PretoriusBrainPort
        port = PretoriusBrainPort(self.path)
        return [m for m in port.brain.store.memories()
                if m["source"].startswith("local-conversation:")]

    def test_interrupted_before_admission_can_resume_without_double_event(self):
        from doctor_lives.ipseity_integration import DoctorSyntheticIpseitySession
        with patch.object(DoctorSyntheticIpseitySession, "ingest",
                          side_effect=RuntimeError("crash before Doctor ingress")):
            with self.assertRaisesRegex(RuntimeError, "crash before"):
                self.take(user_text="The glass case is closed.")
        self.assertEqual(len(self.admitted()), 0)
        response = self.take(resume=True)
        self.assertEqual(response, "I have heard the question.")
        self.assertEqual(len(self.admitted()), 1)
        self.assertEqual(len(self.calls), 1)

    def test_interrupted_after_admission_resumes_without_duplicate_memory(self):
        from doctor_lives.ipseity_integration import DoctorSyntheticIpseitySession
        with patch.object(DoctorSyntheticIpseitySession, "publish_current",
                          side_effect=RuntimeError("crash after Doctor ingress")):
            with self.assertRaisesRegex(RuntimeError, "crash after"):
                self.take(user_text="The balance is on the bench.")
        before = self.admitted()
        self.assertEqual(len(before), 1)
        self.assertEqual(len(self.calls), 0)
        self.assertEqual(self.take(resume=True), "I have heard the question.")
        after = self.admitted()
        self.assertEqual([m["id"] for m in before], [m["id"] for m in after])
        self.assertEqual(len(self.calls), 1)

    def test_interrupted_after_outbox_commit_reuses_same_subject_frame(self):
        from doctor_lives.local_turn_journal import LocalTurnJournal
        original = LocalTurnJournal.advance
        def fail_when_published(journal, key, prior, stage):
            if (prior, stage) == ("admitted", "published"):
                raise RuntimeError("crash after subject outbox")
            return original(journal, key, prior, stage)
        with patch.object(LocalTurnJournal, "advance", fail_when_published):
            with self.assertRaisesRegex(RuntimeError, "crash after subject"):
                self.take(user_text="I have another instrument question.")
        before = self.admitted()
        self.assertEqual(len(before), 1)
        self.assertEqual(self.take(resume=True), "I have heard the question.")
        self.assertEqual(len(self.admitted()), 1)
        self.assertEqual(len(self.calls), 1)

    def test_after_ack_crash_refuses_duplicate_model_invocation(self):
        from doctor_lives.local_turn_journal import LocalTurnJournal
        from doctor_lives.ipseity_local import PendingSubjectDelivery
        original = LocalTurnJournal.advance
        def fail_after_delivery(journal, key, prior, stage):
            if (prior, stage) == ("published", "delivered"):
                raise RuntimeError("crash after ack")
            return original(journal, key, prior, stage)
        with patch.object(LocalTurnJournal, "advance", fail_after_delivery):
            with self.assertRaisesRegex(RuntimeError, "crash after ack"):
                self.take(user_text="Observe the bell jar.")
        self.assertEqual(len(self.calls), 1)
        with self.assertRaisesRegex(PendingSubjectDelivery, "already acknowledged"):
            self.take(resume=True)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(len(self.admitted()), 1)
        self.assertEqual(self.take(user_text="A new test follows."),
                         "I have heard the question.")
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(len(self.admitted()), 2)

    def test_uncertain_prepared_intent_detects_foreign_brain_mutation(self):
        from doctor_lives.ipseity_integration import DoctorSyntheticIpseitySession
        from doctor_lives.chassis import PretoriusBrainPort
        from doctor_lives.ipseity_local import LocalTurnConflict
        with patch.object(DoctorSyntheticIpseitySession, "ingest",
                          side_effect=RuntimeError("crash before ingress")):
            with self.assertRaisesRegex(RuntimeError, "crash before"):
                self.take(user_text="The flask has changed.")
        actual = PretoriusBrainPort(self.path, neural_config=small_config())
        actual.ingest({
            "channel": "world",
            "source": "some-unrelated-event",
            "text": "A visitor entered the laboratory.",
        })
        with self.assertRaisesRegex(LocalTurnConflict, "changed since input"):
            self.take(resume=True)
        self.assertEqual(len(self.admitted()), 0)

    def test_prior_turn_blocks_new_input_after_crash(self):
        from doctor_lives.ipseity_integration import DoctorSyntheticIpseitySession
        from doctor_lives.ipseity_local import PendingSubjectDelivery
        with patch.object(DoctorSyntheticIpseitySession, "publish_current",
                          side_effect=RuntimeError("failed before publish")):
            with self.assertRaises(RuntimeError):
                self.take(user_text="Please measure the liquid.")
        with self.assertRaisesRegex(PendingSubjectDelivery, "Previous subject"):
            self.take(user_text="Please measure the liquid.")
        self.assertEqual(len(self.admitted()), 1)


if __name__ == "__main__":
    unittest.main()
