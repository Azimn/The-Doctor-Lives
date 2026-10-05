from __future__ import annotations

import dataclasses
import json
from dataclasses import replace
import tempfile
import unittest
from pathlib import Path

from doctor_lives.awareness import AwarenessCandidate, AwarenessRouter
from doctor_lives.phenomenology import (
    CertaintyBand,
    ObjectiveProvenance,
    SubjectiveSourceKind,
)
from doctor_lives.recollection import (
    ContextAssociation,
    MemoryTrace,
    OmissionCause,
    ProtectedEvidenceRef,
    ReconstructionConfig,
    RetrievalEpisode,
    TemporalPrecision,
    TraceDetail,
    TraceDetailState,
    reconstruct_recollection,
)
from doctor_lives.reconsolidation import (
    ReconsolidationContext,
    ReconsolidationDecision,
    ReconsolidationPolicy,
    TraceVersionLedger,
    apply_reconsolidation,
    evaluate_reconsolidation,
    reconsolidate_and_record,
)
from doctor_lives.source_monitoring import (
    RecollectionFinalizationContext,
    SourceMonitoringCues,
    finalize_recollection,
    finalize_recollection_event,
    monitor_recollection_source,
)


class ReconsolidationTests(unittest.TestCase):
    def trace(
        self,
        *,
        label: str = "base",
        strength: float = 0.30,
        accessibility: float = 0.30,
        familiarity: float = 0.30,
    ) -> MemoryTrace:
        return MemoryTrace(
            subject_id="subject-reconsolidation",
            version=0,
            protected_evidence=(
                ProtectedEvidenceRef(
                    evidence_id=f"evidence:{label}",
                    digest=f"sha256:{label}",
                ),
            ),
            gist=f"The {label} demonstration occurred in the laboratory",
            details=(
                TraceDetail(
                    detail_id=f"detail:{label}",
                    text=f"Henry stood beside the {label} apparatus",
                    cue_terms=("henry", "apparatus"),
                ),
            ),
            source_cues=("visual-richness",),
            strength=strength,
            accessibility=accessibility,
            familiarity=familiarity,
        )

    def trace_with_two_details(self) -> MemoryTrace:
        return MemoryTrace(
            subject_id="subject-reconsolidation",
            version=0,
            protected_evidence=(
                ProtectedEvidenceRef(
                    evidence_id="evidence:detail-drift",
                    digest="sha256:detail-drift",
                ),
            ),
            gist="The demonstration occurred in the laboratory",
            details=(
                TraceDetail(
                    detail_id="detail:henry",
                    text="Henry stood beside the apparatus",
                    cue_terms=("henry", "apparatus"),
                ),
                TraceDetail(
                    detail_id="detail:notebook",
                    text="A blue notebook rested on the side table",
                    cue_terms=("blue", "notebook", "table"),
                ),
            ),
            strength=0.60,
            accessibility=0.60,
            familiarity=0.60,
        )

    def finalized_from_candidate(self, candidate):
        decision = monitor_recollection_source(
            candidate=candidate,
            cues=self.source_cues(),
        )
        finalized = finalize_recollection(
            candidate=candidate,
            decision=decision,
            context=RecollectionFinalizationContext(
                tick=80,
                source_state_digest="sha256:p6b-finalization",
                objective_provenance=ObjectiveProvenance(
                    evidence_class="lived_runtime_memory",
                    source="world",
                    record_ids=candidate.protected_evidence_refs,
                ),
            ),
        )
        awareness = AwarenessRouter().route(
            (
                AwarenessCandidate(
                    event=finalized.event,
                    salience=1.0,
                    change=1.0,
                    novelty=1.0,
                    goal_relevance=1.0,
                    persistence=1.0,
                ),
            )
        )[0]
        return decision, finalized, awareness

    def source_cues(self) -> SourceMonitoringCues:
        return SourceMonitoringCues(
            retrieval_fluency=0.90,
            perceptual_richness=0.95,
            temporal_coherence=0.90,
            spatial_coherence=0.90,
            contextual_compatibility=0.90,
            familiarity=0.85,
            trace_accessibility=0.85,
            rehearsal_frequency=0.40,
            cue_match=0.90,
        )

    def reconstruct(
        self,
        trace: MemoryTrace,
        *,
        episode_id: str,
        cue_text: str = "Henry apparatus",
        config: ReconstructionConfig | None = None,
    ):
        episode = RetrievalEpisode(
            episode_id=episode_id,
            subject_id=trace.subject_id,
            tick=40 + trace.version,
            cue_text=cue_text,
            candidate_trace_ids=(trace.trace_id,),
            context_refs=("room:laboratory",),
            subject_state_digest=f"sha256:state:{trace.version}",
        )
        return reconstruct_recollection(
            (trace,),
            episode,
            config=config or ReconstructionConfig(max_details=1),
        )

    def final_event(
        self,
        trace: MemoryTrace,
        *,
        episode_id: str,
        cues: SourceMonitoringCues | None = None,
        content_certainty: CertaintyBand = CertaintyBand.MODERATE,
        focal: bool = True,
        evidence_class: str = "lived_runtime_memory",
    ):
        candidate = self.reconstruct(trace, episode_id=episode_id)
        decision = monitor_recollection_source(
            candidate=candidate,
            cues=cues or self.source_cues(),
        )
        finalized = finalize_recollection(
            candidate=candidate,
            decision=decision,
            context=RecollectionFinalizationContext(
                tick=60 + trace.version,
                source_state_digest=f"sha256:p5:{trace.version}",
                objective_provenance=ObjectiveProvenance(
                    evidence_class=evidence_class,
                    source="world",
                    record_ids=candidate.protected_evidence_refs,
                ),
                subjective_content_certainty=content_certainty,
            ),
        )
        awareness_candidate = AwarenessCandidate(
            event=finalized.event,
            salience=1.0 if focal else 0.0,
            change=1.0 if focal else 0.0,
            novelty=1.0 if focal else 0.0,
            goal_relevance=1.0 if focal else 0.0,
            conflict=0.7 if focal else 0.0,
            persistence=1.0 if focal else 0.0,
            habituation=0.0,
        )
        awareness_decision = AwarenessRouter().route((awareness_candidate,))[0]
        return candidate, decision, finalized, awareness_decision

    def eligible_context(self, *, enabled: bool = True) -> ReconsolidationContext:
        return ReconsolidationContext(
            enabled=enabled,
            reactivation_strength=0.95,
            prediction_error=0.65,
            emotional_activation=0.55,
            goal_relevance=0.65,
            explicit_rehearsal=True,
        )

    def test_decision_is_factory_controlled(self):
        with self.assertRaises(TypeError):
            ReconsolidationDecision()

    def test_latent_recollection_does_not_reconsolidate(self):
        trace = self.trace()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        original_digest = trace.snapshot_digest
        candidate, source_decision, finalized, latent_event = self.final_event(
            trace,
            episode_id="episode:latent",
            focal=False,
        )

        decision, successor = reconsolidate_and_record(
            ledger=ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=latent_event,
            context=self.eligible_context(),
        )

        self.assertFalse(decision.eligible)
        self.assertIn(
            "recollection_not_consciously_accessible",
            decision.reason_codes,
        )
        self.assertIsNone(successor)
        self.assertEqual(trace.snapshot_digest, original_digest)
        self.assertEqual(len(ledger.history(trace.trace_lineage_id)), 1)

    def test_preconscious_recollection_does_not_reconsolidate(self):
        trace = self.trace(label="preconscious")
        candidate = self.reconstruct(trace, episode_id="episode:preconscious")
        source_decision = monitor_recollection_source(
            candidate=candidate,
            cues=self.source_cues(),
        )
        finalized = finalize_recollection(
            candidate=candidate,
            decision=source_decision,
            context=RecollectionFinalizationContext(
                tick=61,
                source_state_digest="sha256:p5:preconscious",
                objective_provenance=ObjectiveProvenance(
                    evidence_class="test",
                    source="audit",
                    record_ids=candidate.protected_evidence_refs,
                ),
            ),
        )
        awareness_decision = AwarenessRouter().route(
            (
                AwarenessCandidate(
                    event=finalized.event,
                    salience=1.0,
                    change=0.0,
                    novelty=0.0,
                    goal_relevance=0.0,
                    conflict=0.0,
                    persistence=0.0,
                    habituation=0.0,
                ),
            )
        )[0]
        self.assertEqual(
            awareness_decision.awareness.value,
            "preconscious",
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness_decision,
            context=self.eligible_context(),
        )
        self.assertFalse(decision.eligible)
        self.assertIn(
            "recollection_not_consciously_accessible",
            decision.reason_codes,
        )

    def test_matched_reconsolidation_lesion_holds_upstream_chain_fixed(self):
        trace = self.trace(label="matched-lesion")
        candidate, source_decision, finalized, awareness_decision = self.final_event(
            trace,
            episode_id="episode:matched-lesion",
        )
        original_digest = trace.snapshot_digest

        disabled_ledger = TraceVersionLedger()
        disabled_ledger.register_initial(trace)
        disabled_decision, disabled_successor = reconsolidate_and_record(
            ledger=disabled_ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness_decision,
            context=self.eligible_context(enabled=False),
        )

        enabled_ledger = TraceVersionLedger()
        enabled_ledger.register_initial(trace)
        enabled_decision, enabled_successor = reconsolidate_and_record(
            ledger=enabled_ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness_decision,
            context=self.eligible_context(enabled=True),
        )

        self.assertEqual(trace.snapshot_digest, original_digest)
        self.assertEqual(
            disabled_decision.candidate_digest,
            enabled_decision.candidate_digest,
        )
        self.assertEqual(
            disabled_decision.source_decision_fingerprint,
            enabled_decision.source_decision_fingerprint,
        )
        self.assertEqual(
            disabled_decision.recollection_event_id,
            enabled_decision.recollection_event_id,
        )
        self.assertFalse(disabled_decision.eligible)
        self.assertIsNone(disabled_successor)
        self.assertEqual(len(disabled_ledger.history(trace.trace_lineage_id)), 1)

        self.assertTrue(enabled_decision.eligible)
        self.assertIsNotNone(enabled_successor)
        assert enabled_successor is not None
        self.assertEqual(enabled_successor.parent_trace_id, trace.trace_id)
        self.assertEqual(
            enabled_successor.protected_evidence,
            trace.protected_evidence,
        )
        self.assertEqual(len(enabled_ledger.history(trace.trace_lineage_id)), 2)

    def test_focal_recollection_creates_immutable_successor(self):
        trace = self.trace()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        original_digest = trace.snapshot_digest
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:focal",
        )

        decision, successor = reconsolidate_and_record(
            ledger=ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )

        self.assertTrue(decision.eligible)
        self.assertIsNotNone(successor)
        assert successor is not None
        self.assertEqual(trace.snapshot_digest, original_digest)
        self.assertEqual(successor.version, trace.version + 1)
        self.assertEqual(successor.parent_trace_id, trace.trace_id)
        self.assertEqual(successor.trace_lineage_id, trace.trace_lineage_id)
        self.assertNotEqual(successor.trace_id, trace.trace_id)
        self.assertEqual(successor.protected_evidence, trace.protected_evidence)
        self.assertEqual(successor.gist, trace.gist)
        self.assertEqual(successor.details, trace.details)
        self.assertEqual(successor.source_cues, trace.source_cues)
        self.assertEqual(successor.retrieval_count, trace.retrieval_count + 1)
        self.assertEqual(successor.rehearsal_count, trace.rehearsal_count + 1)
        self.assertEqual(
            successor.reconsolidation_decision_fingerprint,
            decision.decision_fingerprint,
        )
        self.assertEqual(
            decision.finalized_recollection_fingerprint,
            finalized.finalization_fingerprint,
        )
        self.assertEqual(successor.reconsolidation_event_id, event.event.event_id)
        self.assertEqual(len(ledger.history(trace.trace_lineage_id)), 2)

    def test_misattribution_without_reconsolidation_does_not_rewrite_trace(self):
        trace = self.trace()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:misattributed",
            cues=self.source_cues(),
            evidence_class="reconstructed_preawakening_memory",
        )
        self.assertIs(source_decision.selected_source, SubjectiveSourceKind.LIVED)
        self.assertEqual(
            event.event.objective_provenance.evidence_class,
            "reconstructed_preawakening_memory",
        )
        self.assertNotEqual(
            event.event.objective_provenance.evidence_class,
            source_decision.selected_source.value,
        )
        original_digest = trace.snapshot_digest

        decision, successor = reconsolidate_and_record(
            ledger=ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(enabled=False),
        )

        self.assertFalse(decision.eligible)
        self.assertIn("reconsolidation_disabled", decision.reason_codes)
        self.assertIsNone(successor)
        self.assertEqual(trace.snapshot_digest, original_digest)
        self.assertEqual(len(ledger.history(trace.trace_lineage_id)), 1)

    def test_matched_reconsolidation_lesion_changes_only_enabled_condition(self):
        trace = self.trace(label="matched-lesion")
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:matched-lesion",
        )
        original_digest = trace.snapshot_digest

        disabled_ledger = TraceVersionLedger()
        disabled_ledger.register_initial(trace)
        disabled_decision, disabled_successor = reconsolidate_and_record(
            ledger=disabled_ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(enabled=False),
        )

        enabled_ledger = TraceVersionLedger()
        enabled_ledger.register_initial(trace)
        enabled_decision, enabled_successor = reconsolidate_and_record(
            ledger=enabled_ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(enabled=True),
        )

        self.assertFalse(disabled_decision.eligible)
        self.assertIsNone(disabled_successor)
        self.assertTrue(enabled_decision.eligible)
        self.assertIsNotNone(enabled_successor)
        self.assertEqual(trace.snapshot_digest, original_digest)
        self.assertEqual(len(disabled_ledger.history(trace.trace_lineage_id)), 1)
        self.assertEqual(len(enabled_ledger.history(trace.trace_lineage_id)), 2)

    def test_reconsolidation_decision_binds_exact_awareness_state(self):
        trace = self.trace(label="awareness-binding")
        candidate, source_decision, finalized, latent_event = self.final_event(
            trace,
            episode_id="episode:awareness-binding",
            focal=False,
        )
        focal_decision = AwarenessRouter().route(
            (
                AwarenessCandidate(
                    event=latent_event.event,
                    salience=1.0,
                    change=1.0,
                    novelty=1.0,
                    goal_relevance=1.0,
                    persistence=1.0,
                ),
            )
        )[0]
        self.assertEqual(
            latent_event.event.event_id,
            focal_decision.event.event_id,
        )

        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=focal_decision,
            context=self.eligible_context(),
        )
        self.assertTrue(decision.eligible)
        self.assertIs(
            decision.recollection_awareness,
            focal_decision.awareness,
        )

        with self.assertRaises(ValueError):
            apply_reconsolidation(
                old_trace=trace,
                candidate=candidate,
                source_decision=source_decision,
                finalized_recollection=finalized,
                awareness_decision=latent_event,
                decision=decision,
            )

    def test_p6_rejects_real_p3_decision_over_forged_recollection_content(self):
        trace = self.trace(label="forged-p5-content")
        candidate, source_decision, finalized, _ = self.final_event(
            trace,
            episode_id="episode:forged-p5-content",
            focal=False,
        )

        forged_event = replace(
            finalized.event,
            canonical_first_person=(
                "I can call to mind the following: "
                "Henry left before the demonstration."
            ),
        )
        self.assertNotEqual(
            forged_event.canonical_first_person,
            finalized.event.canonical_first_person,
        )
        forged_awareness = AwarenessRouter().route(
            (
                AwarenessCandidate(
                    event=forged_event,
                    salience=1.0,
                    change=1.0,
                    novelty=1.0,
                    goal_relevance=1.0,
                    persistence=1.0,
                ),
            )
        )[0]

        with self.assertRaises(ValueError):
            evaluate_reconsolidation(
                old_trace=trace,
                candidate=candidate,
                source_decision=source_decision,
                finalized_recollection=finalized,
                awareness_decision=forged_awareness,
                context=self.eligible_context(),
            )

    def test_p6_rejects_routed_event_from_different_p5_finalization_context(self):
        trace = self.trace(label="altered-p5-context")
        candidate = self.reconstruct(
            trace,
            episode_id="episode:altered-p5-context",
        )
        source_decision = monitor_recollection_source(
            candidate=candidate,
            cues=self.source_cues(),
        )
        canonical = finalize_recollection(
            candidate=candidate,
            decision=source_decision,
            context=RecollectionFinalizationContext(
                tick=62,
                source_state_digest="sha256:canonical-p5",
                objective_provenance=ObjectiveProvenance(
                    evidence_class="reconstructed_preawakening_memory",
                    source="archive-a",
                    record_ids=candidate.protected_evidence_refs,
                ),
            ),
        )
        altered = finalize_recollection(
            candidate=candidate,
            decision=source_decision,
            context=RecollectionFinalizationContext(
                tick=63,
                source_state_digest="sha256:altered-p5",
                objective_provenance=ObjectiveProvenance(
                    evidence_class="reconstructed_preawakening_memory",
                    source="archive-b",
                    record_ids=candidate.protected_evidence_refs,
                ),
            ),
        )
        self.assertEqual(canonical.candidate_id, altered.candidate_id)
        self.assertEqual(canonical.candidate_digest, altered.candidate_digest)
        self.assertEqual(
            canonical.source_decision_fingerprint,
            altered.source_decision_fingerprint,
        )
        self.assertNotEqual(
            canonical.finalization_fingerprint,
            altered.finalization_fingerprint,
        )

        altered_awareness = AwarenessRouter().route(
            (
                AwarenessCandidate(
                    event=altered.event,
                    salience=1.0,
                    change=1.0,
                    novelty=1.0,
                    goal_relevance=1.0,
                    persistence=1.0,
                ),
            )
        )[0]

        with self.assertRaises(ValueError):
            evaluate_reconsolidation(
                old_trace=trace,
                candidate=candidate,
                source_decision=source_decision,
                finalized_recollection=canonical,
                awareness_decision=altered_awareness,
                context=self.eligible_context(),
            )

    def test_p6_rejects_bare_phenomenal_event_in_place_of_p3_decision(self):
        trace = self.trace(label="bare-event")
        candidate, source_decision, finalized, awareness_decision = self.final_event(
            trace,
            episode_id="episode:bare-event",
        )
        with self.assertRaises(TypeError):
            evaluate_reconsolidation(
                old_trace=trace,
                candidate=candidate,
                source_decision=source_decision,
                finalized_recollection=finalized,
                awareness_decision=awareness_decision.event,  # type: ignore[arg-type]
                context=self.eligible_context(),
            )

    def test_initial_p6_ignores_non_neutral_content_certainty(self):
        trace = self.trace()
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:certainty",
            content_certainty=CertaintyBand.VERY_HIGH,
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        self.assertFalse(decision.eligible)
        self.assertIn(
            "nonneutral_content_certainty_not_grounded_for_p6",
            decision.reason_codes,
        )

    def test_initial_p6_cannot_enable_blended_reconsolidation(self):
        first = self.trace(label="blend-first")
        second = self.trace(label="blend-second")
        episode = RetrievalEpisode(
            episode_id="episode:blend",
            subject_id=first.subject_id,
            tick=50,
            cue_text="Henry apparatus",
            candidate_trace_ids=(first.trace_id, second.trace_id),
            subject_state_digest="sha256:blend",
        )
        candidate = reconstruct_recollection(
            (first, second),
            episode,
            config=ReconstructionConfig(max_details=2),
        )
        source_decision = monitor_recollection_source(
            candidate=candidate,
            cues=self.source_cues(),
        )
        finalized = finalize_recollection(
            candidate=candidate,
            decision=source_decision,
            context=RecollectionFinalizationContext(
                tick=51,
                source_state_digest="sha256:blend",
                objective_provenance=ObjectiveProvenance(
                    evidence_class="test",
                    source="audit",
                    record_ids=candidate.protected_evidence_refs,
                ),
            ),
        )
        focal_decision = AwarenessRouter().route(
            (
                AwarenessCandidate(
                    event=finalized.event,
                    salience=1.0,
                    change=1.0,
                    novelty=1.0,
                    goal_relevance=1.0,
                    persistence=1.0,
                ),
            )
        )[0]
        decision = evaluate_reconsolidation(
            old_trace=first,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=focal_decision,
            context=self.eligible_context(),
        )
        self.assertFalse(decision.eligible)
        self.assertIn("blended_recollection_not_enabled", decision.reason_codes)
        self.assertIn(
            "multiple_trace_reconsolidation_not_enabled",
            decision.reason_codes,
        )

    def test_policy_thresholds_cannot_be_configured_to_zero(self):
        with self.assertRaises(ValueError):
            ReconsolidationPolicy(min_reactivation=0.0)
        with self.assertRaises(ValueError):
            ReconsolidationPolicy(min_prediction_error=0.0)
        with self.assertRaises(ValueError):
            ReconsolidationPolicy(max_strength_delta=0.0)

    def test_no_destabilizing_signal_means_no_reconsolidation(self):
        trace = self.trace()
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:no-destabilizer",
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=ReconsolidationContext(
                reactivation_strength=0.90,
                prediction_error=0.0,
                emotional_activation=0.0,
                goal_relevance=0.8,
                explicit_rehearsal=False,
            ),
        )
        self.assertFalse(decision.eligible)
        self.assertIn(
            "no_destabilizing_or_rehearsal_signal",
            decision.reason_codes,
        )

    def test_reconsolidation_requires_exact_p4_p5_event_chain(self):
        first = self.trace(label="first")
        second = self.trace(label="second")
        first_candidate, first_source, first_finalized, first_event = self.final_event(
            first,
            episode_id="episode:first",
        )
        second_candidate, _, _, _ = self.final_event(
            second,
            episode_id="episode:second",
        )
        with self.assertRaises(ValueError):
            evaluate_reconsolidation(
                old_trace=first,
                candidate=second_candidate,
                source_decision=first_source,
                finalized_recollection=first_finalized,
                awareness_decision=first_event,
                context=self.eligible_context(),
            )
        self.assertNotEqual(first_candidate.candidate_id, second_candidate.candidate_id)

    def test_every_successor_change_has_explicit_operation(self):
        trace = self.trace()
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:operations",
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        successor = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            decision=decision,
        )
        assert successor is not None

        operation_fields = {op.field_name for op in decision.operations}
        changed_psychological_fields = {
            name
            for name in (
                "strength",
                "accessibility",
                "familiarity",
                "retrieval_count",
                "rehearsal_count",
            )
            if getattr(trace, name) != getattr(successor, name)
        }
        self.assertEqual(operation_fields, changed_psychological_fields)
        self.assertEqual(successor.gist, trace.gist)
        self.assertEqual(successor.details, trace.details)
        self.assertEqual(successor.protected_evidence, trace.protected_evidence)

    def test_successor_changes_later_p4_recall_without_changing_protected_truth(self):
        trace = self.trace(
            label="threshold",
            strength=0.30,
            accessibility=0.30,
            familiarity=0.30,
        )
        before = self.reconstruct(
            trace,
            episode_id="episode:before",
            cue_text="unrelated cue",
            config=ReconstructionConfig(
                max_details=1,
                minimum_detail_score=0.28,
            ),
        )
        self.assertEqual(before.included_detail_refs, ())

        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:reactivate",
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        successor = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            decision=decision,
        )
        assert successor is not None

        after = self.reconstruct(
            successor,
            episode_id="episode:after",
            cue_text="unrelated cue",
            config=ReconstructionConfig(
                max_details=1,
                minimum_detail_score=0.28,
            ),
        )
        self.assertEqual(trace.protected_evidence, successor.protected_evidence)
        self.assertEqual(trace.gist, successor.gist)
        self.assertEqual(trace.details, successor.details)
        self.assertEqual(len(after.included_detail_refs), 1)
        self.assertNotEqual(before.reconstructed_scene, after.reconstructed_scene)

    def test_source_attribution_does_not_change_update_rule(self):
        trace = self.trace()
        candidate = self.reconstruct(trace, episode_id="episode:sources")
        lived = monitor_recollection_source(
            candidate=candidate,
            cues=self.source_cues(),
        )
        read = monitor_recollection_source(
            candidate=candidate,
            cues=SourceMonitoringCues(
                retrieval_fluency=0.75,
                perceptual_richness=0.10,
                temporal_coherence=0.70,
                spatial_coherence=0.65,
                contextual_compatibility=0.80,
                familiarity=0.85,
                trace_accessibility=0.70,
                rehearsal_frequency=0.70,
                reconstruction_exposure=0.20,
                cue_match=0.80,
                textual_signature=0.95,
            ),
        )
        self.assertIs(lived.selected_source, SubjectiveSourceKind.LIVED)
        self.assertIs(read.selected_source, SubjectiveSourceKind.READ)

        def event_for(source_decision):
            finalized = finalize_recollection(
                candidate=candidate,
                decision=source_decision,
                context=RecollectionFinalizationContext(
                    tick=60,
                    source_state_digest="sha256:p5:sources",
                    objective_provenance=ObjectiveProvenance(
                        evidence_class="test",
                        source="audit",
                        record_ids=candidate.protected_evidence_refs,
                    ),
                ),
            )
            awareness_decision = AwarenessRouter().route(
                (
                    AwarenessCandidate(
                        event=finalized.event,
                        salience=1.0,
                        change=1.0,
                        novelty=1.0,
                        goal_relevance=1.0,
                        persistence=1.0,
                    ),
                )
            )[0]
            return finalized, awareness_decision

        lived_finalized, lived_event = event_for(lived)
        read_finalized, read_event = event_for(read)
        lived_decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=lived,
            finalized_recollection=lived_finalized,
            awareness_decision=lived_event,
            context=self.eligible_context(),
        )
        read_decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=read,
            finalized_recollection=read_finalized,
            awareness_decision=read_event,
            context=self.eligible_context(),
        )

        self.assertEqual(lived_decision.operations, read_decision.operations)
        self.assertEqual(
            lived_decision.eligibility_strength,
            read_decision.eligibility_strength,
        )

    def test_detail_state_defaults_preserve_stable_semantic_detail(self):
        trace = self.trace_with_two_details()
        self.assertEqual(
            tuple(state.detail_id for state in trace.detail_states),
            tuple(detail.detail_id for detail in trace.details),
        )
        for state in trace.detail_states:
            self.assertEqual(state.retention, 1.0)
            self.assertEqual(state.accessibility, 1.0)
            self.assertEqual(state.temporal_confidence, 1.0)
            self.assertEqual(state.association_strength, 1.0)
            self.assertIsNone(state.parent_state_fingerprint)

    def test_p6b_default_policy_produces_real_weak_cue_degradation(self):
        trace = self.trace_with_two_details()
        before = self.reconstruct(
            trace,
            episode_id="episode:p6b-default-before",
            cue_text="laboratory",
            config=ReconstructionConfig(
                max_details=2,
                minimum_detail_score=0.537,
            ),
        )
        self.assertIn(
            f"{trace.trace_id}:detail:notebook",
            before.included_detail_refs,
        )

        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-default-reactivation",
            cue_text="Henry apparatus",
            config=ReconstructionConfig(max_details=1),
        )
        source_decision, finalized, awareness = self.finalized_from_candidate(
            candidate
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=True,
                interference_strength=1.0,
            ),
        )
        successor = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            decision=decision,
        )
        assert successor is not None

        after = self.reconstruct(
            successor,
            episode_id="episode:p6b-default-after",
            cue_text="laboratory",
            config=ReconstructionConfig(
                max_details=2,
                minimum_detail_score=0.537,
            ),
        )
        self.assertIn(
            f"{successor.trace_id}:detail:notebook",
            after.omitted_detail_refs,
        )
        self.assertEqual(successor.details, trace.details)

    def test_p6b_detail_drift_weakens_only_omitted_detail_state(self):
        trace = self.trace_with_two_details()
        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-weakening",
            cue_text="Henry apparatus",
            config=ReconstructionConfig(max_details=1),
        )
        self.assertIn(
            f"{trace.trace_id}:detail:notebook",
            candidate.omitted_detail_refs,
        )
        self.assertIn(
            f"{trace.trace_id}:detail:henry",
            candidate.included_detail_refs,
        )
        source_decision, finalized, awareness = self.finalized_from_candidate(
            candidate
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=True,
                interference_strength=1.0,
            ),
            policy=ReconsolidationPolicy(
                max_detail_accessibility_loss=0.20,
            ),
        )
        self.assertTrue(decision.eligible)
        self.assertEqual(len(decision.detail_operations), 1)
        detail_op = decision.detail_operations[0]
        self.assertEqual(detail_op.detail_id, "detail:notebook")
        self.assertEqual(detail_op.field_name, "accessibility")
        self.assertLess(detail_op.new_value, detail_op.old_value)
        self.assertLess(detail_op.delta, 0.0)

        successor = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            decision=decision,
        )
        assert successor is not None
        old_henry = trace.detail_state("detail:henry")
        new_henry = successor.detail_state("detail:henry")
        old_notebook = trace.detail_state("detail:notebook")
        new_notebook = successor.detail_state("detail:notebook")

        self.assertEqual(new_henry, old_henry)
        self.assertEqual(new_notebook.detail_id, old_notebook.detail_id)
        self.assertEqual(new_notebook.retention, old_notebook.retention)
        self.assertEqual(
            new_notebook.temporal_confidence,
            old_notebook.temporal_confidence,
        )
        self.assertEqual(
            new_notebook.association_strength,
            old_notebook.association_strength,
        )
        self.assertLess(
            new_notebook.accessibility,
            old_notebook.accessibility,
        )
        self.assertEqual(
            new_notebook.parent_state_fingerprint,
            old_notebook.state_fingerprint,
        )
        self.assertEqual(
            new_notebook.state_fingerprint,
            detail_op.new_state_fingerprint,
        )
        self.assertEqual(successor.details, trace.details)
        self.assertEqual(successor.gist, trace.gist)
        self.assertEqual(successor.protected_evidence, trace.protected_evidence)

    def test_p6b_matched_detail_drift_lesion_changes_only_detail_state(self):
        trace = self.trace_with_two_details()
        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-lesion",
            cue_text="Henry apparatus",
            config=ReconstructionConfig(max_details=1),
        )
        source_decision, finalized, awareness = self.finalized_from_candidate(
            candidate
        )
        policy = ReconsolidationPolicy(max_detail_accessibility_loss=0.20)

        disabled = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=False,
                interference_strength=1.0,
            ),
            policy=policy,
        )
        enabled = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=True,
                interference_strength=1.0,
            ),
            policy=policy,
        )
        self.assertEqual(disabled.operations, enabled.operations)
        self.assertEqual(
            disabled.eligibility_strength,
            enabled.eligibility_strength,
        )
        self.assertEqual(disabled.detail_operations, ())
        self.assertEqual(len(enabled.detail_operations), 1)

        disabled_successor = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            decision=disabled,
        )
        enabled_successor = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            decision=enabled,
        )
        assert disabled_successor is not None
        assert enabled_successor is not None
        for field_name in (
            "strength",
            "accessibility",
            "familiarity",
            "retrieval_count",
            "rehearsal_count",
        ):
            self.assertEqual(
                getattr(disabled_successor, field_name),
                getattr(enabled_successor, field_name),
            )
        self.assertEqual(
            disabled_successor.detail_state("detail:henry"),
            enabled_successor.detail_state("detail:henry"),
        )
        self.assertNotEqual(
            disabled_successor.detail_state("detail:notebook"),
            enabled_successor.detail_state("detail:notebook"),
        )

    def test_p6b_weakening_can_cause_later_omission_without_deleting_detail(self):
        trace = self.trace_with_two_details()
        before = self.reconstruct(
            trace,
            episode_id="episode:p6b-before",
            cue_text="laboratory",
            config=ReconstructionConfig(
                max_details=2,
                minimum_detail_score=0.525,
            ),
        )
        self.assertIn(
            f"{trace.trace_id}:detail:notebook",
            before.included_detail_refs,
        )

        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-reactivation",
            cue_text="Henry apparatus",
            config=ReconstructionConfig(max_details=1),
        )
        source_decision, finalized, awareness = self.finalized_from_candidate(
            candidate
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=True,
                interference_strength=1.0,
            ),
            policy=ReconsolidationPolicy(
                max_detail_accessibility_loss=0.20,
            ),
        )
        successor = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            decision=decision,
        )
        assert successor is not None

        after = self.reconstruct(
            successor,
            episode_id="episode:p6b-after",
            cue_text="laboratory",
            config=ReconstructionConfig(
                max_details=2,
                minimum_detail_score=0.525,
            ),
        )
        self.assertIn(
            f"{successor.trace_id}:detail:notebook",
            after.omitted_detail_refs,
        )
        self.assertEqual(
            tuple(detail.detail_id for detail in successor.details),
            ("detail:henry", "detail:notebook"),
        )
        self.assertEqual(successor.details, trace.details)
        self.assertEqual(successor.protected_evidence, trace.protected_evidence)

    def test_p6b_weakened_detail_remains_recoverable_under_strong_matching_cue(self):
        trace = self.trace_with_two_details()
        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-recovery-reactivation",
            cue_text="Henry apparatus",
            config=ReconstructionConfig(max_details=1),
        )
        source_decision, finalized, awareness = self.finalized_from_candidate(
            candidate
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=True,
                interference_strength=1.0,
            ),
            policy=ReconsolidationPolicy(
                max_detail_accessibility_loss=0.20,
            ),
        )
        successor = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            decision=decision,
        )
        assert successor is not None

        weak_cue = self.reconstruct(
            successor,
            episode_id="episode:p6b-recovery-weak",
            cue_text="laboratory",
            config=ReconstructionConfig(
                max_details=2,
                minimum_detail_score=0.525,
            ),
        )
        strong_cue = self.reconstruct(
            successor,
            episode_id="episode:p6b-recovery-strong",
            cue_text="blue notebook table",
            config=ReconstructionConfig(
                max_details=2,
                minimum_detail_score=0.525,
            ),
        )
        self.assertIn(
            f"{successor.trace_id}:detail:notebook",
            weak_cue.omitted_detail_refs,
        )
        self.assertIn(
            f"{successor.trace_id}:detail:notebook",
            strong_cue.included_detail_refs,
        )

    def test_p6b_detail_state_and_operation_survive_restart(self):
        trace = self.trace_with_two_details()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-persist",
            cue_text="Henry apparatus",
            config=ReconstructionConfig(max_details=1),
        )
        source_decision, finalized, awareness = self.finalized_from_candidate(
            candidate
        )
        decision, successor = reconsolidate_and_record(
            ledger=ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=True,
                interference_strength=1.0,
            ),
            policy=ReconsolidationPolicy(
                max_detail_accessibility_loss=0.20,
            ),
        )
        assert successor is not None
        self.assertEqual(len(decision.detail_operations), 1)

        restored = TraceVersionLedger.from_json(ledger.stable_json())
        restored_successor = restored.latest(trace.trace_lineage_id)
        self.assertEqual(restored_successor, successor)
        self.assertEqual(
            restored.decision_audit(successor.trace_id)["detail_operations"],
            [dataclasses.asdict(decision.detail_operations[0])],
        )

    def test_p6b_ledger_rejects_fabricated_detail_state_transition(self):
        trace = self.trace_with_two_details()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-forged-detail-state",
            cue_text="Henry apparatus",
            config=ReconstructionConfig(max_details=1),
        )
        source_decision, finalized, awareness = self.finalized_from_candidate(
            candidate
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=True,
                interference_strength=1.0,
            ),
            policy=ReconsolidationPolicy(
                max_detail_accessibility_loss=0.20,
            ),
        )
        valid = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            decision=decision,
        )
        assert valid is not None

        notebook = valid.detail_state("detail:notebook")
        forged_states = tuple(
            (
                TraceDetailState(
                    detail_id=state.detail_id,
                    retention=state.retention,
                    accessibility=max(0.0, state.accessibility - 0.10),
                    temporal_confidence=state.temporal_confidence,
                    association_strength=state.association_strength,
                    parent_state_fingerprint=state.parent_state_fingerprint,
                )
                if state.detail_id == notebook.detail_id
                else state
            )
            for state in valid.detail_states
        )
        forged = MemoryTrace(
            subject_id=valid.subject_id,
            version=valid.version,
            protected_evidence=valid.protected_evidence,
            gist=valid.gist,
            details=valid.details,
            detail_states=forged_states,
            temporal_cues=valid.temporal_cues,
            actor_refs=valid.actor_refs,
            object_refs=valid.object_refs,
            encoding_affect=valid.encoding_affect,
            source_cues=valid.source_cues,
            strength=valid.strength,
            accessibility=valid.accessibility,
            familiarity=valid.familiarity,
            rehearsal_count=valid.rehearsal_count,
            retrieval_count=valid.retrieval_count,
            competing_trace_ids=valid.competing_trace_ids,
            parent_trace_id=valid.parent_trace_id,
            reconsolidation_decision_fingerprint=valid.reconsolidation_decision_fingerprint,
            reconsolidation_event_id=valid.reconsolidation_event_id,
        )
        with self.assertRaises(ValueError):
            ledger.append_successor(
                parent=trace,
                successor=forged,
                decision=decision,
            )

    def test_p6b_initial_ledger_rejects_detail_state_with_fake_parent(self):
        base = self.trace_with_two_details()
        first = base.detail_state("detail:henry")
        second = base.detail_state("detail:notebook")
        forged = MemoryTrace(
            subject_id=base.subject_id,
            version=0,
            protected_evidence=base.protected_evidence,
            gist=base.gist,
            details=base.details,
            detail_states=(
                TraceDetailState(
                    detail_id=first.detail_id,
                    retention=first.retention,
                    accessibility=first.accessibility,
                    temporal_confidence=first.temporal_confidence,
                    association_strength=first.association_strength,
                    parent_state_fingerprint="detail_state_nonexistent_parent",
                ),
                second,
            ),
            temporal_cues=base.temporal_cues,
            actor_refs=base.actor_refs,
            object_refs=base.object_refs,
            encoding_affect=base.encoding_affect,
            source_cues=base.source_cues,
            strength=base.strength,
            accessibility=base.accessibility,
            familiarity=base.familiarity,
            rehearsal_count=base.rehearsal_count,
            retrieval_count=base.retrieval_count,
            competing_trace_ids=base.competing_trace_ids,
        )
        ledger = TraceVersionLedger()
        with self.assertRaises(ValueError):
            ledger.register_initial(forged)

    def test_p6b_source_attribution_does_not_change_detail_drift(self):
        trace = self.trace_with_two_details()
        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-source-independence",
            cue_text="Henry apparatus",
            config=ReconstructionConfig(max_details=1),
        )
        lived = monitor_recollection_source(
            candidate=candidate,
            cues=self.source_cues(),
        )
        read = monitor_recollection_source(
            candidate=candidate,
            cues=SourceMonitoringCues(
                retrieval_fluency=0.75,
                perceptual_richness=0.10,
                temporal_coherence=0.70,
                spatial_coherence=0.65,
                contextual_compatibility=0.80,
                familiarity=0.85,
                trace_accessibility=0.70,
                rehearsal_frequency=0.70,
                reconstruction_exposure=0.20,
                cue_match=0.80,
                textual_signature=0.95,
            ),
        )
        self.assertIs(lived.selected_source, SubjectiveSourceKind.LIVED)
        self.assertIs(read.selected_source, SubjectiveSourceKind.READ)

        def finalize_and_route(source_decision):
            finalized = finalize_recollection(
                candidate=candidate,
                decision=source_decision,
                context=RecollectionFinalizationContext(
                    tick=91,
                    source_state_digest="sha256:p6b-source-independent",
                    objective_provenance=ObjectiveProvenance(
                        evidence_class="test",
                        source="audit",
                        record_ids=candidate.protected_evidence_refs,
                    ),
                ),
            )
            awareness = AwarenessRouter().route(
                (
                    AwarenessCandidate(
                        event=finalized.event,
                        salience=1.0,
                        change=1.0,
                        novelty=1.0,
                        goal_relevance=1.0,
                        persistence=1.0,
                    ),
                )
            )[0]
            return finalized, awareness

        lived_finalized, lived_awareness = finalize_and_route(lived)
        read_finalized, read_awareness = finalize_and_route(read)
        context = ReconsolidationContext(
            enabled=True,
            reactivation_strength=0.95,
            prediction_error=0.65,
            emotional_activation=0.55,
            goal_relevance=0.65,
            explicit_rehearsal=True,
            detail_drift_enabled=True,
            interference_strength=1.0,
        )
        policy = ReconsolidationPolicy(max_detail_accessibility_loss=0.20)
        lived_decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=lived,
            finalized_recollection=lived_finalized,
            awareness_decision=lived_awareness,
            context=context,
            policy=policy,
        )
        read_decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=read,
            finalized_recollection=read_finalized,
            awareness_decision=read_awareness,
            context=context,
            policy=policy,
        )
        self.assertEqual(
            lived_decision.detail_operations,
            read_decision.detail_operations,
        )
        self.assertEqual(
            lived_decision.detail_reason_codes,
            read_decision.detail_reason_codes,
        )

    def test_p6b_detail_drift_requires_interference_threshold(self):
        trace = self.trace_with_two_details()
        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-low-interference",
            cue_text="Henry apparatus",
            config=ReconstructionConfig(max_details=1),
        )
        source_decision, finalized, awareness = self.finalized_from_candidate(
            candidate
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=True,
                interference_strength=0.10,
            ),
        )
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.detail_operations, ())
        self.assertIn(
            "detail_interference_below_threshold",
            decision.detail_reason_codes,
        )

    def test_p6b_included_detail_is_not_weakened(self):
        trace = self.trace_with_two_details()
        candidate = self.reconstruct(
            trace,
            episode_id="episode:p6b-included",
            cue_text="blue notebook table",
            config=ReconstructionConfig(max_details=1),
        )
        self.assertIn(
            f"{trace.trace_id}:detail:notebook",
            candidate.included_detail_refs,
        )
        source_decision, finalized, awareness = self.finalized_from_candidate(
            candidate
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=awareness,
            context=ReconsolidationContext(
                enabled=True,
                reactivation_strength=0.95,
                prediction_error=0.65,
                emotional_activation=0.55,
                goal_relevance=0.65,
                explicit_rehearsal=True,
                detail_drift_enabled=True,
                interference_strength=1.0,
            ),
            policy=ReconsolidationPolicy(
                max_detail_accessibility_loss=0.20,
            ),
        )
        weakened_ids = {op.detail_id for op in decision.detail_operations}
        self.assertNotIn("detail:notebook", weakened_ids)

    def test_p6b_repeated_omission_is_bounded_and_asymptotic(self):
        current = self.trace_with_two_details()
        ledger = TraceVersionLedger()
        ledger.register_initial(current)
        policy = ReconsolidationPolicy(
            max_detail_accessibility_loss=0.20,
            detail_accessibility_floor=0.10,
        )
        first_loss = None
        last_loss = None

        for index in range(100):
            candidate = self.reconstruct(
                current,
                episode_id=f"episode:p6b-repeat:{index}",
                cue_text="Henry apparatus",
                config=ReconstructionConfig(max_details=1),
            )
            source_decision, finalized, awareness = self.finalized_from_candidate(
                candidate
            )
            decision, successor = reconsolidate_and_record(
                ledger=ledger,
                old_trace=current,
                candidate=candidate,
                source_decision=source_decision,
                finalized_recollection=finalized,
                awareness_decision=awareness,
                context=ReconsolidationContext(
                    enabled=True,
                    reactivation_strength=0.95,
                    prediction_error=0.65,
                    emotional_activation=0.55,
                    goal_relevance=0.65,
                    explicit_rehearsal=True,
                    detail_drift_enabled=True,
                    interference_strength=1.0,
                ),
                policy=policy,
            )
            assert successor is not None
            notebook_ops = [
                op
                for op in decision.detail_operations
                if op.detail_id == "detail:notebook"
            ]
            if notebook_ops:
                loss = abs(float(notebook_ops[0].delta))
                if first_loss is None:
                    first_loss = loss
                last_loss = loss
            current = successor

        notebook_state = current.detail_state("detail:notebook")
        self.assertGreaterEqual(
            notebook_state.accessibility,
            policy.detail_accessibility_floor,
        )
        self.assertEqual(notebook_state.availability_state.value, "suppressed")
        self.assertEqual(current.version, 100)
        self.assertEqual(len(ledger.history(current.trace_lineage_id)), 101)

        strong_recovery = self.reconstruct(
            current,
            episode_id="episode:p6b-repeat-recovery",
            cue_text="blue notebook table",
            config=ReconstructionConfig(
                max_details=2,
                minimum_detail_score=0.80,
            ),
        )
        self.assertIn(
            f"{current.trace_id}:detail:notebook",
            strong_recovery.included_detail_refs,
        )

        self.assertIsNotNone(first_loss)
        self.assertIsNotNone(last_loss)
        assert first_loss is not None and last_loss is not None
        self.assertLess(last_loss, first_loss)

    def test_p6b_restart_rejects_missing_detail_state_payload(self):
        trace = self.trace_with_two_details()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        payload = json.loads(ledger.stable_json())
        payload["traces"][0].pop("detail_states")
        corrupted = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self.assertRaises(ValueError):
            TraceVersionLedger.from_json(corrupted)

    def test_p6b_restart_rejects_tampered_detail_state_fingerprint(self):
        trace = self.trace_with_two_details()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        payload = json.loads(ledger.stable_json())
        payload["traces"][0]["detail_states"][0][
            "state_fingerprint"
        ] = "detail_state_corrupt"
        corrupted = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self.assertRaises(ValueError):
            TraceVersionLedger.from_json(corrupted)

    def test_p6b_restart_rejects_tampered_detail_availability_state(self):
        trace = self.trace_with_two_details()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        payload = json.loads(ledger.stable_json())
        payload["traces"][0]["detail_states"][0][
            "availability_state"
        ] = "suppressed"
        corrupted = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self.assertRaises(ValueError):
            TraceVersionLedger.from_json(corrupted)

    def test_ledger_rejects_silent_fork(self):
        trace = self.trace()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:fork",
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        successor = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            decision=decision,
        )
        assert successor is not None
        ledger.append_successor(
            parent=trace,
            successor=successor,
            decision=decision,
        )
        with self.assertRaises(ValueError):
            ledger.append_successor(
                parent=trace,
                successor=successor,
                decision=decision,
            )

    def test_ledger_rejects_nonmonotonic_successor_version(self):
        trace = self.trace(label="nonmonotonic")
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:nonmonotonic",
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        valid = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            decision=decision,
        )
        assert valid is not None
        invalid = MemoryTrace(
            subject_id=valid.subject_id,
            version=2,
            protected_evidence=valid.protected_evidence,
            gist=valid.gist,
            details=valid.details,
            temporal_cues=valid.temporal_cues,
            actor_refs=valid.actor_refs,
            object_refs=valid.object_refs,
            encoding_affect=valid.encoding_affect,
            source_cues=valid.source_cues,
            strength=valid.strength,
            accessibility=valid.accessibility,
            familiarity=valid.familiarity,
            rehearsal_count=valid.rehearsal_count,
            retrieval_count=valid.retrieval_count,
            competing_trace_ids=valid.competing_trace_ids,
            parent_trace_id=trace.trace_id,
            reconsolidation_decision_fingerprint=decision.decision_fingerprint,
            reconsolidation_event_id=event.event.event_id,
        )
        with self.assertRaises(ValueError):
            ledger.append_successor(
                parent=trace,
                successor=invalid,
                decision=decision,
            )

    def test_ledger_rejects_successor_not_described_by_decision_operations(self):
        trace = self.trace(label="forged-successor")
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:forged-successor",
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        valid = apply_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            decision=decision,
        )
        assert valid is not None

        forged = MemoryTrace(
            subject_id=valid.subject_id,
            version=valid.version,
            protected_evidence=valid.protected_evidence,
            gist=valid.gist,
            details=valid.details,
            temporal_cues=valid.temporal_cues,
            actor_refs=valid.actor_refs,
            object_refs=valid.object_refs,
            encoding_affect=valid.encoding_affect,
            source_cues=valid.source_cues,
            strength=min(1.0, valid.strength + 0.05),
            accessibility=valid.accessibility,
            familiarity=valid.familiarity,
            rehearsal_count=valid.rehearsal_count,
            retrieval_count=valid.retrieval_count,
            competing_trace_ids=valid.competing_trace_ids,
            parent_trace_id=valid.parent_trace_id,
            reconsolidation_decision_fingerprint=valid.reconsolidation_decision_fingerprint,
            reconsolidation_event_id=valid.reconsolidation_event_id,
        )
        with self.assertRaises(ValueError):
            ledger.append_successor(
                parent=trace,
                successor=forged,
                decision=decision,
            )

    def test_ledger_restart_round_trip_preserves_exact_history(self):
        trace = self.trace()
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:persist",
        )
        _, successor = reconsolidate_and_record(
            ledger=ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        assert successor is not None

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace-ledger.json"
            ledger.save(path)
            restored = TraceVersionLedger.load(path)

        self.assertEqual(restored.stable_json(), ledger.stable_json())
        restored_history = restored.history(trace.trace_lineage_id)
        self.assertEqual(
            tuple(item.trace_id for item in restored_history),
            tuple(item.trace_id for item in ledger.history(trace.trace_lineage_id)),
        )
        self.assertEqual(restored.latest(trace.trace_lineage_id).trace_id, successor.trace_id)
        audit = restored.decision_audit(successor.trace_id)
        self.assertEqual(
            audit["decision_fingerprint"],
            successor.reconsolidation_decision_fingerprint,
        )
        self.assertTrue(audit["eligible"])
        self.assertTrue(audit["operations"])

    def test_ledger_rejects_missing_persisted_trace_identity(self):
        trace = self.trace(label="missing-trace-id")
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        payload = json.loads(ledger.stable_json())
        payload["traces"][0].pop("trace_id")
        corrupted = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self.assertRaises(ValueError):
            TraceVersionLedger.from_json(corrupted)

    def test_ledger_rejects_noncanonical_persisted_numeric_types(self):
        trace = self.trace(label="typed-ledger")
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)

        version_payload = json.loads(ledger.stable_json())
        version_payload["traces"][0]["version"] = True
        with self.assertRaises(ValueError):
            TraceVersionLedger.from_json(
                json.dumps(
                    version_payload,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )

        strength_payload = json.loads(ledger.stable_json())
        strength_payload["traces"][0]["strength"] = "0.3"
        with self.assertRaises(ValueError):
            TraceVersionLedger.from_json(
                json.dumps(
                    strength_payload,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )

    def test_ledger_rejects_missing_p5_finalization_attestation_on_restart(self):
        trace = self.trace(label="missing-finalization-attestation")
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:missing-finalization-attestation",
        )
        _, successor = reconsolidate_and_record(
            ledger=ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        assert successor is not None

        payload = json.loads(ledger.stable_json())
        payload["transitions"][0]["decision"].pop(
            "finalized_recollection_fingerprint"
        )
        corrupted = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self.assertRaises(ValueError):
            TraceVersionLedger.from_json(corrupted)

    def test_persisted_transition_audit_corruption_fails_closed(self):
        trace = self.trace(label="audit-corruption")
        ledger = TraceVersionLedger()
        ledger.register_initial(trace)
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:audit-corruption",
        )
        _, successor = reconsolidate_and_record(
            ledger=ledger,
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        assert successor is not None

        payload = json.loads(ledger.stable_json())
        payload["transitions"][0]["decision"]["operations"][0]["new_value"] += 0.01
        corrupted = json.dumps(payload, sort_keys=True, separators=(",", ":"))

        with self.assertRaises(ValueError):
            TraceVersionLedger.from_json(corrupted)

    def test_repeated_recall_is_bounded_and_asymptotic(self):
        current = self.trace(
            label="long-run",
            strength=0.20,
            accessibility=0.20,
            familiarity=0.20,
        )
        ledger = TraceVersionLedger()
        ledger.register_initial(current)
        policy = ReconsolidationPolicy()
        first_strength_delta = None
        last_strength_delta = None

        for index in range(100):
            candidate, source_decision, finalized, event = self.final_event(
                current,
                episode_id=f"episode:repeat:{index}",
            )
            decision, successor = reconsolidate_and_record(
                ledger=ledger,
                old_trace=current,
                candidate=candidate,
                source_decision=source_decision,
                finalized_recollection=finalized,
                awareness_decision=event,
                context=self.eligible_context(),
                policy=policy,
            )
            self.assertTrue(decision.eligible)
            assert successor is not None
            strength_ops = [
                op for op in decision.operations if op.field_name == "strength"
            ]
            if strength_ops:
                if first_strength_delta is None:
                    first_strength_delta = float(strength_ops[0].delta)
                last_strength_delta = float(strength_ops[0].delta)
            current = successor

        self.assertEqual(current.version, 100)
        self.assertLessEqual(current.strength, policy.strength_ceiling)
        self.assertLessEqual(current.accessibility, policy.accessibility_ceiling)
        self.assertLessEqual(current.familiarity, policy.familiarity_ceiling)
        self.assertEqual(len(ledger.history(current.trace_lineage_id)), 101)
        self.assertIsNotNone(first_strength_delta)
        self.assertIsNotNone(last_strength_delta)
        assert first_strength_delta is not None and last_strength_delta is not None
        self.assertLess(last_strength_delta, first_strength_delta)

    def test_corrupted_reconsolidation_decision_fails_closed(self):
        trace = self.trace()
        candidate, source_decision, finalized, event = self.final_event(
            trace,
            episode_id="episode:corrupt",
        )
        decision = evaluate_reconsolidation(
            old_trace=trace,
            candidate=candidate,
            source_decision=source_decision,
            finalized_recollection=finalized,
            awareness_decision=event,
            context=self.eligible_context(),
        )
        object.__setattr__(decision, "eligibility_strength", 0.01)
        with self.assertRaises(ValueError):
            apply_reconsolidation(
                old_trace=trace,
                candidate=candidate,
                source_decision=source_decision,
                finalized_recollection=finalized,
                awareness_decision=event,
                decision=decision,
            )


if __name__ == "__main__":
    unittest.main()
