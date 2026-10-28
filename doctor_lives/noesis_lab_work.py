"""Trusted Laboratory offer/receipt adapter for Noesis-owned work selection.

The host has NO preference ordering and NO rule interpreter. It verifies which
physical work offers are legal, verifies acquired book evidence, and asks the
ORIGINAL Noesis to pick. It may authorize the picked action but cannot replace
it with its own choice. All world and memory receipts stay with their owners.
"""
from __future__ import annotations

from dataclasses import dataclass
import json

from .experience_to_action import _source_read_page
from .lab_home_bridge import DoctorHomeBridge, _row
from .organs import NoesisOrgan

_OFFERS = ("experiment", "repair")


@dataclass(frozen=True)
class NoesisWorkProposal:
    action: str
    decision_id: str
    observation_memory_id: str
    supporting_memory_ids: tuple[str, ...]
    neural_scores: dict[str, float]
    candidate_scores: dict[str, float]
    selector: str = "original_noesis"
    motor_authorization: str = "not_granted"


def _feasible_work(bridge: DoctorHomeBridge) -> tuple[str, ...]:
    """Call the pinned world PURE physics function; do not read goals here."""
    from pretorius_lab.daily_rhythm import transition
    from pretorius_lab.physics import Conflict, LabError

    state = bridge.subject.rhythm.audit_state()  # Host only, never subject.
    station = bridge.subject.embodied.verify()["station"]
    if station != "station:bench":
        raise PermissionError("No bench work opportunity away from the bench")
    legal = []
    for action in _OFFERS:
        try:
            transition(state, action, {}, station)
        except (Conflict, LabError):
            continue
        legal.append(action)
    return tuple(legal)


def propose_noesis_work(
    bridge: DoctorHomeBridge, *, learning_enabled: bool = True,
    neural_prior_enabled: bool = True,
) -> NoesisWorkProposal:
    """Give one real situated opportunity and eligible lived IDs to Noesis.

    No action target, raw page, preferred work class, motor command or reward
    is passed. The original recurrent motor distribution and memory content
    are evaluated *inside* the canonical Noesis cognitive decision.
    """
    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("Use a source-authorized original brain Laboratory bridge")
    if type(learning_enabled) is not bool or type(neural_prior_enabled) is not bool:
        raise TypeError("Both experimental lesion flags must be booleans")
    options = _feasible_work(bridge)
    if not options:
        raise RuntimeError("Real Laboratory offers no feasible work action")
    received = bridge.observe()
    observation = bridge.doctor.brain.store.get_memory(received["memory_id"])
    if (observation is None or not observation["active"]
            or observation["evidence_class"] != "lived_runtime_memory"
            or observation["source"].startswith("laboratory-home:observe:") is False
            or observation["text"] != received["subject"]["inner"]):
        raise PermissionError("No verified current first-person Laboratory observation")

    # The host verifies only provenance, not the meaning of source text.
    # Noesis chooses from all candidate acquired book memories itself.
    eligible = []
    for memory in bridge.doctor.brain.store.memories():
        if not memory["text"].startswith("I read a page of "):
            continue
        if _source_read_page(bridge, memory["id"]) is not None:
            eligible.append(memory["id"])
        if len(eligible) >= 32:
            break
    decision = NoesisOrgan(bridge.doctor).deliberate_feasible_actions(
        observation_memory_id=received["memory_id"],
        eligible_read_memory_ids=tuple(eligible),
        feasible_actions=options,
        learning_enabled=learning_enabled,
        neural_prior_enabled=neural_prior_enabled,
    )
    return NoesisWorkProposal(
        action=decision["selected_action"],
        decision_id=decision["policy_decision_id"],
        observation_memory_id=received["memory_id"],
        supporting_memory_ids=tuple(decision["source_memory_ids"]),
        neural_scores=decision["base_action_scores"],
        candidate_scores=decision["action_scores"],
    )


def execute_noesis_work(
    bridge: DoctorHomeBridge, *, decision_id: str,
    event_id: str, authorized_world_action: bool = False,
) -> dict:
    """Authorize only the exact *recorded Noesis* concrete action choice."""
    if authorized_world_action is not True:
        raise PermissionError("Native cognitive decision has no motor authority")
    if type(decision_id) is not str or not decision_id:
        raise ValueError("Original canonical policy ID required")
    from .noesis_situated_choice import VERSION
    with bridge.doctor.brain.store.connect() as db:
        rows = db.execute(
            "SELECT id,selected_action,state_pressure_json FROM policy_decisions "
            "WHERE id=? AND trigger='noesis_situated_choice' AND policy_version=?",
            (decision_id, VERSION),
        ).fetchall()
        latest = db.execute(
            "SELECT id FROM policy_decisions WHERE trigger='noesis_situated_choice' "
            "ORDER BY rowid DESC LIMIT 1",
        ).fetchone()
    if len(rows) != 1 or latest is None or latest["id"] != decision_id:
        raise PermissionError("No fresh original Noesis situated policy choice")
    action = rows[0]["selected_action"]
    evidence = json.loads(rows[0]["state_pressure_json"])
    if (action not in _OFFERS or evidence.get("selector_authority") != "original_noesis"
            or evidence.get("physical_authority") != "none"
            or evidence.get("version") != VERSION):
        raise PermissionError("Original Noesis decision has invalid action evidence")

    # Idempotent existing world receipt may be retried after a crash/restart
    # even when the physical condition has already changed.
    with bridge.world._open() as db:
        prior = db.execute(
            "SELECT event_id FROM rhythm_events WHERE event_id=?", (event_id,)
        ).fetchone()
        if prior is not None:
            envelope, _ = _row(db, "rhythm_events", prior["event_id"])
            if envelope.get("op") != action:
                raise PermissionError("World receipt was recorded for another action")
            return {"action": action, "decision_id": decision_id,
                    "world": bridge.act(action, event_id=event_id)}

    # Fresh execution checks world eligibility and ensures the exact same
    # admitted observation still represents current physical world state.
    if action not in _feasible_work(bridge):
        raise PermissionError("Native action no longer physically feasible")
    now = bridge.observe()
    if now["memory_id"] != evidence.get("observation_memory_id"):
        raise PermissionError("Original Noesis decision is stale after world change")
    return {"action": action, "decision_id": decision_id,
            "world": bridge.act(action, event_id=event_id)}
