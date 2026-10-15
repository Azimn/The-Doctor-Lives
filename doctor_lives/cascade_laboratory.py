"""Bounded source-memory -> physical action loop in the existing Laboratory.

An explicit task policy, not a learned planner or a new identity authority.
Only locally offered sightings admitted to Doctor memory guide shelf order.
World receipts are verified by the Laboratory; current location is never
inferred from an old sighting. No renderer participates in action selection.
"""
from __future__ import annotations

import json
import re
import sqlite3
from uuid import uuid4

from .cascade_background import operation_lock
from .cascade_governance import snapshot_doctor

SHELVES = tuple(f"station:shelf:{i}" for i in (1, 2, 3))


def _volume(book_id):
    if not isinstance(book_id, str) or not re.fullmatch(r"book:[0-9]{3}", book_id):
        raise ValueError("Only stable Laboratory book identities are supported")
    return f"research volume {int(book_id.split(':')[1])}"


def _percept(book_id, station):
    return f"I see {_volume(book_id)} on shelf {station.rsplit(':', 1)[1]}."


def _verified_looks(port):
    port.verify()
    # Engineer-side provenance lookup only. This history is not a subject
    # knowledge store: selection below requires a matching ACTIVE Doctor memory.
    with port.habitat._open() as db:
        return [(json.loads(e), h) for e, h in db.execute(
            "SELECT envelope,event_hash FROM embodied_events ORDER BY revision DESC")
                if json.loads(e)["kind"] == "look"]


def remember_look(host, port, receipt):
    """Admit only an authentic local offer, never a caller-asserted sighting."""
    verified = next(((e, h) for e, h in _verified_looks(port)
                     if e["event_id"] == receipt.get("event_id")), None)
    if verified is None:
        raise PermissionError("Unknown Laboratory observation")
    event, event_hash = verified
    if (receipt.get("event_hash") != event_hash
            or receipt.get("offered_payload") != event["offered_payload"]
            or receipt.get("station") != event["after_station"]):
        raise PermissionError("Altered Laboratory observation")
    station = event["after_station"]
    if station not in SHELVES:
        return []
    admitted = []
    present = {x["object_id"] for x in event["offered_payload"]["nearby_objects"]}
    # An actual failed local search can revise the prior on a later task.
    for memory in host._doctor.brain.store.memories():
        match = re.fullmatch(r"I see research volume ([0-9]+) on shelf ([123])\.", memory["text"])
        if match and station.endswith(":" + match[2]):
            book = f"book:{int(match[1]):03d}"
            if book not in present:
                source = f"laboratory-look:{event_hash}:{book}"
                if not any(m["source"] == source for m in host._doctor.brain.store.memories(False)):
                    result = host._doctor.ingest({
                        "channel": "world", "percept": _percept(book, station).replace("I see", "I no longer see"),
                        "source": source, "kind": "observation"})
                    admitted.append(result["memory_id"])
    for item in event["offered_payload"]["nearby_objects"]:
        book_id = item["object_id"]
        if not re.fullmatch(r"book:[0-9]{3}", book_id):
            continue
        source = f"laboratory-look:{event_hash}:{book_id}"
        existing = next((m for m in host._doctor.brain.store.memories(False)
                         if m["source"] == source), None)
        if existing:
            # An archived event is not silently reactivated by receipt replay.
            admitted.append(existing["id"])
            continue
        result = host._doctor.ingest({
            "channel": "world", "percept": _percept(book_id, station),
            "source": source, "kind": "observation", "novelty": .35,
        })
        admitted.append(result["memory_id"])
    return admitted


def remembered_shelf(host, port, book_id):
    """Latest authentic sighting with an active, matching lived memory.

    Sorting uses source chronology, not lexical wording or rehearsal recency.
    A sighting is a search prior, never a claim of present object location.
    """
    _volume(book_id)
    memories = {m["source"]: m for m in host._doctor.brain.store.memories()
                if m["evidence_class"] == "lived_runtime_memory"}
    ruled_out = set()
    for event, event_hash in _verified_looks(port):
        station = event["after_station"]
        memory = memories.get(f"laboratory-look:{event_hash}:{book_id}")
        if memory and station in SHELVES and memory["text"] == _percept(book_id, station).replace("I see", "I no longer see"):
            if not any(x["object_id"] == book_id for x in event["offered_payload"]["nearby_objects"]):
                ruled_out.add(station)
        if (station in SHELVES and station not in ruled_out and memory
                and memory["text"] == _percept(book_id, station)
                and any(x["object_id"] == book_id
                        for x in event["offered_payload"]["nearby_objects"])):
            return {"station": station, "memory_id": memory["id"],
                    "source_event_hash": event_hash}
    return None


