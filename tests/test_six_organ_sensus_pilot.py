"""Pinned Sensus causal-acquisition pilot: explicit negative and matched controls.

These tests only execute when the REAL reviewed Sensus donor is installed.
The dedicated CI workflow forces installation and fails if the donor is absent.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.sensus_pilot import SensusCandidatePilot

HAS_SENSUS = importlib.util.find_spec("sensus_artificialis") is not None
if HAS_SENSUS:
    from sensus_artificialis import Evidence, Percept


def config():
    result = dict(DEFAULT_CONFIG)
    result.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    return result


@unittest.skipUnless(HAS_SENSUS, "Pinned Sensus donor required")
class PinnedSixOrganSensusPilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.runtime = SixOrganRuntime.open(self.root / "pretorius", neural_config=config())
        self.pilot = self.runtime.sensus.opt_in_multichannel_pilot()

    def percept(self, event_id, channel, value, *, evidence=None, source=None,
                attr="vessel color", tick=1, object_hint="vessel"):
        return Percept(
            event_id=event_id, channel=channel,
            evidence=evidence or Evidence.OBSERVED,
            source_ref=source or ("lab:" + event_id),
            tick=tick, attribute=attr, value=value, confidence=.95,
            object_hint=object_hint, features=(("type", "vessel"),),
        )

    def test_two_verified_agreeing_channels_become_first_person_acquisitions(self):
        claims = (
            self.percept("a", "vision", "red"),
            self.percept("b", "instrument", "red"),
        )
        result = self.pilot.acquire(
            1, claims, trusted_refs=frozenset({"lab:a", "lab:b"}),
            verified_world_refs=frozenset({"lab:a", "lab:b"}),
        )
        self.assertEqual(len(result.admitted), 2)
        self.assertFalse(result.vetoed_attributes)
        for receipt in result.admitted:
            self.assertTrue(receipt.first_person.startswith("I "))
            memory = self.runtime._port.brain.store.get_memory(receipt.memory_id)
            self.assertEqual(memory["text"], receipt.first_person)
            self.assertNotIn("world_epoch", memory["text"])
        self.assertNotEqual(result.admitted[0].memory_id, result.admitted[1].memory_id)

    def test_conflicting_observations_veto_autobiographical_admission(self):
        claims = (
            self.percept("a", "vision", "red"),
            self.percept("b", "instrument", "blue"),
        )
        before = self.runtime._port.brain.store.digest()
        result = self.pilot.acquire(
            1, claims, trusted_refs=frozenset({"lab:a", "lab:b"}),
            verified_world_refs=frozenset({"lab:a", "lab:b"}),
        )
        self.assertEqual(result.admitted, ())
        self.assertEqual(result.vetoed_attributes, ("vessel color",))
        self.assertEqual(set(result.withheld_claim_ids), {"a", "b"})
        self.assertNotEqual(before, self.runtime._port.brain.store.digest())
        self.assertEqual(len(result.epistemic_gap_ids), 1)
        with self.runtime._port.brain.store.connect() as db:
            concerns = db.execute(
                "SELECT id,source,actor FROM concerns WHERE source=?",
                ("preview_sensus_conflict",),
            ).fetchall()
            incoming = db.execute(
                "SELECT count(*) FROM memories WHERE source LIKE 'sensus-pilot-verified:%'"
            ).fetchone()[0]
        self.assertEqual(len(concerns), 1)
        self.assertEqual(concerns[0]["id"], result.epistemic_gap_ids[0])
        self.assertEqual(concerns[0]["actor"], "PREVIEW_HOST")
        self.assertEqual(incoming, 0)

    def test_conflict_lesion_changes_subsequent_memory_with_same_input(self):
        """Actual matched causal effect on autobiographical content, not IQ gain."""
        claims = (
            self.percept("a", "vision", "red"),
            self.percept("b", "instrument", "blue"),
        )
        # Control: current single-stream organ accepts both host-authorized
        # conflicting claims without the donor's multichannel scene veto.
        control = SixOrganRuntime.open(self.root / "control", neural_config=config())
        for claim in claims:
            control.sensus.acquire_existing_percept(
                {
                    "channel": "world",
                    "percept": f"I see that the vessel color is {claim.value}.",
                    "source": "lab:" + claim.event_id,
                },
                host_authorized=True,
            )
        lesion_memories = [
            m["text"] for m in control._port.brain.store.memories(False)
            if m["source"].startswith("lab:")
        ]
        donor = self.pilot.acquire(
            1, claims, trusted_refs=frozenset({"lab:a", "lab:b"}),
            verified_world_refs=frozenset({"lab:a", "lab:b"}),
        )
        donor_memories = [
            m["text"] for m in self.runtime._port.brain.store.memories(False)
            if m["source"].startswith("sensus-pilot-verified:")
        ]
        self.assertEqual(len(lesion_memories), 2)
        self.assertEqual(len(donor.admitted), 0)
        self.assertEqual(donor_memories, [])
        # This proves a selective difference in memory admission, not
        # independent perception of real laboratory phenomena.

    def test_unverified_and_reported_cues_do_not_become_lived_observations(self):
        clues = (
            self.percept("a", "vision", "red"),
            self.percept("b", "conversation", "blue",
                         evidence=Evidence.REPORTED),
        )
        before = self.runtime._port.brain.store.digest()
        outcome = self.pilot.acquire(
            1, clues, trusted_refs=frozenset({"lab:a", "lab:b"}),
            verified_world_refs=frozenset(),
        )
        self.assertFalse(outcome.admitted)
        self.assertEqual(before, self.runtime._port.brain.store.digest())
        self.assertCountEqual(outcome.withheld_claim_ids, ("a", "b"))

    def test_sensus_conflict_triggers_endogenous_mnemosyne_without_host_question(self):
        """Connected mechanism, not an injected concern or scripted recollection."""
        claims = (
            self.percept("a", "vision", "red"),
            self.percept("b", "instrument", "blue"),
        )
        control = SixOrganRuntime.open(
            self.root / "no-conflict", neural_config=config()
        )
        outcome = self.pilot.acquire(
            1, claims, trusted_refs=frozenset({"lab:a", "lab:b"}),
            verified_world_refs=frozenset({"lab:a", "lab:b"}),
        )
        self.assertEqual(outcome.admitted, ())
        self.assertEqual(len(outcome.epistemic_gap_ids), 1)
        control_mnemosyne = control.mnemosyne.opt_in_endogenous_recollection()
        treatment_mnemosyne = (
            self.runtime.mnemosyne.opt_in_endogenous_recollection()
        )
        a = control_mnemosyne.deliberate(recall_cost=0.0)
        b = treatment_mnemosyne.deliberate(recall_cost=0.0)
        self.assertNotEqual(a.action, "recall")
        self.assertEqual(b.action, "recall")
        self.assertEqual(b.selected_gap_id, outcome.epistemic_gap_ids[0])
        before = self.runtime._port.brain.store.digest()
        recollection = treatment_mnemosyne.recollect()
        from doctor_lives.models import SubjectFrame, SubjectRendererCapability
        self.assertIsInstance(recollection, SubjectFrame)
        self.assertTrue(SubjectRendererCapability.read(recollection))
        self.assertEqual(before, self.runtime._port.brain.store.digest())
        with self.runtime._port.brain.store.connect() as db:
            lived = db.execute(
                "SELECT count(*) FROM memories WHERE source LIKE 'sensus-pilot-verified:%'"
            ).fetchone()[0]
        self.assertEqual(lived, 0)

    def test_actual_sensus_conflict_can_drive_prior_memory_into_original_policy(self):
        """End-to-end opt-in Sensus -> Mnemosyne -> single Noesis policy."""
        # This is an independently admitted, earlier first-person experience.
        # The subsequently disputed values are NOT written as observations.
        prior = self.runtime.sensus.acquire_existing_percept(
            {
                "channel": "world", "source": "earlier-attested-vessel",
                "percept": "I saw that the vessel color was red yesterday.",
            },
            host_authorized=True,
        )
        outcome = self.pilot.acquire(
            1, (
                self.percept("a", "vision", "red"),
                self.percept("b", "instrument", "blue"),
            ),
            trusted_refs=frozenset({"lab:a", "lab:b"}),
            verified_world_refs=frozenset({"lab:a", "lab:b"}),
        )
        self.assertEqual(len(outcome.epistemic_gap_ids), 1)
        self.assertEqual(outcome.admitted, ())
        recall = self.runtime.mnemosyne.opt_in_endogenous_recollection()
        self.assertEqual(recall.deliberate(recall_cost=0).action, "recall")
        result = recall.reflect_selected_recollection()
        self.assertIsNotNone(result.next_policy_decision_id)
        self.assertTrue(result.cue_sha256)
        with self.runtime._port.brain.store.connect() as db:
            row = db.execute(
                "SELECT * FROM policy_decisions WHERE id=?",
                (result.next_policy_decision_id,),
            ).fetchone()
            disputed_memories = db.execute(
                "SELECT count(*) FROM memories WHERE source LIKE 'sensus-pilot-verified:%'"
            ).fetchone()[0]
            thoughts = db.execute(
                "SELECT count(*) FROM thoughts WHERE trigger='mnemosyne_private_reflection'"
            ).fetchone()[0]
        import json
        audit = json.loads(row["state_pressure_json"])
        self.assertEqual(audit["decision_text_sha256"], result.cue_sha256)
        self.assertEqual(disputed_memories, 0)
        self.assertEqual(thoughts, 1)
        self.assertIn(
            "vessel color", self.runtime._port.brain.store.get_memory(prior.memory_id)["text"]
        )
        self.runtime.checkpoint()
        from doctor_lives.organs import SixOrganRuntime
        reopened = SixOrganRuntime.open(self.root / "pretorius")
        with reopened._port.brain.store.connect() as db:
            persisted = db.execute(
                "SELECT count(*) FROM policy_decisions WHERE id=?",
                (result.next_policy_decision_id,),
            ).fetchone()[0]
        self.assertEqual(persisted, 1)
        new_recall = reopened.mnemosyne.opt_in_endogenous_recollection()
        with self.assertRaises(PermissionError):
            new_recall.reflect_selected_recollection()

    def test_single_channel_conflict_does_not_create_a_cross_channel_memory_cue(self):
        claims = (
            self.percept("a", "vision", "red"),
            self.percept("b", "vision", "blue"),
        )
        outcome = self.pilot.acquire(
            1, claims, trusted_refs=frozenset({"lab:a", "lab:b"}),
            verified_world_refs=frozenset({"lab:a", "lab:b"}),
        )
        self.assertTrue(outcome.vetoed_attributes)
        self.assertFalse(outcome.epistemic_gap_ids)
        self.assertFalse(outcome.admitted)

    def test_missing_source_and_unbounded_observation_reject_without_writes(self):
        before = self.runtime._port.brain.store.digest()
        claim = self.percept("a", "vision", "red")
        with self.assertRaises(PermissionError):
            self.pilot.acquire(
                1, (claim,), trusted_refs=frozenset({"unrelated"}),
                verified_world_refs=frozenset(),
            )
        with self.assertRaises(PermissionError):
            self.pilot.acquire(
                1, (claim,), trusted_refs=frozenset({"lab:a"}),
                verified_world_refs=frozenset({"unrelated"}),
            )
        unsafe = self.percept("unsafe", "vision", "red", attr="world_epoch")
        with self.assertRaises(ValueError):
            self.pilot.acquire(
                1, (unsafe,), trusted_refs=frozenset({"lab:unsafe"}),
                verified_world_refs=frozenset({"lab:unsafe"}),
            )
        self.assertEqual(before, self.runtime._port.brain.store.digest())

    def test_durable_replay_protection_without_sensus_memory_database(self):
        claim = self.percept("a", "hearing", "cracking", attr="sound")
        first = self.pilot.acquire(
            1, (claim,), trusted_refs=frozenset({"lab:a"}),
            verified_world_refs=frozenset({"lab:a"}),
        )
        self.assertEqual(len(first.admitted), 1)
        self.runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "pretorius")
        other_pilot = SensusCandidatePilot(reopened.sensus)
        duplicate = self.percept(
            "a", "hearing", "cracking", attr="sound", tick=2
        )
        before = reopened._port.brain.store.digest()
        with self.assertRaisesRegex(RuntimeError, "Repeated sensory event"):
            other_pilot.acquire(
                2, (duplicate,), trusted_refs=frozenset({"lab:a"}),
                verified_world_refs=frozenset({"lab:a"}),
            )
        self.assertEqual(before, reopened._port.brain.store.digest())
        self.assertFalse((self.root / "pretorius" / "sensus.sqlite3").exists())


if __name__ == "__main__":
    unittest.main()
