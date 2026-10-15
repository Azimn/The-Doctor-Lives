"""CASCADE contracts and actual four-organ Pretorius preview integration.

Deterministic renderer only. These are software gates, not a longitudinal
quality claim or evidence of autonomy.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.cascade_governance import (
    CycleGrant, bounded_bayesian_evidence, propose_chronos_wake,
)

HAVE_DONORS = (
    importlib.util.find_spec("synthetic_ipseity") is not None
    and importlib.util.find_spec("sensus_artificialis") is not None
)


class PureCASCADEContracts(unittest.TestCase):
    def test_bayes_calculates_and_excludes_impossible_evidence(self):
        self.assertAlmostEqual(bounded_bayesian_evidence(0.5, 0.8, 0.2), 0.8)
        self.assertAlmostEqual(bounded_bayesian_evidence(0.8, 0.5, 0.5), 0.8)
        for values in ((0.5, 0, 0), (1.1, 0.5, 0.5),
                       (float("nan"), 0.5, 0.5)):
            with self.assertRaises(ValueError):
                bounded_bayesian_evidence(*values)

    def test_deterministic_wake_is_not_automatic_action(self):
        p = propose_chronos_wake(current_tick=10, last_wake_tick=6,
                                min_interval=4, permission=True,
                                pending_delivery=False)
        self.assertTrue(p.due)
        self.assertEqual(p.reason, "due_for_host_review")
        self.assertFalse(propose_chronos_wake(
            current_tick=10, last_wake_tick=6, min_interval=4,
            permission=False, pending_delivery=False).due)
        self.assertEqual(propose_chronos_wake(
            current_tick=10, last_wake_tick=6, min_interval=4,
            permission=True, pending_delivery=True).reason, "pending_delivery")
        with self.assertRaises(ValueError):
            propose_chronos_wake(current_tick=9, last_wake_tick=10,
                                min_interval=1, permission=True,
                                pending_delivery=False)

    def test_grant_validates_permission_budget_and_no_subject_override(self):
        digest = "0" * 64
        CycleGrant(digest, 1, frozenset({"observe", "communicate"}), 1)
        with self.assertRaises(ValueError):
            CycleGrant(digest, 1, frozenset({"delete_memory"}), 1)
        with self.assertRaises(ValueError):
            CycleGrant(digest, 1, frozenset({"communicate"}), 0)
        with self.assertRaises(ValueError):
            CycleGrant(digest, 1, frozenset({"communicate"}), 129)


@unittest.skipUnless(HAVE_DONORS, "Reviewed Sensus and Ipseity donor checkouts required")
class ActualCASCADEHost(unittest.TestCase):
    def setUp(self):
        from doctor_lives.cascade_preview import CascadePretoriusPreview
        from sensus_artificialis import Evidence, Percept
        from doctor_lives.neural import DEFAULT_CONFIG
        cfg = dict(DEFAULT_CONFIG)
        cfg.update({
            "neurons": 128, "sensory_dim": 64, "avg_recurrent_degree": 8,
            "input_degree": 4, "action_population_size": 8,
        })
        self.Host, self.Percept, self.Evidence = CascadePretoriusPreview, Percept, Evidence
        self.cfg = cfg
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.state_dir = Path(temp.name) / "three-organ-preview"
        self.frames = []

    def host(self):
        return self.Host(
            self.state_dir, renderer=lambda frame: self.frames.append(frame) or
            "I will consider this carefully.", enabled=True,
            neural_config=self.cfg, require_governor=False,
        )

    def report(self, host, event="sample"):
        return self.Percept(
            event_id=event, channel="conversation", evidence=self.Evidence.REPORTED,
            source_ref="trusted:" + event, tick=host._scene_tick,
            attribute="message", value="What happened to the balance?", confidence=0.95,
        )

    def test_real_sensus_doctor_recall_ipseity_and_causal_receipt(self):
        from doctor_lives.cascade_governance import snapshot_doctor
        with self.host() as host:
            prior = snapshot_doctor(host)
            claim = self.report(host)
            grant = host.make_host_grant(
                permissions=frozenset({"communicate"}), max_percepts=1,
            )
            intact, ablated = host.counterfactual_gate(
                (claim,), trusted_source_refs=frozenset({claim.source_ref}),
                cascade_grant=grant, remove_permission="communicate",
            )
            self.assertTrue(intact.allowed)
            self.assertFalse(ablated.allowed)
            self.assertEqual(ablated.reason, "permission_denied")
            self.assertEqual(snapshot_doctor(host).state_digest, prior.state_digest)
            result = host.cycle(
                (claim,), trusted_source_refs=frozenset({claim.source_ref}),
                now_ms=1000, cascade_grant=grant,
            )
            self.assertEqual(result["answer"], "I will consider this carefully.")
            self.assertEqual(result["cascade_schema"], "pretorius.cascade-conformance.v0.1")
            trace = result["cascade_causal_trace"]
            self.assertTrue(trace["changed"])
            self.assertEqual(trace["before_digest"], prior.state_digest)
            self.assertNotEqual(trace["before_digest"], trace["after_digest"])
            self.assertEqual(trace["policy_decision_id"], result["endogenous_decision_id"])
            self.assertEqual(result["ipseity_pending"], 0)
            self.assertEqual(len(self.frames), 1)
            self.assertNotIn("cascade_arbiter", self.frames[0])
            self.assertNotIn("policy_decisions", self.frames[0])
            self.assertIn("I read a message from User", self.frames[0])
            with self.assertRaises(PermissionError):
                host.cycle(
                    (self.report(host, "after"),),
                    trusted_source_refs=frozenset({"trusted:after"}),
                    now_ms=2000, cascade_grant=grant,
                )
        with self.host() as reopened:
            self.assertEqual(reopened.pending_count(), 0)
            self.assertNotEqual(snapshot_doctor(reopened).state_digest, prior.state_digest)

    def test_permission_budget_and_false_source_fail_without_mutation(self):
        from doctor_lives.cascade_governance import snapshot_doctor
        with self.host() as host:
            before = snapshot_doctor(host).state_digest
            claim = self.report(host)
            empty = host.make_host_grant(
                permissions=frozenset({"observe"}), max_percepts=1,
            )
            with self.assertRaisesRegex(PermissionError, "permission_denied"):
                host.cycle((claim,), trusted_source_refs=frozenset({claim.source_ref}),
                           now_ms=1000, cascade_grant=empty)
            low_chars = host.make_host_grant(
                permissions=frozenset({"communicate"}), max_percepts=1,
                max_claim_chars=5,
            )
            with self.assertRaisesRegex(PermissionError, "resource_exhausted"):
                host.cycle((claim,), trusted_source_refs=frozenset({claim.source_ref}),
                           now_ms=1000, cascade_grant=low_chars)
            grant = host.make_host_grant(
                permissions=frozenset({"communicate"}), max_percepts=1,
            )
            with self.assertRaisesRegex(PermissionError, "untrusted_source"):
                host.cycle((claim,), trusted_source_refs=frozenset({"fake"}),
                           now_ms=1000, cascade_grant=grant)
            self.assertEqual(snapshot_doctor(host).state_digest, before)
            self.assertFalse(self.frames)

    def test_graph_probe_only_returns_existing_ids_and_no_source_upgrade(self):
        with self.host() as host:
            memories = host._doctor.brain.store.memories()
            self.assertTrue(memories)
            origin = memories[0]["id"]
            receipt = host.graph_probe(origin, max_hops=2)
            self.assertEqual(receipt.origin_id, origin)
            self.assertLessEqual(len(receipt.discovered_ids), 63)
            with self.assertRaises(PermissionError):
                host.graph_probe("fabricated-memory-id")
            self.assertEqual(host.chronos_proposal(
                current_tick=10, last_wake_tick=5, min_interval=5,
                host_authorized=False).reason, "permission_denied")

    def test_governor_is_required_in_full_profile(self):
        with self.assertRaises(PermissionError):
            self.Host(self.state_dir, enabled=True,
                      renderer=lambda _: "I am here.",
                      neural_config=self.cfg, require_governor=True)
        self.assertFalse(self.state_dir.exists())
