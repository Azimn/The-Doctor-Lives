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
from .noesis_situated_choice import (DAILY_BODY_VERSION, NEURAL_AFFORDANCE_MAP,
                                    select_with_original_noesis)
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


# The established home topology supplies only physical routing, just as
# the existing book and rest pursuits do. No remote supply or object state
# is used as knowledge. Each selected route advances ONE adjacent hop.
_ROUTE_TARGETS = {"seek_kitchen": "station:kitchen",
                  "seek_bedroom": "station:bedroom"}


def _daily_binding(action: str, evidence: dict) -> tuple[str, dict]:
    """Recover exact recorded motor arguments; legacy local actions stay valid."""
    if action in _ROUTE_TARGETS:
        from pretorius_lab.embodied_access import STATIONS
        args = evidence.get("motor_args")
        if (evidence.get("motor_op") != "walk" or type(args) is not dict
                or set(args) != {"station"} or args["station"] not in STATIONS):
            raise PermissionError("Invalid durable household route binding")
        return "walk", args
    if action not in NEURAL_AFFORDANCE_MAP:
        raise PermissionError("Unknown daily motor")
    args = physical_args(action)
    if (evidence.get("motor_op", action) != action
            or evidence.get("motor_args", args) != args):
        raise PermissionError("Altered daily motor binding")
    return action, args


def _motor_for_offer(bridge: DoctorHomeBridge, action: str) -> tuple[str, dict]:
    if action in _ROUTE_TARGETS:
        from .lab_endogenous_book_task import EndogenousBookPursuit
        at = bridge.subject.embodied.verify()["station"]
        hop = EndogenousBookPursuit._route(at, _ROUTE_TARGETS[action])
        if hop is None:
            raise PermissionError("No adjacent household route is available")
        return "walk", {"station": hop}
    return action, physical_args(action)


def _is_daily_reservation(action: str, evidence: dict) -> bool:
    # New daily decisions have a distinct policy version. Older dedicated
    # work reservations are recovered by their original work host, not by
    # the daily motor path. Legacy non-work daily reservations stay readable.
    return (evidence.get("version") == DAILY_BODY_VERSION
            or action not in ("repair", "experiment")
            or evidence.get("motor_scope") == "daily")


def pending_daily_action_ids(bridge: DoctorHomeBridge) -> tuple[str, ...]:
    """Read-only canonical reservations awaiting world/memory reconciliation.

    This does not execute a physical action or invent a replacement goal.
    The caller must have separate world authorization before replay.
    """
    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("Original Laboratory bridge required for pending-action audit")
    with bridge.doctor.brain.store.connect() as db:
        rows = db.execute(
            "SELECT id,selected_action,state_pressure_json FROM policy_decisions "
            "WHERE trigger='noesis_situated_choice' ORDER BY rowid"
        ).fetchall()
    pending = []
    for row in rows:
        evidence = json.loads(row["state_pressure_json"])
        if (_is_daily_reservation(row["selected_action"], evidence)
                and evidence.get("motor_authorization") == "authorized"
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


def daily_affordances(bridge: DoctorHomeBridge, observation: dict) -> tuple[str, ...]:
    """Concrete local operations plus need-relevant reviewed household routes."""
    from .noesis_interoception import perceived_regulatory_pressure
    from .lab_endogenous_book_task import EndogenousBookPursuit
    memory = bridge.doctor.brain.store.get_memory(observation["memory_id"])
    if (memory is None or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or not memory["source"].startswith("laboratory-home:observe:")
            or memory["text"] != observation["subject"]["inner"]):
        raise PermissionError("Household offers require admitted perception")
    options = list(real_affordances(bridge))
    pressure, _ = perceived_regulatory_pressure(
        memory["text"], tuple(_ROUTE_TARGETS))
    at = bridge.subject.embodied.verify()["station"]
    for action, target in _ROUTE_TARGETS.items():
        if pressure[action] > 0 and EndogenousBookPursuit._route(at, target) is not None:
            options.append(action)
    return tuple(sorted(options))


def offer_daily_opportunity(bridge: DoctorHomeBridge, *, author_goal: bool = True,
                            use_consequences: bool = True,
                            enable_habits: bool = False) -> DailyChoice:
    """One independent Noesis choice, without any operator action argument."""
    if (type(author_goal) is not bool or type(use_consequences) is not bool
            or type(enable_habits) is not bool):
        raise TypeError("Typed researcher-lesion flags required")
    if pending_daily_action_ids(bridge):
        raise RuntimeError("A pending daily motor must reconcile before another choice")
    observed = bridge.observe()
    options = daily_affordances(bridge, observed)
    if not options:
        raise RuntimeError("World offers no source-feasible bodily actions")
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
        interoception_enabled=True,
        habit_bridge=bridge if enable_habits else None,
    )
    return DailyChoice(choice["policy_decision_id"], choice["selected_action"],
                       observed["memory_id"], options)



