"""Bounded, offline, real-elapsed-time host for the ONE original Doctor brain.

The host schedules cognitive opportunities only. It never chooses goals,
issues physical actions, forges world perceptions, or renders engineer data as
subjective experience. The original Laboratory remains the world authority.
"""
from __future__ import annotations

import errno
from contextlib import contextmanager
import math
import os
from pathlib import Path
import threading
import time

from .engineer_time import engineer_time


@contextmanager
def _exclusive_lock(lock_path: Path, label: str):
    """Keep a cooperative OS lock on a persistent, non-symlink sidecar."""
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(lock_path, flags, 0o600)
    with os.fdopen(fd, "r+b") as handle:
        acquired = False
        try:
            if os.name == "nt":
                import msvcrt
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            acquired = True
        except OSError as exc:
            if exc.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                raise RuntimeError(f"{label} host already active") from exc
            raise
        try:
            yield
        finally:
            if acquired:
                if os.name == "nt":
                    import msvcrt
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def _exclusive_host(state: Path, world: Path | None = None):
    """Exclude cooperating hosts sharing EITHER the brain OR the real world.

    The original state lock remains in place. A second lock beside the
    resolved Laboratory SQLite file also denies a different state directory
    pointed at the same world. Both sidecars are persistent so unlinking
    cannot silently split lock ownership. These are cooperative host leases,
    not protection from privileged/direct database writers.
    """
    with _exclusive_lock(state / ".laboratory-host.lock", "Canonical Doctor Laboratory"):
        if world is None:
            yield
        else:
            canonical_world = world.resolve(strict=True)
            if not canonical_world.is_file():
                raise FileNotFoundError("Existing authoritative Laboratory world required")
            # A pathname-based sidecar is not shared by hardlinks to the same
            # SQLite inode. Fail closed before opening either world authority
            # rather than allow two cooperating hosts to lock different names.
            if canonical_world.stat().st_nlink != 1:
                raise RuntimeError("Authoritative Laboratory world hardlinks are unsupported")
            world_lock = canonical_world.with_name(
                canonical_world.name + ".laboratory-host.lock"
            )
            with _exclusive_lock(world_lock, "Authoritative Laboratory world"):
                # Recheck after acquiring the sidecar. A new hardlink created
                # while another host runs is rejected by its next entrant.
                if canonical_world.stat().st_nlink != 1:
                    raise RuntimeError("Authoritative Laboratory world hardlinks are unsupported")
                yield


def run_laboratory(
    state: Path, world: Path, *, duration_seconds: float,
    interval_seconds: float, stop: threading.Event | None = None,
) -> dict:
    """Run with an OS-backed nonblocking lease on the ONE canonical state."""
    with _exclusive_host(state, world):
        return _run_laboratory_session(
            state, world, duration_seconds=duration_seconds,
            interval_seconds=interval_seconds, stop=stop,
        )



def sleep_laboratory(state: Path, world: Path, *, event_id: str) -> dict:
    """Operator-requested, original-Lab physical sleep, never a Doctor goal.

    The original Laboratory must place the body in its actual bedroom first.
    A caller supplies one stable action ID; replay cannot advance the world
    again. This advances Laboratory *simulated* time, not wall-clock soak time.
    The next lab-run is the explicit wake/resume operation.
    """
    with _exclusive_host(state, world):
        if not (state / "brain.sqlite3").is_file() or not (
            state / "pretorius_recurrent.npz"
        ).is_file():
            raise FileNotFoundError(
                "Existing canonical Doctor BrainStore and neural checkpoint required"
            )
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.subject_port import SubjectPort
        from .organs import SixOrganRuntime

        runtime = SixOrganRuntime.open(state)
        bridge = runtime.bind_laboratory(
            SubjectPort(SpatialHabitat(world)), authorized=True,
        )
        # Capture identities before replay so a recovered sleep is presented
        # only once. The bridge remains the sole durable intent authority.
        pending_before = bridge.pending_action_intents()
        recovered = bridge.recover_pending_actions()
        if bridge.pending_action_intents():
            raise RuntimeError("Unreconciled Laboratory action; sleep denied")
        if len(recovered) != len(pending_before):
            raise RuntimeError("Laboratory recovery identity count changed")

        # A historical receipt is allowed to replay after Pretorius has
        # genuinely walked elsewhere. This lookup grants NO authority: act()
        # must still authenticate the original receipt, action identity, and
        # canonical lived memory. A NEW sleep remains bedroom-only.
        with bridge.world._open() as db:
            historical_sleep = db.execute(
                "SELECT 1 FROM rhythm_events WHERE event_id=? LIMIT 1",
                (event_id,),
            ).fetchone() is not None
        if (not historical_sleep
                and bridge.subject.embodied.verify()["station"] != "station:bedroom"):
            raise RuntimeError(
                "Physical sleep requires the actual Laboratory bedroom"
            )
        result = bridge.act("sleep", event_id=event_id)
        runtime.checkpoint()
        clock = engineer_time()
        subject_frames = [
            item["subject"] for intent, item in zip(pending_before, recovered)
            if intent["event_id"] != event_id
        ]
        subject_frames.append(result["subject"])
        return {
            "schema": "doctor-laboratory-offline-sleep.v1",
            "status": result["status"],
            "recovered": len(recovered),
            "subject_frames": subject_frames,
            "physical_sleep_minutes": 480,
            "clock": {"utc": clock.utc_iso, "beat": clock.beat},
        }



