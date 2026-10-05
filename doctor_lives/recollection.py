"""P4 reconstructive-memory architecture for UPPB.

This module is intentionally upstream of subjective source monitoring and
awareness. It models protected-evidence references, immutable/versioned memory
trace snapshots, explicit retrieval episodes, and deterministic nonfinal
recollection candidates.

P4 does not create PhenomenalEvent values. P5 owns subjective source
attribution and final phenomenal recollection construction.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from .phenomenology import VividnessBand


_TOKEN_RE = re.compile(r"[A-Za-z0-9']+")


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(text) if token}


def _tuple_of_strings(value: Iterable[str], name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a sequence of strings, not a string")
    try:
        normalized = tuple(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be an iterable of strings") from exc
    if any(not isinstance(item, str) for item in normalized):
        raise TypeError(f"{name} must contain only strings")
    if any(not item.strip() for item in normalized):
        raise ValueError(f"{name} cannot contain blank identifiers")
    return normalized


def _tuple_of_type(value: Iterable[Any], item_type: type, name: str) -> tuple[Any, ...]:
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a sequence")
    try:
        normalized = tuple(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be iterable") from exc
    if any(not isinstance(item, item_type) for item in normalized):
        raise TypeError(f"{name} must contain only {item_type.__name__} values")
    return normalized


def _unit(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be numeric, not bool")
    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be a finite number") from exc
    if not math.isfinite(normalized):
        raise ValueError(f"{name} must be finite")
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return normalized


def _nonnegative_int(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be a non-boolean integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ProtectedEvidenceRef:
    """Reference to truth owned outside UPPB."""

    evidence_id: str
    digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_id, str) or not self.evidence_id.strip():
            raise ValueError("evidence_id is required")
        if not isinstance(self.digest, str) or not self.digest.strip():
            raise ValueError("protected evidence digest is required")


@dataclass(frozen=True)
class TraceDetail:
    """One retained detail in an immutable memory-trace snapshot."""

    detail_id: str
    text: str
    cue_terms: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.detail_id, str) or not self.detail_id.strip():
            raise ValueError("detail_id is required")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("trace detail text is required")
        object.__setattr__(
            self,
            "cue_terms",
            _tuple_of_strings(self.cue_terms, "cue_terms"),
        )


@dataclass(frozen=True)
class MemoryTrace:
    """Immutable/versioned autobiographical trace snapshot."""

    subject_id: str
    version: int
    protected_evidence: tuple[ProtectedEvidenceRef, ...]
    gist: str
    details: tuple[TraceDetail, ...] = ()
    temporal_cues: tuple[str, ...] = ()
    actor_refs: tuple[str, ...] = ()
    object_refs: tuple[str, ...] = ()
    encoding_affect: tuple[str, ...] = ()
    source_cues: tuple[str, ...] = ()
    strength: float = 0.5
    accessibility: float = 0.5
    familiarity: float = 0.5
    rehearsal_count: int = 0
    retrieval_count: int = 0
    competing_trace_ids: tuple[str, ...] = ()
    trace_lineage_id: str = field(init=False)
    trace_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.subject_id, str) or not self.subject_id.strip():
            raise ValueError("subject_id is required")
        _nonnegative_int(self.version, "version")
        protected = _tuple_of_type(
            self.protected_evidence,
            ProtectedEvidenceRef,
            "protected_evidence",
        )
        if not protected:
            raise ValueError("MemoryTrace requires protected evidence")
        object.__setattr__(self, "protected_evidence", protected)
        if not isinstance(self.gist, str) or not self.gist.strip():
            raise ValueError("memory trace gist is required")
        object.__setattr__(
            self,
            "details",
            _tuple_of_type(self.details, TraceDetail, "details"),
        )
        for field_name in (
            "temporal_cues",
            "actor_refs",
            "object_refs",
            "encoding_affect",
            "source_cues",
            "competing_trace_ids",
        ):
            object.__setattr__(
                self,
                field_name,
                _tuple_of_strings(getattr(self, field_name), field_name),
            )
        for field_name in ("strength", "accessibility", "familiarity"):
            object.__setattr__(
                self,
                field_name,
                _unit(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "rehearsal_count",
            _nonnegative_int(self.rehearsal_count, "rehearsal_count"),
        )
        object.__setattr__(
            self,
            "retrieval_count",
            _nonnegative_int(self.retrieval_count, "retrieval_count"),
        )

        lineage_payload = {
            "subject_id": self.subject_id,
            "protected_evidence": [asdict(ref) for ref in self.protected_evidence],
        }
        object.__setattr__(
            self,
            "trace_lineage_id",
            "trace_lineage_" + _stable_sha256(lineage_payload)[:24],
        )
        snapshot_payload = {
            "trace_lineage_id": self.trace_lineage_id,
            "version": self.version,
            "gist": self.gist,
            "details": [asdict(detail) for detail in self.details],
            "temporal_cues": self.temporal_cues,
            "actor_refs": self.actor_refs,
            "object_refs": self.object_refs,
            "encoding_affect": self.encoding_affect,
            "source_cues": self.source_cues,
            "strength": self.strength,
            "accessibility": self.accessibility,
            "familiarity": self.familiarity,
            "rehearsal_count": self.rehearsal_count,
            "retrieval_count": self.retrieval_count,
            "competing_trace_ids": self.competing_trace_ids,
        }
        object.__setattr__(
            self,
            "trace_id",
            "trace_" + _stable_sha256(snapshot_payload)[:24],
        )

    @property
    def protected_evidence_digest(self) -> str:
        return _stable_sha256([asdict(ref) for ref in self.protected_evidence])

    @property
    def snapshot_digest(self) -> str:
        return _stable_sha256(asdict(self))

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


@dataclass(frozen=True)
class RetrievalEpisode:
    """Explicit occurrence identity for one recall attempt."""

    episode_id: str
    subject_id: str
    tick: int
    cue_text: str
    candidate_trace_ids: tuple[str, ...]
    context_refs: tuple[str, ...] = ()
    subject_state_digest: str = ""
    reconstruction_rule_version: str = "uppb-p4-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.episode_id, str) or not self.episode_id.strip():
            raise ValueError("episode_id is required")
        if not isinstance(self.subject_id, str) or not self.subject_id.strip():
            raise ValueError("subject_id is required")
        _nonnegative_int(self.tick, "tick")
        if not isinstance(self.cue_text, str) or not self.cue_text.strip():
            raise ValueError("cue_text is required")
        candidates = _tuple_of_strings(
            self.candidate_trace_ids,
            "candidate_trace_ids",
        )
        if not candidates:
            raise ValueError("retrieval episode requires candidate traces")
        if len(set(candidates)) != len(candidates):
            raise ValueError("candidate_trace_ids cannot contain duplicates")
        object.__setattr__(self, "candidate_trace_ids", candidates)
        object.__setattr__(
            self,
            "context_refs",
            _tuple_of_strings(self.context_refs, "context_refs"),
        )
        if not isinstance(self.subject_state_digest, str):
            raise TypeError("subject_state_digest must be a string")
        if (
            not isinstance(self.reconstruction_rule_version, str)
            or not self.reconstruction_rule_version.strip()
        ):
            raise ValueError("reconstruction_rule_version is required")

    @property
    def cue_fingerprint(self) -> str:
        return _stable_sha256(
            {
                "cue_text": self.cue_text,
                "context_refs": self.context_refs,
                "subject_state_digest": self.subject_state_digest,
            }
        )

    @property
    def occurrence_fingerprint(self) -> str:
        return _stable_sha256(asdict(self))

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


@dataclass(frozen=True)
class ReconstructionConfig:
    max_details: int = 3
    minimum_detail_score: float = 0.0

    def __post_init__(self) -> None:
        if isinstance(self.max_details, bool) or not isinstance(self.max_details, int):
            raise TypeError("max_details must be a non-boolean integer")
        if self.max_details < 0:
            raise ValueError("max_details cannot be negative")
        object.__setattr__(
            self,
            "minimum_detail_score",
            _unit(self.minimum_detail_score, "minimum_detail_score"),
        )


@dataclass(frozen=True)
class RecollectionCandidate:
    """Nonfinal P4 reconstruction with no subjective source attribution."""

    subject_id: str
    retrieval_episode_id: str
    trace_ids: tuple[str, ...]
    protected_evidence_refs: tuple[str, ...]
    reconstructed_scene: str
    included_detail_refs: tuple[str, ...]
    omitted_detail_refs: tuple[str, ...]
    vividness: VividnessBand
    content_confidence: float
    fragmented: bool
    blended: bool
    reconstruction_operations: tuple[str, ...]
    candidate_id: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "subject_id",
            "retrieval_episode_id",
            "reconstructed_scene",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        for field_name in (
            "trace_ids",
            "protected_evidence_refs",
            "included_detail_refs",
            "omitted_detail_refs",
            "reconstruction_operations",
        ):
            object.__setattr__(
                self,
                field_name,
                _tuple_of_strings(getattr(self, field_name), field_name),
            )
        if not self.trace_ids:
            raise ValueError("RecollectionCandidate requires trace_ids")
        if not isinstance(self.vividness, VividnessBand):
            raise TypeError("vividness must be VividnessBand")
        object.__setattr__(
            self,
            "content_confidence",
            _unit(self.content_confidence, "content_confidence"),
        )
        if not isinstance(self.fragmented, bool):
            raise TypeError("fragmented must be bool")
        if not isinstance(self.blended, bool):
            raise TypeError("blended must be bool")

        identity_payload = {
            "subject_id": self.subject_id,
            "retrieval_episode_id": self.retrieval_episode_id,
            "trace_ids": self.trace_ids,
            "protected_evidence_refs": self.protected_evidence_refs,
            "reconstructed_scene": self.reconstructed_scene,
            "included_detail_refs": self.included_detail_refs,
            "omitted_detail_refs": self.omitted_detail_refs,
            "vividness": self.vividness.value,
            "content_confidence": self.content_confidence,
            "fragmented": self.fragmented,
            "blended": self.blended,
            "reconstruction_operations": self.reconstruction_operations,
        }
        object.__setattr__(
            self,
            "candidate_id",
            "recollection_candidate_" + _stable_sha256(identity_payload)[:24],
        )

    @property
    def candidate_digest(self) -> str:
        return _stable_sha256(asdict(self))

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


def _vividness(score: float) -> VividnessBand:
    if score < 0.25:
        return VividnessBand.FAINT
    if score < 0.50:
        return VividnessBand.WEAK
    if score < 0.78:
        return VividnessBand.MODERATE
    return VividnessBand.VIVID


def _detail_score(detail: TraceDetail, cue_tokens: set[str], trace: MemoryTrace) -> float:
    detail_tokens = _tokens(detail.text) | {
        token.lower() for token in detail.cue_terms
    }
    if cue_tokens:
        overlap = len(cue_tokens & detail_tokens) / max(1, len(cue_tokens))
    else:
        overlap = 0.0
    base = (
        0.45 * trace.accessibility
        + 0.30 * trace.strength
        + 0.15 * trace.familiarity
        + 0.10 * overlap
    )
    return max(0.0, min(1.0, base + 0.35 * overlap))


def reconstruct_recollection(
    traces: Iterable[MemoryTrace],
    episode: RetrievalEpisode,
    *,
    config: ReconstructionConfig | None = None,
) -> RecollectionCandidate:
    """Deterministically reconstruct a nonfinal recollection candidate."""

    config = config or ReconstructionConfig()
    trace_values = tuple(traces)
    if not trace_values:
        raise ValueError("reconstruction requires at least one MemoryTrace")
    if any(not isinstance(trace, MemoryTrace) for trace in trace_values):
        raise TypeError("traces must contain only MemoryTrace values")
    if any(trace.subject_id != episode.subject_id for trace in trace_values):
        raise ValueError("all traces must belong to the retrieval subject")

    trace_by_id = {trace.trace_id: trace for trace in trace_values}
    if len(trace_by_id) != len(trace_values):
        raise ValueError("duplicate trace snapshots are not allowed")
    if set(trace_by_id) != set(episode.candidate_trace_ids):
        raise ValueError(
            "retrieval episode candidate_trace_ids must exactly match supplied trace snapshots"
        )

    ordered = tuple(trace_by_id[trace_id] for trace_id in episode.candidate_trace_ids)
    cue_tokens = _tokens(episode.cue_text)

    ranked_details: list[tuple[float, int, TraceDetail]] = []
    for trace_index, trace in enumerate(ordered):
        for detail in trace.details:
            ranked_details.append(
                (_detail_score(detail, cue_tokens, trace), trace_index, detail)
            )
    ranked_details.sort(
        key=lambda item: (item[0], -item[1], item[2].detail_id),
        reverse=True,
    )

    eligible = [
        item
        for item in ranked_details
        if item[0] >= config.minimum_detail_score
    ]
    included = eligible[: config.max_details]
    included_detail_refs = tuple(
        f"{ordered[trace_index].trace_id}:{detail.detail_id}"
        for _, trace_index, detail in included
    )
    all_detail_refs = tuple(
        f"{trace.trace_id}:{detail.detail_id}"
        for trace in ordered
        for detail in trace.details
    )
    included_set = set(included_detail_refs)
    omitted_detail_refs = tuple(
        detail_ref for detail_ref in all_detail_refs if detail_ref not in included_set
    )

    gist_parts = [trace.gist.strip().rstrip(".") for trace in ordered]
    detail_parts = [item[2].text.strip().rstrip(".") for item in included]
    scene_parts = gist_parts + detail_parts
    reconstructed_scene = ". ".join(part for part in scene_parts if part) + "."

    average_quality = sum(
        (trace.strength + trace.accessibility + trace.familiarity) / 3.0
        for trace in ordered
    ) / len(ordered)
    mean_detail_score = (
        sum(item[0] for item in included) / len(included)
        if included
        else average_quality * 0.5
    )
    content_confidence = max(
        0.0,
        min(1.0, 0.6 * average_quality + 0.4 * mean_detail_score),
    )
    vividness = _vividness(
        max(
            0.0,
            min(
                1.0,
                0.45 * average_quality
                + 0.35 * mean_detail_score
                + 0.20 * min(1.0, len(included) / max(1, config.max_details)),
            ),
        )
    )

    operations = ["retrieve_gist"]
    if included:
        operations.append("retrieve_details")
    if omitted_ids:
        operations.append("omit_details")
    if len(ordered) > 1:
        operations.append("blend_traces")

    protected_refs = tuple(
        ref.evidence_id
        for trace in ordered
        for ref in trace.protected_evidence
    )
    return RecollectionCandidate(
        subject_id=episode.subject_id,
        retrieval_episode_id=episode.episode_id,
        trace_ids=tuple(trace.trace_id for trace in ordered),
        protected_evidence_refs=protected_refs,
        reconstructed_scene=reconstructed_scene,
        included_detail_refs=included_detail_refs,
        omitted_detail_refs=omitted_detail_refs,
        vividness=vividness,
        content_confidence=content_confidence,
        fragmented=bool(omitted_detail_refs),
        blended=len(ordered) > 1,
        reconstruction_operations=tuple(operations),
    )
