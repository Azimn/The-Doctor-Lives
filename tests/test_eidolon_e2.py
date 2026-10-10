"""E2: no-cue intention construction tests, not independent behavioral proof."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.eidolon import EidolonEngine
from doctor_lives.neural import ACTIONS, DEFAULT_CONFIG


BASE = {a: 0.1 for a in ACTIONS}
CASES = (
    ("Cobalt bell behind the window.", "create"),
    ("Amber ribbon above the doorway.", "challenge"),
    ("Silver needle inside the drawer.", "cooperate"),
    ("Crimson ladder by the chimney.", "persist"),
)


class NoCueProspectiveTests(unittest.TestCase):
    @staticmethod
    def train(text: str, action: str, *, learn: bool = True) -> EidolonEngine:
        e = EidolonEngine()
        e.observe(Experience(text, actor="Henry"), BASE,
                  teaching_action=action if learn else None,
                  learn=learn)
        e.advance_without_cue(3)
        return e

    def test_delayed_readout_has_no_cue_at_decision_boundary(self):
        for text, action in CASES:
            with self.subTest(action=action):
                model = self.train(text, action)
                intact = model.probe_intention(BASE)
                lesion = model.probe_intention(BASE, lesion_recurrence=True)
                self.assertGreater(intact.action_scores[action],
                                   lesion.action_scores[action])
                self.assertAlmostEqual(lesion.action_scores[action], 0.1)
                self.assertEqual(
                    max(intact.action_scores, key=intact.action_scores.get),
                    action
                )
                self.assertGreater(intact.recurrent_strength, 0.0)
                self.assertEqual(lesion.recurrent_strength, 0.0)

    def test_no_learning_and_cue_only_matched_exposure(self):
        for text, action in CASES:
            with self.subTest(action=action):
                unlearned = self.train(text, action, learn=False)
                learned = self.train(text, action)
                self.assertAlmostEqual(
                    unlearned.probe_intention(BASE).action_scores[action], 0.1
                )
                self.assertAlmostEqual(
                    learned.probe_intention(
                        BASE, lesion_recurrence=True
                    ).action_scores[action], 0.1
                )

    def test_no_cue_advance_equals_trace_decay_and_skips_binding(self):
        model = EidolonEngine()
        model.observe(Experience(CASES[0][0], actor="Henry"), BASE,
                      teaching_action="create", learn=True)
        before = model.snapshot()
        model.advance_without_cue(3)
        after = model.snapshot()
        self.assertEqual(before["weights"], after["weights"])
        for earlier, later in zip(before["intention_trace"], after["intention_trace"]):
            self.assertAlmostEqual(later,
                                   earlier * model.config.trace_decay ** 3)
        self.assertEqual(after["tick"], before["tick"] + 3)

    def test_zero_tick_no_cue_does_not_change_state(self):
        model = self.train(CASES[0][0], "create")
        prior = model.snapshot()
        model.advance_without_cue(0)
        self.assertEqual(prior, model.snapshot())

    def test_probe_is_read_only_and_cloneable(self):
        model = self.train(CASES[1][0], "challenge")
        prior = json.loads(json.dumps(model.snapshot()))
        first = model.probe_intention(BASE)
        again = model.probe_intention(BASE)
        cloned = EidolonEngine.from_snapshot(prior).probe_intention(BASE)
        self.assertEqual(first.action_scores, again.action_scores)
        self.assertEqual(first.action_scores, cloned.action_scores)
        self.assertEqual(model.snapshot(), prior)

    def test_no_cue_probes_reject_bad_base_scores(self):
        model = EidolonEngine()
        with self.assertRaises(ValueError):
            model.probe_intention({"create": 1.0})
        with self.assertRaises(ValueError):
            model.probe_intention({a: float("nan") for a in ACTIONS})

    def test_no_cue_tick_validation_is_fail_closed(self):
        model = EidolonEngine()
        for invalid in (-1, True, 1.5, "4", 1000001):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    model.advance_without_cue(invalid)
        self.assertEqual(model.tick, 0)

    def test_external_claim_cannot_train_trace(self):
        model = EidolonEngine()
        with self.assertRaisesRegex(ValueError, "Janus Gate"):
            model.observe(
                Experience("A stranger says this was my laboratory.",
                           external=True),
                BASE, teaching_action="create", learn=True
            )
        model.advance_without_cue(3)
        self.assertAlmostEqual(
            model.probe_intention(BASE).action_scores["create"], 0.1
        )

    def test_real_pretorius_policy_counterfactual_preserves_state(self):
        cfg = dict(DEFAULT_CONFIG)
        cfg.update({
            "neurons": 128, "sensory_dim": 64, "avg_recurrent_degree": 8,
            "input_degree": 4, "action_population_size": 8, "seed": 1842
        })
        with tempfile.TemporaryDirectory() as d:
            brain = PretoriusBrain(Path(d), neural_config=cfg)
            experience = Experience(
                "I promise Henry to finish the anatomical apparatus.",
                actor="Henry", creation=0.8
            )
            brain.ingest(experience)
            base = brain.neural.action_scores()
            before = (brain.store.digest(), brain.neural.tick,
                      brain.render_request().to_dict())
            model = EidolonEngine()
            model.observe_pretorius(brain, experience,
                                    teaching_action="create", learn=True)
            model.advance_without_cue(3)
            out = model.probe_intention(brain.neural.action_scores())
            lesion = model.probe_intention(
                brain.neural.action_scores(), lesion_recurrence=True
            )
            self.assertGreater(out.action_scores["create"],
                               lesion.action_scores["create"])
            self.assertEqual(lesion.action_scores, base)
            self.assertEqual(
                before,
                (brain.store.digest(), brain.neural.tick,
                 brain.render_request().to_dict())
            )


if __name__ == "__main__":
    unittest.main()
