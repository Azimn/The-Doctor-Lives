"""Bounded, offline, real-elapsed-time host for the ONE original Doctor brain.

The host schedules cognitive opportunities only. It never chooses goals,
issues physical actions, forges world perceptions, or renders engineer data as
subjective experience. The original Laboratory remains the world authority.
"""
from __future__ import annotations

import errno
from contextlib import contextmanager
import math
import os
import secrets
from pathlib import Path
import threading
import time

from .engineer_time import engineer_time


@contextmanager
def _exclusive_lock(lock_path: Path, label: str):
    """Keep a cooperative OS lock on a persistent, non-symlink sidecar."""
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(lock_path, flags, 0o600)
    with os.fdopen(fd, "r+b") as handle:
        acquired = False
        try:
            if os.name == "nt":
                import msvcrt
                # Windows byte-range locks must target an existing byte.
                # Persistent sidecars start empty on a clean offline install.
                # Initialize once; competing initializers write the same byte
                # and still arbitrate exclusively through the OS lock below.
                if os.fstat(handle.fileno()).st_size == 0:
                    handle.write(b"0")
                    handle.flush()
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            acquired = True
        except OSError as exc:
            if exc.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                raise RuntimeError(f"{label} host already active") from exc
            raise
        try:
            yield
        finally:
            if acquired:
                if os.name == "nt":
                    import msvcrt
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def _exclusive_host(state: Path, world: Path | None = None):
    """Exclude cooperating hosts sharing EITHER the brain OR the real world.

    The original state lock remains in place. A second lock beside the
    resolved Laboratory SQLite file also denies a different state directory
    pointed at the same world. Both sidecars are persistent so unlinking
    cannot silently split lock ownership. These are cooperative host leases,
    not protection from privileged/direct database writers.
    """
    with _exclusive_lock(state / ".laboratory-host.lock", "Canonical Doctor Laboratory"):
        if world is None:
            yield
        else:
            canonical_world = world.resolve(strict=True)
            if not canonical_world.is_file():
                raise FileNotFoundError("Existing authoritative Laboratory world required")
            # A pathname-based sidecar is not shared by hardlinks to the same
            # SQLite inode. Fail closed before opening either world authority
            # rather than allow two cooperating hosts to lock different names.
            if canonical_world.stat().st_nlink != 1:
                raise RuntimeError("Authoritative Laboratory world hardlinks are unsupported")
            world_lock = canonical_world.with_name(
                canonical_world.name + ".laboratory-host.lock"
            )
            with _exclusive_lock(world_lock, "Authoritative Laboratory world"):
                # Recheck after acquiring the sidecar. A new hardlink created
                # while another host runs is rejected by its next entrant.
                if canonical_world.stat().st_nlink != 1:
                    raise RuntimeError("Authoritative Laboratory world hardlinks are unsupported")
                yield


def run_laboratory(
    state: Path, world: Path, *, duration_seconds: float,
    interval_seconds: float, stop: threading.Event | None = None,
    work_interval_seconds: float | None = None,
    activity_sink=None,
) -> dict:
    """Run with one brain/world lease; optional host-offered Noesis work."""
    with _exclusive_host(state, world):
        return _run_laboratory_session(
            state, world, duration_seconds=duration_seconds,
            interval_seconds=interval_seconds, stop=stop,
            work_interval_seconds=work_interval_seconds,
            activity_sink=activity_sink,
        )




