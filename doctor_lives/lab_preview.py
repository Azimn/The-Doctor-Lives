"""One-time experimental genesis using the original Doctor and Laboratory.

Operator-only; never a planner, source of lived memory, world command, or renderer.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path


def initialize_preview(workspace: str | Path) -> dict:
    """Atomically publish two verified canonical authorities in one directory.

    An already-existing workspace is NEVER reseeded, migrated, or overwritten.
    Both authorities are staged as siblings on the same filesystem. Failed
    genesis leaves no publishable workspace and no invented lived experience.
    """
    destination = Path(workspace).expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Preview workspace already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from .cognition import PretoriusBrain
    from .organs import SixOrganRuntime

    staging = Path(tempfile.mkdtemp(prefix=".pretorius-preview-", dir=destination.parent))
    published = False
    try:
        state = staging / "state"
        world_path = staging / "laboratory.sqlite3"
        world = SpatialHabitat.create(world_path)
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        world_proof = world.verify()
        HomeLife(world).verify()
        DailyRhythm(world).verify()

        brain = PretoriusBrain(state)
        brain.save()
        SixOrganRuntime.open(state)  # Same original brain, not a new selector.
        if not (state / "brain.sqlite3").is_file() or not (
            state / "pretorius_recurrent.npz"
        ).is_file():
            raise RuntimeError("Incomplete canonical brain or recurrent checkpoint")
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f"Preview workspace appeared during genesis: {destination}")
        staging.rename(destination)
        published = True
        return {
            "schema": "doctor-laboratory-experimental-genesis.v1",
            "status": "ready_for_operator_start",
            "release_accepted": False,
            "workspace": str(destination),
            "state": str(destination / "state"),
            "world": str(destination / "laboratory.sqlite3"),
            "world_epoch": world_proof["world_epoch"],
            "laboratory_source_commit_runtime_attested": False,
            "subject_experienced_initialization": False,
            "books_installed": False,
            "three_task_autonomy_proven": False,
        }
    finally:
        if not published:
            shutil.rmtree(staging, ignore_errors=True)
