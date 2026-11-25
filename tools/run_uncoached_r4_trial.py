#!/usr/bin/env python3
"""Uncoached installed-operator R4 trial with independent physical witness.

No goal prompt, scripted action, user conversation, or host-chosen sequence.
The read-only witness is diagnostic. Source audit alone determines R4 credit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import signal
import os
import sqlite3
from pathlib import Path
import subprocess
import sys
import time

# Support both direct script execution and import by the independent tests.
if __package__:
    from .observe_uncoached_r4 import inspect_neural_origins, sample
else:
    from observe_uncoached_r4 import inspect_neural_origins, sample

from doctor_lives.r4_diagnostics import classify, describe_exception

SAMPLE_SECONDS = 15.0
CAPACITY_RECEIPTS = 520
CAPACITY_WATCHDOG_SECONDS = 3600


def _capacity_stop_reason(observation_stop, error):
    if error:
        return "operator_error" if error.startswith("operator_") else "witness_or_operator_error"
    return observation_stop


def _capacity_result(data, *, progress_reached, operator_error):
    """Missing observations are not evidence of psychological incapacity.

    Only the original source audit can award behavioral credit. A timeout
    or missing activity blocks qualification without diagnosing incapacity.
    """
    problems = set(data.get("problems", ()))
    if operator_error or problems - {"three_distinct_uncoached_activities_not_observed"}:
        return "FAIL"
    if not progress_reached or data.get("status") != "PASS":
        return "INCONCLUSIVE"
    return "PASS"



def _stop_with_live_origin_sampling(proc, command, record_origins, *,
                                   timeout_seconds=90):
    """Observe the real child while a graceful stop command is pending.

    A sealed goal may finish after the observation horizon but before the
    Doctor has exited. Sampling cannot block on preview-stop and then call
    the first postmortem database snapshot a live neural-origin witness.
    The observer is read-only, fsynced by its caller, and never drives goals.
    """
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise ValueError("Positive graceful-stop observation timeout required")
    stopper = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    deadline = time.monotonic() + timeout_seconds
    try:
        while True:
            alive = proc.poll() is None
            # Use actual OS process liveness for EVERY origin observation.
            # A late goal appears live only if its source was readable while
            # the original Doctor process was still alive.
            record_origins(alive)
            finished = stopper.poll() is not None
            if finished and (not alive or stopper.returncode != 0):
                break
            if time.monotonic() >= deadline:
                stopper.kill()
                stopper.communicate(timeout=10)
                return 124, "preview-stop observation exceeded deadline"
            time.sleep(0.1)
        _, stderr = stopper.communicate(timeout=10)
        return stopper.returncode, stderr
    finally:
        if stopper.poll() is None:
            stopper.kill()
            stopper.communicate(timeout=10)


def main():
    cancellation = []
    def cancelled(signum, _frame):
        if not cancellation:
            cancellation.append(signum)
    previous = {sig: signal.signal(sig, cancelled) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        return _main(cancellation)
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def _main(cancellation):
    p = argparse.ArgumentParser()
    p.add_argument("--install-root", type=Path, required=True)
    p.add_argument("--seconds", type=int, default=90)
    p.add_argument("--capacity-receipts", type=int, default=None,
                   help="Minimum original-world receipt growth, not elapsed time or autonomy credit")
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    if not 30 <= args.seconds <= 3600:
        p.error("Real observation horizon must be 30..3600 seconds")
    if args.capacity_receipts is not None and args.capacity_receipts < 1:
        p.error("Capacity receipt target must be positive")
    root = args.install_root.resolve(strict=True)
    vpy = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    workspace = root / "workspace"
    doctor_args = [str(vpy), "-m", "doctor_lives.cli"]
    start = doctor_args + [
        "preview-start", "--workspace", str(workspace),
        "--native-affectus-source", str(root / "sources" / "donor-affectus")]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    witness_path = args.report.with_suffix(".witness.jsonl")
    origins_path = args.report.with_suffix(".origins.jsonl")
    stdout_path = args.report.with_suffix(".operator.stdout.txt")
    stderr_path = args.report.with_suffix(".operator.stderr.txt")
    error, final_sample, baseline, proc = None, None, None, None
    last_origins, last_origin_alive, origin_snapshots = None, None, 0
    began = time.monotonic()
    progress_reached = False
    stop_reason = None
    stop_requested_elapsed = None
    errors, diagnostics = [], []

    def note_error(value):
        nonlocal error
        errors.append(value)
        if error is None:
            error = value
    with witness_path.open("w", encoding="utf-8") as witness, \
         origins_path.open("w", encoding="utf-8") as origins_stream, \
         stdout_path.open("w", encoding="utf-8") as operator_stdout, \
         stderr_path.open("w", encoding="utf-8") as operator_stderr:
        def record(alive):
            nonlocal baseline, final_sample
            result = sample(
                workspace, process_alive=alive,
                elapsed_seconds=time.monotonic() - began,
                baseline_world_receipts=baseline,
            )
            # A sample that crossed the actual process exit earns no live credit.
            result["process_alive_at_start"] = alive
            result["process_alive_at_end"] = bool(alive and proc is not None and proc.poll() is None)
            result["process_alive"] = result["process_alive_at_start"] and result["process_alive_at_end"]
            if baseline is None:
                baseline = result["world_receipt_total"]
            witness.write(json.dumps(result, sort_keys=True) + "\n")
            witness.flush()
            os.fsync(witness.fileno())
            final_sample = result

        def record_origins(alive):
            nonlocal last_origins, last_origin_alive, origin_snapshots
            # Independently sample actual canonical rows while the installed
            # Doctor process runs. This is not a fabricated goal or an
            # attestation that a self-consistent DB row came from a neural act.
            current = inspect_neural_origins(workspace)
            alive = bool(alive and proc is not None and proc.poll() is None)
            if current == last_origins and alive == last_origin_alive:
                return
            entry = {
                "schema": "pretorius.r4.external-neural-origin-observation.v1",
                "elapsed_seconds": round(time.monotonic() - began, 3),
                "process_alive": alive,
                "goals": current,
                "source_authentication_performed": False,
                "autonomy_credit": False,
            }
            origins_stream.write(json.dumps(entry, sort_keys=True) + "\n")
            origins_stream.flush()
            os.fsync(origins_stream.fileno())
            last_origins = current
            last_origin_alive = alive
            origin_snapshots += 1

        try:
            record(False)
            record_origins(False)
            # File-backed output cannot block a long-running child on a full
            # PIPE buffer. Logs are preserved even if the child hard exits.
            proc = subprocess.Popen(
                start, stdout=operator_stdout, stderr=operator_stderr, text=True)
            deadline = began + args.seconds
            next_sample = began + SAMPLE_SECONDS
            while True:
                if proc.poll() is not None:
                    note_error("operator_exited_before_uncoached_window")
                    break
                if cancellation:
                    stop_reason = "external_cancellation"
                    note_error("external_cancellation")
                    break
                if time.monotonic() >= deadline:
                    stop_reason = "watchdog"
                    break
                record_origins(proc.poll() is None)
                if proc.poll() is not None:
                    note_error("operator_exited_before_uncoached_window")
                    break
                if time.monotonic() >= next_sample:
                    record(True)
                    if (args.capacity_receipts is not None
                            and final_sample["process_alive"]
                            and final_sample["world_receipt_delta_from_initial"] >= args.capacity_receipts):
                        progress_reached = True
                        stop_reason = "receipt_progress_target"
                        break
                    next_sample = time.monotonic() + SAMPLE_SECONDS
                time.sleep(0.25)
            if proc.poll() is None:
                stop_requested_elapsed = time.monotonic() - began
                stop_code, stop_stderr = _stop_with_live_origin_sampling(
                    proc, doctor_args + ["preview-stop", "--workspace", str(workspace)],
                    record_origins, timeout_seconds=90,
                )
                if stop_code != 0:
                    note_error("operator_did_not_cleanly_stop:" + stop_stderr[-400:])
            elif error is None:
                note_error("operator_exited_before_graceful_stop")
                stop_reason = None
            try:
                proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=30)
                note_error("operator_did_not_terminate")
            if proc.returncode != 0:
                note_error("operator_return_code_" + str(proc.returncode))
        except (OSError, ValueError, RuntimeError, sqlite3.DatabaseError) as exc:
            note_error("independent_witness_or_operator_error:" + type(exc).__name__ + ":" + str(exc))
            diagnostics.append(describe_exception(exc, phase="witness"))
        finally:
            if proc is not None and proc.poll() is None:
                proc.kill()
                proc.wait(timeout=30)
            try:
                record_origins(False)
                record(False)
            except (OSError, ValueError, RuntimeError, sqlite3.DatabaseError) as exc:
                note_error("independent_final_witness_error:" + type(exc).__name__ + ":" + str(exc))
                diagnostics.append(describe_exception(exc, phase="final_witness"))
    # Retain the source audit verbatim, separate from the combined verdict.
    source_report = args.report.with_suffix(".source-audit.json")
    audit_stdout = args.report.with_suffix(".audit.stdout.txt")
    audit_stderr = args.report.with_suffix(".audit.stderr.txt")
    audit_started = time.monotonic()
    audit_returncode = None
    try:
        independent = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("audit_three_uncoached.py")),
             "--workspace", str(workspace), "--report", str(source_report),
             "--origin-witness", str(origins_path)], capture_output=True, timeout=180)
        audit_returncode = independent.returncode
        audit_stdout.write_bytes(independent.stdout)
        audit_stderr.write_bytes(independent.stderr)
        data = json.loads(source_report.read_text(encoding="utf-8"))
        if audit_returncode != 0 and data.get("status") == "PASS":
            note_error("independent_auditor_nonzero_return_code")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        if isinstance(exc, subprocess.TimeoutExpired):
            audit_stdout.write_bytes(exc.stdout or b"")
            audit_stderr.write_bytes(exc.stderr or b"")
        note_error("independent_auditor_execution_error:" + type(exc).__name__ + ":" + str(exc))
        diagnostics.append(describe_exception(exc, phase="auditor"))
        data = {"gate": "R4", "status": "FAIL", "three_distinct_uncoached": False,
                "original_source_world_verified": False, "problems": ["independent_auditor_execution_error"]}
    for line in stderr_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("R4_OPERATOR_EXCEPTION="):
            try:
                diagnostics.append(json.loads(line.split("=", 1)[1]))
            except ValueError:
                note_error("malformed_operator_exception_diagnostic")
    if cancellation and "external_cancellation" not in errors:
        note_error("external_cancellation")
    data["audit_elapsed_seconds"] = time.monotonic() - audit_started
    data["audit_return_code"] = audit_returncode
    data["original_diagnostic_files"] = {
        path.name: {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in (stdout_path, stderr_path, audit_stdout, audit_stderr, source_report)
        if path.is_file()
    }
    data["observation_elapsed_target_seconds"] = args.seconds
    data["operator_run_error"] = error
    data["operator_controlled_goal_prompt"] = False
    data["operator_controlled_action_sequence"] = False
    data["independent_witness"] = {
        "path": witness_path.name,
        "neural_origin_observations_path": origins_path.name,
        "neural_origin_change_snapshots": origin_snapshots,
        "neural_origin_consistency_is_not_causal_proof": True,
        "sample_interval_seconds": SAMPLE_SECONDS,
        "baseline_world_receipts": baseline,
        "last_world_receipt_delta": (
            final_sample["world_receipt_delta_from_initial"] if final_sample else None),
        "last_native_event": (
            final_sample["operator_ledger_diagnostic_only"]["last_native_event"]
            if final_sample else None),
        "last_daily_action": (
            final_sample["operator_ledger_diagnostic_only"]["last_daily_action"]
            if final_sample else None),
        "source_authentication_performed": False, "autonomy_credit": False,
    }
    source_status = data["status"]
    source_problems = list(data.get("problems", ()))
    source_three_distinct = data.get("three_distinct_uncoached", False)
    termination = classify(initiator=stop_reason, requested_elapsed=stop_requested_elapsed,
        watchdog_seconds=args.seconds, progress=progress_reached,
        operator_returncode=proc.returncode if proc else None, errors=errors, diagnostics=diagnostics,
        cancelled_signal=cancellation[0] if cancellation else None,
        audit_status=source_status, audit_problems=source_problems)
    termination["final_observation_elapsed_seconds"] = final_sample["elapsed_seconds"] if final_sample else None
    termination["final_witness_receipt_delta"] = final_sample["world_receipt_delta_from_initial"] if final_sample else None
    termination["final_receipt_count_is_source_audit_verified"] = bool(final_sample and data.get("original_source_world_verified"))
    data["termination"] = termination
    if error:
        data["status"] = "FAIL"
        data["three_distinct_uncoached"] = False
        data.setdefault("problems", []).append(error)
    if args.capacity_receipts is not None:
        data["source_audit_status"] = source_status
        data["source_audit_three_distinct_uncoached"] = source_three_distinct
        data["capacity_observation"] = {
            "minimum_world_receipt_delta": args.capacity_receipts,
            "progress_reached_while_alive": progress_reached,
            "stop_reason": termination["classification"],
            "stop_initiator": termination["stop_initiator"],
            "watchdog_initiated": termination["watchdog_initiated"],
            "watchdog_seconds": args.seconds,
            "receipt_count_is_not_autonomy_credit": True,
            "missing_behavior_is_not_incapacity": True,
        }
        data["status"] = _capacity_result(data, progress_reached=progress_reached,
                                          operator_error=error)
    args.report.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print("R4_UNCOACHED_SOURCE_AUDIT=" + json.dumps(data, sort_keys=True))
    return 0 if audit_returncode == 0 and not error and data["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
