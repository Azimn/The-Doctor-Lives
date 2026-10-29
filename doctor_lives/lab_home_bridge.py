"""Opt-in source-verified bridge from the real Doctor to his Laboratory home.

The Laboratory remains the physical authority and the existing PretoriusBrain
remains the ONLY identity/cognition/memory authority. This module is a trusted
host adapter, not a second planner or a renderer. World actions are physical
actions, but an action offer is not evidence the Doctor independently chose it.
"""
from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
import sqlite3
import json
import re
from typing import Any

from .chassis import PretoriusBrainPort

SCHEMA = "doctor-laboratory-home-bridge.v0.1"
_ACTION_DOMAINS = {
    "walk": "embodied_events", "open": "domestic_events",
    "close": "domestic_events", "take": "domestic_events",
    "put": "domestic_events", "shift_stool": "domestic_events",
    "advance": "rhythm_events", "light": "rhythm_events",
    "extinguish": "rhythm_events", "prepare_meal": "rhythm_events",
    "eat": "rhythm_events", "brew_tea": "rhythm_events",
    "sleep": "rhythm_events", "rest": "rhythm_events",
    "clean": "rhythm_events", "experiment": "rhythm_events",
    "repair": "rhythm_events", "book": "books_events",
    "measure": "instrument_events", "take_book": "custody_events",
    "put_book": "custody_events",
}
_EVENT_PAYLOAD_COLUMNS = {"books_events": "payload", "custody_events": "payload"}
_SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")
_HEX = re.compile(r"[0-9a-f]{64}\Z")


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _first_person_frame(value: dict) -> str:
    if not isinstance(value, dict) or set(value) != {"inner", "spoken_aloud"}:
        raise ValueError("Only an authenticated two-field subject frame is admissible")
    text, spoken = value["inner"], value["spoken_aloud"]
    if not isinstance(text, str) or not re.match(r"^(?:I|My|Mine|Me)\b", text):
        raise ValueError("Only first-person natural-language perception is admissible")
    if not text.strip() or text.lstrip().startswith(("{", "[")):
        raise ValueError("Structured engineering input cannot become experience")
    if spoken is not None and (not isinstance(spoken, str) or not spoken.strip()):
        raise ValueError("Invalid audible world event")
    # The subject's own out-loud response is already experienced in the frame.
    # The host does not silently present a second authoritative voice.
    return text


def _row(db, table, event_id):
    # Only the hard-coded trusted domain mapping selects these tables.
    # Source books/custody store "payload"; physical/rhythm "envelope".
    column = _EVENT_PAYLOAD_COLUMNS.get(table, "envelope")
    result = db.execute(
        "SELECT " + column + ",event_hash FROM " + table + " WHERE event_id=?",
        (event_id,),
    ).fetchone()
    if not result:
        raise RuntimeError("An offered Laboratory action has no durable world receipt")
    envelope, event_hash = result
    parsed = json.loads(envelope)
    if _hash(parsed) != event_hash or not _HEX.fullmatch(event_hash):
        raise RuntimeError("Laboratory event evidence is not authentic")
    return parsed, event_hash


