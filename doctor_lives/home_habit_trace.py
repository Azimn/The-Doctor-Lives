"""Opt-in, world-receipt-linked procedural habit trace for Pretorius's home.

This is a bounded HOST-PLANE habit learner, never a second personal identity,
and cannot command Laboratory actions. An accepted source-replayed world
action, its pre-state and its real material effect are the ONLY reinforcement.
No caller-provided reward value is accepted.
"""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from .lab_home_bridge import DoctorHomeBridge, _hash

RULES = "doctor-home-habit-receipts.v0.1"
OPS = {"tea": "brew_tea", "tidy": "clean"}
REVERSE = {v: k for k, v in OPS.items()}
CUES = ("kitchen:morning", "kitchen:afternoon")
MIN_PRACTICE = 2


def _db(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, isolation_level=None, timeout=10)
    con.execute("PRAGMA busy_timeout=10000")
    con.execute("""CREATE TABLE IF NOT EXISTS practiced_actions(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       world_epoch TEXT NOT NULL,
       source_hash TEXT NOT NULL UNIQUE,
       event_id TEXT NOT NULL,
       cue TEXT NOT NULL,
       task TEXT NOT NULL,
       before_sha TEXT NOT NULL,
       after_sha TEXT NOT NULL
    )""")
    return con


def kitchen_cue(state, station):
    if station != "station:kitchen":
        raise ValueError("Habits are only grounded in the actual kitchen")
    m = state["minute"] % 1440
    if 6 * 60 <= m < 12 * 60:
        return "kitchen:morning"
    if 12 * 60 <= m < 18 * 60:
        return "kitchen:afternoon"
    raise ValueError("Outside the registered kitchen dayparts")


def _material_gain(task, before, after):
    if task == "tea":
        return (after["supplies"]["tea"] == before["supplies"]["tea"] - 1
                and after["supplies"]["water"] == before["supplies"]["water"] - 1
                and after["thirst"] < before["thirst"])
    if task == "tidy":
        return (after["chores"] == before["chores"] + 1
                and after["cleanliness"]["room:kitchen"] <
                before["cleanliness"]["room:kitchen"])
    return False


