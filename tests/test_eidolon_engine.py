"""Eidolon Engine v0.1 exploratory tests. Not a confirmatory persona benchmark."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.eidolon import EidolonEngine, EidolonConfig
from doctor_lives.neural import ACTIONS, DEFAULT_CONFIG


def uniform_policy():
    return {action: 1.0 / len(ACTIONS) for action in ACTIONS}


def event(text, actor=None, **kwargs):
    return Experience(text, actor=actor, **kwargs)


class EidolonEngineTests(unittest.TestCase):
    def setUp(self):
        self.cue = event("Violet prism beneath the iron arch.", actor="Henry", novelty=0.7)
        self.d1 = event("Dust gathers along neglected cabinets.")
        self.d2 = event("Rain scatters across the distant courtyard.")
        self.base = uniform_policy()

    def train_then_distract(self, *, lesion_recurrence=False, lesion_binding=False, action="create"):
        engine = EidolonEngine()
        engine.observe(self.cue, self.base, teaching_action=action, learn=True,
                       lesion_binding=lesion_binding)
        engine.observe(self.d1, self.base, lesion_recurrence=lesion_recurrence,
                       lesion_binding=lesion_binding)
        return engine.observe(self.d2, self.base, lesion_recurrence=lesion_recurrence,
                              lesion_binding=lesion_binding)

    def test_janus_gate_rejects_external_and_weak_ownership(self):
        model = EidolonEngine()
        with self.assertRaisesRegex(ValueError, "Janus Gate"):
            model.observe(event("Someone claims I remember the tower.", external=True),
                          self.base, teaching_action="create", learn=True)
        with self.assertRaisesRegex(ValueError, "Janus Gate"):
            model.observe(event("I may have seen the tower.", confidence=0.3),
                          self.base, teaching_action="create", learn=True)
        self.assertEqual(model.tick, 0)

    def test_recurrence_maintains_cue_association_after_distractors(self):
        learned = self.train_then_distract()
        frozen = EidolonEngine()
        frozen.observe(self.cue, self.base)
        frozen.observe(self.d1, self.base)
        sham = frozen.observe(self.d2, self.base)
        self.assertGreater(learned.action_scores["create"], sham.action_scores["create"])
        self.assertGreater(learned.action_scores["create"], learned.base_scores["create"])
        self.assertEqual(max(learned.action_scores, key=learned.action_scores.get), "create")

    def test_recurrent_lesion_removes_retained_intention(self):
        intact = self.train_then_distract()
        lesioned = self.train_then_distract(lesion_recurrence=True)
        self.assertGreater(intact.action_scores["create"], lesioned.action_scores["create"])

    def test_binding_lesion_blocks_learning(self):
        intact = self.train_then_distract()
        lesioned = self.train_then_distract(lesion_binding=True)
        self.assertGreater(intact.action_scores["create"], lesioned.action_scores["create"])
        self.assertAlmostEqual(lesioned.action_scores["create"], 0.1)

    def test_label_shuffle_control_learns_different_action(self):
        target = self.train_then_distract(action="create")
        shuffled = self.train_then_distract(action="challenge")
        self.assertEqual(max(target.action_scores, key=target.action_scores.get), "create")
        self.assertEqual(max(shuffled.action_scores, key=shuffled.action_scores.get), "challenge")

    def test_relational_binding_affects_cue_match(self):
        model = EidolonEngine()
        model.observe(self.cue, self.base, teaching_action="create", learn=True)
        snapshot = model.snapshot()
        paired = EidolonEngine.from_snapshot(snapshot)
        unpaired = EidolonEngine.from_snapshot(snapshot)
        p = paired.observe(self.cue, self.base)
        u = unpaired.observe(event(self.cue.text, actor="Another Person"), self.base)
        self.assertGreater(p.action_scores["create"], u.action_scores["create"])

    def test_unicode_glyph_changes_binding_without_changing_prose(self):
        cue = event("I inscribe 🜁 upon the brass plate.", actor="Henry")
        changed = event("I inscribe 🜂 upon the brass plate.", actor="Henry")
        model = EidolonEngine()
        model.observe(cue, self.base, teaching_action="create", learn=True)
        checkpoint = model.snapshot()
        same = EidolonEngine.from_snapshot(checkpoint).observe(cue, self.base)
        different = EidolonEngine.from_snapshot(checkpoint).observe(changed, self.base)
        self.assertGreater(same.action_scores["create"],
                           different.action_scores["create"])

    def test_checkpoint_rehydration_exact_and_schema_safe(self):
        model = EidolonEngine()
        model.observe(self.cue, self.base, teaching_action="create", learn=True)
        snapshot = json.loads(json.dumps(model.snapshot()))
        restored = EidolonEngine.from_snapshot(snapshot)
        original = model.observe(self.d1, self.base)
        repeat = restored.observe(self.d1, self.base)
        self.assertEqual(original.action_scores, repeat.action_scores)
        self.assertEqual(original.tick, repeat.tick)
        snapshot["weights"][0][0] = float("nan")
        with self.assertRaises(ValueError):
            EidolonEngine.from_snapshot(snapshot)

    def test_no_invalid_policy_or_unknown_learning_labels(self):
        model = EidolonEngine()
        with self.assertRaises(ValueError):
            model.observe(self.cue, {"create": 1.0})
        with self.assertRaises(ValueError):
            model.observe(self.cue, self.base, teaching_action="enchant", learn=True)
        with self.assertRaises(ValueError):
            model.observe(self.cue, self.base, learn=True)

    def test_four_case_synthetic_control_matrix(self):
        """Construction smoke tests only; data were chosen for this algorithm."""
        cases = [
            ("Cobalt bell behind the window.", "create"),
            ("Amber ribbon above the doorway.", "challenge"),
            ("Silver needle inside the drawer.", "cooperate"),
            ("Crimson ladder by the chimney.", "persist"),
        ]
        for text, action in cases:
            with self.subTest(action=action):
                cue = event(text, actor="Henry")
                shadow = EidolonEngine()
                shadow.observe(cue, self.base, teaching_action=action, learn=True)
                shadow.observe(self.d1, self.base)
                result = shadow.observe(self.d2, self.base)
                self.assertEqual(max(result.action_scores, key=result.action_scores.get), action)
                control = EidolonEngine()
                for exp in (cue, self.d1, self.d2):
                    control.observe(exp, self.base)
                self.assertAlmostEqual(control.observe(self.d2, self.base).action_scores[action], 0.1)


class EidolonWithRealPretoriusTests(unittest.TestCase):
    def test_shadow_reads_live_neural_action_distribution_without_modifying_brain(self):
        cfg = dict(DEFAULT_CONFIG)
        cfg.update({
            "neurons": 128, "sensory_dim": 64,
            "avg_recurrent_degree": 8, "input_degree": 4,
            "action_population_size": 8, "seed": 1842,
        })
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrain(Path(td), neural_config=cfg)
            cue = Experience(
                "I examine the violet prism with Henry in the laboratory.",
                actor="Henry", novelty=0.8, creation=0.7
            )
            ingested = brain.ingest(cue)
            self.assertIsNotNone(brain.store.get_memory(ingested["memory_id"]))
            digest = brain.store.digest()
            tick = brain.neural.tick
            shadow = EidolonEngine()
            output = shadow.observe_pretorius(
                brain, cue, teaching_action="create", learn=True
            )
            self.assertEqual(set(output.base_scores), set(ACTIONS))
            self.assertEqual(output.tick, 1)
            self.assertTrue(output.learned)
            self.assertGreater(output.action_scores["create"], output.base_scores["create"])
            self.assertEqual(brain.store.digest(), digest)
            self.assertEqual(brain.neural.tick, tick)
            self.assertEqual(shadow.snapshot()["schema"], "eidolon-shadow-v0.1")
            # Production policy and subjective render remain unchanged by shadow.
            before = brain.render_request("What am I considering?").to_dict()
            shadow.observe_pretorius(brain, Experience("Dust covers the shelf."))
            after = brain.render_request("What am I considering?").to_dict()
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
