"""Read-only PHASE research snapshot and subject-frame-only conditioning.

The diagnostic tree is ENGINEER PRIVATE. The renderer receives *only*
SubjectFrame text that Pretorius's existing projection boundary admitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import closing

from doctor_lives.cognition import PretoriusBrain
from doctor_lives.models import CognitiveView, SubjectFrame
from .core import CharacterState, Field, AuthoritySnapshot, ConflictSignals, selective_deliberation


@dataclass(frozen=True)
class RenderArms:
    flat: tuple[str, ...]
    hierarchical: tuple[str, ...]
    selective: tuple[str, ...]
    deliberation_required: bool
    reason_count: int


def snapshot_from_brain(brain: PretoriusBrain) -> tuple[CharacterState, AuthoritySnapshot]:
    """No speculative new memories. Private tree records real schema rows only."""
    if not isinstance(brain, PretoriusBrain):
        raise TypeError("expected native PretoriusBrain")
    before = brain.store.digest()
    refs: set[str] = set()
    fields: list[Field] = []
    memories = brain.store.memories()
    refs.update("memory:" + str(m["id"]) for m in memories)
    with closing(brain.store.connect()) as conn:
        rows = conn.execute(
            "SELECT id,claim,evidence,updated_tick FROM self_model WHERE status='active' ORDER BY id"
        ).fetchall()
    for row in rows:
        ref = "hypothesis:" + str(row["id"])
        refs.add(ref)
        # This is a *fallible* self-model claim, NOT new autobiographical truth.
        fields.append(Field(
            "persona.hypothesis." + str(row["id"]),
            str(row["claim"]), (ref,), int(row["updated_tick"]),
        ))
    for item in brain.store.open_commitments():
        ref = "commitment:" + str(item["id"])
        refs.add(ref)
        fields.append(Field(
            "session.commitment." + str(item["id"]),
            str(item["description"]), (ref,), int(item["updated_tick"]),
        ))
    for item in brain.store.open_concerns():
        ref = "concern:" + str(item["id"])
        refs.add(ref)
        fields.append(Field(
            "session.concern." + str(item["id"]),
            str(item["description"]), (ref,), int(item["updated_tick"]),
        ))
    for item in brain.store.relationships():
        ref = "relationship:" + str(item["peer_id"])
        refs.add(ref)
        fields.append(Field(
            "session.relationship." + str(item["peer_id"]),
            str(item["summary"]), (ref,), int(item["updated_tick"]),
        ))
    if brain.store.digest() != before:
        raise AssertionError("shadow state extraction modified native BrainStore")
    state = CharacterState(
        subject_id="pretorius",
        manifest_digest=brain.evidence.manifest_fingerprint,
        base_source_digest=before,
        identity=tuple(brain.identity),
        fields=tuple(sorted(fields, key=lambda f: f.path)),
        tick=brain.store.tick,
    )
    return state, AuthoritySnapshot(
        source_digest=before, manifest_digest=state.manifest_digest,
        authorized_refs=tuple(sorted(refs)),
        world_witnesses=(),  # no actual world-attested updates claimed
    )


def _visible_slices(brain: PretoriusBrain, view: CognitiveView) -> tuple[
    tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]
]:
    """Partition the same authorized SubjectFrame texts by native event order.

    Does not infer source authority from natural-language content and never
    replaces or edits a single subject-native sentence. Uses the exact
    projection order implemented in _subject_frame_from_view; if the count
    changes, it fails rather than mapping secret metadata onto the wrong text.
    """
    frame = brain._subject_frame_from_view(view)
    if not isinstance(frame, SubjectFrame):
        raise AssertionError("native projector did not return SubjectFrame")
    approved = frame.renderer_context()
    memories_n = len(view.experiences)
    feelings_n = sum(1 for k, v in sorted(view.felt_state.items())
                     if brain._felt_subject_text(k, v) is not None)
    impulses_n = int(bool(view.action_tendencies))
    relations_n = len(view.relationships)
    concerns_n = len(view.concerns)
    commitments_n = len(view.commitments)
    expected = memories_n + feelings_n + impulses_n + relations_n + concerns_n + commitments_n
    if len(approved) != expected:
        raise AssertionError("authorized SubjectFrame event layout changed")
    idx = 0
    memories = approved[:memories_n]
    idx += memories_n
    moment = approved[idx:idx+feelings_n+impulses_n]
    idx += feelings_n+impulses_n
    relations = approved[idx:idx+relations_n]
    idx += relations_n
    obligations = approved[idx:]
    return memories, moment, relations, obligations


def build_render_arms(
    brain: PretoriusBrain, view: CognitiveView, signals: ConflictSignals,
) -> RenderArms:
    """Three matched content arms; selective flag alone runs no extra LLM."""
    memory, moment, relationships, obligations = _visible_slices(brain, view)
    original = (*memory, *moment, *relationships, *obligations)
    # PHASE-style topical grouping. Root/persona content is restricted to the
    # EXISTING authorized memories; private persona.claim values are NOT copied.
    # Markers are renderer-control descriptions, never presented as Pretorius's
    # perceived experience or injected into a SubjectFrame.
    layered = (
        "[Previously accessible recollections]", *memory,
        "[Current impressions and impulses]", *moment,
        "[Current relations]", *relationships,
        "[Unresolved concerns and commitments]", *obligations,
    )
    decision = selective_deliberation(signals)
    # The discretionary second pass would be called only by a separate
    # controller; no prompts or hidden protected values are provided here.
    return RenderArms(
        flat=original, hierarchical=layered, selective=layered,
        deliberation_required=decision.required,
        reason_count=len(decision.reasons),
    )