def compete_with_commitment(session, *, commitment_key: str, goal_id: str,
                            allow_native_rest: bool = False):
    """Compete over actual bodily needs and one existing, verified intention.

    The current original goal is neither replaced nor completed by this
    opportunity. No physical continuation command exists. If Noesis chooses
    continuation, the caller resumes the existing goal's own motor procedure.
    If a bodily action wins, its usual exact daily motor reservation applies.
    """
    from .lab_six_organ_session import SixOrganLaboratoryCycle
    from .noesis_interoception import perceived_regulatory_pressure
    from .organs import CognitiveProposal
    from .noesis_situated_choice import _verified_active_commitment
    if type(allow_native_rest) is not bool:
        raise TypeError("Native restorative intention permission must be explicit")
    if type(session) is not SixOrganLaboratoryCycle:
        raise TypeError("Actual same-brain six-organ session required")
    bridge = session.bridge
    if pending_daily_action_ids(bridge):
        raise RuntimeError("Prior daily motor must reconcile")
    observed = bridge.observe()
    def bodily_pressure(observed):
        options = daily_affordances(bridge, observed)
        contributions, _ = perceived_regulatory_pressure(
            observed["subject"]["inner"], options)
        return {a: contributions[a] for a in options if contributions[a] > 0.0}
    pressure = bodily_pressure(observed)
    if not pressure:
        return None
    cycle = session.cycle(authorized_world_action=False)
    if len(cycle.ports_used) != 6 or cycle.subjective_delivery_count != 1:
        raise RuntimeError("Incomplete six-organ commitment opportunity")
    # The existing native AVOID tendency may originate an independent
    # restorative intention while a meaningful project is still active.
    # A fresh authenticated fatigue cue and genuine feasible rest/route
    # must be at least as pressing as other observed bodily alternatives.
    # Do not turn a sleep choice into a rest or reuse a stale policy.
    rest_pressure = max(pressure.get("rest", 0), pressure.get("seek_bedroom", 0))
    if (allow_native_rest and cycle.selected_tendency == "avoid"
            and rest_pressure > 0 and rest_pressure >= max(pressure.values())):
        brain = bridge.doctor.brain
        _verified_active_commitment(brain, (commitment_key, goal_id))
        with brain.store.connect() as db:
            origin = db.execute(
                "SELECT id,selected_action,trigger FROM policy_decisions ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            thought = db.execute("SELECT id FROM thoughts WHERE generated_by=?",
                                 ("neural_policy:" + origin["id"],)).fetchall()
        if (origin["trigger"] != "six_organ_lab_cycle"
                or origin["selected_action"] != "avoid" or len(thought) != 1):
            raise PermissionError("Rest interruption lacks current original avoid policy")
        return CognitiveProposal(origin["id"], thought[0]["id"], "avoid")
    observed = bridge.observe()
    alternatives = tuple(bodily_pressure(observed))
    if not alternatives:
        return None
    options = tuple(sorted((*alternatives, "continue_commitment")))
    choice = select_with_original_noesis(
        bridge.doctor.brain,
        observation_memory_id=observed["memory_id"],
        eligible_read_memory_ids=(), feasible_actions=options,
        author_day_goal=False, interoception_enabled=True,
        active_commitment=(commitment_key, goal_id),
    )
    return DailyChoice(choice["policy_decision_id"], choice["selected_action"],
                       observed["memory_id"], options)


