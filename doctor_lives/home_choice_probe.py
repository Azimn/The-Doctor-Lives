"""Exploratory four-condition real-Doctor versus receipt-rule household action pilot.

Every arm receives the same SOURCE-BACKED first-person Laboratory observation.
The real Doctor's existing ten-action neural policy selects an ABSTRACT
tendency; a FROZEN, arbitrary documented mapping translates that tendency
to one of four household tasks. The matched simple controller uses only the
identical first-person text. Host pathfinding and lighting are shared assistive
mechanisms, not attributed to subject cognition.

NO Article pass: equal sensory input is not equal autobiographical memory,
the mapping is untrained and environment-specific, and conditions are authored.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from pathlib import Path
import json
import tempfile

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge, _hash
from doctor_lives.neural import ACTIONS, DEFAULT_CONFIG

SCHEMA = "pretorius-home-choice-pilot.v0.1"
CASES = ("ordinary_work", "worn_apparatus", "exhaustion", "thirst")
ARMS = ("real_doctor_policy", "simple_firstperson_rule")
NATIVE_TO_TASK = {
    "explore": "experiment", "challenge": "experiment",
    "approach": "tea", "avoid": "rest", "cooperate": "tea",
    "dominate": "repair", "create": "experiment",
    "persist": "repair", "conceal": "rest", "comply": "repair",
}
TARGET_STATIONS = {"experiment": "station:bench", "repair": "station:bench",
                   "rest": "station:bedroom", "tea": "station:kitchen"}
EXPECTED = {"ordinary_work": "experiment", "worn_apparatus": "repair",
            "exhaustion": "rest", "thirst": "tea"}
MAX_ACTIONS = 9


def simple_choice(subject_text: str) -> str:
    """A deliberately strong, fixed cheap controller with NO numeric internals."""
    if not isinstance(subject_text, str) or not subject_text.startswith("I "):
        raise ValueError("The baseline may receive only ordinary first-person input")
    # Order fixes precedence in competing-need scenarios.
    if "instruments look worn" in subject_text or "apparatus needs" in subject_text:
        return "repair"
    if "feel worn out" in subject_text:
        return "rest"
    if "mouth is dry" in subject_text:
        return "tea"
    return "experiment"


def _shortest_route(start, goal):
    """Fixed host transport helper, not a model-authored travel decision."""
    from pretorius_lab.embodied_access import STATIONS
    if start not in STATIONS or goal not in STATIONS:
        raise ValueError("Unrecognized room station")
    routes = deque([(start, ())])
    visited = set()
    while routes:
        pos, route = routes.popleft()
        if pos == goal:
            return route
        if pos in visited:
            continue
        visited.add(pos)
        for adjacent in sorted(STATIONS[pos][1]):
            if adjacent not in visited:
                routes.append((adjacent, (*route, adjacent)))
    raise ValueError("The required room is physically unreachable")


def _setup_case(life, home, case: str):
    """Engineer-authorized physical conditioning, before cognitive evaluation."""
    if case == "ordinary_work":
        return
    if case == "worn_apparatus":
        home.walk("station:center")
        home.walk("station:bench")
        life.act("experiment", event_id="setup-experiment-a")
        life.act("experiment", event_id="setup-experiment-b")
    elif case in ("exhaustion", "thirst"):
        repetitions = 5 if case == "exhaustion" else 3
        for i in range(repetitions):
            life.advance(240, event_id="setup-elapsed-" + str(i))
    else:
        raise ValueError("Unknown authored case")


def _execute(bridge, choice, prefix):
    from pretorius_lab.daily_rhythm import _can_see
    from pretorius_lab.embodied_access import STATIONS
    if choice not in TARGET_STATIONS:
        raise ValueError("Unknown fixed task proposal")
    intended = TARGET_STATIONS[choice]
    route = _shortest_route(bridge.subject.embodied.verify()["station"], intended)
    used, trace = 0, []
    before = bridge.subject.rhythm.audit_state()
    try:
        for loc in route:
            if used >= MAX_ACTIONS:
                raise RuntimeError("Finite host action budget exceeded in transit")
            used += 1
            bridge.act("walk", event_id=f"{prefix}-step-{used}", station=loc)
            trace.append("walk")
        state = bridge.subject.rhythm.audit_state()
        room = STATIONS[intended][0]
        if choice != "rest" and not _can_see(state, room):
            if used >= MAX_ACTIONS:
                raise RuntimeError("Budget exhausted before illumination")
            used += 1
            bridge.act("light", event_id=f"{prefix}-lamp-{used}")
            trace.append("light")
        if used >= MAX_ACTIONS:
            raise RuntimeError("No authorization left for the intended task")
        used += 1
        op = "brew_tea" if choice == "tea" else ("sleep" if choice == "rest" else choice)
        event = bridge.act(op, event_id=f"{prefix}-work-{used}")
        trace.append(op)
        after = bridge.subject.rhythm.audit_state()
        changed = {
            "experiment": after["experiments"] > before["experiments"],
            "repair": after["apparatus"] > before["apparatus"],
            "rest": after["fatigue"] < before["fatigue"],
            "tea": after["thirst"] < before["thirst"],
        }[choice]
        return {"completed": changed, "actions_used": used,
                "host_assisted_actions": trace,
                "experience": event["subject"]["inner"],
                "denied_reason": None}
    except (RuntimeError, ValueError) as exc:
        return {"completed": False, "actions_used": used,
                "host_assisted_actions": trace,
                "experience": None,
                "denied_reason": type(exc).__name__ + ": " + str(exc)[:160]}


def run_pilot() -> dict:
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.subject_port import SubjectPort
    if set(NATIVE_TO_TASK) != set(ACTIONS):
        raise AssertionError("Native action mapping is not total and frozen")
    rows = []
    tiny = dict(DEFAULT_CONFIG)
    tiny.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                input_degree=4, action_population_size=8)
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for case in CASES:
            for arm in ARMS:
                path = root / case / arm
                path.mkdir(parents=True)
                world = SpatialHabitat.create(path / "laboratory.sqlite3")
                home = HomeLife(world)
                home.initialize()
                rhythm = DailyRhythm(world)
                rhythm.initialize()
                _setup_case(rhythm, home, case)
                initial = deepcopy(rhythm.audit_state())
                station = home.habitat and SubjectPort(world).embodied.verify()["station"]
                doctor = PretoriusBrainPort(path / "doctor", neural_config=tiny)
                bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
                seen = bridge.observe()
                frame = seen["subject"]["inner"]
                if arm == "real_doctor_policy":
                    native = bridge.request_cognition(trigger="home_pilot_cognition")
                    tendency = native["selected_action"]
                    choice = NATIVE_TO_TASK[tendency]
                    policy_source = "actual_recurrent_policy_fixed_mapping"
                    policy_decision = native["policy_decision_id"]
                else:
                    tendency = None
                    choice = simple_choice(frame)
                    policy_source = "literal_firstperson_rules"
                    policy_decision = None
                result = _execute(bridge, choice, prefix=f"{case}-{arm}")
                rows.append({
                    "case": case, "arm": arm, "world_initial_condition": _hash(initial),
                    "initial_station": station, "observed_frame_sha256": _hash(frame),
                    "doctor_memory_id": seen["memory_id"],
                    "native_tendency": tendency,
                    "policy_decision_id": policy_decision,
                    "task_proposed": choice, "expected_task": EXPECTED[case],
                    "policy_source": policy_source,
                    "matched_intended_task": choice == EXPECTED[case],
                    "expected_task_completed": result["completed"] and choice == EXPECTED[case],
                    **result,
                })
    pairs = []
    for case in CASES:
        native = next(x for x in rows if x["case"] == case and
                      x["arm"] == "real_doctor_policy")
        control = next(x for x in rows if x["case"] == case and
                       x["arm"] == "simple_firstperson_rule")
        if (native["world_initial_condition"], native["initial_station"]) != (
                control["world_initial_condition"], control["initial_station"]):
            raise AssertionError("Paired physical preparations are unequal")
        if native["observed_frame_sha256"] != control["observed_frame_sha256"]:
            raise AssertionError("Controller got a different first-person observation")
        pairs.append({
            "case": case, "same_world_state": True, "same_sensory_frame": True,
            "native_proposal": native["task_proposed"],
            "simple_proposal": control["task_proposed"],
            "native_expected_task_completed": native["expected_task_completed"],
            "simple_expected_task_completed": control["expected_task_completed"],
        })
    totals = {arm: sum(x["expected_task_completed"] for x in rows if x["arm"] == arm)
              for arm in ARMS}
    return {
        "schema": SCHEMA, "qualification": "UNASSESSABLE",
        "method": "authored exploratory scenarios; actual Doctor policy versus text-rule controller; matched current first-person observations and host action budgets; unmatched biographical priors",
        "mapping": deepcopy(NATIVE_TO_TASK), "actions_per_arm": MAX_ACTIONS,
        "result": totals, "cases": rows, "pairs": pairs,
        "interpretation": "An actual physical task is only credited when the independent Laboratory state changed in the expected direction. No evidence of general autonomy, Article completion or consciousness.",
    }
