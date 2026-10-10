"""Research-only mechanics and source-boundary tests for the Predictive Self Loop."""
from __future__ import annotations

import math
import json
import tempfile
from pathlib import Path
import unittest

from research_prototypes.predictive_self.loop import (
    EvidenceKind, ObservedEpisode, PredictiveSelfLoop,
    SelfSnapshot, SemanticClaim, Situation,
)
from research_prototypes.predictive_self.adapter import (
    snapshot_from_brain, witnessed_policy_decision,
)


def fixture():
    snap = SelfSnapshot(
        subject_id="pretorius-test", state_digest="a" * 64,
        state_version=2, manifest_digest="b" * 64,
        cutoff_tick=12,
        actions=("challenge", "cooperate", "explore"),
        base_probabilities=(.3, .35, .35),
        admitted_refs=("design:1", "relationship:henry"),
    )
    claim = SemanticClaim(
        "independent_inquiry", ("challenge", "explore"), .8, ("design:1",),
        prior_strength=4,
    )
    return snap, claim


def episode(forecast, *, event="event-1", tick=13, action="cooperate",
            precision=1.0, kind=EvidenceKind.RUNTIME_POLICY,
            success=None, partner=None):
    return ObservedEpisode(
        event_id=event, forecast_id=forecast.forecast_id, tick=tick,
        situation=forecast.situation, action=action,
        evidence_kind=kind, witness_ref="test-witness:" + event,
        evidence_precision=precision,
        world_success=success, partner_cooperated=partner,
    )


