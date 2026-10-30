"""R5: exercise installed Doctor/Laboratory wheels outside either source checkout.

Run with the clean wheel virtualenv Python and its console-script PATH. This
script is an external test harness, not a new production host or memory store.
"""
from __future__ import annotations

from contextlib import closing
import gc

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.neural import DEFAULT_CONFIG, NeuralCheckpointError, PretoriusRecurrentSubstrate
import numpy as np
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


def _poison_recurrent_degree(path: Path) -> None:
    """Keep a shape-valid 4,096-neuron NPZ, but make cold loading impossible."""
    with np.load(path, allow_pickle=False) as checkpoint:
        fields = {name: np.array(checkpoint[name], copy=True)
                  for name in checkpoint.files}
    cfg = json.loads(str(fields["cfg_json"].item()))
    assert cfg["neurons"] == 4096 and cfg["avg_recurrent_degree"] > 0
    cfg["avg_recurrent_degree"] = -1
    fields["cfg_json"] = np.asarray(json.dumps(cfg, sort_keys=True))
    with path.open("wb") as stream:
        np.savez_compressed(stream, **fields)
    # This is the precise QA counterexample: structural checks alone pass.
    assert PretoriusRecurrentSubstrate._validate_checkpoint_file(path)["cfg"][
        "avg_recurrent_degree"] == -1
    try:
        PretoriusRecurrentSubstrate.load(path)
    except NeuralCheckpointError:
        pass
    else:
        raise AssertionError("Unloadable checkpoint unexpectedly passed cold load")


