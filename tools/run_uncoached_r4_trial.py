#!/usr/bin/env python3
"""Uncoached R4 observation using only the installed public preview operator.

There are no scripted actions, no user messages, no model prompt, no test
injection of choices, no goal request, and no automatic reply.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--install-root", type=Path, required=True)
    p.add_argument("--seconds", type=int, default=90)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    if not 30 <= args.seconds <= 3600:
        p.error("Real observation horizon must be 30..3600 seconds")
    root = args.install_root.resolve(strict=True)
    vpy = root / ".venv" / (
        "Scripts/python.exe" if os.name == "nt" else "bin/python")
    workspace = root / "workspace"
    doctor_args = [str(vpy), "-m", "doctor_lives.cli"]
    start = doctor_args + [
        "preview-start", "--workspace", str(workspace),
        "--native-affectus-source", str(root / "sources" / "donor-affectus")]
    proc = subprocess.Popen(start, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    experiment_error = None
    try:
        deadline = time.monotonic() + args.seconds
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                experiment_error = "operator_exited_before_uncoached_window"
                break
            time.sleep(0.25)
        if proc.poll() is None:
            stop = subprocess.run(
                doctor_args + ["preview-stop", "--workspace", str(workspace)],
                capture_output=True, text=True, timeout=90,
            )
            if stop.returncode != 0:
                experiment_error = "operator_did_not_cleanly_stop:" + stop.stderr
        try:
            output, errors = proc.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            proc.kill()
            output, errors = proc.communicate()
            experiment_error = "operator_did_not_terminate"
        if proc.returncode != 0:
            experiment_error = "operator_return_code_" + str(proc.returncode) + ": " + errors[-600:]
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.communicate()
    # Separate process and standard-library-only reader, with no library
    # imports from the subject, world simulator, or preview ledger.
    independent = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("audit_three_uncoached.py")),
         "--workspace", str(workspace), "--report", str(args.report)],
        capture_output=True, text=True, timeout=60,
    )
    data = json.loads(args.report.read_text(encoding="utf-8"))
    data["observation_elapsed_target_seconds"] = args.seconds
    data["operator_run_error"] = experiment_error
    data["operator_controlled_goal_prompt"] = False
    data["operator_controlled_action_sequence"] = False
    if experiment_error:
        data["status"] = "FAIL"
        data["three_distinct_uncoached"] = False
        data.setdefault("problems", []).append(experiment_error)
    args.report.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print("R4_UNCOACHED_SOURCE_AUDIT=" + json.dumps(data, sort_keys=True))
    return 0 if independent.returncode == 0 and not experiment_error else 1


if __name__ == "__main__":
    raise SystemExit(main())