def _complete_daily_motor(bridge: DoctorHomeBridge, policy_id: str,
                          event_id: str, memory_id: str) -> None:
    """Atomically admit one original motor and its verified bodily recovery.

    A genuine daily rest is a sixty-minute ORIGINAL Laboratory event. Its
    source-backed lived memory licenses six existing ten-minute canonical
    relaxation opportunities, exactly once. This is not a new Noesis choice,
    an invented rest, or a change to physical fatigue/finite supplies.
    The same transaction commits both the original motor completion and
    original-brain homeostasis, including after a cold recovery.
    """
    from .lab_home_bridge import _row
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
        if evidence.get("motor_completion") == "admitted":
            if evidence.get("motor_memory_id") != memory_id:
                raise PermissionError("Completed motor cannot change its lived memory")
            return  # Cold replay cannot relax the same body a second time.
        if evidence.get("motor_completion") not in (None, "pending"):
            raise PermissionError("Unrecognized original motor completion state")

        # Every physical daily action, not only rest, must have the exact
        # original world receipt and matching canonical first-person memory.
        action = row["selected_action"]
        op, args = _daily_binding(action, evidence)
        world = bridge.subject.verify()
        from .lab_home_bridge import _ACTION_DOMAINS
        with bridge.world._open() as world_db:
            original, event_hash = _row(world_db, _ACTION_DOMAINS[op], event_id)
            bridge._check_action_proof(op, args, original)
            if op == "walk":
                domestic, _ = _row(world_db, "domestic_events", "motion:" + event_hash[:32])
                if domestic.get("body_cursor") != event_hash:
                    raise PermissionError("Household movement lacks original domestic consequence")
                frame = domestic.get("subject")
            else:
                frame = original.get("subject")
        memory = db.execute(
            "SELECT source,text,evidence_class,active,external FROM memories WHERE id=?",
            (memory_id,),
        ).fetchone()
        expected = frame.get("inner") if type(frame) is dict else None
        # SubjectPort appends verified rhythm perception to movement, and
        # adapts the historical advance wording. The original body hash
        # and domestic source must still match.
        if op == "advance" and type(expected) is str:
            expected = "I notice time passing. " + expected
        exact_text = memory is not None and (
            memory["text"] == expected or
            (op == "walk" and type(expected) is str
             and memory["text"].startswith(expected + " "))
        )
        if (original.get("event_id") != event_id
                or original.get("world_epoch") != world["world_epoch"]
                or (action == "rest" and original.get("station") != "station:bedroom")
                or memory is None or memory["active"] != 1 or memory["external"]
                or memory["evidence_class"] != "lived_runtime_memory"
                or memory["source"] != "laboratory-home:action:" + event_hash
                or not exact_text):
            label = "rest" if action == "rest" else "motor"
            raise PermissionError(
                f"Daily {label} lacks its matching original physical/lived receipt"
            )
        if action == "rest":
            brain = bridge.doctor.brain
            for _ in range(6):
                tick = store.advance_tick(db)
                brain._relax_needs(db, tick)
                brain._update_commitments_due(db, tick)

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
    if len(pending_daily_action_ids(bridge)) > 1:
        raise RuntimeError("Multiple pending daily motors require integrity review")
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
        action = row["selected_action"]
        if (not _is_daily_reservation(action, evidence)
                or evidence.get("motor_authorization") != "authorized"
                or evidence.get("motor_completion") == "admitted"):
            continue
        event_id = evidence.get("motor_event_id")
        op, args = _daily_binding(action, evidence)
        if (op not in _ACTION_DOMAINS
                or evidence.get("selector_authority") != "original_noesis"
                or evidence.get("physical_authority") != "none"
                or type(event_id) is not str
                or type(evidence.get("observation_memory_id")) is not str):
            raise PermissionError("Unverifiable pending daily motor reservation")
        with bridge.world._open() as db:
            table = _ACTION_DOMAINS[op]
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
            if (action not in daily_affordances(bridge, observed)
                    or _motor_for_offer(bridge, action) != (op, args)):
                raise RuntimeError("Pending daily action no longer physically feasible")
        receipt = bridge.act(op, event_id=event_id, **args)
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
    if choice.action == "continue_commitment":
        raise PermissionError("Continuation is a cognitive decision, not a world motor")
    if pending_daily_action_ids(bridge):
        raise PermissionError("Recover the prior daily motor before authorizing another")
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
    observed = bridge.observe()
    if observed["memory_id"] != evidence.get("observation_memory_id"):
        raise PermissionError("World observation changed after Noesis selected")
    if choice.action not in daily_affordances(bridge, observed):
        raise PermissionError("World no longer offers the selected physical task")
    op, args = _motor_for_offer(bridge, choice.action)
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
        prior_rows = db.execute(
            "SELECT state_pressure_json FROM policy_decisions "
            "WHERE trigger='noesis_situated_choice' AND id!=?",
            (choice.policy_id,),
        ).fetchall()
        if any(json.loads(prior["state_pressure_json"]).get("motor_event_id") == event_id
               for prior in prior_rows):
            raise PermissionError("Daily event ID already bound to another Noesis decision")
        updated["motor_event_id"] = event_id
        updated["motor_authorization"] = "authorized"
        updated["motor_scope"] = "daily"
        updated["motor_op"] = op
        updated["motor_args"] = args
        db.execute("UPDATE policy_decisions SET state_pressure_json=? WHERE id=?",
                   (json.dumps(updated, sort_keys=True), choice.policy_id))
        store.bump_state_version(db)
    actual = bridge.act(op, event_id=event_id, **args)
    if actual["status"] not in ("admitted", "already_admitted"):
        raise RuntimeError("Actual Laboratory action not source-admitted")
    _complete_daily_motor(bridge, choice.policy_id, event_id, actual["memory_id"])
    return {"policy_decision_id": choice.policy_id, "action": choice.action,
            "motor_op": op, "motor_args": args,
            "event_id": event_id, "memory_id": actual["memory_id"],
            "status": actual["status"]}
