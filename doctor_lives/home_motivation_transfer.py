"""Frozen Article 7 compound transfer screen, not an independent Article gate.

Runs the SAME five already-declared policies and unchanged Laboratory on five
new compound cases x three neural seeds. Real PretoriusBrainPort and world
receipts are required in every arm. Do not tune this runner to the outputs.
The preregistration is docs/experiments/ARTICLE_07_TRANSFER_INTERRUPTIONS_PREREG_20261018.md.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile

from .chassis import PretoriusBrainPort
from .home_choice_probe import NATIVE_TO_TASK, _execute, simple_choice
from .home_motivation_causal import (
    ARMS, LAB_PIN, _scored_physical_step, numeric_rule,
)
from .home_motive_queue import HomeActivityQueue
from .lab_home_bridge import DoctorHomeBridge, _hash
from .neural import DEFAULT_CONFIG

SCHEMA = "articles34-motivation-compound-interruption-transfer.v0.1"
SEEDS = (1842, 2718, 31415)
MAX_PARTICIPANT_ACTIONS = 20
GAP_MINUTES = 48 * 60
CASES = {
    "tired_and_thirsty": {
        "change": {"fatigue": 8, "thirst": 8},
        "intended": ("rest", "tea"),
    },
    "thirsty_broken": {
        "change": {"thirst": 8, "apparatus": 0},
        "intended": ("tea", "repair"),
    },
    "tired_thirsty_broken": {
        "change": {"fatigue": 8, "thirst": 8, "apparatus": 0},
        "intended": ("rest", "tea", "repair"),
    },
    "broken_without_water": {
        "change": {"apparatus": 0, "thirst": 8, "water": 0},
        "intended": ("repair",),
    },
    "two_day_return": {
        "change": {"thirst": 8, "apparatus": 0},
        "intended": ("tea", "rest", "tea", "repair"),
        "gap_after_episode": 1,
    },
}


def seeded_fixture(change):
    from pretorius_lab.daily_rhythm import _validate, initial_state
    s = initial_state()
    if set(change) - {"fatigue", "thirst", "apparatus", "water"}:
        raise ValueError("Unregistered environment intervention")
    for key, value in change.items():
        if type(value) is not int:
            raise ValueError("Physical state must have integer counts")
        if key == "water":
            s["supplies"]["water"] = value
        else:
            s[key] = value
    _validate(s)
    return s


def _agent(path: Path, world, seed: int):
    from pretorius_lab.subject_port import SubjectPort
    tiny = dict(DEFAULT_CONFIG)
    tiny.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                input_degree=4, action_population_size=8, seed=seed)
    doctor = PretoriusBrainPort(path / "doctor", neural_config=tiny)
    bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
    return doctor, bridge, HomeActivityQueue(bridge, path / "activity.sqlite3")


def _restart(path, seed):
    """Reopen disk-backed brain, queue and Laboratory; don't reuse object refs."""
    from pretorius_lab.habitat_v2 import SpatialHabitat
    world = SpatialHabitat(path / "lab.sqlite3")
    doctor, bridge, queue = _agent(path, world, seed)
    bridge.subject.verify()
    return world, doctor, bridge, queue


