#!/usr/bin/env python3
"""Uncoached installed-operator R4 trial with independent physical witness.

No goal prompt, scripted action, user conversation, or host-chosen sequence.
The read-only witness is diagnostic. Source audit alone determines R4 credit.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from observe_uncoached_r4 import sample

SAMPLE_SECONDS = 15.0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--install-root", type=Path, required=True)
    p.add_argument("--seconds", type=int, default=90)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    if not 30 <= args.seconds <= 3600:
        p.error("Real observation horizon must be 30..3600 seconds")
    root = args.install_root.resolve(strict=True)
    vpy = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    workspace = root / "workspace"
    doctor_args = [str(vpy), "-m", "doctor_lives.cli"]
    start = doctor_args + [
        "preview-start", "--workspace", str(workspace),
        "--native-affectus-source", str(root / "sources" / "donor-affectus")]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    witness_path = args.report.with_suffix(".witness.jsonl")
    stdout_path = args.report.with_suffix(".operator.stdout.txt")
    stderr_path = args.report.with_suffix(".operator.stderr.txt")
    error, final_sample, baseline, proc = None, None, None, None
    began = time.monotonic()
    with witness_path.open("w", encoding="utf-8") as witness, \
         stdout_path.open("w", encoding="utf-8") as operator_stdout, \
         stderr_path.open("w", encoding="utf-8") as operator_stderr:
        def record(alive):
            nonlocal baseline, final_sample
            result = sample(
                workspace, process_alive=alive,
                elapsed_seconds=time.monotonic() - began,
                baseline_world_receipts=baseline,
            )
            if baseline is None:
                baseline = result["world_receipt_total"]
            witness.write(json.dumps(result, sort_keys=True) + "\n")
            witness.flush()
            os.fsync(witness.fileno())
            final_sample = result

        try:
            record(False)
            # File-backed output cannot block a long-running child on a full
            # PIPE buffer. Logs are preserved even if the child hard exits.
            proc = subprocess.Popen(
                start, stdout=operator_stdout, stderr=operator_stderr, text=True)
            deadline = began + args.seconds
            next_sample = began + SAMPLE_SECONDS
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    error = "operator_exited_before_uncoached_window"
                    break
                if time.monotonic() >= next_sample:
                    record(True)
                    next_sample = time.monotonic() + SAMPLE_SECONDS
                time.sleep(0.25)
            if proc.poll() is None:
                stop = subprocess.run(
                    doctor_args + ["preview-stop", "--workspace", str(workspace)],
                    capture_output=True, text=True, timeout=90)
                if stop.returncode != 0:
                    error = "operator_did_not_cleanly_stop:" + stop.stderr[-400:]
            try:
                proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=30)
                error = "operator_did_not_terminate"
            if proc.returncode != 0:
                error = "operator_return_code_" + str(proc.returncode)
        except (OSError, ValueError, RuntimeError) as exc:
            error = "independent_witness_or_operator_error:" + type(exc).__name__ + ":" + str(exc)[:300]
        finally:
            if proc is not None and proc.poll() is None:
                proc.kill()
                proc.wait(timeout=30)
            try:
                record(False)
            except (OSError, ValueError, RuntimeError) as exc:
                error = "independent_final_witness_error:" + type(exc).__name__ + ":" + str(exc)[:300]
    independent = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("audit_three_uncoached.py")),
         "--workspace", str(workspace), "--report", str(args.report)],
        capture_output=True, text=True, timeout=60)
    data = json.loads(args.report.read_text(encoding="utf-8"))
    data["observation_elapsed_target_seconds"] = args.seconds
    data["operator_run_error"] = error
    data["operator_controlled_goal_prompt"] = False
    data["operator_controlled_action_sequence"] = False
    data["independent_witness"] = {
        "path": witness_path.name,
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
    if error:
        data["status"] = "FAIL"
        data["three_distinct_uncoached"] = False
        data.setdefault("problems", []).append(error)
    args.report.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print("R4_UNCOACHED_SOURCE_AUDIT=" + json.dumps(data, sort_keys=True))
    return 0 if independent.returncode == 0 and not error else 1


if __name__ == "__main__":
    raise SystemExit(main())
