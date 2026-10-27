"""Canonical, single-brain weather continuation for bounded six-organ research.

Only existing Pretorius BrainStore meta owns durable weather state.
Loads reviewed Affectus source under a DISTINCT Python package namespace so
the pinned Sensus scene donor cannot be accidentally substituted. No new
database, separate cognitive selector, model, or per-organ persistent store.

The Spinoza direction tags describe recent state, NEVER future change.
Weather is still an experimental input, not a production default.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any

from .chassis import PretoriusBrainPort

_DONOR_SHA = "904bf11861700739ccc03d4b0d4340ff3422a7d3"
_SOURCE_BLOBS = {
    "core.py": "507cd9f75af04353b5e42d67fb60c147acff5ffb",
    "affectus.py": "0bd2394291efe9ff41fd59320ae00d37b3d7f007",
}
_PACKAGE = "pretorius_reviewed_weather_donor"
_META = "six_organ_canonical_weather_v1"
_SCHEMA = "pretorius.canonical-affectus-weather.v1"


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def _digest(payload: dict) -> str:
    return sha256(_json(payload).encode("utf-8")).hexdigest()


def _git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load_reviewed_weather(source_root: str | Path):
    """Fail closed unless BOTH reviewed Git blobs match exactly.

    The independently reviewed Sensus is allowed to own the ordinary
    sensus_artificialis import; weather has no right to replace it.
    """
    root = Path(source_root).resolve()
    folder = root / "sensus_artificialis"
    for file, expected in _SOURCE_BLOBS.items():
        candidate = folder / file
        if not candidate.is_file() or _git_blob(candidate) != expected:
            raise RuntimeError("Unreviewed Affectus donor source: " + file)
    # Package-level namespacing is for code provenance, NOT a second brain.
    existing = sys.modules.get(_PACKAGE)
    if existing is not None and Path(existing.__path__[0]).resolve() != folder:
        raise RuntimeError("Different donor directory already loaded")
    if existing is None:
        package = ModuleType(_PACKAGE)
        package.__package__ = _PACKAGE
        package.__path__ = [str(folder)]
        sys.modules[_PACKAGE] = package
    for name in ("core", "affectus"):
        fullname = _PACKAGE + "." + name
        target = folder / (name + ".py")
        prior = sys.modules.get(fullname)
        if prior is not None:
            if Path(prior.__file__).resolve() != target:
                raise RuntimeError("Pinned Affectus donor module path changed")
            continue
        spec = importlib.util.spec_from_file_location(fullname, target)
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load reviewed donor module")
        module = importlib.util.module_from_spec(spec)
        sys.modules[fullname] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            del sys.modules[fullname]
            raise
    return sys.modules[_PACKAGE + ".affectus"]


@dataclass(frozen=True)
class WeatherReceipt:
    tick: int
    replay: bool
    modulation: dict[str, float]


class CanonicalWeather:
    """Bounded, optionally enabled six-organ weather, stored in ONE BrainStore."""

    def __init__(self, port: PretoriusBrainPort, *, donor_root: str | Path,
                 seed: int):
        if type(port) is not PretoriusBrainPort or type(seed) is not int:
            raise TypeError("Requires canonical brain port and fixed integer seed")
        self._port = port
        self._module = load_reviewed_weather(donor_root)
        self._config = self._module.AffectusConfig(seed=seed)
        self._config_json = asdict(self._config)
        self._weather = None
        self._stored_digest: str | None = None
        saved = port.brain.store.meta(_META)
        if saved is None:
            self._weather = self._module.Affectus(self._config)
            self._persist_new()
        else:
            envelope = self._decode(saved)
            if envelope["config"] != self._config_json:
                raise RuntimeError("Canonical weather configuration mismatch")
            self._weather = self._module.Affectus.restore(
                envelope["snapshot"], self._config,
            )
            self._stored_digest = envelope["integrity"]

    @classmethod
    def _decode(cls, raw: str) -> dict:
        try:
            envelope = json.loads(raw)
            integrity = envelope.pop("integrity")
            if (envelope["schema"] != _SCHEMA
                    or envelope["donor_sha"] != _DONOR_SHA
                    or integrity != _digest(envelope)):
                raise RuntimeError("Corrupt or unreviewed canonical weather")
            envelope["integrity"] = integrity
            if type(envelope["snapshot"]) is not dict:
                raise RuntimeError("Invalid canonical weather snapshot")
            return envelope
        except (ValueError, TypeError, KeyError) as exc:
            raise RuntimeError("Invalid canonical weather record") from exc

    def _envelope(self) -> dict:
        return {
            "schema": _SCHEMA,
            "donor_sha": _DONOR_SHA,
            "config": self._config_json,
            "snapshot": self._weather.snapshot(),
        }

    def _persist_new(self) -> None:
        envelope = self._envelope()
        digest = _digest(envelope)
        envelope["integrity"] = digest
        with self._port.brain.store.transaction() as conn:
            if conn.execute("SELECT 1 FROM meta WHERE key=?", (_META,)).fetchone():
                raise RuntimeError("Concurrent canonical weather initialization")
            self._port.brain.store.set_meta(_META, _json(envelope), conn)
            self._port.brain.store.bump_state_version(conn)
        self._stored_digest = digest

    @property
    def tick(self) -> int:
        return int(self._weather.snapshot()["last_tick"])

    def modulation(self):
        return self._weather.modulation()

    def step(self, tick: int, drivers: tuple, *,
             authorized: bool = False) -> WeatherReceipt:
        if authorized is not True:
            raise PermissionError("Only trusted host can advance weather")
        if type(tick) is not int or tick != (1 if self.tick == -1 else self.tick + 1):
            raise RuntimeError("Weather ticks must be monotonically continuous")
        if type(drivers) is not tuple or any(
            type(event) is not self._module.DriverEvent for event in drivers
        ):
            raise TypeError("Drivers must be source-pinned typed events")
        old = self._stored_digest
        self._weather.step(tick, drivers)
        envelope = self._envelope()
        new = _digest(envelope)
        envelope["integrity"] = new
        with self._port.brain.store.transaction() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key=?", (_META,)).fetchone()
            if row is None or self._decode(row[0])["integrity"] != old:
                raise RuntimeError("Concurrent/stale canonical weather writer")
            self._port.brain.store.set_meta(_META, _json(envelope), conn)
            self._port.brain.store.bump_state_version(conn)
        self._stored_digest = new
        return WeatherReceipt(
            tick=tick, replay=False,
            modulation=asdict(self._weather.modulation()),
        )

    def driver(self, kind: str, magnitude: float, source_ref: str):
        """Accept explicit trusted engineering fixture, never a model claim."""
        if not isinstance(source_ref, str) or not source_ref:
            raise ValueError("An engineer-side source reference is required")
        return self._module.DriverEvent(kind, magnitude, source_ref=source_ref)

    def snapshot_digest(self) -> str:
        return self._stored_digest
