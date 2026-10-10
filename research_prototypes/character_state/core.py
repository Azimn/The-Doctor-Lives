"""PHASE-style hierarchical state + PersonaForge-inspired selective conflict gate.

RESEARCH ONLY: This is an original adaptation of published *ideas*, not a
vendored copy of either upstream project and not their benchmark reproduction.
It never writes BrainStore or authorizes an LLM to invent an experience.
"""
from __future__ import annotations

from dataclasses import dataclass, replace, asdict
from hashlib import sha256
import json
from typing import Literal


RESISTANCE: dict[str, tuple[int, int, int]] = {
    # (distinct episodes, required high-significance episodes, cooldown ticks)
    "moment": (1, 0, 0),
    "session": (1, 0, 1),
    "persona_moderate": (3, 0, 3),
    "persona_core": (16, 6, 16),
}
PROTOCOL = "pretorius-phase-personaforge-research-v0.1"


def digest(data: object) -> str:
    return sha256(json.dumps(data, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Evidence:
    """Ref is admitted by host, not a model-written or caller-inferred truth."""
    ref: str
    episode_id: str
    tick: int
    significance: Literal["medium", "high"] = "medium"
    witness_sha256: str | None = None

    def __post_init__(self):
        if not self.ref or not self.episode_id or self.tick < 0:
            raise ValueError("incomplete evidence ticket")
        if self.significance not in {"medium", "high"}:
            raise ValueError("invalid significance")


@dataclass(frozen=True)
class AuthoritySnapshot:
    source_digest: str
    manifest_digest: str
    authorized_refs: tuple[str, ...]
    # Trusted world witnesses must be verified *by an external host* first;
    # this struct is not a cryptographic signature or world authority.
    world_witnesses: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        if len(self.source_digest) != 64 or len(self.manifest_digest) != 64:
            raise ValueError("missing pinned source or manifest digest")
        if len(set(self.authorized_refs)) != len(self.authorized_refs):
            raise ValueError("duplicate source refs")
        if len(set(ref for ref, _ in self.world_witnesses)) != len(self.world_witnesses):
            raise ValueError("duplicate world witness refs")

    def verify(self, item: Evidence, *, requires_world: bool) -> None:
        if item.ref not in self.authorized_refs:
            raise ValueError("evidence reference absent from admitted state")
        if requires_world and (item.witness_sha256 is None or
                              (item.ref, item.witness_sha256) not in self.world_witnesses):
            raise ValueError("persona revision requires independently attested world evidence")


@dataclass(frozen=True)
class Field:
    path: str
    value: str
    source_refs: tuple[str, ...]
    last_tick: int

    def __post_init__(self):
        if not self.path or not self.value or not self.source_refs:
            raise ValueError("every field must have provenance and content")


@dataclass(frozen=True)
class CharacterState:
    """Identity root never appears as a patchable field."""
    subject_id: str
    manifest_digest: str
    base_source_digest: str
    identity: tuple[str, ...]
    fields: tuple[Field, ...] = ()
    tick: int = 0
    revision: int = 0

    def __post_init__(self):
        if not self.subject_id or not self.identity:
            raise ValueError("subject and immutable identity required")
        paths = [f.path for f in self.fields]
        if len(set(paths)) != len(paths):
            raise ValueError("duplicate field paths")
        if any(not path.startswith(("persona.", "session.", "moment."))
               for path in paths):
            raise ValueError("only three mutable layers are valid")

    @property
    def fingerprint(self) -> str:
        return digest(asdict(self))

    def get(self, path: str) -> Field | None:
        return next((f for f in self.fields if f.path == path), None)


@dataclass(frozen=True)
class Patch:
    path: str
    new_value: str
    evidence: tuple[Evidence, ...]
    update_tick: int
    resistance: Literal["moment", "session", "persona_moderate", "persona_core"]
    description: str = ""

    def __post_init__(self):
        if not self.new_value.strip() or not self.evidence:
            raise ValueError("patch needs content and witness list")
        if self.resistance not in RESISTANCE:
            raise ValueError("invalid resistance")
        prefix = self.resistance.split("_")[0] + "."
        if not self.path.startswith(prefix):
            raise ValueError("patch resistance does not match field layer")
        if self.update_tick < 0:
            raise ValueError("negative update tick")


@dataclass(frozen=True)
class PatchResult:
    applied: bool
    reason: str
    source_fingerprint: str
    result_fingerprint: str
    state: CharacterState


def apply_patch(
    state: CharacterState, patch: Patch, authority: AuthoritySnapshot,
) -> PatchResult:
    """Locally gated patch, fail closed on unknown facts, never rewrite identity."""
    if state.manifest_digest != authority.manifest_digest or (
        state.base_source_digest != authority.source_digest
    ):
        raise ValueError("canonical manifest or source identity mismatch")
    if patch.path.startswith("identity."):
        raise ValueError("identity is immutable")
    if patch.update_tick < state.tick:
        raise ValueError("retroactive patch")
    previous = state.get(patch.path)
    min_episodes, min_high, cooldown = RESISTANCE[patch.resistance]
    if previous and patch.update_tick - previous.last_tick < cooldown:
        return PatchResult(False, "cooldown", state.fingerprint, state.fingerprint, state)
    refs, episodes = set(), set()
    highs = set()
    for e in patch.evidence:
        authority.verify(e, requires_world=patch.path.startswith("persona."))
        if e.tick > patch.update_tick:
            raise ValueError("evidence from future tick")
        if e.ref in refs:
            raise ValueError("duplicate witness in patch")
        refs.add(e.ref)
        episodes.add(e.episode_id)
        if e.significance == "high":
            highs.add(e.episode_id)
    if len(episodes) < min_episodes or len(highs) < min_high:
        return PatchResult(False, "insufficient_independent_evidence",
                           state.fingerprint, state.fingerprint, state)
    new_field = Field(patch.path, patch.new_value, tuple(sorted(refs)), patch.update_tick)
    updated = tuple(f for f in state.fields if f.path != patch.path) + (new_field,)
    next_state = replace(
        state, fields=tuple(sorted(updated, key=lambda field: field.path)),
        tick=patch.update_tick, revision=state.revision + 1,
    )
    return PatchResult(True, "evidence_admitted", state.fingerprint,
                       next_state.fingerprint, next_state)


@dataclass(frozen=True)
class ConflictSignals:
    """Trusted structural observations, NEVER free-form keyword triggers."""
    source_contradiction: bool = False
    relationship_conflict: bool = False
    value_conflict: bool = False
    commitment_conflict: bool = False
    missing_autobiographical_evidence: bool = False
    high_stakes: bool = False
    known_partner: bool = True

    def __post_init__(self):
        if any(type(getattr(self, key)) is not bool for key in self.__dataclass_fields__):
            raise TypeError("all conflict signals must be typed booleans")


@dataclass(frozen=True)
class Deliberation:
    required: bool
    reasons: tuple[str, ...]
    # This is ONLY a scheduling proposal, never a tool/LLM call.
    requires_authorization: bool = True
    calls_executed: int = 0


def selective_deliberation(signals: ConflictSignals) -> Deliberation:
    flags = (
        ("verified_contradiction", signals.source_contradiction),
        ("relationship_tension", signals.relationship_conflict),
        ("values_in_conflict", signals.value_conflict),
        ("promise_conflict", signals.commitment_conflict),
        ("absent_autobiography", signals.missing_autobiographical_evidence),
        ("high_stakes", signals.high_stakes),
        ("first_encounter", not signals.known_partner),
    )
    reasons = tuple(label for label, active in flags if active)
    return Deliberation(bool(reasons), reasons)


def text_budget_view(state: CharacterState, *, max_chars: int = 1200) -> str:
    """ENGINEER PLANE ONLY: never feed this directly into a subject renderer.

    Renderer-accessible material must come separately from an authorized
    SubjectFrame, not this debug snapshot.
    """
    if max_chars < 64:
        raise ValueError("unreasonably small diagnostic budget")
    parts = [
        f"{field.path}={field.value}"
        for field in sorted(state.fields, key=lambda f: f.path)
    ]
    return "\n".join(parts)[:max_chars]
