from __future__ import annotations

import unittest

from doctor_lives.awareness import AwarenessCandidate, AwarenessPolicy, AwarenessRouter
from doctor_lives.phenomenology import (
    AwarenessLevel,
    ObjectiveProvenance,
    PhenomenalEvent,
    PhenomenalMode,
    PrivacyState,
)


class AwarenessRouterTests(unittest.TestCase):
    def event(self, event_id: str, text: str) -> PhenomenalEvent:
        return PhenomenalEvent(
            event_id=event_id,
            tick=1,
            subject_id="subject-gamma",
            mode=PhenomenalMode.FEELING,
            awareness=AwarenessLevel.LATENT,
            canonical_first_person=text,
            privacy=PrivacyState.PRIVATE,
            projection_rule_version="uppb-p3",
            source_state_digest="sha256:awareness-state",
            objective_provenance=ObjectiveProvenance(
                evidence_class="mechanistic_projection",
                source="test",
            ),
        )

    def test_router_is_capacity_limited(self):
        router = AwarenessRouter(
            AwarenessPolicy(
                conscious_capacity=2,
                focal_capacity=1,
                conscious_threshold=0.30,
                focal_threshold=0.50,
                preconscious_threshold=0.15,
            )
        )
        candidates = [
            AwarenessCandidate(self.event("a", "I feel a sharp concern."), salience=.9, change=.9, novelty=.8, goal_relevance=.9),
            AwarenessCandidate(self.event("b", "I feel tired."), salience=.8, change=.6, goal_relevance=.8),
            AwarenessCandidate(self.event("c", "I feel slightly cold."), salience=.7, change=.5, goal_relevance=.7),
            AwarenessCandidate(self.event("d", "Something faintly bothers me."), salience=.3),
        ]
        decisions = router.route(candidates)
        conscious = [
            d for d in decisions
            if d.awareness in {AwarenessLevel.CONSCIOUS, AwarenessLevel.FOCAL}
        ]
        focal = [d for d in decisions if d.awareness is AwarenessLevel.FOCAL]
        self.assertEqual(len(conscious), 2)
        self.assertEqual(len(focal), 1)

    def test_habituation_can_demote_stable_background_state(self):
        router = AwarenessRouter()
        event = self.event("cold", "I feel a little chilly.")
        fresh = AwarenessCandidate(
            event,
            salience=.7,
            change=.7,
            novelty=.8,
            goal_relevance=.4,
            habituation=.0,
        )
        habituated = AwarenessCandidate(
            event,
            salience=.7,
            change=.0,
            novelty=.0,
            goal_relevance=.1,
            habituation=1.0,
        )
        fresh_decision = router.route([fresh])[0]
        habituated_decision = router.route([habituated])[0]
        self.assertGreater(fresh_decision.priority, habituated_decision.priority)
        self.assertIn(
            fresh_decision.awareness,
            {AwarenessLevel.CONSCIOUS, AwarenessLevel.FOCAL},
        )
        self.assertIn(
            habituated_decision.awareness,
            {AwarenessLevel.LATENT, AwarenessLevel.PRECONSCIOUS},
        )

    def test_conflict_and_change_can_promote_event(self):
        router = AwarenessRouter()
        quiet = AwarenessCandidate(
            self.event("quiet", "I am unsure what I feel."),
            salience=.3,
            change=.0,
            conflict=.0,
            goal_relevance=.1,
        )
        conflicted = AwarenessCandidate(
            self.event("conflicted", "I want to stay, but I also want to leave."),
            salience=.6,
            change=.8,
            conflict=1.0,
            goal_relevance=.8,
            novelty=.6,
        )
        decisions = {d.event.event_id: d for d in router.route([quiet, conflicted])}
        self.assertGreater(
            decisions["conflicted"].priority,
            decisions["quiet"].priority,
        )
        self.assertIn(
            decisions["conflicted"].awareness,
            {AwarenessLevel.CONSCIOUS, AwarenessLevel.FOCAL},
        )

    def test_routing_does_not_mutate_source_event(self):
        router = AwarenessRouter()
        source = self.event("source", "I feel a sudden chill.")
        candidate = AwarenessCandidate(
            source,
            salience=.9,
            change=.9,
            novelty=.9,
            goal_relevance=.8,
        )
        decision = router.route([candidate])[0]
        self.assertIs(source.awareness, AwarenessLevel.LATENT)
        self.assertIsNot(source, decision.event)
        self.assertIn(
            decision.awareness,
            {AwarenessLevel.CONSCIOUS, AwarenessLevel.FOCAL},
        )

    def test_fixed_candidates_route_deterministically(self):
        router = AwarenessRouter()
        candidates = [
            AwarenessCandidate(self.event("a", "I feel uneasy."), salience=.6, novelty=.4),
            AwarenessCandidate(self.event("b", "I feel tired."), salience=.5, change=.3),
        ]
        first = router.route(candidates)
        second = router.route(candidates)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
