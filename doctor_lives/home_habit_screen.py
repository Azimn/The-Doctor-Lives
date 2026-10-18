"""Two independent real-home Article 8 learning trajectories, with controls.

Host demonstrator chooses tasks for training; actual Doctor ingests first-person
observations and acts are recorded in the real Laboratory with source proofs.
No person or neural brain is credited with self-originating these demos.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from .chassis import PretoriusBrainPort
from .home_habit_trace import VerifiedHouseholdHabit, OPS
from .home_motive_queue import motive_scores
from .lab_home_bridge import DoctorHomeBridge, _hash
from .neural import DEFAULT_CONFIG

SCHEMA = "articles34-household-habits-reversed-contexts.v0.1"
LAB_PIN = "6e49795752835d64fa6fd63d16359669a1ca2ba7"
MAPPINGS = {
    "A": {"kitchen:morning": "tea", "kitchen:afternoon": "tidy"},
    "B": {"kitchen:morning": "tidy", "kitchen:afternoon": "tea"},
}
FIXED_SCHEDULE = {"kitchen:morning": "tea", "kitchen:afternoon": "tidy"}


def _reopen(path: Path):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.subject_port import SubjectPort
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
               input_degree=4, action_population_size=8, seed=1842)
    world = SpatialHabitat(path / "lab.sqlite3")
    doctor = PretoriusBrainPort(path / "doctor", neural_config=cfg)
    bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
    habit = VerifiedHouseholdHabit(bridge, path / "habits.sqlite3")
    return bridge, habit


def _act(bridge, op, event_id, **args):
    result = bridge.act(op, event_id=event_id, **args)
    if not result["subject"]["inner"].startswith(("I ", "My ")):
        raise RuntimeError("Real Doctor received non-first-person experience")
    return result


def _advance_to(bridge, target_minute, prefix):
    now = bridge.subject.rhythm.audit_state()["minute"]
    gap = target_minute - now
    if gap < 0 or gap % 10:
        raise ValueError("Invalid exact simulated schedule")
    i = 0
    while gap:
        tick = min(gap, 240)
        _act(bridge, "advance", f"{prefix}-time-{i}", minutes=tick)
        gap -= tick
        i += 1


def _morning_after_sleep(bridge, day):
    state = bridge.subject.rhythm.audit_state()
    target = (day - 1) * 1440 + 23 * 60
    _advance_to(bridge, target, f"day{day}-evening")
    _act(bridge, "walk", f"day{day}-hall-sleep", station="station:hall")
    _act(bridge, "walk", f"day{day}-bedroom", station="station:bedroom")
    _act(bridge, "sleep", f"day{day}-sleep")
    _act(bridge, "walk", f"day{day}-hall-wake", station="station:hall")
    _act(bridge, "walk", f"day{day}-kitchen", station="station:kitchen")
    arrived = bridge.subject.rhythm.audit_state()["minute"]
    assert arrived == day * 1440 + 7 * 60, (arrived, day)


def _motive_baseline(state):
    """Original formula, choosing among the two domain actions only."""
    scores = motive_scores(state)["scores"]
    eligibility = motive_scores(state)["eligible"]
    # Existing home motive policy calls this activity "clean"; this
    # experiment uses the ordinary-household synonym "tidy". Translation
    # only: no policy thresholds, scores or feasibility values are changed.
    original_name = {"tea": "tea", "tidy": "clean"}
    options = [task for task in OPS if eligibility[original_name[task]]]
    return (max(options, key=lambda name: (
        scores[original_name[name]], -tuple(OPS).index(name)))
            if options else None)


def _experience(bridge, prefix):
    seen = bridge.observe()
    thought = bridge.request_cognition(trigger="article08_kitchen_habit_experience")
    frame = seen["subject"]["inner"]
    if any(token in frame for token in ("fatigue=", "world_epoch", "supplies=")):
        raise RuntimeError("Hidden engineering state leaked to actual Doctor")
    return {"frame_sha256": _hash(frame),
            "doctor_native_action": thought["selected_action"],
            "source_memory_id": seen["memory_id"]}


def _one_world(root, mapping_name):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm

    path = root / mapping_name
    path.mkdir(parents=True)
    world = SpatialHabitat.create(path / "lab.sqlite3")
    HomeLife(world).initialize()
    DailyRhythm(world).initialize()
    bridge, habit = _reopen(path)
    _act(bridge, "walk", "enter-hall", station="station:hall")
    _act(bridge, "walk", "enter-kitchen", station="station:kitchen")
    mapping = MAPPINGS[mapping_name]
    practice = []
    last_action = None
    for day in (1, 2):
        for cue, clock in (("kitchen:morning", 7 * 60),
                           ("kitchen:afternoon", 15 * 60)):
            _advance_to(bridge, (day - 1) * 1440 + clock,
                        f"train-{day}-{cue.split(':')[1]}")
            before = bridge.subject.rhythm.audit_state()
            context = _experience(bridge, f"train-{day}-{cue}")
            advice_before = habit.advise(
                state=before, station=bridge.subject.embodied.verify()["station"])
            if advice_before["cue"] != cue:
                raise AssertionError("Wrong household activity context")
            task = mapping[cue]
            event_id = f"practice-{day}-{cue.split(':')[1]}"
            _act(bridge, OPS[task], event_id)
            learned = habit.learn(event_id=event_id, before=before)
            practice.append({"day": day, "cue": cue, "demonstrated": task,
                             "before_source": _hash(before),
                             "learned": learned, "first_person": context,
                             "prior_advice": advice_before["advice"]})
            last_action = task
        _morning_after_sleep(bridge, day)
        bridge, habit = _reopen(path)

    after_restart = habit.verify()
    if after_restart["verified_practices"] != 4:
        raise AssertionError("Expected four authentic, source-bound practice events")
    scores = []
    for cue, clock in (("kitchen:morning", 7 * 60),
                       ("kitchen:afternoon", 15 * 60)):
        _advance_to(bridge, 2 * 1440 + clock,
                    "holdout-" + cue.split(":")[1])
        state = bridge.subject.rhythm.audit_state()
        context = _experience(bridge, "holdout-" + cue)
        advice = habit.advise(state=state, station="station:kitchen")
        expected = mapping[cue]
        untrained = VerifiedHouseholdHabit(bridge, path / "empty_habit_control.sqlite3")
        controls = {
            "verified_practice": advice["advice"],
            "fixed_schedule": FIXED_SCHEDULE[cue],
            "recency": last_action,
            "original_motive_scores": _motive_baseline(state),
            "untrained_trace": untrained.advise(
                state=state, station="station:kitchen")["advice"],
        }
        # This candidate's choice is actually executed (not just a fluent
        # proposal), but holdout events never become additional training data.
        physically_completed = False
        if advice["advice"] is not None:
            before = bridge.subject.rhythm.audit_state()
            receipt = _act(bridge, OPS[advice["advice"]],
                           "holdout-" + cue.split(":")[1] + "-world-act")
            after = bridge.subject.rhythm.audit_state()
            from .home_habit_trace import _material_gain
            physically_completed = _material_gain(advice["advice"], before, after)
            if not physically_completed:
                raise AssertionError("Claimed holdout action left no material consequence")
            last_action = advice["advice"]
        scores.append({
            "cue": cue, "expected_experimentally_demonstrated": expected,
            "first_person": context, "advice": controls,
            "accurate": {k: v == expected for k, v in controls.items()},
            "physically_completed": physically_completed,
            "actual_world_after_sha256": _hash(bridge.subject.rhythm.audit_state()),
        })
    proof = habit.verify()
    brain_memories = len([
        m for m in bridge.doctor.brain.store.memories(False)
        if m["source"].startswith("laboratory-home:")
    ])
    return {
        "mapping": mapping_name, "practices": practice,
        "heldout": scores, "world_replay": bridge.subject.verify()["verified"],
        "habits_replayed": proof, "real_doctor_memories": brain_memories,
        "actual_days_elapsed": (
            bridge.subject.rhythm.audit_state()["minute"] // 1440
        ),
    }


def run_habit_screen():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        worlds = [_one_world(root, name) for name in MAPPINGS]
    decisions = [x for world in worlds for x in world["heldout"]]
    totals = {
        name: sum(int(x["accurate"][name]) for x in decisions)
        for name in (
            "verified_practice", "fixed_schedule", "recency",
            "original_motive_scores", "untrained_trace"
        )
    }
    return {
        "schema": SCHEMA,
        "preregistration":
            "docs/experiments/ARTICLE_08_HOUSEHOLD_HABIT_PREREG_20261018.md",
        "pinned_original_lab": LAB_PIN,
        "full_article_qualification": "UNASSESSABLE",
        "article_08_engineering_score_before_and_after": 10,
        "independent_blinded_transfer": False,
        "worlds": worlds,
        "totals": totals,
        "all_material_worlds_verified": all(w["world_replay"] for w in worlds),
        "all_training_receipts_verified": all(
            w["habits_replayed"]["verified_practices"] == 4 for w in worlds),
        "all_recalled_acts_physically_completed": all(
            x["physically_completed"] for x in decisions),
        "predeclared_screen_met": bool(
            totals["verified_practice"] == 4
            and totals["fixed_schedule"] <= 2
            and totals["untrained_trace"] == 0
            and all(w["world_replay"] for w in worlds)
            and all(x["physically_completed"] for x in decisions)),
        "limits": [
            "training actions were host-selected, not self-initiated by Doctor",
            "clock cues are simple explicit environmental signals, not neural habits",
            "only two actions/two dayparts, two demonstrations each",
            "no independent external assessor or blinded holdout",
            "physical Doctor was actually instantiated and observed source-backed experiences",
            "no Article 8 engineering score increase or full qualification",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run_habit_screen(), sort_keys=True, indent=2))
