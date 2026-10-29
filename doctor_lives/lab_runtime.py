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
        observed = bridge.observe()
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
