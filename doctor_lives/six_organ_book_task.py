"""Source-verified book-search benchmark on the ONE six-organ Pretorius.

Selective adaptation from draft PR #61 at
29adbf6b68b47f1a65e4ff3dab7be97a925a267b.

This is explicitly a HOST-authored bounded search task. Real Laboratory
EmbodiedAccess owns all movement, observation, and book-access receipts.
Doctor BrainStore owns all autobiographical observations. The optional task
SQLite is an engineer-only execution reservation journal (never an organ,
identity, memory, world truth or competing policy). Interrupted tasks fail
closed; the caller reconciles externally. This adapter neither manufactures
endogenous goals nor establishes advantage over an equal-information ledger.
"""
from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3

from .organs import SixOrganRuntime

SHELVES = tuple(f"station:shelf:{i}" for i in (1, 2, 3))
_BOOK = re.compile(r"book:[0-9]{3}\Z")
_TASK = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
_SIGHT = re.compile(r"I see research volume ([0-9]+) on shelf ([123])\.\Z")


def _phrase(book_id: str, station: str) -> str:
    if type(book_id) is not str or not _BOOK.fullmatch(book_id):
        raise ValueError("Invalid bounded book identity")
    if station not in SHELVES:
        raise ValueError("Only real shelf stations are supported")
    return f"I see research volume {int(book_id.split(':')[1])} on shelf {station[-1]}."


def _verified_looks(port):
    port.verify()
    with port.habitat._open() as conn:
        rows = list(conn.execute(
            "SELECT envelope,event_hash FROM embodied_events ORDER BY revision DESC"
        ))
    return [
        (json.loads(raw), digest)
        for raw, digest in rows
        if json.loads(raw).get("kind") == "look"
    ]


