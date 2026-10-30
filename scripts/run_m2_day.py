"""Offline M2 accelerated-day evidence producer, original pinned Laboratory only.

No host-supplied action, goal, target, or reward crosses into Noesis. Independent
seeded counterfactuals and random-controller baselines live in separate study
replicas; the subject uses ONE canonical BrainStore and ONE Laboratory world.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import random
import signal
import sqlite3
import subprocess
import sys
import time
from uuid import uuid4

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.noesis_day import (real_affordances, offer_daily_opportunity,
                                    act_on_noesis_choice)
from doctor_lives.noesis_lab_work import propose_noesis_work
from scripts.verify_day import LAB_PIN, SCHEMA, judge


def config(seed):
    answer = dict(DEFAULT_CONFIG)
    answer.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                  input_degree=4, action_population_size=8, seed=seed)
    return answer


def world_and_subject(root: Path, *, seed=1842, new=False):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.embodied_access import EmbodiedAccess
    from pretorius_lab.book_library import BookLibrary
    from pretorius_lab.subject_port import SubjectPort

    world_path = root / "world.sqlite3"
    if new:
        root.mkdir(parents=True, exist_ok=False)
        world = SpatialHabitat.create(world_path)
        # A source-declared *starting condition*, not a staged host movement.
        # All subsequent physical actions must have a Noesis origin.
        EmbodiedAccess(world).initialize(station="station:bench")
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        BookLibrary(world).initialize()
        doctor = PretoriusBrainPort(root / "brain", neural_config=config(seed))
    else:
        world = SpatialHabitat(world_path)
        doctor = PretoriusBrainPort(root / "brain")
    bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
    return doctor, bridge


def original_goal(brain_db: Path):
    with sqlite3.connect(brain_db) as db:
        row = db.execute(
            "SELECT value FROM meta WHERE key='pretorius_day_noesis_goal_v1'"
        ).fetchone()
    if row is None:
        return None
    return json.loads(row[0])["payload"]


def receipt_counts(root: Path):
    with sqlite3.connect(root / "world.sqlite3") as db:
        keys = db.execute(
            "SELECT event_id,event_hash FROM rhythm_events ORDER BY event_id"
        ).fetchall()
    with sqlite3.connect(root / "brain" / "brain.sqlite3") as db:
        sources = db.execute(
            "SELECT source,count(*) FROM memories "
            "WHERE source LIKE 'laboratory-home:action:%' GROUP BY source"
        ).fetchall()
    return dict(keys), dict(sources)


def phase_start(root: Path):
    doctor, bridge = world_and_subject(root, new=True)
    choice = offer_daily_opportunity(bridge, author_goal=True)
    work = act_on_noesis_choice(
        bridge, choice, event_id="day-" + uuid4().hex, authorized=True,
    )
    doctor.save()
    goal = original_goal(root / "brain" / "brain.sqlite3")
    if goal is None or goal["phase"] != "active":
        raise RuntimeError("Subject has no persistently authored unfinished goal")
    print(json.dumps({"event": "goal_ready", "pid": os.getpid(),
                      "goal": goal, "action": work}), flush=True)
    # The parent kills this *actual* process, without an orderly cleanup.
    # Its canonical brain, world and journal are already independently durable.
    while True:
        time.sleep(5)


def phase_resume(root: Path):
    doctor, bridge = world_and_subject(root, new=False)
    before = original_goal(root / "brain" / "brain.sqlite3")
    if before is None:
        raise RuntimeError("Cold restart lost the original subject's goal")
    report = []
    # Only *opportunity count* is scheduled. No task or expected outcome.
    for _ in range(28):
        options = real_affordances(bridge)
        if not options:
            break
        selected = offer_daily_opportunity(bridge, author_goal=True)
        outcome = act_on_noesis_choice(
            bridge, selected, event_id="day-" + uuid4().hex, authorized=True,
        )
        report.append(outcome)
        doctor.save()
        with sqlite3.connect(root / "world.sqlite3") as db:
            body = json.loads(db.execute(
                "SELECT value FROM rhythm_meta WHERE key='state'"
            ).fetchone()[0])
        # The scheduler can stop a bounded test when sufficient evidence
        # exists, but it never chooses a next action.
        if len({row["action"] for row in report}) >= 3 and (
            sum(body[key] >= 4 for key in ("fatigue", "thirst", "hunger")) >= 2
            or any(row["action"] in ("rest", "sleep") for row in report)
        ):
            break
    after = original_goal(root / "brain" / "brain.sqlite3")
    if after is None or after["id"] != before["id"]:
        raise RuntimeError("Recovered subject intention was not preserved")
    print(json.dumps({"pid": os.getpid(), "before_goal": before,
                      "after_goal": after, "actions": report}), flush=True)


def ablation_trials(root: Path):
    trials = []
    for index in range(20):
        seed = 7600 + index
        trial = root / "trials" / str(seed)
        doctor, bridge = world_and_subject(trial, seed=seed, new=True)
        # Independently real physical consequence intervention in EACH
        # control arm. This is deliberately NOT presented as a subject action
        # from the primary autonomous-day brain.
        intervention = bridge.act(
            "experiment", event_id="control-physical-consequence-" + str(seed),
        )
        if intervention["status"] != "admitted":
            raise RuntimeError("Matched ablation lacks an original world consequence")
        with_memory = propose_noesis_work(
            bridge, learning_enabled=False, neural_prior_enabled=True,
            outcome_learning_enabled=True,
        )
        without_memory = propose_noesis_work(
            bridge, learning_enabled=False, neural_prior_enabled=True,
            outcome_learning_enabled=False,
        )
        trials.append({
            "seed": seed, "trial_dir": "trials/" + str(seed),
            "with_memory": with_memory.decision_id,
            "without_memory": without_memory.decision_id,
        })
        # The original neural weights have not changed during these paired
        # read-only policy proposals. Do NOT rewrite the saved checkpoint,
        # or the exact policy-row model SHA could change without new learning.
    return trials


def random_baseline(root: Path):
    random_root = root / "random"
    doctor, bridge = world_and_subject(random_root, seed=1842, new=True)
    rng = random.Random(914287)
    actions = []
    for _ in range(5):
        options = real_affordances(bridge)
        if not options:
            break
        action = rng.choice(options)  # Random baseline, NOT canonical Noesis.
        event_id = "random-" + uuid4().hex
        outcome = bridge.act(action, event_id=event_id)
        actions.append({"event_id": event_id, "action": action, "status": outcome["status"]})
    doctor.save()
    (random_root / "day.json").write_text(json.dumps({
        "schema": SCHEMA, "lab_pin": LAB_PIN,
        "brain_db": "brain/brain.sqlite3", "world_db": "world.sqlite3",
        "intent_db": "world.sqlite3.doctor-action-intents.sqlite3",
        "host_opportunities": [{"tick": i} for i in range(len(actions))],
        "restart": None, "ablation": [],
        "random_baseline": None,
    }, sort_keys=True))
    return actions


def parent_run(root: Path, lab_root: Path):
    root.mkdir(parents=True, exist_ok=False)
    # Child-created state directory has an isolated location. Parent/root is
    # an evidence bundle, not another BrainStore.
    subject = root / "subject"
    command = [sys.executable, __file__, "--phase", "start", "--subject", str(subject)]
    started = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, bufsize=1)
    first_line = started.stdout.readline()
    if not first_line:
        raise RuntimeError("Subject start failed: " + started.stderr.read())
    first = json.loads(first_line)
    if first.get("event") != "goal_ready" or first["pid"] != started.pid:
        raise RuntimeError("Child never durably authored its original goal")
    before_world, before_memory = receipt_counts(subject)
    started.kill()
    killed = started.wait(timeout=15)
    if killed not in (-signal.SIGKILL, 128 + signal.SIGKILL):
        raise RuntimeError("The subject did not undergo a real hard kill")
    resumed = subprocess.run(
        [sys.executable, __file__, "--phase", "resume", "--subject", str(subject)],
        capture_output=True, text=True, timeout=120,
    )
    if resumed.returncode:
        raise RuntimeError("Cold subject restart failed: " + resumed.stderr)
    second = json.loads(resumed.stdout)
    after_world, after_memory = receipt_counts(subject)
    world_duplicates = sum(
        event_id not in after_world or after_world[event_id] != digest
        for event_id, digest in before_world.items()
    )
    memory_duplicates = sum(
        after_memory.get(source) != count or count != 1
        for source, count in before_memory.items()
    )
    # Move nothing or recompute nothing in the primary subject authority.
    # Relative path references keep this bundle self-contained.
    experiments = ablation_trials(root)
    baseline_actions = random_baseline(root)
    data = {
        "schema": SCHEMA, "lab_pin": LAB_PIN,
        "brain_db": "subject/brain/brain.sqlite3",
        "world_db": "subject/world.sqlite3",
        "intent_db": "subject/world.sqlite3.doctor-action-intents.sqlite3",
        "host_opportunities": [{"tick": n} for n in range(1 + len(second["actions"]))],
        "restart": {
            "signal": "SIGKILL", "exit_code": killed,
            "first_pid": started.pid, "second_pid": second["pid"],
            "before_goal": first["goal"], "after_goal": second["after_goal"],
            "duplicate_world_receipts": world_duplicates,
            "duplicate_lived_memories": memory_duplicates,
        },
        "ablation": experiments, "random_baseline": "random",
    }
    (root / "day.json").write_text(json.dumps(data, indent=2, sort_keys=True))
    result = judge(root, lab_root)
    output = {"judge": result,
              "first_action": first["action"], "continued_actions": second["actions"],
              "random_baseline_actions": baseline_actions}
    (root / "result.json").write_text(json.dumps(output, indent=2, sort_keys=True))
    print(json.dumps(output, indent=2, sort_keys=True))
    return int(not result["pass"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path)
    parser.add_argument("--lab-root", type=Path)
    parser.add_argument("--phase", choices=("start", "resume"))
    parser.add_argument("--subject", type=Path)
    args = parser.parse_args()
    if args.phase == "start":
        phase_start(args.subject)
        return 0
    if args.phase == "resume":
        phase_resume(args.subject)
        return 0
    if args.run is None or args.lab_root is None:
        parser.error("--run and --lab-root are required for parent verification")
    return parent_run(args.run, args.lab_root)


if __name__ == "__main__":
    raise SystemExit(main())
