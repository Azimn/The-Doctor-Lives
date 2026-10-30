"""Opt-in Mnemosyne -> original Noesis causal feedback and negative controls."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime


def cfg():
    c = dict(DEFAULT_CONFIG)
    c.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    return c


def setup_run(root: Path, *, include_relevant_memory: bool):
    from test_six_organ_mnemosyne_pilot import seed_epistemic_gap

    runtime = SixOrganRuntime.open(root, neural_config=cfg())
    # Both arms receive exactly the same inputs and policy checkpoint.
    if include_relevant_memory:
        runtime.sensus.acquire_existing_percept(
            {
                "channel": "world",
                "source": "paired-first-person-pendulum",
                "percept": "I saw a silver pendulum swinging beside the cabinet.",
            },
            host_authorized=True,
        )
        runtime.sensus.acquire_existing_percept(
            {
                "channel": "world",
                "source": "paired-first-person-garden",
                "percept": "I heard the garden gate creak at sunset.",
            },
            host_authorized=True,
        )
    seed_epistemic_gap(
        runtime, identifier="paired-pendulum-gap",
        description="the silver pendulum", uncertainty=.99, importance=.99,
    )
    return runtime


class RecollectionInfluencesCognitionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_selected_recollection_changes_actual_cognitive_policy_input(self):
        recalled = setup_run(self.root / "recalled", include_relevant_memory=True)
        control = setup_run(self.root / "control", include_relevant_memory=True)
        a = recalled.mnemosyne.opt_in_endogenous_recollection()
        b = control.mnemosyne.opt_in_endogenous_recollection()
        self.assertEqual(a.deliberate(recall_cost=0).action, "recall")
        self.assertEqual(b.deliberate(recall_cost=0).action, "recall")

        treatment = a.reflect_selected_recollection()
        # Same brain mechanisms, same states and same endogenous selection.
        # Control consumes the recollection capability without allowing
        # retrieved first-person content to influence the next decision.
        b.recollect()
        baseline = control._port.brain.think("mnemosyne_private_reflection")
        self.assertIsNotNone(treatment.next_policy_decision_id)
        self.assertTrue(treatment.cue_sha256)
        self.assertGreater(treatment.relevant_lines, 0)
        with recalled._port.brain.store.connect() as conn:
            a_row = conn.execute(
                "SELECT * FROM policy_decisions WHERE id=?",
                (treatment.next_policy_decision_id,),
            ).fetchone()
        with control._port.brain.store.connect() as conn:
            b_row = conn.execute(
                "SELECT * FROM policy_decisions WHERE id=?",
                (baseline["policy_decision_id"],),
            ).fetchone()
        self.assertEqual(
            a_row["policy_version"], b_row["policy_version"],
        )
        a_audit = json.loads(a_row["state_pressure_json"])
        b_audit = json.loads(b_row["state_pressure_json"])
        self.assertEqual(
            a_audit["decision_text_sha256"], treatment.cue_sha256,
        )
        self.assertNotEqual(
            a_audit["decision_text_sha256"],
            b_audit["decision_text_sha256"],
        )
        # The experiment tests the actual canonical cognitive decision,
        # not a fabricated 'recall succeeded' flag. Do not assert superiority.
        observed_difference = (
            json.loads(a_row["selected_record_ids_json"])
            != json.loads(b_row["selected_record_ids_json"])
            or json.loads(a_row["action_scores_json"])
            != json.loads(b_row["action_scores_json"])
        )
        self.assertTrue(
            observed_difference,
            "First-person recollection had no observed downstream policy effect",
        )
        self.assertEqual(treatment.next_tendency, a_row["selected_action"])
        with self.assertRaises(PermissionError):
            a.reflect_selected_recollection()

    def test_concern_without_matching_lived_memory_does_not_invent_recall(self):
        runtime = setup_run(
            self.root / "without-memory", include_relevant_memory=False,
        )
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        self.assertEqual(pilot.deliberate(recall_cost=0).action, "recall")
        with runtime._port.brain.store.connect() as db:
            before = db.execute("SELECT count(*) FROM thoughts").fetchone()[0]
        effect = pilot.reflect_selected_recollection()
        self.assertIsNone(effect.next_policy_decision_id)
        self.assertIsNone(effect.next_tendency)
        self.assertEqual(effect.relevant_lines, 0)
        self.assertIsNone(effect.cue_sha256)
        with runtime._port.brain.store.connect() as db:
            after = db.execute("SELECT count(*) FROM thoughts").fetchone()[0]
        self.assertEqual(before, after)
        # Only an unresolved *concern* is projected, which is not a memory.
        with self.assertRaises(PermissionError):
            pilot.recollect()

    def test_restart_and_unselected_request_cannot_replay_private_cognition(self):
        runtime = setup_run(self.root / "replay", include_relevant_memory=True)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        with self.assertRaises(PermissionError):
            pilot.reflect_selected_recollection()
        self.assertEqual(pilot.deliberate(recall_cost=0).action, "recall")
        effect = pilot.reflect_selected_recollection()
        self.assertIsNotNone(effect.next_policy_decision_id)
        runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "replay")
        new_pilot = reopened.mnemosyne.opt_in_endogenous_recollection()
        with self.assertRaises(PermissionError):
            new_pilot.reflect_selected_recollection()
        with reopened._port.brain.store.connect() as db:
            matches = db.execute(
                "SELECT count(*) FROM policy_decisions WHERE trigger=?",
                ("mnemosyne_private_reflection",),
            ).fetchone()[0]
        self.assertEqual(matches, 1)


if __name__ == "__main__":
    unittest.main()
