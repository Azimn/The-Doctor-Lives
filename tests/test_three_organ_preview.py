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
                m["source"] == "preview-verified-user:trusted:user1"
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


if __name__ == "__main__":
    unittest.main()
