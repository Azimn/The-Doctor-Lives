"""Behavioral-contract and lesion tests for the isolated SelfBindingModulator.

This suite only validates deterministic input/output behavior and safety
boundaries. It is not an empirical character-continuity outcome test.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
import math
import unittest

from doctor_lives.awareness import AwarenessCandidate, AwarenessRouter
from doctor_lives.phenomenology import (
    AwarenessLevel,
    ObjectiveProvenance,
    PhenomenalEvent,
    PhenomenalMode,
    PrivacyState,
)
from research_prototypes.ritual_interface.self_binding_modulator import (
    BindingCandidate,
    BindingMode,
    BindingPolicy,
    EvidenceMatch,
    SelfBindingModulator,
)
from research_prototypes.ritual_interface.state import IdentitySnapshot


MANIFEST = "c" * 64
SUBJECT = "synthetic-pretorius"


def snapshot() -> IdentitySnapshot:
    return IdentitySnapshot(
        subject_id=SUBJECT,
        state_version=7,
        manifest_digest=MANIFEST,
        invariants=("core:a",),
        relationships=("relationship:a",),
        commitments=("commitment:a",),
        memories=("memory:a", "memory:b"),
        self_model_hypotheses=("self:a",),
    )


def inputs() -> tuple[BindingCandidate, ...]:
    return (
        BindingCandidate(
            "evt-a", SUBJECT, 0.45,
            (EvidenceMatch("core:a", 0.9), EvidenceMatch("memory:a", 0.5)),
        ),
        BindingCandidate(
            "evt-b", SUBJECT, 0.48,
            (EvidenceMatch("commitment:a", 0.2),),
        ),
        BindingCandidate("evt-c", SUBJECT, 0.65, ()),
    )


def run(
    mode: BindingMode = BindingMode.NORMAL,
    candidates: tuple[BindingCandidate, ...] | None = None,
    state: IdentitySnapshot | None = None,
):
    return SelfBindingModulator().run(
        state if state is not None else snapshot(),
        candidates if candidates is not None else inputs(),
        mode=mode,
        expected_manifest=MANIFEST,
        expected_state_version=7,
    )


class SelfBindingModulatorTests(unittest.TestCase):
    def test_off_is_an_exact_noop(self):
        result = run(BindingMode.OFF)
        self.assertEqual(result.gain, 0.0)
        for before, after in zip(inputs(), result.proposals):
            self.assertEqual(before.base_salience, after.proposed_salience)
            self.assertEqual(after.effective_bonus, 0.0)
        self.assertFalse(result.contradiction_freeze)

    def test_monotonic_gain_preserves_source_and_baselines(self):
        low = run(BindingMode.LOW)
        normal = run(BindingMode.NORMAL)
        high = run(BindingMode.HIGH)
        for idx in (0, 1):
            self.assertLess(low.proposals[idx].proposed_salience, normal.proposals[idx].proposed_salience)
            self.assertLess(normal.proposals[idx].proposed_salience, high.proposals[idx].proposed_salience)
        self.assertEqual(high.proposals[2].effective_bonus, 0)
        self.assertEqual([p.source_refs for p in low.proposals], [p.source_refs for p in high.proposals])
        self.assertEqual(high.snapshot_digest, snapshot().digest)
        self.assertLessEqual(max(x.requested_bonus for x in high.proposals), 0.10)

    def test_deterministic_replay_and_content_addressed_trace(self):
        first = run()
        second = run()
        self.assertEqual(first, second)
        self.assertEqual(len(first.audit_digest), 64)
        altered = inputs()[:1] + (
            BindingCandidate("evt-b", SUBJECT, .48, (EvidenceMatch("commitment:a", .8),)),
            inputs()[2],
        )
        self.assertNotEqual(first.audit_digest, run(candidates=altered).audit_digest)

    def test_saturation_clamps_effective_bonus(self):
        item = BindingCandidate("evt-a", SUBJECT, .98, (EvidenceMatch("core:a", 1),))
        result = run(BindingMode.HIGH, (item,)).proposals[0]
        self.assertAlmostEqual(result.requested_bonus, .10)
        self.assertAlmostEqual(result.proposed_salience, 1.0)
        self.assertAlmostEqual(result.effective_bonus, .02)

    def test_reference_weight_is_class_specific_and_not_count_amplified(self):
        commitment = BindingCandidate("evt-a", SUBJECT, .2, (EvidenceMatch("commitment:a", 1),))
        weak_self = BindingCandidate("evt-b", SUBJECT, .2, (EvidenceMatch("self:a", .5),))
        result = run(BindingMode.HIGH, (commitment, weak_self))
        self.assertAlmostEqual(result.proposals[0].supported_relevance, 1.0)
        self.assertAlmostEqual(result.proposals[1].supported_relevance, .5)
        many = BindingCandidate(
            "evt-c", SUBJECT, .2,
            (EvidenceMatch("core:a", 1), EvidenceMatch("memory:a", 1), EvidenceMatch("memory:b", 1)),
        )
        self.assertAlmostEqual(run(BindingMode.HIGH, (many,)).proposals[0].requested_bonus, .10)

    def test_world_contradiction_suspends_all_identity_bonuses(self):
        conflicting = BindingCandidate("evt-world", SUBJECT, .36, (), True)
        paired = inputs() + (conflicting,)
        result = run(BindingMode.HIGH, paired)
        self.assertTrue(result.contradiction_freeze)
        self.assertTrue(all(p.requested_bonus == 0 for p in result.proposals))
        self.assertEqual(tuple(p.proposed_salience for p in result.proposals),
                         tuple(c.base_salience for c in paired))
        self.assertEqual(result.proposals[-1].event_id, "evt-world")

    def test_shuffled_lesion_permutes_only_match_packets(self):
        base = run()
        shuffled = run(BindingMode.SHUFFLED)
        self.assertNotEqual(base.audit_digest, shuffled.audit_digest)
        self.assertEqual(tuple(x.event_id for x in base.proposals), tuple(x.event_id for x in shuffled.proposals))
        self.assertEqual(
            sorted(x.source_refs for x in base.proposals),
            sorted(x.source_refs for x in shuffled.proposals),
        )
        self.assertEqual(
            tuple(x.base_salience for x in base.proposals),
            tuple(x.base_salience for x in shuffled.proposals),
        )
        self.assertNotEqual(
            tuple(x.supported_relevance for x in base.proposals),
            tuple(x.supported_relevance for x in shuffled.proposals),
        )
        self.assertEqual(shuffled, run(BindingMode.SHUFFLED))

    def test_shuffled_noninformative_cases_fail_explicitly(self):
        only_one = (inputs()[0],)
        with self.assertRaisesRegex(ValueError, "at least two"):
            run(BindingMode.SHUFFLED, only_one)
        same_packet = (
            BindingCandidate("evt-a", SUBJECT, .1, (EvidenceMatch("core:a", .9),)),
            BindingCandidate("evt-b", SUBJECT, .9, (EvidenceMatch("core:a", .9),)),
        )
        with self.assertRaisesRegex(ValueError, "identical"):
            run(BindingMode.SHUFFLED, same_packet)

    def test_matrix_runs_all_matched_modes_and_is_repeatable(self):
        modulator = SelfBindingModulator()
        params = {"expected_manifest": MANIFEST, "expected_state_version": 7}
        matrix = modulator.lesion_matrix(snapshot(), inputs(), **params)
        self.assertEqual(tuple(x.mode for x in matrix), tuple(BindingMode))
        self.assertEqual(matrix, modulator.lesion_matrix(snapshot(), inputs(), **params))
        self.assertEqual({x.snapshot_digest for x in matrix}, {snapshot().digest})
        self.assertEqual({x.policy_version for x in matrix}, {"scc-self-binding-v1"})

    def test_unknown_refs_and_other_subject_are_rejected_even_in_off_mode(self):
        bad = (BindingCandidate("a", SUBJECT, .2, (EvidenceMatch("unverified", 1),)),)
        with self.assertRaisesRegex(ValueError, "unknown"):
            run(BindingMode.OFF, bad)
        wrong = (BindingCandidate("a", "other-subject", .2, (EvidenceMatch("core:a", 1),)),)
        with self.assertRaisesRegex(ValueError, "cross-subject"):
            run(candidates=wrong)

    def test_manifest_version_mismatch_rejected(self):
        engine = SelfBindingModulator()
        with self.assertRaisesRegex(ValueError, "authority"):
            engine.run(snapshot(), inputs(), expected_manifest="b"*64, expected_state_version=7)
        with self.assertRaisesRegex(ValueError, "authority"):
            engine.run(snapshot(), inputs(), expected_manifest=MANIFEST, expected_state_version=8)
        with self.assertRaisesRegex(ValueError, "authority"):
            engine.run(snapshot(), inputs(), expected_manifest=MANIFEST, expected_state_version=True)

    def test_duplicate_ids_and_cross_family_refs_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            run(candidates=(inputs()[0], inputs()[0]))
        with self.assertRaisesRegex(ValueError, "duplicate source"):
            BindingCandidate("a", SUBJECT, .2, (EvidenceMatch("core:a", 1), EvidenceMatch("core:a", .5)))
        duplicate_family = IdentitySnapshot(
            SUBJECT, 7, MANIFEST, ("same",), ("same",), (), ()
        )
        with self.assertRaisesRegex(ValueError, "multiple"):
            run(state=duplicate_family, candidates=())

    def test_numerical_validation_and_restricted_policy(self):
        for value in (float("nan"), float("inf"), -1, 1.001):
            with self.assertRaises(ValueError):
                EvidenceMatch("core:a", value)
        with self.assertRaises(TypeError):
            EvidenceMatch("core:a", True)
        with self.assertRaises(ValueError):
            BindingPolicy(max_bonus=.11)
        with self.assertRaises(TypeError):
            BindingCandidate("a", SUBJECT, .2, (), verified_world_contradiction=1)
        with self.assertRaises(TypeError):
            run(mode="normal")  # type: ignore[arg-type]

    def test_policy_and_candidates_immutable(self):
        source = inputs()
        with self.assertRaises(FrozenInstanceError):
            source[0].base_salience = 0.9
        with self.assertRaises(FrozenInstanceError):
            run().proposals[0].effective_bonus = 1.0
        self.assertEqual(source, inputs())
        changed_policy = SelfBindingModulator(BindingPolicy(version="controlled-v2"))
        changed = changed_policy.run(
            snapshot(), source, expected_manifest=MANIFEST, expected_state_version=7,
        )
        self.assertNotEqual(changed.audit_digest, run().audit_digest)

    def test_live_awareness_router_unmodified_by_trial(self):
        # Validate the isolation contract: no router call, access-state write,
        # or awareness threshold mutation occurs during binding.
        phenomenal = PhenomenalEvent(
            tick=7, subject_id=SUBJECT, mode=PhenomenalMode.PERCEPT,
            awareness=AwarenessLevel.LATENT,
            canonical_first_person="I notice something at the door.",
            privacy=PrivacyState.PRIVATE,
            projection_rule_version="p3-test",
            source_state_digest="sha256:unchanged",
            objective_provenance=ObjectiveProvenance(
                evidence_class="mechanistic_projection", source="synthetic",
            ),
        )
        router = AwarenessRouter()
        original_policy = router.policy
        before = router.route([AwarenessCandidate(phenomenal, salience=.30)])
        result = run()
        after = router.route([AwarenessCandidate(phenomenal, salience=.30)])
        self.assertEqual(before, after)
        self.assertEqual(original_policy, router.policy)
        self.assertIs(phenomenal.awareness, AwarenessLevel.LATENT)
        self.assertNotIsInstance(result.proposals[0], PhenomenalEvent)


if __name__ == "__main__":
    unittest.main()
