"""Experimental durable Doctor commitment -> authorized Laboratory consequence.

This is a trusted-host dispatcher, not another cognitive store or an LLM planner.
The Doctor owns the commitment; this journal binds its executable permission,
prerequisite, world epoch, one attempt, and source-backed outcome. Host wakes
are required. No external action or automatic recovery follows a crash.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sqlite3

from .cascade_background import integer, operation_lock
from .cascade_laboratory import _volume, remembered_shelf

_ID = re.compile(r"[A-Za-z0-9_-]{1,60}\Z")
_SCHEMA = "cascade.commitment-laboratory.v0.1"


def _ledger(host):
    path = Path(host.state_dir) / "cascade-commitments.sqlite3"
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS executable_commitments (
        task_id TEXT PRIMARY KEY,
        doctor_commitment_id TEXT,
        book_id TEXT NOT NULL,
        lab_id TEXT NOT NULL,
        world_epoch TEXT NOT NULL,
        expires_ms INTEGER NOT NULL,
        max_actions INTEGER NOT NULL,
        status TEXT NOT NULL,
        report TEXT
    )""")
    db.commit()
    return db


def _doctor_commitment(host, commitment_id):
    with host._doctor.brain.store.connect() as db:
        row = db.execute(
            "SELECT id,status,outcome FROM commitments WHERE id=?", (commitment_id,)
        ).fetchone()
        return dict(row) if row else None


def _check_host(host):
    from .cascade_preview import CascadePretoriusPreview
    if not isinstance(host, CascadePretoriusPreview):
        raise TypeError("The actual CASCADE Pretorius host is required")


def accept_lab_commitment(host, port, *, task_id, book_id, expires_ms,
                          max_actions=4, authorized=False):
    """Persist a real Doctor commitment and a bounded executable binding.

    Authorization here grants the *possibility* of one bounded action attempt.
    A separate trusted, explicitly authorized host wake starts any world action.
    """
    _check_host(host)
    if authorized is not True:
        raise PermissionError("Explicit host authorization required for commitment")
    if not isinstance(task_id, str) or _ID.fullmatch(task_id) is None:
        raise ValueError("Short stable commitment task ID required")
    _volume(book_id)
    integer(expires_ms, 1)
    if type(max_actions) is not int or not 1 <= max_actions <= 40:
        raise ValueError("Action allowance must be a bounded integer")
    with operation_lock(host.state_dir):
        host._cascade_background.assert_reconciled()
        if host.pending_count() or host._journal.active() is not None:
            raise RuntimeError("Pending subject delivery must be recovered first")
        world = port.verify()
        with _ledger(host) as db:
            old = db.execute("SELECT * FROM executable_commitments WHERE task_id=?",
                             (task_id,)).fetchone()
            if old:
                if (old["book_id"], old["lab_id"], old["world_epoch"],
                    old["expires_ms"], old["max_actions"]) != (
                        book_id, world["lab_id"], world["world_epoch"],
                        expires_ms, max_actions):
                    raise PermissionError("Cannot modify or refill an accepted task")
                if old["status"] == "preparing":
                    raise RuntimeError("Interrupted acceptance requires reconciliation")
                return {"task_id": task_id,
                        "doctor_commitment_id": old["doctor_commitment_id"],
                        "status": old["status"], "replayed": True}
            db.execute("""INSERT INTO executable_commitments
                (task_id,doctor_commitment_id,book_id,lab_id,world_epoch,
                 expires_ms,max_actions,status,report)
                VALUES (?,?,?,?,?,?,?,'preparing',NULL)""",
                (task_id, None, book_id, world["lab_id"], world["world_epoch"],
                 expires_ms, max_actions))
            db.commit()
            commitment_id = host._doctor.brain.add_commitment(
                "Find and read " + _volume(book_id) +
                " in the Laboratory when its location is witnessed.",
                actor="self", importance=0.7)
            host._doctor.brain.save()
            db.execute("""UPDATE executable_commitments
                SET doctor_commitment_id=?, status='waiting' WHERE task_id=?""",
                (commitment_id, task_id))
            db.commit()
    return {"task_id": task_id, "doctor_commitment_id": commitment_id,
            "status": "waiting", "replayed": False}