class VerifiedBookSearch:
    def __init__(self, runtime: SixOrganRuntime, embodied_port, *,
                 authorized: bool = False):
        if not isinstance(runtime, SixOrganRuntime):
            raise TypeError("Canonical SixOrganRuntime required")
        if authorized is not True:
            raise PermissionError("Explicit host-only Laboratory test authorization required")
        if not hasattr(embodied_port, "habitat") or not hasattr(embodied_port, "look"):
            raise TypeError("Verified real Laboratory embodied port required")
        embodied_port.verify()
        self._runtime = runtime
        self._port = embodied_port
        self._journal_path = runtime._port.brain.state_dir / "research_book_tasks.sqlite3"
        self._journal_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self._journal_path)) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY, request_json TEXT NOT NULL,
                status TEXT NOT NULL, report_json TEXT NOT NULL
            )""")
            conn.commit()

    def admit_sighting(self, receipt: dict) -> tuple[str, ...]:
        """Only an independently stored and verified local LOOK may be lived."""
        if type(receipt) is not dict:
            raise TypeError("Laboratory look receipt required")
        looked = next(
            ((e, h) for e, h in _verified_looks(self._port)
             if e["event_id"] == receipt.get("event_id")),
            None,
        )
        if looked is None:
            raise PermissionError("Unrecognized physical observation")
        event, proof = looked
        if (receipt.get("event_hash") != proof
                or receipt.get("offered_payload") != event["offered_payload"]
                or receipt.get("station") != event["after_station"]):
            raise PermissionError("Altered or stale Laboratory LOOK receipt")
        station = event["after_station"]
        if station not in SHELVES:
            return ()
        present = {
            item["object_id"]
            for item in event["offered_payload"]["nearby_objects"]
        }
        admitted = []
        store = self._runtime._port.brain.store
        # When a previously witnessed item is now missing, that very
        # absence is an independently reobserved first-person experience.
        for memory in store.memories():
            match = _SIGHT.fullmatch(memory["text"])
            if match and station.endswith(":" + match[2]):
                candidate = f"book:{int(match[1]):03d}"
                if candidate not in present:
                    candidate_source = f"lab-book-look:{proof}:{candidate}"
                    past = [m for m in store.memories(False)
                            if m["source"] == candidate_source]
                    if not past:
                        res = self._runtime.sensus.acquire_existing_percept({
                            "channel": "world", "kind": "observation",
                            "percept": _phrase(candidate, station).replace(
                                "I see", "I no longer see"
                            ),
                            "source": candidate_source,
                        }, host_authorized=True)
                        admitted.append(res.memory_id)
        for item in event["offered_payload"]["nearby_objects"]:
            book_id = item["object_id"]
            if not isinstance(book_id, str) or not _BOOK.fullmatch(book_id):
                continue
            source = f"lab-book-look:{proof}:{book_id}"
            existing = [m for m in store.memories(False)
                        if m["source"] == source]
            if existing:
                if len(existing) != 1 or existing[0]["text"] != _phrase(book_id, station):
                    raise RuntimeError("Conflicting repeated source observation")
                admitted.append(existing[0]["id"])
                continue
            result = self._runtime.sensus.acquire_existing_percept({
                "channel": "world", "kind": "observation",
                "percept": _phrase(book_id, station),
                "source": source, "novelty": 0.35,
            }, host_authorized=True)
            admitted.append(result.memory_id)
        return tuple(admitted)

    def memory_hint(self, book_id: str):
        """Past source-qualified observation, NEVER privileged current location."""
        _phrase(book_id, SHELVES[0])
        active = {
            m["source"]: m for m in self._runtime._port.brain.store.memories()
            if m["evidence_class"] == "lived_runtime_memory"
        }
        disconfirmed = set()
        for event, proof in _verified_looks(self._port):
            station = event["after_station"]
            if station not in SHELVES:
                continue
            book_source = f"lab-book-look:{proof}:{book_id}"
            lived = active.get(book_source)
            if lived is None:
                continue
            present = any(
                obj["object_id"] == book_id
                for obj in event["offered_payload"]["nearby_objects"]
            )
            if (not present and lived["text"] ==
                    _phrase(book_id, station).replace("I see", "I no longer see")):
                disconfirmed.add(station)
                continue
            if (present and station not in disconfirmed and
                    lived["text"] == _phrase(book_id, station)):
                return {"station": station, "memory_id": lived["id"],
                        "source_event_hash": proof}
        return None

    def run(self, *, task_id: str, book_id: str, max_actions: int,
            authorized: bool = False, ledger_hint: str | None = None):
        """One host-directed physical task, idempotent completion, fail-closed crash.

        ledger_hint is an explicit engineering A/B baseline. Its caller must
        establish the same previous observational information; it is NOT a
        brain recollection and must never enter model/subject context.
        """
        if authorized is not True:
            raise PermissionError("Individual task requires separate host approval")
        _phrase(book_id, SHELVES[0])
        if (type(task_id) is not str or not _TASK.fullmatch(task_id)
                or type(max_actions) is not int or not 1 <= max_actions <= 40
                or ledger_hint is not None and ledger_hint not in SHELVES):
            raise ValueError("Bounded task, budget and ledger comparator required")
        world = self._port.verify()
        if world["station"] not in (*SHELVES, "station:center", "station:threshold"):
            raise ValueError("Task supports real main Laboratory shelves only")
        request = {
            "book_id": book_id, "max_actions": max_actions,
            "lab_id": world["lab_id"], "world_epoch": world["world_epoch"],
            "ledger_hint": ledger_hint,
        }
        with closing(sqlite3.connect(
            self._journal_path, isolation_level=None, timeout=15
        )) as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT request_json,status,report_json FROM tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if existing:
                if json.loads(existing[0]) != request:
                    raise PermissionError("Task ID cannot be reused for a changed request")
                if existing[1] != "complete":
                    raise RuntimeError("Interrupted task requires human reconciliation")
                return json.loads(existing[2])
            if db.execute("SELECT 1 FROM tasks WHERE status!='complete'").fetchone():
                raise RuntimeError("An interrupted task blocks new task execution")
            # In the experimental baseline arm the ledger provides a prior
            # location to the very same host execution policy.
            hint = self.memory_hint(book_id) if ledger_hint is None else None
            first = ledger_hint or (hint["station"] if hint else None)
            order = ([first] if first else []) + [
                s for s in SHELVES if s != first
            ]
            result = {
                "schema": "doctor.six-organ-book-task.v1",
                "request": request, "memory_hint": hint,
                "shelf_order": order, "actions": [], "success": False,
                "page_text": None, "outcome_memory_id": None,
                "scope": "host-directed-not-endogenous-goal-or-better-cognition",
            }
            def save(state="running"):
                db.execute(
                    "UPDATE tasks SET status=?,report_json=? WHERE task_id=?",
                    (state, json.dumps(result, sort_keys=True), task_id),
                )
                db.commit()
            db.execute(
                "INSERT INTO tasks VALUES (?,?,?,?)",
                (task_id, json.dumps(request, sort_keys=True), "running",
                 json.dumps(result, sort_keys=True)),
            )
            db.commit()
            def action(kind, argument=None):
                if len(result["actions"]) >= max_actions:
                    return None
                event_id = f"{task_id}_{len(result['actions'])}"
                reserved = {
                    "kind": kind, "argument": argument,
                    "event_id": event_id, "status": "reserved",
                }
                result["actions"].append(reserved)
                save()
                if kind == "move":
                    proof = self._port.move(argument, event_id=event_id)
                elif kind == "look":
                    proof = self._port.look(event_id=event_id)
                    self.admit_sighting(proof)
                else:
                    proof = self._port.book(book_id, kind, event_id=event_id)
                reserved.update(status="executed", receipt=proof)
                save()
                return proof

            try:
                for station in order:
                    current = self._port.verify()["station"]
                    if current != station:
                        if current != "station:center":
                            if action("move", "station:center") is None:
                                break
                        if action("move", station) is None:
                            break
                    looked = action("look")
                    if looked is None:
                        break
                    if not any(
                        item["object_id"] == book_id
                        for item in looked["offered_payload"]["nearby_objects"]
                    ):
                        continue
                    if action("open") is None:
                        break
                    page = action("read")
                    if page is None:
                        break
                    from pretorius_lab.book_library import BookLibrary
                    from pretorius_lab.physics import digest
                    BookLibrary(self._port.habitat).verify()
                    with self._port.habitat._open() as world_db:
                        read_row = world_db.execute(
                            "SELECT payload,event_hash FROM books_events "
                            "WHERE event_id=?",
                            (page["delivery_event_id"],),
                        ).fetchone()
                    if not read_row:
                        raise RuntimeError("Missing source book receipt")
                    source = json.loads(read_row[0])
                    if (source["book_id"] != book_id
                            or source["page_receipt"]["page_digest"]
                            != digest(page["page_text"])):
                        raise RuntimeError("Invalid book page evidence")
                    admitted = self._runtime._port.ingest({
                        "channel": "tool", "kind": "tool_result",
                        "percept": page["page_text"],
                        "source": "lab-book-read:" + read_row[1],
                    })
                    result.update(
                        success=True, page_text=page["page_text"],
                        outcome_memory_id=admitted["memory_id"],
                        read_event_hash=read_row[1],
                    )
                    break
                result["actions_used"] = len(result["actions"])
                self._port.verify()
                save("complete")
                return result
            except BaseException:
                save("interrupted")
                raise
