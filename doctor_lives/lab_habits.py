"""Original Article 8 contextual habits, adapted to the single live BrainStore.

Source: e398cc10ddf7404d83589251d7ceec12e27c782d, home_habit_trace.py.
Reuse its context, material gain and minimum-practice rule. Do not create
the historical experimental habit database in product mode. Learn from
the canonical character's own admitted consequences, whether independently
chosen or coached. Source metadata remains engineer-side; Noesis receives
a bounded preference over currently feasible options, not a motor grant.
"""
from __future__ import annotations

import json
from contextlib import closing

from .home_habit_trace import OPS, REVERSE, MIN_PRACTICE, kitchen_cue, _material_gain
from .lab_home_bridge import DoctorHomeBridge, _hash, _row

WEIGHT = 0.025


def verified_habit_pressure(brain, bridge, observation_id, feasible_actions):
    if type(bridge) is not DoctorHomeBridge or bridge.doctor.brain is not brain:
        raise PermissionError("Actual same-brain Laboratory bridge required")
    scores = {action: 0.0 for action in feasible_actions}
    counts = {task: 0 for task in OPS}
    ids = []
    if not set(feasible_actions).intersection(REVERSE):
        return scores, ids, counts
    proof = bridge.subject.verify()
    station = bridge.subject.embodied.verify()["station"]
    if station != "station:kitchen":
        return scores, ids, counts
    store = brain.store
    memory = store.get_memory(observation_id)
    with bridge.world._open() as world:
        stamp = bridge._physical_stamp(world)
        current = bridge.subject.rhythm.audit_state()
        if (memory is None or not memory["active"] or memory["external"]
                or memory["evidence_class"] != "lived_runtime_memory"
                or not memory["text"].startswith("I am in my kitchen. ")
                or memory["source"] != "laboratory-home:observe:" + _hash({
                    "epoch": proof["world_epoch"], "station": station,
                    "state": stamp, "text": memory["text"]})):
            raise PermissionError("Current admitted kitchen perception required")
        try:
            cue = kitchen_cue(current, station)
        except ValueError:
            return scores, ids, counts
        from pretorius_lab.daily_rhythm import transition
        genesis = world.execute("SELECT value FROM rhythm_meta WHERE key='genesis'").fetchone()
        if genesis is None:
            raise RuntimeError("Original rhythm genesis missing")
        state = json.loads(genesis[0])
        events = world.execute("SELECT event_id FROM rhythm_events ORDER BY revision").fetchall()
        with closing(store.connect()) as db:
            rows = db.execute(
                "SELECT id,source,text FROM memories WHERE active=1 AND external=0 "
                "AND evidence_class='lived_runtime_memory' AND source LIKE 'laboratory-home:action:%'"
            ).fetchall()
        sources = {}
        for row in rows:
            sources.setdefault(row["source"], []).append(row)
        practiced = {task: [] for task in OPS}
        for (eid,) in events:
            event, digest = _row(world, "rhythm_events", eid)
            after, subject = transition(state, event["op"], event["args"], event["station"])
            if (event["world_epoch"] != proof["world_epoch"]
                    or event["before_digest"] != _hash(state)
                    or event["after_digest"] != _hash(after)
                    or event["subject"] != subject):
                raise PermissionError("Original habit source replay mismatch")
            task = REVERSE.get(event["op"])
            if (task is not None and event["station"] == station
                    and event["args"] == {} and _material_gain(task, state, after)):
                try:
                    prior_cue = kitchen_cue(state, station)
                except ValueError:
                    prior_cue = None
                if prior_cue == cue:
                    claims = sources.get("laboratory-home:action:" + digest, [])
                    if len(claims) > 1:
                        raise PermissionError("Ambiguous prior habit experience")
                    if claims:
                        if claims[0]["text"] != event["subject"]["inner"]:
                            raise PermissionError("Habit experience differs from world receipt")
                        practiced[task].append(claims[0]["id"])
            state = after
        if state != current or bridge.subject.verify() != proof:
            raise PermissionError("World changed during habit verification")
    counts = {task: len(practiced[task]) for task in OPS}
    best, other = sorted(OPS, key=lambda task: (-counts[task], task))
    if counts[best] >= MIN_PRACTICE and counts[best] > counts[other] and OPS[best] in scores:
        scores[OPS[best]] = WEIGHT
        ids = practiced[best][-8:]
    return scores, ids, counts
