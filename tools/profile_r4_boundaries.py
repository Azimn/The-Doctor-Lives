#!/usr/bin/env python3
"""Opt-in diagnostic timing for the real installed R4 operator.

No new input, goal, history, motor or source authority. Only run on a disposable
qualification installation. The separate JSONL is not acceptance evidence.
Nested measured boundaries are exclusive to the innermost timed boundary.
Database spans are connection/transaction scopes, not pure SQL-engine time.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from contextlib import contextmanager, closing
import functools
import importlib
import json
import math
from pathlib import Path
import sqlite3
import statistics
import sys
import time

try:
    import resource
except ImportError:
    resource = None

PHASES = ("cognitive_processing", "model_inference", "physical_world",
          "persistence_evidence", "operator_auditor")


class TimingRecorder:
    def __init__(self, stream):
        self.stream = stream
        self.rows = defaultdict(list)
        self.stack = []
        self.started = time.perf_counter_ns()
        self.window = self.started
        self.failed = False

    @contextmanager
    def span(self, phase, name):
        start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
        child = [0, 0]
        self.stack.append(child)
        try:
            yield
        finally:
            wall = time.perf_counter_ns() - start
            cpu = time.process_time_ns() - cpu_start
            self.stack.pop()
            if not self.failed:
                self.rows[(phase, name)].append((wall, cpu, max(0, wall-child[0]), max(0, cpu-child[1])))
            if self.stack:
                self.stack[-1][0] += wall
                self.stack[-1][1] += cpu

    def install(self, module, owner, name, phase, subphase, *, transaction=False):
        obj = importlib.import_module(module)
        if owner:
            obj = getattr(obj, owner)
        raw = vars(obj)[name]
        descriptor = isinstance(raw, classmethod)
        fn = raw.__func__ if descriptor else raw
        key = subphase + ":" + module + "." + ((owner + ".") if owner else "") + name
        if transaction:
            @contextmanager
            @functools.wraps(fn)
            def wrapped(*args, **kwargs):
                with self.span(phase, key), fn(*args, **kwargs) as result:
                    yield result
        else:
            @functools.wraps(fn)
            def wrapped(*args, **kwargs):
                with self.span(phase, key):
                    return fn(*args, **kwargs)
        setattr(obj, name, classmethod(wrapped) if descriptor else wrapped)
        return lambda: setattr(obj, name, raw)

    @staticmethod
    def summarize(rows):
        durations = sorted(row[0] for row in rows)
        return {
            "calls": len(rows), "wall_inclusive_ns": sum(durations),
            "wall_exclusive_ns": sum(r[2] for r in rows),
            "cpu_inclusive_ns": sum(r[1] for r in rows),
            "cpu_exclusive_ns": sum(r[3] for r in rows),
            "median_ns": statistics.median(durations),
            "p95_ns": durations[math.ceil(.95*len(rows))-1],
            "max_ns": durations[-1],
        }

    def flush(self, kind, *, workspace=None):
        if self.stack:
            raise RuntimeError("Flush only at a completed diagnostic timing boundary")
        if self.failed:
            self.rows.clear()
            return
        try:
            now = time.perf_counter_ns()
            counters = {}
            if workspace:
                # These are diagnostics, not source authentication or autonomous
                # behavior credit. Read-only connections after the real step.
                with closing(sqlite3.connect((workspace/"laboratory.sqlite3").resolve().as_uri()+"?mode=ro", uri=True)) as db:
                    counters["world_receipts"] = {t: db.execute("SELECT COUNT(*) FROM "+t).fetchone()[0]
                        for t in ("books_events", "rhythm_events", "embodied_events")}
                with closing(sqlite3.connect((workspace/"state/brain.sqlite3").resolve().as_uri()+"?mode=ro", uri=True)) as db:
                    counters["memory_rows"] = db.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
                    counters["policy_rows"] = db.execute("SELECT COUNT(*) FROM policy_decisions").fetchone()[0]
            phases = {name: [] for name in PHASES}
            details = {}
            for (phase, name), rows in self.rows.items():
                phases[phase].extend(rows)
                # Stream raw timings per opportunity for exact offline percentiles.
                details[name] = {"phase": phase, "summary": self.summarize(rows), "samples_ns": rows}
            payload = {
                "schema": "pretorius.r4.diagnostic-profile.v1", "window": kind,
                "elapsed_ns": now-self.started, "window_wall_ns": now-self.window,
                "phases": {k: self.summarize(v) if v else {"calls": 0} for k,v in phases.items()},
                "boundaries": details, "counters": counters,
                "peak_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource else None,
                "diagnostic_only": True, "autonomy_credit": False,
            }
            self.stream.write(json.dumps(payload, sort_keys=True)+"\n")
            self.stream.flush()
            self.window = time.perf_counter_ns()
        except (OSError, ValueError, sqlite3.Error) as exc:
            # A measurement failure is not authority over the subject or gate.
            self.failed = True
            print("R4_PROFILE_INCOMPLETE: "+repr(exc), file=sys.stderr, flush=True)
        finally:
            self.rows.clear()


def install_boundaries(p):
    P, C, W, O, M = "persistence_evidence", "cognitive_processing", "physical_world", "operator_auditor", "model_inference"
    points = [
        ("doctor_lives.evidence_authority","CanonicalEvidenceAuthority","prepare",P,"source_authentication"),
        ("doctor_lives.preview_native",None,"verify_donors",P,"source_authentication"),
        ("doctor_lives.sensus_pilot",None,"_load_verified_donor",P,"source_authentication"),
        ("doctor_lives.canonical_affectus_weather",None,"load_reviewed_weather",P,"source_authentication"),
        ("doctor_lives.cognition","PretoriusBrain","__init__",O,"runtime_initialization"),
        ("doctor_lives.organs","SixOrganRuntime","open",O,"runtime_initialization"),
        ("doctor_lives.lab_six_organ_session","SixOrganLaboratoryCycle","__init__",O,"runtime_initialization"),
        ("doctor_lives.store","BrainStore","connect",P,"database"),
        ("doctor_lives.store","BrainStore","digest",P,"database"),
        ("doctor_lives.neural","PretoriusRecurrentSubstrate","step",C,"neural_execution"),
        ("doctor_lives.neural","PretoriusRecurrentSubstrate","action_scores",C,"neural_execution"),
        ("doctor_lives.neural","PretoriusRecurrentSubstrate","load",P,"checkpoint_io"),
        ("doctor_lives.neural","PretoriusRecurrentSubstrate","save",P,"checkpoint_io"),
        ("doctor_lives.cognition","PretoriusBrain","think",C,"cognitive_processing"),
        ("doctor_lives.cognition","PretoriusBrain","ingest",C,"cognitive_processing"),
        ("doctor_lives.cognition","PretoriusBrain","_ranked_memory_sets",C,"cognitive_processing"),
        ("doctor_lives.ipseity_integration","DoctorSyntheticIpseitySession","_publish_typed_subject_frame",O,"subject_delivery"),
        ("doctor_lives.ipseity_integration","DoctorSyntheticIpseitySession","deliver_next",O,"subject_delivery"),
        ("synthetic_ipseity.local_ollama","LocalOllamaRenderer","__call__",M,"renderer_inference"),
        ("pretorius_lab.habitat_v2","SpatialHabitat","_open",P,"world_database"),
    ]
    for module, cls, act in [
        ("habitat_v2","SpatialHabitat","commit"), ("embodied_access","EmbodiedAccess","_offer"),
        ("home_life","HomeLife","_do"), ("daily_rhythm","DailyRhythm","act"),
        ("book_library","BookLibrary","_commit"), ("subject_port","SubjectPort","act"),
    ]:
        points.append(("pretorius_lab."+module,cls,"verify",P,"world_authentication"))
        points.append(("pretorius_lab."+module,cls,act,W,"original_world_execution"))
    undo = []
    try:
        for point in points:
            undo.append(p.install(*point))
        undo.append(p.install("doctor_lives.store","BrainStore","transaction",P,"transaction_scope",
                              transaction=True))
    except BaseException:
        for restore in reversed(undo):
            restore()
        raise
    return undo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("operator_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.operator_args
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv or argv[0] != "preview-start" or "--workspace" not in argv:
        parser.error("This diagnostic wraps the actual preview-start command")
    workspace = Path(argv[argv.index("--workspace")+1])
    from doctor_lives import preview_operator
    from doctor_lives.cli import main as original_main

    # Refuse to overwrite prior diagnostic evidence.
    with args.output.open("x", encoding="utf-8") as stream:
        recorder = TimingRecorder(stream)
        undo = install_boundaries(recorder)
        native = preview_operator.native_step
        @functools.wraps(native)
        def step(*a, **kw):
            try:
                with recorder.span("operator_auditor", "native_step_total"):
                    return native(*a, **kw)
            finally:
                recorder.flush("native_step", workspace=workspace)
        preview_operator.native_step = step
        try:
            return original_main(argv)
        finally:
            preview_operator.native_step = native
            for restore in reversed(undo):
                restore()
            recorder.flush("operator_exit", workspace=workspace)


if __name__ == "__main__":
    raise SystemExit(main())
