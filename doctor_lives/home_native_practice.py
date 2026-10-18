"""Article 8: source-verified habits from native NEURAL-MAPPED household choices.

There are no host-supplied training task labels. Every training task comes
from an actual PretoriusBrainPort cognition receipt, through the frozen
generic-action mapping below. A host still schedules and routes each choice,
so this is NOT fully autonomous household living or subjective preference.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import tempfile

from .chassis import PretoriusBrainPort
from .home_habit_screen import _act, _advance_to, _morning_after_sleep
from .home_habit_trace import OPS, _material_gain, VerifiedHouseholdHabit
from .lab_home_bridge import DoctorHomeBridge, _hash
from .neural import ACTIONS, DEFAULT_CONFIG

SCHEMA = "article08-native-mapped-household-practice.v0.1"
LAB_PIN = "6e49795752835d64fa6fd63d16359669a1ca2ba7"
SEEDS = (1842, 2718, 31415)
TEA_ACTIONS = frozenset(("approach", "cooperate", "comply", "avoid", "conceal"))
NATIVE_TO_HOUSEHOLD = {
    action: ("tea" if action in TEA_ACTIONS else "tidy")
    for action in ACTIONS
}
FIXED = {"kitchen:morning": "tea", "kitchen:afternoon": "tidy"}
CLOCKS = (("kitchen:morning", 420), ("kitchen:afternoon", 900))


def _agent(path: Path, seed: int):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.subject_port import SubjectPort
    config = dict(DEFAULT_CONFIG)
    config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                  input_degree=4, action_population_size=8, seed=seed)
    world = SpatialHabitat(path / "lab.sqlite3")
    doctor = PretoriusBrainPort(path / "doctor", neural_config=config)
    bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
    return bridge, VerifiedHouseholdHabit(bridge, path / "habits.sqlite3")


def _choose(bridge, prefix):
    seen = bridge.observe()
    first_person = seen["subject"]["inner"]
    if not first_person.startswith(("I ", "My ")):
        raise AssertionError("Neural choice lacks a verified first-person frame")
    if any(key in first_person for key in ("world_epoch", "supplies=", "fatigue=")):
        raise AssertionError("Raw engineering state crossed the subject boundary")
    decision = bridge.request_cognition(trigger="article08_native_mapped_choice")
    native = decision["selected_action"]
    if native not in NATIVE_TO_HOUSEHOLD:
        raise AssertionError("Neural cognition yielded unknown generic action")
    if not decision.get("policy_decision_id"):
        raise AssertionError("Real Doctor selected no persistent policy receipt")
    return {
        "first_person_frame_sha256": _hash(first_person),
        "admitted_observation_memory_id": seen["memory_id"],
        "neural_policy_receipt": decision["policy_decision_id"],
        "native_action": native,
        "mapped_household_task": NATIVE_TO_HOUSEHOLD[native],
    }


def _execute_once(bridge, task: str, eid: str, *, train: bool, habit=None):
    """Apply chosen action exactly as selected: never swap a blocked choice."""
    from pretorius_lab.physics import Conflict, LabError
    state_before = bridge.subject.rhythm.audit_state()
    try:
        _act(bridge, OPS[task], eid)
    except (Conflict, LabError, RuntimeError, ValueError) as exc:
        after = bridge.subject.rhythm.audit_state()
        if after != state_before:
            raise AssertionError("Denied action changed the physical source") from exc
        return {
            "attempted": task, "world_accepted": False,
            "material_benefit": False, "learned": False,
            "denial": type(exc).__name__ + ": " + str(exc)[:140],
            "before_sha256": _hash(state_before),
            "after_sha256": _hash(after),
        }
    state_after = bridge.subject.rhythm.audit_state()
    benefit = _material_gain(task, state_before, state_after)
    learned = False
    if benefit and train:
        if habit is None:
            raise AssertionError("No genuine habit source for this learning action")
        proof = habit.learn(event_id=eid, before=state_before)
        learned = proof["status"] == "learned"
    return {
        "attempted": task, "world_accepted": True,
        "material_benefit": benefit,
        "learned": learned, "denial": None,
        "before_sha256": _hash(state_before),
        "after_sha256": _hash(state_after),
    }


def _world(root: Path, seed: int):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    path = root / str(seed)
    path.mkdir(parents=True, exist_ok=True)
    world = SpatialHabitat.create(path / "lab.sqlite3")
    HomeLife(world).initialize()
    DailyRhythm(world).initialize()
    bridge, habit = _agent(path, seed)
    _act(bridge, "walk", f"s{seed}-enter-hall", station="station:hall")
    _act(bridge, "walk", f"s{seed}-enter-kitchen", station="station:kitchen")
    practice = []
    heldout = []
    restarts = []
    last_success = None

    for day in (1, 2, 3):
        for cue, clock in CLOCKS:
            _advance_to(bridge, (day - 1) * 1440 + clock,
                        f"p{seed}-{day}-{cue.split(':')[-1]}")
            source = bridge.subject.rhythm.audit_state()
            station = bridge.subject.embodied.verify()["station"]
            if habit.advise(state=source, station=station)["cue"] != cue:
                raise AssertionError("Preregistered source daypart was not reached")
            decision = _choose(bridge, f"practice-{seed}-{day}-{cue}")
            eid = f"s{seed}-practice-d{day}-{cue.split(':')[-1]}"
            result = _execute_once(bridge, decision["mapped_household_task"],
                                   eid, train=True, habit=habit)
            if result["material_benefit"]:
                last_success = decision["mapped_household_task"]
            practice.append({
                "day": day, "cue": cue, "decision": decision, "action": result,
                "world_receipts_replay": bridge.subject.verify()["verified"],
            })
        _morning_after_sleep(bridge, day)
        before_restart = habit.verify()["verified_practices"]
        bridge, habit = _agent(path, seed)
        after_restart = habit.verify()["verified_practices"]
        if before_restart != after_restart:
            raise AssertionError("Source-linked learned practices vanished after restart")
        restarts.append({
            "day": day, "practices_before": before_restart,
            "practices_after": after_restart,
            "reopened_actual_doctor": True,
            "world_verified": bridge.subject.verify()["verified"],
        })

    untrained = VerifiedHouseholdHabit(bridge, path / "untrained.sqlite3")
    for cue, clock in CLOCKS:
        _advance_to(bridge, 3 * 1440 + clock,
                    f"h{seed}-{cue.split(':')[-1]}")
        source = bridge.subject.rhythm.audit_state()
        station = bridge.subject.embodied.verify()["station"]
        if station != "station:kitchen":
            raise AssertionError("Holdout has wrong physical body position")
        prediction = habit.advise(state=source, station=station)
        none = untrained.advise(state=source, station=station)
        decision = _choose(bridge, f"holdout-{seed}-{cue}")
        target = decision["mapped_household_task"]
        comparisons = {
            "receipt_habit": prediction["advice"],
            "fixed_clock": FIXED[cue],
            "last_successful_action": last_success,
            "untrained_lesion": none["advice"],
        }
        actual = _execute_once(
            bridge, target, f"s{seed}-holdout-{cue.split(':')[-1]}",
            train=False)
        heldout.append({
            "cue": cue, "decision": decision,
            "learned_counts": prediction["practices"],
            "predictions": comparisons,
            "agrees_with_native_mapping": {
                k: task == target for k, task in comparisons.items()
            },
            "world_action": actual,
            "no_holdout_learning": habit.verify()["verified_practices"],
        })

    all_practice = habit.verify()
    return {
        "seed": seed, "training_offers": practice, "heldout_offers": heldout,
        "night_restarts": restarts, "physical_world_verified":
            bridge.subject.verify()["verified"],
        "source_verified_practices": all_practice["verified_practices"],
        "neural_actions_seen": dict(Counter(
            offer["decision"]["native_action"]
            for offer in practice + heldout)),
        "no_synthetic_life": True,
    }


def run_native_practice_screen(*, seeds=SEEDS):
    if not seeds or set(seeds) - set(SEEDS):
        raise ValueError("Only preregistered neural seeds are admitted")
    with tempfile.TemporaryDirectory() as folder:
        worlds = [_world(Path(folder), seed) for seed in seeds]
    choices = [row for world in worlds for row in world["heldout_offers"]]
    training = [row for world in worlds for row in world["training_offers"]]
    agreement = {
        name: sum(int(row["agrees_with_native_mapping"][name])
                  for row in choices)
        for name in ("receipt_habit", "fixed_clock", "last_successful_action",
                     "untrained_lesion")
    }
    selected = sorted({
        row["decision"]["mapped_household_task"]
        for row in training
    })
    return {
        "schema": SCHEMA, "pinned_laboratory": LAB_PIN, "seeds": list(seeds),
        "article_8_engineering_score_before_and_after": 10,
        "independent_transfer_gate": False,
        "qualification": "UNASSESSABLE",
        "training_action_origin": "real_neural_selected_action_via_frozen_generic_mapping",
        "host_scheduled_executions_not_self_directed_life": True,
        "worlds": worlds, "native_choice_distribution": {
            name: sum(row["decision"]["native_action"] == name
                      for row in training + choices)
            for name in ACTIONS
        },
        "native_mapped_categories_seen_during_training": selected,
        "neural_opportunities": len(training) + len(choices),
        "training_accepted": sum(row["action"]["world_accepted"] for row in training),
        "training_material_benefits": sum(
            row["action"]["material_benefit"] for row in training),
        "training_blocked": sum(
            not row["action"]["world_accepted"] for row in training),
        "advice_abstentions": sum(
            row["predictions"]["receipt_habit"] is None for row in choices),
        "heldout_neural_agreement": agreement,
        "all_worlds_verified": all(w["physical_world_verified"] for w in worlds),
        "all_restored_practices_verified": all(
            all(n["practices_before"] == n["practices_after"]
                for n in w["night_restarts"]) for w in worlds),
        "observed_both_task_classes": len(selected) == 2,
        "not_proof_of_spontaneous_habits": True,
    }
