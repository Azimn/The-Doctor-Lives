"""Four-arm comparison: native Doctor, native+motives, motive lesion, text rule.

All arms use the existing PretoriusBrainPort, a fixed pinned physical Laboratory,
identical first-person scene frame per paired condition, and host-pathfinding.
This is a regression-oriented authored pilot, NOT Article qualification.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile

from .chassis import PretoriusBrainPort
from .lab_home_bridge import DoctorHomeBridge, _hash
from .neural import DEFAULT_CONFIG
from .home_choice_probe import (
    CASES, EXPECTED, MAX_ACTIONS, NATIVE_TO_TASK,
    _setup_case, _execute, simple_choice,
)
from .home_motive_queue import HomeActivityQueue

ARMS = ("native_only", "native_plus_motives", "motives_body_lesion",
        "simple_firstperson_rules")
SCHEMA = "pretorius-home-motives-comparison.v0.1"


def _meaningful_change(task, before, after):
    return {
        "experiment": after["experiments"] > before["experiments"],
        "repair": after["apparatus"] > before["apparatus"],
        "rest": after["fatigue"] < before["fatigue"],
        "tea": after["thirst"] < before["thirst"],
        "meal": after["hunger"] < before["hunger"],
        "clean": after["cleanliness"]["room:sanctum"] <
                 before["cleanliness"]["room:sanctum"],
    }[task]


def run_motive_pilot():
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.subject_port import SubjectPort
    rows = []
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
               input_degree=4, action_population_size=8)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for case in CASES:
            for arm in ARMS:
                base = root / case / arm
                base.mkdir(parents=True, exist_ok=True)
                world = SpatialHabitat.create(base / "lab.sqlite3")
                home = HomeLife(world)
                home.initialize()
                rhythm = DailyRhythm(world)
                rhythm.initialize()
                _setup_case(rhythm, home, case)
                starting = deepcopy(rhythm.audit_state())
                doctor = PretoriusBrainPort(base / "doctor", neural_config=cfg)
                bridge = DoctorHomeBridge(doctor, SubjectPort(world),
                                          authorized=True)
                if arm in ("native_plus_motives", "motives_body_lesion"):
                    queue = HomeActivityQueue(bridge, base / "activity.sqlite3")
                    plan = queue.start("pilot", body_enabled=(
                        arm == "native_plus_motives"))
                    chosen = plan["task"]
                    frame_hash = plan["choices"]["frame_sha256"]
                    selected = plan["choices"]["native_selected"]
                    decision_id = plan["choices"]["native_policy_id"]
                    action_counter = 0
                    state = "active"
                    for n in range(MAX_ACTIONS):
                        outcome = queue.step("pilot")
                        if outcome["subject"] is not None:
                            action_counter += 1
                        state = outcome["status"]
                        if state != "active":
                            break
                    verification = queue.verify("pilot")
                    after = rhythm.audit_state()
                    did_work = (state == "completed" and
                                _meaningful_change(chosen, starting, after))
                    step_receipts = verification["source_receipts"]
                    error = None if state == "completed" else state
                    arm_procedure = "source_neural_scores+bounded_homeostatic_utilities"
                    if arm == "motives_body_lesion":
                        arm_procedure += "_disabled"
                else:
                    witnessed = bridge.observe()
                    frame = witnessed["subject"]["inner"]
                    frame_hash = _hash(frame)
                    # Equal opportunity for real Doctor cognition to all arms;
                    # the literal-rule baseline does not use its result.
                    policy = bridge.request_cognition(
                        trigger="home_motive_comparison")
                    selected = policy["selected_action"]
                    decision_id = policy["policy_decision_id"]
                    if arm == "native_only":
                        chosen = NATIVE_TO_TASK[selected]
                        arm_procedure = "native_recurrent_fixed_task_map"
                    else:
                        chosen = simple_choice(frame)
                        arm_procedure = "cheap_firstperson_literal_rules"
                    from .home_choice_probe import _execute
                    physical = _execute(bridge, chosen, prefix=f"{case}-{arm}")
                    after = rhythm.audit_state()
                    did_work = bool(physical["completed"])
                    action_counter = physical["actions_used"]
                    step_receipts = action_counter if did_work else None
                    error = physical["denied_reason"]
                row = {
                    "case": case, "arm": arm,
                    "procedure": arm_procedure,
                    "starting_state_sha256": _hash(starting),
                    "firstperson_frame_sha256": frame_hash,
                    "neural_selected_tendency": selected,
                    "neural_policy_decision_id": decision_id,
                    "task_proposed": chosen, "expected_task": EXPECTED[case],
                    "physical_goal_occurred": did_work,
                    "expected_task_completed": (
                        did_work and chosen == EXPECTED[case]),
                    "physical_actions": action_counter,
                    "max_actions": MAX_ACTIONS,
                    "receipt_count": step_receipts,
                    "error": error,
                }
                if row["physical_actions"] > MAX_ACTIONS:
                    raise AssertionError("Fair action budget exceeded")
                rows.append(row)
    matched = []
    for case in CASES:
        cases = [x for x in rows if x["case"] == case]
        if len(set(x["starting_state_sha256"] for x in cases)) != 1:
            raise AssertionError("World conditioning differed across arms")
        if len(set(x["firstperson_frame_sha256"] for x in cases)) != 1:
            raise AssertionError("First-person observations differed across arms")
        matched.append({"case": case, "matching_physical_world": True,
                        "matching_first_person_observation": True,
                        "proposals": {x["arm"]: x["task_proposed"] for x in cases}})
    summary = {arm: sum(x["expected_task_completed"] for x in rows
                        if x["arm"] == arm) for arm in ARMS}
    return {
        "schema": SCHEMA, "qualification": "UNASSESSABLE",
        "research_grade": "authored exploratory engineering pilot; one seeded small Doctor per case; no held-out preregistered transfer",
        "arms": ARMS, "cases": CASES, "action_budget": MAX_ACTIONS,
        "totals": summary, "matched_conditions": matched,
        "observations": rows,
        "claim_boundary": (
            "The fixed homeostatic controller is an external policy contribution "
            "to the Doctor's original neural tendencies, not an emergent choice "
            "from the recurrent substrate. Neither this pilot nor a 4/4 score "
            "justifies passing any Article. The simple rules baseline may tie."
        ),
    }
