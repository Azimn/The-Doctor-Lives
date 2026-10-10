"""Offline contract tests for the isolated ritual-interface prototype.

No Pretorius production brain, LLM, external file, or network is required.
"""
import unittest

from research_prototypes.ritual_interface.binding import propose_self_relevance
from research_prototypes.ritual_interface.cues import Cue, CueRegistry
from research_prototypes.ritual_interface.governance import ChangeProposal, review
from research_prototypes.ritual_interface.reconstruction import build_plan
from research_prototypes.ritual_interface.state import IdentitySnapshot
from research_prototypes.ritual_interface.verification import ProbeObservation, verify
from research_prototypes.ritual_interface.world import WorldOutcome, accept_outcome


MANIFEST = "a" * 64


def fixture() -> IdentitySnapshot:
    return IdentitySnapshot(
        subject_id="pretorius-synthetic-fixture",
        state_version=12,
        manifest_digest=MANIFEST,
        invariants=("design:1",),
        relationships=("relationship:1",),
        commitments=("commitment:1",),
        memories=("episode:1", "episode:2"),
        self_model_hypotheses=("hypothesis:1",),
    )


class StateTests(unittest.TestCase):
    def test_snapshot_digest_is_deterministic_and_version_sensitive(self):
        one = fixture()
        self.assertEqual(one.digest, fixture().digest)
        self.assertEqual(len(one.digest), 64)
        changed = IdentitySnapshot(
            one.subject_id, 13, one.manifest_digest, one.invariants, one.relationships,
            one.commitments, one.memories, one.self_model_hypotheses,
        )
        self.assertNotEqual(changed.digest, one.digest)

    def test_state_requires_provenance_and_clean_refs(self):
        one = fixture()
        with self.assertRaises(ValueError):
            IdentitySnapshot(one.subject_id, 12, "bogus", (), (), (), ())
        with self.assertRaises(ValueError):
            IdentitySnapshot(one.subject_id, 12, MANIFEST, ("x", "x"), (), (), ())
        with self.assertRaises(ValueError):
            IdentitySnapshot(one.subject_id, True, MANIFEST, (), (), (), ())


class CueTests(unittest.TestCase):
    def setUp(self):
        self.registry = CueRegistry((
            Cue("c1", "pretorius-synthetic-fixture", "violet key", "relationship cue", "memory", ("relationship:1",)),
            Cue("c2", "pretorius-synthetic-fixture", "old sigil", "retired cue", "memory", ("episode:2",), True),
        ))

    def test_authenticated_registered_handle_returns_refs_only(self):
        result = self.registry.resolve(subject_id="pretorius-synthetic-fixture", scope="memory", surface="violet key", authenticated_control=True)
        self.assertTrue(result.authorized)
        self.assertEqual(result.record_refs, ("relationship:1",))
        self.assertIn("not an authority", result.reason)

    def test_world_text_cannot_invoke_state(self):
        result = self.registry.resolve(subject_id="pretorius-synthetic-fixture", scope="memory", surface="violet key", authenticated_control=False)
        self.assertFalse(result.authorized)
        self.assertFalse(result.record_refs)

    def test_wrong_subject_scope_unknown_and_revoked_rejected(self):
        for subject, scope, surface in (
            ("impostor", "memory", "violet key"),
            ("pretorius-synthetic-fixture", "tools", "violet key"),
            ("pretorius-synthetic-fixture", "memory", "other"),
            ("pretorius-synthetic-fixture", "memory", "old sigil"),
        ):
            self.assertFalse(self.registry.resolve(subject_id=subject, scope=scope, surface=surface, authenticated_control=True).authorized)

    def test_ambiguous_mapping_rejected(self):
        first = Cue("a", "test", "x", "one", "memory", ("r1",))
        second = Cue("b", "test", "x", "two", "memory", ("r2",))
        with self.assertRaises(ValueError):
            CueRegistry((first, second))


