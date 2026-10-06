from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from doctor_lives import (
    AwarenessPolicy,
    Experience,
    PhenomenalEvent,
    PretoriusBrain,
    TraceVersionLedger,
)
from doctor_lives.neural import DEFAULT_CONFIG, NEURAL_CONVERGENCE_CONFIG


def small(cfg: dict) -> dict:
    out = dict(cfg)
    out.update({
        "neurons": 96,
        "sensory_dim": 48,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 6,
        "seed": 1842,
    })
    return out


class ReleaseCandidateTests(unittest.TestCase):
    def test_definitive_tree_exports_uppb_and_live_brain_together(self):
        self.assertIsNotNone(PhenomenalEvent)
        self.assertIsNotNone(AwarenessPolicy)
        self.assertIsNotNone(TraceVersionLedger)
        self.assertIsNotNone(PretoriusBrain)

    def test_release_default_remains_legacy_v04_neural_control(self):
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrain(Path(td), neural_config=small(DEFAULT_CONFIG))
            self.assertEqual(brain.status()["neural_diagnostics"]["profile"], "legacy_v04")

    def test_release_can_select_convergence_without_second_brain_type(self):
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrain(Path(td), neural_config=small(NEURAL_CONVERGENCE_CONFIG))
            result = brain.ingest(Experience(
                "A difficult unfamiliar apparatus demands attention.",
                novelty=.8,
                threat=.4,
                arousal=.6,
                confidence=.9,
            ))
            self.assertEqual(brain.status()["neural_diagnostics"]["profile"], "neural_convergence_v05")
            self.assertIn("recurrent_action_tendencies", result)
            self.assertIs(brain.neural.__class__.__name__, "PretoriusRecurrentSubstrate")

    def test_convergence_profile_does_not_change_identity_authority(self):
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            legacy = PretoriusBrain(Path(left_dir), neural_config=small(DEFAULT_CONFIG))
            convergence = PretoriusBrain(Path(right_dir), neural_config=small(NEURAL_CONVERGENCE_CONFIG))
            self.assertEqual(legacy.identity, convergence.identity)
            self.assertEqual(
                legacy.store.meta("bootstrap_version"),
                convergence.store.meta("bootstrap_version"),
            )


if __name__ == "__main__":
    unittest.main()
