#!/usr/bin/env python3
"""Independent real-time monitor for installed Candidate B public operator.

Never injects a goal, book, plan, or Doctor action. This is a health witness,
not a substitute for independently checking original Laboratory/BrainStore receipts.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--install-root", type=Path, required=True)
    p.add_argument("--seconds", type=int, default=14400)
    p.add_argument("--interval", type=int, default=30)
    p.add_argument("--report-dir", type=Path, required=True)
    args = p.parse_args()
    if args.seconds != 14400 or args.interval != 30:
        p.error("Four-hour production witness requires 14,400s at 30s sampling")
    root = args.install_root.resolve(strict=True)
    workspace = root / "workspace"
    state = workspace / "state"
    world = workspace / "laboratory.sqlite3"
    brain = state / "brain.sqlite3"
    neural = state / "pretorius_recurrent.npz"
    if not all(x.is_file() for x in (world, brain, neural)):
        raise RuntimeError("Missing original world, BrainStore or neural checkpoint")
    report = args.report_dir.absolute()
    report.mkdir(parents=True, exist_ok=True)
    python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        raise FileNotFoundError("Installed Python missing")
    base = [str(python), "-m", "doctor_lives.cli"]
    stdinless = {"stdin": subprocess.DEVNULL, "cwd": root, "env": {**os.environ, "PYTHONPATH": ""}}
    start_state = {"world": digest(world), "brain": digest(brain), "neural": digest(neural)}
    samples: list[dict] = []
    failure: str | None = None
    started = time.monotonic()
    with (report / "operator.stdout.log").open("w") as out, \
         (report / "operator.stderr.log").open("w") as err:
        operator = subprocess.Popen(
            base + ["preview-resume", "--workspace", str(workspace)],
            stdout=out, stderr=err, **stdinless)
        try:
            while True:
                now = time.monotonic()
                elapsed = now - started
                if operator.poll() is not None:
                    failure = "operator_exited_during_witness"
                    break
                status = subprocess.run(
                    base + ["preview-status", "--workspace", str(workspace)],
                    capture_output=True, text=True, timeout=20, **stdinless)
                sample = {
                    "utc": utc(),
                    "monotonic_elapsed_seconds": elapsed,
                    "operator_pid": operator.pid,
                    "operator_returncode": operator.poll(),
                    "status_exit": status.returncode,
                    "status_response": status.stdout[-4000:],
                }
                if status.returncode != 0:
                    # Foreground startup may need a moment to create status.
                    # Do not count startup as a process failure.
                    if elapsed > 30.0:
                        failure = "public_operator_status_failed"
                else:
                    try:
                        status_json = json.loads(status.stdout)
                        if status_json.get("status") in ("unresponsive", "stopped", "error"):
                            failure = "public_operator_unhealthy"
                        if status_json.get("pid") not in (None, operator.pid):
                            failure = "operator_process_identity_mismatch"
                    except (json.JSONDecodeError, ValueError):
                        failure = "invalid_operator_status_json"
                samples.append(sample)
                with (report / "witness.jsonl").open("a") as sink:
                    sink.write(json.dumps(sample, sort_keys=True) + "\n")
                    sink.flush()
                    os.fsync(sink.fileno())
                if failure or elapsed >= args.seconds:
                    break
                time.sleep(min(args.interval, max(0.0, args.seconds - elapsed)))
        finally:
            if operator.poll() is None:
                try:
                    stop = subprocess.run(
                        base + ["preview-stop", "--workspace", str(workspace)],
                        capture_output=True, text=True, timeout=90, **stdinless)
                    if stop.returncode != 0 and failure is None:
                        failure = "public_operator_stop_failed"
                    operator.wait(timeout=90)
                except (subprocess.TimeoutExpired, OSError):
                    operator.kill()
                    operator.wait()
                    failure = failure or "operator_required_forced_kill"
    elapsed_total = time.monotonic() - started
    gaps = [b["monotonic_elapsed_seconds"] - a["monotonic_elapsed_seconds"]
            for a, b in zip(samples, samples[1:])]
    checks = {
        "real_monotonic_four_hours": elapsed_total >= 14400,
        "public_operator_stayed_alive": failure is None,
        "samples_every_30s_with_slack": bool(gaps) and max(gaps) <= 60,
        "single_observed_process": len({s["operator_pid"] for s in samples}) == 1,
        "workspace_persists": all(x.is_file() for x in (world, brain, neural)),
        "world_changed": digest(world) != start_state["world"],
        "canonical_brain_changed": digest(brain) != start_state["brain"],
    }
    verdict = {
        "schema": "pretorius.candidate-b.four-hour-witness.v1",
        "elapsed_monotonic_seconds": elapsed_total,
        "observed_samples": len(samples),
        "max_sampling_gap": max(gaps) if gaps else None,
        "failure": failure,
        "checks": checks,
        "pass": all(checks.values()),
        "not_proven_by_this_witness": [
            "three_distinct_uncoached_goals",
            "24h_uninterrupted_soak",
            "no_operator_prompting",
            "independent_world_receipt_attestation",
        ],
    }
    (report / "four-hour-witness.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n")
    print(json.dumps(verdict, sort_keys=True))
    return 0 if verdict["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
