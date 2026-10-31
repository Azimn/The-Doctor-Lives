"""Source-pinned native-goal operator adapter and read-only QA evidence.

No new planner or cognitive selector. NativeLaboatoryGoalChooser remains the
sole existing experimental goal-routing mechanism. This adapter only checks
installed reviewed donors and reconciles existing world/BrainStore receipts.
"""
from __future__ import annotations

from contextlib import closing
from importlib.metadata import version
import json
from pathlib import Path
import sqlite3

_CONFIG = "preview-native-mode.json"
_SCHEMA = "pretorius.preview.native-operator.v1"
_BOOK_KEY = "six_organ_endogenous_book_goal_v1"
_REST_KEY = "six_organ_native_rest_intention_v1"


def verify_donors(affectus_source: Path) -> Path:
    source = Path(affectus_source).expanduser().resolve(strict=True)
    if not source.is_dir():
        raise ValueError("Pinned Affectus source must be a directory")
    from .canonical_affectus_weather import load_reviewed_weather
    from .sensus_pilot import _load_verified_donor
    load_reviewed_weather(source)  # reviewed Git BLOBs, never substitute Sensus
    _load_verified_donor()         # real detached HEAD and exact source blobs
    import synthetic_ipseity
    if version("synthetic-ipseity") != "0.9.11":
        raise RuntimeError("Reviewed Synthetic Ipseity v0.9.11 required")
    from synthetic_ipseity import DurableIpseityHost, SubjectOnlyRendererPort
    if not DurableIpseityHost or not SubjectOnlyRendererPort:
        raise RuntimeError("Pinned Ipseity subject-only gate is unavailable")
    return source


def _config_path(workspace: Path) -> Path:
    path = workspace / _CONFIG
    if path.is_symlink():
        raise PermissionError("Symlinked native operator configuration forbidden")
    return path


def configured_source(workspace: Path) -> Path | None:
    path = _config_path(workspace)
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError("Invalid native mode file")
    value = json.loads(path.read_text(encoding="utf-8"))
    if (type(value) is not dict
            or set(value) != {"schema", "affectus_source", "operator_selected"}
            or value["schema"] != _SCHEMA
            or value["operator_selected"] is not True
            or not isinstance(value["affectus_source"], str)):
        raise ValueError("Invalid native operator configuration")
    return verify_donors(Path(value["affectus_source"]))


def select_native(workspace: Path, source: Path) -> bool:
    """A one-time explicit operator mode selection, never a Doctor instruction."""
    verified = verify_donors(source)
    existing = configured_source(workspace)
    if existing is not None:
        if existing != verified:
            raise PermissionError("Existing native operator source cannot be replaced")
        return False
    path = _config_path(workspace)
    payload = {"schema": _SCHEMA, "affectus_source": str(verified),
               "operator_selected": True}
    # O_EXCL-like file creation; never replace a mode or source by accident.
    with path.open("x", encoding="utf-8") as out:
        json.dump(payload, out, sort_keys=True)
        out.write("\n")
        out.flush()
        import os
        os.fsync(out.fileno())
    return True


def _intent_source(state: Path, goal_id: str) -> dict:
    """Read real canonical intent origin; never create a policy or goal."""
    from .lab_native_work_goal import WORK_KEY
    with closing(sqlite3.connect(state / "brain.sqlite3")) as db:
        for key, kind in ((_BOOK_KEY, "read_book"), (_REST_KEY, "rest"),
                          (WORK_KEY, "work")):
            row = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
            if not row:
                continue
            entry = json.loads(row[0])["payload"]
            if entry["id"] != goal_id:
                continue
            choice = db.execute(
                "SELECT selected_action FROM policy_decisions WHERE id=?",
                (entry["origin_policy_id"],)
            ).fetchone()
            expected = {"read_book": "explore", "rest": "avoid",
                        "work": "persist"}[kind]
            if not choice or choice[0] != expected:
                raise PermissionError("Native intent has no original Noesis decision")
            return {"origin_policy_id": entry["origin_policy_id"],
                    "original_tendency": choice[0], "goal_kind": kind,
                    "goal_phase": entry["phase"]}
    raise PermissionError("No canonical neural goal origin found")


def _lived_receipt(state: Path, world: Path, memory_id: str) -> dict:
    """Replay authentic world receipt against original lived BrainStore memory."""
    from .organs import SixOrganRuntime
    from .lab_home_bridge import _row
    from pretorius_lab.habitat_v2 import SpatialHabitat
    runtime = SixOrganRuntime.open(state)
    memory = runtime._port.brain.store.get_memory(memory_id)
    if (memory is None or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or not memory["source"].startswith("laboratory-home:action:")):
        raise PermissionError("Native activity lacks canonical lived memory")
    digest = memory["source"].removeprefix("laboratory-home:action:")
    lab = SpatialHabitat(world)
    lab.verify()
    with closing(lab._open()) as db:
        matches = []
        for table in ("embodied_events", "books_events", "rhythm_events"):
            for row in db.execute("SELECT event_id FROM " + table + " WHERE event_hash=?", (digest,)):
                record, checked = _row(db, table, row[0])
                if checked == digest:
                    matches.append((table, row[0], record))
    if len(matches) != 1:
        raise PermissionError("Ambiguous or absent original world event for native activity")
    return {"world_table": matches[0][0],
            "world_event_id": matches[0][1],
            "world_receipt_sha256": digest,
            "canonical_memory_id": memory_id,
            "canonical_memory_source": memory["source"],
            "source_rechecked_by_host": True,
            "independent_attestation": False}


def native_step(state: Path, world: Path, affectus_source: Path) -> dict:
    """One existing Noesis opportunity; no operator-selected goal or action."""
    from .lab_runtime import run_native_laboratory
    result = run_native_laboratory(
        state, world, affectus_source=affectus_source, steps=1,
        allow_world_actions=True, enable_sustained_work=True
    )
    receipt = result["receipts"][-1]
    event = {
        "status": receipt["status"], "goal_id": receipt["goal_id"],
        "kind": receipt["kind"], "selected_tendency": receipt["selected_tendency"],
        "host_selected_goal_mapping": True,
        "host_selected_route": True, "operator_supplied_goal": None,
        "same_original_brain": result["same_original_brain"],
        "original_world_epoch_unchanged": result["original_world_epoch_unchanged"],
        "source_attestation_independent": False,
    }
    if receipt["goal_id"] is not None:
        event.update(_intent_source(state, receipt["goal_id"]))
    if receipt["memory_id"] is not None:
        event.update(_lived_receipt(state, world, receipt["memory_id"]))
    return event
