"""Non-skipped actual Laboratory readiness smoke for all SIX shared ports.

This smoke certifies laboratory TESTABILITY, not six mechanism graduation:
the multichannel Sensus donor, durable Ipseity donor and weather donor each
require separately pinned isolated CI jobs, because Sensus and Affectus are
different reviewed commits of the same external package. No new model, policy,
identity, persistent store, or world state authority is introduced.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.models import SubjectFrame, SubjectRendererCapability
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime, ORGAN_REGISTRY
from doctor_lives.noesis_corpus_pilot import HostCorpusOffer

LAB_AVAILABLE = importlib.util.find_spec("pretorius_lab") is not None


@unittest.skipUnless(LAB_AVAILABLE, "Requires pinned actual Laboratory, provided in CI")
class SixOrganActualLabReadiness(unittest.TestCase):
    def test_one_brain_six_live_ports_and_source_verified_lived_consequence(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            world = SpatialHabitat.create(home / "world.sqlite3")
            HomeLife(world).initialize()
            DailyRhythm(world).initialize()
            cfg = dict(DEFAULT_CONFIG)
            cfg.update(
                neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                input_degree=4, action_population_size=8, seed=1842,
            )
            rt = SixOrganRuntime.open(home / "brain", neural_config=cfg)
            ports = (
                rt.noesis, rt.mnemosyne, rt.affectus, rt.sensus,
                rt.synthetic_ipseity, rt.corpus,
            )
            self.assertEqual({d.name for d in ORGAN_REGISTRY}, {
                "Noesis", "Mnemosyne", "Affectus", "Sensus",
                "Synthetic Ipseity", "Corpus",
            })
            self.assertEqual({id(port._port) for port in ports}, {id(rt._port)})
            self.assertEqual(len(ports), 6)
            self.assertNotIn("production", rt.status()["qualification"].lower().split(";")[0])
            subject = SubjectPort(world)

            # Sensus source admission goes through the verified original
            # bridge, not via an untrusted caller asserting authorization.
            with self.assertRaises(PermissionError):
                rt.sensus.acquire_existing_percept({
                    "channel": "world", "percept": "I invented a world."
                })
            bridge = rt.bind_laboratory(subject, authorized=True)
            looked = bridge.observe()
            self.assertEqual(looked["status"], "admitted")
            source = rt._port.brain.store.get_memory(looked["memory_id"])
            self.assertEqual(source["text"], looked["subject"]["inner"])
            self.assertEqual(source["evidence_class"], "lived_runtime_memory")
            self.assertTrue(source["source"].startswith("laboratory-home:"))

            # Noesis alone supplies a tendency, not motor authority.
            pilot = rt.bind_causal_laboratory(subject, authorized=True)
            first = rt.noesis.deliberate(host_trigger="six-readiness-hall")
            offer = HostCorpusOffer(first.selected_tendency, "walk", "station:hall")
            with self.assertRaises(PermissionError):
                pilot.act(first, offer)
            hallway = pilot.act(first, offer, authorized=True)
            self.assertEqual(hallway.status, "admitted")
            self.assertEqual(subject.embodied.verify()["station"], "station:hall")
            second = rt.noesis.deliberate(host_trigger="six-readiness-impact")
            impact = pilot.act(
                second,
                HostCorpusOffer(
                    second.selected_tendency, "walk", "station:shop:private",
                ), authorized=True,
            )
            self.assertEqual(impact.spoken_aloud, "Ow! My foot!")

            # Affectus uses the previously reviewed, signed Laboratory body
            # evidence, not the independent Spinoza donor's private state.
            affect = rt.affectus.opt_in_laboratory_body_evidence(
                rt, subject, authorized=True,
            )
            before_affect = rt.affectus.read_motivational_influence()
            bodily = affect.admit_impact(impact, authorized=True)
            self.assertEqual(bodily.status, "admitted")
            self.assertIn("pain", bodily.first_person.lower())
            self.assertNotEqual(
                rt.affectus.read_motivational_influence().state_version,
                before_affect.state_version,
            )

            # Mnemosyne executes original replay, never authors a new memory
            # or competing self. Separate donor CI tests endogenous selection.
            sleep = rt.mnemosyne.replay_sleep(1)
            self.assertEqual(sleep.requested_ticks, 1)

            # Typed Ipseity exposes only first-person subject projections.
            frame = rt.synthetic_ipseity.project_subject_frame()
            self.assertIsInstance(frame, SubjectFrame)
            lines = SubjectRendererCapability.read(frame)
            self.assertTrue(lines)
            for hidden in (
                "world_epoch", "foot_soreness", "neural_checkpoint",
                "exploration_bias", "action_scores_json",
                "host_task_reservations",
            ):
                self.assertTrue(all(hidden not in text for text in lines))

            # Corpus and action/affect receipts survive the SAME brain restart.
            rt.checkpoint()
            reopened = SixOrganRuntime.open(home / "brain")
            self.assertEqual(
                {id(p._port) for p in (
                    reopened.noesis, reopened.mnemosyne, reopened.affectus,
                    reopened.sensus, reopened.synthetic_ipseity, reopened.corpus,
                )}, {id(reopened._port)},
            )
            self.assertEqual(
                reopened._port.brain.store.get_memory(bodily.body_memory_id)["text"],
                bodily.first_person,
            )
            replay = reopened.bind_causal_laboratory(
                subject, authorized=True,
            ).act(
                second,
                HostCorpusOffer(
                    second.selected_tendency, "walk", "station:shop:private"
                ),
                authorized=True,
            )
            self.assertEqual(replay.status, "already_admitted")
            self.assertEqual(replay.memory_id, impact.memory_id)
            self.assertEqual(
                reopened.affectus.opt_in_laboratory_body_evidence(
                    reopened, subject, authorized=True,
                ).admit_impact(impact, authorized=True).status,
                "already_admitted",
            )
            # Research weather from PR #90 has never been silently installed
            # as another organ-local persistent state.
            self.assertFalse((home / "brain" / "spinoza_weather.json").exists())
            self.assertFalse((home / "brain" / "affectus.sqlite3").exists())


if __name__ == "__main__":
    unittest.main()
