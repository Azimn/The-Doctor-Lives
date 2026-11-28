"""Independent Candidate B health/failure taxonomy, no Doctor state mutation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthSample:
    process_alive: bool
    elapsed_seconds: float
    heartbeat_age_seconds: float | None
    last_physical_task_age_seconds: float | None
    verified_completed_tasks: int


def classify(sample: HealthSample) -> str:
    """Distinguish process death, halted heartbeat, and live-but-no-task.

    A missing task is an experimental failure, NOT proof of refusal, death, or
    a broken brain. The independent source auditor determines which goal
    receipts count; a heartbeat alone is never task completion.
    """
    if type(sample) is not HealthSample:
        raise TypeError("Expected independent health observation")
    if not sample.process_alive:
        return "crash"
    if sample.elapsed_seconds < 0 or sample.verified_completed_tasks < 0:
        raise ValueError("Invalid sample")
    if (sample.heartbeat_age_seconds is None
            or sample.heartbeat_age_seconds > 90.0):
        return "stall" if sample.elapsed_seconds >= 90.0 else "startup"
    if sample.verified_completed_tasks == 0 and sample.elapsed_seconds >= 600.0:
        return "silent_skip"
    if (sample.last_physical_task_age_seconds is not None
            and sample.last_physical_task_age_seconds > 900.0):
        return "silent_skip"
    return "active"
