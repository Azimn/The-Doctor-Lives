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

import hashlib
import json
import os
import tempfile
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Callable, Mapping

from .chassis import HostRecollectionController, PretoriusBrainPort
from .subject_inquiry import SubjectInquiryAuthorizationError
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



def _subject_transport_parts(lines, limit=1000):
    """Frame existing subject text without truncation or new conscious events.

    The pinned donor joins admitted signals with LF. Track only the LFs
    introduced by transport. These offsets are delivery metadata, never
    conscious input or a second autobiographical history.
    """
    parts, inserted, length = [], [], 0
    for line in lines:
        if parts:
            length += 1  # original frame separator, retained
        start = 0
        while start < len(line):
            end = min(start + limit, len(line))
            if end < len(line):
                boundary = line.rfind(" ", start + 1, end + 1)
                if boundary > start and boundary - start >= limit // 2:
                    end = boundary
            part = line[start:end]
            if not part.strip():
                raise ValueError("Subject transport contains a blank fragment")
            if start:
                inserted.append(length)
                length += 1
            parts.append(part)
            length += len(part)
            start = end
    return tuple(parts), tuple(inserted)


def _text_digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _restore_subject_transport(text, manifest):
    if _text_digest(text) != manifest["packed_sha256"]:
        raise ValueError("Subject transport content mismatch")
    offsets = manifest["inserted_lfs"]
    if (not isinstance(offsets, list) or any(type(i) is not int for i in offsets)
            or offsets != sorted(set(offsets))
            or any(i < 0 or i >= len(text) or text[i] != "\n" for i in offsets)):
        raise ValueError("Invalid subject transport boundaries")
    boundaries = set(offsets)
    restored = "".join(ch for i, ch in enumerate(text) if i not in boundaries)
    if _text_digest(restored) != manifest["original_sha256"]:
        raise ValueError("Subject transport reconstruction mismatch")
    return restored


