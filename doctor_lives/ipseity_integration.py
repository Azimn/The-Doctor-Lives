"""Optional Synthetic Ipseity output boundary for the actual Pretorius brain.

This module is a trusted in-process adapter. It NEVER owns Pretorius identity,
neural state, source authority, autobiographical memory or physical actions.
It routes only Doctor-created typed SubjectFrame through the actual
SyntheticIpseityOrgan durable acquisition/outbox path, then to a callback
that receives one first-person string and nothing else.

A caller that uses some other renderer or directly calls the model can bypass
this path. The eventual standalone host must forbid such paths.
"""
from __future__ import annotations

from pathlib import Path
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Callable, Mapping

from .chassis import PretoriusBrainPort
from .models import SubjectFrame, SubjectRendererCapability

try:
    from synthetic_ipseity import (
        AccessPolicy, Channel, DurableIpseityHost, Kind, Observation,
        SourceSignal, SubjectOnlyRendererPort,
    )
except ImportError as exc:
    raise ImportError(
        "Synthetic Ipseity is an optional version-pinned integration; "
        "install the reviewed synthetic-ipseity v0.9.11 donor revision."
    ) from exc


class DoctorSyntheticIpseitySession:
    """Real-brain, durable subject-only rendering session.

    Calling publish_* means a trusted host authorizes one new presentation
    opportunity. It is not an autonomous cognitive tick or a guarantee that
    the character's underlying state has changed. The existing first-person
    Doctor projector stays the epistemic authority; Synthetic Ipseity adds
    an independent durable admission gate and a renderer-only outbox.
    """

    SUBJECT_ID = "pretorius"
    DEFAULT_EPOCH = "pretorius-lifetime-v1"
    MAX_SUBJECT_ITEMS = 64

    def __init__(
        self,
        state_dir: str | Path,
        *,
        renderer: Callable[[str], str],
        epoch_id: str = DEFAULT_EPOCH,
        neural_config: dict[str, Any] | None = None,
    ):
        if not callable(renderer):
            raise TypeError("renderer must accept subject text")
        try:
            donor_version = version("synthetic-ipseity")
        except PackageNotFoundError as exc:
            raise RuntimeError(
                "Synthetic Ipseity must be installed from the reviewed donor"
            ) from exc
        if donor_version != "0.9.11" or not hasattr(Kind, "PROJECTED_SUBJECT_EVENT"):
            raise RuntimeError(
                "Unreviewed Synthetic Ipseity donor: expected 0.9.11 "
                "with trusted projected-event and drained-outbox capabilities"
            )
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._doctor = PretoriusBrainPort(self.state_dir, neural_config=neural_config)
        self._ipseity = DurableIpseityHost(
            self.state_dir / "synthetic_ipseity.sqlite3",
            subject_id=self.SUBJECT_ID,
            epoch_id=epoch_id,
            policy=AccessPolicy(
                capacity=self.MAX_SUBJECT_ITEMS,
                max_batch=self.MAX_SUBJECT_ITEMS,
            ),
        )
        self._renderer = SubjectOnlyRendererPort(self._ipseity, renderer)
        self._epoch_id = epoch_id

    def ingest(self, event: Mapping[str, Any]) -> dict[str, Any]:
        """Use existing Doctor source projection; NEVER ingest model replies."""
        return self._doctor.ingest(event)

    def think(self, trigger: str = "host") -> dict[str, Any]:
        """Advance Doctor cognition; caller must keep the audit from renderer."""
        return self._doctor.cognition(trigger)

    def publish_current(self, user_input: str | None = None):
        """Commit real Doctor subject experience into the durable Ipseity gate."""
        source = self._doctor.brain.render_request(user_input).subject_frame
        return self._publish_typed_subject_frame(source)

    def publish_recollection(self, question: str):
        """Admit real retrieved first-person memory, not a fabricated User turn."""
        source = self._doctor.brain.subject_recollection(question)
        return self._publish_typed_subject_frame(source)

    def _publish_typed_subject_frame(self, frame: SubjectFrame):
        if type(frame) is not SubjectFrame:
            raise TypeError("Cannot bypass Doctor's factory-controlled SubjectFrame")
        subject_lines = SubjectRendererCapability.read(frame)
        if len(subject_lines) > self.MAX_SUBJECT_ITEMS:
            raise ValueError("Too many subject items for bounded Ipseity gate")
        current = self._ipseity.checkpoint()
        next_tick = current.last_tick + 1
        events = tuple(
            Observation(
                sequence=current.last_sequence + offset + 1,
                tick=next_tick,
                epoch_id=self._epoch_id,
                channel=Channel.COGNITION,
                signal=SourceSignal(
                    subject_id=self.SUBJECT_ID,
                    kind=Kind.PROJECTED_SUBJECT_EVENT,
                    value=line,
                    acquired=True,
                    salience=1.0,
                    source_ref=f"doctor-projection:{current.last_sequence + offset + 1}",
                ),
                # Only the typed Doctor projector can reach this branch.
                attested=True,
            )
            for offset, line in enumerate(subject_lines)
        )
        # A transaction atomically advances Synthetic Ipseity's own checkpoint
        # and queues its first-person text. No raw Doctor data goes to renderer.
        # Guard check and checkpoint mutation occur in the SAME SQLite transaction.
        # Prevent publishing a second subject frame while the first is still
        # pending or leased to a renderer, including after process restart.
        return self._ipseity.process(next_tick, events, require_drained=True)

    def deliver_next(self, *, now_ms: int, lease_ms: int = 30_000):
        """Only the organ's subject text reaches the callback."""
        return self._renderer.deliver_next(now_ms=now_ms, lease_ms=lease_ms)

    def pending_count(self) -> int:
        return self._ipseity.pending_count()

    def close(self) -> None:
        self._ipseity.close()

    def __enter__(self) -> "DoctorSyntheticIpseitySession":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
