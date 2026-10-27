"""12-cycle real Laboratory six-organ experimental host + restart exercise.

Distinct pinned donors are REQUIRED in dedicated CI; no source stub,
unauthenticated lived percept or fabricated physical receipt is accepted.
The locked acceptance protocol still demands matched full task/lesion
comparisons before claiming the *complete* autonomous Pretorius.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

from doctor_lives.lab_six_organ_session import SixOrganLaboratoryCycle
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.neural import DEFAULT_CONFIG

HAS_ALL = (
    all(importlib.util.find_spec(x) is not None
        for x in ("pretorius_lab", "sensus_artificialis",
                  "synthetic_ipseity"))
    and bool(os.getenv("PRETORIUS_PINNED_AFFECTUS_ROOT"))
)


def config():
    c = dict(DEFAULT_CONFIG)
    c.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
             input_degree=4, action_population_size=8, seed=1842)
    return c


@unittest.skipUnless(HAS_ALL, "Requires three independently pinned donor checkouts")
class TwelveCycleActualSixOrganLaboratory(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.world = SpatialHabitat.create(self.root / "lab.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.subject = SubjectPort(self.world)
        self.received = []
        self.config = config()
        self.weather_root = os.environ["PRETORIUS_PINNED_AFFECTUS_ROOT"]

    def renderer(self, first_person):
        if type(first_person) is not str or not first_person.startswith(
            ("I ", "My ", "Mine ", "Me ")
        ):
            raise PermissionError("Renderer received anything other than subject experience")
        self.received.append(first_person)
        return "I want to understand what happened."

    def host(self, runtime):
        return SixOrganLaboratoryCycle(
            runtime, self.subject, affectus_source=self.weather_root,
            renderer=self.renderer, authorized=True,
        )

    def test_12_cycles_all_six_source_attested_restart_and_no_extra_brain_store(self):
        rt = SixOrganRuntime.open(self.root / "brain", neural_config=self.config)
        results = []
        with self.host(rt) as session:
            for _ in range(6):
                results.append(session.cycle(authorized_world_action=True))
            self.assertEqual(session.weather.tick, 6)
            before = session.weather.snapshot_digest()
            rt.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "brain")
        with self.host(reopened) as session:
            self.assertEqual(session.weather.tick, 6)
            self.assertEqual(before, session.weather.snapshot_digest())
            for _ in range(6):
                results.append(session.cycle(authorized_world_action=True))
            self.assertEqual(session.weather.tick, 12)
            self.assertIs(session.runtime._port, session.runtime.noesis._port)
            self.assertIs(session.runtime._port, session.runtime.mnemosyne._port)
            self.assertIs(session.runtime._port, session.runtime.sensus._port)
            self.assertIs(session.runtime._port, session.runtime.affectus._port)
            self.assertIs(session.runtime._port, session.runtime.corpus._port)
            self.assertIs(session.runtime._port, session.runtime.synthetic_ipseity._port)
        self.assertEqual(len(results), 12)
        self.assertEqual(len(self.received), 12)
        self.assertEqual([r.tick for r in results], list(range(1, 13)))
        self.assertTrue(all(r.ports_used == (
            "Sensus", "Corpus", "Affectus", "Mnemosyne",
            "Noesis", "Synthetic Ipseity"
        ) for r in results))
        self.assertTrue(all(r.scene_admitted == 1 and r.body_verified
                            and r.subjective_delivery_count == 1 for r in results))
        self.assertTrue(all(not r.self_selected_goal_proven for r in results))
        self.assertTrue(all(not r.scene_vetoed for r in results))
        from doctor_lives.canonical_affectus_weather import _META
        self.assertIsNotNone(reopened._port.brain.store.meta(_META))
        self.assertFalse((self.root / "brain" / "affectus.sqlite3").exists())
        self.assertFalse((self.root / "brain" / "spinoza_weather.json").exists())
        self.subject.verify()
        for m in reopened._port.brain.store.memories():
            if m["source"].startswith(("laboratory-home:", "sensus-pilot-verified:")):
                self.assertEqual(m["evidence_class"], "lived_runtime_memory")
        for line in self.received:
            for forbidden in ("action_scores_json", "lab_experiment_weather",
                              "world_epoch", "opponent_levels", "checkpoint_sha256"):
                self.assertNotIn(forbidden, line)

    def test_host_denial_all_six_still_run_without_world_move(self):
        rt = SixOrganRuntime.open(self.root / "denied", neural_config=self.config)
        before = self.subject.embodied.verify()["revision"]
        with self.host(rt) as session:
            outcome = session.cycle(authorized_world_action=False)
        self.assertEqual(outcome.ports_used, (
            "Sensus", "Corpus", "Affectus", "Mnemosyne",
            "Noesis", "Synthetic Ipseity",
        ))
        self.assertEqual(outcome.movement_status, "not_executed")
        # Looking is an authenticated receipt; lack of movement still means
        # one observation event may advance the world log revision.
        self.assertEqual(self.subject.embodied.verify()["station"],
                         "station:threshold")
        self.assertGreaterEqual(self.subject.embodied.verify()["revision"], before)


if __name__ == "__main__":
    unittest.main()
