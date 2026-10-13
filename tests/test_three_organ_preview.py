"""Real Sensus + real Doctor policy + real Synthetic Ipseity, isolated preview.

All assertions use disposable Doctor state and a deterministic renderer callback.
These are software-integration gates, NOT an autonomous model-quality study.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.neural import DEFAULT_CONFIG

HAVE_BOTH = (
    importlib.util.find_spec("synthetic_ipseity") is not None
    and importlib.util.find_spec("sensus_artificialis") is not None
)


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128, "sensory_dim": 64, "avg_recurrent_degree": 8,
        "input_degree": 4, "action_population_size": 8,
    })
    return cfg


@unittest.skipUnless(HAVE_BOTH, "reviewed optional preview donors not installed")
class ThreeOrganPretoriusPreviewTests(unittest.TestCase):
    def setUp(self):
        from doctor_lives.three_organ_preview import ThreeOrganPretoriusPreview
        from sensus_artificialis import Evidence, Percept
        self.Host = ThreeOrganPretoriusPreview
        self.Evidence = Evidence
        self.Percept = Percept
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / "three-organ-preview"
        self.frames = []

    def host(self, renderer=None):
        return self.Host(
            self.state, enabled=True,
            renderer=renderer or (lambda subject: self.frames.append(subject)
                                 or "I shall examine this."),
            neural_config=small_config(),
        )

    def claim(self, *, event, channel, attribute, value, evidence=None,
              object_hint="sample", ref=None, tick=1):
        return self.Percept(
            event_id=event, channel=channel,
            evidence=evidence or self.Evidence.OBSERVED,
            source_ref=ref or ("trusted:" + event),
            tick=tick, attribute=attribute, value=value,
            confidence=0.99, object_hint=object_hint,
        )

    def test_reject_default_opt_out_and_canonical_state_path(self):
        with self.assertRaises(PermissionError):
            self.Host(self.state, enabled=False, renderer=lambda _: "answer")
        forbidden = self.state.parent / "pretorius-production"
        with self.assertRaises(ValueError):
            self.Host(forbidden, enabled=True, renderer=lambda _: "answer")
        self.assertFalse(forbidden.exists())
        self.assertFalse(self.state.exists())

    def test_real_three_way_conflict_selects_recall_from_prior_firstperson_memory(self):
        with self.host() as host:
            prior = host.ingest({
                "channel": "world",
                "text": "The laboratory balance reading was 325 grams.",
                "source": "trusted:prior-meter-reading",
                "novelty": 0.4,
            })
            before = host._doctor.brain.store.memories()
            self.assertTrue(before)
            tick = host._scene_tick
            items = (
                self.claim(event="m1", channel="vision",
                           attribute="laboratory balance reading",
                           value="451 grams", tick=tick),
                self.claim(event="m2", channel="instrument",
                           attribute="laboratory balance reading",
                           value="919 grams", tick=tick),
            )
            outcome = host.cycle(
                items, trusted_source_refs=frozenset({"trusted:m1", "trusted:m2"}),
                now_ms=1000,
            )
            self.assertEqual(outcome["scene_conflicts"], 1)
            self.assertEqual(outcome["admitted_percepts"], 0)
            self.assertEqual(outcome["endogenous_action"], "recall")
            self.assertTrue(outcome["recollection_selected"])
            self.assertEqual(outcome["ipseity_pending"], 0)
            self.assertEqual(len(outcome["new_epistemic_gap_ids"]), 1)
            self.assertEqual(outcome["answer"], "I shall examine this.")
            self.assertEqual(len(self.frames), 1)
            self.assertIn("325", self.frames[0])
            self.assertNotIn("451 grams", self.frames[0])
            self.assertNotIn("919 grams", self.frames[0])
            self.assertNotIn("preview_sensus_conflict", self.frames[0])
            self.assertNotIn("policy_decisions", self.frames[0])
            memory_text = [m["text"] for m in host._doctor.brain.store.memories()]
            self.assertFalse(any("451 grams" in t or "919 grams" in t for t in memory_text))
            with host._doctor.brain.store.connect() as conn:
                row = conn.execute(
                    "SELECT * FROM policy_decisions WHERE id=?",
                    (outcome["endogenous_decision_id"],),
                ).fetchone()
            self.assertEqual(row["selected_action"], "recall")
            self.assertEqual(
                row["policy_version"], "preview-epistemic-deliberation-v0.1"
            )
            self.assertIsNotNone(prior["memory_id"])
        with self.host() as reopened:
            self.assertEqual(reopened.pending_count(), 0)
            self.assertTrue(any(
                m["source"] == "trusted:prior-meter-reading"
                for m in reopened._doctor.brain.store.memories()
            ))

    def test_uncontested_observed_inputs_are_admitted_through_doctor(self):
        with self.host() as host:
            tick = host._scene_tick
            claims = (
                self.claim(event="o1", channel="vision",
                           attribute="laboratory balance", value="steady",
                           tick=tick),
                self.claim(event="o2", channel="hearing",
                           attribute="motor hum", value="gentle",
                           tick=tick),
            )
            outcome = host.cycle(
                claims, trusted_source_refs=frozenset({"trusted:o1", "trusted:o2"}),
                now_ms=1000,
            )
            self.assertEqual(outcome["admitted_percepts"], 2)
            self.assertEqual(outcome["scene_conflicts"], 0)
            self.assertEqual(outcome["endogenous_action"], "continue")
            self.assertEqual(len(self.frames), 1)
            texts = [m["text"] for m in host._doctor.brain.store.memories()]
            self.assertTrue(any("laboratory balance" in t for t in texts))
            self.assertTrue(any("motor hum" in t for t in texts))

    def test_reported_user_message_does_not_upgrade_to_world_fact(self):
        with self.host() as host:
            p = self.claim(
                event="user1", channel="conversation", attribute="message",
                value="The beaker might be missing.", object_hint="speech",
                evidence=self.Evidence.REPORTED, tick=host._scene_tick,
            )
            result = host.cycle(
                (p,), trusted_source_refs=frozenset({"trusted:user1"}),
                now_ms=1000,
            )
            self.assertEqual(result["admitted_percepts"], 1)
            self.assertTrue(any(
                m["source"].startswith("preview-verified-user:trusted:user1:")
                and m["kind"] == "communication"
                and "I read a message from User" in m["text"]
                and "beaker might be missing" in m["text"]
                for m in host._doctor.brain.store.memories()
            ))
            # Doctor's lived-runtime record is of hearing a message; the
            # reported proposition is never promoted to a world observation.
            self.assertFalse(any(
                m["source"].startswith("preview-verified-world:")
                for m in host._doctor.brain.store.memories()
            ))
            self.assertIn("I read a message from User", self.frames[0])

    def test_reported_or_inferred_cannot_inject_a_verified_world_fact(self):
        with self.host() as host:
            tick = host._scene_tick
            observed = self.claim(
                event="o", channel="vision", attribute="object color",
                value="blue", tick=tick,
            )
            inferred = self.claim(
                event="i", channel="thought", attribute="object color",
                value="red", evidence=self.Evidence.INFERRED, tick=tick,
            )
            result = host.cycle(
                (observed, inferred),
                trusted_source_refs=frozenset({"trusted:o", "trusted:i"}),
                now_ms=1000,
            )
            self.assertEqual(result["scene_conflicts"], 1)
            self.assertEqual(result["admitted_percepts"], 0)
            self.assertFalse(result["new_epistemic_gap_ids"])
            texts = [m["text"] for m in host._doctor.brain.store.memories()]
            self.assertFalse(any("object color" in t for t in texts))

    def test_untrusted_claim_prevents_all_mutation_and_model_call(self):
        with self.host() as host:
            before = host._doctor.brain.store.digest()
            p = self.claim(event="fake", channel="vision",
                           attribute="beaker shape", value="round",
                           tick=host._scene_tick)
            with self.assertRaises(PermissionError):
                host.cycle((p,), trusted_source_refs=frozenset({"other:claim"}),
                           now_ms=1000)
            self.assertEqual(before, host._doctor.brain.store.digest())
            self.assertFalse(self.frames)
            self.assertEqual(host.pending_count(), 0)

    def test_pending_outbox_recovery_does_not_reingest_or_rechoose(self):
        turns = []
        def crash_once(subject):
            turns.append(subject)
            if len(turns) == 1:
                raise RuntimeError("synthetic renderer interrupted")
            return "I have resumed."
        with self.host(renderer=crash_once) as host:
            p = self.claim(event="voice", channel="conversation",
                           attribute="message", value="Good evening.",
                           evidence=self.Evidence.REPORTED,
                           object_hint="speech", tick=host._scene_tick)
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                host.cycle((p,), trusted_source_refs=frozenset({"trusted:voice"}),
                           now_ms=100, )
            self.assertEqual(host.pending_count(), 1)
            before = len(host._doctor.brain.store.memories())
        with self.host(renderer=crash_once) as recovered:
            self.assertEqual(recovered.resume_preview(now_ms=30101),
                             "I have resumed.")
            self.assertEqual(recovered.pending_count(), 0)
            self.assertEqual(len(recovered._doctor.brain.store.memories()), before)
            self.assertEqual(len(turns), 2)
            self.assertEqual(turns[0], turns[1])

    def test_research_policy_controls_are_still_synthetic_only_by_default(self):
        with self.host() as host:
            with self.assertRaises(RuntimeError):
                host._doctor.brain.research_endogenous_recall(enabled=True)
            with self.assertRaises(TypeError):
                host._doctor.brain.research_endogenous_recall(
                    enabled=True, preview_live="yes"
                )


    def test_provenance_and_subsequent_policy_change_on_resolution(self):
        """Mechanical causal-state test, not evidence of general cognition."""
        import json
        with self.host() as host:
            tick = host._scene_tick
            dispute = (
                self.claim(event="c1", channel="vision", attribute="balance",
                           value="451 grams", object_hint="balance1", tick=tick),
                self.claim(event="c2", channel="instrument", attribute="balance",
                           value="919 grams", object_hint="balance1", tick=tick),
            )
            first = host.cycle(
                dispute, trusted_source_refs=frozenset({"trusted:c1", "trusted:c2"}),
                now_ms=1000,
            )
            gap = first["new_epistemic_gap_ids"][0]
            with host._doctor.brain.store.connect() as db:
                row = db.execute(
                    "SELECT outcome FROM concern_events "
                    "WHERE concern_id=? AND transition='opened'", (gap,),
                ).fetchone()
            evidence = json.loads(row["outcome"])
            self.assertEqual({c["value"] for c in evidence["claims"]},
                             {"451 grams", "919 grams"})
            self.assertEqual({c["source_ref"] for c in evidence["claims"]},
                             {"trusted:c1", "trusted:c2"})
            before = host._doctor.brain.research_endogenous_recall(
                enabled=True, persist=False, preview_live=True, cooldown_ticks=1,
            )
            tick = host._scene_tick
            correction = (
                self.claim(event="v1", channel="vision", attribute="balance",
                           value="451 grams", object_hint="balance1", tick=tick),
                self.claim(event="v2", channel="instrument", attribute="balance",
                           value="451 grams", object_hint="balance1", tick=tick),
            )
            result = host.cycle(
                correction, trusted_source_refs=frozenset({"trusted:v1", "trusted:v2"}),
                now_ms=2000,
            )
            self.assertEqual(result["resolved_epistemic_gap_ids"], [gap])
            after = host._doctor.brain.research_endogenous_recall(
                enabled=True, persist=False, preview_live=True, cooldown_ticks=1,
            )
            self.assertIn(gap, before["audit"]["candidate_gap_ids"])
            self.assertNotIn(gap, after["audit"]["candidate_gap_ids"])
            # Matched-state intervention: reopen ONLY this concern, with all
            # memories, needs, recurrent weights and renderer held unchanged.
            with host._doctor.brain.store.transaction() as db:
                prior_row = db.execute(
                    "SELECT resolved_tick,resolution FROM concerns WHERE id=?",
                    (gap,),
                ).fetchone()
                db.execute(
                    "UPDATE concerns SET status='open',resolved_tick=NULL,"
                    "resolution=NULL WHERE id=?", (gap,),
                )
                host._doctor.brain.store.bump_state_version(db)
            counterfactual = host._doctor.brain.research_endogenous_recall(
                enabled=True, persist=False, preview_live=True, cooldown_ticks=1,
            )
            with host._doctor.brain.store.transaction() as db:
                db.execute(
                    "UPDATE concerns SET status='resolved',resolved_tick=?,"
                    "resolution=? WHERE id=?",
                    (prior_row["resolved_tick"], prior_row["resolution"], gap),
                )
                host._doctor.brain.store.bump_state_version(db)
            self.assertIn(gap, counterfactual["audit"]["candidate_gap_ids"])
            self.assertNotEqual(counterfactual["scores"], after["scores"])
            self.assertGreater(
                before["audit"]["information_need_family"]["recall_pressure"],
                after["audit"]["information_need_family"]["recall_pressure"],
            )
            with host._doctor.brain.store.connect() as db:
                row = db.execute(
                    "SELECT status,resolution FROM concerns WHERE id=?", (gap,),
                ).fetchone()
            self.assertEqual(row["status"], "resolved")
            resolution = json.loads(row["resolution"])
            with host._doctor.brain.store.connect() as db:
                effects = db.execute(
                    "SELECT outcome FROM concern_events WHERE concern_id=? "
                    "AND transition='policy_effect'", (gap,),
                ).fetchall()
            self.assertEqual(len(effects), 1)
            receipt = json.loads(effects[0]["outcome"])
            self.assertEqual(receipt["decision_id"], result["endogenous_decision_id"])
            self.assertEqual(
                receipt["effect"],
                "resolved_concern_excluded_from_policy_candidates",
            )
            self.assertEqual(len(resolution["resolution"]), 2)
            self.assertEqual(
                resolution["downstream_effect"],
                "remove_gap_from_future_policy_candidates",
            )

    def test_no_production_module_passes_preview_live_true(self):
        import ast
        import doctor_lives
        root = Path(doctor_lives.__file__).parent
        for module in root.glob("*.py"):
            if module.name == "three_organ_preview.py":
                continue
            tree = ast.parse(module.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    for keyword in node.keywords:
                        if keyword.arg == "preview_live" and isinstance(keyword.value, ast.Constant):
                            self.assertIsNot(keyword.value.value, True, str(module))

    def test_pinned_donor_modified_bytes_are_rejected_before_state_open(self):
        from unittest.mock import patch
        import doctor_lives.three_organ_preview as preview
        with patch.object(preview, "_PINNED_SENSUS_CORE_BLOB", "unreviewed"):
            with self.assertRaisesRegex(RuntimeError, "Dirty or substituted"):
                self.Host(self.state, enabled=True, renderer=lambda _: "never")
        self.assertFalse(self.state.exists())


    def test_sensus_object_id_persists_across_processes(self):
        with self.host() as host:
            one = self.claim(
                event="identity-one", channel="vision", attribute="glass colour",
                value="amber", tick=host._scene_tick,
            )
            one = self.Percept(
                event_id=one.event_id, channel=one.channel,
                evidence=one.evidence, source_ref=one.source_ref,
                tick=one.tick, attribute=one.attribute, value=one.value,
                confidence=one.confidence, object_hint="glass",
                features=(("material", "glass"), ("shape", "round")),
            )
            first = host.cycle(
                (one,), trusted_source_refs=frozenset({"trusted:identity-one"}),
                now_ms=1000,
            )
            original_id = first["scene_object_ids"][0]
        with self.host() as reopened:
            second = self.Percept(
                event_id="identity-two", channel="touch",
                evidence=self.Evidence.OBSERVED, source_ref="trusted:identity-two",
                tick=reopened._scene_tick, attribute="glass texture", value="smooth",
                confidence=0.99, object_hint="glass",
                features=(("material", "glass"), ("shape", "round")),
            )
            result = reopened.cycle(
                (second,), trusted_source_refs=frozenset({"trusted:identity-two"}),
                now_ms=2000,
            )
            self.assertEqual(result["scene_object_ids"], [original_id])
        from pathlib import Path
        self.assertTrue((self.state / "preview_scene_journal.sqlite3").exists())

    def test_scene_journal_recovers_without_reingesting_or_reselecting(self):
        """Fault injection is software correctness evidence, not real-model QA."""
        from unittest.mock import patch
        checkpoints = (
            "scene_built", "applied_operation", "journaled_operation",
            "admitted", "decision_persisted", "decided",
            "published_not_journaled", "published",
        )
        for crash_stage in checkpoints:
            with self.subTest(stage=crash_stage):
                with tempfile.TemporaryDirectory() as root:
                    state = Path(root) / "three-organ-preview"
                    def renderer(_text):
                        return "I received it."
                    with self.Host(
                        state, enabled=True, renderer=renderer,
                        neural_config=small_config(),
                    ) as host:
                        p = self.Percept(
                            event_id="message", channel="conversation",
                            evidence=self.Evidence.REPORTED,
                            source_ref="trusted:message", tick=host._scene_tick,
                            attribute="message", value="An ordinary inquiry.",
                            confidence=0.8,
                        )
                        def fail_once(name):
                            if name == crash_stage:
                                raise RuntimeError("injected kill " + name)
                        with patch.object(host, "_checkpoint", side_effect=fail_once):
                            with self.assertRaisesRegex(RuntimeError, "injected kill"):
                                host.cycle(
                                    (p,),
                                    trusted_source_refs=frozenset({"trusted:message"}),
                                    now_ms=1000,
                                )
                        with host._doctor.brain.store.connect() as db:
                            before_events = db.execute(
                                "SELECT COUNT(*) FROM events WHERE source LIKE "
                                "'preview-verified-user:trusted:message:%'"
                            ).fetchone()[0]
                            before_decisions = db.execute(
                                "SELECT COUNT(*) FROM policy_decisions "
                                "WHERE policy_version='preview-epistemic-deliberation-v0.1'"
                            ).fetchone()[0]
                    with self.Host(
                        state, enabled=True, renderer=renderer,
                        neural_config=small_config(),
                    ) as restarted:
                        self.assertEqual(restarted.resume_preview(now_ms=30101),
                                         "I received it.")
                        with restarted._doctor.brain.store.connect() as db:
                            after_events = db.execute(
                                "SELECT COUNT(*) FROM events WHERE source LIKE "
                                "'preview-verified-user:trusted:message:%'"
                            ).fetchone()[0]
                            after_decisions = db.execute(
                                "SELECT COUNT(*) FROM policy_decisions "
                                "WHERE policy_version='preview-epistemic-deliberation-v0.1'"
                            ).fetchone()[0]
                        self.assertEqual(after_events, 1)
                        self.assertEqual(after_decisions, 1)
                        self.assertLessEqual(before_events, after_events)
                        self.assertLessEqual(before_decisions, after_decisions)
                        with self.assertRaises(RuntimeError):
                            restarted.resume_preview(now_ms=60101)

    def test_crash_after_delivery_ack_never_replays_output(self):
        from unittest.mock import patch
        called = []
        with self.host(renderer=lambda _text: called.append(1) or "Delivered.") as host:
            p = self.Percept(
                event_id="last", channel="conversation",
                evidence=self.Evidence.REPORTED,
                source_ref="trusted:last", tick=host._scene_tick,
                attribute="message", value="Last statement.", confidence=0.8,
            )
            with patch.object(
                host, "_checkpoint",
                side_effect=lambda name: (_ for _ in ()).throw(RuntimeError("ack crash"))
                if name == "delivery_acknowledged" else None,
            ):
                with self.assertRaisesRegex(RuntimeError, "ack crash"):
                    host.cycle(
                        (p,), trusted_source_refs=frozenset({"trusted:last"}),
                        now_ms=1000,
                    )
        with self.host(renderer=lambda _text: called.append(1) or "Duplicate.") as recovery:
            with self.assertRaisesRegex(RuntimeError, "acknowledged"):
                recovery.resume_preview(now_ms=40000)
        self.assertEqual(len(called), 1)


    def test_hard_exit_across_scene_boundaries(self):
        """Actual child-process termination, beyond Python exception injection."""
        import subprocess
        import sys
        stages = (
            "scene_built", "applied_operation", "journaled_operation",
            "admitted", "decision_persisted", "decided",
            "published_not_journaled", "published",
            "delivery_acknowledged", "delivered",
        )
        child = """
