"""Exact-source weather continuation tests against ONE PretoriusBrainStore.

Optional-source tests are skipped in ordinary Doctor CI. Dedicated CI must
install the reviewed donor and run every test without skip.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from doctor_lives.organs import SixOrganRuntime
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.canonical_affectus_weather import (
    CanonicalWeather, load_reviewed_weather, _META,
)

ROOT = os.environ.get("PRETORIUS_PINNED_AFFECTUS_ROOT")
AVAILABLE = bool(ROOT and (
    Path(ROOT) / "sensus_artificialis" / "affectus.py"
).is_file())


def config():
    c = dict(DEFAULT_CONFIG)
    c.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
             input_degree=4, action_population_size=8, seed=1842)
    return c


@unittest.skipUnless(AVAILABLE, "Needs pinned Affectus donor checkout from dedicated CI")
class CanonicalSixOrganWeatherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "brain"
        self.runtime = SixOrganRuntime.open(self.path, neural_config=config())

    def weather(self, port=None):
        return CanonicalWeather(
            port or self.runtime._port, donor_root=ROOT, seed=1842
        )

    def tick_weather(self, weather, tick, kind):
        return weather.step(tick, (
            weather.driver(kind, 1.0, "verified:engineer-fixture"),
        ), authorized=True)

    def test_weather_survives_canonical_brain_restart_with_all_donor_dynamics(self):
        weather = self.weather()
        for tick in range(1, 37):
            self.tick_weather(
                weather, tick,
                "goal_progress" if tick <= 18 else "goal_impediment",
            )
        before_mod = weather.modulation()
        first_digest = weather.snapshot_digest()
        saved = json.loads(self.runtime._port.brain.store.meta(_META))
        self.assertEqual(saved["snapshot"]["last_tick"], 36)
        self.assertTrue(saved["snapshot"]["trajectory"])
        self.assertTrue(saved["snapshot"]["receipts"])
        self.assertTrue(saved["snapshot"]["opponent"])
        self.assertTrue(saved["snapshot"]["sensitivity"])
        self.assertTrue(saved["snapshot"]["rng_state"])
        self.runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.path)
        reconstructed = CanonicalWeather(
            reopened._port, donor_root=ROOT, seed=1842,
        )
        self.assertEqual(reconstructed.tick, 36)
        self.assertEqual(reconstructed.snapshot_digest(), first_digest)
        self.assertEqual(reconstructed.modulation(), before_mod)
        for tick in range(37, 49):
            kind = "monotony" if tick < 44 else "rest_density"
            self.tick_weather(reconstructed, tick, kind)
        # Exactly ONE canonical owner: the reopened runtime has advanced
        # weather; the stale pre-restart handle MUST fail closed.
        with self.assertRaises(RuntimeError):
            self.tick_weather(weather, 37, "monotony")
        self.assertEqual(
            CanonicalWeather(reopened._port, donor_root=ROOT, seed=1842).tick,
            48,
        )
        self.assertFalse((self.path / "spinoza_weather.json").exists())
        self.assertFalse((self.path / "affectus.sqlite3").exists())

    def test_source_binds_distinct_sensus_package_and_rejects_modified_blobs(self):
        from types import ModuleType
        import sys
        original = sys.modules.get("sensus_artificialis")
        sentinel = ModuleType("sensus_artificialis")
        try:
            sys.modules["sensus_artificialis"] = sentinel
            donor = load_reviewed_weather(ROOT)
            self.assertEqual(donor.Affectus.__module__,
                             "pretorius_reviewed_weather_donor.affectus")
            self.assertIs(sys.modules["sensus_artificialis"], sentinel)
        finally:
            if original is None:
                del sys.modules["sensus_artificialis"]
            else:
                sys.modules["sensus_artificialis"] = original
        with tempfile.TemporaryDirectory() as tmp:
            from shutil import copytree
            copied = Path(tmp)
            copytree(Path(ROOT) / "sensus_artificialis",
                     copied / "sensus_artificialis")
            (copied / "sensus_artificialis" / "affectus.py").write_text(
                (copied / "sensus_artificialis" / "affectus.py").read_text()
                + "\n# changed source\n",
            )
            with self.assertRaisesRegex(RuntimeError, "Unreviewed"):
                load_reviewed_weather(copied)

    def test_rejects_tampered_and_wrong_config_canonical_state(self):
        weather = self.weather()
        self.tick_weather(weather, 1, "goal_progress")
        with self.assertRaisesRegex(RuntimeError, "configuration mismatch"):
            CanonicalWeather(self.runtime._port, donor_root=ROOT, seed=9999)
        with self.runtime._port.brain.store.transaction() as db:
            record = json.loads(db.execute(
                "SELECT value FROM meta WHERE key=?", (_META,)
            ).fetchone()[0])
            record["snapshot"]["state"]["valence"] = 1000
            db.execute("UPDATE meta SET value=? WHERE key=?", (
                json.dumps(record), _META,
            ))
        with self.assertRaisesRegex(RuntimeError, "Corrupt"):
            self.weather()

    def test_untrusted_driver_and_tick_rejected_without_store_change(self):
        weather = self.weather()
        before = weather.snapshot_digest()
        with self.assertRaises(PermissionError):
            weather.step(1, ())
        with self.assertRaises(RuntimeError):
            weather.step(2, (), authorized=True)
        with self.assertRaises(TypeError):
            weather.step(1, ({"kind": "goal_progress"},), authorized=True)
        with self.assertRaises(ValueError):
            weather.driver("goal_progress", 1.0, "")
        self.assertEqual(self.weather().snapshot_digest(), before)
        self.tick_weather(weather, 1, "goal_progress")
        with self.assertRaises(RuntimeError):
            self.tick_weather(weather, 1, "goal_progress")
        self.assertEqual(self.weather().tick, 1)


if __name__ == "__main__":
    unittest.main()