def service_lab_commitment(host, port, *, task_id, now_ms, authorized=False):
    """One host-scheduled wake. No new User instruction is necessary.

    Preconditions are authentic, active Doctor sighting memories, never a
    privileged world-map query. Source-backed completion is idempotent.
    """
    _check_host(host)
    if authorized is not True:
        raise PermissionError("Explicit host action-wake authorization required")
    if not isinstance(task_id, str) or _ID.fullmatch(task_id) is None:
        raise ValueError("Invalid commitment ID")
    integer(now_ms, 0)
    with operation_lock(host.state_dir, "cascade-commitment-dispatch.lock"):
        with operation_lock(host.state_dir):
            host._cascade_background.assert_reconciled()
            if host.pending_count() or host._journal.active() is not None:
                raise RuntimeError("Pending subject delivery blocks the wake")
            with _ledger(host) as db:
                row = db.execute("SELECT * FROM executable_commitments WHERE task_id=?",
                                 (task_id,)).fetchone()
                if row is None:
                    raise KeyError(task_id)
                world = port.verify()
                if (world["lab_id"], world["world_epoch"]) != (
                        row["lab_id"], row["world_epoch"]):
                    raise PermissionError("Commitment bound to another Laboratory epoch")
                status = row["status"]
                if status == "completed":
                    return {"schema": _SCHEMA, "task_id": task_id,
                            "status": "completed", "replayed": True,
                            "evidence": json.loads(row["report"])}
                if status not in ("waiting", "dispatching"):
                    raise RuntimeError("Commitment requires operator reconciliation")
                doctor = _doctor_commitment(host, row["doctor_commitment_id"])
                if doctor is None:
                    raise RuntimeError("Authoritative Doctor commitment is missing")
                if status == "waiting":
                    if doctor["status"] not in ("open", "overdue"):
                        raise RuntimeError("Doctor commitment was changed outside dispatcher")
                    if now_ms >= row["expires_ms"]:
                        return {"schema": _SCHEMA, "task_id": task_id,
                                "status": "authorization_expired", "actions": 0}
                    hint = remembered_shelf(host, port, row["book_id"])
                    if hint is None:
                        return {"schema": _SCHEMA, "task_id": task_id,
                                "status": "waiting_prerequisite", "actions": 0}
                    db.execute("""UPDATE executable_commitments
                        SET status='dispatching' WHERE task_id=?""", (task_id,))
                    db.commit()
                else:
                    # Only replay a completed Laboratory receipt after an
                    # interruption between verified action and finalization.
                    with sqlite3.connect(Path(host.state_dir) /
                                         "cascade-laboratory.sqlite3") as actions:
                        previous = actions.execute(
                            "SELECT status FROM tasks WHERE id=?",
                            ("commit-" + task_id,)).fetchone()
                    if previous is None or previous[0] != "complete":
                        raise RuntimeError("Uncertain dispatched task needs manual reconciliation")
                book_id, max_actions, commitment_id = (
                    row["book_id"], row["max_actions"], row["doctor_commitment_id"])
        # The Laboratory itself takes the CASCADE exclusion lock, reserves
        # every action before the tool call and verifies source delivery.
        outcome = host.laboratory_read(
            port, task_id="commit-" + task_id, book_id=book_id,
            max_actions=max_actions, authorized=True)
        with operation_lock(host.state_dir):
            host._cascade_background.assert_reconciled()
            if not outcome["success"]:
                with _ledger(host) as db:
                    db.execute("""UPDATE executable_commitments
                        SET status='needs_review',report=? WHERE task_id=?""",
                        (json.dumps(outcome, sort_keys=True), task_id))
                    db.commit()
                return {"schema": _SCHEMA, "task_id": task_id,
                        "status": "needs_review", "actions": outcome["actions_used"]}
            source_hash = outcome["read_event_hash"]
            evidence = host._doctor.brain.store.get_memory(outcome["outcome_memory_id"])
            if (not evidence or not evidence["active"] or
                    evidence["source"] != "laboratory-read:" + source_hash):
                raise RuntimeError("The verified outcome must exist in Doctor lived memory")
            from pretorius_lab.book_library import BookLibrary
            BookLibrary(port.habitat).verify()
            # The original task is externally idempotent. Resolve only
            # after authentic delivery, not merely after an action attempt.
            doctor = _doctor_commitment(host, commitment_id)
            expected = "verified-laboratory-read:" + source_hash
            if doctor["status"] in ("open", "overdue"):
                host._doctor.brain.resolve_commitment(commitment_id, expected, kept=True)
                host._doctor.brain.save()
            elif doctor["status"] != "kept" or doctor["outcome"] != expected:
                raise RuntimeError("Doctor completion conflicts with world evidence")
            receipt = {"schema": _SCHEMA, "task_id": task_id, "status": "completed",
                       "doctor_commitment_id": commitment_id,
                       "read_event_hash": source_hash,
                       "outcome_memory_id": outcome["outcome_memory_id"],
                       "actions": outcome["actions_used"],
                       "world_epoch": row["world_epoch"],
                       "engineering_only": True}
            with _ledger(host) as db:
                db.execute("""UPDATE executable_commitments
                    SET status='completed',report=? WHERE task_id=?""",
                    (json.dumps(receipt, sort_keys=True), task_id))
                db.commit()
            return receipt
