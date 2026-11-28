"""Evidence-driven R4 stop/failure classification; no behavior authority."""
from __future__ import annotations

import errno
import signal
import traceback

ABSENCE = "three_distinct_uncoached_activities_not_observed"
INTEGRITY_PREFIXES = (
    "invalid_or_torn_activity_record:", "unapproved_external_input:",
    "coached_task_input:", "duplicate_goal_origin:", "unauthenticated_completion:",
    "original_source_world_authority_not_verified:", "independent_origin_witness_not_verified:",
)
RESOURCE_ERRNOS = {errno.ENOMEM, errno.ENOSPC, errno.EMFILE, errno.ENFILE,
                   getattr(errno, "EDQUOT", -1)}


def describe_exception(exc, *, phase):
    """Report an observed exception; do not infer OOM from a signal."""
    stack = traceback.extract_tb(exc.__traceback__)
    cls = type(exc)
    if isinstance(exc, MemoryError) or getattr(exc, "errno", None) in RESOURCE_ERRNOS:
        domain = "resource_exhaustion"
    elif isinstance(exc, KeyboardInterrupt):
        domain = "external_cancellation"
    elif cls.__name__ in ("EvidenceIntegrityError", "NeuralCheckpointError") and cls.__module__.startswith("doctor_lives."):
        domain = "evidence_integrity_failure"
    elif any(f.name == "_publish_typed_subject_frame" for f in stack):
        domain = "operator_error"
    elif any(f.name in ("native_step", "run_native_laboratory", "run_daily_life_cycle",
                       "_run_laboratory_session") for f in stack):
        domain = "runtime_failure"
    elif phase == "operator":
        domain = "operator_error"
    else:
        domain = "unknown"
    return {
        "schema": "pretorius.r4.failure.v1", "phase": phase,
        "classification": domain, "exception_type": cls.__module__+"."+cls.__name__,
        "errno": getattr(exc, "errno", None), "message": str(exc),
        "frames": [{"file": f.filename, "function": f.name, "line": f.lineno} for f in stack],
        "traceback": "".join(traceback.format_exception(exc)),
    }


def classify(*, initiator=None, requested_elapsed=None, watchdog_seconds,
             progress=False, operator_returncode=None, errors=(), diagnostics=(),
             cancelled_signal=None, audit_status=None, audit_problems=()):
    """Separate the stop initiator from failure classes and source verdict."""
    errors, diagnostics, problems = tuple(errors), tuple(diagnostics), tuple(audit_problems)
    valid_watchdog = (initiator == "watchdog" and requested_elapsed is not None
                      and requested_elapsed >= watchdog_seconds)
    classes = []

    def add(value):
        if value not in classes:
            classes.append(value)

    if cancelled_signal is not None or initiator == "external_cancellation":
        add("external_cancellation")
    for d in diagnostics:
        if d.get("schema") == "pretorius.r4.failure.v1":
            kind = d.get("classification")
            if kind in ("resource_exhaustion", "external_cancellation", "evidence_integrity_failure",
                        "runtime_failure", "operator_error", "unknown"):
                add(kind)
    if operator_returncode in (-signal.SIGINT, -signal.SIGTERM):
        add("external_cancellation")
    elif operator_returncode not in (None, 0) and not classes:
        add("unknown" if operator_returncode < 0 else "operator_error")
    if errors and not classes:
        add("operator_error" if any(x.startswith("operator_") for x in errors) else "unknown")
    if any(p.startswith(INTEGRITY_PREFIXES) for p in problems):
        add("evidence_integrity_failure")
    if (audit_status != "PASS" and not (problems and set(problems) == {ABSENCE})
            and not any(p.startswith(INTEGRITY_PREFIXES) for p in problems)):
        add("unknown")
    if classes:
        reason = classes[0]
    elif initiator == "receipt_progress_target" and progress and operator_returncode == 0 and audit_status == "PASS":
        reason = "capacity_completion"
    elif valid_watchdog:
        reason = "watchdog"
    elif initiator == "receipt_progress_target" and progress and set(problems) == {ABSENCE}:
        reason = "behavior_not_observed"
    else:
        reason = "unknown"
    return {
        "classification": reason, "stop_initiator": initiator,
        "watchdog_initiated": valid_watchdog,
        "stop_requested_elapsed_seconds": requested_elapsed,
        "operator_return_code": operator_returncode,
        "cancellation_signal": cancelled_signal, "failure_classes": classes,
        "errors": list(errors), "operator_diagnostics": list(diagnostics),
        "source_audit_status": audit_status, "source_audit_problems": list(problems),
    }
