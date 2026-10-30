"""Measure the pre-M2 host-offered behavior against the independent day judge.

This deliberately DOES NOT fabricate missing goals, rest, restart or ablations.
The failing judge result is the M2 work queue, not a passing demonstration.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.noesis_lab_work import propose_noesis_work, execute_noesis_work
from scripts.verify_day import judge, SCHEMA, LAB_PIN


def probe(root: Path, lab_root: Path):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.book_library import BookLibrary
    from pretorius_lab.subject_port import SubjectPort

    root.mkdir(parents=True, exist_ok=True)
    world = SpatialHabitat.create(root / "world.sqlite3")
    HomeLife(world).initialize()
    DailyRhythm(world).initialize()
    BookLibrary(world).initialize()
    config = dict(DEFAULT_CONFIG)
    config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                  input_degree=4, action_population_size=8, seed=1842)
    doctor = PretoriusBrainPort(root / "brain", neural_config=config)
    bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
    # Existing M1 approach: host arranges a working opportunity by choosing
    # two concrete physical navigation commands. This MUST NOT pass check b.
    bridge.act("walk", event_id="m1-host-center", station="station:center")
    bridge.act("walk", event_id="m1-host-bench", station="station:bench")
    proposal = propose_noesis_work(bridge, outcome_learning_enabled=True)
    work = execute_noesis_work(bridge, decision_id=proposal.decision_id,
                               event_id="m1-native-work", authorized_world_action=True)
    doctor.save()
    manifest = {
        "schema": SCHEMA, "lab_pin": LAB_PIN, "brain_db": "brain/brain.sqlite3",
        "world_db": "world.sqlite3",
        "intent_db": "world.sqlite3.doctor-action-intents.sqlite3",
        "host_opportunities": [{"tick": 1}, {"tick": 2}],
        "restart": None, "ablation": [], "random_baseline": None,
        "verified_need_conflict": False,
    }
    (root / "day.json").write_text(json.dumps(manifest, sort_keys=True))
    result = judge(root, lab_root)
    report = {"probe": "m1-host-offered-real-Lab",
              "native_work_action": work["action"],
              "native_work_decision": proposal.decision_id,
              "judge": result}
    print(json.dumps(report, indent=2, sort_keys=True))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--lab-root", required=True, type=Path)
    args = parser.parse_args()
    result = probe(args.run, args.lab_root)
    # This is a negative control: original M1 behavior must NOT pass M2.
    return 0 if not result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
