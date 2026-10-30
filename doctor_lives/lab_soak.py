"""Offline, operator-visible elapsed-time soak using the ONE shipping host.

This is an engineering evidence log, never a second brain, memory, planner,
world ledger or subject renderer. A log by itself is not independent attestation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
import re
from pathlib import Path
import threading
import time

from .lab_runtime import _exclusive_host, _exclusive_lock, _run_laboratory_session

SCHEMA = "doctor-laboratory-soak-segment.v1"
LAB_SOURCE_PIN = "6e49795752835d64fa6fd63d16359669a1ca2ba7"
MAX_GAP_SECONDS = 60.0
QUALIFY_SECONDS = 86400.0


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("Soak timestamps must be UTC ISO-8601")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _stable(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: dict) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def read_soak_log(path: Path) -> dict:
    """Validate every record, monotone elapsed intervals and chain continuity.

    The hash chain detects accidental edits and torn records. It is not a
    signature and cannot defend against a privileged writer rehashing a log.
    """
    path = Path(path)
    if path.is_symlink():
        raise RuntimeError("Symlinked soak evidence is forbidden")
    entries = []
    previous = "0" * 64
    epoch = None
    last_end = None
    gaps = []
    ids = set()
    with path.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            try:
                record = json.loads(line)
                digest = record.pop("sha256")
                if (record["schema"] != SCHEMA or record["previous_sha256"] != previous
                        or _digest(record) != digest
                        or record["sequence"] != number
                        or record["lab_source_pin_expected"] != LAB_SOURCE_PIN
                        or record["status"] not in ("completed", "interrupted")
                        or not isinstance(record.get("beat"), str)
                        or re.fullmatch(r"@[0-9]{3}", record["beat"]) is None):
                    raise ValueError("Soak record chain or schema mismatch")
                start, end = _timestamp(record["started_utc"]), _timestamp(record["ended_utc"])
                wall = (end - start).total_seconds()
                active = record["active_seconds"]
                if (type(active) not in (int, float) or not math.isfinite(active)
                        or active < 0 or wall < 0 or active > wall + 2.0
                        or type(record["world_epoch"]) is not str
                        or not record["world_epoch"]):
                    raise ValueError("Impossible real-elapsed soak evidence")
                if epoch is None:
                    epoch = record["world_epoch"]
                if record["world_epoch"] != epoch:
                    raise ValueError("Authoritative Laboratory epoch changed")
                if last_end is not None:
                    gap = (start - last_end).total_seconds()
                    if gap < -1.0:
                        raise ValueError("Overlapping or reversed soak intervals")
                    gaps.append(max(0.0, gap))
                last_end = end
                work_ids = record["work_event_ids"]
                if (type(work_ids) is not list or any(type(x) is not str for x in work_ids)
                        or len(set(work_ids)) != len(work_ids)
                        or ids.intersection(work_ids)):
                    raise ValueError("Duplicate physical work identity in soak")
                ids.update(work_ids)
                record["sha256"] = digest
                entries.append(record)
                previous = digest
            except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"Invalid or torn soak record {number}") from exc
    active_total = round(sum(x["active_seconds"] for x in entries), 3)
    span = ((_timestamp(entries[-1]["ended_utc"]) -
             _timestamp(entries[0]["started_utc"])).total_seconds() if entries else 0.0)
    continuous = bool(entries and all(x["status"] == "completed" for x in entries)
                      and all(g <= MAX_GAP_SECONDS for g in gaps))
    return {
        "schema": "doctor-laboratory-soak-evidence.v1",
        "segments": len(entries),
        "active_seconds": active_total,
        "wall_span_seconds": round(span, 3),
        "largest_gap_seconds": round(max(gaps, default=0.0), 3),
        "continuous": continuous,
        "qualified_24h_candidate": bool(continuous and active_total >= QUALIFY_SECONDS
                                         and span >= QUALIFY_SECONDS),
        "world_epoch": epoch,
        "last_sha256": previous,
        "work_event_ids": len(ids),
        "source_lab_pin_expected": LAB_SOURCE_PIN,
        "independent_source_attestation": False,
    }


def _validate_evidence_location(state: Path, world: Path, evidence: Path) -> None:
    """Deny engineering evidence and its lock from aliasing real authorities.

    SQLite owns its WAL, shared-memory, rollback and master-journal siblings.
    The original Laboratory owns the persistent world host-lock sidecar.
    Reject reserved names even before they exist, and reject existing hardlinks
    by file identity. Symlinks are denied separately, including parent aliases.
    """
    canonical_state = state.resolve()
    canonical_world = world.resolve()
    if evidence.is_symlink():
        raise ValueError("Symlinked soak evidence is forbidden")
    evidence_lock = evidence.with_name(evidence.name + ".lock")
    if evidence_lock.is_symlink():
        raise ValueError("Symlinked soak evidence lock is forbidden")

    stem = canonical_world.name
    reserved_names = {
        stem, stem + "-wal", stem + "-shm", stem + "-journal",
        stem + "-stmtjrnl", stem + "-super-journal",
        stem + ".laboratory-host.lock",
    }
    reserved_paths = [canonical_world.with_name(name) for name in reserved_names]
    # Existing hardlinks can put a canonical brain file outside its state
    # directory, just as they can alias a world SQLite sidecar.
    reserved_paths.extend(
        canonical_state / name for name in (
            "brain.sqlite3", "brain.sqlite3-wal", "brain.sqlite3-shm",
            "brain.sqlite3-journal", "pretorius_recurrent.npz",
            ".laboratory-host.lock",
        )
    )
    reserved_names_folded = {name.casefold() for name in reserved_names}
    reserved_identity = {
        (item.stat().st_dev, item.stat().st_ino)
        for item in reserved_paths if item.exists()
    }
    for candidate in (evidence, evidence_lock):
        resolved = candidate.resolve()
        if resolved == canonical_state or canonical_state in resolved.parents:
            raise ValueError("Engineering soak evidence must be outside the canonical brain")
        if (resolved.parent == canonical_world.parent
                and (resolved.name.casefold() in reserved_names_folded
                     or resolved.name.casefold().startswith(
                         stem.casefold() + "-mj"
                     ))):
            raise ValueError("Engineering soak evidence collides with a Laboratory sidecar")
        if candidate.exists():
            stat = candidate.stat()
            if (stat.st_dev, stat.st_ino) in reserved_identity:
                raise ValueError("Engineering soak evidence hardlinks a Laboratory authority")


def soak_laboratory(
    state: Path, world: Path, evidence: Path, *, target_seconds: float,
    segment_seconds: float = 900.0, interval_seconds: float = 30.0,
    work_interval_seconds: float | None = None,
    stop: threading.Event | None = None,
) -> dict:
    """Run real elapsed segments under ONE uninterrupted two-authority lease.

    Existing canonical Noesis alone chooses any offered work. A restart
    continues from completed segments, never invents missing elapsed time.
    """
    if not (math.isfinite(target_seconds) and 0.1 <= target_seconds <= 90000):
        raise ValueError("Target must be between 0.1 and 90000 real seconds")
    if not (math.isfinite(segment_seconds) and 0.1 <= segment_seconds <= 3600):
        raise ValueError("Segment must be between 0.1 and 3600 real seconds")
    if not (math.isfinite(interval_seconds) and 0.05 <= interval_seconds
            and interval_seconds <= segment_seconds):
        raise ValueError("Pulse interval exceeds segment")
    if work_interval_seconds is not None and not (
        math.isfinite(work_interval_seconds)
        and 0.05 <= work_interval_seconds <= segment_seconds
    ):
        raise ValueError("Work interval exceeds segment")
    state, world, evidence = Path(state), Path(world), Path(evidence)
    _validate_evidence_location(state, world, evidence)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    stop = stop if stop is not None else threading.Event()
    with _exclusive_lock(evidence.with_name(evidence.name + ".lock"), "Soak evidence"):
        with _exclusive_host(state, world):
            from pretorius_lab.habitat_v2 import SpatialHabitat
            world_epoch = SpatialHabitat(world).verify()["world_epoch"]
            report = read_soak_log(evidence) if evidence.exists() else {
                "segments": 0, "active_seconds": 0.0, "world_epoch": None,
                "last_sha256": "0" * 64,
            }
            if report["world_epoch"] not in (None, world_epoch):
                raise RuntimeError("Soak evidence belongs to another Laboratory epoch")
            if report["segments"] and not report.get("continuous", False):
                raise RuntimeError("Interrupted or discontinuous soak cannot resume as continuous")
            if report["segments"]:
                with evidence.open("r", encoding="utf-8") as stream:
                    last = json.loads(list(stream)[-1])
                gap = (_timestamp(_utc()) - _timestamp(last["ended_utc"])).total_seconds()
                if gap < -1 or gap > MAX_GAP_SECONDS:
                    raise RuntimeError("Real elapsed soak gap exceeds continuity limit")
            while report["active_seconds"] < target_seconds and not stop.is_set():
                remaining = target_seconds - report["active_seconds"]
                duration = min(segment_seconds, max(0.1, remaining))
                # The original host enforces its own 0.1..3600s segment bounds.
                started_utc = _utc()
                result = _run_laboratory_session(
                    state, world, duration_seconds=duration,
                    interval_seconds=min(interval_seconds, duration),
                    work_interval_seconds=(min(work_interval_seconds, duration)
                                           if work_interval_seconds is not None else None),
                    stop=stop,
                )
                ended_utc = _utc()
                record = {
                    "schema": SCHEMA,
                    "sequence": report["segments"] + 1,
                    "previous_sha256": report["last_sha256"],
                    "started_utc": started_utc,
                    "ended_utc": ended_utc,
                    "active_seconds": float(result["elapsed_seconds"]),
                    "status": result["status"],
                    "beat": result["clock"]["beat"],
                    "world_epoch": SpatialHabitat(world).verify()["world_epoch"],
                    "pulses": result["pulses"],
                    "recovered": result["recovered"],
                    "abandoned": result.get("abandoned", 0),
                    "work_event_ids": [x["event_id"] for x in result["work_events"]],
                    "subject_frame_count": len(result["subject_frames"]),
                    "lab_source_pin_expected": LAB_SOURCE_PIN,
                }
                record["sha256"] = _digest(record)
                # Append-only engineering evidence, never first-person memory.
                with evidence.open("a", encoding="utf-8", newline="\n") as stream:
                    stream.write(_stable(record) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                report = read_soak_log(evidence)
                if report["world_epoch"] != world_epoch:
                    raise RuntimeError("Original Laboratory epoch changed during soak")
                if result["status"] != "completed":
                    break
            return {**report, "status": ("interrupted" if stop.is_set()
                                        else "target_reached" if
                                        report["active_seconds"] >= target_seconds
                                        else "incomplete")}
