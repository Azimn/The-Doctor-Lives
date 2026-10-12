"""Fail-closed local conversational entrypoint through Synthetic Ipseity.

The only model invocation is LocalOllamaRenderer behind
DoctorSyntheticIpseitySession's durable SubjectOnlyRendererPort. No internal
brain diagnostics or raw engine data are passed to the inference adapter.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import time
from typing import Any, Callable

from .ipseity_integration import DoctorSyntheticIpseitySession
from synthetic_ipseity import LocalOllamaRenderer


class PendingSubjectDelivery(RuntimeError):
    """An earlier first-person frame must be reconciled before new input."""


def local_turn(
    state_dir: str | Path,
    *,
    user_text: str | None = None,
    resume: bool = False,
    model: str = "qwen3:1.5b",
    renderer: Callable[[str], str] | None = None,
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
        user_text != user_text.strip() or len(user_text) > 2000
    ):
        raise ValueError("User message must be 1 to 2000 nonblank characters")
    if now_ms is None:
        now_ms = int(time.time() * 1000)
    if type(now_ms) is not int or now_ms < 0:
        raise ValueError("now_ms must be a nonnegative integer")

    actual_renderer = (
        renderer if renderer is not None else LocalOllamaRenderer(model)
    )
    with DoctorSyntheticIpseitySession(
        state_dir, renderer=actual_renderer, neural_config=neural_config
    ) as session:
        outstanding = session.pending_count()
        if resume:
            if outstanding == 0:
                raise PendingSubjectDelivery("No pending subject experience to resume")
        else:
            if outstanding:
                raise PendingSubjectDelivery(
                    "Previous subject experience is undelivered. Use --resume "
                    "before admitting another user message."
                )
            # The communication projector attributes the actual incoming
            # message to a User, never to Pretorius's self-authored thoughts.
            session.ingest({
                "channel": "user",
                "actor": "User",
                "source": "local-conversation",
                "text": user_text,
            })
            session.publish_current(user_input=user_text)

        delivery = session.deliver_next(now_ms=now_ms)
        if delivery is None:
            raise PendingSubjectDelivery(
                "Subject delivery is leased by another worker. Retry --resume "
                "after the existing lease expires."
            )
        return delivery.response


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
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
