"""Trusted Laboratory offer/receipt adapter for Noesis-owned work selection.

The host has NO preference ordering and NO rule interpreter. It verifies which
physical work offers are legal, verifies acquired book evidence, and asks the
ORIGINAL Noesis to pick. It may authorize the picked action but cannot replace
it with its own choice. All world and memory receipts stay with their owners.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3

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


def _verified_work_outcomes(bridge: DoctorHomeBridge) -> tuple[str, ...]:
    """Identify original lived outcomes with independently replayable world hashes.

    The host supplies only eligible *memory IDs*. It cannot tell the original
    Noesis which action the episode favors or supply its numeric world state.
    """
    import re
    # Verify full rhythm and world history before trusting ANY row in its chain.
    bridge.subject.rhythm.verify()
    verified = []
    with bridge.world._open() as db:
        for m in bridge.doctor.brain.store.memories():
            if (m["evidence_class"] != "lived_runtime_memory"
                    or m["external"]
                    or not m["source"].startswith("laboratory-home:action:")):
                continue
            digest = m["source"].removeprefix("laboratory-home:action:")
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                continue
            matches = db.execute(
                "SELECT event_id FROM rhythm_events WHERE event_hash=?",
                (digest,),
            ).fetchall()
            if len(matches) != 1:
                continue
            receipt, checked = _row(db, "rhythm_events", matches[0][0])
            if (checked != digest or receipt.get("op") not in _OFFERS
                    or receipt.get("station") != "station:bench"
                    or receipt.get("args") != {}
                    or not isinstance(receipt.get("subject"), dict)
                    or receipt["subject"].get("inner") != m["text"]):
                continue
            verified.append(m["id"])
            if len(verified) >= 64:
                break
    return tuple(verified)


def propose_noesis_work(
    bridge: DoctorHomeBridge, *, learning_enabled: bool = True,
    neural_prior_enabled: bool = True, outcome_learning_enabled: bool = False,
) -> NoesisWorkProposal:
    """Give one real situated opportunity and eligible lived IDs to Noesis.

    No action target, raw page, preferred work class, motor command or reward
    is passed. The original recurrent motor distribution and memory content
    are evaluated *inside* the canonical Noesis cognitive decision.
    """
    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("Use a source-authorized original brain Laboratory bridge")
    if (type(learning_enabled) is not bool or type(neural_prior_enabled) is not bool
            or type(outcome_learning_enabled) is not bool):
        raise TypeError("Experimental lesion flags must be booleans")
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
    verified_outcomes = (
        _verified_work_outcomes(bridge) if outcome_learning_enabled else ()
    )
    decision = NoesisOrgan(bridge.doctor).deliberate_feasible_actions(
        observation_memory_id=received["memory_id"],
        eligible_read_memory_ids=tuple(eligible),
        feasible_actions=options,
        learning_enabled=learning_enabled,
        neural_prior_enabled=neural_prior_enabled,
        outcome_learning_enabled=outcome_learning_enabled,
        eligible_outcome_memory_ids=verified_outcomes,
    )
    return NoesisWorkProposal(
        action=decision["selected_action"],
        decision_id=decision["policy_decision_id"],
        observation_memory_id=received["memory_id"],
        supporting_memory_ids=tuple(
            decision["source_memory_ids"] + decision["used_outcome_memory_ids"]
        ),
        neural_scores=decision["base_action_scores"],
        candidate_scores=decision["action_scores"],
    )


def verify_noesis_work_replay(
    bridge: DoctorHomeBridge, *, event_id: str, action: str,
) -> str:
    """Authenticate BOTH prior Doctor intent and a bound original-Noesis choice.

    A real Laboratory receipt proves a physical event, not that Pretorius
    selected or performed it. This read-only guard must run before replay
    can create a fresh bridge reservation or first-person autobiography.
    """
    from .lab_home_bridge import _stable
    from .noesis_situated_choice import VERSION, OUTCOME_VERSION

    path = bridge._intent_path()
    if not path.is_file():
        raise PermissionError("No preexisting Doctor-owned work reservation")
    with sqlite3.connect(path, timeout=30) as db:
        row = db.execute(
            "SELECT request_json,status FROM doctor_action_intents WHERE event_id=?",
            (event_id,),
        ).fetchone()
    if (row is None or row[0] != _stable({"op": action, "args": {}})
            or row[1] not in ("pending", "complete")):
        raise PermissionError("No matching preexisting Doctor-owned work reservation")

    with bridge.doctor.brain.store.connect() as db:
        rows = db.execute(
            "SELECT id,selected_action,policy_version,state_pressure_json "
            "FROM policy_decisions WHERE trigger='noesis_situated_choice'"
        ).fetchall()
    matching = []
    for decision in rows:
        evidence = json.loads(decision["state_pressure_json"])
        if evidence.get("motor_event_id") != event_id:
            continue
        if (decision["selected_action"] != action
                or decision["policy_version"] not in (VERSION, OUTCOME_VERSION)
                or evidence.get("version") != decision["policy_version"]
                or evidence.get("selector_authority") != "original_noesis"
                or evidence.get("physical_authority") != "none"
                or evidence.get("motor_authorization") != "authorized"):
            raise PermissionError("Invalid original-Noesis work binding")
        matching.append(decision["id"])
    if len(matching) != 1:
        raise PermissionError("No unique original-Noesis decision bound to work receipt")
    return matching[0]


def prior_noesis_motor_binding(bridge: DoctorHomeBridge, event_id: str) -> bool:
    """A durable original policy binding cannot be assigned a second choice."""
    with bridge.doctor.brain.store.connect() as db:
        rows = db.execute(
            "SELECT state_pressure_json FROM policy_decisions "
            "WHERE trigger='noesis_situated_choice'"
        ).fetchall()
    return any(
        json.loads(row["state_pressure_json"]).get("motor_event_id") == event_id
        for row in rows
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
    from .noesis_situated_choice import VERSION, OUTCOME_VERSION
    with bridge.doctor.brain.store.connect() as db:
        rows = db.execute(
            "SELECT id,selected_action,policy_version,state_pressure_json FROM policy_decisions "
            "WHERE id=? AND trigger='noesis_situated_choice' "
            "AND policy_version IN (?,?)",
            (decision_id, VERSION, OUTCOME_VERSION),
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
            or evidence.get("version") != rows[0]["policy_version"]
            or rows[0]["policy_version"] not in (VERSION, OUTCOME_VERSION)):
        raise PermissionError("Original Noesis decision has invalid action evidence")
    if evidence.get("motor_event_id") not in (None, event_id):
        raise PermissionError("Original Noesis decision already bound to another work ID")

    # Idempotent existing world receipt may be retried after a crash/restart
    # even when the physical condition has already changed.
    with bridge.world._open() as db:
        prior = db.execute(
            "SELECT event_id FROM rhythm_events WHERE event_id=?", (event_id,)
        ).fetchone()
        if prior is not None:
            envelope, _ = _row(db, "rhythm_events", prior[0])
            if envelope.get("op") != action:
                raise PermissionError("World receipt was recorded for another action")
            if verify_noesis_work_replay(
                bridge, event_id=event_id, action=action,
            ) != decision_id:
                raise PermissionError("World receipt belongs to another Noesis decision")
            return {"action": action, "decision_id": decision_id,
                    "world": bridge.act(action, event_id=event_id)}

    # Fresh execution checks world eligibility and ensures the exact same
    # admitted observation still represents current physical world state.
    if action not in _feasible_work(bridge):
        raise PermissionError("Native action no longer physically feasible")
    now = bridge.observe()
    if now["memory_id"] != evidence.get("observation_memory_id"):
        raise PermissionError("Original Noesis decision is stale after world change")

    # Persist the exact event-ID binding in the EXISTING canonical Noesis
    # policy row BEFORE the original Laboratory can commit a physical event.
    # A crash after the world commit can then prove the Doctor's prior choice.
    store = bridge.doctor.brain.store
    with store.transaction() as db:
        saved = db.execute(
            "SELECT state_pressure_json FROM policy_decisions WHERE id=? "
            "AND trigger='noesis_situated_choice'", (decision_id,),
        ).fetchone()
        if saved is None:
            raise PermissionError("Original Noesis decision disappeared")
        # Canonical BrainStore transaction enforces unique physical identity
        # even when an alternate caller skips shipping-host preflight.
        prior_rows = db.execute(
            "SELECT id,state_pressure_json FROM policy_decisions "
            "WHERE trigger='noesis_situated_choice' AND id!=?",
            (decision_id,),
        ).fetchall()
        if any(
            json.loads(prior["state_pressure_json"]).get("motor_event_id") == event_id
            for prior in prior_rows
        ):
            raise PermissionError(
                "Work event ID already bound to another original-Noesis decision"
            )
        bound = json.loads(saved["state_pressure_json"])
        if bound.get("motor_event_id") not in (None, event_id):
            raise PermissionError("Original Noesis decision bound to another work ID")
        if (bound.get("selector_authority") != "original_noesis"
                or bound.get("version") != rows[0]["policy_version"]):
            raise PermissionError("Original Noesis decision evidence changed")
        bound["motor_event_id"] = event_id
        bound["motor_authorization"] = "authorized"
        db.execute(
            "UPDATE policy_decisions SET state_pressure_json=? WHERE id=?",
            (json.dumps(bound, sort_keys=True), decision_id),
        )
        store.bump_state_version(db)
    return {"action": action, "decision_id": decision_id,
            "world": bridge.act(action, event_id=event_id)}
