"""Matched opt-in PR #59 endogenous recall tests on one Doctor BrainStore."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.mnemosyne_pilot import MnemosyneEndogenousPilot
from doctor_lives.models import SubjectFrame, SubjectRendererCapability
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime


def small_config():
    c = dict(DEFAULT_CONFIG)
    c.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
             input_degree=4, action_population_size=8, seed=1842)
    return c


def seed_epistemic_gap(runtime, *, source="preview_sensus_conflict",
                       actor="PREVIEW_HOST", identifier="trusted-gap-1",
                       description="the glass vessel", uncertainty=0.99,
                       importance=0.99):
    """Explicitly labeled host-verified research fixture, not user speech."""
    brain = runtime._port.brain
    with brain.store.transaction() as db:
        db.execute(
            """INSERT INTO concerns
            (id,created_tick,updated_tick,description,status,importance,
             uncertainty,actor,source) VALUES(?,?,?,?,'open',?,?,?,?)""",
            (identifier, brain.store.tick, brain.store.tick, description,
             importance, uncertainty, actor, source),
        )
        brain.store.bump_state_version(db)


class EndogenousRecallOrganTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def runtime(self, name):
        return SixOrganRuntime.open(self.root / name, neural_config=small_config())

    def test_qualified_internal_gap_causes_selected_recall_and_read_only_frame(self):
        runtime = self.runtime("one")
        runtime.sensus.acquire_existing_percept(
            {"channel": "world", "source": "fixture-vessel",
             "percept": "I heard a glass vessel shatter behind me."},
            host_authorized=True,
        )
        seed_epistemic_gap(runtime)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        decision = pilot.deliberate(recall_cost=0.0)
        self.assertEqual(decision.action, "recall")
        self.assertEqual(decision.selected_gap_id, "trusted-gap-1")
        self.assertGreater(decision.recall_pressure, 0.9)
        self.assertEqual(decision.initiated_by, "host_scheduled_internal_policy")
        with runtime._port.brain.store.connect() as db:
            rec = db.execute(
                "SELECT * FROM policy_decisions WHERE id=?", (decision.decision_id,)
            ).fetchone()
        self.assertEqual(rec["selected_action"], "recall")
        self.assertEqual(rec["policy_version"],
                         "preview-epistemic-deliberation-v0.1")
        audit = json.loads(rec["state_pressure_json"])
        self.assertFalse(audit["autonomous_model_authorship_proven"])
        self.assertFalse(audit["memory_retrieval_performed"])
        self.assertTrue(audit["question_sha256"])
        before = runtime._port.brain.store.digest()
        frame = pilot.recollect()
        self.assertIsInstance(frame, SubjectFrame)
        lines = SubjectRendererCapability.read(frame)
        self.assertTrue(lines)
        self.assertEqual(before, runtime._port.brain.store.digest())
        self.assertNotIn("neural_checkpoint_sha256", "\n".join(lines))
        with self.assertRaises(PermissionError):
            pilot.recollect()

    def test_matched_no_gap_ablation_blocks_recollection_without_new_brain(self):
        control = self.runtime("control")
        with_gap = self.runtime("treatment")
        seed_epistemic_gap(with_gap)
        a = control.mnemosyne.opt_in_endogenous_recollection()
        b = with_gap.mnemosyne.opt_in_endogenous_recollection()
        none = a.deliberate(recall_cost=0.0)
        present = b.deliberate(recall_cost=0.0)
        self.assertNotEqual(none.action, "recall")
        self.assertIsNone(none.selected_gap_id)
        self.assertEqual(present.action, "recall")
        with self.assertRaises(PermissionError):
            a.recollect()
        self.assertIs(a._port, control._port)
        self.assertIs(b._port, with_gap._port)

    def test_forged_or_reported_gap_is_not_an_internally_selected_cue(self):
        runtime = self.runtime("forged")
        seed_epistemic_gap(runtime, source="external_user_message",
                           actor="User", identifier="external-claim")
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        decision = pilot.deliberate(recall_cost=0)
        self.assertNotEqual(decision.action, "recall")
        with self.assertRaises(PermissionError):
            pilot.recollect()

    def test_low_information_pressure_and_high_cost_decline_recollection(self):
        runtime = self.runtime("low-pressure")
        seed_epistemic_gap(runtime, uncertainty=0.01, importance=0.01)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        decision = pilot.deliberate(recall_cost=1)
        self.assertNotEqual(decision.action, "recall")
        self.assertLess(decision.recall_pressure, 0.01)

    def test_restart_preserves_cooldown_and_prevents_pending_grant_replay(self):
        runtime = self.runtime("restart")
        seed_epistemic_gap(runtime)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        first = pilot.deliberate(recall_cost=0.0)
        self.assertEqual(first.action, "recall")
        runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "restart")
        new_pilot = reopened.mnemosyne.opt_in_endogenous_recollection()
        with self.assertRaises(PermissionError):
            new_pilot.recollect()
        cooled = new_pilot.deliberate(recall_cost=0.0)
        self.assertNotEqual(cooled.action, "recall")
        with reopened._port.brain.store.connect() as db:
            matches = db.execute(
                "SELECT count(*) FROM policy_decisions WHERE trigger=?",
                ("preview_endogenous_recall_v01",),
            ).fetchone()[0]
        self.assertEqual(matches, 2)
        self.assertFalse((self.root / "restart" / "mnemosyne.sqlite3").exists())

    def test_invalid_inputs_and_reentrant_decision_fail_closed(self):
        runtime = self.runtime("guards")
        with self.assertRaises(PermissionError):
            MnemosyneEndogenousPilot(runtime._port)
        seed_epistemic_gap(runtime)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        for cost in (-0.1, 2.0, float("nan"), True):
            with self.subTest(cost=cost), self.assertRaises(ValueError):
                pilot.deliberate(recall_cost=cost)
        selected = pilot.deliberate(recall_cost=0.0)
        self.assertEqual(selected.action, "recall")
        with self.assertRaises(RuntimeError):
            pilot.deliberate()
        pilot.recollect()


if __name__ == "__main__":
    unittest.main()
