"""Bounded, offline, real-elapsed-time host for the ONE original Doctor brain.

The host schedules cognitive opportunities only. It never chooses goals,
issues physical actions, forges world perceptions, or renders engineer data as
subjective experience. The original Laboratory remains the world authority.
"""
from __future__ import annotations

import math
from pathlib import Path
import threading
import time

from .engineer_time import engineer_time


def run_laboratory(
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
    runtime = SixOrganRuntime.open(state)
    bridge = runtime.bind_laboratory(
        SubjectPort(SpatialHabitat(world)), authorized=True,
    )
    recovered = bridge.recover_pending_actions()
    if bridge.pending_action_intents():
        raise RuntimeError("Unreconciled Laboratory action; host startup denied")
    observed = bridge.observe()
    subject_frames = [item["subject"] for item in recovered]
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
