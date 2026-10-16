"""Opt-in portable game-AI arbitration, not a replacement Pretorius brain.

The existing brain owns motive, identity, relationships, goals and memories.
Environment adapters supply *perceived* opportunities, not world omniscience.
This module owns only bounded selection and source-verified procedural statistics.
It never executes actions, invents experience, or emits a subject-facing frame.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Mapping
import json
import math
import sqlite3


@dataclass(frozen=True)
class Opportunity:
    key: str  # environment-local action ID, never a life-memory ID
    domain: str
    strategy: str  # transferable procedural strategy, e.g. 'prepare'
    effects: Mapping[str, float]  # perceived expected benefit per motive
    effort: float = 0.0
    risk: float = 0.0
    goal_ids: frozenset[str] = field(default_factory=frozenset)
    perceived: bool = True


@dataclass(frozen=True)
class DecisionFrame:
    first_person: str
    source_event: str  # source-verified by the boundary adapter
    motives: Mapping[str, float]
    goal_ids: frozenset[str] = field(default_factory=frozenset)
    native_strategy_scores: Mapping[str, float] = field(default_factory=dict)
    cue: str = "general"  # subject-accessible situation category


@dataclass(frozen=True)
class Decision:
    key: str
    strategy: str
    score: float
    alternatives: tuple[tuple[str, float], ...]
    # Engineer audit ONLY. Never present as a Doctor perception or memory.


def _unit(value: object, what: str) -> float:
    if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{what} must be finite and between zero and one")
    return float(value)


def _identifier(value: str, what: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 128 or not value.strip() or "\x00" in value:
        raise ValueError(f"Invalid {what}")
    return value


class PortableLifePolicy:
    """Small portable utility arbitration with bounded habit and inertia biases.

    choose is advisory; only the host-authorized existing action interface
    can act. record_outcome requires a trusted source receipt validator.
    Stored habits and last-choice reference are procedural, NOT autobiography.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS procedures (
                cue TEXT NOT NULL, strategy TEXT NOT NULL,
                successes INTEGER NOT NULL, failures INTEGER NOT NULL,
                PRIMARY KEY (cue, strategy))""")
            db.execute("""CREATE TABLE IF NOT EXISTS receipts (
                source_receipt TEXT PRIMARY KEY, result_json TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS continuity (
                slot TEXT PRIMARY KEY, value TEXT NOT NULL)""")

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.execute("PRAGMA busy_timeout=10000")
        try:
            with db:
                yield db
        finally:
            db.close()

    def habit(self, cue: str, strategy: str) -> tuple[int, int]:
        with self._db() as db:
            row = db.execute("SELECT successes,failures FROM procedures WHERE cue=? AND strategy=?",
                             (cue, strategy)).fetchone()
            return (row[0], row[1]) if row else (0, 0)

    def choose(self, frame: DecisionFrame, options: list[Opportunity] | tuple[Opportunity, ...],
               *, learn_enabled: bool = True, inertia_enabled: bool = True,
               native_enabled: bool = True, commit: bool = False) -> Decision:
        if not isinstance(frame, DecisionFrame) or not isinstance(options, (list, tuple)):
            raise TypeError("DecisionFrame and explicit perceived options required")
        if not frame.first_person.startswith(("I ", "My ")):
            raise ValueError("Only first-person subject frames may enter")
        _identifier(frame.source_event, "source event")
        _identifier(frame.cue, "perceived cue")
        for motive, value in frame.motives.items():
            _identifier(motive, "motive")
            _unit(value, "motive pressure")
        for strategy, value in frame.native_strategy_scores.items():
            _identifier(strategy, "neural strategy")
            _unit(value, "neural contribution")
        if not options:
            raise ValueError("No perceived opportunities")
        if len(options) > 128:
            raise ValueError("Too many opportunities for a bounded decision")
        names: set[str] = set()
        with self._db() as db:
            row = db.execute("SELECT value FROM continuity WHERE slot='last_strategy'").fetchone()
            previous = json.loads(row[0]) if row else None
            # Inertia is local to an ongoing concern, not a global personality trait.
            last = (previous["strategy"] if previous and
                    (previous["cue"] == frame.cue or
                     set(previous["goal_ids"]).intersection(frame.goal_ids)) else None)
        scored: list[tuple[str, str, float]] = []
        for option in options:
            if not isinstance(option, Opportunity):
                raise TypeError("All candidates must be Opportunities")
            for label, value in (("key", option.key), ("domain", option.domain),
                                 ("strategy", option.strategy)):
                _identifier(value, label)
            if option.key in names:
                raise ValueError("Duplicate opportunity key")
            names.add(option.key)
            _unit(option.effort, "effort")
            _unit(option.risk, "risk")
            for key, effect in option.effects.items():
                _identifier(key, "effect motive")
                _unit(effect, "expected effect")
            if not option.perceived:
                continue  # no hidden-object omniscience
            value = sum(frame.motives.get(key, 0.0) * effect
                        for key, effect in option.effects.items())
            value += .55 * min(2, len(frame.goal_ids.intersection(option.goal_ids)))
            value -= .23 * option.effort + .30 * option.risk
            if native_enabled:
                value += .12 * frame.native_strategy_scores.get(option.strategy, 0.0)
            if inertia_enabled and last == option.strategy:
                value += .16  # stability, but a genuine need can override it
            if learn_enabled:
                wins, losses = self.habit(frame.cue, option.strategy)
                # Empirical strategy preference: no practice, no advantage.
                # Bounded on purpose: experience is not a forced rule.
                value += .30 * (wins - losses) / (wins + losses + 4)
            scored.append((option.key, option.strategy, round(value, 8)))
        if not scored:
            raise ValueError("No subject-perceived opportunity")
        scored.sort(key=lambda row: (-row[2], row[0]))
        winner = scored[0]
        if commit:
            # Reference-only continuity; existing Doctor owns life goals.
            with self._db() as db:
                db.execute("INSERT OR REPLACE INTO continuity(slot,value) VALUES('last_strategy',?)",
                           (json.dumps({"strategy": winner[1], "cue": frame.cue,
                                        "goal_ids": sorted(frame.goal_ids)}),))
        return Decision(winner[0], winner[1], winner[2],
                        tuple((key, score) for key, _, score in scored))

    def record_outcome(self, *, source_receipt: str, action_key: str, cue: str,
                       strategy: str, succeeded: bool,
                       verify_receipt: Callable[[str, str, bool], bool]) -> bool:
        """Apply exactly one actual outcome after independent world verification.

        verify_receipt MUST validate trusted source provenance + action binding.
        This is not an independent cryptographic verifier or evidence admission.
        """
        for label, value in (("source_receipt", source_receipt), ("action_key", action_key),
                             ("cue", cue), ("strategy", strategy)):
            _identifier(value, label)
        if type(succeeded) is not bool or not callable(verify_receipt):
            raise TypeError("Boolean outcome and trusted verifier required")
        if verify_receipt(source_receipt, action_key, succeeded) is not True:
            raise PermissionError("Unverified outcome cannot train a procedure")
        payload = json.dumps([action_key, cue, strategy, succeeded], separators=(",", ":"))
        with self._db() as db:
            row = db.execute("SELECT result_json FROM receipts WHERE source_receipt=?",
                             (source_receipt,)).fetchone()
            if row:
                if row[0] != payload:
                    raise RuntimeError("Receipt replay attempts to rewrite an outcome")
                return False
            db.execute("INSERT INTO receipts VALUES (?,?)", (source_receipt, payload))
            db.execute("""INSERT INTO procedures(cue,strategy,successes,failures)
                VALUES(?,?,?,?) ON CONFLICT(cue,strategy) DO UPDATE SET
                successes=successes+excluded.successes,
                failures=failures+excluded.failures""",
                (cue, strategy, int(succeeded), int(not succeeded)))
        return True
