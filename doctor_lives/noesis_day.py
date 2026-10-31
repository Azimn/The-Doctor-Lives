"""Source-verified offline daily opportunities for the ONE original Noesis.

The host merely wakes the selector and authorizes the *selected* action. It
cannot pass an action name, goal, preferred destination or expected outcome.
The candidate set is derived by the actual Laboratory's pure physics from its
current independently maintained world state. No second planner or BrainStore.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3

from .lab_home_bridge import DoctorHomeBridge
from .noesis_lab_work import _verified_work_outcomes
from .noesis_situated_choice import NEURAL_AFFORDANCE_MAP, select_with_original_noesis
from .store import new_id


@dataclass(frozen=True)
class DailyChoice:
    policy_id: str
    action: str
    observation_id: str
    options: tuple[str, ...]


def physical_args(action: str) -> dict:
    """The Laboratory source authorizes 10 to 240 minute time increments.

    A neutral one-hour simulation quantum is not an action preference; only
    original Noesis decides whether any physical time passage will occur.
    """
    return {"minutes": 60} if action == "advance" else {}


def pending_daily_action_ids(bridge: DoctorHomeBridge) -> tuple[str, ...]:
    """Read-only canonical reservations awaiting world/memory reconciliation.

    This does not execute a physical action or invent a replacement goal.
    The caller must have separate world authorization before replay.
    """
    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("Original Laboratory bridge required for pending-action audit")
    with bridge.doctor.brain.store.connect() as db:
        rows = db.execute(
            "SELECT id,state_pressure_json FROM policy_decisions "
            "WHERE trigger='noesis_situated_choice' ORDER BY rowid"
        ).fetchall()
    pending = []
    for row in rows:
        evidence = json.loads(row["state_pressure_json"])
        if (evidence.get("motor_authorization") == "authorized"
                and evidence.get("motor_completion") != "admitted"):
            pending.append(row["id"])
    return tuple(pending)


def real_affordances(bridge: DoctorHomeBridge) -> tuple[str, ...]:
    """Enumerate the ORIGINAL world physics, never a host-supplied task list."""
    from pretorius_lab.daily_rhythm import OPERATIONS, transition
    from pretorius_lab.physics import Conflict, LabError

    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("An original DoctorHomeBridge is required")
    bridge.subject.verify()
    station = bridge.subject.embodied.verify()["station"]
    physical = bridge.subject.rhythm.audit_state()
    possible = []
    # The source-defined operations, not the harness's preferred sequence.
    for op in sorted(OPERATIONS - {"look"}):
        if op not in NEURAL_AFFORDANCE_MAP:
            continue
        try:
            transition(physical, op, physical_args(op), station)
        except (Conflict, LabError):
            continue
        possible.append(op)
    return tuple(possible)


def offer_daily_opportunity(bridge: DoctorHomeBridge, *, author_goal: bool = True,
                            use_consequences: bool = True) -> DailyChoice:
    """One independent Noesis choice, without any operator action argument."""
    if type(author_goal) is not bool or type(use_consequences) is not bool:
        raise TypeError("Typed researcher-lesion flags required")
    options = real_affordances(bridge)
    if not options:
        raise RuntimeError("World offers no source-feasible bodily actions")
    observed = bridge.observe()
    memory = bridge.doctor.brain.store.get_memory(observed["memory_id"])
    if (memory is None or not memory["active"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or not memory["source"].startswith("laboratory-home:observe:")
            or memory["text"] != observed["subject"]["inner"]):
        raise PermissionError("No original first-person physical perception")
    # One original neural substrate advances before situating physical
    # affordances. The recurrent dynamics, not a second controller, are used.
    from .organs import NoesisOrgan
    NoesisOrgan(bridge.doctor).deliberate(host_trigger="m2_daily_opportunity")
    outcomes = _verified_work_outcomes(bridge) if use_consequences else ()
    choice = select_with_original_noesis(
        bridge.doctor.brain,
        observation_memory_id=observed["memory_id"],
        eligible_read_memory_ids=(),
        feasible_actions=options,
        learning_enabled=True, neural_prior_enabled=True,
        outcome_learning_enabled=use_consequences,
        eligible_outcome_memory_ids=outcomes,
        author_day_goal=author_goal,
    )
    return DailyChoice(choice["policy_decision_id"], choice["selected_action"],
                       observed["memory_id"], options)



def _complete_daily_motor(bridge: DoctorHomeBridge, policy_id: str,
                          event_id: str, memory_id: str) -> None:
    """Record only the already source-admitted action in the ONE BrainStore."""
    store = bridge.doctor.brain.store
    with store.transaction() as db:
        row = db.execute(
            "SELECT selected_action,state_pressure_json FROM policy_decisions "
            "WHERE id=? AND trigger='noesis_situated_choice'", (policy_id,)
        ).fetchone()
        if row is None:
            raise PermissionError("Daily motor lost its original Noesis policy")
        evidence = json.loads(row["state_pressure_json"])
        if (evidence.get("selector_authority") != "original_noesis"
                or evidence.get("motor_authorization") != "authorized"
                or evidence.get("motor_event_id") != event_id
                or evidence.get("motor_memory_id") not in (None, memory_id)):
            raise PermissionError("Daily motor completion does not match original policy")
        evidence["motor_completion"] = "admitted"
        evidence["motor_memory_id"] = memory_id
        db.execute("UPDATE policy_decisions SET state_pressure_json=? WHERE id=?",
                   (json.dumps(evidence, sort_keys=True), policy_id))
        store.bump_state_version(db)


def reconcile_pending_daily_action(bridge: DoctorHomeBridge) -> tuple[dict, ...]:
    """Cold-replay an authorized original-Noesis action without a new choice.

    A kill after the policy reservation, original physical commit or memory
    admission must not create another action. The original Laboratory bridge
    verifies the same event ID and source, then admits the one lived memory.
    If an uncommitted action's world has changed, refuse to act on stale
    perception. This is one-action crash recovery, NOT sustained goal agency.
    """
    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("Original Laboratory bridge required for recovery")
    from .lab_home_bridge import _ACTION_DOMAINS
    store = bridge.doctor.brain.store
    with store.connect() as db:
        rows = db.execute(
            "SELECT id,selected_action,state_pressure_json FROM policy_decisions "
            "WHERE trigger='noesis_situated_choice' ORDER BY rowid"
        ).fetchall()
    pending = []
    for row in rows:
        evidence = json.loads(row["state_pressure_json"])
        if (evidence.get("motor_authorization") != "authorized"
                or evidence.get("motor_completion") == "admitted"):
            continue
        action = row["selected_action"]
        event_id = evidence.get("motor_event_id")
        if (action not in NEURAL_AFFORDANCE_MAP
                or action not in _ACTION_DOMAINS
                or evidence.get("selector_authority") != "original_noesis"
                or evidence.get("physical_authority") != "none"
                or type(event_id) is not str
                or type(evidence.get("observation_memory_id")) is not str):
            raise PermissionError("Unverifiable pending daily motor reservation")
        with bridge.world._open() as db:
            table = _ACTION_DOMAINS[action]
            table_exists = db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (table,)
            ).fetchone() is not None
            world_committed = table_exists and db.execute(
                "SELECT 1 FROM " + table + " WHERE event_id=?",
                (event_id,)
            ).fetchone() is not None
        if not world_committed:
            observed = bridge.observe()
            if observed["memory_id"] != evidence["observation_memory_id"]:
                raise RuntimeError("Pending daily action has stale physical observation")
            if action not in real_affordances(bridge):
                raise RuntimeError("Pending daily action no longer physically feasible")
        receipt = bridge.act(action, event_id=event_id, **physical_args(action))
        if receipt["status"] not in ("admitted", "already_admitted"):
            raise RuntimeError("Recovered daily motor lacks original world admission")
        _complete_daily_motor(bridge, row["id"], event_id, receipt["memory_id"])
        pending.append({
            "policy_decision_id": row["id"], "action": action,
            "event_id": event_id, "memory_id": receipt["memory_id"],
            "status": receipt["status"], "new_goal_selected": False,
            "original_world_receipt_replayed": bool(world_committed),
        })
    return tuple(pending)


def act_on_noesis_choice(bridge: DoctorHomeBridge, choice: DailyChoice, *,
                         event_id: str, authorized: bool = False) -> dict:
    """No action parameter: execute only the committed original Noesis winner."""
    if authorized is not True:
        raise PermissionError("Subject's cognitive preference is not motor permission")
    if type(choice) is not DailyChoice:
        raise TypeError("Actual original Noesis decision required")
    store = bridge.doctor.brain.store
    with store.connect() as db:
        row = db.execute(
            "SELECT id,selected_action,trigger,policy_version,state_pressure_json "
            "FROM policy_decisions WHERE id=?", (choice.policy_id,)
        ).fetchone()
        latest = db.execute(
            "SELECT id FROM policy_decisions WHERE trigger='noesis_situated_choice' "
            "ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
    if row is None or latest is None or latest["id"] != choice.policy_id:
        raise PermissionError("Missing or stale original subject choice")
    evidence = json.loads(row["state_pressure_json"])
    if (row["trigger"] != "noesis_situated_choice"
            or row["selected_action"] != choice.action
            or evidence.get("selector_authority") != "original_noesis"
            or evidence.get("physical_authority") != "none"
            or evidence.get("motor_event_id") not in (None, event_id)):
        raise PermissionError("No genuine original-Noesis action authority")
    if choice.action not in real_affordances(bridge):
        raise PermissionError("World no longer offers the selected physical task")
    observed = bridge.observe()
    if observed["memory_id"] != evidence.get("observation_memory_id"):
        raise PermissionError("World observation changed after Noesis selected")
    if evidence.get("motor_authorization") == "authorized":
        raise PermissionError("This decision already owns another work attempt")
    # Transactionally bind the original choice to exactly one future world
    # event before crossing the original DoctorHomeBridge intent authority.
    with store.transaction() as db:
        row = db.execute(
            "SELECT state_pressure_json FROM policy_decisions WHERE id=?",
            (choice.policy_id,),
        ).fetchone()
        if row is None:
            raise PermissionError("Original decision disappeared")
        updated = json.loads(row["state_pressure_json"])
        if updated.get("motor_event_id") not in (None, event_id):
            raise PermissionError("Decision bound to another event")
        updated["motor_event_id"] = event_id
        updated["motor_authorization"] = "authorized"
        db.execute("UPDATE policy_decisions SET state_pressure_json=? WHERE id=?",
                   (json.dumps(updated, sort_keys=True), choice.policy_id))
        store.bump_state_version(db)
    actual = bridge.act(choice.action, event_id=event_id, **physical_args(choice.action))
    if actual["status"] not in ("admitted", "already_admitted"):
        raise RuntimeError("Actual Laboratory action not source-admitted")
    _complete_daily_motor(bridge, choice.policy_id, event_id, actual["memory_id"])
    return {"policy_decision_id": choice.policy_id, "action": choice.action,
            "event_id": event_id, "memory_id": actual["memory_id"],
            "status": actual["status"]}
