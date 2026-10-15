"""Opt-in pure-tool execution of the existing Doctor's selected native action.

Tool authority stays in this host adapter. No renderer selects a tool and no
new identity, memory store, neural policy, or cognitive controller is created.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import time

from .cascade_background import operation_lock
from .cascade_governance import snapshot_doctor
from .neural import ACTIONS


@dataclass(frozen=True)
class TaskOption:
    action: str
    method: str

    def __post_init__(self):
        if self.action not in ACTIONS or self.method not in ("direct_sha256", "stream_sha256"):
            raise ValueError("Only native actions and allowlisted pure checksum tools are supported")


@dataclass(frozen=True)
class TaskGrant:
    request_id: str
    expected_state_digest: str
    input_sha256: str
    allowed_options: tuple[TaskOption, ...]

    def __post_init__(self):
        if not isinstance(self.request_id, str) or not self.request_id or len(self.request_id) > 128:
            raise ValueError("Bounded request ID required")
        if any(not isinstance(v, str) or len(v) != 64 or any(c not in '0123456789abcdef' for c in v)
               for v in (self.expected_state_digest, self.input_sha256)):
            raise ValueError("Exact hexadecimal state and task digests required")
        if (type(self.allowed_options) is not tuple or not 1 <= len(self.allowed_options) <= 10
                or any(type(o) is not TaskOption for o in self.allowed_options)
                or len({o.action for o in self.allowed_options}) != len(self.allowed_options)):
            raise ValueError("Unique bounded native action options required")


def issue_task_grant(host, *, request_id, text, options, authorized=False):
    if getattr(host, "_cascade_host_guard", None) is None:
        raise RuntimeError("An open CASCADE host is required")
    if type(authorized) is not bool or not authorized:
        raise PermissionError("Trusted host must explicitly authorize a task")
    if not isinstance(text, str) or not 1 <= len(text.encode('utf-8')) <= 65536:
        raise ValueError("Task input must be nonempty and at most 64 KiB")
    return TaskGrant(request_id, snapshot_doctor(host).state_digest,
                     hashlib.sha256(text.encode('utf-8')).hexdigest(), options)


def execute_task(host, *, grant, text, authorized=False):
    from .cascade_preview import CascadePretoriusPreview
    if not isinstance(host, CascadePretoriusPreview):
        raise TypeError("Actual isolated CASCADE host required")
    if getattr(host, "_cascade_host_guard", None) is None:
        raise RuntimeError("Closed host cannot execute tasks")
    if type(authorized) is not bool or not authorized or type(grant) is not TaskGrant:
        raise PermissionError("Explicit host task authority required")
    if not isinstance(text, str) or not 1 <= len(text.encode('utf-8')) <= 65536:
        raise ValueError("Bounded text task required")
    if hashlib.sha256(text.encode('utf-8')).hexdigest() != grant.input_sha256:
        raise PermissionError("Task content differs from authorized input")
    with operation_lock(host.state_dir):
        host._cascade_background.assert_reconciled()
        if host.pending_count() or host._journal.active() is not None:
            raise RuntimeError("Complete pending subject delivery before task actions")
        brain = host._doctor.brain
        with brain.store.connect() as conn:
            records = conn.execute("SELECT payload_json FROM events WHERE kind='preview_task_reservation'").fetchall()
        if any(json.loads(row[0])["request_id"] == grant.request_id for row in records):
            raise PermissionError("Task ID already reserved; no automatic replay or retry")
        if snapshot_doctor(host).state_digest != grant.expected_state_digest:
            raise PermissionError("Stale task state grant")
        # Commit reservation before policy or tool execution. A crash cannot
        # silently re-execute the request. Reservation itself is engineer evidence.
        with brain.store.transaction() as conn:
            brain.store.event(conn, brain.store.tick, "preview_task_reservation", "preview_task_host",
                              {"request_id": grant.request_id, "input_sha256": grant.input_sha256},
                              "lived_runtime_memory", False, 1.0)
            brain.store.bump_state_version(conn)
        started = time.perf_counter_ns()
        decision = brain.think(trigger="preview_authorized_tool_task",
                               decision_text="I can check this sample with the methods available to me.",
                               allowed_actions=tuple(o.action for o in grant.allowed_options))
        option = next(o for o in grant.allowed_options if o.action == decision["selected_action"])
        data = text.encode('utf-8')
        if option.method == "direct_sha256":
            result = hashlib.sha256(data).hexdigest()
        else:
            hasher = hashlib.sha256()
            for offset in range(0, len(data), 64):
                hasher.update(data[offset:offset + 64])
            result = hasher.hexdigest()
        receipt = {"schema": "pretorius.native-task.v1", "request_id": grant.request_id,
                   "input_sha256": grant.input_sha256, "result_sha256": result,
                   "selected_action": decision["selected_action"], "executed_method": option.method,
                   "policy_decision_id": decision["policy_decision_id"],
                   "policy_version": decision["policy_version"],
                   "elapsed_ns": time.perf_counter_ns() - started,
                   "renderer_called_for_selection": False, "external_io": False}
        with brain.store.transaction() as conn:
            brain.store.event(conn, brain.store.tick, "preview_task_completed", "preview_task_host",
                              receipt, "lived_runtime_memory", False, 1.0)
            brain.store.bump_state_version(conn)
        # Only first-person natural language enters subject experience. Do not
        # infer tool correctness here: a future evaluator must score the output.
        host.ingest({"channel": "tool", "percept": "The sample check has finished.",
                     "source": "preview_pure_checksum_tool"})
        return receipt