def _recover_shipping_actions(bridge):
    """Safely reconcile all pending intents before admitting any lived memory.

    A killed process can leave an intent with no world effect. Never execute
    that ghost motor command on restart: prove absence across every original
    Laboratory receipt domain, then atomically discard its pending reservation
    using the EXISTING Doctor bridge journal. For a committed receipt, verify
    its exact action identity and original Noesis provenance before replay.
    The caller holds both cooperative authority locks throughout.
    """
    from .lab_home_bridge import _ACTION_DOMAINS, _row
    from .noesis_lab_work import verify_noesis_work_replay

    pending = bridge.pending_action_intents()
    committed, uncommitted = [], []
    # Validate the ENTIRE batch before changing any journal or autobiography.
    with bridge.world._open() as db:
        for item in pending:
            op, event_id, args = item["op"], item["event_id"], item["args"]
            table = _ACTION_DOMAINS.get(op)
            if table is None:
                raise PermissionError("Unknown pending Laboratory action")
            present = db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            ).fetchone()
            if not present:
                raise RuntimeError("Missing authoritative Laboratory receipt table")
            found = db.execute(
                "SELECT 1 FROM " + table + " WHERE event_id=? LIMIT 1",
                (event_id,),
            ).fetchone()
            if found is None:
                uncommitted.append(item)
                continue
            receipt, _ = _row(db, table, event_id)
            bridge._check_action_proof(op, args, receipt)
            if op in ("repair", "experiment"):
                verify_noesis_work_replay(
                    bridge, event_id=event_id, action=op,
                )
            committed.append(item)
    # An absent expected receipt might still be a conflicting receipt in
    # another domain. The bridge rechecks ALL domains while holding the
    # existing SQLite intent transaction and refuses uncertain outcomes.
    for item in uncommitted:
        bridge.abandon_proven_uncommitted_intent(
            item["event_id"], item["op"], item["args"],
        )
    recovered = bridge.recover_pending_actions()
    if bridge.pending_action_intents():
        raise RuntimeError("Unreconciled Laboratory action; host denied")
    if len(recovered) != len(committed):
        raise RuntimeError("Laboratory recovery identity count changed")
    return tuple(committed), recovered, tuple(uncommitted)


def sleep_laboratory(state: Path, world: Path, *, event_id: str) -> dict:
    """Operator-requested, original-Lab physical sleep, never a Doctor goal.

    The original Laboratory must place the body in its actual bedroom first.
    A caller supplies one stable action ID; replay cannot advance the world
    again. This advances Laboratory *simulated* time, not wall-clock soak time.
    The next lab-run is the explicit wake/resume operation.
    """
    from .lab_home_bridge import _SAFE_ID
    if type(event_id) is not str or not _SAFE_ID.fullmatch(event_id):
        raise ValueError("Stable bounded Laboratory sleep action ID required")
    with _exclusive_host(state, world):
        if not (state / "brain.sqlite3").is_file() or not (
            state / "pretorius_recurrent.npz"
        ).is_file():
            raise FileNotFoundError(
                "Existing canonical Doctor BrainStore and neural checkpoint required"
            )
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.subject_port import SubjectPort
        from .organs import SixOrganRuntime

        runtime = SixOrganRuntime.open(state)
        bridge = runtime.bind_laboratory(
            SubjectPort(SpatialHabitat(world)), authorized=True,
        )
        # A crash may leave an original-Noesis work motor binding BEFORE
        # any Doctor action intent exists. Reject its reuse as sleep before
        # recovering unrelated pending actions or creating a new reservation.
        # The bridge independently enforces this for every non-work action.
        from .noesis_lab_work import prior_noesis_motor_binding
        if prior_noesis_motor_binding(bridge, event_id):
            raise PermissionError(
                "Laboratory action ID already bound to an original-Noesis work decision"
            )
        # The world may contain a genuine sleep by another actor. Check
        # PREEXISTING Doctor ownership before recovery or bridge.act could
        # manufacture an intent and launder that event into autobiography.
        with bridge.world._open() as db:
            historical_sleep = db.execute(
                "SELECT 1 FROM rhythm_events WHERE event_id=? LIMIT 1",
                (event_id,),
            ).fetchone() is not None
        if historical_sleep:
            owned = bridge.existing_action_intent(event_id)
            if (owned is None or owned["op"] != "sleep"
                    or owned["args"] != {}):
                raise RuntimeError(
                    "No matching preexisting Doctor-owned sleep reservation"
                )
        # Capture identities before replay so a recovered sleep is presented
        # only once. The bridge remains the sole durable intent authority.
        pending_before, recovered, abandoned = _recover_shipping_actions(bridge)

        # A historical receipt is allowed to replay after Pretorius has
        # genuinely walked elsewhere. This lookup grants NO authority: act()
        # must still authenticate the original receipt, action identity, and
        # canonical lived memory. A NEW sleep remains bedroom-only.
        if (not historical_sleep
                and bridge.subject.embodied.verify()["station"] != "station:bedroom"):
            raise RuntimeError(
                "Physical sleep requires the actual Laboratory bedroom"
            )
        result = bridge.act("sleep", event_id=event_id)
        runtime.checkpoint()
        clock = engineer_time()
        subject_frames = [
            item["subject"] for intent, item in zip(pending_before, recovered)
            if intent["event_id"] != event_id
        ]
        subject_frames.append(result["subject"])
        return {
            "schema": "doctor-laboratory-offline-sleep.v1",
            "status": result["status"],
            "recovered": len(recovered),
            "abandoned": len(abandoned),
            "subject_frames": subject_frames,
            "physical_sleep_minutes": 480,
            "clock": {"utc": clock.utc_iso, "beat": clock.beat},
        }