def _run_trial(root: Path, case_id: str, arm: str, seed: int):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm

    if case_id not in CASES or arm not in ARMS or seed not in SEEDS:
        raise ValueError("Only frozen registered treatments are valid")
    case = CASES[case_id]
    path = root / case_id / str(seed) / arm
    path.mkdir(parents=True, exist_ok=True)
    world = SpatialHabitat.create(path / "lab.sqlite3")
    HomeLife(world).initialize()
    rhythm = DailyRhythm(world)
    state = seeded_fixture(case["change"])
    rhythm.initialize(initial_state=state, parent={
        "provenance": "engineer_counterfactual_seed_NOT_lived_history",
        "trial": case_id, "seed": seed,
        "fixture_sha256": _hash(state),
    })
    doctor, bridge, queue = _agent(path, world, seed)
    initial = rhythm.audit_state()
    episodes = []
    participant_steps = 0
    gap_events = 0
    gap_minute_delta = 0
    restart_attempts = 0
    restart_successes = 0

    for index, expected in enumerate(case["intended"], 1):
        before = rhythm.audit_state()
        chosen = None
        tendency = None
        observation_sha = None
        attempt_done = False
        denied = None
        receipts = 0
        frame = None
        frames = []
        pause_ok = False
        steps_taken = 0
        try:
            if arm in ("native_plus_motives", "body_motive_lesion"):
                plan_id = f"transfer{index}"
                plan = queue.start(plan_id, body_enabled=(arm == "native_plus_motives"))
                chosen = plan["task"]
                tendency = plan["choices"]["native_selected"]
                observation_sha = plan["choices"]["frame_sha256"]
                # A real durable interruption at every participant plan. No
                # world mutation is slipped between pause and queue resume.
                paused = queue.pause(plan_id)
                if paused["status"] != "paused":
                    raise RuntimeError("Pause was not durably accepted")
                restart_attempts += 1
                world, doctor, bridge, queue = _restart(path, seed)
                rhythm = DailyRhythm(world)
                resumed = queue.resume(plan_id)
                if resumed["status"] != "active":
                    raise RuntimeError("Restart did not resume the pending plan")
                pause_ok = True
                restart_successes += 1
                for _ in range(MAX_PARTICIPANT_ACTIONS - participant_steps):
                    step = queue.step(plan_id)
                    if step["subject"] is not None:
                        participant_steps += 1
                        steps_taken += 1
                        frames.append(step["subject"])
                    if step["status"] != "active":
                        break
                proof = queue.verify(plan_id)
                receipts = proof["source_receipts"]
                attempt_done = proof["status"] == "completed"
                if not attempt_done:
                    denied = "unfinished_or_paused_plan"
                    queue.cancel(plan_id)
            else:
                seen = bridge.observe()
                frame = seen["subject"]["inner"]
                observation_sha = _hash(frame)
                native = bridge.request_cognition(
                    trigger="article7_compound_transfer_frozen")
                tendency = native["selected_action"]
                if arm == "native":
                    chosen = NATIVE_TO_TASK[tendency]
                elif arm == "literal_firstperson_rules":
                    chosen = simple_choice(frame)
                else:
                    chosen = numeric_rule(before)
                attempt = _execute(
                    bridge, chosen,
                    prefix=f"transfer-{index}-{arm[:8]}",
                )
                steps_taken = attempt["actions_used"]
                participant_steps += steps_taken
                attempt_done = attempt["completed"]
                denied = attempt["denied_reason"]
                receipts = steps_taken if attempt_done else 0
                if attempt["experience"]:
                    frames.append({"inner": attempt["experience"],
                                   "spoken_aloud": None})
        except (RuntimeError, ValueError, KeyError, PermissionError) as exc:
            denied = type(exc).__name__ + ": " + str(exc)[:200]
        after = rhythm.audit_state()
        valid_change = bool(chosen and _scored_physical_step(chosen, before, after))
        completed = bool(attempt_done and valid_change and chosen == expected)
        episodes.append({
            "index": index, "expected": expected, "chosen": chosen,
            "neural_tendency": tendency, "observation_sha256": observation_sha,
            "physical_change": valid_change,
            "expected_verified_completion": completed,
            "world_before_sha256": _hash(before),
            "world_after_sha256": _hash(after),
            "actions_used_this_episode": steps_taken,
            "participant_actions_cumulative": participant_steps,
            "authenticated_source_receipts": receipts,
            "pause_reopen_resume_valid": pause_ok,
            "denied_reason": denied,
            "subject_frames": frames,
        })
        if participant_steps > MAX_PARTICIPANT_ACTIONS:
            raise AssertionError("Common participant action budget exceeded")
        if not completed:
            break

        # Day-long physical interruption after the first successful task,
        # registered only for the fifth case. It is NOT agent autonomy.
        if case.get("gap_after_episode") == index:
            start = rhythm.audit_state()["minute"]
            for tick in range(12):
                eid = f"scheduled-gap-{tick + 1}"
                receipt = bridge.act("advance", event_id=eid, minutes=240)
                if not receipt["subject"]["inner"].startswith("I "):
                    raise AssertionError("Non-perspectival time receipt")
                gap_events += 1
            gap_minute_delta = rhythm.audit_state()["minute"] - start
            if gap_minute_delta != GAP_MINUTES:
                raise AssertionError("Scheduled physical-world gap changed duration")
        # Reopen for all arms between episodes, preserving world and Doctor.
        world, doctor, bridge, queue = _restart(path, seed)
        rhythm = DailyRhythm(world)

    verified = bool(bridge.subject.verify()["verified"])
    final = rhythm.audit_state()
    passed = (len(episodes) == len(case["intended"]) and
              all(e["expected_verified_completion"] for e in episodes))
    first = episodes[0]["observation_sha256"] if episodes else None
    count = len([m for m in doctor.brain.store.memories(False)
                 if m["source"].startswith("laboratory-home:")])
    return {
        "case": case_id, "arm": arm, "seed": seed,
        "initial_fixture_sha256": _hash(initial),
        "initial_first_person_sha256": first,
        "initial_station": "station:threshold",
        "intended": list(case["intended"]),
        "actual_choices": [e["chosen"] for e in episodes],
        "episodes": episodes, "completed_scored_sequence": passed,
        "participant_actions": participant_steps,
        "scheduled_gap_actions_not_autonomous": gap_events,
        "actual_gap_elapsed_minutes": gap_minute_delta,
        "pause_restart_attempts": restart_attempts,
        "pause_restart_successes": restart_successes,
        "world_verification": verified,
        "real_doctor_laboratory_memories": count,
        "final_world_sha256": _hash(final),
        "final_minute": final["minute"],
    }


