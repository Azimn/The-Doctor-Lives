"""One-time experimental genesis using the original Doctor and Laboratory.

Operator-only; never a planner, source of lived memory, world command, or renderer.
"""
from __future__ import annotations

import os
import sys
import shutil
import tempfile
import gc
from pathlib import Path


def _publish_noreplace(staging: Path, destination: Path) -> None:
    """Publish a fully staged directory without ever replacing an existing path.

    pathlib.Path.rename is unsafe on POSIX: an empty directory created after
    a last-minute existence check can be silently replaced. Linux renameat2
    RENAME_NOREPLACE and Windows rename supply kernel-enforced exclusivity.
    Unsupported platforms/filesystems fail closed rather than risking a brain.
    """
    if os.name == "nt":
        # Windows MoveFileEx without MOVEFILE_REPLACE_EXISTING, as used by
        # os.rename, refuses an already existing directory or file.
        staging.rename(destination)
        return
    if sys.platform.startswith("linux"):
        import ctypes

        libc = ctypes.CDLL(None, use_errno=True)
        renameat2 = getattr(libc, "renameat2", None)
        if renameat2 is None:
            raise RuntimeError("Atomic no-replace preview publish unavailable on this Linux libc")
        renameat2.argtypes = (
            ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
            ctypes.c_char_p, ctypes.c_uint,
        )
        renameat2.restype = ctypes.c_int
        at_fdcwd = -100
        rename_noreplace = 1
        result = renameat2(
            at_fdcwd, os.fsencode(staging),
            at_fdcwd, os.fsencode(destination),
            rename_noreplace,
        )
        if result != 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error), str(destination))
        return
    raise RuntimeError(
        "Atomic no-replace preview publish unsupported on this platform; "
        "existing workspace must never be overwritten"
    )


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
        verified_runtime = SixOrganRuntime.open(state)  # Same original brain, not a new selector.
        if not (state / "brain.sqlite3").is_file() or not (
            state / "pretorius_recurrent.npz"
        ).is_file():
            raise RuntimeError("Incomplete canonical brain or recurrent checkpoint")
        # Original Laboratory domain verifiers use `with sqlite3.Connection`,
        # which commits but does not explicitly close SQLite handles. On
        # Windows, an unreachable reader can still deny the directory rename.
        # Release all temporary genesis/verification objects and collect any
        # connection cycles before the atomic no-replace publication. This
        # never changes the persisted canonical world or neural checkpoint.
        del verified_runtime, brain, world
        gc.collect()
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f"Preview workspace appeared during genesis: {destination}")
        _publish_noreplace(staging, destination)
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
