"""Source-derived recovery coverage for original Laboratory need states.

Engineering read-only contract. Recovery candidates are *not* chosen here.
No agent gets privileged numerical state or a host-scripted plan. Every
hypothetical action is validated by the pinned Laboratory's own pure physics.
No invisible replenishment or altered fatigue/clutter rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RecoveryOption:
    need: str
    station: str
    actions: tuple[str, ...]
    physically_feasible: bool
    blocker: str | None = None


def _attempt(initial: dict, actions: tuple[str, ...], station: str) -> tuple[bool, str | None]:
    from pretorius_lab.daily_rhythm import transition
    from pretorius_lab.physics import Conflict, LabError

    state = initial
    for action in actions:
        try:
            state, _ = transition(state, action, {}, station)
        except (Conflict, LabError) as exc:
            return False, type(exc).__name__ + ": " + str(exc)
    return True, None


def recovery_options(state: dict[str, Any]) -> tuple[RecoveryOption, ...]:
    """Enumerate physically legal repair alternatives, never autonomous goals.

    A station name denotes a real required destination, *not* teleportation.
    It is the embodied navigation layer's job to show a route and Noesis's
    job to choose. A failed option remains visible as a blocker.
    """
    from pretorius_lab.daily_rhythm import _validate, _can_see
    _validate(state)
    needs: list[tuple[str, str, tuple[str, ...]]] = []
    if state["fatigue"] >= 4:
        needs.extend((
            ("fatigue", "station:bedroom", ("rest",)),
            ("fatigue", "station:bedroom", ("sleep",)),
        ))
    if state["hunger"] >= 4:
        if state["meal_ready"]:
            needs.append(("hunger", "station:kitchen", ("eat",)))
        else:
            needs.append(("hunger", "station:kitchen", ("prepare_meal", "eat")))
    if state["thirst"] >= 6:
        needs.append(("thirst", "station:kitchen", ("brew_tea",)))
    if state["apparatus"] <= 1:
        needs.append(("apparatus", "station:bench", ("repair",)))
    for room, station in (
        ("room:sanctum", "station:bench"),
        ("room:kitchen", "station:kitchen"),
        ("room:shop", "station:shop:private"),
    ):
        if state["cleanliness"][room] >= 2:
            needs.append(("clutter:" + room, station, ("clean",)))
    # Darkness itself is a real obstruction. Original light physics require
    # oil, a reachable room and exact physical world action, not free vision.
    for room, station in (
        ("room:sanctum", "station:bench"),
        ("room:kitchen", "station:kitchen"),
        ("room:bedroom", "station:bedroom"),
        ("room:parlor", "station:parlor"),
        ("room:hall", "station:hall"),
        ("room:shop", "station:shop:private"),
    ):
        if not _can_see(state, room):
            needs.append(("darkness:" + room, station, ("light",)))
    options = []
    for need, station, actions in needs:
        ok, blocker = _attempt(state, actions, station)
        options.append(RecoveryOption(need, station, actions, ok, blocker))
    return tuple(options)


def supply_gaps(state: dict[str, Any]) -> dict[str, str]:
    """Name finite stocks with no confirmed replenishment, without inventing a shop."""
    from pretorius_lab.daily_rhythm import _validate
    _validate(state)
    return {
        item: ("exhausted_no_verified_replenishment" if count == 0
               else "finite_stock_no_verified_replenishment")
        for item, count in state["supplies"].items()
    }


def audit_original_life(bridge) -> dict:
    """Trusted engineering-side report, NEVER an Ipseity or memory input."""
    from .lab_home_bridge import DoctorHomeBridge
    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("Expected the actual original Laboratory bridge")
    bridge.subject.verify()
    state = bridge.subject.rhythm.audit_state()
    routes = []
    from .lab_endogenous_book_task import EndogenousBookPursuit
    at = bridge.subject.embodied.verify()["station"]
    for option in recovery_options(state):
        step = None if at == option.station else EndogenousBookPursuit._route(at, option.station)
        routes.append({
            "need": option.need, "station": option.station,
            "actions": list(option.actions),
            "physical_feasible_at_destination": option.physically_feasible,
            "first_source_route_step": step,
            "route_exists": at == option.station or step is not None,
            "blocker": option.blocker,
            "engineer_only": True,
        })
    return {
        "schema": "pretorius.candidate-b.original-lab-recovery-census.v1",
        "source": "pinned_original_lab_pure_transition",
        "current_station": at,
        "recovery_paths": routes,
        "finite_supplies": supply_gaps(state),
        "external_procurement_available": False,
        "noesis_goal_selection_proven": False,
        "source_verified_task_completion_proven": False,
        "not_a_simulation_action_or_subject_percept": True,
    }