class PredictiveSelfLoopTests(unittest.TestCase):
    def setUp(self):
        self.state, self.claim = fixture()
        self.loop = PredictiveSelfLoop(self.state, claims=(self.claim,))

    def test_forecast_is_normalized_and_sealed_before_outcome(self):
        c = Situation("henry_disagrees", "scientist", "henry")
        f = self.loop.forecast(c)
        self.assertAlmostEqual(sum(f.action_probabilities), 1.0)
        self.assertEqual(f.cutoff_tick, 12)
        self.assertEqual(f.source_snapshot, self.state.digest)
        self.assertEqual(len(f.digest), 64)
        self.assertEqual(f.semantic_probability, (("independent_inquiry", .8),))
        self.assertEqual(f.partner_cooperation_probability, .5)
        self.assertEqual(f.inquiry.kind, "ask_partner")
        self.assertTrue(f.inquiry.requires_authorization)
        self.assertEqual(self.loop.audit()["n_open"], 1)

    def test_local_learning_is_immediate_but_global_identity_is_slow(self):
        c = Situation("single_context", "scientist")
        before = self.loop.forecast(c)
        self.loop.observe(episode(before, action="cooperate"))
        after = self.loop.forecast(c)
        i = self.state.actions.index("cooperate")
        self.assertGreater(after.action_probabilities[i], before.action_probabilities[i])
        self.assertEqual(after.semantic_probability, before.semantic_probability)

    def test_semantic_prior_revision_requires_three_distinct_contexts(self):
        for number in range(2):
            f = self.loop.forecast(Situation("c" + str(number), "scientist"))
            self.loop.observe(episode(f, event="event-" + str(number),
                                      action="cooperate", tick=13 + number,
                                      kind=EvidenceKind.WORLD_VERIFIED))
        self.assertAlmostEqual(self.loop.forecast(
            Situation("new", "scientist")).semantic_probability[0][1], .8)
        f = self.loop.forecast(Situation("third_context", "colleague"))
        change = self.loop.observe(
            episode(f, event="event-third", tick=16, action="cooperate",
                    kind=EvidenceKind.WORLD_VERIFIED)
        )
        first = change.semantic_shift[0]
        self.assertEqual(first[0], "independent_inquiry")
        self.assertAlmostEqual(first[1], .8)
        self.assertLess(first[2], .8)
        self.assertGreaterEqual(first[2], .65)

    def test_low_precision_does_not_revise_global_identity(self):
        for number in range(5):
            f = self.loop.forecast(Situation("c" + str(number), "visitor"))
            self.loop.observe(episode(f, event="event-" + str(number),
                                      tick=13 + number, action="cooperate",
                                      precision=.2,
                                      kind=EvidenceKind.WORLD_VERIFIED))
        self.assertEqual(self.loop.audit()["semantic_posterior"]["independent_inquiry"], .8)

    def test_internal_action_log_never_rewrites_slow_semantic_belief(self):
        for number in range(5):
            f = self.loop.forecast(Situation("runtime-" + str(number), "scientist"))
            self.loop.observe(episode(
                f, event="internal-" + str(number), tick=13 + number,
                action="cooperate", kind=EvidenceKind.RUNTIME_POLICY,
            ))
        self.assertEqual(
            self.loop.audit()["semantic_posterior"]["independent_inquiry"], .8
        )

    def test_portable_checkpoint_replays_exactly_on_same_source(self):
        for number in range(4):
            f = self.loop.forecast(Situation("context-" + str(number), "scientist"))
            self.loop.observe(episode(
                f, event="world-" + str(number), tick=13 + number,
                action="cooperate", kind=EvidenceKind.WORLD_VERIFIED,
            ))
        checkpoint = self.loop.export_checkpoint()
        restored = PredictiveSelfLoop.restore_checkpoint(
            self.state, claims=(self.claim,), checkpoint_json=checkpoint
        )
        self.assertEqual(restored.audit(), self.loop.audit())
        probe = Situation("fresh-future-context", "scientist")
        self.assertEqual(
            restored.forecast(probe).action_probabilities,
            self.loop.forecast(probe).action_probabilities,
        )
        tampered = json.loads(checkpoint)
        tampered["payload"]["episodes"][0]["observation"]["action"] = "challenge"
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            PredictiveSelfLoop.restore_checkpoint(
                self.state, claims=(self.claim,),
                checkpoint_json=json.dumps(tampered),
            )
        bad_snapshot = SelfSnapshot(
            self.state.subject_id, "c" * 64, 2, "b" * 64, 12,
            self.state.actions, self.state.base_probabilities,
            self.state.admitted_refs,
        )
        with self.assertRaisesRegex(ValueError, "source state"):
            PredictiveSelfLoop.restore_checkpoint(
                bad_snapshot, claims=(self.claim,), checkpoint_json=checkpoint
            )

    def test_no_checkpoint_with_pending_forecast(self):
        self.loop.forecast(Situation("still-open", "scientist"))
        with self.assertRaisesRegex(ValueError, "outstanding forecasts"):
            self.loop.export_checkpoint()

    def test_reused_witness_ref_cannot_fake_independent_contexts(self):
        first = self.loop.forecast(Situation("lab-1", "scientist"))
        self.loop.observe(episode(first, event="first", tick=13))
        second = self.loop.forecast(Situation("lab-2", "scientist"))
        forged = ObservedEpisode(
            "second", second.forecast_id, 14, second.situation,
            "cooperate", EvidenceKind.RUNTIME_POLICY, "test-witness:first",
        )
        with self.assertRaisesRegex(ValueError, "duplicated witness reference"):
            self.loop.observe(forged)

    def test_world_feedback_learns_observable_partner_behavior_and_success(self):
        c = Situation("joint_lab", "collaborator", "henry")
        f1 = self.loop.forecast(c)
        self.assertAlmostEqual(f1.partner_cooperation_probability, .5)
        self.assertAlmostEqual(f1.success_probability_by_action[0], .5)
        self.loop.observe(episode(
            f1, kind=EvidenceKind.WORLD_VERIFIED, action="challenge", tick=14,
            success=True, partner=True,
        ))
        f2 = self.loop.forecast(c)
        self.assertGreater(f2.partner_cooperation_probability, .5)
        self.assertGreater(f2.success_probability_by_action[0], .5)
        self.assertIsNone(f2.inquiry if (
            .35 <= f2.partner_cooperation_probability <= .65
        ) else None)  # no unearned tool authority

    def test_prediction_error_scored_from_preexisting_forecast(self):
        c = Situation("unscripted", "visitor")
        f = self.loop.forecast(c)
        record = self.loop.observe(episode(f, action="challenge", tick=13))
        self.assertEqual(record.forecast_id, f.forecast_id)
        self.assertAlmostEqual(record.action_log_loss,
                               -math.log(f.action_probabilities[0]))
        self.assertAlmostEqual(record.multiclass_brier,
                               sum((p-(i == 0))**2
                                   for i,p in enumerate(f.action_probabilities)))
        self.assertIsNone(record.success_brier)
        self.assertEqual(self.loop.audit()["n_scored"], 1)
        self.assertEqual(self.loop.audit()["n_open"], 0)

    def test_invalid_hindsight_source_or_reuse_rejected_without_mutation(self):
        c = Situation("one", "visitor")
        f = self.loop.forecast(c)
        for invalid in (
            episode(f, tick=12),
            episode(f, action="unknown"),
            ObservedEpisode("x", f.forecast_id, 13, Situation("other", "visitor"),
                            "cooperate", EvidenceKind.RUNTIME_POLICY, "witness"),
        ):
            before = self.loop.audit()["audit_sha256"]
            with self.assertRaises(ValueError):
                self.loop.observe(invalid)
            self.assertEqual(before, self.loop.audit()["audit_sha256"])
        accepted = episode(f, event="unique")
        self.loop.observe(accepted)
        with self.assertRaises(ValueError):
            self.loop.observe(accepted)
        new = self.loop.forecast(c)
        with self.assertRaisesRegex(ValueError, "duplicated witnessed event"):
            self.loop.observe(episode(new, event="unique"))

    def test_world_effects_not_accepted_from_internal_policy_records(self):
        c = Situation("lab", "scientist")
        f = self.loop.forecast(c)
        with self.assertRaises(ValueError):
            episode(f, success=True)
        with self.assertRaises(ValueError):
            episode(f, partner=True)
        with self.assertRaises(ValueError):
            episode(f, kind=EvidenceKind.WORLD_VERIFIED, partner=True,
                    action="explore")

    def test_unproven_identity_refs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unadmitted"):
            PredictiveSelfLoop(self.state, claims=(
                SemanticClaim("invented_identity", ("explore",), .9, ("missing:ref",)),
            ))
        with self.assertRaises(ValueError):
            SelfSnapshot("x", "c"*64, 1, "d"*64, 1,
                         ("a", "b"), (.9, .9))
        with self.assertRaises(TypeError):
            SemanticClaim("a", ("explore",), True, ("design:1",))
        with self.assertRaises(ValueError):
            SelfSnapshot("x", "c"*64, 1, "d"*64, 1,
                         ("a", "b"), (.5, .5), ("dup", "dup"))

    def test_repeated_forecast_is_not_duplicate_evidence(self):
        c = Situation("lab", "scientist")
        first = self.loop.forecast(c)
        second = self.loop.forecast(c)
        self.assertNotEqual(first.forecast_id, second.forecast_id)
        self.assertEqual(first.action_probabilities, second.action_probabilities)
        self.assertEqual(self.loop.audit()["n_scored"], 0)

    def test_engineer_only_inquiry_proposals_do_not_execute_actions(self):
        c = Situation("ambiguous", "visitor", "henry")
        f = self.loop.forecast(c)
        self.assertIn(f.inquiry.kind, ("ask_partner", "inspect_evidence"))
        self.assertTrue(f.inquiry.requires_authorization)
        self.assertEqual(self.loop.history, ())
        self.assertEqual(self.loop.audit()["n_scored"], 0)


