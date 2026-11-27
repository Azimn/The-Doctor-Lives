"""Native intentions in the existing canonical commitment system.

The native world-bound goal envelope remains the authority. Telos makes that
same goal available to canonical Noesis and Ipseity through the ORIGINAL
commitments table, not a competing goal store. Projection can be repaired
after a cold restart from the authenticated goal; no generic promise API can
close these rows. Completion requires its exact lived physical consequence.
"""
from __future__ import annotations
from contextlib import closing
import re

SOURCE_PREFIX = "telos:native:"
DEFAULT_IMPORTANCE = 0.6  # Existing PretoriusBrain.add_commitment default.


def identity(goal):
    if not re.fullmatch(r"[0-9a-f]{24}", goal["id"]):
        raise PermissionError("Invalid native goal identity")
    if not goal["goal"].startswith("I want to "):
        raise PermissionError("Native goal is not a reviewed first-person intention")
    return ("telos_" + goal["id"],
            SOURCE_PREFIX + goal["origin_policy_id"],
            goal["goal"].removeprefix("I want to ").rstrip("."))


def _verified_completion(chooser, kind, state):
    from .lab_home_bridge import _row
    if kind == "read_book":
        chooser.book._completed_source(state)
        memory_id = state["read_memory_id"]
        event_id, table = "eb_" + state["id"] + "_read", "books_events"
    elif kind == "work":
        # The native work loader verifies situated choice and physical custody.
        memory_id = state["memory_id"]
        event_id, table = "ng_" + state["id"] + "_work", "rhythm_events"
    else:
        memory_id = state["memory_id"]
        event_id, table = "ng_" + state["id"] + "_rest", "rhythm_events"
    memory = chooser.store.get_memory(memory_id)
    if (memory is None or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"):
        raise PermissionError("Telos completion needs the actual active lived consequence")
    with chooser.host.bridge.world._open() as db:
        event, digest = _row(db, table, event_id)
    if (event.get("world_epoch") != state["world_epoch"]
            or memory["source"] != "laboratory-home:action:" + digest):
        raise PermissionError("Telos completion differs from original world receipt")
    if kind == "rest" and (event.get("op") != "rest"
            or event.get("station") != "station:bedroom"
            or event.get("subject", {}).get("inner") != memory["text"]):
        raise PermissionError("Telos rest has no authentic physical completion")
    return memory["text"]


def sync_native_commitments(chooser):
    """Synchronize only validated active slots; archived kept rows are retained.

    Before/after each authorized opportunity, the canonical native loaders
    verify the original origin and any completed source. This is not an
    externally supplied task, and a generic commitment cannot create a goal.
    """
    from .lab_native_goal_choice import NativeLaboratoryGoalChooser
    if type(chooser) is not NativeLaboratoryGoalChooser:
        raise PermissionError("Actual native chooser required")
    states = [("read_book", chooser.book._load()), ("rest", chooser._load_rest())]
    if chooser.work is not None:
        states.append(("work", chooser.work._load()))
    store = chooser.store
    projections = []
    for kind, state in states:
        if state is None:
            continue
        rid, source, description = identity(state)
        status, outcome = "open", None
        if state["phase"] == "complete":
            status, outcome = "kept", _verified_completion(chooser, kind, state)
        elif state["phase"] == "exhausted":
            status, outcome = "released", "Bounded search ended without a feasible volume."
        with closing(store.connect()) as db:
            origin = db.execute("SELECT tick FROM policy_decisions WHERE id=?",
                                (state["origin_policy_id"],)).fetchone()
        if origin is None:
            raise PermissionError("Missing original goal policy")
        projections.append((rid, source, description, int(origin["tick"]), status, outcome))
    with store.transaction() as db:
        changed = False
        for rid, source, description, created, status, outcome in projections:
            row = db.execute("SELECT * FROM commitments WHERE id=?", (rid,)).fetchone()
            if row is None:
                db.execute(
                    "INSERT INTO commitments (id,created_tick,updated_tick,description,"
                    "status,due_tick,importance,actor,source,outcome) VALUES(?,?,?,?,?,NULL,?,NULL,?,?)",
                    (rid, created, store.tick, description, status, DEFAULT_IMPORTANCE, source, outcome),
                )
                changed = True
                continue
            if (row["source"] != source or row["description"] != description
                    or row["created_tick"] != created or row["due_tick"] is not None
                    or row["actor"] is not None or row["importance"] != DEFAULT_IMPORTANCE):
                raise PermissionError("Canonical Telos commitment no longer matches its source")
            if row["status"] == status:
                if row["outcome"] != outcome:
                    raise PermissionError("Telos outcome differs from physical consequence")
                continue
            if row["status"] != "open" or row["outcome"] is not None:
                raise PermissionError("Native commitment cannot be closed or reopened by prose")
            db.execute("UPDATE commitments SET status=?,outcome=?,updated_tick=? WHERE id=?",
                       (status, outcome, store.tick, rid))
            changed = True
        if changed:
            store.bump_state_version(db)
    return tuple(rid for rid, *_ in projections)


def active_persistence(brain, goal):
    """Existing Noesis continuation pressure is now tied to canonical Telos.

    Legacy control paths without a projection retain their original weight.
    No caller can substitute a different commitment for the source goal.
    """
    rid, source, description = identity(goal)
    with closing(brain.store.connect()) as db:
        row = db.execute("SELECT * FROM commitments WHERE id=?", (rid,)).fetchone()
    if row is None:
        return None, DEFAULT_IMPORTANCE
    if (row["source"] != source or row["description"] != description
            or row["status"] != "open" or row["outcome"] is not None
            or row["actor"] is not None or row["due_tick"] is not None
            or row["importance"] != DEFAULT_IMPORTANCE):
        raise PermissionError("Active native intention has invalid Telos projection")
    return rid, float(row["importance"])
