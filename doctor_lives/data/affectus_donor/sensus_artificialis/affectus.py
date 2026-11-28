"""Affectus prototype: slow interoceptive weather dynamics.

Jazz, not composition. This module composes the instrument -- state
variables, drivers, update rules, the felt-report interface, receipts --
and never composes the performance. Trajectories emerge from drivers x
dynamics x noise; they are not scripted. The felt report is a coarse,
possibly misattributed quantization of the state. The gap between felt
and actual is the point, not a bug.

Character-agnostic and standalone. Drivers are abstract event kinds, not
organism concepts. Modulation outputs are typed but unconsumed here;
lateral adapters (Daemonium gain, rehearsal bias, Ipseity admission) are
future work behind the adoption gates. Nothing here writes to any
archive. There is deliberately no reset method: if the weather can be
willed away, it is a setting, not an emotion.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite
from random import Random

from .core import Attribution, Evidence, Percept

DIMS = ("valence", "arousal", "security", "fatigue")

DRIVER_KINDS = (
    "prediction_error",
    "goal_progress",
    "goal_impediment",
    "social_feedback",  # signed magnitude: + praise, - reproach
    "novelty",
    "monotony",
    "unresolved_loops",
    "rest_density",
)

# driver kind -> {dimension: weight}. Magnitude sign flows through, so
# social_feedback(-1.0) pushes valence/security negative.
_DRIVER_MAP = {
    "prediction_error": {"arousal": 0.6, "valence": -0.3},
    "goal_progress": {"valence": 0.6, "security": 0.4},
    "goal_impediment": {"valence": -0.6, "arousal": 0.3},
    "social_feedback": {"valence": 0.5, "security": 0.5},
    "novelty": {"arousal": 0.5},
    "monotony": {"arousal": -0.4, "fatigue": 0.4},
    "unresolved_loops": {"fatigue": 0.5, "security": -0.4},
    "rest_density": {"fatigue": -0.5, "arousal": -0.2},
}


@dataclass(frozen=True, slots=True)
class AffectusConfig:
    """Baseline heuristics. Every constant is inspectable and tunable."""

    step_gain: float = 0.08          # state displacement per unit net drive
    state_decay: float = 0.002      # per-tick pull toward 0 (half-life ~346)
    habituation_rate: float = 0.10  # sensitivity loss per exposure
    sensitivity_recovery: float = 0.03  # per quiet tick, toward 1.0
    opponent_build: float = 0.025   # counter-force accumulation; superlinear
    opponent_decay: float = 0.02    # counter-force release per tick
    noise_std: float = 0.004        # seeded jitter per dim per tick
    felt_quantum: float = 0.25      # felt report coarseness (the gap)
    trajectory_window: int = 8      # ticks of state history behind the felt direction
    direction_epsilon: float = 0.02  # min |delta| over the window to feel a direction
    seed: int = 0

    def __post_init__(self) -> None:
        for name in ("step_gain", "state_decay", "habituation_rate",
                     "sensitivity_recovery", "opponent_build",
                     "opponent_decay", "noise_std", "felt_quantum",
                     "direction_epsilon"):
            value = getattr(self, name)
            if not isfinite(value) or value < 0:
                raise ValueError(name + " must be a finite nonnegative number")
        if (not isinstance(self.trajectory_window, int)
                or self.trajectory_window < 2):
            raise ValueError("trajectory_window must be an int >= 2")
        if not isinstance(self.seed, int):
            raise TypeError("seed must be an int")


@dataclass(frozen=True, slots=True)
class DriverEvent:
    """One abstract push on the weather. Character-agnostic by construction."""

    kind: str
    magnitude: float
    source_ref: str = ""

    def __post_init__(self) -> None:
        if self.kind not in DRIVER_KINDS:
            raise ValueError("unknown driver kind: " + repr(self.kind))
        if not isfinite(self.magnitude):
            raise ValueError("magnitude must be finite")


@dataclass(frozen=True, slots=True)
class Receipt:
    """Append-only record: what moved the weather, and what it became."""

    tick: int
    driver_kind: str
    magnitude: float
    sensitivity: float
    state_after: tuple[tuple[str, float], ...]


@dataclass(frozen=True, slots=True)
class Modulation:
    """Typed but unconsumed here. Lateral adapters are future work."""

    salience_gain: float      # arousal widens/narrows what gets noticed
    exploration_bias: float   # valence/fatigue tilt explore vs exploit
    rehearsal_bias: float     # mood-congruent rehearsal tilt
    decay_multiplier: float   # arousal-gated consolidation strength


class Affectus:
    """Slow weather generator. Speaks Percept; owns no narrative."""

    def __init__(self, config: AffectusConfig | None = None) -> None:
        self.config = config or AffectusConfig()
        self._rng = Random(self.config.seed)
        self._state: dict[str, float] = {dim: 0.0 for dim in DIMS}
        self._sensitivity: dict[str, float] = {k: 1.0 for k in DRIVER_KINDS}
        self._opponent: dict[str, float] = {k: 0.0 for k in DRIVER_KINDS}
        self._receipts: list[Receipt] = []
        # Recent state trajectory: the felt direction is read off actual
        # recent movement, not the current level. Part of the weather --
        # it survives gaps via snapshot/restore.
        self._trajectory: deque[dict[str, float]] = deque(
            maxlen=self.config.trajectory_window)
        self._last_tick = -1
        self._event_seq = 0

    # -- read-only views -------------------------------------------------

    @property
    def state(self) -> dict[str, float]:
        return dict(self._state)

    @property
    def sensitivities(self) -> dict[str, float]:
        return dict(self._sensitivity)

    @property
    def opponent_levels(self) -> dict[str, float]:
        return dict(self._opponent)

    @property
    def receipts(self) -> tuple[Receipt, ...]:
        return tuple(self._receipts)

    # -- dynamics ---------------------------------------------------------

    def step(self, tick: int, drivers: tuple[DriverEvent, ...] = ()) -> None:
        """Advance one tick. Drivers are applied, then quiet-tick maintenance.

        Ticks must advance strictly. There is no reset: weather is not
        willable away.
        """
        if not isinstance(tick, int) or tick <= self._last_tick:
            raise ValueError("Ticks must advance strictly")
        driven: set[str] = set()
        for event in drivers:
            if not isinstance(event, DriverEvent):
                raise TypeError("Only DriverEvent values are accepted")
            kind = event.kind
            driven.add(kind)
            sensitivity = self._sensitivity[kind]
            effective = event.magnitude * sensitivity
            # a-process: immediate push through the driver map.
            displacement = effective * self.config.step_gain
            for dim, weight in _DRIVER_MAP[kind].items():
                self._state[dim] += displacement * weight
            # b-process: slower counter-force accumulates against the drive.
            # Superlinear in |effective|: intense drive recruits a strong
            # opponent (relief/letdown overshoot), while moderate drive
            # leaves the weather to persist on its slow decay.
            self._opponent[kind] += (effective * abs(effective)
                                     * self.config.opponent_build)
            self._sensitivity[kind] *= (1.0 - self.config.habituation_rate)
            self._event_seq += 1
            self._receipts.append(Receipt(
                tick=tick,
                driver_kind=kind,
                magnitude=event.magnitude,
                sensitivity=round(sensitivity, 6),
                state_after=tuple((d, round(v, 6)) for d, v in self._state.items()),
            ))
        cfg = self.config
        for kind in DRIVER_KINDS:
            if kind not in driven:
                s = self._sensitivity[kind]
                self._sensitivity[kind] = s + (1.0 - s) * cfg.sensitivity_recovery
            # The counter-force pushes every tick, driven or not: this is
            # what makes relief/letdown happen after the driver stops.
            push = self._opponent[kind] * cfg.step_gain
            for dim, weight in _DRIVER_MAP[kind].items():
                self._state[dim] -= push * weight
            self._opponent[kind] *= (1.0 - cfg.opponent_decay)
        for dim in DIMS:
            value = self._state[dim] * (1.0 - cfg.state_decay)
            value += self._rng.gauss(0.0, cfg.noise_std)
            self._state[dim] = max(-1.0, min(1.0, value))
        self._trajectory.append(dict(self._state))
        self._last_tick = tick

    # -- felt report ------------------------------------------------------

    def _felt_direction(self, dim: str) -> str:
        """Spinoza's transition channel: the felt *direction* of the weather.

        Read off the actual recent trajectory (oldest-to-newest state in
        the window), quantized coarsely like the level: '^' rising, 'v'
        falling, '~' no felt movement. A falling-but-still-positive valence
        reports '0.25v' -- the channel deliberately disagrees with the level
        when the trajectory does.
        """
        if len(self._trajectory) < 2:
            return "~"
        delta = self._trajectory[-1][dim] - self._trajectory[0][dim]
        eps = self.config.direction_epsilon
        if delta > eps:
            return "^"
        if delta < -eps:
            return "v"
        return "~"

    def _felt_value(self) -> str:
        q = self.config.felt_quantum
        parts = []
        for dim in DIMS:
            coarse = round(self._state[dim] / q) * q
            parts.append(dim + ":" + ("%.2f" % max(-1.0, min(1.0, coarse)))
                         + self._felt_direction(dim))
        return " ".join(parts)

    def emit_interoception(
        self,
        tick: int,
        event_id: str,
        source_ref: str = "affectus:weather",
        attributions: tuple[Attribution, ...] = (),
    ) -> Percept:
        """Speak the weather as an interoceptive Percept.

        The value is a coarse quantization of the state -- the felt/actual
        gap. Attributions are uncertain candidates supplied by the caller
        (the narrator/harness); this module never manufactures them. Empty
        attributions means unknown cause; a wrong cause_ref is representable
        and stays typed-uncertain, never observed.
        """
        if any(not isinstance(a, Attribution) for a in attributions):
            raise TypeError("attributions must be Attribution values")
        strength = max(abs(v) for v in self._state.values())
        return Percept(
            event_id=event_id,
            channel="interoception",
            evidence=Evidence.INTEROCEPTIVE,
            source_ref=source_ref,
            tick=tick,
            attribute="affective-weather",
            value=self._felt_value(),
            confidence=round(min(0.9, 0.4 + strength), 3),
            attributions=tuple(attributions),
        )

    # -- modulation (typed, unconsumed) ------------------------------------

    def modulation(self) -> Modulation:
        s = self._state
        return Modulation(
            salience_gain=round(1.0 + 0.5 * s["arousal"], 4),
            exploration_bias=round(0.5 * s["valence"] - 0.3 * s["fatigue"], 4),
            rehearsal_bias=round(0.5 * s["valence"], 4),
            decay_multiplier=round(max(0.5, min(1.5, 1.0 - 0.25 * s["arousal"])), 4),
        )

    # -- persistence across gaps -------------------------------------------

    def snapshot(self) -> dict:
        # The RNG stream is part of the weather: restoring it keeps the
        # stochastic texture continuous across the gap instead of
        # restarting it.
        version, internal, gauss_next = self._rng.getstate()
        return {
            "state": dict(self._state),
            "sensitivity": dict(self._sensitivity),
            "opponent": dict(self._opponent),
            "last_tick": self._last_tick,
            "event_seq": self._event_seq,
            "rng_state": [version, list(internal),
                          gauss_next if gauss_next is None else float(gauss_next)],
            "receipts": [
                {"tick": r.tick, "driver_kind": r.driver_kind,
                 "magnitude": r.magnitude, "sensitivity": r.sensitivity,
                 "state_after": [list(p) for p in r.state_after]}
                for r in self._receipts
            ],
            # The felt direction is part of the weather: it crosses the gap.
            "trajectory": [
                {d: float(snap[d]) for d in DIMS} for snap in self._trajectory
            ],
        }

    @classmethod
    def restore(cls, data: dict, config: AffectusConfig | None = None) -> "Affectus":
        inst = cls(config)
        inst._state = {d: float(data["state"][d]) for d in DIMS}
        inst._sensitivity = {k: float(data["sensitivity"][k]) for k in DRIVER_KINDS}
        inst._opponent = {k: float(data["opponent"][k]) for k in DRIVER_KINDS}
        inst._last_tick = int(data["last_tick"])
        inst._event_seq = int(data["event_seq"])
        inst._trajectory = deque(
            ({d: float(snap[d]) for d in DIMS}
             for snap in data.get("trajectory", [])),
            maxlen=inst.config.trajectory_window,
        )
        version, internal, gauss_next = data["rng_state"]
        inst._rng.setstate((int(version), tuple(internal), gauss_next))
        inst._receipts = [
            Receipt(tick=int(r["tick"]), driver_kind=r["driver_kind"],
                    magnitude=float(r["magnitude"]),
                    sensitivity=float(r["sensitivity"]),
                    state_after=tuple((d, float(v)) for d, v in r["state_after"]))
            for r in data["receipts"]
        ]
        return inst
