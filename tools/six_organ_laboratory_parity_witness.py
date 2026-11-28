"""Frozen-main versus six-organ real Laboratory behavioral witness.

Invoke this script in two separate Python processes, once importing the
immutable Doctor baseline and once importing the six-organ implementation.
The caller MUST verify each imported Doctor's checkout path. Outputs only
stable behavioral observations, not UUIDs, world epochs, neural hashes or
other incomparable engineering identities.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

import doctor_lives
from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.neural import DEFAULT_CONFIG

from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.home_life import HomeLife
from pretorius_lab.daily_rhythm import DailyRhythm
from pretorius_lab.subject_port import SubjectPort


def verify_source() -> None:
    requested = os.environ.get("EXPECTED_DOCTOR_ROOT")
    if not requested:
        raise RuntimeError("EXPECTED_DOCTOR_ROOT must pin the checkout")
    actual = Path(doctor_lives.__file__).resolve()
    expected = Path(requested).resolve()
    if not actual.is_relative_to(expected):
        raise RuntimeError(f"Expected Doctor from {expected}; imported {actual}")


def witness(*, six_organ: bool) -> dict:
    config = dict(DEFAULT_CONFIG)
    config.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        habitat = SpatialHabitat.create(root / "world.sqlite3")
        HomeLife(habitat).initialize()
        DailyRhythm(habitat).initialize()
        subject = SubjectPort(habitat)
        doctor = PretoriusBrainPort(root / "brain", neural_config=config)
        if six_organ:
            # Deliberately unavailable in frozen main: no second brain.
            from doctor_lives.organs import SixOrganRuntime

            runtime = SixOrganRuntime(doctor)
            bridge = runtime.bind_laboratory(subject, authorized=True)
        else:
            runtime = None
            bridge = DoctorHomeBridge(doctor, subject, authorized=True)

        values = []
        for report in (
            bridge.observe(),
            bridge.act("walk", event_id="historical-hall", station="station:hall"),
            bridge.act(
                "walk", event_id="historical-stool",
                station="station:shop:private",
            ),
            bridge.act("advance", event_id="historical-time", minutes=120),
            bridge.observe(),
        ):
            if report["status"] != "admitted":
                raise AssertionError("First physical episode not newly admitted")
            subject_frame = report["subject"]["inner"]
            if not subject_frame.startswith(("I ", "My ", "Mine ", "Me ")):
                raise AssertionError("Non-first-person world experience")
            if "world_epoch" in subject_frame or "foot_soreness" in subject_frame:
                raise AssertionError("Engineer world/body state leaked")
            values.append({
                "first_person": subject_frame,
                "speech": report["subject"].get("spoken_aloud"),
            })
        tick_before = doctor.brain.store.tick
        replay = bridge.act(
            "walk", event_id="historical-stool",
            station="station:shop:private",
        )
        if replay["status"] != "already_admitted":
            raise AssertionError("World replay created a new experience")
        if doctor.brain.store.tick != tick_before:
            raise AssertionError("World replay mutated memory")
        if runtime is None:
            policy = doctor.cognition(trigger="historical-lab")["selected_action"]
            doctor.save()
        else:
            policy = runtime.noesis.deliberate(
                host_trigger="historical-lab"
            ).selected_tendency
            runtime.checkpoint()
        if runtime is None:
            reopened = PretoriusBrainPort(root / "brain")
            reopened_bridge = DoctorHomeBridge(
                reopened, subject, authorized=True
            )
        else:
            reopened_runtime = SixOrganRuntime.open(root / "brain")
            reopened = reopened_runtime._port
            reopened_bridge = reopened_runtime.bind_laboratory(
                subject, authorized=True
            )
        after_restart = reopened_bridge.act(
            "walk", event_id="historical-stool",
            station="station:shop:private",
        )
        if (after_restart["status"] != "already_admitted"
                or after_restart["memory_id"] != replay["memory_id"]):
            raise AssertionError("Restart caused double admission")
        memories = [
            m for m in reopened.brain.store.memories(False)
            if m["source"].startswith("laboratory-home:")
        ]
        return {
            "events": values,
            "selected_tendency": policy,
            "replayed_experience": replay["subject"]["inner"],
            "restarted_experience": after_restart["subject"]["inner"],
            "source_memory_text": sorted(m["text"] for m in memories),
            "source_memory_classes": sorted(
                m["evidence_class"] for m in memories
            ),
            "body": subject.home.audit_state()["body"],
            "station": subject.embodied.verify()["station"],
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("classic", "six"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verify_source()
    result = witness(six_organ=args.mode == "six")
    args.output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Verified {args.mode} Laboratory episode, "
        f"{len(result['events'])} source-attested events"
    )


if __name__ == "__main__":
    main()
