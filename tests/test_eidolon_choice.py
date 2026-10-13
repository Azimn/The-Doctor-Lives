"""D3 disposable-clone causal policy interface tests, construction only."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.eidolon_choice import run_disposable_policy_probe
from doctor_lives.neural import DEFAULT_CONFIG
from scripts.run_eidolon_d3 import main as run_assay


def cfg():
    config = dict(DEFAULT_CONFIG)
    config.update({
        "neurons": 128, "sensory_dim": 64,
        "avg_recurrent_degree": 8, "input_degree": 4,
        "action_population_size": 8, "seed": 1842,
    })
    return config


class DisposablePolicyTests(unittest.TestCase):
    def test_four_matched_clone_outcomes_are_expected_by_design(self):
        output = run_assay()
        outcomes = output["conditions"]
        self.assertEqual(
            {key: value["selected_action"] for key, value in outcomes.items()},
            {
                "sham": "challenge", "intact": "persist",
                "history_lesion": "challenge", "clock_lesion": "challenge",
            }
        )
        self.assertFalse(outcomes["sham"]["intervention_applied"])
        self.assertTrue(outcomes["intact"]["intervention_applied"])
        self.assertFalse(outcomes["history_lesion"]["intervention_applied"])
        self.assertFalse(outcomes["clock_lesion"]["intervention_applied"])
        self.assertTrue(outcomes["intact"]["source_commitment_in_gate"])
        self.assertTrue(outcomes["intact"]["source_episode_witness_in_gate"])
        self.assertTrue(all(x["identical_parent_state_at_clone_start"]
                            for x in outcomes.values()))
        self.assertTrue(all(x["persisted_thought_count"] >= 1
                            for x in outcomes.values()))
        self.assertTrue(output["parent_database_unchanged"])
        self.assertTrue(output["parent_recurrent_tick_unchanged"])
        self.assertTrue(output["parent_checkpoint_unchanged"])

    def test_fails_closed_for_unmarked_brain(self):
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrain(Path(td), neural_config=cfg())
            original = brain._state_policy_scores
            with self.assertRaises(PermissionError):
                run_disposable_policy_probe(brain, enabled=True)
            self.assertEqual(brain._state_policy_scores, original)

    def test_original_policy_callable_restored_if_clone_think_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            brain = PretoriusBrain(path, neural_config=cfg())
            brain.ingest(Experience(
                "I examined the anatomical apparatus alongside Henry.",
                actor="Henry", kind="interaction", confidence=.9,
            ))
            brain.add_commitment(
                "Finish the anatomical apparatus", actor="Henry",
                due_tick=brain.store.tick, importance=.8,
            )
            (path / ".eidolon_disposable_clone").write_text("research clone\n")
            original = brain._state_policy_scores
            with patch.object(brain, "think", side_effect=RuntimeError("injected failure")):
                with self.assertRaisesRegex(RuntimeError, "injected failure"):
                    run_disposable_policy_probe(brain, enabled=True)
            self.assertEqual(brain._state_policy_scores, original)


if __name__ == "__main__":
    unittest.main()
