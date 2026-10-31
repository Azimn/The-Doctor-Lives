"""Append-only operator evidence. Never a source of lived Doctor memory.

The chain detects accidental edits. Only original Laboratory/Noesis checks can
authenticate physical actions, and independent QA must still inspect sources.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

from .engineer_time import engineer_time

_ZERO = "0" * 64
_SCHEMA = "doctor-laboratory-preview-activity.v1"


def _hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _path(workspace: Path) -> Path:
    workspace = Path(workspace).resolve(strict=True)
    target = workspace / "preview-activity.jsonl"
    if target.is_symlink():
        raise ValueError("Symlinked operator ledger forbidden")
    if target.exists():
        stat = target.stat()
        if not target.is_file() or stat.st_nlink != 1:
            raise ValueError("Operator evidence must be a single regular file")
        for authority in (
            workspace / "laboratory.sqlite3",
            workspace / "state" / "brain.sqlite3",
            workspace / "state" / "pretorius_recurrent.npz",
        ):
            if authority.exists() and os.path.samefile(target, authority):
                raise ValueError("Operator evidence aliases canonical authority")
    return target


def read_activity_ledger(workspace: Path) -> list[dict]:
    path = _path(workspace)
    if not path.exists():
        return []
    previous = _ZERO
    entries = []
    with path.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            try:
                event = json.loads(line)
                if (type(event) is not dict or event.get("schema") != _SCHEMA
                        or event.get("sequence") != number
                        or event.get("previous_sha256") != previous
                        or event.get("sha256") != _hash({
                            k: v for k, v in event.items() if k != "sha256"
                        })):
                    raise ValueError("Ledger sequence or digest mismatch")
                if (type(event.get("external_input")) is not bool
                        or not re.fullmatch(r"@[0-9]{3}", event.get("beat", ""))):
                    raise ValueError("Malformed ledger source fields")
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"Invalid or torn operator ledger line {number}") from exc
            entries.append(event)
            previous = event["sha256"]
    return entries


def append_activity(workspace: Path, *, event: str, external_input: bool,
                    fields: dict | None = None) -> dict:
    """Durably append one engineering record under the sole operator lease."""
    if not event or not isinstance(external_input, bool):
        raise ValueError("Operator event and external input flag required")
    path = _path(workspace)
    prior = read_activity_ledger(workspace)
    clock = engineer_time()
    git_sha = os.environ.get("GITHUB_SHA") or os.environ.get("PRETORIUS_GIT_SHA")
    if not (git_sha and re.fullmatch("[0-9a-f]{40}", git_sha)):
        git_sha = None
    runtime_file = Path(__file__).with_name("lab_runtime.py")
    record = {
        "schema": _SCHEMA,
        "sequence": len(prior) + 1,
        "previous_sha256": prior[-1]["sha256"] if prior else _ZERO,
        "utc": clock.utc_iso,
        "beat": clock.beat,
        "event": event,
        "external_input": external_input,
        "operator_declared_git_sha_unattested": git_sha,
        "operator_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runtime_code_sha256": hashlib.sha256(runtime_file.read_bytes()).hexdigest(),
        "source_attestation_independent": False,
        "fields": fields or {},
    }
    record["sha256"] = _hash(record)
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "a", encoding="utf-8") as output:
            output.write(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n")
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        raise
    return record
