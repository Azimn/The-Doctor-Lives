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
import sqlite3
from contextlib import closing
from doctor_lives.lab_failure_taxonomy import HealthSample, classify

def completed_physical_tasks(world: Path) -> int:
    """Original Laboratory receipts only, not activity ledger or heartbeat."""
    target = world.absolute().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(target, uri=True)) as db:
        rhythm = [json.loads(row[0]) for row in db.execute(
            "SELECT envelope FROM rhythm_events")]
        books = [json.loads(row[0]) for row in db.execute(
            "SELECT envelope FROM books_events")]
    tasks = {"prepare_meal", "eat", "brew_tea", "sleep", "rest",
             "clean", "experiment", "repair"}
    return (sum(event.get("op") in tasks for event in rhythm)
            + sum(event.get("action", {}).get("op") == "read"
                  for event in books))


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
    task_count_start = completed_physical_tasks(world)
    task_count_current = task_count_start
    last_new_task = None
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
                status_heartbeat_age = None
                task_count_now = completed_physical_tasks(world)
                if task_count_now < task_count_current:
                    failure = "physical_ledger_regressed"
                if task_count_now > task_count_current:
                    last_new_task = elapsed
                task_count_current = task_count_now
                if status.returncode == 0:
                    try:
                        status_data = json.loads(status.stdout)
                        stamp = datetime.fromisoformat(
                            status_data["last_heartbeat"].replace("Z", "+00:00"))
                        status_heartbeat_age = max(
                            0.0, (datetime.now(timezone.utc)-stamp).total_seconds())
                    except (ValueError, KeyError, TypeError):
                        pass
                live = HealthSample(
                    process_alive=operator.poll() is None,
                    elapsed_seconds=elapsed,
                    heartbeat_age_seconds=status_heartbeat_age,
                    last_physical_task_age_seconds=(
                        elapsed - last_new_task if last_new_task is not None else None),
                    verified_completed_tasks=task_count_now-task_count_start,
                )
                classification = classify(live)
                sample["health_classification"] = classification
                sample["source_physical_task_receipts_since_start"] = (
                    task_count_now-task_count_start)
                sample["operator_heartbeat_age_seconds"] = status_heartbeat_age
                if classification in ("crash", "stall", "silent_skip"):
                    failure = failure or classification
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
        "original_physical_task_progress": task_count_current > task_count_start,
        "no_crash_stall_or_silent_skip": failure is None,
    }
    verdict = {
        "schema": "pretorius.candidate-b.four-hour-witness.v1",
        "elapsed_monotonic_seconds": elapsed_total,
        "observed_samples": len(samples),
        "max_sampling_gap": max(gaps) if gaps else None,
        "failure": failure,
        "failure_kind": failure if failure in (
            "crash", "stall", "silent_skip") else (
                "infrastructure_or_source_integrity" if failure else None),
        "original_world_task_count_start": task_count_start,
        "original_world_task_count_end": task_count_current,
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
