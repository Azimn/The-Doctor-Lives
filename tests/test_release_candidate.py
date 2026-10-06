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


    def test_existing_checkpoint_accepts_same_profile_and_omitted_config(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            cfg = small(DEFAULT_CONFIG)
            PretoriusBrain(state, neural_config=cfg).save()
            same = PretoriusBrain(state, neural_config=cfg)
            self.assertEqual(same.status()["neural_diagnostics"]["profile"], "legacy_v04")
            omitted = PretoriusBrain(state)
            self.assertEqual(omitted.status()["neural_diagnostics"]["profile"], "legacy_v04")

    def test_existing_checkpoint_rejects_explicit_opposite_profile(self):
        with tempfile.TemporaryDirectory() as legacy_dir:
            state = Path(legacy_dir)
            PretoriusBrain(state, neural_config=small(DEFAULT_CONFIG)).save()
            with self.assertRaisesRegex(RuntimeError, "explicit neural checkpoint migration required"):
                PretoriusBrain(state, neural_config=small(NEURAL_CONVERGENCE_CONFIG))

        with tempfile.TemporaryDirectory() as convergence_dir:
            state = Path(convergence_dir)
            PretoriusBrain(state, neural_config=small(NEURAL_CONVERGENCE_CONFIG)).save()
            with self.assertRaisesRegex(RuntimeError, "explicit neural checkpoint migration required"):
                PretoriusBrain(state, neural_config=small(DEFAULT_CONFIG))

    def test_low_pressure_ingest_uses_query_aware_direct_history(self):
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrain(Path(td), neural_config=small(DEFAULT_CONFIG))
            with brain.store.connect() as conn:
                row = conn.execute(
                    """SELECT m.id
                    FROM memories m
                    JOIN memory_provenance p ON p.memory_id=m.id
                    WHERE p.history_key='curated:history.homunculi'"""
                ).fetchone()
            self.assertIsNotNone(row)
            history_id = str(row["id"])

            relevant = Experience(
                "The homunculi creation suggests another artificial life experiment.",
                kind="observation",
                arousal=0.0,
                novelty=0.0,
                threat=0.0,
                creation=0.0,
            )
            self.assertFalse(brain._warrants_cognition(relevant))
            result = brain.ingest(relevant)
            self.assertIsNone(result["thought"])
            self.assertIn(history_id, result["state_pressure"]["source_ids"]["history"])
            self.assertTrue(any(
                abs(float(value)) > 0.0
                for value in result["state_pressure"]["families"]["history"].values()
            ))

            neutral = Experience(
                "A brass dial remains motionless.",
                kind="observation",
                arousal=0.0,
                novelty=0.0,
                threat=0.0,
            )
            self.assertFalse(brain._warrants_cognition(neutral))
            neutral_result = brain.ingest(neutral)
            self.assertIsNone(neutral_result["thought"])
            self.assertTrue(all(
                abs(float(value)) < 1e-12
                for value in neutral_result["state_pressure"]["families"]["history"].values()
            ))


if __name__ == "__main__":
    unittest.main()