class DoctorHomeBridge:
    """Explicitly authorized Laboratory access on the *actual* PretoriusBrainPort.

    This is not an autonomous scheduler. Each call represents an authorized
    host action or a requested perception. The real Doctor receives only its
    admitted perspectival text, through the existing ingress firewall.
    """

    def __init__(self, doctor: PretoriusBrainPort, subject_port, *,
                 authorized: bool = False):
        if type(authorized) is not bool or not authorized:
            raise PermissionError("Explicit isolated Laboratory opt-in required")
        if not isinstance(doctor, PretoriusBrainPort):
            raise TypeError("Expected the actual Doctor Lives brain port")
        if not hasattr(subject_port, "habitat") or not hasattr(subject_port, "act"):
            raise TypeError("Expected the restricted Laboratory subject port")
        self.doctor = doctor
        self.subject = subject_port
        self.world = subject_port.habitat
        self.subject.verify()
        self._active_verified_admission = None
        self.doctor._register_laboratory_bridge(self)

    def _admit_verified(self, frame, source, *, kind, source_book_page=False):
        """Host-only handoff after verified observation or physical action.

        The active grant is one-use and never materialized as a portable
        boolean or user-provided source label. Only the two world-verified
        entrypoints below may call this method.
        """
        if self._active_verified_admission is not None:
            raise RuntimeError("Overlapping Laboratory source admissions")
        text = _first_person_frame(frame)
        if source_book_page:
            text = " ".join(text.split())
        self._active_verified_admission = (source, text)
        try:
            return self._admit(
                frame, source, kind=kind, source_book_page=source_book_page,
            )
        finally:
            self._active_verified_admission = None

    def _admit(self, frame, source, *, kind, source_book_page=False):
        text = _first_person_frame(frame)
        if source_book_page:
            # The Laboratory stores the ORIGINAL verified source bytes with
            # print-style newlines in its book ledger. Doctor's existing
            # world ingress intentionally normalizes all whitespace. For
            # a verified BOOK READ only, normalize that same whitespace
            # *before* the canonical admission equality check, so a real
            # book's content is neither rejected nor silently rewritten.
            # Keep original full source and independent receipt unchanged.
            text = " ".join(text.split())
            frame = {"inner": text, "spoken_aloud": frame["spoken_aloud"]}
        if self._active_verified_admission != (source, text):
            raise PermissionError("Laboratory experience was not verified by the host")
        if not source.startswith("laboratory-home:"):
            raise PermissionError("Unapproved lived Laboratory source")
        if len(source) > 225:
            raise ValueError("Unbounded Laboratory source key")
        # This makes interrupted bridge delivery idempotent without claiming
        # cross-database atomicity. If the brain was written but the host
        # crashed before returning, a retry finds that exact admitted source.
        previous = [row for row in self.doctor.brain.store.memories(False)
                    if row["source"] == source]
        if previous:
            if len(previous) != 1 or previous[0]["text"] != text:
                raise RuntimeError("Conflicting Doctor memory bound to world source")
            return {"status": "already_admitted",
                    "memory_id": previous[0]["id"],
                    "subject": frame}
        outcome = self.doctor._ingest_verified_laboratory({
            "channel": "world", "percept": text,
            "kind": kind, "source": source,
            "confidence": 1.0,
        }, bridge=self)
        if outcome["ingress"]["subject_text"] != text:
            raise RuntimeError("Doctor ingress changed verified world wording")
        return {"status": "admitted", "memory_id": outcome["memory_id"],
                "subject": frame}

    @staticmethod
    def _physical_stamp(db):
        result = {}
        for domain, keys in {
            "meta": ("head_hash", "state"),
            "domestic_meta": ("state",),
            "rhythm_meta": ("state",),
            "books_meta": ("books",),
            "custody_meta": ("items",),
        }.items():
            present = db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (domain,),
            ).fetchone() is not None
            if present:
                records = {k: json.loads(v) for k, v in db.execute(
                    "SELECT key,value FROM " + domain)}
                result[domain] = {k: records[k] for k in keys if k in records}
        return _hash(result)

    def observe(self):
        """Coherent local world perception, not a prompted account of being at home."""
        before = self.subject.verify()
        initial_station = self.subject.embodied.verify()["station"]
        with self.world._open() as db:
            before_state = self._physical_stamp(db)
        frame = self.subject.observe()
        after = self.subject.verify()
        final_station = self.subject.embodied.verify()["station"]
        with self.world._open() as db:
            after_state = self._physical_stamp(db)
        # Receipt-only LOOK operations advance journal revisions but must
        # neither change physical conditions nor alter subject location.
        if (before["world_epoch"], before["minute"],
                initial_station, before_state) != (
                after["world_epoch"], after["minute"],
                final_station, after_state):
            raise RuntimeError("World changed while Doctor perceived the room")
        source = "laboratory-home:observe:" + _hash({
            "epoch": after["world_epoch"], "station": final_station,
            "state": after_state, "text": frame["inner"],
        })
        return self._admit_verified(frame, source, kind="observation")

    @staticmethod
    def _check_action_proof(op, args, event):
        """Prevent a retry from binding an old receipt to a different request."""
        if op == "walk":
            if event.get("kind") != "move" or event.get("after_station") != args.get("station"):
                raise RuntimeError("Mismatched embodied movement receipt")
        elif op == "book":
            action = event.get("action", {})
            expected = {"op": args.get("operation"), "book_id": args.get("book_id")}
            for key in ("direction", "bookmark_id"):
                if key in args:
                    expected[key] = args[key]
            if action != expected:
                raise RuntimeError("Mismatched book operation receipt")
        elif op in ("take_book", "put_book"):
            action = event.get("action", {})
            expected = "take" if op == "take_book" else "put"
            if (action.get("op") != expected or
                    action.get("book_id") != args.get("book_id") or
                    (op == "put_book" and action.get("anchor_id") != args.get("anchor_id"))):
                raise RuntimeError("Mismatched custody receipt")
        elif op == "measure":
            if any(event.get(k) != v for k, v in {
                "instrument": args.get("instrument"),
                "object_id": args.get("object_id"),
                "quantity": args.get("quantity"),
            }.items()):
                raise RuntimeError("Mismatched instrument receipt")
        elif event.get("op") != op or event.get("args") != args:
            raise RuntimeError("Mismatched domestic/rhythm receipt")

    def _intent_path(self) -> Path:
        """Host action reservations live beside, never inside, the world DB."""
        path = getattr(self.world, "path", None)
        if not isinstance(path, (str, Path)):
            raise RuntimeError("A durable Laboratory world path is required")
        return Path(str(path) + ".doctor-action-intents.sqlite3")

    @contextmanager
    def _locked_action_intent(self, op: str, event_id: str, args: dict):
        """Durably reserve an action ID, then serialize its world/brain replay.

        The first committed reservation survives a killed process. A separate
        SQLite IMMEDIATE transaction remains open across the physical action
        and first-person admission, so competing local processes cannot both
        pass the cross-domain preflight. This is host coordination, not memory
        or an independent world authority. All cooperating callers must use
        this bridge; a privileged external Laboratory writer is not covered.
        """
        payload = _stable({"op": op, "args": args})
        with sqlite3.connect(
            self._intent_path(), isolation_level=None, timeout=30,
        ) as db:
            db.execute("PRAGMA busy_timeout=30000")
            db.execute("PRAGMA synchronous=FULL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS doctor_action_intents ("
                "event_id TEXT PRIMARY KEY, request_json TEXT NOT NULL, "
                "status TEXT NOT NULL CHECK(status IN ('pending','complete')))"
            )
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT request_json FROM doctor_action_intents WHERE event_id=?",
                (event_id,),
            ).fetchone()
            if row is not None and row[0] != payload:
                db.execute("ROLLBACK")
                raise RuntimeError("Action event ID already reserved for another Laboratory action domain or request")
            if row is None:
                db.execute(
                    "INSERT INTO doctor_action_intents "
                    "(event_id,request_json,status) VALUES (?,?,'pending')",
                    (event_id, payload),
                )
            db.execute("COMMIT")  # durable BEFORE the Laboratory action
            db.execute("BEGIN IMMEDIATE")  # held across world + brain admission
            try:
                yield
            except BaseException:
                # A rejected pre-world action must not poison startup replay.
                # Keep the journal lock while consulting the original world's
                # durable receipts. Only a PROVEN absence in the exact
                # action's authoritative domain permits removal. A receipt
                # in another domain proves a conflicting ID, not this action.
                # If the world cannot be inspected, fail closed: leave pending.
                try:
                    with self.world._open() as world_db:
                        table = _ACTION_DOMAINS[op]
                        exists = world_db.execute(
                            "SELECT 1 FROM sqlite_master "
                            "WHERE type='table' AND name=?", (table,),
                        ).fetchone() is not None
                        has_receipt = exists and world_db.execute(
                            "SELECT 1 FROM " + table +
                            " WHERE event_id=? LIMIT 1", (event_id,),
                        ).fetchone() is not None
                    if has_receipt:
                        db.execute("ROLLBACK")  # uncertain post-world admission
                    else:
                        db.execute(
                            "DELETE FROM doctor_action_intents "
                            "WHERE event_id=? AND request_json=? AND status='pending'",
                            (event_id, payload),
                        )
                        db.execute("COMMIT")  # no physical event to recover
                except Exception:
                    if db.in_transaction:
                        db.execute("ROLLBACK")  # preserve uncertain intent
                raise
            else:
                db.execute(
                    "UPDATE doctor_action_intents SET status='complete' "
                    "WHERE event_id=? AND request_json=?",
                    (event_id, payload),
                )
                db.execute("COMMIT")

    def pending_action_intents(self) -> tuple[dict, ...]:
        """Host-only durable replay queue, never a subject-facing memory."""
        path = self._intent_path()
        if not path.is_file():
            return ()
        with sqlite3.connect(path, timeout=30) as db:
            rows = db.execute(
                "SELECT event_id,request_json FROM doctor_action_intents "
                "WHERE status='pending' ORDER BY rowid"
            ).fetchall()
        return tuple(
            {"event_id": event_id, **json.loads(request)}
            for event_id, request in rows
        )

    def recover_pending_actions(self) -> tuple[dict, ...]:
        """Replay only previously authorized, durably reserved action IDs."""
        return tuple(
            self.act(item["op"], event_id=item["event_id"], **item["args"])
            for item in self.pending_action_intents()
        )

    def act(self, op: str, *, event_id: str, **args):
        """Bounded physical action plus deduplicated first-person Doctor ingress."""
        if op not in _ACTION_DOMAINS:
            raise PermissionError("Action unavailable through Doctor's subject port")
        if type(event_id) is not str or not _SAFE_ID.fullmatch(event_id):
            raise ValueError("Stable bounded action identity required")
        with self._locked_action_intent(op, event_id, args):
            return self._act_reserved(op, event_id, args)

    def _act_reserved(self, op: str, event_id: str, args: dict):
        """Execute only while the durable cross-process intent lock is held."""
        # Return old *admitted* experiences on a retry even when daily time
        # has changed since the original action. Never regenerate a subjective
        # result from the new world state for an old source receipt.
        with self.world._open() as db:
            table = _ACTION_DOMAINS[op]
            # Action IDs identify host intents across every Laboratory domain,
            # not merely within the table chosen by the current operation.
            # This rejects already-committed cross-domain reuse. The shipping
            # host must still serialize concurrent writers across processes.
            existing_tables = {
                row[0] for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            for other_table in sorted(set(_ACTION_DOMAINS.values()) - {table}):
                if other_table in existing_tables and db.execute(
                    "SELECT 1 FROM " + other_table + " WHERE event_id=? LIMIT 1",
                    (event_id,),
                ).fetchone():
                    raise RuntimeError(
                        "Action event ID already belongs to another Laboratory action domain"
                    )
            column = _EVENT_PAYLOAD_COLUMNS.get(table, "envelope")
            known = db.execute(
                "SELECT " + column + ",event_hash FROM " + table +
                " WHERE event_id=?", (event_id,),
            ).fetchone()
        if known is not None:
            prior, cursor = json.loads(known[0]), known[1]
            if _hash(prior) != cursor:
                raise RuntimeError("Tampered action replay receipt")
            self._check_action_proof(op, args, prior)
            existing = [m for m in self.doctor.brain.store.memories(False)
                        if m["source"] == "laboratory-home:action:" + cursor]
            if existing:
                if len(existing) != 1:
                    raise RuntimeError("Duplicate source admission in Doctor store")
                # For replays return the earlier first-person trace. The
                # recorded out-loud impulse belongs to that historical event.
                spoken = None
                if op == "walk":
                    with self.world._open() as db:
                        row = db.execute(
                            "SELECT envelope FROM domestic_events WHERE event_id=?",
                            ("motion:" + cursor[:32],),
                        ).fetchone()
                    if row:
                        spoken = json.loads(row[0])["subject"]["spoken_aloud"]
                return {"status": "already_admitted", "memory_id": existing[0]["id"],
                        "subject": {"inner": existing[0]["text"],
                                    "spoken_aloud": spoken}}
        result = self.subject.act(op, event_id=event_id, **args)
        # The low-level domain receipt is the evidence authority. It is
        # independently persisted before this Doctor memory admission.
        with self.world._open() as db:
            e, cursor = _row(db, _ACTION_DOMAINS[op], event_id)
            self._check_action_proof(op, args, e)
        source = "laboratory-home:action:" + cursor
        return self._admit_verified(
            result, source, kind="observation",
            source_book_page=(op == "book" and args.get("operation") == "read"),
        )

    def request_cognition(self, *, trigger="laboratory_home"):
        """Actual Doctor cognition is available, not a scripted second policy.

        The caller must decide if and when cognition is scheduled. This alone
        does NOT authorize taking an action based on the returned tendency.
        """
        return self.doctor.cognition(trigger=trigger)
