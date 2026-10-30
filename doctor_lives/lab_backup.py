"""Offline, operator-quiesced backup of the ONE Doctor and original Laboratory.

The Laboratory owns physical facts; BrainStore owns lived experience. This
archive only copies their persisted bytes, including the host action journal.
It never interprets or reconstructs memories. No cloud service is involved.
"""
from __future__ import annotations

from contextlib import ExitStack, closing
from datetime import datetime, timezone
from hashlib import sha256
import gc
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
    with closing(sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)) as db:
        if db.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise RuntimeError("SQLite integrity check failed")


def _copy_sqlite(source: Path, target: Path) -> None:
    with closing(sqlite3.connect(f"file:{source}?mode=ro", uri=True)) as db:
        with closing(sqlite3.connect(target)) as dest:
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




def _verify_original_laboratory(world: Path) -> None:
    """Use the original Laboratory's full world and domain-ledger verifier.

    SpatialHabitat.backup_to verifies the source's spatial chain and every
    installed original domain ledger before copying and verifying the copy.
    Its temporary verification copy is never an authority or a restored world.
    """
    from pretorius_lab.habitat_v2 import SpatialHabitat

    def verify_copy(candidate: Path, destination: Path) -> str | None:
        # The pinned Laboratory's backup_to verifies every installed domain
        # ledger, but some of its "with sqlite3.connect(...)" blocks commit
        # without closing connections. On Windows those handles prevent
        # deleting the private proof copy. Return only the failure text so
        # exception tracebacks cannot retain a connection during cleanup.
        try:
            SpatialHabitat(candidate).backup_to(destination)
        except Exception as exc:
            return f"{type(exc).__name__}: {exc}"
        return None

    try:
        with tempfile.TemporaryDirectory(prefix=".doctor-lab-proof-") as temp:
            # Verify a private copy, never the sealed archive itself.
            candidate = Path(temp) / "candidate-world.sqlite3"
            shutil.copyfile(world, candidate)
            failure = verify_copy(candidate, Path(temp) / "verified-world.sqlite3")
            # This is resource cleanup, not a verification bypass. All
            # original Laboratory checks must have completed successfully.
            gc.collect()
            if failure is not None:
                raise RuntimeError(f"Laboratory verifier rejected world: {failure}")
    except Exception as exc:
        raise RuntimeError(
            "Original Laboratory world/ledger verification failed"
        ) from exc



def _verify_neural_checkpoint(path: Path) -> None:
    """Validate original recurrent checkpoint semantics, not only its digest.

    An archive manifest can be rewritten by its holder. Its SHA-256 proves
    byte consistency, not that the neural payload is loadable. The canonical
    loader validates schema and arrays, then reconstructs the configured
    recurrent substrate. Shape-only validation misses configuration values
    that fail during reconstruction (for example a negative connection degree).
    Run the SAME loader used at cold start before publishing any restored
    brain or Laboratory world. This does not admit experience or alter the
    archived checkpoint.
    """
    from .neural import PretoriusRecurrentSubstrate

    PretoriusRecurrentSubstrate.load(path)


def _validate_authority_binding(brain: Path, world: Path, journal: Path) -> None:
    """Fail closed when lived action evidence or host intents belong elsewhere.

    Per-file digests cannot establish that independently valid SQLite files
    describe the SAME original physical history. This is an archive-only
    cross-check, never an alternative source of memory or world authority.
    """
    _verify_original_laboratory(world)

    from .lab_home_bridge import (
        _ACTION_DOMAINS, _EVENT_PAYLOAD_COLUMNS, _hash,
        DoctorHomeBridge,
    )

    def read_only(path: Path):
        return sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)

    with closing(read_only(brain)) as mind, closing(read_only(world)) as physical, closing(read_only(journal)) as intents:
        world_tables = {
            row[0] for row in physical.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        receipts_by_hash = {}
        receipts_by_id = {}
        for table in sorted(set(_ACTION_DOMAINS.values())):
            if table not in world_tables:
                continue
            column = _EVENT_PAYLOAD_COLUMNS.get(table, "envelope")
            for event_id, raw, event_hash in physical.execute(
                "SELECT event_id," + column + ",event_hash FROM " + table
            ):
                try:
                    payload = json.loads(raw)
                    if _hash(payload) != event_hash:
                        raise ValueError("event digest differs")
                except (TypeError, ValueError) as exc:
                    raise RuntimeError("Laboratory action receipt is not authentic") from exc
                if event_hash in receipts_by_hash or event_id in receipts_by_id:
                    raise RuntimeError("Duplicate Laboratory action receipt identity")
                receipts_by_hash[event_hash] = (table, event_id, payload)
                receipts_by_id[event_id] = (table, event_hash, payload)

        admitted = set()
        for table in ("memories", "events"):
            present = mind.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            ).fetchone()
            if present is None:
                raise RuntimeError("Canonical BrainStore action history is unavailable")
            for (source,) in mind.execute(
                "SELECT source FROM " + table +
                " WHERE source LIKE 'laboratory-home:action:%'"
            ):
                digest = source[len("laboratory-home:action:"):]
                if digest not in receipts_by_hash:
                    raise RuntimeError(
                        "BrainStore lived action belongs to a different Laboratory world"
                    )
                admitted.add(digest)

        if intents.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' "
            "AND name='doctor_action_intents'"
        ).fetchone() is None:
            raise RuntimeError("Host action-intent journal schema is unavailable")
        matched_receipt = False
        for event_id, request_json, status in intents.execute(
            "SELECT event_id,request_json,status FROM doctor_action_intents"
        ):
            try:
                request = json.loads(request_json)
                op, args = request["op"], request["args"]
                if op not in _ACTION_DOMAINS or not isinstance(args, dict):
                    raise ValueError("Invalid action intent")
            except (TypeError, ValueError, KeyError) as exc:
                raise RuntimeError("Malformed host action-intent record") from exc
            receipt = receipts_by_id.get(event_id)
            if receipt is None:
                if status != "pending":
                    raise RuntimeError("Completed host action has no Laboratory receipt")
                continue  # pre-world pending intent is legitimate, not world proof
            table, digest, payload = receipt
            if table != _ACTION_DOMAINS[op]:
                raise RuntimeError("Host action intent belongs to another world domain")
            try:
                DoctorHomeBridge._check_action_proof(op, args, payload)
            except RuntimeError as exc:
                raise RuntimeError("Host action intent does not match world receipt") from exc
            if status == "complete" and digest not in admitted:
                raise RuntimeError("Completed host action lacks canonical lived memory")
            matched_receipt = True

        # A never-used brain/world pair has no persistent mutual binding in
        # this schema. Refuse to certify it as a coherent archival unit.
        if not admitted and not matched_receipt:
            raise RuntimeError(
                "No authenticated brain/world action or world/intent receipt binds authorities"
            )


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
            _validate_authority_binding(
                staging / "brain" / "brain.sqlite3",
                staging / "world.sqlite3",
                staging / "action-intents.sqlite3",
            )
            _verify_neural_checkpoint(staging / "brain" / "pretorius_recurrent.npz")
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
    _validate_authority_binding(
        actual["brain/brain.sqlite3"], actual["world.sqlite3"],
        actual["action-intents.sqlite3"],
    )
    _verify_neural_checkpoint(actual["brain/pretorius_recurrent.npz"])
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
