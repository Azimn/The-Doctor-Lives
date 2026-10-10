"""D2 source-owned Mnemosyne + Chronos construction controls.

These tests validate source and temporal contracts, not learned forecasting.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.eidolon_temporal import ChronosCoil, MnemosyneLoom
from doctor_lives.neural import DEFAULT_CONFIG


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128, "sensory_dim": 64, "avg_recurrent_degree": 8,
        "input_degree": 4, "action_population_size": 8, "seed": 1842,
    })
    return cfg


class MnemosyneChronosTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.brain = PretoriusBrain(Path(self.temp.name), neural_config=small_config())

    @staticmethod
    def goal(audit, cid):
        return next(g for g in audit.goals if g.commitment_id == cid)

    def prepare_henry(self):
        episode = self.brain.ingest(Experience(
            "I examined the anatomical apparatus alongside Henry.",
            actor="Henry", kind="interaction", confidence=.9,
            novelty=.3, social=.7, valence=.4
        ))
        cid = self.brain.add_commitment(
            "Finish the anatomical apparatus",
            actor="Henry", due_tick=self.brain.store.tick + 4,
            importance=.7
        )
        return episode, cid

    def test_lived_history_attaches_original_event_provenance(self):
        ingested, cid = self.prepare_henry()
        witnesses = MnemosyneLoom.collect(self.brain)
        specific = [w for w in witnesses if w.memory_id == ingested["memory_id"]]
        self.assertEqual(len(specific), 1)
        self.assertEqual(specific[0].event_id, ingested["event_id"])
        self.assertEqual(specific[0].actor, "Henry")
        audit = ChronosCoil.forecast(self.brain)
        goal = self.goal(audit, cid)
        self.assertIn(ingested["memory_id"], goal.evidence_memory_ids)
        self.assertIn(ingested["event_id"], goal.evidence_event_ids)
        self.assertGreater(goal.priority, goal.baseline)

    def test_history_lesion_removes_evidence_boost_but_preserves_temporal(self):
        _, cid = self.prepare_henry()
        normal = self.goal(ChronosCoil.forecast(self.brain), cid)
        lesioned = self.goal(ChronosCoil.forecast(self.brain, with_history=False), cid)
        self.assertGreater(normal.priority, lesioned.priority)
        self.assertEqual(lesioned.evidence_support, 0)
        self.assertEqual(normal.urgency, lesioned.urgency)
        self.assertEqual(lesioned.evidence_event_ids, ())

    def test_same_description_other_actor_not_a_valid_witness(self):
        self.prepare_henry()
        wrong_id = self.brain.add_commitment(
            "Finish the anatomical apparatus", actor="Morgan",
            due_tick=self.brain.store.tick+4, importance=.7
        )
        row = self.goal(ChronosCoil.forecast(self.brain), wrong_id)
        self.assertEqual(row.evidence_support, 0)
        self.assertEqual(row.evidence_memory_ids, ())

    def test_external_only_claim_has_no_autobiographical_support(self):
        testimony = self.brain.ingest(Experience(
            "I examined the anatomical apparatus alongside Henry.",
            external=True, actor="Henry", source="message",
            kind="interaction", confidence=1.0
        ))
        cid = self.brain.add_commitment(
            "Finish the anatomical apparatus", actor="Henry", importance=.8
        )
        witness_ids = {w.memory_id for w in MnemosyneLoom.collect(self.brain)}
        self.assertNotIn(testimony["memory_id"], witness_ids)
        row = self.goal(ChronosCoil.forecast(self.brain), cid)
        self.assertEqual(row.evidence_support, 0)

    def test_corrupt_source_event_is_excluded_instead_of_trusted(self):
        ingested, cid = self.prepare_henry()
        self.assertGreater(
            self.goal(ChronosCoil.forecast(self.brain), cid).evidence_support, 0
        )
        with self.brain.store.transaction() as conn:
            conn.execute("UPDATE events SET payload_json=? WHERE id=?",
                         ('{"text":"A different event","actor":"Henry"}',
                          ingested["event_id"]))
            self.brain.store.bump_state_version(conn)
        ids = {w.memory_id for w in MnemosyneLoom.collect(self.brain)}
        self.assertNotIn(ingested["memory_id"], ids)
        self.assertEqual(
            self.goal(ChronosCoil.forecast(self.brain), cid).evidence_support, 0
        )

    def test_inactive_memory_does_not_survive_as_lived_evidence(self):
        ingested, cid = self.prepare_henry()
        with self.brain.store.transaction() as conn:
            self.brain.store.archive_memory(
                conn, ingested["memory_id"], self.brain.store.tick, "D2 fixture")
            self.brain.store.bump_state_version(conn)
        self.assertNotIn(
            ingested["memory_id"],
            {w.memory_id for w in MnemosyneLoom.collect(self.brain)}
        )
        self.assertEqual(
            self.goal(ChronosCoil.forecast(self.brain), cid).evidence_support, 0
        )

    def test_due_tick_and_time_lesion_are_distinguishable(self):
        _, cid = self.prepare_henry()
        now = self.brain.store.tick
        current = self.goal(ChronosCoil.forecast(self.brain), cid)
        future = self.goal(ChronosCoil.forecast(self.brain, at_tick=now+4), cid)
        self.assertGreater(future.urgency, current.urgency)
        self.assertTrue(future.projected_clock)
        self.assertEqual(future.evidence_event_ids, current.evidence_event_ids)
        no_temporal_current = self.goal(
            ChronosCoil.forecast(self.brain, with_temporal=False), cid)
        no_temporal_future = self.goal(
            ChronosCoil.forecast(self.brain, at_tick=now+4,
                                 with_temporal=False), cid)
        self.assertEqual(no_temporal_current.urgency, no_temporal_future.urgency)
        self.assertAlmostEqual(
            no_temporal_current.priority, no_temporal_future.priority
        )

    def test_resolved_commitment_ceases_to_be_eligible(self):
        _, cid = self.prepare_henry()
        self.assertEqual(len(ChronosCoil.forecast(self.brain).goals), 1)
        self.brain.resolve_commitment(cid, "Evidence checked and task completed.")
        self.assertEqual(len(ChronosCoil.forecast(self.brain).goals), 0)

    def test_future_episode_not_visible_in_counterfactual_past(self):
        # No future knowledge is used, even when the current DB contains it.
        self.brain.ingest(Experience(
            "I examined the anatomical apparatus alongside Henry.",
            actor="Henry", kind="interaction"
        ))
        witness = MnemosyneLoom.collect(self.brain)
        self.assertTrue(witness)
        earlier_tick = self.brain.store.tick-1
        self.assertFalse(MnemosyneLoom.collect(self.brain, as_of_tick=earlier_tick))

    def test_unmodified_production_state_and_subject_interface(self):
        _, cid = self.prepare_henry()
        before = (
            self.brain.store.digest(), self.brain.neural.tick,
            self.brain.neural.action_scores(),
            self.brain.render_request().to_dict(),
        )
        a = ChronosCoil.forecast(self.brain)
        b = ChronosCoil.forecast(self.brain)
        self.assertEqual(a, b)
        self.assertEqual(a.schema, "eidolon-d2-chronos-shadow-v0.1")
        self.assertEqual(self.goal(a, cid).projected_clock, False)
        after = (
            self.brain.store.digest(), self.brain.neural.tick,
            self.brain.neural.action_scores(),
            self.brain.render_request().to_dict(),
        )
        self.assertEqual(before, after)

    def test_invalid_clock_and_source_inputs_rejected(self):
        for value in (-1, True, "five", 0.3):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ChronosCoil.forecast(self.brain, at_tick=value)
        with self.assertRaises(TypeError):
            ChronosCoil.forecast(object())
        with self.assertRaises(TypeError):
            MnemosyneLoom.collect(object())

    def test_preawakening_stories_do_not_become_lived_events(self):
        witness_ids = {e.memory_id for e in MnemosyneLoom.collect(self.brain)}
        for row in self.brain.store.memories_with_classification():
            if row.get("autobiographical_class") in {
                "canonical_preawakening_memory",
                "reconstructed_preawakening_memory",
                "synthesized_preawakening_memory",
            }:
                self.assertNotIn(row["id"], witness_ids)


if __name__ == "__main__":
    unittest.main()
