"""Real Noesis -> Corpus -> Laboratory -> memory -> Noesis experiments.

Requires pinned, non-skipped Pretorius-Laboratory. No simulated tool success,
second planner, autonomous world initiative, or model-issued authorization.
"""
from __future__ import annotations

from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime, CognitiveProposal
from doctor_lives.noesis_corpus_pilot import (
    NoesisCorpusLaboratoryPilot, HostCorpusOffer, VerifiedBodyConsequence,
)

AVAILABLE = importlib.util.find_spec("pretorius_lab") is not None


def config():
    values = dict(DEFAULT_CONFIG)
    values.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    return values


def setup_lab(root: Path):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.subject_port import SubjectPort
    world = SpatialHabitat.create(root / "world.sqlite3")
    HomeLife(world).initialize()
    DailyRhythm(world).initialize()
    runtime = SixOrganRuntime.open(root / "brain", neural_config=config())
    subject = SubjectPort(world)
    return runtime, subject, NoesisCorpusLaboratoryPilot(
        runtime, subject, authorized=True
    )


def scores(runtime, decision_id):
    with runtime._port.brain.store.connect() as db:
        row = db.execute(
            "SELECT * FROM policy_decisions WHERE id=?", (decision_id,)
        ).fetchone()
    return {
        "action_scores": json.loads(row["action_scores_json"]),
        "records": json.loads(row["selected_record_ids_json"]),
        "decision_sha": json.loads(row["state_pressure_json"])[
            "decision_text_sha256"
        ],
        "action": row["selected_action"],
    }


