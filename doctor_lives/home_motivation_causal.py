"""Predeclared single-variable and longitudinal Motivation causal-control pilot.

The real DoctorBrainPort ingests only source-backed first-person Laboratory text.
The external Sims-style motive controller uses engineer-side body state, which
is NEVER sent to the subject as raw numbers. Numeric-rule arm gets equal
engineering information. Fixed literal and neural arms are also measured.
No coefficients, task labels or success criteria may change after first CI run.

This tests the engineering causal-controls gate for Article 7 ONLY. It does
not demonstrate spontaneous initiation or independent held-out transfer.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile

from .chassis import PretoriusBrainPort
from .lab_home_bridge import DoctorHomeBridge, _hash
from .neural import DEFAULT_CONFIG
from .home_motive_queue import HomeActivityQueue
from .home_choice_probe import NATIVE_TO_TASK, _execute, simple_choice

SCHEMA = "articles34-motivation-isolated-interventions.v1"
CASES = {
    "baseline": {"change": {}, "intended": ("experiment",)},
    "wear_only": {"change": {"apparatus": 0}, "intended": ("repair",)},
    "fatigue_only": {"change": {"fatigue": 8}, "intended": ("rest",)},
    "thirst_only": {"change": {"thirst": 8}, "intended": ("tea",)},
    "wear_and_fatigue": {
        "change": {"apparatus": 0, "fatigue": 8},
        "intended": ("rest", "repair"),
    },
}
ARMS = (
    "native",
    "native_plus_motives",
    "body_motive_lesion",
    "literal_firstperson_rules",
    "numeric_state_rules",
)
MAX_ACTIONS = 12
LAB_PIN = "6e49795752835d64fa6fd63d16359669a1ca2ba7"


def numeric_rule(state):
    """Independent strong counter-controller given the SAME numeric body state."""
    if state["fatigue"] >= 7:
        return "rest"
    if state["thirst"] >= 8:
        return "tea"
    if state["apparatus"] <= 0:
        return "repair"
    return "experiment"


def _fixture(change):
    from pretorius_lab.daily_rhythm import initial_state, _validate
    s = initial_state()
    assert all(k in ("fatigue", "thirst", "apparatus") for k in change)
    for key, value in change.items():
        s[key] = value
    _validate(s)
    return s


def _scored_physical_step(task, before, after):
    # Only committed physical changes count, never narrated intentions.
    return {
        "experiment": after["experiments"] > before["experiments"],
        "repair": after["apparatus"] > before["apparatus"],
        "rest": after["fatigue"] < before["fatigue"],
        "tea": after["thirst"] < before["thirst"],
    }.get(task, False)


def _run_case(root: Path, name: str, arm: str):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.subject_port import SubjectPort

    env = CASES[name]
    fixture = _fixture(env["change"])
    loc = root / name / arm
    loc.mkdir(parents=True)
    world = SpatialHabitat.create(loc / "lab.sqlite3")
    HomeLife(world).initialize()
    rhythm = DailyRhythm(world)
    rhythm.initialize(initial_state=fixture, parent={
        "provenance": "engineer_counterfactual_seed_NOT_lived_history",
        "trial": name,
        "starting_fixture_sha256": _hash(fixture),
    })
    tiny = dict(DEFAULT_CONFIG)
    tiny.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                input_degree=4, action_population_size=8)
    doctor = PretoriusBrainPort(loc / "doctor", neural_config=tiny)
    bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
    activity = HomeActivityQueue(bridge, loc / "activity.sqlite3")
    first = rhythm.audit_state()
    results = []
    spent = 0
    target = env["intended"]
    for episode in range(len(target)):
        before = rhythm.audit_state()
        observation = None
        if arm in ("native_plus_motives", "body_motive_lesion"):
            plan = activity.start("activity" + str(episode + 1),
                                  body_enabled=arm == "native_plus_motives")
            chosen = plan["task"]
            sensory = plan["choices"]["frame_sha256"]
            selected = plan["choices"]["native_selected"]
            world_events = []
            remain = MAX_ACTIONS - spent
            for _ in range(remain):
                step = activity.step(plan["plan_id"])
                if step["subject"] is not None:
                    world_events.append(step["subject"])
                    spent += 1
                if step["status"] != "active":
                    break
            proof = activity.verify(plan["plan_id"])
            completed_plan = proof["status"] == "completed"
            receipts = proof["source_receipts"]
        else:
            seen = bridge.observe()
            observation = seen["subject"]["inner"]
            sensory = _hash(observation)
            native = bridge.request_cognition(
                trigger="article7_isolated_environment")
            selected = native["selected_action"]
            if arm == "native":
                chosen = NATIVE_TO_TASK[selected]
            elif arm == "literal_firstperson_rules":
                chosen = simple_choice(observation)
            elif arm == "numeric_state_rules":
                chosen = numeric_rule(before)
            else:
                raise ValueError("Unknown arm")
            from .home_choice_probe import _execute
            attempt = _execute(
                bridge, chosen, prefix=f"ctl-{arm[:8]}-{episode + 1}"
            )
            spent += attempt["actions_used"]
            completed_plan = attempt["completed"]
            world_events = ([{"inner": attempt["experience"], "spoken_aloud": None}]
                            if attempt["experience"] else [])
            receipts = attempt["actions_used"] if completed_plan else None
        after = rhythm.audit_state()
        real_change = _scored_physical_step(chosen, before, after)
        completed = bool(completed_plan and real_change)
        results.append({
            "episode": episode + 1, "expected_action": target[episode],
            "chosen_action": chosen, "native_tendency": selected,
            "first_person_frame_sha256": sensory,
            "physical_completed": completed,
            "expected_action_completed": completed and chosen == target[episode],
            "physical_before_sha256": _hash(before),
            "physical_after_sha256": _hash(after),
            "actions_cumulative": spent, "real_source_receipts": receipts,
            "subject_frames": [
                {"inner": e["inner"], "spoken_aloud": e.get("spoken_aloud")}
                for e in world_events
            ],
        })
        if spent > MAX_ACTIONS:
            raise AssertionError("Common physical action budget exceeded")
        # Only run a second episode if the first actually resolved the need.
        # In the dual-need case, this determines whether rest precedes repair.
        if not results[-1]["expected_action_completed"]:
            break
    end = rhythm.audit_state()
    passed = len(results) == len(target) and all(
        item["expected_action_completed"] for item in results
    )
    return {
        "case": name, "arm": arm,
        "engineered_initial_fixture_sha256": _hash(first),
        "initial_body_state": {k: first[k] for k in ("fatigue","thirst","apparatus")},
        "initial_station": "station:threshold",
        "expected_sequence": list(target), "episodes": results,
        "actual_sequence": [x["chosen_action"] for x in results],
        "completed_scored_sequence": passed,
        "final_state_digest": _hash(end), "total_physical_actions": spent,
        "actual_experiments": end["experiments"],
        "actual_apparatus": end["apparatus"],
        "actual_fatigue": end["fatigue"],
        "persistent_real_doctor_memories": len([
            m for m in doctor.brain.store.memories(False)
            if m["source"].startswith("laboratory-home:")
        ]),
        "world_verification": bridge.subject.verify()["verified"],
    }


def run_isolated_motivation_pilot():
    from pretorius_lab.daily_rhythm import initial_state
    unperturbed = initial_state()
    for name, spec in CASES.items():
        actual = _fixture(spec["change"])
        difference = {k for k in unperturbed if actual[k] != unperturbed[k]}
        if difference != set(spec["change"]):
            raise AssertionError("Intervention changed unregistered variables")
    samples = []
    with tempfile.TemporaryDirectory() as directory:
        for name in CASES:
            for arm in ARMS:
                samples.append(_run_case(Path(directory), name, arm))
    for name in CASES:
        paired = [x for x in samples if x["case"] == name]
        if len({x["engineered_initial_fixture_sha256"] for x in paired}) != 1:
            raise AssertionError("Physical intervention not identical across arms")
        if len({x["episodes"][0]["first_person_frame_sha256"]
                for x in paired}) != 1:
            raise AssertionError("First-person observation differs between arms")
    totals = {
        arm: sum(s["completed_scored_sequence"] for s in samples
                 if s["arm"] == arm)
        for arm in ARMS
    }
    deltas = {}
    for name in ("wear_only", "fatigue_only", "thirst_only"):
        deltas[name] = [
            name, list(CASES[name]["change"]),
            "single_variable_vs_baseline_engineered_genesis",
        ]
    return {
        "schema": SCHEMA, "article": 7,
        "qualification": "UNASSESSABLE",
        "research_justification": "Actual world action receipts and external motive-pressure ablation; no claim of independently learned neural motivation",
        "registered_before_first_run": True,
        "laboratory_pin": LAB_PIN, "case_definitions": CASES,
        "arms": ARMS, "budget_total_per_arm": MAX_ACTIONS,
        "causal_contrasts": deltas,
        "totals": totals, "trials": samples,
        "limitations": [
            "authored rather than independent blinded held-out scenarios",
            "small 128-neuron Doctor, no multi-seed power",
            "motive controller and numeric-rule baseline use privileged true simulated state; real Doctor perceives first-person words only",
            "the host plans routes and explicitly advances each queue step",
            "positive outcome demonstrates host motive contribution, not brain-internal motivational learning or spontaneous agency",
        ],
    }
