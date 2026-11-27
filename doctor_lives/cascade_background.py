"""Budgeted host-scheduled cognition for the isolated CASCADE preview.

The operational ledger owns leases and receipts, never identity or memories.
This is a trusted local host API, not authentication of arbitrary callers.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import sqlite3
import time

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")


def checked_id(value):
    if type(value) is not str or not _ID.fullmatch(value):
        raise ValueError("bounded host identifier required")
    return value


def integer(value, low=0, high=10**15):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("integer outside the operational domain")
    return value


@contextmanager
def operation_lock(directory, name="cascade-operation.lock"):
    """Crash leaves a lock for explicit operator reconciliation, never a retry.

    All supported CASCADE foreground and background paths use this lock.
    Direct private Doctor APIs remain a trusted-host bypass, not a sandbox.
    """
    path = Path(directory) / name
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise RuntimeError("CASCADE operation active or crashed; reconcile the lock") from exc
    try:
        os.write(fd, json.dumps({"pid": os.getpid(), "started_ns": time.time_ns()}).encode())
        os.fsync(fd)
        yield
    finally:
        os.close(fd)
        path.unlink()


@dataclass(frozen=True)
class BackgroundLease:
    lease_id: str
    total_ticks: int
    max_ticks_per_wake: int
    interval_ms: int
    expires_ms: int

    def __post_init__(self):
        checked_id(self.lease_id)
        integer(self.total_ticks, 1, 10000)
        integer(self.max_ticks_per_wake, 1, min(100, self.total_ticks))
        integer(self.interval_ms, 1)
        integer(self.expires_ms, 1)


class BackgroundLedger:
    def __init__(self, directory):
        self.path = Path(directory) / "cascade-operations.sqlite3"
        with self.connect() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            names = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if version == 0 and not names:
                db.executescript('''
                    CREATE TABLE leases (id TEXT PRIMARY KEY, spec TEXT NOT NULL,
                      remaining INTEGER NOT NULL, last_ms INTEGER, revoked INTEGER NOT NULL);
                    CREATE TABLE wakes (id TEXT PRIMARY KEY, lease TEXT NOT NULL,
                      now_ms INTEGER NOT NULL, ticks INTEGER NOT NULL,
                      status TEXT NOT NULL, receipt TEXT);
                    PRAGMA user_version=1;
                ''')
            elif version != 1 or names != {"leases", "wakes"}:
                raise RuntimeError("Unsupported CASCADE operational ledger schema")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def assert_reconciled(self, *, allowed_commitment_task_id=None):
        commitment_path = self.path.parent / "cascade-commitments.sqlite3"
        if commitment_path.exists():
            with sqlite3.connect(commitment_path) as commitments:
                blocked = commitments.execute(
                    "SELECT task_id,status FROM executable_commitments "
                    "WHERE status IN ('preparing','dispatching')"
                ).fetchall()
            for task_id, status in blocked:
                if status == "preparing" or task_id != allowed_commitment_task_id:
                    raise RuntimeError(
                        "Unresolved commitment operation requires reconciliation")
        laboratory = self.path.parent / "cascade-laboratory.sqlite3"
        if laboratory.exists():
            with sqlite3.connect(laboratory) as db:
                if db.execute("SELECT 1 FROM tasks WHERE status!='complete'").fetchone():
                    raise RuntimeError("Interrupted Laboratory action requires manual reconciliation")
        with self.connect() as db:
            pending = db.execute("SELECT id FROM wakes WHERE status!='completed' LIMIT 1").fetchone()
            if pending:
                raise RuntimeError("Unresolved background operation requires operator reconciliation")

    def issue(self, lease):
        if type(lease) is not BackgroundLease:
            raise TypeError("host-created BackgroundLease required")
        encoded = json.dumps(asdict(lease), sort_keys=True)
        with self.connect() as db:
            existing = db.execute("SELECT spec FROM leases WHERE id=?", (lease.lease_id,)).fetchone()
            if existing:
                if existing[0] != encoded:
                    raise PermissionError("Cannot alter or refill an existing lease")
                return
            db.execute("INSERT INTO leases VALUES (?, ?, ?, NULL, 0)",
                       (lease.lease_id, encoded, lease.total_ticks))

    def revoke(self, lease_id):
        checked_id(lease_id)
        with self.connect() as db:
            if db.execute("UPDATE leases SET revoked=1 WHERE id=?", (lease_id,)).rowcount != 1:
                raise KeyError(lease_id)

    def reserve(self, lease_id, wake_id, now_ms, ticks):
        checked_id(lease_id)
        checked_id(wake_id)
        integer(now_ms)
        integer(ticks, 1, 100)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT * FROM wakes WHERE id=?", (wake_id,)).fetchone()
            if old:
                if (old["lease"], old["now_ms"], old["ticks"]) != (lease_id, now_ms, ticks):
                    raise PermissionError("Conflicting reuse of wake identifier")
                if old["status"] != "completed":
                    raise RuntimeError("Indeterminate or failed wake requires operator reconciliation")
                return json.loads(old["receipt"])
            lease = db.execute("SELECT * FROM leases WHERE id=?", (lease_id,)).fetchone()
            if lease is None or lease["revoked"]:
                raise PermissionError("Missing or revoked background lease")
            spec = json.loads(lease["spec"])
            if now_ms >= spec["expires_ms"]:
                raise PermissionError("Background lease expired")
            if ticks > spec["max_ticks_per_wake"] or ticks > lease["remaining"]:
                raise PermissionError("Background tick budget exhausted")
            if lease["last_ms"] is not None and now_ms - lease["last_ms"] < spec["interval_ms"]:
                raise PermissionError("Background wake not due or clock moved backwards")
            db.execute("UPDATE leases SET remaining=remaining-?,last_ms=? WHERE id=?",
                       (ticks, now_ms, lease_id))
            db.execute("INSERT INTO wakes VALUES (?, ?, ?, ?, 'started', NULL)",
                       (wake_id, lease_id, now_ms, ticks))
        # The reservation commits BEFORE Doctor cognition. Crashes cannot refund it.
        return None

    def complete(self, wake_id, receipt, status="completed"):
        if status not in {"completed", "failed"}:
            raise ValueError("invalid operational outcome")
        with self.connect() as db:
            changed = db.execute("UPDATE wakes SET status=?,receipt=? WHERE id=? AND status='started'",
                                 (status, json.dumps(receipt, sort_keys=True), wake_id)).rowcount
            if changed != 1:
                raise RuntimeError("Missing or terminal wake reservation")


def run_wake(host, *, lease_id, wake_id, now_ms, ticks=1, authorized=False):
    """Run actual Doctor heartbeat cognition, with no invented external stimulus.

    No renderer, notification, tool action or memory resolution is forced. The
    existing Doctor heartbeat decides whether open concerns warrant thought.
    Time and policy counts are real; tick quota is not a token/energy measure.
    """
    from .cascade_governance import snapshot_doctor
    if type(authorized) is not bool or not authorized:
        raise PermissionError("Explicit host background authorization required")
    with operation_lock(host.state_dir):
        host._cascade_background.assert_reconciled()
        if host.pending_count() or host._journal.active() is not None:
            raise RuntimeError("Pending scene or subject delivery must be recovered first")
        previous = host._cascade_background.reserve(lease_id, wake_id, now_ms, ticks)
        if previous is not None:
            return {**previous, "replayed_receipt": True}
        before = snapshot_doctor(host)
        started_ns = time.time_ns()
        start = time.perf_counter_ns()
        try:
            result = host._doctor.brain.heartbeat(ticks=ticks)
            host._doctor.brain.save()
            after = snapshot_doctor(host)
            receipt = dict(
                schema="pretorius.cascade.background.v0.2", wake_id=wake_id,
                lease_id=lease_id, host_clock_ms=now_ms, ticks=ticks,
                started_unix_ns=started_ns, finished_unix_ns=time.time_ns(),
                elapsed_ns=time.perf_counter_ns() - start,
                before_digest=before.state_digest, after_digest=after.state_digest,
                before_tick=before.tick, after_tick=after.tick,
                policy_decision_ids=[t["policy_decision_id"] for t in result["thoughts"]],
                renderer_calls=0, external_actions=0, replayed_receipt=False,
                engineer_only=True,
            )
            host._cascade_background.complete(wake_id, receipt)
            host._scene_tick = max(host._scene_tick, after.tick + 1)
            return receipt
        except BaseException as exc:
            host._cascade_background.complete(wake_id, {
                "error_type": type(exc).__name__, "operator_reconciliation_required": True,
                "no_automatic_retry": True}, status="failed")
            raise
