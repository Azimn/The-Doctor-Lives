"""Original UPPB P4-P6 reconstruction on canonical Mnemosyne.

A trace is a mnemonic representation, not another event or another memory
authority. A single authenticated source supplies its immutable evidence.
Version ledger and occurrence receipts live in the existing BrainStore.
Only the conscious first-person recollection enters cognition.
"""
from __future__ import annotations
from hashlib import sha256
import json
import re

from .awareness import AwarenessCandidate, AwarenessRouter
from .history import render_memory_for_workspace
from .phenomenology import AwarenessLevel, ObjectiveProvenance
from .recollection import (MemoryTrace, ProtectedEvidenceRef, TraceDetail,
                           RetrievalEpisode, ReconstructionConfig, reconstruct_recollection)
from .source_monitoring import (SourceMonitoringCues, RecollectionFinalizationContext,
                                monitor_recollection_source, finalize_recollection)
from .reconsolidation import (TraceVersionLedger, ReconsolidationContext,
                              reconsolidate_and_record)
from .models import SubjectFrame, SubjectRendererCapability
from .first_person_governance import first_person_line

PREFIX = "mnemosyne:p6:trace:"
RECALL_PREFIX = "mnemosyne:p6:recall:"


def _hash(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode()).hexdigest()


def _root(row):
    # Never treat objective class as a source-monitoring answer. The
    # protected digest preserves original wording and class for audit.
    evidence = ProtectedEvidenceRef(row["id"], _hash({
        k: row[k] for k in ("id", "text", "source", "evidence_class", "external")}))
    text = first_person_line(render_memory_for_workspace(row))
    # Retain epistemic framing in the gist, so an omitted detail cannot
    # turn an inherited, reported or dreamed account into a lived fact.
    if row["evidence_class"] == "lived_runtime_memory" and not row["external"]:
        gist = "I have a recollection of an experience."
    elif row["evidence_class"] == "dreamed_not_lived":
        gist = "I have a recollection of a dream, not a waking event."
    else:
        gist = "I have an account in mind, not necessarily something I lived."
    # Conservative extractive encoding: no invented dates, actors or
    # paraphrased source assertions. Whole reported accounts remain intact.
    pieces = re.split(r"(?<=[.!?])\s+(?=(?:I|My)\s)", text) if gist.startswith("I have a recollection of an experience") else [text]
    details = tuple(TraceDetail("detail-" + str(i), piece,
                     tuple(sorted(set(re.findall(r"[a-z]{4,}", piece.lower())))))
                    for i, piece in enumerate(pieces[:8]))
    return MemoryTrace(subject_id="pretorius", version=0, protected_evidence=(evidence,),
                       gist=gist, details=details, strength=.6, accessibility=.6,
                       familiarity=.5)


