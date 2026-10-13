"""Fail-closed local conversational entrypoint through Synthetic Ipseity.

The only model invocation is LocalOllamaRenderer behind
DoctorSyntheticIpseitySession's durable SubjectOnlyRendererPort. No internal
brain diagnostics or raw engine data are passed to the inference adapter.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path
import time
from typing import Any, Callable

from .ipseity_integration import DoctorSyntheticIpseitySession
from .local_turn_journal import LocalTurnConflict, LocalTurnJournal
from .speech_emission import (
    SpeechEmissionJournal, SpeechEmissionReceipt, SpeechEmissionUncertain,
    SpeechSinkAck, digest,
)
from synthetic_ipseity import LocalOllamaRenderer


def build_local_renderer(model: str):
    """Reviewed model adapter reused only behind a subject-only delivery port."""
    return LocalOllamaRenderer(model)


class PendingSubjectDelivery(RuntimeError):
    """An earlier first-person frame must be reconciled before new input."""


def local_turn(
    state_dir: str | Path,
    *,
    user_text: str | None = None,
    resume: bool = False,
    model: str = "qwen3:1.5b",
    renderer: Callable[[str], str] | None = None,
    emit: Callable[[str, str], SpeechSinkAck] | None = None,
    neural_config: dict[str, Any] | None = None,
    now_ms: int | None = None,
) -> str:
    """Take exactly one renderer delivery from a persistent real Doctor.

    A new user message is admitted as an external communication percept.
    An interrupted presentation is recovered with resume=True, with NO
    duplicate ingestion. Renderer text is never saved as experience or
    authorized as an action merely because it was generated.
    """
    if type(resume) is not bool:
        raise TypeError("resume must be a boolean")
    if resume == (user_text is not None):
        raise ValueError("Provide either a new user message or --resume")
    if user_text is not None and (
        type(user_text) is not str or not user_text.strip() or
        user_text != user_text.strip() or len(user_text) > 800
    ):
        raise ValueError("User message must be 1 to 800 nonblank characters")
    if now_ms is None:
        now_ms = int(time.time() * 1000)
    if type(now_ms) is not int or now_ms < 0:
        raise ValueError("now_ms must be a nonnegative integer")

    actual_renderer = (
        renderer if renderer is not None else LocalOllamaRenderer(model)
    )
    if emit is not None and not callable(emit):
        raise TypeError("emit must be a trusted output sink")

    record = None
    active_session = None
    active_speech = None

    def recording_renderer(subject: str) -> str:
        # This callback runs BEFORE the organ ACKs subject delivery.
        # Save the exact generated text first so a crash does not force
        # another model inference on recovery.
        if record is None or active_session is None or active_speech is None:
            raise SpeechEmissionUncertain("Missing accountable output context")
        existing = active_speech.prepared_text(record.key)
        if existing is not None:
            return existing
        rendered = actual_renderer(subject)
        brain = active_session._doctor.brain
        return active_speech.prepare(
            record.key, rendered,
            before_tick=brain.store.tick,
            before_neural_tick=brain.neural.tick,
        )
    # Serialize the whole local operation across processes, but commit its
    # recovery record between each separate Doctor/Ipseity write. A crash
    # releases this lease while the intent and admitted experience survive.
    try:
        with LocalTurnJournal(state_dir) as journal, SpeechEmissionJournal(
            state_dir
        ) as speech, DoctorSyntheticIpseitySession(
            state_dir,
            renderer=recording_renderer if emit is not None else actual_renderer,
            neural_config=neural_config,
        ) as session:
            active_session = session
            active_speech = speech
            pending = session.pending_count()
            record = journal.open_turn()
            if resume:
                if record is None and pending == 0:
                    raise PendingSubjectDelivery("No pending subject experience to resume")
            else:
                if record is not None or pending:
                    raise PendingSubjectDelivery(
                        "Previous subject experience is undelivered or uncertain. "
                        "Use --resume before admitting another user message."
                    )
                brain = session._doctor.brain
                record = journal.prepare(
                    user_text, brain.store.digest(),
                    brain.store.tick, brain.neural.tick,
                )

            if record is not None:
                source = "local-conversation:" + record.key
                matched = [
                    memory for memory in session._doctor.brain.store.memories()
                    if memory["source"] == source
                ]
                if len(matched) > 1:
                    raise LocalTurnConflict(
                        "Duplicate Doctor admissions; engineer review required"
                    )
                stage = record.state

                if stage == "prepared":
                    if not matched:
                        if session._doctor.brain.store.digest() != record.before_digest:
                            raise LocalTurnConflict(
                                "Doctor state changed since input preparation; "
                                "do not silently ingest the message twice"
                            )
                        if pending:
                            raise LocalTurnConflict(
                                "Unattributed pending render cannot be linked to input"
                            )
                        # The unique journal key becomes the Doctor source;
                        # the incoming text remains external User communication.
                        session.ingest({
                            "channel": "user",
                            "actor": "User",
                            "source": source,
                            "text": record.message,
                        })
                        matched = [
                            m for m in session._doctor.brain.store.memories()
                            if m["source"] == source
                        ]
                    if len(matched) != 1:
                        raise LocalTurnConflict(
                            "Doctor input admission unverified; stop before rendering"
                        )
                    journal.advance(record.key, "prepared", "admitted")
                    stage = "admitted"

                if not matched:
                    raise LocalTurnConflict(
                        "Previously accepted Doctor input is missing; fail closed"
                    )
                # Doctor's SQL event commit occurs before recurrent stepping
                # and saving. A crash between those writes could leave a
                # memory without its neural consequence. Do not declare the
                # turn recovered merely because a matching memory row exists.
                brain = session._doctor.brain
                speech_already_admitted = (
                    emit is not None
                    and stage == "published"
                    and len([
                        memory for memory in brain.store.memories()
                        if memory["source"] == "local-emission:" + record.key
                    ]) == 1
                    and speech._row(record.key) is not None
                    and speech._row(record.key)[2] == "acknowledged"
                )
                expected_tick = (
                    record.before_tick + 2 if speech_already_admitted
                    else record.before_tick + 1
                )
                if (
                    int(matched[0]["created_tick"]) != record.before_tick + 1
                    or brain.store.tick != expected_tick
                    or brain.neural.tick <= record.before_neural_tick
                ):
                    raise LocalTurnConflict(
                        "Doctor memory/neural checkpoint continuity uncertain; "
                        "do not replay or claim a complete turn"
                    )
                if stage == "admitted":
                    # If the host crashed after outbox commit but before this
                    # journal marker, a pending frame already exists. Never
                    # publish it a second time.
                    if not pending:
                        session.publish_current(user_input=record.message)
                        pending = session.pending_count()
                    if pending != 1:
                        raise LocalTurnConflict(
                            "Expected one verified pending subject frame"
                        )
                    journal.advance(record.key, "admitted", "published")
                    stage = "published"

                if stage != "published":
                    raise LocalTurnConflict("Unexpected local turn stage")
                if not pending and emit is None:
                    # Legacy API returns a generated string without claiming
                    # that text was actually emitted or perceived.
                    journal.advance(record.key, "published", "delivered")
                    raise PendingSubjectDelivery(
                        "Prior renderer delivery already acknowledged; "
                        "response is not replayable, so no duplicate inference"
                    )
                if not pending and speech.prepared_text(record.key) is None:
                    raise SpeechEmissionUncertain(
                        "Renderer ACK preceded durable speech preparation; "
                        "do not invent or regenerate a missing response"
                    )

            if pending:
                delivery = session.deliver_next(now_ms=now_ms)
                if delivery is None:
                    raise PendingSubjectDelivery(
                        "Subject delivery is leased by another worker. Retry "
                        "--resume after the existing lease expires."
                    )
                response = delivery.response
            elif record is not None and emit is not None:
                response = speech.prepared_text(record.key)
            else:
                raise PendingSubjectDelivery("No subject frame remains to deliver")

            if record is not None and emit is not None:
                receipt = speech.emit_once(record.key, emit)
                # The terminal host has now confirmed writing the exact
                # output text. Only THIS event permits a subject-owned
                # recollection of words the host actually emitted.
                source = "local-emission:" + record.key
                matches = [
                    m for m in session._doctor.brain.store.memories()
                    if m["source"] == source
                ]
                if len(matches) > 1:
                    raise SpeechEmissionUncertain("Duplicate speech memory detected")
                if not matches:
                    brain = session._doctor.brain
                    if (brain.store.tick != receipt.before_tick
                        or brain.neural.tick != receipt.before_neural_tick):
                        raise SpeechEmissionUncertain(
                            "Brain moved since speech preparation; "
                            "do not forge an emitted experience"
                        )
                    # Host verified the terminal WRITE, not that a human
                    # read it or that the words were factually correct.
                    statement = "I see my words appear in the conversation: “" + response + "”"
                    from .models import Experience
                    try:
                        event = Experience(
                            text=statement, source=source,
                            kind="confirmed_written_utterance",
                            tags=("host_attested_emission",),
                        )
                    except (ValueError, TypeError):
                        # Malformed or control-like model prose must not
                        # become a fabricated first-person quotation.
                        event = Experience(
                            text="I see that my reply has been written to the conversation.",
                            source=source,
                            kind="confirmed_written_utterance",
                            tags=("host_attested_emission", "content_withheld"),
                        )
                    brain.ingest(event)
                else:
                    brain = session._doctor.brain
                    if (int(matches[0]["created_tick"]) != receipt.before_tick + 1
                        or brain.store.tick != receipt.before_tick + 1
                        or brain.neural.tick <= receipt.before_neural_tick):
                        raise SpeechEmissionUncertain(
                            "Prior emitted-speech memory lacks neural continuity"
                        )
            if record is not None:
                journal.advance(record.key, "published", "delivered")
            return response
    except sqlite3.OperationalError as exc:
        raise LocalTurnConflict(
            "Concurrent local turn or unavailable journal lock; retry safely"
        ) from exc


def _stdout_sink(text: str, delivery_key: str) -> SpeechSinkAck:
    # ACK establishes successful local stream write + flush, not receipt by a
    # remote viewer and not audible speech. Keep the signal engineer-owned.
    sys.stdout.write(text + "\n")
    sys.stdout.flush()
    return SpeechSinkAck(delivery_key, "local-stdout", digest(text))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="doctor-lives-local",
        description="Local Pretorius renderer with mandatory Synthetic Ipseity gate",
    )
    parser.add_argument("--state", type=Path, default=Path("pretorius-state"))
    parser.add_argument("--model", default="qwen3:1.5b")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--say", help="Incoming human message, recorded as perception")
    mode.add_argument("--resume", action="store_true", help="Retry pending subject frame")
    opts = parser.parse_args(argv)
    result = local_turn(
        opts.state,
        user_text=opts.say,
        resume=opts.resume,
        model=opts.model,
        emit=_stdout_sink,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