class VerifiedHouseholdHabit:
    """Engineer-only advisory; a real DoctorBrainPort remains the sole brain."""

    def __init__(self, bridge: DoctorHomeBridge, path: str | Path):
        if not isinstance(bridge, DoctorHomeBridge):
            raise TypeError("Existing authenticated DoctorHomeBridge required")
        self.bridge = bridge
        self.path = Path(path)
        with _db(self.path):
            pass

    def _verified_world_event(self, event_id, before):
        if type(event_id) is not str or not event_id:
            raise ValueError("Real stable event_id required")
        proof = self.bridge.subject.verify()
        with self.bridge.world._open() as db:
            row = db.execute(
                "SELECT envelope,event_hash FROM rhythm_events WHERE event_id=?",
                (event_id,),
            ).fetchone()
        if row is None:
            raise ValueError("Cannot learn from a nonexistent action receipt")
        event, event_hash = json.loads(row[0]), row[1]
        after = self.bridge.subject.rhythm.audit_state()
        if (_hash(event) != event_hash or event["world_epoch"] != proof["world_epoch"]
                or event["before_digest"] != _hash(before)
                or event["after_digest"] != _hash(after)
                or event["station"] != "station:kitchen"):
            raise ValueError("Unverified world state or intervening material action")
        claimed = [
            memory for memory in self.bridge.doctor.brain.store.memories(False)
            if memory["source"] == "laboratory-home:action:" + event_hash
        ]
        if len(claimed) != 1:
            raise ValueError("Actual Doctor has not received the action's first-person outcome")
        return event, event_hash, after, proof["world_epoch"]

    def learn(self, *, event_id: str, before: dict):
        """Bind an actual physical successful task to its ACTUAL prior cue."""
        event, h, after, epoch = self._verified_world_event(event_id, before)
        op = event.get("op")
        if op not in REVERSE or event.get("args") != {}:
            raise ValueError("Only actual tea and cleaning outcomes can train these habits")
        task = REVERSE[op]
        if not _material_gain(task, before, after):
            raise ValueError("No independently visible material task outcome")
        cue = kitchen_cue(before, event["station"])
        with _db(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT world_epoch,source_hash,event_id,cue,task,before_sha,after_sha "
                "FROM practiced_actions WHERE source_hash=?", (h,)
            ).fetchone()
            identity = (epoch, h, event_id, cue, task, _hash(before), _hash(after))
            if prior:
                if prior != identity:
                    raise ValueError("World receipt conflicts with recorded practice")
                return {"status": "already_learned", "cue": cue, "task": task}
            # The habit store is bound to one real world, not to purported
            # personal life events imported from parallel simulated subjects.
            worlds = {row[0] for row in db.execute(
                "SELECT DISTINCT world_epoch FROM practiced_actions")}
            if worlds and worlds != {epoch}:
                raise ValueError("Habit trace cannot silently cross different material worlds")
            db.execute(
                "INSERT INTO practiced_actions(world_epoch,source_hash,event_id,cue,"
                "task,before_sha,after_sha) VALUES(?,?,?,?,?,?,?)", identity)
        return {"status": "learned", "cue": cue, "task": task}

    def advise(self, *, state: dict, station: str):
        # Advisory reads must not accept a manipulated local count cache.
        # Validate every claimed reinforcement against the real replayed
        # source events before any learned preference can influence action.
        self.verify()
        # Even the caller's proposed perception context must come from
        # the currently authenticated physical world. No fake "morning"
        # label or stale hidden numeric snapshot may steer this policy.
        if (state != self.bridge.subject.rhythm.audit_state() or
                station != self.bridge.subject.embodied.verify()["station"]):
            raise ValueError("Habit cue does not match the live physical source")
        cue = kitchen_cue(state, station)
        counts = {task: 0 for task in OPS}
        with _db(self.path) as db:
            for task, n in db.execute(
                "SELECT task,COUNT(*) FROM practiced_actions WHERE cue=? GROUP BY task",
                (cue,)):
                if task not in counts:
                    raise ValueError("Unknown persisted procedural action")
                counts[task] = n
        sorted_tasks = sorted(OPS, key=lambda task: (-counts[task], task))
        best, other = sorted_tasks
        chosen = (best if counts[best] >= MIN_PRACTICE
                  and counts[best] > counts[other] else None)
        return {"cue": cue, "advice": chosen,
                "practices": counts, "abstained": chosen is None}

    def verify(self):
        """Reconstruct historical context and result for every habit claim.

        Checking only the event hash is insufficient: it proves that an
        action took place but cannot prove a mutable trace's claimed cue.
        Replay every real rhythm transition and require that the claimed
        daypart, physical success and actual Doctor source match.
        """
        from pretorius_lab.daily_rhythm import transition
        proof = self.bridge.subject.verify()
        with _db(self.path) as db:
            entries = db.execute(
                "SELECT world_epoch,source_hash,event_id,cue,task,before_sha,after_sha "
                "FROM practiced_actions ORDER BY id").fetchall()
        claims = {}
        for entry in entries:
            if entry[2] in claims:
                raise ValueError("An action cannot be claimed twice")
            claims[entry[2]] = entry

        with self.bridge.world._open() as world:
            data = {
                k: json.loads(v) for k, v in world.execute(
                    "SELECT key,value FROM rhythm_meta")
            }
            old = data["genesis"]
            inspected = {}
            for (envelope,) in world.execute(
                "SELECT envelope FROM rhythm_events ORDER BY revision"):
                event = json.loads(envelope)
                after, subject = transition(
                    old, event["op"], event["args"], event["station"])
                if (event["before_digest"] != _hash(old)
                        or event["after_digest"] != _hash(after)
                        or event["subject"] != subject):
                    raise ValueError("Independent historical world replay diverged")
                entry = claims.get(event["event_id"])
                if entry:
                    epoch, h, event_id, cue, task, prior_sha, after_sha = entry
                    if (epoch != proof["world_epoch"]
                            or _hash(event) != h
                            or event["op"] != OPS.get(task)
                            or event["args"] != {}
                            or event["station"] != "station:kitchen"
                            or prior_sha != _hash(old)
                            or after_sha != _hash(after)
                            or kitchen_cue(old, event["station"]) != cue
                            or not _material_gain(task, old, after)):
                        raise ValueError("Learned trace fabricates a cue or physical outcome")
                    inspected[event_id] = h
                old = after
            if len(inspected) != len(entries):
                raise ValueError("Claimed habit event is missing from source world")
        doctor_sources = {
            m["source"] for m in self.bridge.doctor.brain.store.memories(False)
        }
        for source_hash in inspected.values():
            if "laboratory-home:action:" + source_hash not in doctor_sources:
                raise ValueError("Doctor did not receive the observed outcome")
        return {"rules": RULES, "verified": True,
                "verified_practices": len(inspected)}