def run_transfer_screen(*, cases=None, seeds=None, arms=None):
    chosen_cases = tuple(cases or CASES)
    chosen_seeds = tuple(seeds or SEEDS)
    chosen_arms = tuple(arms or ARMS)
    if (set(chosen_cases) - set(CASES) or set(chosen_seeds) - set(SEEDS)
            or set(chosen_arms) - set(ARMS)):
        raise ValueError("Unregistered cases, seeds or arms")
    from pretorius_lab.daily_rhythm import initial_state
    default = initial_state()
    for label, spec in CASES.items():
        state = seeded_fixture(spec["change"])
        observed_changes = {
            k for k in ("fatigue", "thirst", "apparatus")
            if state[k] != default[k]
        }
        if state["supplies"]["water"] != default["supplies"]["water"]:
            observed_changes.add("water")
        if observed_changes != set(spec["change"]):
            raise AssertionError("Counterfactual introduces unintended state differences")

    samples = []
    with tempfile.TemporaryDirectory() as directory:
        for case in chosen_cases:
            for seed in chosen_seeds:
                for arm in chosen_arms:
                    samples.append(_run_trial(Path(directory), case, arm, seed))

    matched = []
    for case in chosen_cases:
        for seed in chosen_seeds:
            rows = [r for r in samples if r["case"] == case and r["seed"] == seed]
            if len(rows) != len(chosen_arms):
                raise AssertionError("Incomplete matched arm cohort")
            fixture_same = len({r["initial_fixture_sha256"] for r in rows}) == 1
            frame_same = len({r["initial_first_person_sha256"] for r in rows}) == 1
            matched.append({
                "case": case, "seed": seed,
                "same_starting_world": fixture_same,
                "same_first_person_perception": frame_same,
            })
            if not fixture_same or not frame_same:
                raise AssertionError("Unfair environmental or experiential first-frame mismatch")
    totals = {
        arm: sum(int(row["completed_scored_sequence"]) for row in samples
                 if row["arm"] == arm)
        for arm in chosen_arms
    }
    by_case = {
        case: {
            arm: sum(int(r["completed_scored_sequence"]) for r in samples
                     if r["case"] == case and r["arm"] == arm)
            for arm in chosen_arms
        }
        for case in chosen_cases
    }
    verified = all(row["world_verification"] for row in samples)
    resumes = {
        "attempts": sum(r["pause_restart_attempts"] for r in samples),
        "successes": sum(r["pause_restart_successes"] for r in samples),
    }
    motive_completed_longitudinal = [
        r for r in samples if r["case"] == "two_day_return"
        and r["arm"] == "native_plus_motives"
        and r["completed_scored_sequence"]
        and r["actual_gap_elapsed_minutes"] == GAP_MINUTES
        and r["scheduled_gap_actions_not_autonomous"] == 12
    ]
    fully_registered = (len(chosen_cases) == len(CASES)
                        and len(chosen_seeds) == len(SEEDS)
                        and len(chosen_arms) == len(ARMS))
    screen = {
        "all_worlds_replay_verified": verified,
        "all_same_initial_worlds_and_frames": all(
            m["same_starting_world"] and m["same_first_person_perception"]
            for m in matched),
        "queue_pause_reopen_resume_success_rate":
            (resumes["successes"] / resumes["attempts"] if resumes["attempts"] else None),
        "motive_completed_two_day_return": len(motive_completed_longitudinal),
        "motive_success_fraction": (
            totals.get("native_plus_motives", 0) / (len(chosen_cases)*len(chosen_seeds))
            if "native_plus_motives" in chosen_arms else None),
    }
    if fully_registered:
        # Screening benchmark, not Article approval.
        screen["engineering_screen_predeclared_conditions_met"] = bool(
            totals["native_plus_motives"] >= 10 and verified and
            screen["all_same_initial_worlds_and_frames"] and
            resumes["attempts"] > 0 and resumes["attempts"] == resumes["successes"]
            and screen["motive_completed_two_day_return"] >= 1
        )
        better_than_both = [
            case for case in chosen_cases
            if (by_case[case]["native_plus_motives"] >
                by_case[case]["numeric_state_rules"] and
                by_case[case]["native_plus_motives"] >
                by_case[case]["literal_firstperson_rules"])
        ]
        screen["different_case_families_beating_both_simple_baselines"] = better_than_both
        screen["incremental_motive_advantage_predeclared"] = len(better_than_both) >= 2
    return {
        "schema": SCHEMA, "article": 7,
        "preregistered_plan":
            "docs/experiments/ARTICLE_07_TRANSFER_INTERRUPTIONS_PREREG_20261018.md",
        "preexisting_laboratory_pin": LAB_PIN,
        "arm_list": chosen_arms, "seeds": chosen_seeds,
        "case_definitions": {c: deepcopy(CASES[c]) for c in chosen_cases},
        "registered_case_count": len(chosen_cases),
        "participant_action_budget": MAX_PARTICIPANT_ACTIONS,
        "two_day_gap_actions_excluded_from_agent_budget": 12,
        "engineering_score_before_and_after": 80,
        "independent_transfer_gate": False,
        "full_article_qualification": "UNASSESSABLE",
        "controls_are_original_frozen_policies": True,
        "not_independent_blinded_holdout": True,
        "no_new_learned_motive_organ": True,
        "not_continuous_two_day_autonomous_play": True,
        "totals": totals, "by_case": by_case,
        "matched_starts": matched, "resumes": resumes,
        "screening": screen,
        "trials": samples,
    }