def reconstruct_selected(brain, question, recall_id, selected_line):
    """Consume an actual selected endogenous recall and its authorized line.

    The original concern policy and state-bound recollection grant have
    already selected this line. No renderer, user text or raw ID can author
    the question or choose an unrelated memory.
    """
    from contextlib import closing
    from .mnemosyne_pilot import _TRIGGER
    store = brain.store
    with closing(store.connect()) as db:
        decision = db.execute("SELECT selected_action,trigger,state_pressure_json FROM policy_decisions WHERE id=?",
                              (recall_id,)).fetchone()
    if (decision is None or decision["trigger"] != _TRIGGER
            or decision["selected_action"] != "recall"
            or json.loads(decision["state_pressure_json"]).get("question_sha256")
            != sha256(question.encode()).hexdigest()):
        raise PermissionError("Original internally selected recollection required")
    prior = store.meta(RECALL_PREFIX + recall_id)
    if prior is not None:
        saved = json.loads(prior)
        return saved["subject_text"]
    ranked = brain.cognitive_view(query=question, audit=False).experiences
    item = next((x for x in ranked if x.first_person == selected_line), None)
    if item is None:
        raise PermissionError("Selected line is absent from canonical recall")
    rows = {row["id"]: row for row in store.memories_with_classification()}
    row = rows.get(item.record_id)
    if row is None or not row["active"]:
        raise PermissionError("Inactive reconstruction source")
    root = _root(row)
    key = PREFIX + row["id"]
    raw = store.meta(key)
    ledger = TraceVersionLedger.from_json(raw) if raw else TraceVersionLedger()
    if raw:
        trace = ledger.latest(root.trace_lineage_id)
        if ledger.history(root.trace_lineage_id)[0] != root:
            raise PermissionError("Protected source changed since initial encoding")
    else:
        ledger.register_initial(root)
        trace = root
    state_digest = store.digest()
    episode = RetrievalEpisode(recall_id, "pretorius", store.tick, question,
                               (trace.trace_id,), subject_state_digest=state_digest)
    candidate = reconstruct_recollection((trace,), episode,
                  config=ReconstructionConfig(max_details=3, minimum_detail_score=.1))
    # Explicit bounded cue mapping from the recalled wording and the
    # mnemonic representation, not objective provenance or hidden facts.
    words = selected_line.lower()
    cue_terms = set(re.findall(r"[a-z]{4,}", question.lower()))
    overlap = len(cue_terms & set(re.findall(r"[a-z]{4,}", words))) / max(1, len(cue_terms))
    cues = SourceMonitoringCues(
        retrieval_fluency=trace.accessibility, familiarity=trace.familiarity,
        trace_accessibility=trace.accessibility, cue_match=min(1., overlap),
        textual_signature=.8 if any(x in words for x in ("i read", "account", "text", "page")) else .0,
        social_communication_signature=.8 if any(x in words for x in ("told me", "said to me", "message from")) else .0,
        dreamlike_discontinuity=.8 if "dream" in words else .0,
        reconstruction_exposure=.7 if "reconstruct" in words else .0,
    )
    source = monitor_recollection_source(candidate=candidate, cues=cues)
    finalized = finalize_recollection(candidate=candidate, decision=source,
        context=RecollectionFinalizationContext(store.tick, state_digest,
          ObjectiveProvenance(row["evidence_class"], row["source"],
                              bool(row["external"]), float(row["confidence"]),
                              candidate.protected_evidence_refs)))
    awareness = AwarenessRouter().route((AwarenessCandidate(
        finalized.event, salience=.8, change=.5, novelty=.4,
        goal_relevance=.8, persistence=.5),))[0]
    if awareness.event.awareness not in (AwarenessLevel.CONSCIOUS, AwarenessLevel.FOCAL):
        return None
    # Explicit policy-selected recollection is a real rehearsal opportunity.
    # Do not fabricate emotional distress, interference, time disorientation
    # or prediction error simply to demonstrate the optional distortion modes.
    decision, successor = reconsolidate_and_record(ledger=ledger, old_trace=trace,
        candidate=candidate, source_decision=source, finalized_recollection=finalized,
        awareness_decision=awareness, context=ReconsolidationContext(
            reactivation_strength=trace.accessibility, goal_relevance=min(1., overlap),
            explicit_rehearsal=True))
    text = SubjectRendererCapability.read(SubjectFrame.from_events((awareness.event,)))[0]
    receipt = {"source_memory": row["id"], "candidate": candidate.candidate_id,
               "source_decision": source.decision_fingerprint,
               "reconsolidation": decision.decision_fingerprint,
               "parent": trace.trace_id, "successor": successor.trace_id if successor else None,
               "subject_text": text, "world_fact_created": False}
    with store.transaction() as db:
        existing = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        if (existing[0] if existing else None) != raw:
            raise RuntimeError("Concurrent mnemonic version change")
        if db.execute("SELECT 1 FROM meta WHERE key=?", (RECALL_PREFIX + recall_id,)).fetchone():
            raise RuntimeError("Recall occurrence already consumed")
        store.set_meta(key, ledger.stable_json(), db)
        store.set_meta(RECALL_PREFIX + recall_id, json.dumps(receipt, sort_keys=True), db)
        store.bump_state_version(db)
    return text
