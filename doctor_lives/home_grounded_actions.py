"""Physical affordance-grounded home activity arbitration, with honest baselines.

An opt-in HOST controller. The real PretoriusBrainPort remains the single
cognition/identity/memory owner; the original Laboratory owns all physics and
action receipts. The Doctor's generic neural symbols are bounded *bias only*,
never magical home commands. No second identity, no invented preferences.

IMPORTANT: This does not schedule itself and does not grant arbitrary tools.
An authorized host must explicitly invoke choose() and execute().
"""
from __future__ import annotations

from .home_motive_queue import TASKS, motive_scores, plan_steps
from .home_native_practice import NATIVE_TO_HOUSEHOLD
from .lab_home_bridge import DoctorHomeBridge, _hash

RULES = "doctor-home-grounded-affordance.v0.1"
ARMS = ("legacy_mapped", "grounded_doctor", "grounded_simple")


def physically_available(state: dict, station: str):
    """Dry-run every proposed *complete* existing task using Lab physics.

    This reads engineering-side state only and never crosses the Doctor's
    first-person ingress. Even 'prepare meal then eat' must be feasible.
    """
    from pretorius_lab.daily_rhythm import transition
    from pretorius_lab.physics import Conflict, LabError
    available, rejected = {}, {}
    for task in TASKS:
        try:
            steps = plan_steps(state, station, task)
            # Walking changes pose but does not teleport or change clock
            # in pinned original Laboratory (turn-cost is a separate pilot).
            position = station
            draft = state
            for step in steps:
                op, args = step["op"], step["args"]
                if op == "walk":
                    from .home_choice_probe import _shortest_route
                    route = _shortest_route(position, args["station"])
                    if route != (args["station"],):
                        raise ValueError("Proposed walk is not adjacent")
                    position = args["station"]
                else:
                    draft, _ = transition(draft, op, args, position)
            available[task] = steps
        except (Conflict, LabError, RuntimeError, ValueError) as exc:
            rejected[task] = type(exc).__name__ + ": " + str(exc)[:140]
    return {"available": available, "rejected": rejected}


def physical_stamp(bridge: DoctorHomeBridge):
    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("A real authorized DoctorHomeBridge is required")
    with bridge.world._open() as db:
        return bridge._physical_stamp(db)


def choose(bridge: DoctorHomeBridge, *, arm: str):
    """Observe actual first-person source and get one real cognition receipt.

    The cheap arm still invokes same existing Doctor cognition for matched
    observation/memory exposure; it merely ignores neural action weights.
    """
    if arm not in ARMS:
        raise ValueError("Unregistered controller arm")
    observed = bridge.observe()
    frame = observed["subject"]["inner"]
    if not frame.startswith(("I ", "My ")):
        raise RuntimeError("Only coherent first-person perception is admitted")
    cognition = bridge.request_cognition(trigger="grounded_home_action")
    if not cognition.get("policy_decision_id"):
        raise RuntimeError("Cognition lacked a durable policy decision")
    state = bridge.subject.rhythm.audit_state()
    station = bridge.subject.embodied.verify()["station"]
    availability = physically_available(state, station)
    if arm == "legacy_mapped":
        # The original Article 8 failure, unchanged: avoid→tea.
        task = NATIVE_TO_HOUSEHOLD[cognition["selected_action"]]
        # The legacy controller did not predict feasibility. This plan is
        # used for evidence only, not to veto its selected action.
        steps = [{"op": "brew_tea" if task == "tea" else "clean", "args": {}}]
        scores = None
    else:
        preference = (cognition["action_scores"]
                      if arm == "grounded_doctor" else None)
        scores = motive_scores(state, preference)["scores"]
        choices = availability["available"]
        task = (sorted(choices, key=lambda t: (-scores[t], TASKS.index(t)))[0]
                if choices else None)
        steps = choices[task] if task is not None else []
    return {
        "schema": RULES, "arm": arm,
        "first_person_sha256": _hash(frame),
        "perception_memory_id": observed["memory_id"],
        "neural_policy_receipt": cognition["policy_decision_id"],
        "native_generic_action": cognition["selected_action"],
        "state_sha256": _hash(state), "physical_stamp": physical_stamp(bridge),
        "station": station, "selected_task": task,
        "steps": steps, "available_tasks": tuple(availability["available"]),
        "unavailable_tasks": availability["rejected"],
        "numeric_action_scores": scores,
    }


def execute(bridge: DoctorHomeBridge, decision: dict, *, prefix: str):
    """Execute only from same validated source; no silent alternate/refill."""
    if not isinstance(decision, dict) or decision.get("schema") != RULES:
        raise ValueError("Unknown grounded decision")
    if not isinstance(prefix, str) or not prefix.isascii() or not prefix.isalnum():
        raise ValueError("Safe bounded action prefix required")
    if len(prefix) > 30:
        raise ValueError("Action prefix is too long")
    if (decision["physical_stamp"] != physical_stamp(bridge)
            or decision["state_sha256"] != _hash(
                bridge.subject.rhythm.audit_state())
            or decision["station"] != bridge.subject.embodied.verify()["station"]):
        raise RuntimeError("World changed; reobserve and choose again")
    task = decision["selected_task"]
    if task is None:
        return {"completed": False, "abstained": True,
                "denied_reason": "no_supported_activity",
                "receipts": [], "actual_effect": None}
    if decision["arm"] != "legacy_mapped":
        active = physically_available(
            bridge.subject.rhythm.audit_state(), decision["station"])["available"]
        if task not in active or active[task] != decision["steps"]:
            raise RuntimeError("Proposed household action is no longer feasible")
    initial = bridge.subject.rhythm.audit_state()
    receipts = []
    try:
        for n, step in enumerate(decision["steps"], 1):
            eid = f"{prefix}{n}"
            action = bridge.act(step["op"], event_id=eid, **step["args"])
            if not action["subject"]["inner"].startswith(("I ", "My ")):
                raise RuntimeError("Physical action did not reach Doctor as experience")
            receipts.append({"op": step["op"], "event_id": eid,
                             "subject": action["subject"]["inner"]})
    except Exception as exc:
        # World may have partially changed after a prior valid move; never
        # roll it back or claim the plan completed.
        bridge.subject.verify()
        return {"completed": False, "abstained": False,
                "denied_reason": type(exc).__name__ + ": " + str(exc)[:180],
                "receipts": receipts, "actual_effect": None}
    after = bridge.subject.rhythm.audit_state()
    benefit = {
        "tea": after["thirst"] < initial["thirst"],
        "tidy": after["chores"] > initial["chores"],
        "clean": after["chores"] > initial["chores"],
        "experiment": after["experiments"] > initial["experiments"],
        "repair": after["repairs"] > initial["repairs"],
        "meal": after["hunger"] < initial["hunger"],
        "rest": after["fatigue"] < initial["fatigue"],
    }[task]
    proof = bridge.subject.verify()
    return {
        "completed": True, "abstained": False, "denied_reason": None,
        "receipts": receipts, "actual_effect": benefit,
        "world_replay_verified": proof["verified"],
        "final_state_sha256": _hash(after),
    }
