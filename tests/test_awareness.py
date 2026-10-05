from __future__ import annotations

import unittest

from doctor_lives.awareness import (
    AwarenessCandidate,
    AwarenessDecision,
    AwarenessPolicy,
    AwarenessRouter,
)
from doctor_lives.phenomenology import (
    AwarenessLevel,
    ObjectiveProvenance,
    PhenomenalEvent,
    PhenomenalMode,
    PrivacyState,
)


class AwarenessRouterTests(unittest.TestCase):
    def event(
        self,
        label: str,
        text: str,
        *,
        subject_id: str = "subject-gamma",
    ) -> PhenomenalEvent:
        return PhenomenalEvent(
            tick=1,
            subject_id=subject_id,
            mode=PhenomenalMode.FEELING,
            awareness=AwarenessLevel.LATENT,
            canonical_first_person=text,
            privacy=PrivacyState.PRIVATE,
            projection_rule_version="uppb-p3h",
            source_state_digest="sha256:awareness-state",
            objective_provenance=ObjectiveProvenance(
                evidence_class="mechanistic_projection",
                source="test",
                record_ids=(f"record:{label}",),
            ),
            source_event_refs=(f"source:{label}",),
        )

    def test_awareness_decision_cannot_be_fabricated_directly(self):
        with self.assertRaises(TypeError):
            AwarenessDecision(
                event=self.event("forged", "I feel certain."),
                priority=1.0,
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
        decisions = {d.event.subject_text: d for d in router.route([quiet, conflicted])}
        self.assertGreater(
            decisions["I want to stay, but I also want to leave."].priority,
            decisions["I am unsure what I feel."].priority,
        )
        self.assertIn(
            decisions["I want to stay, but I also want to leave."].awareness,
            {AwarenessLevel.CONSCIOUS, AwarenessLevel.FOCAL},
        )

    def test_routing_does_not_mutate_source_event_or_identity(self):
        router = AwarenessRouter()
        source = self.event("source", "I feel a sudden chill.")
        source_id = source.event_id
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
        self.assertEqual(source_id, decision.event.event_id)
        self.assertIn(
            decision.awareness,
            {AwarenessLevel.CONSCIOUS, AwarenessLevel.FOCAL},
        )

    def test_mixed_subject_candidates_fail_closed_before_capacity_competition(self):
        router = AwarenessRouter()
        a = AwarenessCandidate(
            self.event("a", "I feel uneasy.", subject_id="subject-a"),
            salience=.8,
        )
        b = AwarenessCandidate(
            self.event("b", "I feel tired.", subject_id="subject-b"),
            salience=.9,
        )
        with self.assertRaises(ValueError):
            router.route([a, b])

    def test_candidate_numeric_inputs_are_normalized(self):
        candidate = AwarenessCandidate(
            self.event("numeric", "I feel uneasy."),
            salience="0.5",  # type: ignore[arg-type]
            change=1,
            novelty=0,
        )
        self.assertEqual(candidate.salience, 0.5)
        self.assertIsInstance(candidate.salience, float)
        self.assertEqual(candidate.change, 1.0)

    def test_malformed_nonfinite_and_boolean_candidate_inputs_fail_closed(self):
        with self.assertRaises(TypeError):
            AwarenessCandidate(
                self.event("bad-string", "I feel uneasy."),
                salience="not-a-number",  # type: ignore[arg-type]
            )
        with self.assertRaises(TypeError):
            AwarenessCandidate(
                self.event("bool", "I feel uneasy."),
                salience=True,  # type: ignore[arg-type]
            )
        with self.assertRaises(ValueError):
            AwarenessCandidate(
                self.event("nan", "I feel uneasy."),
                salience=float("nan"),
            )
        with self.assertRaises(ValueError):
            AwarenessCandidate(
                self.event("inf", "I feel uneasy."),
                salience=float("inf"),
            )

    def test_policy_requires_integer_capacities_and_normalizes_thresholds(self):
        policy = AwarenessPolicy(
            conscious_capacity=2,
            focal_capacity=1,
            conscious_threshold="0.35",  # type: ignore[arg-type]
            focal_threshold=0.55,
            preconscious_threshold=0.20,
        )
        self.assertEqual(policy.conscious_threshold, 0.35)
        self.assertIsInstance(policy.conscious_threshold, float)

        with self.assertRaises(TypeError):
            AwarenessPolicy(conscious_capacity=1.5)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            AwarenessPolicy(conscious_capacity=True)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            AwarenessPolicy(focal_capacity=False)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            AwarenessPolicy(conscious_threshold=float("nan"))
        with self.assertRaises(ValueError):
            AwarenessPolicy(focal_threshold=float("inf"))

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
