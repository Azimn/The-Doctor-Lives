"""R5: exercise installed Doctor/Laboratory wheels outside either source checkout.

Run with the clean wheel virtualenv Python and its console-script PATH. This
script is an external test harness, not a new production host or memory store.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.neural import DEFAULT_CONFIG
from pretorius_lab.daily_rhythm import DailyRhythm
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.home_life import HomeLife
from pretorius_lab.subject_port import SubjectPort


def _run(args, *, expected=0):
    completed = subprocess.run(args, capture_output=True, text=True, timeout=120)
    assert completed.returncode == expected, (
        f"exit {completed.returncode} expected {expected}: {args!r}\n"
        f"stdout={completed.stdout}\nstderr={completed.stderr}"
    )
    return completed


def _crash(world_path: Path, brain_path: Path):
    world = SpatialHabitat(world_path)
    doctor = PretoriusBrainPort(brain_path)
    from doctor_lives.lab_home_bridge import DoctorHomeBridge

    bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)

    def die_after_original_world_commit(frame, source, **kwargs):
        with world._open() as db:
            row = db.execute(
                "SELECT event_hash FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchone()
        assert row and source == "laboratory-home:action:" + row[0]
        assert not any(m["source"] == source for m in doctor.brain.store.memories(False))
        os._exit(79)

    bridge._admit_verified = die_after_original_world_commit
    bridge.act("walk", event_id="wheel-crash-walk", station="station:center")
    raise AssertionError("Physical world commit did not reach crash boundary")


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--crash":
        _crash(Path(sys.argv[2]), Path(sys.argv[3]))
        return
    assert len(sys.argv) == 1, "Unexpected smoke-test arguments"
    import doctor_lives
    import pretorius_lab

    # No editable source tree or PYTHONPATH is allowed to satisfy imports.
    assert not os.environ.get("PYTHONPATH"), "PYTHONPATH masks wheel packaging defects"
    assert "site-packages" in str(Path(doctor_lives.__file__).resolve())
    assert "site-packages" in str(Path(pretorius_lab.__file__).resolve())
    console = shutil.which("doctor-lives")
    assert console and Path(console).parent == Path(sys.executable).parent

    with tempfile.TemporaryDirectory(prefix="pretorius-wheel-smoke-") as temp:
        root = Path(temp)
        world_path, brain_path = root / "world.sqlite3", root / "brain"
        world = SpatialHabitat.create(world_path)
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        config = dict(DEFAULT_CONFIG)
        config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                      input_degree=4, action_population_size=8, seed=1842)
        PretoriusBrainPort(brain_path, neural_config=config)

        crashed = _run([sys.executable, __file__, "--crash", str(world_path),
                        str(brain_path)], expected=79)
        assert not crashed.stdout, "Crash child emitted unexpected output"
        with world._open() as db:
            rows = db.execute(
                "SELECT event_hash FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchall()
        assert len(rows) == 1, "World action was not committed exactly once"
        source = "laboratory-home:action:" + rows[0][0]
        before = PretoriusBrainPort(brain_path)
        assert not any(m["source"] == source for m in before.brain.store.memories(False))

        command = [console, "--state", str(brain_path), "lab-start",
                   "--world", str(world_path)]
        first = _run(command)
        result = json.loads(first.stdout)
        assert result["schema"] == "doctor-laboratory-offline-start.v1"
        assert result["status"] == "ready" and result["recovered"] == 1
        assert len(result["subject_frames"]) == 1
        assert result["subject_frames"][0]["inner"].startswith("I ")
        assert re.fullmatch(r"@[0-9]{3}", result["clock"]["beat"])
        assert result["clock"]["utc"].endswith("Z")
        assert "event_id" not in first.stdout and "world_epoch" not in first.stdout

        memories = [m for m in PretoriusBrainPort(brain_path).brain.store.memories(False)
                    if m["source"] == source]
        assert len(memories) == 1
        assert memories[0]["text"] == result["subject_frames"][0]["inner"]
        assert memories[0]["evidence_class"] == "lived_runtime_memory"
        second = json.loads(_run(command).stdout)
        assert second["recovered"] == 0
        with world._open() as db:
            assert db.execute(
                "SELECT COUNT(*) FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchone()[0] == 1
        assert sum(m["source"] == source for m in
                   PretoriusBrainPort(brain_path).brain.store.memories(False)) == 1

        # Clean-wheel CLI must not silently mint an absent world or brain.
        missing = root / "absent-world.sqlite3"
        denied = subprocess.run(
            [console, "--state", str(brain_path), "lab-start", "--world", str(missing)],
            capture_output=True, text=True, timeout=120,
        )
        assert denied.returncode != 0 and not denied.stdout and not missing.exists()
        # Separate default-size 4,096-neuron ORIGINAL recurrent-policy smoke.
        # Preserve the accepted 128-neuron baseline above unchanged.
        full_world_path = root / "full-world.sqlite3"
        full_brain_path = root / "full-brain"
        full_world = SpatialHabitat.create(full_world_path)
        HomeLife(full_world).initialize()
        DailyRhythm(full_world).initialize()
        full_port = PretoriusBrainPort(
            full_brain_path, neural_config=dict(DEFAULT_CONFIG),
        )
        assert full_port.brain.neural.n == 4096
        assert full_port.brain.neural.cfg == DEFAULT_CONFIG
        assert (full_brain_path / "pretorius_recurrent.npz").is_file()
        full_crashed = _run(
            [sys.executable, __file__, "--crash",
             str(full_world_path), str(full_brain_path)],
            expected=79,
        )
        assert not full_crashed.stdout
        with full_world._open() as db:
            full_rows = db.execute(
                "SELECT event_hash FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchall()
        assert len(full_rows) == 1
        full_source = "laboratory-home:action:" + full_rows[0][0]
        assert not any(
            m["source"] == full_source
            for m in PretoriusBrainPort(full_brain_path).brain.store.memories(False)
        )
        full_command = [
            console, "--state", str(full_brain_path),
            "lab-start", "--world", str(full_world_path),
        ]
        full_first = json.loads(_run(full_command).stdout)
        assert full_first["status"] == "ready"
        assert full_first["recovered"] == 1
        assert len(full_first["subject_frames"]) == 1
        full_memories = [
            m for m in PretoriusBrainPort(full_brain_path).brain.store.memories(False)
            if m["source"] == full_source
        ]
        assert len(full_memories) == 1
        assert full_memories[0]["evidence_class"] == "lived_runtime_memory"
        assert full_memories[0]["text"] == full_first["subject_frames"][0]["inner"]
        assert json.loads(_run(full_command).stdout)["recovered"] == 0
        with full_world._open() as db:
            assert db.execute(
                "SELECT COUNT(*) FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchone()[0] == 1
        assert sum(
            m["source"] == full_source
            for m in PretoriusBrainPort(full_brain_path).brain.store.memories(False)
        ) == 1

        print(json.dumps({"result": "PASS", "installed_console": True,
                          "original_lab_world_actions": 1,
                          "verified_lived_memories": 1,
                          "recovered_on_restart": 1,
                          "recovered_on_second_restart": 0,
                          "missing_authority_denied": True,
                          "full_size_4096_original_neurons": 4096,
                          "full_size_4096_recovered": 1,
                          "full_size_4096_second_restart": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