def work_laboratory(state: Path, world: Path, *, event_id: str) -> dict:
    """One operator-offered bench opportunity, chosen by the ORIGINAL Noesis.

    The host cannot select repair versus experiment. Original Laboratory
    physics supplies eligibility and the existing authorized bridge supplies
    durable action intent, source-backed memory, and cold crash recovery.
    This is a bounded externally offered opportunity, not self-initiation.
    """
    from .lab_home_bridge import _ACTION_DOMAINS, _SAFE_ID, _row

    # Deny malformed IDs before opening the canonical brain or creating LOOK.
    if type(event_id) is not str or not _SAFE_ID.fullmatch(event_id):
        raise ValueError("Stable bounded Laboratory work action ID required")
    with _exclusive_host(state, world):
        if not (state / "brain.sqlite3").is_file() or not (
            state / "pretorius_recurrent.npz"
        ).is_file():
            raise FileNotFoundError(
                "Existing canonical Doctor BrainStore and neural checkpoint required"
            )
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.subject_port import SubjectPort
        from .organs import SixOrganRuntime
        from .noesis_lab_work import propose_noesis_work, execute_noesis_work

        runtime = SixOrganRuntime.open(state)
        bridge = runtime.bind_laboratory(
            SubjectPort(SpatialHabitat(world)), authorized=True,
        )
        pending_before = bridge.pending_action_intents()
        recovered = bridge.recover_pending_actions()
        if bridge.pending_action_intents():
            raise RuntimeError("Unreconciled Laboratory action; work denied")
        if len(recovered) != len(pending_before):
            raise RuntimeError("Laboratory recovery identity count changed")
        subject_frames = [
            item["subject"] for intent, item in zip(pending_before, recovered)
            if intent["event_id"] != event_id
        ]

        # A stable ID is a world-wide intent identity, not just a rhythm row.
        # Refuse a foreign embodied/book ID before making a new Noesis choice.
        # A historical work receipt is replayed, never executed a second time
        # and never misreported as a newly selected cognitive action.
        with bridge.world._open() as db:
            tables = {
                row[0] for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            for table in sorted(set(_ACTION_DOMAINS.values()) - {"rhythm_events"}):
                if table in tables and db.execute(
                    "SELECT 1 FROM " + table + " WHERE event_id=? LIMIT 1",
                    (event_id,),
                ).fetchone():
                    raise RuntimeError(
                        "Work event ID already belongs to another Laboratory action"
                    )
            prior = (
                _row(db, "rhythm_events", event_id)[0]
                if db.execute(
                    "SELECT 1 FROM rhythm_events WHERE event_id=?",
                    (event_id,),
                ).fetchone()
                else None
            )
        if prior is not None:
            action = prior.get("op")
            if action not in ("repair", "experiment") or prior.get("args") != {}:
                raise RuntimeError("Work event ID belongs to non-work rhythm action")
            replay = bridge.act(action, event_id=event_id)
            runtime.checkpoint()
            subject_frames.append(replay["subject"])
            clock = engineer_time()
            return {
                "schema": "doctor-laboratory-offline-work.v1",
                "status": replay["status"],
                "action": action,
                "selection": "historical_world_receipt_replay",
                "recovered": len(recovered),
                "subject_frames": subject_frames,
                "clock": {"utc": clock.utc_iso, "beat": clock.beat},
            }

        # Reuse the already-tested Noesis choice and original Lab motor bridge.
        # Neither the CLI nor the scheduler supplies an action preference.
        proposal = propose_noesis_work(
            bridge, outcome_learning_enabled=True,
        )
        executed = execute_noesis_work(
            bridge, decision_id=proposal.decision_id,
            event_id=event_id, authorized_world_action=True,
        )
        runtime.checkpoint()
        subject_frames.append(executed["world"]["subject"])
        clock = engineer_time()
        return {
            "schema": "doctor-laboratory-offline-work.v1",
            "status": executed["world"]["status"],
            "action": executed["action"],
            "selection": "original_noesis",
            "recovered": len(recovered),
            "subject_frames": subject_frames,
            "clock": {"utc": clock.utc_iso, "beat": clock.beat},
        }


def _run_laboratory_session(
    state: Path, world: Path, *, duration_seconds: float,
    interval_seconds: float, stop: threading.Event | None = None,
) -> dict:
    """Recover pending receipts, observe once, then pulse at real clock intervals.

    This is a bounded host session, not proof of autonomous physical initiative
    or a 24-hour soak. Reopening the same authorities provides a wake/resume
    opportunity; sleep scheduling and external process exclusion remain open.
    """
    if not (math.isfinite(duration_seconds) and 0.1 <= duration_seconds <= 3600):
        raise ValueError("duration_seconds must be finite and between 0.1 and 3600")
    if not (math.isfinite(interval_seconds) and 0.05 <= interval_seconds <= duration_seconds):
        raise ValueError("interval_seconds must be finite and between 0.05 and duration")
    if not world.is_file():
        raise FileNotFoundError("Existing authoritative Laboratory world required")
    if not (state / "brain.sqlite3").is_file() or not (
        state / "pretorius_recurrent.npz"
    ).is_file():
        raise FileNotFoundError("Existing canonical Doctor BrainStore and neural checkpoint required")

    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.subject_port import SubjectPort
    from .organs import SixOrganRuntime

    stop = stop if stop is not None else threading.Event()
    # A cancellation already delivered by the CLI signal handler must not
    # produce a new Laboratory LOOK receipt or a lived observation.
    if stop.is_set():
        clock = engineer_time()
        return {
            "schema": "doctor-laboratory-offline-run.v1",
            "status": "interrupted",
            "recovered": 0,
            "subject_frames": [],
            "pulses": 0,
            "elapsed_seconds": 0.0,
            "clock": {"utc": clock.utc_iso, "beat": clock.beat},
        }
    runtime = SixOrganRuntime.open(state)
    bridge = runtime.bind_laboratory(
        SubjectPort(SpatialHabitat(world)), authorized=True,
    )
    recovered = bridge.recover_pending_actions()
    if bridge.pending_action_intents():
        raise RuntimeError("Unreconciled Laboratory action; host startup denied")
    subject_frames = [item["subject"] for item in recovered]
    # Reconciliation may finish after an interrupt. Never start a fresh
    # observation when cancellation arrived during that recovery window.
    if not stop.is_set():
        # The outer check is not sufficient: cancellation may arrive while
        # the bridge prepares its verified physical LOOK. The bridge must
        # check the same stop predicate before invoking original Lab LOOK.
        observed = bridge.observe(cancelled=stop.is_set)
        if observed is not None:
            subject_frames.append(observed["subject"])
    pulses = 0
    started = time.monotonic()
    deadline = started + duration_seconds
    next_pulse = started + interval_seconds
    try:
        while not stop.is_set():
            now = time.monotonic()
            if now >= deadline:
                break
            if stop.wait(max(0.0, min(next_pulse, deadline) - now)):
                break
            now = time.monotonic()
            if now >= deadline:
                break
            runtime.noesis.pulse(1)
            runtime.checkpoint()
            pulses += 1
            next_pulse += interval_seconds
            if next_pulse <= now:
                next_pulse = now + interval_seconds
    finally:
        runtime.checkpoint()
    clock = engineer_time()
    return {
        "schema": "doctor-laboratory-offline-run.v1",
        "status": "interrupted" if stop.is_set() else "completed",
        "recovered": len(recovered),
        "subject_frames": subject_frames,
        "pulses": pulses,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "clock": {"utc": clock.utc_iso, "beat": clock.beat},
    }