def _crash(world_path: Path, brain_path: Path):
    world = SpatialHabitat(world_path)
    doctor = PretoriusBrainPort(brain_path)
    from doctor_lives.lab_home_bridge import DoctorHomeBridge

    bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)

    def die_after_original_world_commit(frame, source, **kwargs):
        with closing(world._open()) as db:
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
        # Operator P0: prove the installed, non-editable offline wheel itself
        # creates the ONE canonical brain and original Laboratory from scratch.
        # This is genesis, not Pretorius's lived experience or an R4 goal.
        preview = root / "operator-preview"
        preview_genesis = json.loads(_run([
            console, "preview-init", "--workspace", str(preview),
        ]).stdout)
        assert preview_genesis["schema"] == "doctor-laboratory-experimental-genesis.v1"
        assert not preview_genesis["release_accepted"]
        assert not preview_genesis["subject_experienced_initialization"]
        assert not preview_genesis["three_task_autonomy_proven"]
        assert not preview_genesis["books_installed"]
        preview_state = preview / "state"
        preview_world = preview / "laboratory.sqlite3"
        assert preview_state.joinpath("brain.sqlite3").is_file()
        assert preview_state.joinpath("pretorius_recurrent.npz").is_file()
        preview_start = [
            console, "--state", str(preview_state), "lab-start",
            "--world", str(preview_world),
        ]
        for _ in range(2):
            actual = json.loads(_run(preview_start).stdout)
            assert actual["status"] == "ready" and actual["abandoned"] == 0
        # An untouched genesis has no physical receipt binding the two
        # authorities, so archival verification correctly refuses it.
        # Prepare the actual original bench with explicitly operator-owned
        # navigation and wear. The next action is NOT chosen by this harness.
        # This is an offered Noesis action, not proof of self-initiated R4 life.
        from doctor_lives.organs import SixOrganRuntime
        runtime = SixOrganRuntime.open(preview_state)
        preview_bridge = runtime.bind_laboratory(
            SubjectPort(SpatialHabitat(preview_world)), authorized=True,
        )
        preview_bridge.act("walk", event_id="preview-setup-center",
                           station="station:center")
        preview_bridge.act("walk", event_id="preview-setup-bench",
                           station="station:bench")
        setup_wear = preview_bridge.act(
            "experiment", event_id="preview-setup-real-wear",
        )
        assert setup_wear["status"] == "admitted"
        runtime.checkpoint()
        del preview_bridge, runtime
        gc.collect()

        noesis_work_id = "preview-noesis-physical-work"
        work_report = json.loads(_run([
            console, "--state", str(preview_state), "lab-work",
            "--world", str(preview_world), "--event-id", noesis_work_id,
        ]).stdout)
        assert work_report["schema"] == "doctor-laboratory-offline-work.v1"
        assert work_report["status"] == "admitted"
        assert work_report["selection"] == "original_noesis"
        assert work_report["action"] in ("repair", "experiment")
        with closing(SpatialHabitat(preview_world)._open()) as world_db:
            receipt = world_db.execute(
                "SELECT event_hash FROM rhythm_events WHERE event_id=?",
                (noesis_work_id,),
            ).fetchone()
        assert receipt is not None
        physical_source = "laboratory-home:action:" + receipt[0]
        source_memories = [
            m for m in PretoriusBrainPort(preview_state).brain.store.memories(False)
            if m["source"] == physical_source
        ]
        assert len(source_memories) == 1
        assert source_memories[0]["evidence_class"] == "lived_runtime_memory"
        assert source_memories[0]["text"] == work_report["subject_frames"][-1]["inner"]
        with closing(PretoriusBrainPort(preview_state).brain.store.connect()) as mind_db:
            decision = mind_db.execute(
                "SELECT state_pressure_json FROM policy_decisions "
                "WHERE trigger='noesis_situated_choice' ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        assert decision is not None
        assert setup_wear["memory_id"] in json.loads(
            decision[0]
        )["used_outcome_memory_ids"]

        # The installed 4,096-neuron preview must survive a complete offline
        # backup/restore into a new, clean workspace, not merely two starts.
        preview_archive = root / "operator-preview-backup"
        saved = json.loads(_run([
            console, "--state", str(preview_state), "lab-backup",
            "--world", str(preview_world), "--output", str(preview_archive),
        ]).stdout)
        assert saved["status"] == "backed_up"
        restored_preview = root / "operator-preview-restored"
        restored_preview_state = restored_preview / "state"
        restored_preview_world = restored_preview / "laboratory.sqlite3"
        restored = json.loads(_run([
            console, "--state", str(restored_preview_state), "lab-restore",
            "--world", str(restored_preview_world), "--archive",
            str(preview_archive),
        ]).stdout)
        assert restored["status"] == "restored"
        restored_start = json.loads(_run([
            console, "--state", str(restored_preview_state), "lab-start",
            "--world", str(restored_preview_world),
        ]).stdout)
        assert restored_start["status"] == "ready"
        assert restored_start["abandoned"] == 0
        assert SpatialHabitat(restored_preview_world).verify()["world_epoch"] == (
            preview_genesis["world_epoch"]
        )
        assert sum(
            m["source"] == physical_source
            for m in PretoriusBrainPort(restored_preview_state).brain.store.memories(False)
        ) == 1
        with closing(SpatialHabitat(restored_preview_world)._open()) as restored_db:
            assert restored_db.execute(
                "SELECT COUNT(*) FROM rhythm_events WHERE event_id=?",
                (noesis_work_id,),
            ).fetchone()[0] == 1
        with np.load(restored_preview_state / "pretorius_recurrent.npz",
                     allow_pickle=False) as checkpoint:
            assert json.loads(str(checkpoint["cfg_json"].item()))["neurons"] == 4096

        # A competing empty backup destination must never be overwritten
        # between the final check and the actual directory publication.
        from unittest.mock import patch
        from doctor_lives import lab_backup, lab_preview
        contested_backup = root / "competing-empty-backup"
        real_publish = lab_preview._publish_noreplace

        def competing_publisher(staging, destination):
            assert destination == contested_backup.resolve()
            destination.mkdir()
            return real_publish(staging, destination)

        with patch("doctor_lives.lab_preview._publish_noreplace",
                   side_effect=competing_publisher):
            try:
                lab_backup.backup(preview_state, preview_world, contested_backup)
            except FileExistsError:
                pass
            else:
                raise AssertionError("Backup replaced a competing empty directory")
        assert contested_backup.is_dir()
        assert list(contested_backup.iterdir()) == []
        assert not list(root.glob(".doctor-backup-*"))
        gc.collect()  # Close discarded SQLite readers before Windows temp cleanup.

        no_reseed = subprocess.run([
            console, "preview-init", "--workspace", str(preview),
        ], capture_output=True, text=True, timeout=120)
        assert no_reseed.returncode != 0 and not no_reseed.stdout
        assert SpatialHabitat(preview_world).verify()["world_epoch"] == (
            preview_genesis["world_epoch"]
        )

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
        with closing(world._open()) as db:
            rows = db.execute(
                "SELECT event_hash FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchall()
        assert len(rows) == 1, "World action was not committed exactly once"
        source = "laboratory-home:action:" + rows[0][0]
        before = PretoriusBrainPort(brain_path)
        assert not any(m["source"] == source for m in before.brain.store.memories(False))

        # R5: snapshot the actual post-world/pre-brain crash, including the
        # pending action journal, and restore into a second clean state/world.
        # No action ID is passed to the installed CLI during recovery.
        archive = root / "quiescent-backup"
        backup_result = json.loads(_run([
            console, "--state", str(brain_path), "lab-backup",
            "--world", str(world_path), "--output", str(archive),
        ]).stdout)
        assert backup_result["status"] == "backed_up"
        assert (archive / "brain" / "pretorius_recurrent.npz").is_file()
        assert (archive / "action-intents.sqlite3").is_file()
        restored_brain = root / "restored-brain"
        restored_world = root / "restored-world.sqlite3"
        restore_result = json.loads(_run([
            console, "--state", str(restored_brain), "lab-restore",
            "--world", str(restored_world), "--archive", str(archive),
        ]).stdout)
        assert restore_result["status"] == "restored"
        restored_command = [
            console, "--state", str(restored_brain), "lab-start",
            "--world", str(restored_world),
        ]
        restored_first = json.loads(_run(restored_command).stdout)
        assert restored_first["recovered"] == 1
        assert len(restored_first["subject_frames"]) == 1
        restored_memories = [
            m for m in PretoriusBrainPort(restored_brain).brain.store.memories(False)
            if m["source"] == source
        ]
        assert len(restored_memories) == 1
        assert restored_memories[0]["text"] == restored_first["subject_frames"][0]["inner"]
        assert restored_memories[0]["evidence_class"] == "lived_runtime_memory"
        assert json.loads(_run(restored_command).stdout)["recovered"] == 0
        with closing(SpatialHabitat(restored_world)._open()) as restored_db:
            assert restored_db.execute(
                "SELECT COUNT(*) FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchone()[0] == 1

        # Corrupt the backed-up neural checkpoint: integrity verification must
        # refuse to create any replacement mind or physical world.
        corrupt = root / "corrupt-backup"
        shutil.copytree(archive, corrupt)
        with (corrupt / "brain" / "pretorius_recurrent.npz").open("ab") as out:
            out.write(b"tampered")
        bad_brain, bad_world = root / "bad-brain", root / "bad-world.sqlite3"
        rejected = subprocess.run([
            console, "--state", str(bad_brain), "lab-restore",
            "--world", str(bad_world), "--archive", str(corrupt),
        ], capture_output=True, text=True, timeout=120)
        assert rejected.returncode != 0 and not rejected.stdout
        assert not bad_brain.exists() and not bad_world.exists()

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
        with closing(world._open()) as db:
            assert db.execute(
                "SELECT COUNT(*) FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchone()[0] == 1
        assert sum(m["source"] == source for m in
                   PretoriusBrainPort(brain_path).brain.store.memories(False)) == 1

        # R6: the installed wheel's optional human transcript comes from
        # the same genuine original-world LOOK and canonical lived memory.
        # It must never serialize action IDs, engineering state or tool JSON.
        human = _run([
            console, "--state", str(brain_path), "lab-run",
            "--world", str(world_path), "--seconds", "0.25",
            "--interval-seconds", "0.1", "--human",
        ])
        assert re.fullmatch(r"@[0-9]{3}", human.stdout.splitlines()[0])
        assert any(line.startswith(("I ", "My ", "Mine ", "Me "))
                   for line in human.stdout.splitlines())
        for hidden in ("world_epoch", "event_id", "memory_id",
                       "neural_scores", "laboratory-home:", '"schema"'):
            assert hidden not in human.stdout, hidden
        actual_observations = [
            m["text"] for m in PretoriusBrainPort(brain_path).brain.store.memories(False)
            if m["source"].startswith("laboratory-home:observe:")
        ]
        assert actual_observations and actual_observations[-1] in human.stdout

        # Independent QA R5 control: a valid brain A with an admitted,
        # authenticated action must NEVER be archived against a different,
        # independently valid original Laboratory world B and its journal.
        foreign_world_path = root / "foreign-world.sqlite3"
        foreign_brain_path = root / "foreign-brain"
        foreign_world = SpatialHabitat.create(foreign_world_path)
        HomeLife(foreign_world).initialize()
        DailyRhythm(foreign_world).initialize()
        foreign_port = PretoriusBrainPort(foreign_brain_path, neural_config=config)
        from doctor_lives.lab_home_bridge import DoctorHomeBridge
        foreign_bridge = DoctorHomeBridge(
            foreign_port, SubjectPort(foreign_world), authorized=True,
        )
        foreign_bridge.act(
            "walk", event_id="foreign-world-walk", station="station:center",
        )
        with closing(foreign_world._open()) as foreign_db:
            foreign_hash = foreign_db.execute(
                "SELECT event_hash FROM embodied_events WHERE event_id=?",
                ("foreign-world-walk",),
            ).fetchone()[0]
        assert foreign_hash != rows[0][0]
        assert any(
            m["source"] == "laboratory-home:action:" + foreign_hash
            for m in foreign_port.brain.store.memories(False)
        )
        foreign_archive = root / "foreign-archive"
        assert json.loads(_run([
            console, "--state", str(foreign_brain_path), "lab-backup",
            "--world", str(foreign_world_path), "--output", str(foreign_archive),
        ]).stdout)["status"] == "backed_up"

        # Source-backed negative: SQLite integrity and every action-row digest
        # remain valid, but the ORIGINAL Laboratory rejects the world ledger.
        # The installed CLI must reject both backup and a manifest-rehashed
        # restore before creating an archive or a new authority.
        from pretorius_lab.physics import Conflict
        for damaged_field, replacement in (
            ("state", {"tampered": True}),
            ("head_hash", "f" * 64),
        ):
            damaged_world = root / f"damaged-{damaged_field}.sqlite3"
            shutil.copyfile(foreign_archive / "world.sqlite3", damaged_world)
            shutil.copyfile(
                foreign_archive / "action-intents.sqlite3",
                Path(str(damaged_world) + ".doctor-action-intents.sqlite3"),
            )
            with closing(sqlite3.connect(damaged_world)) as damaged_db:
                damaged_db.execute(
                    "UPDATE meta SET value=? WHERE key=?",
                    (json.dumps(replacement), damaged_field),
                )
                assert damaged_db.execute(
                    "PRAGMA integrity_check"
                ).fetchone() == ("ok",)
                damaged_db.commit()
            try:
                SpatialHabitat(damaged_world).verify()
            except Conflict:
                pass
            else:
                raise AssertionError(
                    f"Original Laboratory accepted corrupt {damaged_field}"
                )

            denied_archive = root / f"denied-{damaged_field}-backup"
            bad_backup = subprocess.run([
                console, "--state", str(foreign_brain_path), "lab-backup",
                "--world", str(damaged_world), "--output", str(denied_archive),
            ], capture_output=True, text=True, timeout=120)
            assert bad_backup.returncode != 0 and not bad_backup.stdout
            assert "Original Laboratory world/ledger verification failed" in bad_backup.stderr
            assert not denied_archive.exists()

            damaged_archive = root / f"damaged-{damaged_field}-archive"
            shutil.copytree(foreign_archive, damaged_archive)
            # The source is WAL-mode. Checkpoint the corrupted metadata into
            # the main database before copying bytes into the sealed archive.
            # Copying only a WAL-mode main file without checkpointing would
            # silently restore the original valid metadata.
            with closing(sqlite3.connect(damaged_world)) as source_db:
                checkpoint = source_db.execute(
                    "PRAGMA wal_checkpoint(TRUNCATE)"
                ).fetchone()
                assert checkpoint[0] == 0, checkpoint
            member = damaged_archive / "world.sqlite3"
            shutil.copyfile(damaged_world, member)
            # Never open a sealed archive SQLite member directly: the
            # original Laboratory can create -wal/-shm files on open.
            with tempfile.TemporaryDirectory(prefix="damaged-world-proof-") as proof_dir:
                proof_world = Path(proof_dir) / "world.sqlite3"
                shutil.copyfile(member, proof_world)
                try:
                    SpatialHabitat(proof_world).verify()
                except Conflict:
                    pass
                else:
                    raise AssertionError(
                        "Corrupt world did not survive SQLite snapshot"
                    )
                # The pinned Laboratory verifies using sqlite3 context
                # managers that do not close on Windows. Reclaim their
                # unreferenced connections before removing the proof copy.
                gc.collect()
            damaged_manifest = damaged_archive / "manifest.json"
            data = json.loads(damaged_manifest.read_text(encoding="utf-8"))
            data["files"]["world.sqlite3"] = {
                "sha256": hashlib.sha256(member.read_bytes()).hexdigest(),
                "bytes": member.stat().st_size,
            }
            damaged_manifest.write_text(
                json.dumps(data, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            denied_brain = root / f"denied-{damaged_field}-brain"
            denied_world = root / f"denied-{damaged_field}-world.sqlite3"
            bad_restore = subprocess.run([
                console, "--state", str(denied_brain), "lab-restore",
                "--world", str(denied_world), "--archive", str(damaged_archive),
            ], capture_output=True, text=True, timeout=120)
            assert bad_restore.returncode != 0 and not bad_restore.stdout
            assert "Original Laboratory world/ledger verification failed" in bad_restore.stderr
            assert not denied_brain.exists() and not denied_world.exists()
            assert not Path(
                str(denied_world) + ".doctor-action-intents.sqlite3"
            ).exists()

        mixed_backup = root / "forbidden-mixed-backup"
        mixed_backup_attempt = subprocess.run([
            console, "--state", str(brain_path), "lab-backup",
            "--world", str(foreign_world_path), "--output", str(mixed_backup),
        ], capture_output=True, text=True, timeout=120)
        assert mixed_backup_attempt.returncode != 0
        assert not mixed_backup_attempt.stdout and not mixed_backup.exists()

        # Make a valid A/A archive AFTER A's lived memory was admitted.
        admitted_archive = root / "admitted-archive"
        assert json.loads(_run([
            console, "--state", str(brain_path), "lab-backup",
            "--world", str(world_path), "--output", str(admitted_archive),
        ]).stdout)["status"] == "backed_up"
        mixed_archive = root / "mixed-valid-digests"
        shutil.copytree(admitted_archive, mixed_archive)
        manifest_path = mixed_archive / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name in ("world.sqlite3", "action-intents.sqlite3"):
            shutil.copyfile(foreign_archive / name, mixed_archive / name)
            member = mixed_archive / name
            manifest["files"][name] = {
                "sha256": hashlib.sha256(member.read_bytes()).hexdigest(),
                "bytes": member.stat().st_size,
            }
        manifest_path.write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        mixed_brain = root / "mixed-restored-brain"
        mixed_world = root / "mixed-restored-world.sqlite3"
        mixed_restore_attempt = subprocess.run([
            console, "--state", str(mixed_brain), "lab-restore",
            "--world", str(mixed_world), "--archive", str(mixed_archive),
        ], capture_output=True, text=True, timeout=120)
        assert mixed_restore_attempt.returncode != 0
        assert not mixed_restore_attempt.stdout
        assert not mixed_brain.exists() and not mixed_world.exists()
        assert not Path(str(mixed_world) + ".doctor-action-intents.sqlite3").exists()

        # Existing restored authorities are never overwritten, even by a
        # completely valid coherent archive.
        original_brain_digest = hashlib.sha256(
            (restored_brain / "brain.sqlite3").read_bytes()
        ).hexdigest()
        original_world_digest = hashlib.sha256(
            restored_world.read_bytes()
        ).hexdigest()
        existing_restore_attempt = subprocess.run([
            console, "--state", str(restored_brain), "lab-restore",
            "--world", str(restored_world), "--archive", str(admitted_archive),
        ], capture_output=True, text=True, timeout=120)
        assert existing_restore_attempt.returncode != 0
        assert not existing_restore_attempt.stdout
        assert hashlib.sha256(
            (restored_brain / "brain.sqlite3").read_bytes()
        ).hexdigest() == original_brain_digest
        assert hashlib.sha256(
            restored_world.read_bytes()
        ).hexdigest() == original_world_digest

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
        with closing(full_world._open()) as db:
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
        # R5 full-size restore matrix: prove the ORIGINAL 4,096-neuron
        # recurrent policy, original world and pending action journal survive
        # an installed-wheel backup/restore of a post-world/pre-brain crash.
        # This is a separate positive from the preserved 128-neuron controls.
        full_archive = root / "full-size-4096-backup"
        full_backup = json.loads(_run([
            console, "--state", str(full_brain_path), "lab-backup",
            "--world", str(full_world_path), "--output", str(full_archive),
        ]).stdout)
        assert full_backup["status"] == "backed_up"
        assert (full_archive / "brain" / "pretorius_recurrent.npz").is_file()
        assert (full_archive / "action-intents.sqlite3").is_file()
        full_restored_brain = root / "full-size-restored-brain"
        full_restored_world = root / "full-size-restored-world.sqlite3"
        full_restore = json.loads(_run([
            console, "--state", str(full_restored_brain), "lab-restore",
            "--world", str(full_restored_world), "--archive", str(full_archive),
        ]).stdout)
        assert full_restore["status"] == "restored"
        restored_full_port = PretoriusBrainPort(full_restored_brain)
        assert restored_full_port.brain.neural.n == 4096
        assert restored_full_port.brain.neural.cfg == DEFAULT_CONFIG
        restored_full_command = [
            console, "--state", str(full_restored_brain),
            "lab-start", "--world", str(full_restored_world),
        ]
        restored_full_first = json.loads(_run(restored_full_command).stdout)
        assert restored_full_first["status"] == "ready"
        assert restored_full_first["recovered"] == 1
        assert len(restored_full_first["subject_frames"]) == 1
        restored_full_memories = [
            m for m in PretoriusBrainPort(full_restored_brain).brain.store.memories(False)
            if m["source"] == full_source
        ]
        assert len(restored_full_memories) == 1
        assert restored_full_memories[0]["evidence_class"] == "lived_runtime_memory"
        assert restored_full_memories[0]["text"] == restored_full_first["subject_frames"][0]["inner"]
        assert json.loads(_run(restored_full_command).stdout)["recovered"] == 0
        with closing(SpatialHabitat(full_restored_world)._open()) as db:
            assert db.execute(
                "SELECT COUNT(*) FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchone()[0] == 1
        assert sum(
            m["source"] == full_source
            for m in PretoriusBrainPort(full_restored_brain).brain.store.memories(False)
        ) == 1

        # R5 negative matrix at the actual original 4,096-neuron size.
        # A manifest digest is not a neural schema validator: a malicious or
        # damaged archive can have all member hashes recomputed consistently.
        # Each failed restore must leave ALL three authorities absent.
        for failure in (
            "unrehashed-checkpoint",
            "rehashed-invalid-checkpoint",
            "rehashed-unloadable-config",
            "mixed-valid-world-and-journal",
        ):
            invalid_archive = root / ("full-size-" + failure)
            shutil.copytree(full_archive, invalid_archive)
            invalid_manifest_path = invalid_archive / "manifest.json"
            invalid_manifest = json.loads(
                invalid_manifest_path.read_text(encoding="utf-8")
            )
            if failure == "mixed-valid-world-and-journal":
                names = ("world.sqlite3", "action-intents.sqlite3")
                for name in names:
                    shutil.copyfile(foreign_archive / name, invalid_archive / name)
            else:
                names = ("brain/pretorius_recurrent.npz",)
                checkpoint = invalid_archive / names[0]
                if failure == "unrehashed-checkpoint":
                    with checkpoint.open("ab") as stream:
                        stream.write(b"damaged-after-backup")
                elif failure == "rehashed-unloadable-config":
                    _poison_recurrent_degree(checkpoint)
                else:
                    checkpoint.write_bytes(b"not a canonical recurrent checkpoint")
            if failure != "unrehashed-checkpoint":
                for name in names:
                    member = invalid_archive / name
                    invalid_manifest["files"][name] = {
                        "sha256": hashlib.sha256(member.read_bytes()).hexdigest(),
                        "bytes": member.stat().st_size,
                    }
                invalid_manifest_path.write_text(
                    json.dumps(invalid_manifest, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8",
                )
            invalid_brain = root / ("denied-" + failure + "-brain")
            invalid_world = root / ("denied-" + failure + "-world.sqlite3")
            denial = subprocess.run([
                console, "--state", str(invalid_brain), "lab-restore",
                "--world", str(invalid_world),
                "--archive", str(invalid_archive),
            ], capture_output=True, text=True, timeout=120)
            assert denial.returncode != 0 and not denial.stdout, failure
            assert not invalid_brain.exists() and not invalid_world.exists(), failure
            assert not Path(
                str(invalid_world) + ".doctor-action-intents.sqlite3"
            ).exists(), failure

        # The backup direction must likewise reject an already corrupted
        # original 4,096-neuron checkpoint, not seal a useless archive.
        (full_restored_brain / "pretorius_recurrent.npz").write_bytes(
            b"not a canonical recurrent checkpoint"
        )
        denied_full_backup = root / "denied-full-size-checkpoint-backup"
        backup_denial = subprocess.run([
            console, "--state", str(full_restored_brain), "lab-backup",
            "--world", str(full_restored_world),
            "--output", str(denied_full_backup),
        ], capture_output=True, text=True, timeout=120)
        assert backup_denial.returncode != 0 and not backup_denial.stdout
        assert not denied_full_backup.exists()

        # Structurally valid but semantically unloadable full-size neural state
        # must also fail in the BACKUP direction, without altering the source.
        restored_checkpoint = full_restored_brain / "pretorius_recurrent.npz"
        shutil.copyfile(full_archive / "brain" / "pretorius_recurrent.npz",
                        restored_checkpoint)
        _poison_recurrent_degree(restored_checkpoint)
        poisoned_digest = hashlib.sha256(restored_checkpoint.read_bytes()).hexdigest()
        intact_world_digest = hashlib.sha256(full_restored_world.read_bytes()).hexdigest()
        denied_config_backup = root / "denied-full-size-config-backup"
        config_backup_denial = subprocess.run([
            console, "--state", str(full_restored_brain), "lab-backup",
            "--world", str(full_restored_world),
            "--output", str(denied_config_backup),
        ], capture_output=True, text=True, timeout=120)
        assert config_backup_denial.returncode != 0 and not config_backup_denial.stdout
        assert not denied_config_backup.exists()
        assert hashlib.sha256(restored_checkpoint.read_bytes()).hexdigest() == poisoned_digest
        assert hashlib.sha256(full_restored_world.read_bytes()).hexdigest() == intact_world_digest

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
        with closing(full_world._open()) as db:
            assert db.execute(
                "SELECT COUNT(*) FROM embodied_events WHERE event_id=?",
                ("wheel-crash-walk",),
            ).fetchone()[0] == 1
        assert sum(
            m["source"] == full_source
            for m in PretoriusBrainPort(full_brain_path).brain.store.memories(False)
        ) == 1

        # The original Laboratory uses transactional SQLite context managers
        # rather than explicit closes. Do not mask Windows handle leaks by
        # disabling TemporaryDirectory cleanup; reclaim unreferenced handles.
        gc.collect()
        print(json.dumps({"result": "PASS", "installed_console": True,
                          "original_lab_world_actions": 1,
                          "verified_lived_memories": 1,
                          "recovered_on_restart": 1,
                          "recovered_on_second_restart": 0,
                          "missing_authority_denied": True,
                          "journal_backup_restored": True,
                          "restored_crash_recovered": 1,
                          "restored_second_restart": 0,
                          "corrupt_archive_denied": True,
                          "mixed_authority_backup_denied": True,
                          "mixed_authority_restore_denied": True,
                          "existing_restore_denied": True,
                          "corrupt_world_ledger_backup_denied": True,
                          "rehashed_corrupt_world_restore_denied": True,
                          "full_size_4096_original_neurons": 4096,
                          "full_size_4096_recovered": 1,
                          "full_size_4096_second_restart": 0,
                          "full_size_4096_archive_restored": True,
                          "full_size_4096_corrupt_digest_denied": True,
                          "full_size_4096_rehashed_invalid_neural_denied": True,
                          "full_size_4096_rehashed_unloadable_config_denied": True,
                          "full_size_4096_unloadable_config_backup_denied": True,
                          "full_size_4096_mixed_world_denied": True,
                          "full_size_4096_invalid_neural_backup_denied": True,
                          "full_size_4096_restored_recovered": 1,
                          "full_size_4096_restored_second_restart": 0,
                          "installed_human_subject_only": True}, sort_keys=True))


if __name__ == "__main__":
    main()
