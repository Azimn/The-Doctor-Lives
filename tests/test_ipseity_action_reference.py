"""Check actual Pretorius subjects can use the upgraded donor action contract.

IMPORTANT: the donor's tiny reference drawer/lamp is NOT Pretorius-Laboratory.
This is a typed, real-brain -> organ -> allowlisted-host -> feedback interface
smoke, not production authority to mutate the canonical lab or Doctor memory.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.neural import DEFAULT_CONFIG


def small_config():
    config = dict(DEFAULT_CONFIG)
    config.update({
        "neurons": 128, "sensory_dim": 64,
        "avg_recurrent_degree": 8, "input_degree": 4,
        "action_population_size": 8,
    })
    return config


@unittest.skipUnless(importlib.util.find_spec("synthetic_ipseity"),
                     "optional combined Synthetic Ipseity donor unavailable")
class DoctorActionContractTests(unittest.TestCase):
    def setUp(self):
        from doctor_lives.ipseity_integration import DoctorSyntheticIpseitySession
        from synthetic_ipseity.laboratory_action import (
            AuthorizedLaboratoryTurn, LaboratoryActionGateway,
        )
        self.Session = DoctorSyntheticIpseitySession
        self.Action = AuthorizedLaboratoryTurn
        self.Gateway = LaboratoryActionGateway
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.emitted = []

    def test_actual_doctor_first_person_ingress_and_authorized_reference_effect(self):
        model_inputs = []
        def proposal(first_person_text):
            model_inputs.append(first_person_text)
            return '{"action":"open_drawer"}'
        def collect(text):
            self.emitted.append(text)
            return "I have received the observation."

        with self.Session(self.root, renderer=collect,
                          neural_config=small_config()) as session:
            # The world observation is injected by a controlled TEST FIXTURE,
            # not falsely claimed as a real authoritative Pretorius Laboratory.
            session.ingest({
                "channel": "world",
                "text": "A small wooden drawer is closed in a demonstration cabinet.",
                "source": "synthetic-reference-lab-fixture",
            })
            original = session._doctor.brain.store.digest()
            published = session.publish_current()
            self.assertIsNotNone(published.outbox_id)
            with self.Gateway(
                self.root / "synthetic_ipseity.sqlite3",
                subject_id="pretorius",
                epoch_id=session.DEFAULT_EPOCH,
            ) as gate:
                action = self.Action(session._ipseity, gate, proposal)
                receipt = action.propose_and_execute(now_ms=100)
                self.assertIsNotNone(receipt)
                self.assertTrue(receipt.accepted)
                self.assertEqual(receipt.action, "open_drawer")
                self.assertTrue(gate.drawer_open())
                self.assertEqual(gate.action_count(), 1)
                self.assertEqual(len(model_inputs), 1)
                self.assertIn("I notice", model_inputs[0])
                self.assertNotIn("synthetic-reference-lab-fixture", model_inputs[0])
                self.assertEqual(session.pending_count(), 0)
                self.assertEqual(original, session._doctor.brain.store.digest())

                feedback = gate.publish_next_feedback(session._ipseity)
                self.assertEqual(feedback, receipt)
                result = session.deliver_next(now_ms=200)
                self.assertEqual(result.response,
                                 "I have received the observation.")
                self.assertIn("drawer", self.emitted[-1].lower())
                self.assertEqual(session.pending_count(), 0)

            # The donor effect is real in the reference SQLite lab, but NOT
            # automatically a memory in the canonical Pretorius brain.
            self.assertEqual(original, session._doctor.brain.store.digest())

    def test_invalid_untrusted_proposal_cannot_modify_reference_world(self):
        calls = []
        with self.Session(
            self.root, renderer=lambda text: calls.append(text) or "Received.",
            neural_config=small_config(),
        ) as session:
            session.publish_current()
            with self.Gateway(
                self.root / "synthetic_ipseity.sqlite3",
                subject_id="pretorius", epoch_id=session.DEFAULT_EPOCH,
            ) as gate:
                attempt = self.Action(
                    session._ipseity, gate,
                    lambda _: '{"action":"open_drawer","raw_sql":"DROP TABLE"}',
                )
                denied = attempt.propose_and_execute(now_ms=100)
                self.assertFalse(denied.accepted)
                self.assertEqual(denied.action, "REJECTED")
                self.assertFalse(gate.drawer_open())
                self.assertEqual(gate.action_count(), 1)
                gate.publish_next_feedback(session._ipseity)
                session.deliver_next(now_ms=200)
                self.assertIn("not recognized", calls[0])
