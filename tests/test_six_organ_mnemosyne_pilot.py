"""Matched opt-in PR #59 endogenous recall tests on one Doctor BrainStore."""
from __future__ import annotations

import json
from contextlib import closing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.mnemosyne_pilot import MnemosyneEndogenousPilot
from doctor_lives.models import SubjectFrame, SubjectRendererCapability
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime


def small_config():
    c = dict(DEFAULT_CONFIG)
    c.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
             input_degree=4, action_population_size=8, seed=1842)
    return c


def seed_epistemic_gap(runtime, *, source="preview_sensus_conflict",
                       actor="PREVIEW_HOST", identifier="trusted-gap-1",
                       description="the glass vessel", uncertainty=0.99,
                       importance=0.99):
    """Explicitly labeled host-verified research fixture, not user speech."""
    brain = runtime._port.brain
    with brain.store.transaction() as db:
        db.execute(
            """INSERT INTO concerns
            (id,created_tick,updated_tick,description,status,importance,
             uncertainty,actor,source) VALUES(?,?,?,?,'open',?,?,?,?)""",
            (identifier, brain.store.tick, brain.store.tick, description,
             importance, uncertainty, actor, source),
        )
        brain.store.bump_state_version(db)


class EndogenousRecallOrganTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def runtime(self, name):
        return SixOrganRuntime.open(self.root / name, neural_config=small_config())

    def test_qualified_internal_gap_causes_selected_recall_and_read_only_frame(self):
        runtime = self.runtime("one")
        runtime.sensus.acquire_existing_percept(
            {"channel": "world", "source": "fixture-vessel",
             "percept": "I heard a glass vessel shatter behind me."},
            host_authorized=True,
        )
        seed_epistemic_gap(runtime)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        decision = pilot.deliberate(recall_cost=0.0)
        self.assertEqual(decision.action, "recall")
        self.assertEqual(decision.selected_gap_id, "trusted-gap-1")
        self.assertGreater(decision.recall_pressure, 0.9)
        self.assertEqual(decision.initiated_by, "host_scheduled_internal_policy")
        with closing(runtime._port.brain.store.connect()) as db:
            rec = db.execute(
                "SELECT * FROM policy_decisions WHERE id=?", (decision.decision_id,)
            ).fetchone()
        self.assertEqual(rec["selected_action"], "recall")
        self.assertEqual(rec["policy_version"],
                         "preview-epistemic-deliberation-v0.1")
        audit = json.loads(rec["state_pressure_json"])
        self.assertFalse(audit["autonomous_model_authorship_proven"])
        self.assertFalse(audit["memory_retrieval_performed"])
        self.assertTrue(audit["question_sha256"])
        before = runtime._port.brain.store.digest()
        frame = pilot.recollect()
        self.assertIsInstance(frame, SubjectFrame)
        lines = SubjectRendererCapability.read(frame)
        self.assertTrue(lines)
        self.assertEqual(before, runtime._port.brain.store.digest())
        self.assertNotIn("neural_checkpoint_sha256", "\n".join(lines))
        with self.assertRaises(PermissionError):
            pilot.recollect()

    def test_advanced_selected_recall_reconsolidates_without_changing_source(self):
        from doctor_lives.mnemosyne_reconstruction import PREFIX, RECALL_PREFIX
        from doctor_lives.reconsolidation import TraceVersionLedger
        runtime = self.runtime("advanced")
        runtime.sensus.acquire_existing_percept(
            {"channel":"world","source":"fixture-vessel",
             "percept":"I heard a glass vessel shatter behind me."},
            host_authorized=True,
        )
        seed_epistemic_gap(runtime)
        pilot=runtime.mnemosyne.opt_in_endogenous_recollection()
        decision=pilot.deliberate(recall_cost=0)
        self.assertEqual(decision.action,"recall")
        question = pilot._pending_question
        effect=pilot.reflect_selected_recollection(reconstruct=True)
        self.assertTrue(effect.next_policy_decision_id)
        store=runtime._port.brain.store
        record=json.loads(store.meta(RECALL_PREFIX+decision.decision_id))
        self.assertFalse(record["world_fact_created"])
        self.assertTrue(record["subject_text"].startswith("I "))
        self.assertTrue(record["successor"])
        self.assertTrue(TraceVersionLedger.from_json(store.meta(PREFIX+record["source_memory"])))
        self.assertTrue(any(x["id"]==record["source_memory"] and "glass vessel shatter" in x["text"]
                            for x in store.memories()))
        runtime.checkpoint()
        self.assertEqual(SixOrganRuntime.open(self.root/"advanced")._port.brain.store.meta(
            RECALL_PREFIX+decision.decision_id),store.meta(RECALL_PREFIX+decision.decision_id))
        # A cache hit is not a new retrieval grant. Even a valid historical
        # policy must not release content from an inactive source.
        from doctor_lives.mnemosyne_reconstruction import reconstruct_selected
        brain = runtime._port.brain
        line = next(x.first_person for x in brain.cognitive_view(query=question, audit=False).experiences
                    if x.record_id == record["source_memory"])
        self.assertEqual(reconstruct_selected(brain, question, decision.decision_id, line),
                         record["subject_text"])
        with store.transaction() as db:
            db.execute("UPDATE memories SET active=0 WHERE id=?", (record["source_memory"],))
            store.bump_state_version(db)
        before = store.digest()
        with self.assertRaises(PermissionError):
            reconstruct_selected(brain, question, decision.decision_id, line)
        self.assertEqual(store.digest(), before)
        self.assertEqual(json.loads(store.meta(RECALL_PREFIX+decision.decision_id)), record)

    def test_explicit_dream_recollection_preserves_attribution_and_source(self):
        from doctor_lives.lab_phantasmagorium import SOURCE, _stable
        from doctor_lives.phantasmagorium_bridge import DONOR_SHA256
        from doctor_lives.tower_ipseity import TowerIpseity, RECORD
        from doctor_lives.phenomenology import PhenomenalMode, SubjectiveSourceKind

        runtime = self.runtime("dream-ownership")
        brain = runtime._port.brain
        store = brain.store
        subject = TowerIpseity(brain)
        digest = "b" * 64
        source_name = "laboratory-home:action:" + digest
        text = "I recall a dream: a violet pendulum floated above an obsidian clock."
        # Controlled source/admission fixture, not a donor or physical-world test.
        with store.transaction() as db:
            source = store.add_memory(db, store.tick, "I slept.", source_name, "action",
                "lived_runtime_memory", False, 1.0, False, .4,
                classification=brain._runtime_classification("action", source_name))
            mid = store.add_memory(db, store.tick, text, SOURCE + digest,
                "dream_recollection", "dreamed_not_lived", True, 1.0, False, 1.0)
        event = subject.event("Phantasmagorium", text, PhenomenalMode.RECOLLECTION,
            (source, mid), attribution=SubjectiveSourceKind.DREAMED, external=True)
        with store.transaction() as db:
            entry = subject.record(db, "imagination:" + digest, (event,), phase="imagination")
            report = {"source_sha256": digest, "operation": "night",
                "donor_sha256": DONOR_SHA256, "source_memory_id": source,
                "recollection_memory_id": mid, "world_authority": False,
                "factual_memory_eligible": False, "motor_authority": False,
                "ipseity_admission_sha256": entry["sha256"]}
            store.set_meta("phantasmagorium:event:" + digest, _stable(report), db)
        seed_epistemic_gap(runtime, description="the violet pendulum")
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        decision = pilot.deliberate(recall_cost=0)
        self.assertEqual(decision.action, "recall")
        original = brain.think
        observed = []
        def check(*args, **kwargs):
            entry = subject.verify_history()[-1]
            self.assertEqual(entry["key"], RECORD + "recollection:" + decision.decision_id)
            self.assertEqual(entry["content"][0]["attribution"], "dreamed")
            self.assertTrue(entry["content"][0]["external"])
            self.assertEqual(entry["content"][0]["source_refs"], [decision.decision_id, mid])
            self.assertEqual(entry["content"][0]["text"], text)
            observed.append(entry)
            return original(*args, **kwargs)
        with patch.object(brain, "think", side_effect=check):
            effect = pilot.reflect_selected_recollection(reconstruct=True)
        self.assertTrue(effect.next_policy_decision_id)
        self.assertEqual(len(observed), 1)
        self.assertEqual(store.get_memory(mid)["evidence_class"], "dreamed_not_lived")

    def test_unbound_recollection_admitted_before_policy_and_persists(self):
        from doctor_lives.tower_ipseity import TowerIpseity, RECORD
        for reconstruct in (False, True):
            with self.subTest(reconstruct=reconstruct):
                name = "owned-recall-" + str(reconstruct)
                runtime = self.runtime(name)
                brain = runtime._port.brain
                self.assertIsNone(brain.store.meta("small-tower:world-binding-v1"))
                runtime.sensus.acquire_existing_percept(
                    {"channel": "world", "source": "fixture-vessel",
                     "percept": "I heard a glass vessel shatter behind me."},
                    host_authorized=True,
                )
                seed_epistemic_gap(runtime)
                pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
                decision = pilot.deliberate(recall_cost=0)
                self.assertEqual(decision.action, "recall")
                key = RECORD + "recollection:" + decision.decision_id
                original = brain.think
                observed = []
                def observe(*args, **kwargs):
                    # verify_history uses a separate database connection.
                    latest = TowerIpseity(brain).verify_history()[-1]
                    self.assertEqual(latest["key"], key)
                    self.assertEqual(latest["content"][0]["text"], kwargs["decision_text"])
                    self.assertEqual(latest["content"][0]["source_refs"], [decision.decision_id])
                    self.assertEqual(latest["content"][0]["mode"], "recollection")
                    observed.append(latest)
                    return original(*args, **kwargs)
                with patch.object(brain, "think", side_effect=observe):
                    effect = pilot.reflect_selected_recollection(reconstruct=reconstruct)
                self.assertEqual(len(observed), 1)
                self.assertTrue(effect.next_policy_decision_id)
                history = TowerIpseity(brain).verify_history()
                self.assertEqual(sum(x["key"] == key for x in history), 1)
                self.assertEqual(history[-1]["phase"], "private_thought")
                self.assertEqual(history[-1]["content"][0]["organ"], "Noesis")
                self.assertIn(effect.next_policy_decision_id, history[-1]["content"][0]["source_refs"])
                before = brain.store.digest()
                with self.assertRaises(PermissionError):
                    brain.think("mnemosyne_private_reflection",
                                decision_text=observed[0]["content"][0]["text"])
                self.assertEqual(brain.store.digest(), before)
                runtime.checkpoint()
                reopened = SixOrganRuntime.open(self.root / name)
                self.assertEqual(TowerIpseity(reopened._port.brain).verify_history(), history)

    def test_unadmitted_recollection_rejected_before_policy(self):
        runtime = self.runtime("unadmitted")
        brain = runtime._port.brain
        before = (brain.store.digest(), brain.neural.tick)
        with patch.object(brain, "_ranked_memory_sets") as ranking:
            with self.assertRaises(PermissionError):
                brain.think("mnemosyne_private_reflection",
                            decision_text="I remember a glass vessel.")
            ranking.assert_not_called()
        self.assertEqual((brain.store.digest(), brain.neural.tick), before)

    def test_recollection_admission_failure_does_not_call_noesis(self):
        from doctor_lives.tower_ipseity import TowerIpseity
        runtime = self.runtime("denied-admission")
        brain = runtime._port.brain
        runtime.sensus.acquire_existing_percept(
            {"channel": "world", "source": "fixture-vessel",
             "percept": "I heard a glass vessel shatter behind me."},
            host_authorized=True,
        )
        seed_epistemic_gap(runtime)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        self.assertEqual(pilot.deliberate(recall_cost=0).action, "recall")
        before = (brain.store.digest(), brain.neural.tick)
        with patch.object(TowerIpseity, "admit_private", side_effect=PermissionError("denied")):
            with patch.object(brain, "think") as think:
                with self.assertRaises(PermissionError):
                    pilot.reflect_selected_recollection()
                think.assert_not_called()
        self.assertEqual((brain.store.digest(), brain.neural.tick), before)
        with self.assertRaises(PermissionError):
            pilot.reflect_selected_recollection()

    def test_matched_no_gap_ablation_blocks_recollection_without_new_brain(self):
        control = self.runtime("control")
        with_gap = self.runtime("treatment")
        seed_epistemic_gap(with_gap)
        a = control.mnemosyne.opt_in_endogenous_recollection()
        b = with_gap.mnemosyne.opt_in_endogenous_recollection()
        none = a.deliberate(recall_cost=0.0)
        present = b.deliberate(recall_cost=0.0)
        self.assertNotEqual(none.action, "recall")
        self.assertIsNone(none.selected_gap_id)
        self.assertEqual(present.action, "recall")
        with self.assertRaises(PermissionError):
            a.recollect()
        self.assertIs(a._port, control._port)
        self.assertIs(b._port, with_gap._port)

    def test_forged_or_reported_gap_is_not_an_internally_selected_cue(self):
        runtime = self.runtime("forged")
        seed_epistemic_gap(runtime, source="external_user_message",
                           actor="User", identifier="external-claim")
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        decision = pilot.deliberate(recall_cost=0)
        self.assertNotEqual(decision.action, "recall")
        with self.assertRaises(PermissionError):
            pilot.recollect()

    def test_low_information_pressure_and_high_cost_decline_recollection(self):
        runtime = self.runtime("low-pressure")
        seed_epistemic_gap(runtime, uncertainty=0.01, importance=0.01)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        decision = pilot.deliberate(recall_cost=1)
        self.assertNotEqual(decision.action, "recall")
        self.assertLess(decision.recall_pressure, 0.01)

    def test_restart_preserves_cooldown_and_prevents_pending_grant_replay(self):
        runtime = self.runtime("restart")
        seed_epistemic_gap(runtime)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        first = pilot.deliberate(recall_cost=0.0)
        self.assertEqual(first.action, "recall")
        runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "restart")
        new_pilot = reopened.mnemosyne.opt_in_endogenous_recollection()
        with self.assertRaises(PermissionError):
            new_pilot.recollect()
        cooled = new_pilot.deliberate(recall_cost=0.0)
        self.assertNotEqual(cooled.action, "recall")
        with closing(reopened._port.brain.store.connect()) as db:
            matches = db.execute(
                "SELECT count(*) FROM policy_decisions WHERE trigger=?",
                ("preview_endogenous_recall_v01",),
            ).fetchone()[0]
        self.assertEqual(matches, 2)
        self.assertFalse((self.root / "restart" / "mnemosyne.sqlite3").exists())

    def test_invalid_inputs_and_reentrant_decision_fail_closed(self):
        runtime = self.runtime("guards")
        with self.assertRaises(PermissionError):
            MnemosyneEndogenousPilot(runtime._port)
        seed_epistemic_gap(runtime)
        pilot = runtime.mnemosyne.opt_in_endogenous_recollection()
        for cost in (-0.1, 2.0, float("nan"), True):
            with self.subTest(cost=cost), self.assertRaises(ValueError):
                pilot.deliberate(recall_cost=cost)
        selected = pilot.deliberate(recall_cost=0.0)
        self.assertEqual(selected.action, "recall")
        with self.assertRaises(RuntimeError):
            pilot.deliberate()
        pilot.recollect()


if __name__ == "__main__":
    unittest.main()