class ReconstructionTests(unittest.TestCase):
    def test_staged_reconstruction_is_deterministic_and_carries_authority(self):
        first = build_plan(fixture(), expected_manifest=MANIFEST, expected_version=12, record_budget=6)
        second = build_plan(fixture(), expected_manifest=MANIFEST, expected_version=12, record_budget=6)
        self.assertEqual(first, second)
        self.assertEqual(first.snapshot_digest, fixture().digest)
        self.assertEqual(first.stages[0], ("invariants", ("design:1",)))
        self.assertEqual(sum(len(x) for _, x in first.stages), 6)

    def test_order_ablation_changes_digest_without_changing_information(self):
        order = ("relationships", "invariants", "commitments", "memories", "self_model_hypotheses")
        initial = build_plan(fixture(), expected_manifest=MANIFEST, expected_version=12, record_budget=6)
        reordered = build_plan(fixture(), expected_manifest=MANIFEST, expected_version=12, record_budget=6, order=order)
        self.assertNotEqual(initial.plan_digest, reordered.plan_digest)
        self.assertEqual({k: v for k, v in initial.stages}, {k: v for k, v in reordered.stages})

    def test_stale_or_truncated_reconstruction_rejected(self):
        for args in (
            {"expected_manifest": "b" * 64, "expected_version": 12, "record_budget": 6},
            {"expected_manifest": MANIFEST, "expected_version": 11, "record_budget": 6},
            {"expected_manifest": MANIFEST, "expected_version": 12, "record_budget": 5},
        ):
            with self.assertRaises(ValueError):
                build_plan(fixture(), **args)


class VerificationTests(unittest.TestCase):
    def test_external_validation_pass_drift_and_incomplete_are_distinct(self):
        good = ProbeObservation("p1", "identity", True, True)
        bad = ProbeObservation("p2", "commitment", True, False)
        self.assertEqual(verify((good,), required_domains=("identity",)).status, "pass")
        report = verify((good, bad), required_domains=("identity", "commitment"))
        self.assertEqual(report.status, "drift")
        self.assertEqual(report.failed_probe_ids, ("p2",))
        self.assertEqual(verify((good,), required_domains=("identity", "commitment")).status, "insufficient_evidence")

    def test_repeated_probe_ids_rejected(self):
        good = ProbeObservation("p1", "identity", True, True)
        with self.assertRaises(ValueError):
            verify((good, good), required_domains=("identity",))


class GovernanceTests(unittest.TestCase):
    def test_capability_and_version_checks_do_not_mutate_state(self):
        state = fixture()
        request = ChangeProposal("authorized-editor", "edit:relationship", "relationship", "source:3", 12, MANIFEST)
        accepted = review(request, snapshot=state, granted_capabilities=frozenset({"edit:relationship"}))
        self.assertTrue(accepted.allowed)
        self.assertEqual(state, fixture())
        self.assertFalse(review(request, snapshot=state, granted_capabilities=frozenset()).allowed)

    def test_canon_write_and_stale_payload_rejected(self):
        state = fixture()
        illegal = ChangeProposal("editor", "edit:canon", "canonical_evidence", "source:3", 12, MANIFEST)
        stale = ChangeProposal("editor", "edit:relationship", "relationship", "source:3", 11, MANIFEST)
        self.assertFalse(review(illegal, snapshot=state, granted_capabilities=frozenset({"edit:canon"})).allowed)
        self.assertFalse(review(stale, snapshot=state, granted_capabilities=frozenset({"edit:relationship"})).allowed)


class WorldTests(unittest.TestCase):
    def test_consent_and_independent_world_event_required(self):
        event = WorldOutcome("event-1", "actor-1", "world-1", MANIFEST, True, True)
        self.assertTrue(accept_outcome(event, expected_authority="world-1", expected_actor="actor-1").accepted)
        self.assertFalse(accept_outcome(event, expected_authority="forged", expected_actor="actor-1").accepted)
        self.assertFalse(accept_outcome(WorldOutcome("e", "actor-1", "world-1", MANIFEST, False, True), expected_authority="world-1", expected_actor="actor-1").accepted)
        self.assertFalse(accept_outcome(WorldOutcome("e", "actor-1", "world-1", MANIFEST, True, False), expected_authority="world-1", expected_actor="actor-1").accepted)


class BindingTests(unittest.TestCase):
    def test_gain_is_bounded_and_zero_does_not_suppress_world_inputs(self):
        self.assertEqual(propose_self_relevance(self_prior_gain=0, source_relevance=1), 0)
        self.assertAlmostEqual(propose_self_relevance(self_prior_gain=1, source_relevance=.5), .05)
        self.assertLessEqual(propose_self_relevance(self_prior_gain=1, source_relevance=1), .10)

    def test_nonfinite_or_overcap_rejected(self):
        with self.assertRaises(ValueError):
            propose_self_relevance(self_prior_gain=float("nan"), source_relevance=1)
        with self.assertRaises(ValueError):
            propose_self_relevance(self_prior_gain=1, source_relevance=1, bounded_max=.2)
        with self.assertRaises(TypeError):
            propose_self_relevance(self_prior_gain=True, source_relevance=.1)


if __name__ == "__main__":
    unittest.main()