import os
import sys
from pathlib import Path
from doctor_lives.three_organ_preview import ThreeOrganPretoriusPreview
from sensus_artificialis import Evidence, Percept
from doctor_lives.neural import DEFAULT_CONFIG
state = Path(sys.argv[1])
checkpoint = sys.argv[2]
config = dict(DEFAULT_CONFIG)
config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
              input_degree=4, action_population_size=8)
def renderer(_subject):
    with (state / "renderer_calls.txt").open("a", encoding="utf-8") as file:
        file.write("rendered\\n")
    return "Hard-kill probe complete."
with ThreeOrganPretoriusPreview(
    state, enabled=True, renderer=renderer, neural_config=config,
) as host:
    def hard_exit(name):
        if name == checkpoint:
            os._exit(97)
    host._checkpoint = hard_exit
    percept = Percept(
        event_id="hard-kill", channel="conversation",
        evidence=Evidence.REPORTED, source_ref="trusted:hard-kill",
        tick=host._scene_tick, attribute="message",
        value="Retain this interaction across restart.", confidence=0.8,
    )
    host.cycle(
        (percept,), trusted_source_refs=frozenset({"trusted:hard-kill"}),
        now_ms=1000,
    )
raise RuntimeError("checkpoint was not reached")
"""
        for name in stages:
            with self.subTest(stage=name), tempfile.TemporaryDirectory() as root:
                state = Path(root) / "three-organ-preview"
                result = subprocess.run(
                    [sys.executable, "-c", child, str(state), name],
                    capture_output=True, text=True, timeout=60,
                )
                self.assertEqual(result.returncode, 97, result.stderr)
                with self.Host(
                    state, enabled=True, renderer=lambda _subject: "Hard-kill probe complete.",
                    neural_config=small_config(),
                ) as recovered:
                    if name == "delivery_acknowledged":
                        with self.assertRaisesRegex(RuntimeError, "acknowledged"):
                            recovered.resume_preview(now_ms=30101)
                    elif name == "delivered":
                        with self.assertRaisesRegex(RuntimeError, "No pending"):
                            recovered.resume_preview(now_ms=30101)
                    else:
                        self.assertEqual(
                            recovered.resume_preview(now_ms=30101),
                            "Hard-kill probe complete.",
                        )
                    with recovered._doctor.brain.store.connect() as conn:
                        entries = conn.execute(
                            "SELECT COUNT(*) FROM events WHERE source LIKE "
                            "'preview-verified-user:trusted:hard-kill:%'"
                        ).fetchone()[0]
                        decisions = conn.execute(
                            "SELECT COUNT(*) FROM policy_decisions WHERE "
                            "policy_version='preview-epistemic-deliberation-v0.1'"
                        ).fetchone()[0]
                    self.assertEqual(entries, 1)
                    self.assertEqual(decisions, 1)
                marker = state / "renderer_calls.txt"
                if name in ("delivery_acknowledged", "delivered"):
                    self.assertEqual(marker.read_text().count("rendered"), 1)


    def test_completed_scene_source_cannot_be_replayed_as_new_experience(self):
        from doctor_lives.preview_scene_journal import PreviewSceneConflict
        with self.host() as host:
            p = self.claim(
                event="replayed-id", channel="vision", attribute="cabinet",
                value="closed", tick=host._scene_tick,
            )
            host.cycle(
                (p,), trusted_source_refs=frozenset({"trusted:replayed-id"}),
                now_ms=1000,
            )
            before = len(host._doctor.brain.store.memories())
        with self.host() as restarted:
            repeated = self.claim(
                event="replayed-id", channel="vision", attribute="cabinet",
                value="closed", tick=restarted._scene_tick,
            )
            with self.assertRaisesRegex(PreviewSceneConflict, "cannot be replayed"):
                restarted.cycle(
                    (repeated,),
                    trusted_source_refs=frozenset({"trusted:replayed-id"}),
                    now_ms=2000,
                )
            self.assertEqual(before, len(restarted._doctor.brain.store.memories()))
            self.assertIsNone(restarted._journal.active())

if __name__ == "__main__":
    unittest.main()
