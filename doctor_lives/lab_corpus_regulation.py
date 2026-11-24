"""Corpus-to-canonical-need coupling for the actual Laboratory runtime.

The world remains the sole physical authority. This is a one-way regulatory
projection into the existing BrainStore fatigue need, not a second body,
a personal memory, or a new selector. The operator's verified snapshot
stays below the first-person boundary. No renderer receives the numbers.
"""
from __future__ import annotations

import json

from .lab_home_bridge import DoctorHomeBridge, _hash
from .store import clamp

KEY = "lab_corpus_fatigue_projection_v1"


def reconcile_fatigue(bridge: DoctorHomeBridge, observation_id: str) -> bool:
    """Consume a fresh, source-bound bodily snapshot once per physical change.

    The host holds both canonical leases. A new room or LOOK receipt alone
    cannot count as elapsed exertion. Repeated identical physiological state
    does not repeatedly smooth the felt state or advance the cognitive clock.
    A later actual change can update the same existing need transactionally.
    """
    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("Canonical Laboratory bridge required")
    brain = bridge.doctor.brain
    store = brain.store
    proof = bridge.subject.verify()
    station = bridge.subject.embodied.verify()["station"]
    with bridge.world._open() as world_db:
        stamp = bridge._physical_stamp(world_db)
        raw = world_db.execute(
            "SELECT value FROM rhythm_meta WHERE key='state'"
        ).fetchone()
    if raw is None:
        raise RuntimeError("Missing original body state")
    physical = json.loads(raw[0])
    fatigue = physical.get("fatigue")
    minute = physical.get("minute")
    if (type(fatigue) is not int or not 0 <= fatigue <= 10
            or type(minute) is not int or minute != proof["minute"]):
        raise RuntimeError("Invalid original rhythm state")
    if bridge.subject.verify() != proof:
        raise RuntimeError("World changed during bodily projection")
    memory = store.get_memory(observation_id)
    if (memory is None or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or memory["source"] != "laboratory-home:observe:" + _hash({
                "epoch": proof["world_epoch"], "station": station,
                "state": stamp, "text": memory["text"],
            })):
        raise PermissionError("Bodily projection requires current admitted perception")
    # Engineering mapping, not a human calibration: 0-10 physical fatigue
    # maps monotonically onto the canonical need's existing .05-.95 bounds.
    target = 0.05 + 0.09 * fatigue
    snapshot = {
        "world_epoch": proof["world_epoch"], "minute": minute,
        "physical_fatigue": fatigue,
    }
    with store.transaction() as db:
        prior_row = db.execute("SELECT value FROM meta WHERE key=?", (KEY,)).fetchone()
        if prior_row:
            prior = json.loads(prior_row[0])
            if prior["world_epoch"] != snapshot["world_epoch"]:
                raise PermissionError("Body projection belongs to another world epoch")
            if prior["minute"] > minute:
                raise PermissionError("Body projection cannot go backwards in physical time")
            if all(prior[k] == v for k, v in snapshot.items()):
                return False
        need = db.execute("SELECT actual,felt FROM needs WHERE key='fatigue'").fetchone()
        if need is None:
            raise RuntimeError("Canonical fatigue regulation is missing")
        felt = clamp(float(need["felt"]) + 0.65 * (target - float(need["felt"])),
                     0.05, 0.95)
        db.execute("UPDATE needs SET actual=?,felt=?,last_tick=? WHERE key='fatigue'",
                   (target, felt, store.tick))
        store.set_meta(KEY, json.dumps({**snapshot,
            "observation_id": observation_id, "schema": KEY}, sort_keys=True), db)
        store.bump_state_version(db)
    return True