def _write_transport_manifest(path, manifest):
    # Persist only reconstruction metadata before the donor's atomic commit.
    # The existing donor outbox remains the sole delivery text authority.
    fd, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(manifest, out, sort_keys=True)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
        if os.name != "nt":
            directory = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


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
        brain_port: PretoriusBrainPort | None = None,
    ):
        # The six-organ host MUST inject its existing PretoriusBrainPort.
        # Never reopen a competing brain handle or migrate brain state here.
        if brain_port is not None:
            if type(brain_port) is not PretoriusBrainPort:
                raise TypeError("Only the canonical PretoriusBrainPort may be injected")
            if neural_config is not None:
                raise ValueError("Injected brain_port already owns the neural configuration")
            if Path(state_dir).resolve() != brain_port.brain.state_dir.resolve():
                raise ValueError("Durable Ipseity state_dir must equal the canonical brain directory")
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
        self._doctor = (
            brain_port
            if brain_port is not None
            else PretoriusBrainPort(self.state_dir, neural_config=neural_config)
        )
        self._ipseity = DurableIpseityHost(
            self.state_dir / "synthetic_ipseity.sqlite3",
            subject_id=self.SUBJECT_ID,
            epoch_id=epoch_id,
            policy=AccessPolicy(
                capacity=self.MAX_SUBJECT_ITEMS,
                max_batch=self.MAX_SUBJECT_ITEMS,
            ),
        )
        self._epoch_id = epoch_id
        self._transport_path = self.state_dir / (
            "ipseity-output-transport-" + _text_digest(epoch_id) + ".json"
        )
        self._transport_lock = self.state_dir / ".ipseity-output-transport.lock"
        self._render_callback = renderer
        self._renderer = SubjectOnlyRendererPort(self._ipseity, self._render_admitted_text)
        self._recollection_controller: HostRecollectionController | None = None

    def ingest(self, event: Mapping[str, Any]) -> dict[str, Any]:
        """Use existing Doctor source projection; NEVER ingest model replies."""
        return self._doctor.ingest(event)

    def think(self, trigger: str = "host") -> dict[str, Any]:
        """Advance Doctor cognition; caller must keep the audit from renderer."""
        return self._doctor.cognition(trigger)

    def publish_current(self, user_input: str | None = None):
        """Commit real Doctor subject experience into the durable Ipseity gate."""
        source = self._doctor.subject_frame(user_input)
        if self._doctor.brain.store.meta("small-tower:world-binding-v1") is not None:
            from .tower_ipseity import TowerIpseity
            source=TowerIpseity(self._doctor.brain).expression_frame(source)
        return self._publish_typed_subject_frame(source)

    def bind_recollection_controller(
        self, choose_question: Callable[[], str]
    ) -> None:
        """Bind a host-verified selector, never a user/renderer argument."""
        if self._recollection_controller is not None:
            raise SubjectInquiryAuthorizationError(
                "Synthetic Ipseity recollection controller is already bound"
            )
        self._recollection_controller = self._doctor.bind_recollection_controller(
            choose_question
        )

    def publish_recollection(self):
        """Publish only a host-authorized Doctor typed recollection frame.

        This interface does not accept model- or tool-provided question text.
        It does not itself prove that the host's selection was spontaneous.
        """
        if self._recollection_controller is None:
            raise SubjectInquiryAuthorizationError(
                "A trusted host recollection controller must be bound first"
            )
        source = self._recollection_controller.recollect_frame()
        return self._publish_typed_subject_frame(source)

    def _publish_typed_subject_frame(self, frame: SubjectFrame):
        if type(frame) is not SubjectFrame:
            raise TypeError("Cannot bypass Doctor's factory-controlled SubjectFrame")
        from .lab_runtime import _exclusive_lock
        subject_lines = SubjectRendererCapability.read(frame)
        parts, inserted = _subject_transport_parts(subject_lines)
        if len(parts) > self.MAX_SUBJECT_ITEMS:
            raise ValueError("Too many subject items for bounded Ipseity gate")
        with _exclusive_lock(self._transport_lock, "Ipseity output transport"):
            if self._ipseity.pending_count():
                raise RuntimeError("outstanding subject frame must be delivered or reconciled before another publish")
            # A previous failed publication or acknowledged delivery may have
            # left metadata. No pending frame exists, so removal is safe.
            self._transport_path.unlink(missing_ok=True)
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
                    attested=True,
                )
                for offset, line in enumerate(parts)
            )
            if inserted:
                _write_transport_manifest(self._transport_path, {
                    "epoch": self._epoch_id,
                    "tick": next_tick,
                    "last_sequence": current.last_sequence + len(parts),
                    "inserted_lfs": list(inserted),
                    "packed_sha256": _text_digest("\n".join(parts)),
                    "original_sha256": _text_digest("\n".join(subject_lines)),
                })
            # Same pinned donor, same atomic admission/outbox, same callback
            # authorization. Fragmentation affects delivery framing only.
            return self._ipseity.process(next_tick, events, require_drained=True)

    def _render_admitted_text(self, text):
        """The donor invokes this only with checksum-verified outbox text."""
        if self._transport_path.is_symlink():
            raise PermissionError("Symlinked subject transport metadata")
        if self._transport_path.exists():
            manifest = json.loads(self._transport_path.read_text(encoding="utf-8"))
            current = self._ipseity.checkpoint()
            if (manifest["epoch"] != self._epoch_id
                    or manifest["tick"] != current.last_tick
                    or manifest["last_sequence"] != current.last_sequence):
                raise ValueError("Subject transport cursor mismatch")
            text = _restore_subject_transport(text, manifest)
        return self._render_callback(text)

    def deliver_next(self, *, now_ms: int, lease_ms: int = 30_000):
        """Only complete donor-admitted text reaches the existing callback."""
        from .lab_runtime import _exclusive_lock
        with _exclusive_lock(self._transport_lock, "Ipseity output transport"):
            delivery = self._renderer.deliver_next(now_ms=now_ms, lease_ms=lease_ms)
            if not self._ipseity.pending_count():
                self._transport_path.unlink(missing_ok=True)
            return delivery

    def pending_count(self) -> int:
        return self._ipseity.pending_count()

    def close(self) -> None:
        self._ipseity.close()

    def __enter__(self) -> "DoctorSyntheticIpseitySession":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
