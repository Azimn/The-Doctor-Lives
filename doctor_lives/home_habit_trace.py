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
        """No free-standing fabricated successes; rebind to full physical chain."""
        proof = self.bridge.subject.verify()
        verified = 0
        with _db(self.path) as db:
            rows = db.execute(
                "SELECT world_epoch,source_hash,event_id,cue,task,before_sha,after_sha "
                "FROM practiced_actions ORDER BY id").fetchall()
        with self.bridge.world._open() as world:
            for epoch, h, event_id, cue, task, prior, after in rows:
                row = world.execute(
                    "SELECT envelope,event_hash FROM rhythm_events WHERE event_id=?",
                    (event_id,)).fetchone()
                if row is None or row[1] != h:
                    raise ValueError("Habit evidence has no real world event")
                event = json.loads(row[0])
                if (epoch != proof["world_epoch"] or _hash(event) != h
                        or event.get("op") != OPS.get(task)
                        or event.get("args") != {}
                        or event.get("station") != "station:kitchen"
                        or event.get("before_digest") != prior
                        or event.get("after_digest") != after
                        or cue not in CUES):
                    raise ValueError("Persisted habit does not match actual source receipt")
                # Real Doctor must have accepted the same actual experience.
                if not any(m["source"] == "laboratory-home:action:" + h
                           for m in self.bridge.doctor.brain.store.memories(False)):
                    raise ValueError("Habit has no corresponding Doctor lived observation")
                verified += 1
        return {"rules": RULES, "verified": True, "verified_practices": verified}
