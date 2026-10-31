"""Read-only, standard-library-only witness for uncoached original-world R4.

Diagnostic counts are NOT original-world provenance, goal completion, or
independent R4 acceptance. The separate source auditor owns those decisions.
"""
from __future__ import annotations

from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

WORLD_TABLES = ("books_events", "rhythm_events", "embodied_events")


def _read_db(path: Path):
    if not path.is_file():
        raise FileNotFoundError("Independent witness source missing: " + path.name)
    return sqlite3.connect(path.absolute().as_uri() + "?mode=ro", uri=True)


def sample(workspace: Path, *, process_alive: bool, elapsed_seconds: float,
           baseline_world_receipts: int | None = None) -> dict:
    if type(process_alive) is not bool or elapsed_seconds < 0:
        raise ValueError("Invalid independent process sample")
    workspace = Path(workspace)
    world = {}
    with closing(_read_db(workspace / "laboratory.sqlite3")) as db:
        for table in WORLD_TABLES:
            if db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone() is None:
                raise RuntimeError("Missing authoritative world table: " + table)
            rows = db.execute(
                "SELECT event_id,event_hash FROM " + table + " ORDER BY event_id"
            ).fetchall()
            if any(type(a) is not str or type(b) is not str for a, b in rows):
                raise RuntimeError("Malformed original-world receipt identity")
            world[table] = {
                "count": len(rows),
                "identity_digest": hashlib.sha256(json.dumps(
                    rows, separators=(",", ":")
                ).encode("utf-8")).hexdigest(),
            }
    with closing(_read_db(workspace / "state" / "brain.sqlite3")) as db:
        policies = {
            str(trigger) + ":" + str(action): count
            for trigger, action, count in db.execute(
                "SELECT trigger,selected_action,COUNT(*) FROM policy_decisions "
                "GROUP BY trigger,selected_action"
            )
        }
        memories = db.execute(
            "SELECT COUNT(*) FROM memories WHERE evidence_class='lived_runtime_memory' "
            "AND external=0 AND source LIKE 'laboratory-home:action:%'"
        ).fetchone()[0]
    counts = Counter()
    last_native = None
    last_daily = None
    log = workspace / "preview-activity.jsonl"
    if log.is_file():
        for raw in log.read_text(encoding="utf-8").splitlines():
            event = json.loads(raw)
            name = event["event"]
            counts[name] += 1
            fields = event.get("fields", {})
            if name.startswith("native_goal_"):
                last_native = {
                    "event": name, "kind": fields.get("kind"),
                    "goal_phase": fields.get("goal_phase"),
                    "selected_tendency": fields.get(
                        "original_tendency", fields.get("selected_tendency")),
                    "source_receipt_present": bool(fields.get("world_receipt_sha256")),
                }
            if name == "candidate_b_daily_life_pulse":
                last_daily = {
                    "selected_action": fields.get("source_selected_action"),
                    "world_effect_present": fields.get("physical_receipt") is not None,
                    "policy_present": fields.get("origin_policy_id") is not None,
                }
    total = sum(value["count"] for value in world.values())
    delta = None if baseline_world_receipts is None else total - baseline_world_receipts
    if delta is not None and delta < 0:
        raise RuntimeError("Original-world receipt count regressed")
    status_file = workspace / "preview-status.json"
    host_status, age = "not_started", None
    if status_file.is_file():
        status = json.loads(status_file.read_text(encoding="utf-8"))
        if status.get("schema") != "doctor-laboratory-preview-operator.v1":
            raise RuntimeError("Unrecognized operator status source")
        host_status = status.get("status", "unknown")
        heartbeat = datetime.fromisoformat(
            status["last_heartbeat"].replace("Z", "+00:00"))
        age = max(0.0, (datetime.now(timezone.utc) - heartbeat).total_seconds())
    if not process_alive and host_status not in ("stopped", "not_started"):
        classification = "crash"
    elif age is None:
        classification = "startup" if elapsed_seconds < 90 else "stall"
    elif age > 90 and elapsed_seconds >= 90:
        classification = "stall"
    elif delta == 0 and elapsed_seconds >= 600:
        classification = "silent_skip_candidate"
    else:
        classification = "active_or_initializing"
    return {
        "schema": "pretorius.r4.independent-physical-witness.v1",
        "sample_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed_seconds, 3),
        "process_alive": process_alive, "operator_status": host_status,
        "heartbeat_age_seconds": None if age is None else round(age, 3),
        "failure_class_candidate": classification,
        "world_receipts": world, "world_receipt_total": total,
        "world_receipt_delta_from_initial": delta,
        "brain": {"policy_counts": policies, "unverified_lived_action_rows": memories},
        "operator_ledger_diagnostic_only": {
            "entries": sum(counts.values()),
            "event_counts": dict(sorted(counts.items())),
            "last_native_event": last_native, "last_daily_action": last_daily,
        },
        "source_authentication_performed": False, "autonomy_credit": False,
    }