def work_laboratory(state: Path, world: Path, *, event_id: str) -> dict:
    """One operator-offered bench opportunity, chosen by the ORIGINAL Noesis.

    The host cannot select repair versus experiment. Original Laboratory
    physics supplies eligibility and the existing authorized bridge supplies
    durable action intent, source-backed memory, and cold crash recovery.
    This is a bounded externally offered opportunity, not self-initiation.
    """
    from .lab_home_bridge import _ACTION_DOMAINS, _SAFE_ID, _row

    # Deny malformed IDs before opening the canonical brain or creating LOOK.
    if type(event_id) is not str or not _SAFE_ID.fullmatch(event_id):
        raise ValueError("Stable bounded Laboratory work action ID required")
    with _exclusive_host(state, world):
        if not (state / "brain.sqlite3").is_file() or not (
            state / "pretorius_recurrent.npz"
        ).is_file():
            raise FileNotFoundError(
                "Existing canonical Doctor BrainStore and neural checkpoint required"
            )
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.subject_port import SubjectPort
        from .organs import SixOrganRuntime
        from .noesis_lab_work import (
            propose_noesis_work, execute_noesis_work, verify_noesis_work_replay,
            prior_noesis_motor_binding,
        )

        runtime = SixOrganRuntime.open(state)
        bridge = runtime.bind_laboratory(
            SubjectPort(SpatialHabitat(world)), authorized=True,
        )
        pending_before, recovered, abandoned = _recover_shipping_actions(bridge)
        # A recovered action ID cannot be reused for a different offered task.
        for intent in pending_before:
            if intent["event_id"] == event_id and (
                intent["op"] not in ("repair", "experiment") or intent["args"] != {}
            ):
                raise RuntimeError(
                    "Work event ID already reserved for another Laboratory action"
                )
        subject_frames = [
            item["subject"] for intent, item in zip(pending_before, recovered)
            if intent["event_id"] != event_id
        ]

        # A stable ID is a world-wide intent identity, not just a rhythm row.
        # Refuse a foreign embodied/book ID before making a new Noesis choice.
        # A historical work receipt is replayed, never executed a second time
        # and never misreported as a newly selected cognitive action.
        with bridge.world._open() as db:
            tables = {
                row[0] for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            for table in sorted(set(_ACTION_DOMAINS.values()) - {"rhythm_events"}):
                if table in tables and db.execute(
                    "SELECT 1 FROM " + table + " WHERE event_id=? LIMIT 1",
                    (event_id,),
                ).fetchone():
                    raise RuntimeError(
                        "Work event ID already belongs to another Laboratory action"
                    )
            prior = (
                _row(db, "rhythm_events", event_id)[0]
                if db.execute(
                    "SELECT 1 FROM rhythm_events WHERE event_id=?",
                    (event_id,),
                ).fetchone()
                else None
            )
        if prior is not None:
            action = prior.get("op")
            if action not in ("repair", "experiment") or prior.get("args") != {}:
                raise RuntimeError("Work event ID belongs to non-work rhythm action")
            # A hash-valid world event is NOT proof that Pretorius performed it.
            # Deny foreign same-domain receipts before bridge.act could create
            # a fresh intent and misattribute another actor's lived event.
            verify_noesis_work_replay(
                bridge, event_id=event_id, action=action,
            )
            replay = bridge.act(action, event_id=event_id)
            runtime.checkpoint()
            subject_frames.append(replay["subject"])
            clock = engineer_time()
            return {
                "schema": "doctor-laboratory-offline-work.v1",
                "status": replay["status"],
                "action": action,
                "selection": "historical_world_receipt_replay",
                "recovered": len(recovered),
                "abandoned": len(abandoned),
                "subject_frames": subject_frames,
                "clock": {"utc": clock.utc_iso, "beat": clock.beat},
            }

        # A killed child may have bound Noesis before reserving the bridge
        # intent, or may have left a proven-uncommitted tombstone on restart.
        # Neither case may create a second policy choice for the same ID.
        if bridge.abandoned_action_intent(event_id):
            raise RuntimeError(
                "Laboratory action ID permanently abandoned before world commit"
            )
        if prior_noesis_motor_binding(bridge, event_id):
            raise PermissionError(
                "Work event ID already bound to an original-Noesis decision"
            )
        # Reuse the already-tested Noesis choice and original Lab motor bridge.
        # Neither the CLI nor the scheduler supplies an action preference.
        proposal = propose_noesis_work(
            bridge, outcome_learning_enabled=True,
        )
        executed = execute_noesis_work(
            bridge, decision_id=proposal.decision_id,
            event_id=event_id, authorized_world_action=True,
        )
        runtime.checkpoint()
        subject_frames.append(executed["world"]["subject"])
        clock = engineer_time()
        return {
            "schema": "doctor-laboratory-offline-work.v1",
            "status": executed["world"]["status"],
            "action": executed["action"],
            "selection": "original_noesis",
            "recovered": len(recovered),
            "abandoned": len(abandoned),
            "subject_frames": subject_frames,
            "clock": {"utc": clock.utc_iso, "beat": clock.beat},
        }


def _run_laboratory_session(
    state: Path, world: Path, *, duration_seconds: float,
    interval_seconds: float, stop: threading.Event | None = None,
    work_interval_seconds: float | None = None,
    activity_sink=None,
) -> dict:
    """Recover, observe, pulse, and optionally offer native Noesis bench work.

    Each scheduled work opportunity presents all physically feasible bench
    actions to the ORIGINAL Noesis. The host never chooses the action, moves
    the body to the bench, or authors an enduring goal. This is externally
    offered work, not independent self-initiation or a 24-hour soak.
    """
    if not (math.isfinite(duration_seconds) and 0.1 <= duration_seconds <= 3600):
        raise ValueError("duration_seconds must be finite and between 0.1 and 3600")
    if not (math.isfinite(interval_seconds) and 0.05 <= interval_seconds <= duration_seconds):
        raise ValueError("interval_seconds must be finite and between 0.05 and duration")
    if work_interval_seconds is not None and not (
        math.isfinite(work_interval_seconds)
        and 0.05 <= work_interval_seconds <= duration_seconds
    ):
        raise ValueError("work_interval_seconds must be finite and between 0.05 and duration")
    if not world.is_file():
        raise FileNotFoundError("Existing authoritative Laboratory world required")
    if not (state / "brain.sqlite3").is_file() or not (
        state / "pretorius_recurrent.npz"
    ).is_file():
        raise FileNotFoundError("Existing canonical Doctor BrainStore and neural checkpoint required")

    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.subject_port import SubjectPort
    from .organs import SixOrganRuntime

    stop = stop if stop is not None else threading.Event()
    # A cancellation already delivered by the CLI signal handler must not
    # produce a new Laboratory LOOK receipt or a lived observation.
    if stop.is_set():
        clock = engineer_time()
        return {
            "schema": "doctor-laboratory-offline-run.v1",
            "status": "interrupted",
            "recovered": 0,
            "subject_frames": [],
            "pulses": 0,
            "work_events": [],
            "elapsed_seconds": 0.0,
            "clock": {"utc": clock.utc_iso, "beat": clock.beat},
        }
    runtime = SixOrganRuntime.open(state)
    bridge = runtime.bind_laboratory(
        SubjectPort(SpatialHabitat(world)), authorized=True,
    )
    _, recovered, abandoned = _recover_shipping_actions(bridge)
    subject_frames = [item["subject"] for item in recovered]
    # Reconciliation may finish after an interrupt. Never start a fresh
    # observation when cancellation arrived during that recovery window.
    if not stop.is_set():
        # The outer check is not sufficient: cancellation may arrive while
        # the bridge prepares its verified physical LOOK. The bridge must
        # check the same stop predicate before invoking original Lab LOOK.
        observed = bridge.observe(cancelled=stop.is_set)
        if observed is not None:
            subject_frames.append(observed["subject"])
    pulses = 0
    work_events = []
    started = time.monotonic()
    deadline = started + duration_seconds
    next_pulse = started + interval_seconds
    next_work = (
        started + work_interval_seconds
        if work_interval_seconds is not None else None
    )
    try:
        while not stop.is_set():
            now = time.monotonic()
            if now >= deadline:
                break
            next_due = min(
                next_pulse, deadline,
                next_work if next_work is not None else deadline,
            )
            if stop.wait(max(0.0, next_due - now)):
                break
            now = time.monotonic()
            if now >= deadline:
                break
            if next_work is not None and now >= next_work:
                # The host offers work, never chooses or navigates for him.
                from .noesis_lab_work import (
                    _feasible_work, propose_noesis_work, execute_noesis_work,
                )
                # Off-bench means no work opportunity, not a host error.
                # This is a physical precondition, never automatic navigation.
                if (bridge.subject.embodied.verify()["station"] == "station:bench"
                        and _feasible_work(bridge)):
                    proposal = propose_noesis_work(
                        bridge, outcome_learning_enabled=True,
                    )
                    if stop.is_set():
                        break
                    event_id = "elapsed-work-" + secrets.token_hex(16)
                    if activity_sink is not None:
                        activity_sink({
                            "phase": "selected", "event_id": event_id,
                            "action": proposal.action,
                            "decision_id": proposal.decision_id,
                            "selection": "original_noesis",
                            "physical_consequence": None, "memory_write": None,
                        })
                    executed = execute_noesis_work(
                        bridge, decision_id=proposal.decision_id,
                        event_id=event_id, authorized_world_action=True,
                    )
                    runtime.checkpoint()
                    if activity_sink is not None:
                        # The ledger cannot authenticate itself. Reopen actual
                        # original Laboratory and canonical brain under the
                        # existing host leases before calling an effect complete.
                        import hashlib
                        from .lab_home_bridge import _row
                        from .noesis_lab_work import verify_noesis_work_replay
                        with bridge.world._open() as db:
                            original, receipt_hash = _row(db, "rhythm_events", event_id)
                        verified_policy = verify_noesis_work_replay(
                            bridge, event_id=event_id, action=executed["action"])
                        memory = [
                            m for m in bridge.doctor.brain.store.memories(False)
                            if m["source"] == "laboratory-home:action:" + receipt_hash
                        ]
                        if (original.get("op") != executed["action"]
                                or len(memory) != 1 or memory[0]["external"]
                                or memory[0]["evidence_class"] != "lived_runtime_memory"
                                or original.get("subject", {}).get("inner") != memory[0]["text"]):
                            raise PermissionError("No source-authenticated work and memory")
                        activity_sink({
                            "phase": "completed", "event_id": event_id,
                            "action": executed["action"],
                            "selection": "original_noesis",
                            "policy_decision_id": verified_policy,
                            "original_world_receipt_sha256": receipt_hash,
                            "original_world_receipt_utc": original.get("utc"),
                            "memory_id": memory[0]["id"],
                            "memory_text_sha256": hashlib.sha256(
                                memory[0]["text"].encode("utf-8")).hexdigest(),
                            "memory_text": memory[0]["text"],
                            "canonical_memory_source": memory[0]["source"],
                            "source_checked_on_host": True,
                            "independent_source_attestation": False,
                        })
                    subject_frames.append(executed["world"]["subject"])
                    work_events.append({
                        "event_id": event_id,
                        "action": executed["action"],
                        "status": executed["world"]["status"],
                        "selection": "original_noesis",
                    })
                # Skip missed opportunities after slow real-world operations.
                next_work = time.monotonic() + work_interval_seconds
            if stop.is_set():
                break
            now = time.monotonic()
            if now >= next_pulse and now < deadline:
                runtime.noesis.pulse(1)
                runtime.checkpoint()
                pulses += 1
                next_pulse = max(
                    next_pulse + interval_seconds, now + interval_seconds,
                )
    finally:
        runtime.checkpoint()
    clock = engineer_time()
    return {
        "schema": "doctor-laboratory-offline-run.v1",
        "status": "interrupted" if stop.is_set() else "completed",
        "recovered": len(recovered),
        "abandoned": len(abandoned),
        "subject_frames": subject_frames,
        "pulses": pulses,
        "work_events": work_events,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "clock": {"utc": clock.utc_iso, "beat": clock.beat},
    }


def run_native_laboratory(
    state: Path, world: Path, *, affectus_source: Path,
    steps: int = 1, allow_world_actions: bool = False,
) -> dict:
    """Offer bounded original six-organ goal opportunities on the shipping host.

    This is opt-in and requires the existing pinned, locally installed donors.
    The original neural policy originates explore/avoid; the EXISTING native
    chooser maps these to book/rest goals. That mapping and physical routing
    remain host-owned and are disclosed, not misreported as open-ended agency.
    Neither an LLM nor this host supplies a goal, book ID, or action preference.
    """
    if type(steps) is not int or not 1 <= steps <= 64:
        raise ValueError("Native goal steps must be an integer from 1 to 64")
    if type(allow_world_actions) is not bool:
        raise TypeError("World-action permission must be a boolean")
    state, world, affectus_source = Path(state), Path(world), Path(affectus_source)
    if not affectus_source.is_dir():
        raise FileNotFoundError("Existing local pinned Affectus donor required")
    if not world.is_file():
        raise FileNotFoundError("Existing authoritative Laboratory world required")
    if not (state / "brain.sqlite3").is_file() or not (
        state / "pretorius_recurrent.npz"
    ).is_file():
        raise FileNotFoundError("Existing canonical Doctor state required")

    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.subject_port import SubjectPort
    from .lab_native_goal_choice import NativeLaboratoryGoalChooser
    from .lab_six_organ_session import SixOrganLaboratoryCycle
    from .organs import SixOrganRuntime

    def source_only_renderer(subject: str) -> str:
        if type(subject) is not str or not subject.startswith(
            ("I ", "My ", "Mine ", "Me ")
        ):
            raise PermissionError("Renderer received non-subject diagnostics")
        return subject

    with _exclusive_host(state, world):
        runtime = SixOrganRuntime.open(state)
        subject = SubjectPort(SpatialHabitat(world))
        epoch = subject.verify()["world_epoch"]
        receipts = []
        with SixOrganLaboratoryCycle(
            runtime, subject, affectus_source=affectus_source,
            renderer=source_only_renderer, authorized=True,
        ) as session:
            # Reconcile shipping work/sleep intents before offering a new goal.
            # The six-organ session separately reconciles its own movement.
            _, recovered, abandoned = _recover_shipping_actions(session.bridge)
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            try:
                for _ in range(steps):
                    result = chooser.step(
                        authorized_world_action=allow_world_actions
                    )
                    receipts.append({
                        "status": result.status,
                        "kind": result.kind,
                        "goal_id": result.goal_id,
                        "memory_id": result.memory_id,
                        "selected_tendency": result.selected_tendency,
                        "host_selected_goal_mapping": result.host_selected_goal_mapping,
                        "host_selected_route": result.host_selected_route,
                    })
                    if result.status in (
                        "completed", "already_complete", "exhausted",
                        "authorization_required",
                    ):
                        break
            finally:
                runtime.checkpoint()
        if subject.verify()["world_epoch"] != epoch:
            raise RuntimeError("Authoritative Laboratory epoch changed")
        clock = engineer_time()
        return {
            "schema": "doctor-laboratory-native-goals.v1",
            "status": receipts[-1]["status"],
            "steps": len(receipts),
            "recovered": len(recovered),
            "abandoned": len(abandoned),
            "receipts": receipts,
            "same_original_brain": True,
            "original_world_epoch_unchanged": True,
            "host_selected_goal_mapping": True,
            "uncoached_three_task_life_proven": False,
            "natural_language_goal_authorship_proven": False,
            "cloud_calls": 0,
            "clock": {"utc": clock.utc_iso, "beat": clock.beat},
        }
