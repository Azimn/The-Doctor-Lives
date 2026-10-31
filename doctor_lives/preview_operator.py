"""Foreground, offline operator lifecycle for the ONE canonical Laboratory.

Operator control is not Pretorius initiative. This module never authors a
physical action, moves the body, chooses a goal, or stores lived memory.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import time

from .lab_preview import initialize_preview
from .lab_runtime import _exclusive_lock, run_laboratory
from .preview_ledger import append_activity, read_activity_ledger
from .preview_native import configured_source, native_step, select_native, verify_donors


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _workspace(path: Path, *, create: bool = False) -> Path:
    target = Path(path).expanduser().absolute()
    if target.is_symlink():
        raise ValueError("Symlinked preview workspace forbidden")
    if not target.exists() and create:
        initialize_preview(target)
    if not target.is_dir():
        raise FileNotFoundError("Existing preview workspace required")
    if not (target / "state" / "brain.sqlite3").is_file() or not (
        target / "state" / "pretorius_recurrent.npz"
    ).is_file() or not (target / "laboratory.sqlite3").is_file():
        raise FileNotFoundError("Incomplete canonical Doctor and Laboratory workspace")
    return target


def _status_path(workspace: Path) -> Path:
    return workspace / "preview-status.json"


def _read_status(workspace: Path) -> dict | None:
    path = _status_path(workspace)
    if path.is_symlink():
        raise ValueError("Symlinked operator status forbidden")
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "doctor-laboratory-preview-operator.v1":
        raise ValueError("Unrecognized preview status")
    return value


def _write_status(workspace: Path, value: dict) -> None:
    destination = _status_path(workspace)
    if destination.is_symlink():
        raise ValueError("Symlinked operator status forbidden")
    fd, name = tempfile.mkstemp(prefix=".preview-status-", dir=workspace)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(value, file, sort_keys=True)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(name, destination)
    finally:
        Path(name).unlink(missing_ok=True)


def _response(value: dict) -> None:
    print(json.dumps(value, sort_keys=True), flush=True)


def status(workspace: Path) -> int:
    workspace = _workspace(workspace)
    report = _read_status(workspace)
    if report is None:
        _response({"status": "not_started", "workspace": str(workspace)})
        return 3
    current = dict(report)
    if report["status"] == "running":
        heartbeat = datetime.fromisoformat(report["last_heartbeat"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - heartbeat).total_seconds()
        if age > 30.0:
            current["status"] = "unresponsive"
            current["heartbeat_age_seconds"] = round(age, 3)
    started = datetime.fromisoformat(report["started_at"].replace("Z", "+00:00"))
    current["uptime_seconds"] = round(max(0.0, (datetime.now(timezone.utc) - started).total_seconds()), 3)
    _response(current)
    return 0 if current["status"] in ("running", "stopped") else 3


def stop(workspace: Path) -> int:
    workspace = _workspace(workspace)
    report = _read_status(workspace)
    if report is None or report.get("status") != "running":
        _response({"status": "not_running"})
        return 3
    request = workspace / ".preview-stop-request"
    if request.is_symlink():
        raise ValueError("Symlinked stop request forbidden")
    try:
        with request.open("x", encoding="utf-8") as stream:
            stream.write(_utc() + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        _response({"status": "stop_already_requested"})
        return 3
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        current = _read_status(workspace)
        if current and current.get("status") == "stopped":
            _response({"status": "stopped", "workspace": str(workspace)})
            return 0
        time.sleep(0.2)
    _response({"status": "stop_unconfirmed", "workspace": str(workspace)})
    return 4


def run(workspace: Path, *, resume: bool = False, native_source: Path | None = None) -> int:
    if native_source is not None:
        if resume:
            raise ValueError("Resume cannot change native donor selection")
        verify_donors(native_source)  # fail BEFORE creating a new workspace
    workspace = _workspace(workspace, create=not resume)
    # This lease lasts across all cognitive runs. A second operator process
    # cannot compete with the same brain/world even between scheduled pulses.
    with _exclusive_lock(workspace / ".preview-operator.lock", "Preview operator"):
        request = workspace / ".preview-stop-request"
        if request.exists() or request.is_symlink():
            raise RuntimeError("Outstanding stop request: refuse ambiguous restart")
        if native_source is not None:
            if select_native(workspace, native_source):
                append_activity(workspace, event="operator_native_mode_selected",
                                external_input=True,
                                fields={"source_pinned": True, "operator_supplied_goal": None})
        effective_native = configured_source(workspace)
        started = _utc()
        previous = _read_status(workspace)
        if resume and previous is None:
            raise RuntimeError("No previous operator session to resume")
        run_index = 1 if previous is None else int(previous.get("run_index", 0)) + 1
        report = {
            "schema": "doctor-laboratory-preview-operator.v1",
            "status": "running", "workspace": str(workspace),
            "pid": os.getpid(), "run_index": run_index,
            "started_at": started, "last_heartbeat": started,
            "current_activity": ("native_laboratory_goal_opportunity" if effective_native is not None else "original_laboratory_observation"),
            "last_action": None if previous is None else previous.get("last_action"),
            "last_action_origin": None if previous is None else previous.get("last_action_origin"),
            "operator_initiated": True, "uncoached_three_task_life_proven": False,
        }
        # A previous foreground process may have been killed without a final
        # record. Mark that gap rather than invent a successful continuation.
        old = read_activity_ledger(workspace)
        if old and old[-1]["event"] not in ("operator_stop",):
            append_activity(workspace, event="unexpected_termination", external_input=False,
                            fields={"previous_sequence": old[-1]["sequence"],
                                    "unfinished_doctor_goal_resumed": False})
        append_activity(workspace, event="operator_resume" if resume else "operator_start",
                        external_input=True,
                        fields={"run_index": run_index, "operator_supplied_goal": None})
        append_activity(workspace, event=(
                            "native_goal_opportunity_started" if effective_native is not None
                            else "host_observation_started"),
                        external_input=False,
                        fields={"chosen_by": "host_scheduler",
                                "operator_supplied_goal": None,
                                "uncoached_three_task_life_proven": False})
        _write_status(workspace, report)
        _response({"status": "running", "workspace": str(workspace), "pid": os.getpid()})
        # A laboratory observation is a host opportunity, NOT a self-chosen
        # Doctor goal. Only Noesis may select a physically feasible bench action.
        try:
            while not request.exists():
                if effective_native is not None:
                    activity = native_step(
                        workspace / "state", workspace / "laboratory.sqlite3",
                        effective_native)
                    append_activity(workspace, event="native_goal_" + activity["status"],
                                    external_input=False,
                                    fields={**activity, "host_offered_opportunity": True})
                    report["current_activity"] = (
                        activity["kind"] + ":" + activity["goal_id"]
                        if activity["kind"] and activity["goal_id"]
                        else "native_laboratory_goal_opportunity")
                    if activity["status"] in ("moved", "opened", "completed"):
                        report["last_action"] = activity["status"]
                        report["last_action_origin"] = "original_neural_tendency_host_mapped"
                    # A bounded pacing interval lets the operator observe,
                    # interrupt, and reconcile between actual physical steps.
                    report["last_heartbeat"] = _utc()
                    _write_status(workspace, report)
                    time.sleep(0.5)
                    continue
                result = run_laboratory(
                    workspace / "state", workspace / "laboratory.sqlite3",
                    duration_seconds=1.0, interval_seconds=0.25,
                    work_interval_seconds=0.5,
                    activity_sink=lambda item: append_activity(
                        workspace, event="noesis_work_" + item["phase"],
                        external_input=False,
                        fields={**item, "host_offered_opportunity": True}),
                )
                if result["work_events"]:
                    action = result["work_events"][-1]
                    if action.get("selection") != "original_noesis":
                        raise PermissionError("Work not selected by original Noesis")
                    report["last_action"] = action["action"]
                    report["last_action_origin"] = "original_noesis_host_offered"
                report["last_heartbeat"] = _utc()
                _write_status(workspace, report)
        finally:
            if request.exists() and not request.is_symlink():
                request.unlink()
                append_activity(workspace, event="host_observation_interrupted",
                                external_input=False,
                                fields={"reason": "operator_request",
                                        "unfinished_doctor_goal_resumed": False})
                append_activity(workspace, event="operator_stop",
                                external_input=True,
                                fields={"request_received": True})
                report["status"] = "stopped"
                report["current_activity"] = "interrupted_by_operator"
                report["last_heartbeat"] = _utc()
                _write_status(workspace, report)
        _response({"status": "stopped", "workspace": str(workspace)})
        return 0


def command(kind: str, workspace: Path, native_source: Path | None = None) -> int:
    try:
        if kind == "preview-status":
            return status(workspace)
        if kind == "preview-stop":
            return stop(workspace)
        if kind in ("preview-start", "preview-resume"):
            return run(workspace, resume=(kind == "preview-resume"), native_source=native_source)
        raise ValueError("Unknown preview command")
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"{kind}: {exc}", file=sys.stderr)
        return 2