def run_read_task(host, port, *, task_id, book_id, max_actions, authorized=False):
    """Trusted local host call. Every move/look/open/read consumes one action.

    Authority is per task invocation. No background actions are authorized by
    this API. Interrupted tasks remain blocked for manual reconciliation;
    replay of a completed task returns its old receipt without acting again.
    """
    if type(authorized) is not bool or not authorized:
        raise PermissionError("Explicit host authorization required for Laboratory actions")
    _volume(book_id)
    if (not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", task_id)
            or type(max_actions) is not int or not 1 <= max_actions <= 40):
        raise ValueError("Bounded task ID and integer action budget required")
    with operation_lock(host.state_dir):
        host._cascade_background.assert_reconciled()
        if host.pending_count() or host._journal.active() is not None:
            raise RuntimeError("Complete pending subject delivery before external actions")
        body = port.verify()
        if body["station"] not in (*SHELVES, "station:center", "station:threshold"):
            raise ValueError("Read task currently supports the main room shelf routes only")
        request = {"book_id": book_id, "max_actions": max_actions,
                   "lab_id": body["lab_id"], "world_epoch": body["world_epoch"]}
        path = host.state_dir / "cascade-laboratory.sqlite3"
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, request TEXT, status TEXT, report TEXT)")
            previous = db.execute("SELECT request,status,report FROM tasks WHERE id=?", (task_id,)).fetchone()
            if previous:
                if json.loads(previous[0]) != request:
                    raise PermissionError("Task ID cannot be reused for another request")
                if previous[1] != "complete":
                    raise RuntimeError("Interrupted Laboratory task requires manual reconciliation")
                return json.loads(previous[2])
            if db.execute("SELECT 1 FROM tasks WHERE status!='complete'").fetchone():
                raise RuntimeError("Unresolved Laboratory operation blocks new actions")
            hint = remembered_shelf(host, port, book_id)
            order = ([hint["station"]] if hint else []) + [
                s for s in SHELVES if not hint or s != hint["station"]]
            report = {"schema": "cascade.laboratory-read.v1", "task_id": task_id,
                      "request": request, "before_digest": snapshot_doctor(host).state_digest,
                      "policy": "verified-memory-first-then-local-search",
                      "memory_hint": hint, "shelf_order": order, "actions": [],
                      "success": False, "page_text": None,
                      "scope": "engineering_task_policy_not_34_article_qualification"}
            db.execute("INSERT INTO tasks VALUES (?,?,?,?)", (
                task_id, json.dumps(request), "running", json.dumps(report)))
            db.commit()

            def act(kind, argument=None):
                if len(report["actions"]) >= max_actions:
                    return None
                # Commit the decision and consume budget BEFORE the tool call.
                action = {"kind": kind, "argument": argument,
                          "event_id": str(uuid4()), "status": "reserved"}
                report["actions"].append(action)
                save()
                if kind == "move":
                    receipt = port.move(argument, event_id=action["event_id"])
                elif kind == "look":
                    receipt = port.look(event_id=action["event_id"])
                    remember_look(host, port, receipt)
                else:
                    receipt = port.book(book_id, kind, event_id=action["event_id"])
                action.update(status="executed", receipt=receipt)
                save()
                return receipt

            def save(status="running"):
                db.execute("UPDATE tasks SET status=?,report=? WHERE id=?",
                           (status, json.dumps(report), task_id))
                db.commit()

            try:
                for station in order:
                    current = port.verify()["station"]
                    if current != station:
                        if current != "station:center":
                            if act("move", "station:center") is None:
                                break
                        if act("move", station) is None:
                            break
                    view = act("look")
                    if view is None:
                        break
                    if not any(x["object_id"] == book_id for x in view["offered_payload"]["nearby_objects"]):
                        continue
                    if act("open") is None:
                        break
                    page = act("read")
                    if page is None:
                        break
                    from pretorius_lab.book_library import BookLibrary
                    from pretorius_lab.physics import digest
                    BookLibrary(port.habitat).verify()
                    with port.habitat._open() as world:
                        row = world.execute("SELECT payload,event_hash FROM books_events WHERE event_id=?",
                                            (page["delivery_event_id"],)).fetchone()
                    event = json.loads(row[0])
                    if (event["page_receipt"]["page_digest"] != digest(page["page_text"])
                            or event["book_id"] != book_id):
                        raise RuntimeError("Read offer fails source receipt verification")
                    # Same first-person firewall used by other chassis ingress.
                    outcome = host._doctor.ingest({
                        "channel": "tool", "percept": page["page_text"],
                        "source": "laboratory-read:" + row[1], "kind": "tool_result"})
                    report.update(success=True, page_text=page["page_text"],
                                  outcome_memory_id=outcome["memory_id"],
                                  read_event_hash=row[1])
                    break
                report["after_digest"] = snapshot_doctor(host).state_digest
                report["actions_used"] = len(report["actions"])
                port.verify()
                save("complete")
                return report
            except BaseException:
                save("interrupted")
                raise