class PretoriusAdapterTests(unittest.TestCase):
    def test_native_state_read_is_non_mutating_and_observed_action_is_real(self):
        from doctor_lives.cognition import PretoriusBrain
        from doctor_lives.models import Experience
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrain(Path(td))
            original_digest = brain.store.digest()
            prior = snapshot_from_brain(brain)
            self.assertEqual(prior.state_digest, original_digest)
            self.assertEqual(brain.store.digest(), original_digest)
            self.assertEqual(prior.subject_id, "pretorius")
            self.assertGreater(len(prior.actions), 2)
            self.assertAlmostEqual(sum(prior.base_probabilities), 1)
            model = PredictiveSelfLoop(prior)
            forecast = model.forecast(Situation("laboratory", "scientist"))
            brain.ingest(Experience(
                "A new laboratory instrument arrives for inspection.",
                kind="observation", novelty=.75, creation=.5,
            ))
            result = brain.think("predictive_self_shadow_test",
                                 decision_text="Inspect the laboratory instrument.")
            witnessed = witnessed_policy_decision(
                brain, model, forecast, result["policy_decision_id"]
            )
            self.assertEqual(witnessed.action, result["selected_action"])
            self.assertEqual(witnessed.evidence_kind, EvidenceKind.RUNTIME_POLICY)
            self.assertIsNone(witnessed.world_success)
            self.assertEqual(model.observe(witnessed).forecast_id, forecast.forecast_id)
            self.assertEqual(model.audit()["n_scored"], 1)
            self.assertTrue(all(
                episode.evidence_kind == EvidenceKind.RUNTIME_POLICY
                for _, episode, _ in model.history
            ))
            with self.assertRaises(ValueError):
                witnessed_policy_decision(brain, model, forecast, "fake-id")


if __name__ == "__main__":
    unittest.main()
