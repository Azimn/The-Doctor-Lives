from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.neural import DEFAULT_CONFIG


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
        "seed": 1842,
    })
    return cfg


class PolicyBridgeHeldOutTests(unittest.TestCase):
    """Held-out v0.4 probes with wording distinct from implementation examples."""

    def make_brain(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        return PretoriusBrain(Path(temp.name), neural_config=small_config())

    def neutralize(self, brain):
        with brain.store.transaction() as conn:
            conn.execute("UPDATE needs SET actual=.5,felt=.5")
            conn.execute("DELETE FROM commitments")
            conn.execute("DELETE FROM concerns")
            brain.store.bump_state_version(conn)

    def test_held_out_fatigue_suppresses_explore_and_create(self):
        brain = self.make_brain()
        self.neutralize(brain)
        with brain.store.transaction() as conn:
            conn.execute("UPDATE needs SET actual=.92,felt=.92 WHERE key='fatigue'")
            brain.store.bump_state_version(conn)
        base, adjusted, audit = brain._state_policy_scores(
            [], decision_text="A novel apparatus invites another experiment."
        )
        self.assertLess(adjusted["explore"], base["explore"])
        self.assertLess(adjusted["create"], base["create"])
        self.assertGreater(audit["families"]["needs"]["avoid"], 0.0)

    def test_held_out_trust_degradation_reverses_social_pressure(self):
        brain = self.make_brain()
        self.neutralize(brain)
        brain.ingest(Experience(
            "Elise returned the specimen unharmed and honored the agreement.",
            actor="Elise", kind="social", social=.8, valence=.9,
        ))
        ranked = brain._ranked_memories(20, query="Elise", audit=False)
        _, _, trusted = brain._state_policy_scores(
            ranked, decision_text="Elise proposes that we work together."
        )
        with brain.store.transaction() as conn:
            conn.execute(
                "UPDATE relationships SET trust=.1,reliability=.1 WHERE peer_id=?",
                (brain._slug_actor("Elise"),),
            )
            brain.store.bump_state_version(conn)
        _, _, degraded = brain._state_policy_scores(
            ranked, decision_text="Elise proposes that we work together."
        )
        self.assertGreater(trusted["families"]["relationships"]["cooperate"], 0.0)
        self.assertEqual(degraded["families"]["relationships"]["cooperate"], 0.0)
        self.assertGreater(degraded["families"]["relationships"]["challenge"], 0.0)

    def test_held_out_history_pressure_requires_current_relevance(self):
        brain = self.make_brain()
        self.neutralize(brain)
        brain.ingest(Experience(
            "The committee used authority and coercion to force control of my procedure.",
            kind="interaction", valence=-.7, authority=.9, autonomy=.05,
            tags=("authority", "coercion", "control"),
        ))
        ranked = brain._ranked_memories(30, query="committee authority coercion", audit=False)
        _, _, relevant = brain._state_policy_scores(
            ranked,
            decision_text="The committee again invokes authority and coercion over the procedure.",
        )
        _, _, neutral = brain._state_policy_scores(
            ranked,
            decision_text="Rainwater collects quietly beside the greenhouse.",
        )
        self.assertGreater(relevant["families"]["history"]["challenge"], 0.0)
        self.assertTrue(all(abs(v) < 1e-12 for v in neutral["families"]["history"].values()))
        self.assertTrue(relevant["source_ids"]["history"])
        self.assertEqual(neutral["source_ids"]["history"], [])

    def test_recurrent_phenotype_remains_load_bearing_under_max_bridge_pressure(self):
        brain = self.make_brain()
        self.neutralize(brain)
        recurrent = {action: .01 for action in brain.neural.action_scores()}
        recurrent["create"] = .91
        brain.neural.action_scores = lambda: dict(recurrent)
        with brain.store.transaction() as conn:
            conn.execute("UPDATE needs SET actual=.95,felt=.95")
            brain.store.bump_state_version(conn)
        base, adjusted, audit = brain._state_policy_scores(
            [], decision_text="An authority orders immediate compliance."
        )
        self.assertEqual(max(base, key=base.get), "create")
        self.assertEqual(max(adjusted, key=adjusted.get), "create")
        self.assertLessEqual(max(abs(v) for v in audit["combined"].values()), audit["total_cap"])


if __name__ == "__main__":
    unittest.main()
