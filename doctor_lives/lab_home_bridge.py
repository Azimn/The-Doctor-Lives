"""Opt-in source-verified bridge from the real Doctor to his Laboratory home.

The Laboratory remains the physical authority and the existing PretoriusBrain
remains the ONLY identity/cognition/memory authority. This module is a trusted
host adapter, not a second planner or a renderer. World actions are physical
actions, but an action offer is not evidence the Doctor independently chose it.
"""
from __future__ import annotations

from hashlib import sha256
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
    # Table is selected only from hard-coded trusted operation mapping.
    result = db.execute(
        "SELECT envelope,event_hash FROM " + table + " WHERE event_id=?",
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

    def _admit(self, frame, source, *, kind):
        text = _first_person_frame(frame)
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
        outcome = self.doctor.ingest({
            "channel": "world", "percept": text,
            "kind": kind, "source": source,
            "confidence": 1.0,
        })
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
        return self._admit(frame, source, kind="observation")

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

    def act(self, op: str, *, event_id: str, **args):
        """Bounded physical action plus deduplicated first-person Doctor ingress."""
        if op not in _ACTION_DOMAINS:
            raise PermissionError("Action unavailable through Doctor's subject port")
        if type(event_id) is not str or not _SAFE_ID.fullmatch(event_id):
            raise ValueError("Stable bounded action identity required")
        # Return old *admitted* experiences on a retry even when daily time
        # has changed since the original action. Never regenerate a subjective
        # result from the new world state for an old source receipt.
        with self.world._open() as db:
            known = db.execute(
                "SELECT envelope,event_hash FROM " + _ACTION_DOMAINS[op] +
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
        return self._admit(result, source, kind="observation")

    def request_cognition(self, *, trigger="laboratory_home"):
        """Actual Doctor cognition is available, not a scripted second policy.

        The caller must decide if and when cognition is scheduled. This alone
        does NOT authorize taking an action based on the returned tendency.
        """
        return self.doctor.cognition(trigger=trigger)