@unittest.skipUnless(AVAILABLE, "The pinned real Laboratory must be installed")
class NoesisCorpusLaboratoryActionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def fresh(self, name="pilot"):
        root = self.root / name
        root.mkdir()
        return setup_lab(root)

    def test_selected_policy_needs_separate_matching_host_authorization(self):
        runtime, subject, bridge = self.fresh()
        proposal = runtime.noesis.deliberate(host_trigger="body-offer")
        offer = HostCorpusOffer(
            tendency=proposal.selected_tendency, op="walk",
            station="station:hall",
        )
        starting = subject.embodied.verify()["station"]
        tick = runtime._port.brain.store.tick
        with self.assertRaises(PermissionError):
            NoesisCorpusLaboratoryPilot(runtime, subject)
        with self.assertRaises(PermissionError):
            bridge.act(proposal, offer)
        wrong_tendency = next(
            a for a in ("explore", "challenge", "approach", "avoid")
            if a != proposal.selected_tendency
        )
        with self.assertRaises(PermissionError):
            bridge.act(
                proposal,
                HostCorpusOffer(
                    tendency=wrong_tendency, op="walk",
                    station="station:hall",
                ),
                authorized=True,
            )
        fake = replace(proposal, policy_decision_id="policy_forged")
        with self.assertRaises(PermissionError):
            bridge.act(fake, offer, authorized=True)
        with self.assertRaises(ValueError):
            HostCorpusOffer(proposal.selected_tendency, "teleport", "station:moon")
        self.assertEqual(subject.embodied.verify()["station"], starting)
        self.assertEqual(runtime._port.brain.store.tick, tick)
        real = bridge.act(proposal, offer, authorized=True)
        self.assertEqual(real.status, "admitted")
        self.assertTrue(real.first_person.startswith(("I ", "My ")))
        self.assertEqual(subject.embodied.verify()["station"], "station:hall")
        self.assertEqual(
            runtime._port.brain.store.get_memory(real.memory_id)["text"],
            real.first_person,
        )

    def test_verified_consequence_changes_real_policy_and_replays_after_restart(self):
        runtime, subject, pilot = self.fresh()
        pre = runtime.noesis.deliberate(host_trigger="body-choice")
        offer = HostCorpusOffer(pre.selected_tendency, "walk", "station:hall")
        consequence = pilot.act(pre, offer, authorized=True)
        self.assertEqual(consequence.status, "admitted")
        self.assertTrue(consequence.first_person.startswith(("I ", "My ")))
        decision = pilot.reflect(consequence, authorized=True)
        self.assertFalse(decision.is_replay)
        self.assertIsNotNone(decision.policy_decision_id)
        details = scores(runtime, decision.policy_decision_id)
        import hashlib
        self.assertEqual(
            details["decision_sha"],
            hashlib.sha256(consequence.first_person.encode()).hexdigest(),
        )
        before_tick = runtime._port.brain.store.tick
        before_policy_count = len(runtime._port.brain.store.thoughts(100000))
        original_world_revision = subject.verify()["revision"]
        runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "pilot" / "brain")
        again = NoesisCorpusLaboratoryPilot(
            reopened, subject, authorized=True
        )
        replay = again.act(pre, offer, authorized=True)
        self.assertEqual(replay.status, "already_admitted")
        self.assertEqual(replay.memory_id, consequence.memory_id)
        reflected = again.reflect(replay, authorized=True)
        self.assertTrue(reflected.is_replay)
        self.assertEqual(reflected.policy_decision_id, decision.policy_decision_id)
        self.assertEqual(reopened._port.brain.store.tick, before_tick)
        self.assertEqual(
            len(reopened._port.brain.store.thoughts(100000)),
            before_policy_count,
        )
        self.assertEqual(subject.verify()["revision"], original_world_revision)

    def test_collision_bodily_feedback_is_not_fabricated(self):
        runtime, subject, pilot = self.fresh()
        first = runtime.noesis.deliberate(host_trigger="body-first")
        hall = pilot.act(
            first, HostCorpusOffer(first.selected_tendency, "walk", "station:hall"),
            authorized=True,
        )
        self.assertEqual(hall.status, "admitted")
        follow = pilot.reflect(hall, authorized=True)
        self.assertTrue(follow.policy_decision_id)
        second = runtime.noesis.deliberate(host_trigger="body-second")
        impact = pilot.act(
            second,
            HostCorpusOffer(
                second.selected_tendency, "walk", "station:shop:private"
            ),
            authorized=True,
        )
        self.assertIn("foot", impact.first_person.lower())
        self.assertEqual(impact.spoken_aloud, "Ow! My foot!")
        self.assertEqual(
            runtime._port.brain.store.get_memory(impact.memory_id)["text"],
            impact.first_person,
        )
        next_decision = pilot.reflect(impact, authorized=True)
        self.assertFalse(next_decision.is_replay)
        private = runtime.synthetic_ipseity.project_subject_frame()
        from doctor_lives.models import SubjectRendererCapability
        lines = SubjectRendererCapability.read(private)
        self.assertTrue(lines)
        self.assertFalse(any(
            "world_epoch" in x or "action_scores" in x or
            "neural_checkpoint" in x for x in lines
        ))
        # A physical consequence becomes a real memory, not a host claim
        self.assertEqual(
            runtime._port.brain.store.get_memory(impact.memory_id)[
                "evidence_class"
            ], "lived_runtime_memory",
        )

    def test_stale_proposal_rejected_before_movement_and_forged_feedback(self):
        runtime, subject, pilot = self.fresh()
        prior = runtime.noesis.deliberate(host_trigger="body-old")
        runtime.noesis.deliberate(host_trigger="body-new")
        with self.assertRaises(PermissionError):
            pilot.act(
                prior, HostCorpusOffer(
                    prior.selected_tendency, "walk", "station:hall"
                ), authorized=True,
            )
        newest = runtime.noesis.deliberate(host_trigger="body-live")
        good = pilot.act(
            newest,
            HostCorpusOffer(newest.selected_tendency, "walk", "station:hall"),
            authorized=True,
        )
        with self.assertRaises(PermissionError):
            pilot.reflect(good)
        with self.assertRaises(PermissionError):
            pilot.reflect(replace(good, memory_id="memory_unknown"), authorized=True)
        with self.assertRaises(PermissionError):
            pilot.reflect(replace(good, event_id="nc_fake"), authorized=True)
        with self.assertRaises(RuntimeError):
            pilot.act(
                newest,
                HostCorpusOffer(newest.selected_tendency,
                                "walk", "station:shop:private"),
                authorized=True,
            )

    def test_matched_collision_memory_lesion_reports_risk_direction_without_faking_success(self):
        """Same physical consequences; memory-access intervention only.

        Report the change in the next native 'avoid' preference. A higher
        score is a useful *candidate* risk signal, not proof the Doctor
        actually chooses a better subsequent route or wins a task.
        """
        treated, ta, api = self.fresh("collision-treated")
        control, ca, control_api = self.fresh("collision-control")
        outcomes = []
        for runtime, pilot in ((treated, api), (control, control_api)):
            to_hall = runtime.noesis.deliberate(host_trigger="risk-hall")
            hall = pilot.act(
                to_hall,
                HostCorpusOffer(to_hall.selected_tendency, "walk", "station:hall"),
                authorized=True,
            )
            self.assertEqual(hall.status, "admitted")
            at_stool = runtime.noesis.deliberate(host_trigger="risk-stool")
            bump = pilot.act(
                at_stool,
                HostCorpusOffer(
                    at_stool.selected_tendency, "walk", "station:shop:private"
                ),
                authorized=True,
            )
            self.assertEqual(bump.spoken_aloud, "Ow! My foot!")
            outcomes.append(bump)
        self.assertEqual(outcomes[0].first_person, outcomes[1].first_person)
        self.assertEqual(ta.embodied.verify()["station"], ca.embodied.verify()["station"])
        self.assertEqual(ta.home.audit_state()["body"], ca.home.audit_state()["body"])
        # A selective archival lesion removes ONLY access to the bodily
        # consequence, without rewinding the physical world or neural weights.
        brain = control._port.brain
        with brain.store.transaction() as db:
            brain.store.archive_memory(
                db, outcomes[1].memory_id, brain.store.tick,
                "controlled no-recall comparator",
            )
            brain.store.bump_state_version(db)
        with self.assertRaises(PermissionError):
            control_api.reflect(outcomes[1], authorized=True)
        treatment = api.reflect(outcomes[0], authorized=True)
        without = control._port.brain.think(
            "nc_feedback_control", decision_text=None
        )
        a = scores(treated, treatment.policy_decision_id)
        b = scores(control, without["policy_decision_id"])
        self.assertNotEqual(a["decision_sha"], b["decision_sha"])
        self.assertTrue(
            a["action_scores"] != b["action_scores"]
            or a["records"] != b["records"],
            "Bodily consequence failed to influence downstream policy",
        )
        risk_comparison = {
            "schema": "pretorius.noesis-corpus-risk-probe.v1",
            "same_physical_body_state": True,
            "real_collision_reproduced_in_both_arms": True,
            "treatment_avoid_score": a["action_scores"]["avoid"],
            "lesion_avoid_score": b["action_scores"]["avoid"],
            "avoid_score_delta": (
                a["action_scores"]["avoid"] - b["action_scores"]["avoid"]
            ),
            "selected_tendency_with_memory": a["action"],
            "selected_tendency_memory_archived": b["action"],
            "objective_task_success_proven": False,
            "simple_receipt_ledger_superiority_proven": False,
        }
        print("NOESIS_CORPUS_RISK_ABLATION=" + json.dumps(
            risk_comparison, sort_keys=True
        ))

    def test_paired_action_feedback_versus_no_feedback_measures_future_policy(self):
        treated, subject, pilot = self.fresh("treated")
        control, _, _ = self.fresh("control")
        p = treated.noesis.deliberate(host_trigger="paired-choice")
        c = control.noesis.deliberate(host_trigger="paired-choice")
        self.assertEqual(p.selected_tendency, c.selected_tendency)
        self.assertEqual(
            scores(treated, p.policy_decision_id)["action_scores"],
            scores(control, c.policy_decision_id)["action_scores"],
        )
        outcome = pilot.act(
            p, HostCorpusOffer(p.selected_tendency, "walk", "station:hall"),
            authorized=True,
        )
        with_feedback = pilot.reflect(outcome, authorized=True)
        without_feedback = control.noesis.deliberate(
            host_trigger="nc-feedback-control"
        )
        a = scores(treated, with_feedback.policy_decision_id)
        b = scores(control, without_feedback.policy_decision_id)
        # The two arms do not yet have identical post-action world states.
        # So this is a mechanism sensitivity test, NOT a fair demonstration
        # of task improvement or superiority over a receipt-ledger controller.
        self.assertNotEqual(a["decision_sha"], b["decision_sha"])
        changed = a["action_scores"] != b["action_scores"] or (
            [treated._port.brain.store.get_memory(r)["text"]
             for r in a["records"] if treated._port.brain.store.get_memory(r)]
            != [control._port.brain.store.get_memory(r)["text"]
                for r in b["records"] if control._port.brain.store.get_memory(r)]
        )
        self.assertTrue(
            changed,
            "Verified physical consequence had no measured effect on canonical policy",
        )
        self.assertIn(
            outcome.first_person,
            [m["text"] for m in treated._port.brain.store.memories(False)],
        )
        self.assertNotIn(
            outcome.first_person,
            [m["text"] for m in control._port.brain.store.memories(False)],
        )


if __name__ == "__main__":
    unittest.main()
