"""Actual PretoriusBrainPort + opt-in home pilot with source/action replay checks."""
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.models import SubjectFrame, SubjectRendererCapability


LAB_AVAILABLE = importlib.util.find_spec("pretorius_lab") is not None


@unittest.skipUnless(LAB_AVAILABLE, "Pinned Pretorius-Laboratory dependency required")
class RealDoctorHomeBridgeTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.world = SpatialHabitat.create(root / "world.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        config = dict(DEFAULT_CONFIG)
        config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                      input_degree=4, action_population_size=8)
        self.doctor = PretoriusBrainPort(root / "brain", neural_config=config)
        self.port = SubjectPort(self.world)
        self.bridge = DoctorHomeBridge(self.doctor, self.port, authorized=True)

    def source_memories(self):
        return [m for m in self.doctor.brain.store.memories(False)
                if m["source"].startswith("laboratory-home:")]

    def test_unauthorized_bridge_cannot_admit_world_experience(self):
        with self.assertRaises(PermissionError):
            DoctorHomeBridge(self.doctor, self.port)
        with self.assertRaises(PermissionError):
            self.bridge.act("invent_authority", event_id="invent-1")
        self.assertFalse(self.source_memories())

    def test_observation_enters_real_doctor_once_as_first_person_lived_memory(self):
        first = self.bridge.observe()
        self.assertEqual(first["status"], "admitted")
        self.assertTrue(first["subject"]["inner"].startswith("I "))
        old_tick = self.doctor.brain.store.tick
        second = self.bridge.observe()
        self.assertEqual(second["status"], "already_admitted")
        self.assertEqual(first["memory_id"], second["memory_id"])
        self.assertEqual(old_tick, self.doctor.brain.store.tick)
        mem = next(m for m in self.source_memories() if m["id"] == first["memory_id"])
        self.assertEqual(mem["text"], first["subject"]["inner"])
        self.assertEqual(mem["evidence_class"], "lived_runtime_memory")
        self.assertFalse(mem["external"])

    def test_legacy_laboratory_admission_precedes_actual_recurrent_step(self):
        from doctor_lives.tower_ipseity import TowerIpseity

        brain = self.doctor.brain
        self.assertIsNone(brain.store.meta("small-tower:world-binding-v1"))
        subject = TowerIpseity(brain)
        step = brain.neural.step
        observed = []

        def checked_step(text, *args, **kwargs):
            # Read from a separate SQLite connection, inside the actual
            # recurrent call: an uncommitted or post-hoc history cannot pass.
            memory = next(m for m in self.source_memories() if m["text"] == text)
            entries = subject.verify_history()
            owned = [entry for entry in entries
                     if entry["key"].endswith("acquisition:" + memory["id"])]
            self.assertEqual(len(owned), 1)
            item = owned[0]["content"][0]
            self.assertEqual(item["text"], text)
            self.assertEqual(item["attribution"], "lived")
            self.assertFalse(item["external"])
            self.assertIn(memory["source_event_id"], item["source_refs"])
            self.assertEqual(owned[0]["phase"], "acquisition")
            observed.append((memory["id"], owned[0]["sha256"]))
            return step(text, *args, **kwargs)

        with patch.object(brain.neural, "step", side_effect=checked_step):
            first = self.bridge.observe()
            retry = self.bridge.observe()
            self.assertEqual(retry["memory_id"], first["memory_id"])
            move = self.bridge.act("walk", event_id="qi02-hall", station="station:hall")
        self.assertEqual([m for m, _ in observed], [first["memory_id"], move["memory_id"]])
        entries = subject.verify_history()
        acquisitions = [e for e in entries if e["phase"] == "acquisition"]
        self.assertEqual([e["sha256"] for e in acquisitions], [h for _, h in observed])
        reopened = PretoriusBrainPort(brain.state_dir)
        self.assertEqual(TowerIpseity(reopened.brain).verify_history(), entries)

    def test_laboratory_noesis_context_is_owned_before_policy_and_survives_reopen(self):
        from doctor_lives.tower_ipseity import TowerIpseity, RECORD

        brain = self.doctor.brain
        self.bridge.observe()
        subject = TowerIpseity(brain)
        prefix = subject.verify_history()
        context = "I wonder what I should do next."
        original = brain._state_policy_scores

        def checked_policy(*args, **kwargs):
            latest = subject.verify_history()[-1]
            self.assertEqual(latest["phase"], "thought_context")
            self.assertEqual(latest["content"][0]["text"], context)
            self.assertEqual(kwargs["decision_text"], context)
            return original(*args, **kwargs)

        with patch.object(brain, "_state_policy_scores", side_effect=checked_policy):
            result = brain.think("lab_ownership_control", decision_text=context)
        history = subject.verify_history()
        self.assertEqual(history[:len(prefix)], prefix)
        self.assertEqual(history[-2]["sha256"], result["state_pressure"]["ipseity_context"]["sha256"])
        self.assertEqual(history[-1]["key"], RECORD + "thought:" + result["id"])
        self.assertIn(result["policy_decision_id"], history[-1]["content"][0]["source_refs"])
        self.assertEqual(history[-1]["content"][0]["text"], result["text"])

        # Failure must occur before policy, and must not change canonical state.
        before = brain.store.digest()
        with patch.object(TowerIpseity, "record", side_effect=PermissionError("denied")), \
                patch.object(brain, "_state_policy_scores", wraps=original) as policy:
            with self.assertRaisesRegex(PermissionError, "denied"):
                brain.think("lab_ownership_control", decision_text=context)
            policy.assert_not_called()
        self.assertEqual(brain.store.digest(), before)

        # Reopen without constructing a new world bridge: the ownership
        # restriction persists and the old history is not reconstructed.
        reopened = PretoriusBrainPort(brain.state_dir)
        reopened_subject = TowerIpseity(reopened.brain)
        self.assertEqual(reopened_subject.verify_history(), history)
        thought = reopened.cognition("heartbeat")
        self.assertEqual(reopened_subject.verify_history()[-1]["key"],
                         RECORD + "thought:" + thought["id"])
        self.assertEqual(reopened_subject.verify_history()[:-1], history)

    def test_failed_laboratory_subject_admission_does_not_reach_recurrence(self):
        from doctor_lives.tower_ipseity import TowerIpseity

        brain = self.doctor.brain
        tick = brain.store.tick
        neural_tick = brain.neural.tick
        before = TowerIpseity(brain).verify_history()
        with patch.object(TowerIpseity, "record", side_effect=PermissionError("admission fault")), \
                patch.object(brain.neural, "step", wraps=brain.neural.step) as recurrent:
            with self.assertRaisesRegex(PermissionError, "admission fault"):
                self.bridge.observe()
            recurrent.assert_not_called()
        self.assertEqual(brain.store.tick, tick)
        self.assertEqual(brain.neural.tick, neural_tick)
        self.assertEqual(TowerIpseity(brain).verify_history(), before)
        self.assertFalse(self.source_memories())
        self.assertEqual(self.bridge.observe()["status"], "admitted")

    def test_conscious_dream_recollection_requires_owned_admission_before_deliberation(self):
        # Controlled donor-output fixture. The actual Laboratory sleep and
        # source receipt are real; this does not qualify the external donor.
        from doctor_lives.lab_phantasmagorium import STATE, sync_phantasmagorium
        from doctor_lives.tower_ipseity import TowerIpseity
        brain = self.doctor.brain
        self.assertIsNone(brain.store.meta("small-tower:world-binding-v1"))
        for index, station in enumerate(("station:hall", "station:bedroom")):
            self.bridge.act("walk", event_id=f"qi02-dream-walk-{index}", station=station)
        sleep = self.bridge.act("sleep", event_id="qi02-dream-sleep")
        subject = TowerIpseity(brain)
        prefix = subject.verify_history()
        digest_before = brain.store.digest()
        neural_before = brain.neural.tick
        world_before = self.world.verify()
        text = "I recall a dream: a silver pendulum swayed above the sea."
        marked = {"epistemic_status": "dreamed_not_lived", "marked": True,
                  "factual_memory_eligible": False, "world_fact_authority": False,
                  "tool_authority": False}
        packet = {"files": {}, "result": dict(marked, fragments=[]),
                  "recall": dict(marked, has_recollection=True, text=text), "echo": None}
        with patch("doctor_lives.lab_phantasmagorium.verify_archive", return_value=Path("fixture.zip")), \
                patch("doctor_lives.lab_phantasmagorium._run", return_value=packet):
            with patch.object(TowerIpseity, "record", side_effect=PermissionError("admission fault")):
                with self.assertRaisesRegex(PermissionError, "admission fault"):
                    sync_phantasmagorium(self.bridge, Path("fixture.zip"))
            self.assertEqual(brain.store.digest(), digest_before)
            self.assertIsNone(brain.store.meta(STATE))
            self.assertEqual(subject.verify_history(), prefix)
            report = sync_phantasmagorium(self.bridge, Path("fixture.zip"))
            history = subject.verify_history()
            self.assertEqual(history[:-1], prefix)
            self.assertEqual(len(history), len(prefix) + 1)
            entry = history[-1]
            self.assertEqual(entry["sha256"], report["ipseity_admission_sha256"])
            self.assertEqual(entry["phase"], "imagination")
            item = entry["content"][0]
            mid = report["recollection_memory_id"]
            self.assertEqual(item["organ"], "Phantasmagorium")
            self.assertEqual(item["mode"], "recollection")
            self.assertEqual(item["attribution"], "dreamed")
            self.assertEqual(item["text"], text)
            self.assertEqual(item["source_refs"], [sleep["memory_id"], mid])
            self.assertEqual(brain.store.get_memory(mid)["evidence_class"], "dreamed_not_lived")
            self.assertTrue(brain.store.get_memory(mid)["external"])
            for key in ("world_authority", "factual_memory_eligible", "motor_authority"):
                self.assertFalse(report[key])
            self.assertEqual(brain.neural.tick, neural_before)
            self.assertEqual(self.world.verify(), world_before)
            self.assertIsNone(sync_phantasmagorium(self.bridge, Path("fixture.zip")))
            self.assertEqual(subject.verify_history(), history)
        # Controlled downstream cue: both the original dreamed attribution
        # and the new Noesis context must be durably owned BEFORE selection.
        # A context record is a thought about the dream, not a lived event.
        original = brain._state_policy_scores
        witnessed = []
        def checked_policy(*args, **kwargs):
            self.assertEqual(kwargs["decision_text"], text)
            committed = subject.verify_history()
            self.assertEqual(committed[:-1], history)
            self.assertEqual(committed[-2], entry)
            context = committed[-1]
            self.assertEqual(context["phase"], "thought_context")
            self.assertEqual(context["previous_sha256"], entry["sha256"])
            self.assertEqual(context["sequence"], entry["sequence"] + 1)
            self.assertEqual(context["content"], [{
                "organ": "Noesis", "mode": "internal_thought",
                "attribution": "unknown", "text": text,
                "source_refs": [], "external": False,
            }])
            witnessed.append(context)
            return original(*args, **kwargs)
        with patch.object(brain, "_state_policy_scores", side_effect=checked_policy):
            decision = brain.think("test_post_dream_deliberation", decision_text=text)
        self.assertEqual(len(witnessed), 1)
        context = witnessed[0]
        self.assertEqual(decision["state_pressure"]["ipseity_context"],
                         {"key": context["key"], "sha256": context["sha256"]})
        committed = subject.verify_history()
        self.assertEqual(committed[:-1], history + [context])
        thought = committed[-1]
        self.assertEqual(thought["phase"], "private_thought")
        self.assertEqual(thought["previous_sha256"], context["sha256"])
        self.assertEqual(thought["sequence"], context["sequence"] + 1)
        self.assertEqual(thought["content"][0]["text"], decision["text"])
        self.assertIn(decision["id"], thought["content"][0]["source_refs"])
        self.assertIn(decision["policy_decision_id"], thought["content"][0]["source_refs"])
        # Do not promote the dreamed recollection into factual or lived memory.
        dream_memory = brain.store.get_memory(mid)
        self.assertEqual(dream_memory["evidence_class"], "dreamed_not_lived")
        self.assertTrue(dream_memory["external"])
        self.assertEqual(dream_memory["text"], text)
        self.assertEqual(self.world.verify(), world_before)
        self.assertEqual(brain.neural.tick, neural_before)
        reopened = PretoriusBrainPort(brain.state_dir)
        self.assertEqual(TowerIpseity(reopened.brain).verify_history(), committed)
        self.assertEqual(reopened.brain.store.get_memory(mid)["evidence_class"],
                         "dreamed_not_lived")

    def test_waking_fancy_commits_owned_motifs_or_rolls_back(self):
        from doctor_lives.lab_phantasmagorium import STATE, sync_phantasmagorium
        from doctor_lives.tower_ipseity import TowerIpseity
        from doctor_lives.tower_phantasmagorium import fancy_line
        brain = self.doctor.brain
        subject = TowerIpseity(brain)
        # Controlled adapter-boundary test with a genuine source observation.
        # The read candidate and donor packet are fixtures, not a live read or donor qualification.
        seen = self.bridge.observe()
        memory = brain.store.get_memory(seen["memory_id"])
        digest = "f" * 64
        motif = "a clock made of clouds"
        marked = {"epistemic_status": "dreamed_not_lived", "marked": True,
                  "factual_memory_eligible": False, "world_fact_authority": False,
                  "tool_authority": False}
        packet = {"files": {}, "result": dict(marked, epistemic_status="hypothetical_only",
                  fragments=[dict(marked, motif=motif)]), "recall": None, "echo": None}
        prefix = subject.verify_history()
        before = brain.store.digest()
        neural_before = brain.neural.tick
        with patch("doctor_lives.lab_phantasmagorium.verify_archive", return_value=Path("fixture.zip")), \
                patch("doctor_lives.lab_phantasmagorium._next_event", side_effect=lambda bridge, table, cursor, op:
                      (1, digest, memory) if op == "read" and cursor == 0 else None), \
                patch("doctor_lives.lab_phantasmagorium._run", return_value=packet):
            with patch.object(TowerIpseity, "record", side_effect=PermissionError("admission fault")):
                with self.assertRaisesRegex(PermissionError, "admission fault"):
                    sync_phantasmagorium(self.bridge, Path("fixture.zip"))
            self.assertEqual(brain.store.digest(), before)
            self.assertIsNone(brain.store.meta(STATE))
            self.assertEqual(subject.verify_history(), prefix)
            report = sync_phantasmagorium(self.bridge, Path("fixture.zip"))
            entry = subject.verify_history()[-1]
            self.assertEqual(entry["sha256"], report["ipseity_admission_sha256"])
            self.assertEqual(entry["content"], [{"organ": "Phantasmagorium", "text": fancy_line(motif),
                "mode": "internal_thought", "attribution": "imagined",
                "source_refs": [memory["id"]], "external": True}])
            self.assertIsNone(report["recollection_memory_id"])
            self.assertEqual(brain.neural.tick, neural_before)
            self.assertIsNone(sync_phantasmagorium(self.bridge, Path("fixture.zip")))
            self.assertEqual(subject.verify_history(), prefix + [entry])

    def test_involuntary_utterance_becomes_real_doctor_memory_without_raw_body_data(self):
        self.bridge.act("walk", event_id="go-hall", station="station:hall")
        hit = self.bridge.act("walk", event_id="hit-stool", station="station:shop:private")
        self.assertEqual(hit["subject"]["spoken_aloud"], "Ow! My foot!")
        self.assertIn("That was aloud?", hit["subject"]["inner"])
        memory = next(m for m in self.source_memories() if m["id"] == hit["memory_id"])
        self.assertIn("I had not meant", memory["text"])
        self.assertNotIn("foot_soreness", memory["text"])
        self.assertNotIn("world_epoch", memory["text"])
        self.assertEqual(self.port.home.audit_state()["body"]["reflexes"], 1)
        self.assertEqual(self.doctor.brain.store.tick > 0, True)

    def test_retry_after_other_world_actions_never_repeats_earlier_doctor_ingress(self):
        self.bridge.act("walk", event_id="go-hall", station="station:hall")
        first = self.bridge.act("walk", event_id="hit-stool", station="station:shop:private")
        self.bridge.act("advance", event_id="clock-forward", minutes=120)
        memories_before = len(self.source_memories())
        tick = self.doctor.brain.store.tick
        second = self.bridge.act("walk", event_id="hit-stool", station="station:shop:private")
        self.assertEqual(second["status"], "already_admitted")
        self.assertEqual(second["subject"], first["subject"])
        self.assertEqual(tick, self.doctor.brain.store.tick)
        self.assertEqual(len(self.source_memories()), memories_before)
        with self.assertRaises(RuntimeError):
            self.bridge.act("walk", event_id="hit-stool", station="station:bedroom")

    def test_nighttime_source_admitted_without_unseen_items(self):
        self.bridge.act("walk", event_id="go-hall", station="station:hall")
        self.bridge.act("walk", event_id="go-bed", station="station:bedroom")
        self.bridge.act("open", event_id="open-wardrobe", container="wardrobe:bedroom")
        light = self.bridge.observe()
        self.assertIn("heavy wool coat", light["subject"]["inner"])
        for ordinal in (1, 2, 3):
            self.bridge.act("advance", event_id=f"night-{ordinal}", minutes=240)
        dark = self.bridge.observe()
        self.assertIn("too dark", dark["subject"]["inner"])
        self.assertNotIn("heavy wool coat", dark["subject"]["inner"])
        tick = self.doctor.brain.store.tick
        with self.assertRaises(Exception):
            self.bridge.act("take", event_id="invisible-coat", item="garment:coat")
        self.assertEqual(tick, self.doctor.brain.store.tick)
        self.bridge.act("light", event_id="lamp-light")
        revealed = self.bridge.observe()
        self.assertIn("heavy wool coat", revealed["subject"]["inner"])

    def test_actual_doctor_policy_runs_after_admitted_environment_not_host_mock(self):
        result = self.bridge.observe()
        decision = self.bridge.request_cognition(trigger="laboratory_home")
        self.assertIsInstance(decision, dict)
        self.assertTrue(decision.get("selected_action"))
        self.assertTrue(decision.get("action_scores"))
        memory = next(m for m in self.source_memories() if m["id"] == result["memory_id"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        # Cognition is a real decision tendency. This experiment has NOT
        # authorized or demonstrated autonomy in selecting a world action.
        self.assertEqual(self.port.home.audit_state()["body"]["steps"], 0)

    def test_brain_reopen_preserves_admitted_sources_without_cloning_world_life(self):
        seen = self.bridge.observe()
        reopened = PretoriusBrainPort(self.doctor.brain.state_dir)
        actor = DoctorHomeBridge(reopened, self.port, authorized=True)
        retry = actor.observe()
        self.assertEqual(retry["status"], "already_admitted")
        self.assertEqual(retry["memory_id"], seen["memory_id"])


@unittest.skipUnless(LAB_AVAILABLE, "Pinned Pretorius-Laboratory dependency required")
class SixOrganLaboratoryParityTests(RealDoctorHomeBridgeTests):
    """Exercise the SAME Laboratory world and existing bridge via six organs."""

    def setUp(self):
        super().setUp()
        self.runtime = SixOrganRuntime(self.doctor)
        self.bridge = self.runtime.bind_laboratory(self.port, authorized=True)

    def test_six_organ_world_observation_action_memory_and_restart(self):
        with self.assertRaises(PermissionError):
            self.runtime.bind_laboratory(self.port)
        first = self.bridge.observe()
        self.assertEqual(first["status"], "admitted")
        decision = self.runtime.noesis.deliberate(host_trigger="laboratory-parity")
        self.assertTrue(decision.selected_tendency)
        self.assertFalse(hasattr(decision, "world_receipt"))
        walked = self.bridge.act(
            "walk", event_id="six-organ-go-hall", station="station:hall"
        )
        self.assertEqual(walked["status"], "admitted")
        hit = self.bridge.act(
            "walk", event_id="six-organ-hit-stool",
            station="station:shop:private"
        )
        self.assertEqual(hit["subject"]["spoken_aloud"], "Ow! My foot!")
        self.assertIn("That was aloud?", hit["subject"]["inner"])
        self.assertNotIn("foot_soreness", hit["subject"]["inner"])
        frame = self.runtime.synthetic_ipseity.project_subject_frame()
        self.assertIsInstance(frame, SubjectFrame)
        for line in SubjectRendererCapability.read(frame):
            self.assertNotIn("world_epoch", line)
            self.assertNotIn("foot_soreness", line)
        tick = self.doctor.brain.store.tick
        again = self.bridge.act(
            "walk", event_id="six-organ-hit-stool",
            station="station:shop:private"
        )
        self.assertEqual(again["status"], "already_admitted")
        self.assertEqual(tick, self.doctor.brain.store.tick)
        self.runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.doctor.brain.state_dir)
        reopened_bridge = reopened.bind_laboratory(self.port, authorized=True)
        retried = reopened_bridge.act(
            "walk", event_id="six-organ-hit-stool",
            station="station:shop:private"
        )
        self.assertEqual(retried["status"], "already_admitted")
        self.assertEqual(retried["memory_id"], hit["memory_id"])



if __name__ == "__main__":
    unittest.main()
