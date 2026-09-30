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

    def test_held_out_coercion_autonomy_biases_challenge_not_compliance(self):
        brain = self.make_brain()
        self.neutralize(brain)
        with brain.store.transaction() as conn:
            conn.execute("UPDATE needs SET actual=.94,felt=.94 WHERE key='autonomy'")
            brain.store.bump_state_version(conn)
        base, adjusted, audit = brain._state_policy_scores(
            [], decision_text="A director orders surrender of the procedure and demands obedience."
        )
        self.assertGreater(adjusted["challenge"], base["challenge"])
        self.assertLess(adjusted["comply"], base["comply"])
        self.assertGreater(audit["families"]["needs"]["challenge"], 0.0)
        self.assertLess(audit["families"]["needs"]["comply"], 0.0)

    def test_held_out_resolved_commitment_stops_pressure(self):
        brain = self.make_brain()
        self.neutralize(brain)
        cid = brain.add_commitment(
            "Deliver the galvanic notes to Elise.", actor="Elise", importance=.88
        )
        _, _, active = brain._state_policy_scores(
            [], decision_text="Deliver the galvanic notes to Elise."
        )
        brain.resolve_commitment(cid, "Notes delivered and acknowledged.", kept=True)
        _, _, resolved = brain._state_policy_scores(
            [], decision_text="Deliver the galvanic notes to Elise."
        )
        self.assertGreater(active["families"]["commitments"]["persist"], 0.0)
        self.assertTrue(all(abs(v) < 1e-12 for v in resolved["families"]["commitments"].values()))
        self.assertNotIn(cid, resolved["source_ids"]["commitments"])

    def test_held_out_resolved_concern_stops_policy_and_heartbeat_pressure(self):
        brain = self.make_brain()
        self.neutralize(brain)
        probe = Experience(
            "A pressure vessel rupture threatens the reagent room.",
            threat=.92, control=-.7, arousal=.8,
        )
        brain.ingest(probe)
        concern = brain.store.open_concerns()[0]
        _, _, active = brain._state_policy_scores(
            [], decision_text="The pressure vessel rupture threatens the reagent room."
        )
        brain.resolve_concern(concern["id"], "The vessel was replaced and the room verified safe.")
        _, _, resolved = brain._state_policy_scores(
            [], decision_text="The pressure vessel rupture threatens the reagent room."
        )
        self.assertTrue(any(abs(v) > 0 for v in active["families"]["concerns"].values()))
        self.assertTrue(all(abs(v) < 1e-12 for v in resolved["families"]["concerns"].values()))
        self.assertEqual(brain.heartbeat(2)["thoughts"], [])

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
