"""Offline, operator-quiesced backup of the ONE Doctor and original Laboratory.

The Laboratory owns physical facts; BrainStore owns lived experience. This
archive only copies their persisted bytes, including the host action journal.
It never interprets or reconstructs memories. No cloud service is involved.
"""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import sqlite3
import tempfile

SCHEMA = "doctor-laboratory-offline-backup.v1"
_REQUIRED = ("brain/brain.sqlite3", "brain/pretorius_recurrent.npz",
             "world.sqlite3", "action-intents.sqlite3")


def _digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _check_db(path: Path) -> None:
    with sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True) as db:
        if db.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise RuntimeError("SQLite integrity check failed")


def _copy_sqlite(source: Path, target: Path) -> None:
    with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as db:
        with sqlite3.connect(target) as dest:
            db.backup(dest)
    _check_db(target)


def _safe_members(root: Path) -> dict[str, Path]:
    members = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise RuntimeError("Backup refuses symlinks in canonical brain state")
        if not path.is_file():
            continue
        if path.name.endswith(("-wal", "-shm", "-journal")):
            continue
        members["brain/" + path.relative_to(root).as_posix()] = path
    return members


def backup(state: Path, world: Path, destination: Path) -> dict:
    """Require quiescent local writers; lock all three SQLite authorities.

    Lock order matches the host action bridge (intent -> world -> brain).
    Non-SQLite checkpoint/evidence writers must be stopped by the operator.
    """
    state, world, destination = Path(state).resolve(), Path(world).resolve(), Path(destination).resolve()
    journal = Path(str(world) + ".doctor-action-intents.sqlite3")
    if destination.exists():
        raise FileExistsError("Backup destination already exists")
    if destination == state or state in destination.parents:
        raise ValueError("Backup cannot be placed inside canonical brain state")
    members = _safe_members(state)
    members.update({"world.sqlite3": world, "action-intents.sqlite3": journal})
    if any(not members.get(name, Path("/__missing__")).is_file() for name in _REQUIRED):
        raise FileNotFoundError("Existing world, BrainStore, neural checkpoint and host action journal required")
    for name, path in members.items():
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("Backup member is not a regular file")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".doctor-backup-", dir=destination.parent))
    try:
        with ExitStack() as locks:
            for source in (journal, world, state / "brain.sqlite3"):
                conn = sqlite3.connect(source, timeout=5, isolation_level=None)
                locks.callback(conn.close)
                conn.execute("PRAGMA busy_timeout=5000")
                conn.execute("BEGIN IMMEDIATE")
                locks.callback(lambda c=conn: c.execute("ROLLBACK") if c.in_transaction else None)
            files = {}
            for name, source in sorted(members.items()):
                target = staging.joinpath(*PurePosixPath(name).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                if source.suffix == ".sqlite3":
                    _copy_sqlite(source, target)
                else:
                    before = (source.stat().st_size, source.stat().st_mtime_ns)
                    shutil.copyfile(source, target)
                    after = (source.stat().st_size, source.stat().st_mtime_ns)
                    if before != after:
                        raise RuntimeError("Non-SQLite state changed during backup")
                files[name] = {"sha256": _digest(target), "bytes": target.stat().st_size}
        manifest = {"schema": SCHEMA,
                    "created_utc": datetime.now(timezone.utc).isoformat(),
                    "files": files,
                    "quiescence": "operator-stopped external non-SQLite writers"}
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        staging.rename(destination)
        return {"schema": SCHEMA, "files": len(files), "status": "backed_up"}
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def restore(archive: Path, state: Path, world: Path) -> dict:
    """Validate the entire archive before creating either original authority."""
    archive, state, world = Path(archive).resolve(), Path(state).resolve(), Path(world).resolve()
    journal = Path(str(world) + ".doctor-action-intents.sqlite3")
    if state.exists() or world.exists() or journal.exists():
        raise FileExistsError("Restore requires absent brain, world and action journal")
    manifest = json.loads((archive / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA or not isinstance(manifest.get("files"), dict):
        raise RuntimeError("Unsupported or malformed backup manifest")
    files = manifest["files"]
    if not set(_REQUIRED).issubset(files):
        raise RuntimeError("Incomplete canonical brain/world/action journal backup")
    actual = {}
    for path in archive.rglob("*"):
        if path.is_symlink():
            raise RuntimeError("Backup archive contains a symlink")
        if path.is_file() and path != archive / "manifest.json":
            actual[path.relative_to(archive).as_posix()] = path
    if set(actual) != set(files):
        raise RuntimeError("Backup archive has missing or unexpected members: "
                           + repr({"missing": sorted(set(files) - set(actual)),
                                   "unexpected": sorted(set(actual) - set(files))}))
    for name, info in files.items():
        parts = PurePosixPath(name).parts
        if not parts or any(p in (".", "..") for p in parts) or parts[0] not in ("brain", "world.sqlite3", "action-intents.sqlite3"):
            raise RuntimeError("Unsafe backup member path")
        if parts[0] != "brain" and len(parts) != 1:
            raise RuntimeError("Unsafe Laboratory member path")
        source = actual[name]
        if not isinstance(info, dict) or info.get("bytes") != source.stat().st_size or info.get("sha256") != _digest(source):
            raise RuntimeError("Backup member digest mismatch")
        if source.suffix == ".sqlite3":
            _check_db(source)
    try:
        state.mkdir(parents=True)
        for name, source in sorted(actual.items()):
            if name.startswith("brain/"):
                target = state.joinpath(*PurePosixPath(name).parts[1:])
            elif name == "world.sqlite3":
                target = world
            else:
                target = journal
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        return {"schema": SCHEMA, "files": len(files), "status": "restored"}
    except BaseException:
        if state.exists():
            shutil.rmtree(state)
        for path in (world, journal):
            if path.exists():
                path.unlink()
        raise
