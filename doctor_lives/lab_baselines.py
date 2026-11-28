"""Preregistered, world-only matched controller baselines for Candidate B.

These are deliberately NOT Pretorius, not a second mind, and never a source
of self-selected agent intent. They use an identical engineer-authored
recovery challenge and ORIGINAL Laboratory physics/receipts. Baseline
performance is a comparator, not Candidate B acceptance.
"""
from __future__ import annotations

from collections import deque
from pathlib import Path
import tempfile


def _next_station(current: str, target: str) -> str:
    from pretorius_lab.embodied_access import STATIONS
    queue = deque(((current, ()),))
    visited = {current}
    while queue:
        station, path = queue.popleft()
        for neighbor in STATIONS[station][1]:
            if neighbor in visited:
                continue
            route = path + (neighbor,)
            if neighbor == target:
                return route[0]
            visited.add(neighbor)
            queue.append((neighbor, route))
    raise RuntimeError("No real original Laboratory route to baseline target")


def _do(subject, op: str, trace: list[str], **kwargs) -> None:
    subject.act(op, event_id="baseline_" + str(len(trace)), **kwargs)
    trace.append(op)


def run_repair_baseline(mode: str, *, max_steps: int = 24) -> dict:
    """One actual world, severe initial fatigue, clutter and damaged apparatus.

    Simple controller explicitly knows the experimenter's repair objective.
    Flat comparator chooses a source-feasible action without considering it.
    Neither is credited as spontaneous cognitive autonomy.
    """
    if mode not in ("simple", "flat") or type(max_steps) is not int or not 1 <= max_steps <= 64:
        raise ValueError("One predefined baseline and bounded action budget required")
    # Lifetime boundary: the world and its SQLite cursors must become
    # unreachable BEFORE Windows deletes the temporary directory. Entering
    # SQLite Connection as a context manager commits but does not close it.
    # The original Laboratory donor cannot be modified just for this test.
    with tempfile.TemporaryDirectory(prefix="candidate-b-world-only-") as tmp:
        result = _run_repair_baseline_world(Path(tmp), mode, max_steps)
        # Close any source-donor SQLite connection cycles before cleanup.
        # No retries, ignore_errors or suppressed provenance exceptions.
        import gc
        gc.collect()
        return result


def _run_repair_baseline_world(root: Path, mode: str, max_steps: int) -> dict:
    """Execute a single original-world comparison, then release its handles."""
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm, initial_state, transition, OPERATIONS
    from pretorius_lab.physics import Conflict, LabError
    from pretorius_lab.subject_port import SubjectPort
    world = SpatialHabitat.create(root / "lab.sqlite3")
    HomeLife(world).initialize()
    genesis = initial_state()
    genesis["fatigue"] = 9
    genesis["apparatus"] = 0
    genesis["cleanliness"]["room:sanctum"] = 3
    # A changed initial condition is an explicitly RESEARCHER-AUTHORED
    # baseline fixture. The original world refuses noncanonical
    # genesis without documented parent provenance.
    DailyRhythm(world).initialize(
        initial_state=genesis,
        parent={"status": "researcher_authored_comparison_fixture",
                "not_lived_by_pretorius": True,
                "same_initial_state_for_all_baselines": True},
    )
    subject = SubjectPort(world)
    epoch = subject.verify()["world_epoch"]
    trace: list[str] = []
    for _ in range(max_steps):
        current = subject.rhythm.audit_state()
        at = subject.embodied.verify()["station"]
        if (current["apparatus"] > 0
                and current["cleanliness"]["room:sanctum"] < 3):
            break
        if mode == "flat":
            # No goal knowledge. Alphabetical legal local action is a
            # controlled deliberately weak comparator, not pretend agent.
            actions = []
            for op in sorted(OPERATIONS - {"look"}):
                args = {"minutes": 60} if op == "advance" else {}
                try:
                    transition(current, op, args, at)
                except (Conflict, LabError):
                    continue
                actions.append((op, args))
            if not actions:
                break
            op, args = actions[0]
            _do(subject, op, trace, **args)
            continue
        if current["fatigue"] >= 8:
            target, action = "station:bedroom", "sleep"
        elif current["cleanliness"]["room:sanctum"] >= 3:
            target, action = "station:bench", "clean"
        elif current["apparatus"] < 1:
            target, action = "station:bench", "repair"
        else:
            raise RuntimeError("Unexpected simple baseline state")
        if at != target:
            _do(subject, "walk", trace, station=_next_station(at, target))
        else:
            _do(subject, action, trace)
    final = subject.rhythm.audit_state()
    attested = subject.verify()
    if attested["world_epoch"] != epoch:
        raise RuntimeError("Baseline world epoch changed unexpectedly")
    succeeded = final["apparatus"] > 0 and final["cleanliness"]["room:sanctum"] < 3
    return {
        "schema": "pretorius.candidate-b.world-only-baseline.v1",
        "controller": mode,
        "researcher_defined_task": "restore damaged, cluttered workbench after severe fatigue",
        "initial_problem": {"fatigue": 9, "clutter": 3, "apparatus": 0},
        "goal_completed_by_physical_world": succeeded,
        "actions": trace,
        "actual_world_epoch_verified": True,
        "original_source_world_receipts_only": True,
        "Noesis_or_any_organ_invoked": False,
        "autonomy_credit": False,
        "world_final": {
            "fatigue": final["fatigue"],
            "clutter": final["cleanliness"]["room:sanctum"],
            "apparatus": final["apparatus"],
            "spares": final["supplies"]["spares"],
        },
    }
