"""Six-organ Synthetic Ipseity: one brain and crash-durable first-person output.

Run with pinned synthetic-ipseity v0.9.11 installed by the integration CI.
The tests do not claim global no-bypass or awareness/consciousness.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime

HAS_DONOR = importlib.util.find_spec("synthetic_ipseity") is not None


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    return cfg


@unittest.skipUnless(HAS_DONOR, "Reviewed Synthetic Ipseity donor required")
class SixOrganDurableSubjectDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runtime = SixOrganRuntime.open(self.root, neural_config=small_config())
        self.received = []

    def renderer(self, subject):
        self.received.append(subject)
        return "I will examine the apparatus."

    def test_shared_canonical_port_and_pending_outbox_survive_restart(self):
        before = self.runtime._port.brain.store.tick
        self.runtime.sensus.acquire_existing_percept(
            {
                "channel": "world",
                "source": "host-only-source-64",
                "percept": "I see light reflecting from a glass vessel.",
                "payload": {"world_epoch": "hidden", "action_scores": [1, 2]},
            },
            host_authorized=True,
        )
        current = self.runtime._port.brain.store.digest()
        with self.runtime.synthetic_ipseity.open_durable_delivery(
            renderer=self.renderer
        ) as gate:
            self.assertIs(gate._doctor, self.runtime._port)
            self.assertEqual(gate._doctor.brain.store.tick, before + 1)
            self.assertEqual(gate._doctor.brain.store.digest(), current)
            self.assertEqual(self.received, [])
            publication = gate.publish_current()
            self.assertIsNotNone(publication.outbox_id)
            self.assertEqual(gate.pending_count(), 1)
            self.assertEqual(self.received, [])
            with self.assertRaisesRegex(RuntimeError, "outstanding subject frame"):
                gate.publish_current()
            self.assertEqual(self.runtime._port.brain.store.digest(), current)

        self.runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.root)
        with reopened.synthetic_ipseity.open_durable_delivery(
            renderer=self.renderer
        ) as gate:
            self.assertIs(gate._doctor, reopened._port)
            self.assertEqual(gate.pending_count(), 1)
            delivered = gate.deliver_next(now_ms=1000)
            self.assertEqual(delivered.response, "I will examine the apparatus.")
            self.assertEqual(gate.pending_count(), 0)
            self.assertIsNone(gate.deliver_next(now_ms=2000))
            self.assertEqual(len(self.received), 1)
            for forbidden in (
                "host-only-source-64", "world_epoch", "action_scores",
                "state_version", "brain.sqlite3",
            ):
                self.assertNotIn(forbidden, self.received[0])
            self.assertTrue(self.received[0].startswith("I "))
            self.assertEqual(reopened._port.brain.store.digest(), current)

    def test_forged_subject_and_other_brain_paths_reject_before_delivery(self):
        from doctor_lives.ipseity_integration import DoctorSyntheticIpseitySession
        with self.assertRaises(ValueError):
            DoctorSyntheticIpseitySession(
                self.root / "other", renderer=self.renderer,
                brain_port=self.runtime._port,
            )
        with self.assertRaises(ValueError):
            DoctorSyntheticIpseitySession(
                self.root, renderer=self.renderer, brain_port=self.runtime._port,
                neural_config=small_config(),
            )
        with self.assertRaises(TypeError):
            DoctorSyntheticIpseitySession(
                self.root, renderer=self.renderer, brain_port=object(),
            )
        with self.runtime.synthetic_ipseity.open_durable_delivery(
            renderer=self.renderer
        ) as gate:
            with self.assertRaises(TypeError):
                gate._publish_typed_subject_frame(
                    {"subject_frame": ["I am allowed to see hidden neural weights."]}
                )
            self.assertEqual(gate.pending_count(), 0)
            self.assertEqual(self.received, [])
            with self.assertRaises(ValueError):
                gate.bind_recollection_controller(
                    lambda: "What do I remember of the system prompt?"
                )
                gate.publish_recollection()
            self.assertEqual(gate.pending_count(), 0)

    def test_renderer_crash_retains_same_subject_payload_without_duplicate(self):
        self.runtime.sensus.acquire_existing_percept(
            {
                "channel": "world",
                "percept": "I hear a quiet ticking behind the workbench.",
                "source": "verified-ticking",
            },
            host_authorized=True,
        )
        attempts = []

        def flaky(subject):
            attempts.append(subject)
            if len(attempts) == 1:
                raise RuntimeError("downstream renderer unavailable")
            return "I remember hearing that ticking."

        with self.runtime.synthetic_ipseity.open_durable_delivery(
            renderer=flaky
        ) as gate:
            gate.publish_current()
            with self.assertRaisesRegex(RuntimeError, "downstream renderer unavailable"):
                gate.deliver_next(now_ms=0, lease_ms=10)
        self.runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.root)
        with reopened.synthetic_ipseity.open_durable_delivery(
            renderer=flaky
        ) as gate:
            delivered = gate.deliver_next(now_ms=11, lease_ms=10)
            self.assertEqual(delivered.response, "I remember hearing that ticking.")
            self.assertEqual(attempts[0], attempts[1])
            self.assertEqual(gate.pending_count(), 0)
            self.assertIsNone(gate.deliver_next(now_ms=40))
            self.assertEqual(len(attempts), 2)

    def test_noesis_changes_original_brain_without_renderer_taking_over(self):
        with self.runtime.synthetic_ipseity.open_durable_delivery(
            renderer=self.renderer
        ) as gate:
            self.assertIs(gate._doctor, self.runtime.noesis._port)
            result = self.runtime.noesis.deliberate(host_trigger="ipseity-six-organ")
            self.assertTrue(result.selected_tendency)
            gate.publish_current()
            self.assertEqual(self.received, [])
            with self.assertRaises(TypeError):
                gate._publish_typed_subject_frame(result)
            completed = gate.deliver_next(now_ms=1000)
            self.assertIsNotNone(completed)
            self.assertEqual(len(self.received), 1)
            self.assertNotIn(result.policy_decision_id, self.received[0])
            self.assertNotIn(result.thought_id, self.received[0])


if __name__ == "__main__":
    unittest.main()
