"""Small Sims-inspired motive pressure, physical affordances and durable action queue.

Opt-in ENGINEER/HOST layer over the *existing* Doctor and Laboratory.
The real Doctor alone owns identity, memory and recurrent policy. His native
tendencies contribute bounded preference; bodily needs and material constraints
alter executable priorities. No raw numeric state enters first-person ingress.

This is NOT proof the Doctor autonomously devised a plan. A host must explicitly
authorize starting, stepping, pausing and resuming each bounded activity.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import re
import sqlite3

from .home_choice_probe import NATIVE_TO_TASK, _shortest_route
from .lab_home_bridge import DoctorHomeBridge, _hash, _ACTION_DOMAINS

SCHEMA = "pretorius-home-motive-queue.v0.1"
TASKS = ("experiment", "repair", "rest", "tea", "meal", "clean")
STATIONS = {
    "experiment": "station:bench",
    "repair": "station:bench",
    "rest": "station:bedroom",
    "tea": "station:kitchen",
    "meal": "station:kitchen",
    "clean": "station:bench",
}
ACTIONS = {
    "experiment": ("experiment",),
    "repair": ("repair",),
    "rest": ("sleep",),
    "tea": ("brew_tea",),
    "meal": ("prepare_meal", "eat"),
    "clean": ("clean",),
}
_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,39}\Z")


def motive_scores(state: dict, native: dict[str, float] | None = None,
                  *, body_enabled: bool = True) -> dict:
    """Frozen utility calculation; values never appear in the subject frame.

    These numbers are intentionally simple. The unmodified neural policy
    supplies an optional SMALL preference, not a substitute executor.
    A hard affordance gate vetoes actions unavailable in the world.
    """
    from pretorius_lab.daily_rhythm import _can_see
    from pretorius_lab.embodied_access import STATIONS as ROOM_STATIONS
    if not isinstance(state, dict):
        raise TypeError("Trusted domestic environment state is required")
    native = native or {}
    if set(native) - set(NATIVE_TO_TASK):
        raise ValueError("Unknown recurrent action key")
    if any(type(v) not in (int, float) or not 0 <= v <= 1
           for v in native.values()):
        raise ValueError("Invalid bounded recurrent distribution")
    fatigue, thirst, hunger = (state[k] for k in ("fatigue", "thirst", "hunger"))
    wear, clutter = state["apparatus"], state["cleanliness"]["room:sanctum"]
    supply = state["supplies"]
    raw = {
        "experiment": 1.05 - (0.12 if fatigue >= 5 else 0),
        "repair": .15 + .25 * (3 - wear) + (1.00 if wear <= 1 else 0),
        "rest": .15 + .18 * fatigue + (1.30 if fatigue >= 7 else 0),
        "tea": .15 + .17 * thirst + (.65 if thirst >= 6 else 0),
        "meal": .10 + .13 * hunger + (.50 if hunger >= 7 else 0),
        "clean": .12 + .25 * clutter + (.70 if clutter >= 3 else 0),
    }
    # The fixed mapping stays explicit and is never retrofitted per test case.
    native_bias = {task: sum(.12 * score for action, score in native.items()
                             if NATIVE_TO_TASK[action] == task)
                   for task in TASKS}
    feasible = {
        "experiment": wear > 0 and supply["reagents"] > 0 and
                     fatigue < 7 and thirst < 8 and clutter < 3,
        "repair": wear < 3 and supply["spares"] > 0 and fatigue < 8,
        "rest": True,
        "tea": all(supply[x] > 0 for x in ("tea", "water", "fuel")) and fatigue < 9,
        "meal": (state["meal_ready"] or all(
            supply[x] > 0 for x in ("water", "fuel", "rations")
        )) and fatigue < 9 and state["cleanliness"]["room:kitchen"] < 3,
        "clean": clutter > 0 and fatigue < 9,
    }
    for task in TASKS:
        room = ROOM_STATIONS[STATIONS[task]][0]
        if task != "rest" and not _can_see(state, room) and supply["oil"] <= 0:
            feasible[task] = False
    scores = {
        task: round(raw[task] + native_bias[task] if body_enabled else
                    .90 + native_bias[task] + (.3 if task == "experiment" else 0), 6)
        for task in TASKS
    }
    # Physical feasibility applies even to the body-lesioned policy: it
    # cannot conjure fuel, repairs or access to an invisible workbench.
    eligible = [(scores[t], t) for t in TASKS if feasible[t]]
    if not eligible:
        raise RuntimeError("No household action is physically available")
    chosen = sorted(eligible, key=lambda pair: (-pair[0], TASKS.index(pair[1])))[0][1]
    return {"task": chosen, "scores": scores, "eligible": feasible,
            "native_bias": native_bias, "body_enabled": body_enabled}


def plan_steps(state: dict, station: str, task: str) -> list:
    """Visible object affordances become a bounded physical action sequence."""
    from pretorius_lab.daily_rhythm import _can_see
    from pretorius_lab.embodied_access import STATIONS as ROOM_STATIONS
    if task not in TASKS:
        raise ValueError("Unknown household task")
    target = STATIONS[task]
    steps = [{"op": "walk", "args": {"station": p}}
             for p in _shortest_route(station, target)]
    room = ROOM_STATIONS[target][0]
    if task != "rest" and not _can_see(state, room):
        if state["supplies"]["oil"] <= 0:
            raise RuntimeError("A dark room has no usable lamp oil")
        steps.append({"op": "light", "args": {}})
    ops = ACTIONS[task]
    if task == "meal" and state["meal_ready"]:
        ops = ("eat",)
    steps.extend({"op": op, "args": {}} for op in ops)
    if len(steps) > 12:
        raise RuntimeError("Household plan exceeds twelve permitted actions")
    return steps


def _open(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, isolation_level=None, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("""CREATE TABLE IF NOT EXISTS activity_plans (
        plan_id TEXT PRIMARY KEY, world_epoch TEXT NOT NULL,
        status TEXT NOT NULL, task TEXT NOT NULL,
        choices_json TEXT NOT NULL, steps_json TEXT NOT NULL,
        next_index INTEGER NOT NULL, receipts_json TEXT NOT NULL,
        expected_stamp TEXT NOT NULL, pause_reason TEXT,
        seen_source TEXT NOT NULL)""")
    return db


class HomeActivityQueue:
    """Exactly one queued activity at a time; never an independent brain."""

    def __init__(self, bridge: DoctorHomeBridge, path: str | Path):
        if not isinstance(bridge, DoctorHomeBridge):
            raise TypeError("Existing real DoctorHomeBridge required")
        self.bridge = bridge
        self.path = Path(path)
        with _open(self.path):
            pass

    def _stamp(self):
        self.bridge.subject.verify()
        with self.bridge.world._open() as db:
            return self.bridge._physical_stamp(db)

    @staticmethod
    def _load(row):
        return {
            "plan_id": row["plan_id"], "world_epoch": row["world_epoch"],
            "status": row["status"], "task": row["task"],
            "choices": json.loads(row["choices_json"]),
            "steps": json.loads(row["steps_json"]),
            "next_index": row["next_index"],
            "receipts": json.loads(row["receipts_json"]),
            "expected_stamp": row["expected_stamp"],
            "pause_reason": row["pause_reason"],
            "seen_source": row["seen_source"],
        }

    def inspect(self, plan_id):
        """Engineer-only! Never send plan receipts or utility numbers to subject."""
        with _open(self.path) as db:
            row = db.execute("SELECT * FROM activity_plans WHERE plan_id=?",
                             (plan_id,)).fetchone()
            return self._load(row) if row else None

    def start(self, plan_id: str, *, body_enabled=True):
        if not isinstance(plan_id, str) or not _ID.fullmatch(plan_id):
            raise ValueError("Stable bounded plan identifier required")
        if type(body_enabled) is not bool:
            raise TypeError("Ablation toggle must be boolean")
        existing = self.inspect(plan_id)
        if existing is not None:
            if existing["choices"]["body_enabled"] != body_enabled:
                raise RuntimeError("Cannot reuse a plan ID with different control settings")
            return existing
        observed = self.bridge.observe()
        frame = observed["subject"]["inner"]
        if not frame.startswith(("I ", "My ")):
            raise RuntimeError("Source-verified first-person perception required")
        state = self.bridge.subject.rhythm.audit_state()
        native = self.bridge.request_cognition(trigger="home_motive_decision")
        policy = motive_scores(state, native["action_scores"],
                               body_enabled=body_enabled)
        station = self.bridge.subject.embodied.verify()["station"]
        steps = plan_steps(state, station, policy["task"])
        stamp = self._stamp()
        epoch = self.bridge.subject.verify()["world_epoch"]
        choices = {**policy, "native_selected": native["selected_action"],
                   "native_policy_id": native["policy_decision_id"],
                   "frame_sha256": _hash(frame)}
        with _open(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("""SELECT 1 FROM activity_plans
                WHERE status IN ('active','paused')""").fetchone():
                raise RuntimeError("An existing plan must be completed or cancelled")
            db.execute("""INSERT INTO activity_plans VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                       (plan_id, epoch, "active", policy["task"],
                        json.dumps(choices, sort_keys=True),
                        json.dumps(steps, sort_keys=True),
                        0, "[]", stamp, None, observed["memory_id"]))
        return self.inspect(plan_id)

    def _pause(self, db, plan_id, reason):
        db.execute("""UPDATE activity_plans SET status='paused',
                      pause_reason=? WHERE plan_id=?""", (reason, plan_id))
        return {"status": "paused", "reason": reason, "subject": None}

    def step(self, plan_id: str):
        """One bounded physical action; movement or speech can interrupt it.

        Any crash after a physical write but before queue advancement
        fails closed on restart because the world stamp changed. A future
        reconciliation mechanism may safely resume that same event ID only
        after proving no intervening unrelated world events.
        """
        with _open(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM activity_plans WHERE plan_id=?",
                             (plan_id,)).fetchone()
            if row is None:
                raise KeyError(plan_id)
            p = self._load(row)
            if p["status"] != "active":
                return {"status": p["status"], "subject": None,
                        "next_index": p["next_index"]}
            if self.bridge.subject.verify()["world_epoch"] != p["world_epoch"]:
                return self._pause(db, plan_id, "different_world")
            if self._stamp() != p["expected_stamp"]:
                return self._pause(db, plan_id, "world_interrupted")
            index = p["next_index"]
            if index >= len(p["steps"]):
                raise RuntimeError("Inconsistent active plan cursor")
            step = p["steps"][index]
            eid = f"motive-{plan_id}-{index + 1}"
            if len(eid) > 80:
                raise RuntimeError("Action ID out of permitted Laboratory range")
            # The plan remains active until the durable action receipt exists.
            # A crash here can be retried with this *exact* action identity.
            outcome = self.bridge.act(step["op"], event_id=eid, **step["args"])
            with self.bridge.world._open() as world:
                e = world.execute(
                    "SELECT event_hash FROM " + _ACTION_DOMAINS[step["op"]] +
                    " WHERE event_id=?", (eid,)).fetchone()
                if e is None:
                    raise RuntimeError("World action has no durable receipt")
                receipt = e[0]
            receipts = p["receipts"] + [receipt]
            done = index + 1 == len(p["steps"])
            db.execute("""UPDATE activity_plans
                      SET status=?, next_index=?, receipts_json=?,
                          expected_stamp=?, pause_reason=NULL
                      WHERE plan_id=?""",
                       ("completed" if done else "active", index + 1,
                        json.dumps(receipts), self._stamp(), plan_id))
            return {"status": "completed" if done else "active",
                    "task": p["task"], "next_index": index + 1,
                    "subject": outcome["subject"]}

    def pause(self, plan_id: str):
        with _open(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM activity_plans WHERE plan_id=?",
                             (plan_id,)).fetchone()
            if row is None or row["status"] != "active":
                raise RuntimeError("Only an active task may be interrupted")
            return self._pause(db, plan_id, "host_interruption")

    def resume(self, plan_id: str):
        with _open(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM activity_plans WHERE plan_id=?",
                             (plan_id,)).fetchone()
            if row is None or row["status"] != "paused":
                raise RuntimeError("Only a paused plan may resume")
            if (self.bridge.subject.verify()["world_epoch"] != row["world_epoch"] or
                    self._stamp() != row["expected_stamp"]):
                raise RuntimeError("World has changed; explicitly abandon/replan")
            db.execute("""UPDATE activity_plans SET status='active',
                          pause_reason=NULL WHERE plan_id=?""", (plan_id,))
        return self.inspect(plan_id)

    def cancel(self, plan_id: str):
        with _open(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status FROM activity_plans WHERE plan_id=?",
                             (plan_id,)).fetchone()
            if row is None or row["status"] not in ("active", "paused"):
                raise RuntimeError("No unfinished plan to cancel")
            db.execute("UPDATE activity_plans SET status='cancelled' WHERE plan_id=?",
                       (plan_id,))

    def verify(self, plan_id: str):
        """Replay receipt trail against fully verified Laboratory event history."""
        world = self.bridge.subject.verify()
        p = self.inspect(plan_id)
        if p is None:
            raise KeyError(plan_id)
        if world["world_epoch"] != p["world_epoch"]:
            raise RuntimeError("Plan event history belongs to a different world")
        if p["next_index"] != len(p["receipts"]) or not (
                0 <= p["next_index"] <= len(p["steps"])):
            raise RuntimeError("Activity cursor and world receipts disagree")
        with self.bridge.world._open() as db:
            for n, receipt in enumerate(p["receipts"]):
                step = p["steps"][n]
                eid = f"motive-{plan_id}-{n + 1}"
                row = db.execute(
                    "SELECT event_hash FROM " + _ACTION_DOMAINS[step["op"]] +
                    " WHERE event_id=?", (eid,)).fetchone()
                if row is None or row[0] != receipt:
                    raise RuntimeError("Activity receipt not supported by physical world")
        return {"verified": True, "status": p["status"],
                "source_receipts": len(p["receipts"]),
                "task": p["task"], "all_world_events_verified": True}
