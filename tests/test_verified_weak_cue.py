"""Weak recall cues must resolve only uniquely verified, relevant episodes."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import tempfile
import unittest

HAVE = (importlib.util.find_spec("synthetic_ipseity") is not None
        and importlib.util.find_spec("sensus_artificialis") is not None)


@unittest.skipUnless(HAVE, "Reviewed optional donors required")
class VerifiedWeakCueTests(unittest.TestCase):
    def setUp(self):
        from doctor_lives.three_organ_preview import ThreeOrganPretoriusPreview
        from doctor_lives.neural import DEFAULT_CONFIG
        from sensus_artificialis import Percept, Evidence
        self.Host = ThreeOrganPretoriusPreview
        self.Percept = Percept
        self.Evidence = Evidence
        cfg = dict(DEFAULT_CONFIG)
        cfg.update(neurons=64, sensory_dim=32, avg_recurrent_degree=5,
                   input_degree=3, action_population_size=6)
        self.cfg = cfg
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def claim(self, name, tick, channel, attribute, value, serial):
        return self.Percept(
            event_id=name + "-" + channel,
            channel=channel, evidence=self.Evidence.OBSERVED,
            source_ref="trusted:" + name + ":" + channel,
            tick=tick, attribute=attribute, value=value,
            confidence=.98, object_hint="instrument",
            features=(("serial", serial), ("shape", "round")),
        )

    def user(self, name, tick, utterance):
        return self.Percept(
            event_id=name, channel="conversation",
            evidence=self.Evidence.REPORTED,
            source_ref="trusted:" + name,
            tick=tick, attribute="message", value=utterance,
            confidence=.90, object_hint="visitor",
        )

    def step(self, host, percepts):
        return host.cycle(percepts,
                          trusted_source_refs=frozenset(x.source_ref for x in percepts),
                          now_ms=host._scene_tick * 100_000)

    def seed_episode(self, host, attribute, serial):
        tick = host._scene_tick
        conflict = (
            self.claim(serial+"-conflict",tick,"vision",attribute,"451 grams",serial),
            self.claim(serial+"-conflict",tick,"instrument",attribute,"919 grams",serial),
        )
        first = self.step(host, conflict)
        self.assertEqual(first["scene_conflicts"], 1)
        tick = host._scene_tick
        agreed = (
            self.claim(serial+"-agreed",tick,"vision",attribute,"451 grams",serial),
            self.claim(serial+"-agreed",tick,"instrument",attribute,"451 grams",serial),
        )
        result = self.step(host, agreed)
        self.assertEqual(len(result["resolved_epistemic_gap_ids"]), 1)

    def test_single_explicit_weak_cue_matches_unique_verified_episode(self):
        history = []
        with self.Host(Path(self.tmp.name)/"three-organ-preview",
                       enabled=True, renderer=lambda text: history.append(text)
                       or "I need to check the evidence.", neural_config=self.cfg) as host:
            self.seed_episode(host, "laboratory balance reading", "unique-S1")
            p = self.user("ask-balance",host._scene_tick,
                          "Do you remember the balance?")
            self.step(host,(p,))
            self.assertIn("I remember two later observations of the laboratory balance reading "
                          "agreeing at 451 grams",history[-1])
            q = self.user("ask-life",host._scene_tick,
                          "Does creating life entail responsibility?")
            self.step(host,(q,))
            self.assertNotIn("I remember two later observations of the laboratory balance",
                             history[-1])

    def test_ambiguous_explicit_weak_cue_with_two_proven_episodes_withholds(self):
        history = []
        with self.Host(Path(self.tmp.name)/"three-organ-preview",
                       enabled=True, renderer=lambda text: history.append(text)
                       or "I need to check the evidence.", neural_config=self.cfg) as host:
            self.seed_episode(host, "laboratory balance reading", "ambig-S1")
            self.seed_episode(host, "calibrated balance reading", "ambig-S2")
            p = self.user("ask-ambiguous",host._scene_tick,
                          "Do you remember the balance?")
            self.step(host,(p,))
            self.assertNotIn("I remember two later observations of the laboratory balance",
                             history[-1])
            self.assertNotIn("I remember two later observations of the calibrated balance",
                             history[-1])


if __name__ == "__main__":
    unittest.main()
