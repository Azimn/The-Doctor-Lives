"""Real-world, no-manual Noesis choice changes after its own consequences.

This suite uses the original brain, one pinned actual Laboratory and original
source-verified admissions. No invented post-action reward or second selector.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.noesis_lab_work import propose_noesis_work, execute_noesis_work

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


def neural_config():
    c = dict(DEFAULT_CONFIG)
    c.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
             input_degree=4, action_population_size=8, seed=1842)
    return c


@unittest.skipUnless(HAS_LAB, "Requires actual pinned Laboratory, not mock world")
class NoesisActualConsequenceTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        from pretorius_lab.book_library import BookLibrary

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.world = SpatialHabitat.create(root / "world.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.port = PretoriusBrainPort(root / "brain", neural_config=neural_config())
        self.subject = SubjectPort(self.world)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        BookLibrary(self.world).initialize()
        # Location is a host opportunity, not a mind-authored navigation goal.
        self.bridge.act("walk", event_id="arrival-center", station="station:center")
        self.bridge.act("walk", event_id="arrival-bench", station="station:bench")

    def state(self):
        self.subject.verify()
        with self.world._open() as db:
            row = db.execute("SELECT value FROM rhythm_meta WHERE key='state'").fetchone()
            return json.loads(row[0])

    def actions(self, op):
        with self.world._open() as db:
            return db.execute(
                "SELECT count(*) FROM rhythm_events WHERE json_extract(envelope,'$.op')=?",
                (op,),
            ).fetchone()[0]

    def policy_audit(self, pid):
        with self.port.brain.store.connect() as db:
            row = db.execute(
                "SELECT policy_version,selected_action,state_pressure_json "
                "FROM policy_decisions WHERE id=?", (pid,),
            ).fetchone()
        self.assertIsNotNone(row)
        return row["selected_action"], json.loads(row["state_pressure_json"])

    def create_one_real_consequence(self):
        self.assertEqual(self.state()["apparatus"], 2)
        proposal = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(proposal.action, "experiment")
        action = execute_noesis_work(
            self.bridge, decision_id=proposal.decision_id,
            event_id="original-noesis-experiment", authorized_world_action=True,
        )
        self.assertEqual(action["world"]["status"], "admitted")
        self.assertEqual(self.state()["apparatus"], 1)
        self.assertEqual(self.actions("experiment"), 1)
        lived = self.port.brain.store.get_memory(action["world"]["memory_id"])
        self.assertEqual(lived["evidence_class"], "lived_runtime_memory")
        self.assertIn("apparatus shows wear", lived["text"])
        return action["world"]["memory_id"]

    def test_noesis_tried_experiment_suffered_wear_then_selected_real_repair(self):
        consequence_id = self.create_one_real_consequence()
        improved = propose_noesis_work(
            self.bridge, learning_enabled=False, outcome_learning_enabled=True,
        )
        self.assertEqual(improved.action, "repair")
        self.assertIn(consequence_id, improved.supporting_memory_ids)
        selected, audit = self.policy_audit(improved.decision_id)
        self.assertEqual(selected, "repair")
        self.assertEqual(audit["version"], "noesis-situated-choice-v0.3")
        self.assertEqual(audit["used_outcome_memory_ids"], [consequence_id])
        self.assertAlmostEqual(audit["outcome_contributions"]["experiment"], -0.6)
        self.assertAlmostEqual(audit["outcome_contributions"]["repair"], 0)
        self.assertEqual(self.actions("repair"), 0)
        with self.assertRaises(PermissionError):
            execute_noesis_work(
                self.bridge, decision_id=improved.decision_id,
                event_id="noesis-repair", authorized_world_action=False,
            )
        action = execute_noesis_work(
            self.bridge, decision_id=improved.decision_id,
            event_id="noesis-repair", authorized_world_action=True,
        )
        self.assertEqual(action["world"]["status"], "admitted")
        self.assertEqual(action["action"], "repair")
        self.assertEqual(self.state()["apparatus"], 3)
        self.assertEqual(self.state()["repairs"], 1)
        self.assertEqual(self.actions("repair"), 1)
        self.assertEqual(self.port.brain.store.get_memory(
            action["world"]["memory_id"]
        )["evidence_class"], "lived_runtime_memory")
        self.assertEqual(execute_noesis_work(
            self.bridge, decision_id=improved.decision_id,
            event_id="noesis-repair", authorized_world_action=True,
        )["world"]["status"], "already_admitted")
        self.port.save()
        self.port = PretoriusBrainPort(self.port.brain.state_dir)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        self.assertEqual(execute_noesis_work(
            self.bridge, decision_id=improved.decision_id,
            event_id="noesis-repair", authorized_world_action=True,
        )["world"]["status"], "already_admitted")
        self.assertEqual(self.actions("repair"), 1)

    def test_memory_lesion_off_and_restoration_change_choice_without_world_action(self):
        consequence_id = self.create_one_real_consequence()
        state = self.state()
        used = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(used.action, "repair")
        no_outcome = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=False, neural_prior_enabled=False,
        )
        self.assertEqual(no_outcome.action, "experiment")
        self.assertEqual(no_outcome.supporting_memory_ids, ())
        with self.port.brain.store.transaction() as db:
            self.port.brain.store.archive_memory(
                db, consequence_id, self.port.brain.store.tick,
                "temporary experimental outcome-memory ablation",
            )
            self.port.brain.store.bump_state_version(db)
        missing = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(missing.action, "experiment")
        self.assertEqual(missing.supporting_memory_ids, ())
        with self.port.brain.store.transaction() as db:
            db.execute("UPDATE memories SET active=1 WHERE id=?", (consequence_id,))
            self.port.brain.store.bump_state_version(db)
        returned = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(returned.action, "repair")
        self.assertEqual(tuple(returned.supporting_memory_ids), (consequence_id,))
        self.assertEqual(self.state(), state)
        self.port.save()
        self.port = PretoriusBrainPort(self.port.brain.state_dir)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        after_restart = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(after_restart.action, "repair")
        self.assertEqual(tuple(after_restart.supporting_memory_ids), (consequence_id,))

    def test_report_and_fake_self_report_never_promote_outcomes(self):
        genuine_id = self.create_one_real_consequence()
        with self.port.brain.store.transaction() as db:
            self.port.brain.store.archive_memory(
                db, genuine_id, self.port.brain.store.tick, "research lesion",
            )
            self.port.brain.store.bump_state_version(db)
        report = self.port.ingest({
            "channel": "world", "source": "report-of-an-experiment",
            "text": "Someone said I complete a careful experiment at my workbench. "
                    "The apparatus shows wear.",
        })
        self.assertEqual(self.port.brain.store.get_memory(
            report["memory_id"]
        )["evidence_class"], "external_statement")
        proposed = propose_noesis_work(
            self.bridge, learning_enabled=False, neural_prior_enabled=False,
            outcome_learning_enabled=True,
        )
        self.assertEqual(proposed.action, "experiment")
        self.assertEqual(proposed.supporting_memory_ids, ())

    def test_consequence_does_not_apply_after_world_is_repaired(self):
        self.create_one_real_consequence()
        repair = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True,
        )
        action = execute_noesis_work(
            self.bridge, decision_id=repair.decision_id,
            event_id="actual-repair-once", authorized_world_action=True,
        )
        self.assertEqual(action["action"], "repair")
        self.assertEqual(self.state()["apparatus"], 3)
        # Under the new *actually perceived* sound condition, neither the
        # earlier wear penalty nor remembered repair bonus may be applied.
        future = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True,
        )
        selected, audit = self.policy_audit(future.decision_id)
        self.assertEqual(selected, "experiment")
        self.assertEqual(audit["outcome_contributions"], {"experiment": 0.0})
        self.assertEqual(audit["used_outcome_memory_ids"], [])
        self.assertEqual(self.actions("repair"), 1)

    def test_replaying_world_action_is_not_another_learning_episode(self):
        outcome_id = self.create_one_real_consequence()
        retry = self.bridge.act("experiment", event_id="original-noesis-experiment")
        self.assertEqual(retry["status"], "already_admitted")
        self.assertEqual(retry["memory_id"], outcome_id)
        proposed = propose_noesis_work(
            self.bridge, learning_enabled=False, outcome_learning_enabled=True,
        )
        selected, audit = self.policy_audit(proposed.decision_id)
        self.assertEqual(selected, "repair")
        self.assertEqual(audit["used_outcome_memory_ids"], [outcome_id])
        self.assertAlmostEqual(audit["outcome_contributions"]["experiment"], -0.6)
        self.assertEqual(self.actions("experiment"), 1)




    def test_developmental_history_uses_own_receipt_and_survives_restart(self):
        outcome_id = self.create_one_real_consequence()
        def propose(enabled):
            return propose_noesis_work(
                self.bridge, learning_enabled=False, neural_prior_enabled=False,
                outcome_learning_enabled=enabled,
                developmental_history_enabled=enabled,
            )
        learned = propose(True)
        self.assertEqual(learned.action, "repair")
        self.assertEqual(learned.supporting_memory_ids, (outcome_id,))
        self.assertTrue(self.policy_audit(learned.decision_id)[1]["developmental_history_enabled"])
        self.assertEqual(propose(False).action, "experiment")
        self.port.save()
        self.port = PretoriusBrainPort(self.port.brain.state_dir)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        self.assertEqual(propose(True).supporting_memory_ids, (outcome_id,))
        self.assertEqual(propose(True).action, "repair")
        self.assertEqual(self.actions("experiment"), 1)
        self.assertEqual(self.actions("repair"), 0)

    def test_operator_work_is_not_developmental_self_experience(self):
        outcome = self.bridge.act("experiment", event_id="operator-experiment")
        self.assertEqual(outcome["status"], "admitted")
        proposed = propose_noesis_work(
            self.bridge, learning_enabled=False, neural_prior_enabled=False,
            outcome_learning_enabled=True, developmental_history_enabled=True,
        )
        self.assertEqual(proposed.action, "experiment")
        self.assertEqual(proposed.supporting_memory_ids, ())


    def _two_owned_wear_episodes_with_both_choices(self):
        """Actual physical history, with one reagent reserved for the probe."""
        from doctor_lives.lab_endogenous_book_task import EndogenousBookPursuit
        from doctor_lives.noesis_lab_work import _feasible_work
        def travel(destination, prefix):
            for i in range(12):
                current = self.subject.embodied.verify()["station"]
                if current == destination:
                    return
                target = EndogenousBookPursuit._route(current, destination)
                self.assertIsNotNone(target)
                self.bridge.act("walk", event_id=f"{prefix}-{i}", station=target)
            self.fail("Physical route did not arrive")

        # Operator preparation is not eligible as owned developmental experience.
        self.bridge.act("repair", event_id="development-fixture-repair")
        self.assertEqual(self.state()["apparatus"], 3)
        ids = []
        for i in range(2):
            proposal = propose_noesis_work(
                self.bridge, learning_enabled=False, neural_prior_enabled=False,
                outcome_learning_enabled=False,
            )
            self.assertEqual(proposal.action, "experiment")
            outcome = execute_noesis_work(
                self.bridge, decision_id=proposal.decision_id,
                event_id=f"development-experiment-{i}", authorized_world_action=True,
            )
            ids.append(outcome["world"]["memory_id"])
            travel("station:bedroom", f"development-outbound-{i}")
            self.bridge.act("rest", event_id=f"development-rest-{i}")
            travel("station:bench", f"development-return-{i}")
            self.bridge.act("clean", event_id=f"development-clean-{i}")
        self.assertEqual(self.state()["apparatus"], 1)
        self.assertEqual(self.state()["supplies"]["reagents"], 1)
        self.assertEqual(set(_feasible_work(self.bridge)), {"experiment", "repair"})
        return ids

    def _development_probe(self, *, enabled=True, neural=False, legacy=False):
        return propose_noesis_work(
            self.bridge, learning_enabled=False, neural_prior_enabled=neural,
            outcome_learning_enabled=enabled,
            developmental_history_enabled=enabled and not legacy,
        )

    def _set_episode_active(self, memory_id, active):
        store = self.port.brain.store
        with store.transaction() as db:
            if active:
                db.execute("UPDATE memories SET active=1 WHERE id=?", (memory_id,))
            else:
                store.archive_memory(db, memory_id, store.tick, "controlled history lesion")
            store.bump_state_version(db)

    def test_repeated_real_work_history_strengthens_appraisal_at_fixed_opportunity(self):
        first, second = self._two_owned_wear_episodes_with_both_choices()
        state = self.state()
        later = self._development_probe()
        self._set_episode_active(first, False)
        single = self._development_probe()
        self._set_episode_active(first, True)
        restored = self._development_probe()
        for probe in (later, single, restored):
            self.assertEqual(set(probe.candidate_scores), {"experiment", "repair"})
            self.assertEqual(probe.action, "repair")
            self.assertEqual(probe.observation_memory_id, later.observation_memory_id)
        self.assertEqual(set(later.supporting_memory_ids), {first, second})
        self.assertEqual(single.supporting_memory_ids, (second,))
        self.assertAlmostEqual(single.candidate_scores["experiment"], -0.08)
        self.assertAlmostEqual(later.candidate_scores["experiment"], -0.12)
        self.assertEqual(restored.candidate_scores, later.candidate_scores)
        self.assertEqual(self.state(), state)

    def test_accumulation_reverses_choice_under_declared_matched_prior(self):
        """Causal threshold control, not an uncoached neural-policy trial."""
        from unittest.mock import patch
        from doctor_lives.neural import ACTIONS
        first, second = self._two_owned_wear_episodes_with_both_choices()
        state = self.state()
        # Declared controlled prior: 0.20 * (0.75 - 0.25) = 0.10 margin.
        # This is between one and two developmental wear increments.
        prior = dict.fromkeys(ACTIONS, 0.0)
        prior.update(explore=0.75, persist=0.25)

        def probe(**kwargs):
            with patch.object(self.port.brain.neural, "action_scores", return_value=prior):
                return self._development_probe(neural=True, **kwargs)

        full = probe()
        withheld = probe(enabled=False)
        legacy = probe(legacy=True)
        self._set_episode_active(first, False)
        single = probe()
        self._set_episode_active(first, True)
        restored = probe()
        self.port.save()
        self.port = PretoriusBrainPort(self.port.brain.state_dir)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        reopened = probe()
        for result in (full, withheld, legacy, single, restored, reopened):
            self.assertEqual(set(result.candidate_scores), {"experiment", "repair"})
            self.assertEqual(result.observation_memory_id, full.observation_memory_id)
        self.assertEqual(withheld.action, "experiment")
        self.assertEqual(single.action, "experiment")
        self.assertEqual(full.action, "repair")
        self.assertEqual(restored.action, "repair")
        self.assertEqual(reopened.action, "repair")
        # Historical legacy rule already repairs after a single episode.
        self.assertEqual(legacy.action, "repair")
        self.assertEqual(single.supporting_memory_ids, (second,))
        self.assertEqual(set(reopened.supporting_memory_ids), {first, second})
        self.assertEqual(self.state(), state)
        self.assertEqual(self.actions("experiment"), 2)
        self.assertEqual(self.actions("repair"), 1)


class DevelopmentalAppraisalTests(unittest.TestCase):
    def test_distinct_histories_change_bounded_appraisal_not_world_authority(self):
        from types import SimpleNamespace
        from doctor_lives.noesis_consequences import (
            developmental_consequence_pressure, WORN, EXPERIMENT_WEAR,
            REPAIR_IMPROVEMENT,
        )
        records = {}
        def add(mid, event, text, tick, **extra):
            records[mid] = dict(active=True, external=False,
                evidence_class="lived_runtime_memory", created_tick=tick,
                source="laboratory-home:action:" + format(event, "064x"),
                text=text, **extra)
        for i in range(1, 7):
            add(str(i), i, EXPERIMENT_WEAR, i)
        add("alias", 1, EXPERIMENT_WEAR, 1)
        add("repair", 7, REPAIR_IMPROVEMENT, 8)
        add("foreign", 8, EXPERIMENT_WEAR, 9)
        records["foreign"]["external"] = True
        brain = SimpleNamespace(store=SimpleNamespace(get_memory=records.get))
        def evaluate(ids, observation=WORN):
            return developmental_consequence_pressure(
                brain, observation=observation,
                verified_outcome_memory_ids=tuple(ids),
                feasible_actions=("experiment", "repair"),
            )
        one, _, used = evaluate(["1"])
        self.assertEqual(used, ["1"])
        self.assertAlmostEqual(one["experiment"], -0.08)
        repeated, eligible, used = evaluate(list(records))
        self.assertAlmostEqual(repeated["experiment"], -0.15)
        self.assertAlmostEqual(repeated["repair"], 0.04)
        self.assertEqual(len(used), 5)
        self.assertNotIn("foreign", eligible)
        self.assertEqual(evaluate(["1", "alias"])[0], one)
        self.assertEqual(evaluate(list(reversed(records)))[0], repeated)
        self.assertEqual(evaluate(list(records), "I see sound apparatus.")[0],
                         {"experiment": 0.0, "repair": 0.0})
        records["1"]["active"] = False
        self.assertEqual(evaluate(["1"])[0]["experiment"], 0.0)

if __name__ == "__main__":
    unittest.main()
