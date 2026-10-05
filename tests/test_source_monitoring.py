from __future__ import annotations

import dataclasses
import unittest

from doctor_lives.phenomenology import (
    AwarenessLevel,
    ObjectiveProvenance,
    PhenomenalEvent,
    PrivacyState,
    SubjectiveSourceKind,
)
from doctor_lives.recollection import (
    MemoryTrace,
    ProtectedEvidenceRef,
    ReconstructionConfig,
    RetrievalEpisode,
    TraceDetail,
    reconstruct_recollection,
)
from doctor_lives.source_monitoring import (
    RecollectionFinalizationContext,
    SourceMonitoringCues,
    SourceMonitoringDecision,
    finalize_recollection_event,
    monitor_recollection_source,
)


class SourceMonitoringTests(unittest.TestCase):
    def candidate(self, *, label: str = "base", accessibility: float = 0.72):
        trace = MemoryTrace(
            subject_id="subject-source-monitor",
            version=0,
            protected_evidence=(
                ProtectedEvidenceRef(
                    evidence_id=f"evidence:{label}",
                    digest=f"sha256:{label}",
                ),
            ),
            gist=f"The {label} demonstration took place in the laboratory",
            details=(
                TraceDetail(
                    detail_id=f"detail:{label}",
                    text=f"Henry stood beside the {label} apparatus",
                    cue_terms=("henry", "apparatus"),
                ),
            ),
            strength=0.78,
            accessibility=accessibility,
            familiarity=0.76,
        )
        episode = RetrievalEpisode(
            episode_id=f"episode:{label}",
            subject_id=trace.subject_id,
            tick=40,
            cue_text="Henry apparatus",
            candidate_trace_ids=(trace.trace_id,),
            context_refs=("room:laboratory",),
            subject_state_digest="sha256:subject-state",
        )
        return reconstruct_recollection(
            [trace],
            episode,
            config=ReconstructionConfig(max_details=1),
        )

    def lived_cues(self) -> SourceMonitoringCues:
        return SourceMonitoringCues(
            retrieval_fluency=0.90,
            perceptual_richness=0.95,
            temporal_coherence=0.90,
            spatial_coherence=0.90,
            contextual_compatibility=0.85,
            familiarity=0.80,
            trace_accessibility=0.85,
            rehearsal_frequency=0.40,
            imagination_exposure=0.05,
            reconstruction_exposure=0.05,
            competing_source_strength=0.05,
            cue_match=0.90,
            social_communication_signature=0.05,
            textual_signature=0.05,
            inferential_signature=0.05,
            dreamlike_discontinuity=0.02,
        )

    def ambiguous_cues(self) -> SourceMonitoringCues:
        return SourceMonitoringCues(
            retrieval_fluency=0.38,
            perceptual_richness=0.32,
            temporal_coherence=0.35,
            spatial_coherence=0.35,
            contextual_compatibility=0.40,
            familiarity=0.42,
            trace_accessibility=0.40,
            rehearsal_frequency=0.20,
            imagination_exposure=0.28,
            reconstruction_exposure=0.28,
            competing_source_strength=0.82,
            cue_match=0.35,
            social_communication_signature=0.25,
            textual_signature=0.25,
            inferential_signature=0.25,
            dreamlike_discontinuity=0.20,
        )

    def read_cues(self) -> SourceMonitoringCues:
        return SourceMonitoringCues(
            retrieval_fluency=0.75,
            perceptual_richness=0.10,
            temporal_coherence=0.70,
            spatial_coherence=0.65,
            contextual_compatibility=0.80,
            familiarity=0.85,
            trace_accessibility=0.70,
            rehearsal_frequency=0.70,
            imagination_exposure=0.05,
            reconstruction_exposure=0.20,
            competing_source_strength=0.10,
            cue_match=0.80,
            social_communication_signature=0.05,
            textual_signature=0.95,
            inferential_signature=0.10,
            dreamlike_discontinuity=0.02,
        )

    def test_source_monitoring_cues_expose_no_privileged_provenance_fields(self):
        names = {field.name for field in dataclasses.fields(SourceMonitoringCues)}
        forbidden_fragments = {
            "evidence",
            "digest",
            "trace_id",
            "candidate_id",
            "objective",
            "database",
            "archive",
            "classification",
        }
        for name in names:
            for fragment in forbidden_fragments:
                self.assertNotIn(fragment, name)

    def test_default_cues_remain_epistemically_unknown(self):
        candidate = self.candidate()
        decision = monitor_recollection_source(
            candidate_id=candidate.candidate_id,
            cues=SourceMonitoringCues(),
        )
        self.assertIs(decision.selected_source, SubjectiveSourceKind.UNKNOWN)

    def test_matched_candidate_supports_lived_unknown_and_read_attribution(self):
        candidate = self.candidate()

        lived = monitor_recollection_source(
            candidate_id=candidate.candidate_id,
            cues=self.lived_cues(),
        )
        ambiguous = monitor_recollection_source(
            candidate_id=candidate.candidate_id,
            cues=self.ambiguous_cues(),
        )
        read = monitor_recollection_source(
            candidate_id=candidate.candidate_id,
            cues=self.read_cues(),
        )

        self.assertEqual(lived.candidate_id, candidate.candidate_id)
        self.assertEqual(ambiguous.candidate_id, candidate.candidate_id)
        self.assertEqual(read.candidate_id, candidate.candidate_id)

        self.assertIs(lived.selected_source, SubjectiveSourceKind.LIVED)
        self.assertIs(ambiguous.selected_source, SubjectiveSourceKind.UNKNOWN)
        self.assertIs(read.selected_source, SubjectiveSourceKind.READ)

        self.assertNotEqual(lived.decision_fingerprint, ambiguous.decision_fingerprint)
        self.assertNotEqual(read.decision_fingerprint, ambiguous.decision_fingerprint)

    def test_same_cues_different_reconstruction_content_preserve_source_scoring(self):
        first = self.candidate(label="first", accessibility=0.65)
        second = self.candidate(label="second", accessibility=0.91)
        cues = self.read_cues()

        first_decision = monitor_recollection_source(
            candidate_id=first.candidate_id,
            cues=cues,
        )
        second_decision = monitor_recollection_source(
            candidate_id=second.candidate_id,
            cues=cues,
        )

        self.assertNotEqual(first.candidate_id, second.candidate_id)
        self.assertEqual(first_decision.selected_source, second_decision.selected_source)
        self.assertEqual(first_decision.certainty, second_decision.certainty)
        self.assertEqual(first_decision.contributions, second_decision.contributions)
        self.assertNotEqual(
            first_decision.decision_fingerprint,
            second_decision.decision_fingerprint,
        )

    def test_decision_is_factory_controlled(self):
        with self.assertRaises(TypeError):
            SourceMonitoringDecision()

    def test_cue_normalization_rejects_nonfinite_and_boolean_values(self):
        normalized = SourceMonitoringCues(retrieval_fluency="0.5")  # type: ignore[arg-type]
        self.assertEqual(normalized.retrieval_fluency, 0.5)
        self.assertIsInstance(normalized.retrieval_fluency, float)

        with self.assertRaises(TypeError):
            SourceMonitoringCues(retrieval_fluency=True)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            SourceMonitoringCues(retrieval_fluency=float("nan"))
        with self.assertRaises(ValueError):
            SourceMonitoringCues(retrieval_fluency=float("inf"))

    def test_finalization_keeps_candidate_content_fixed_while_source_changes(self):
        candidate = self.candidate()
        lived_decision = monitor_recollection_source(
            candidate_id=candidate.candidate_id,
            cues=self.lived_cues(),
        )
        read_decision = monitor_recollection_source(
            candidate_id=candidate.candidate_id,
            cues=self.read_cues(),
        )
        provenance = ObjectiveProvenance(
            evidence_class="reconstructed_source",
            source="protected-memory-audit",
            record_ids=candidate.protected_evidence_refs,
        )
        context = RecollectionFinalizationContext(
            tick=41,
            source_state_digest="sha256:p5-state",
            objective_provenance=provenance,
        )

        lived_event = finalize_recollection_event(
            candidate=candidate,
            decision=lived_decision,
            context=context,
        )
        read_event = finalize_recollection_event(
            candidate=candidate,
            decision=read_decision,
            context=context,
        )

        self.assertIsInstance(lived_event, PhenomenalEvent)
        self.assertIs(lived_event.awareness, AwarenessLevel.LATENT)
        self.assertIs(read_event.awareness, AwarenessLevel.LATENT)
        self.assertEqual(lived_event.canonical_first_person, read_event.canonical_first_person)
        self.assertIn(candidate.reconstructed_scene, lived_event.canonical_first_person)
        self.assertIs(lived_event.subjective_source.kind, SubjectiveSourceKind.LIVED)
        self.assertIs(read_event.subjective_source.kind, SubjectiveSourceKind.READ)
        self.assertNotEqual(lived_event.event_id, read_event.event_id)

        self.assertIn(candidate.candidate_id, lived_event.source_event_refs)
        self.assertIn(
            lived_decision.decision_fingerprint,
            lived_event.source_event_refs,
        )
        self.assertIn(
            candidate.retrieval_episode_fingerprint,
            lived_event.source_event_refs,
        )

    def test_finalization_requires_decision_for_exact_candidate(self):
        first = self.candidate(label="first")
        second = self.candidate(label="second")
        decision = monitor_recollection_source(
            candidate_id=first.candidate_id,
            cues=self.lived_cues(),
        )
        provenance = ObjectiveProvenance(
            evidence_class="test",
            source="audit",
            record_ids=second.protected_evidence_refs,
        )
        context = RecollectionFinalizationContext(
            tick=1,
            source_state_digest="sha256:test",
            objective_provenance=provenance,
        )
        with self.assertRaises(ValueError):
            finalize_recollection_event(
                candidate=second,
                decision=decision,
                context=context,
            )

    def test_finalization_requires_objective_provenance_to_match_candidate_refs(self):
        candidate = self.candidate()
        decision = monitor_recollection_source(
            candidate_id=candidate.candidate_id,
            cues=self.lived_cues(),
        )
        wrong_provenance = ObjectiveProvenance(
            evidence_class="test",
            source="audit",
            record_ids=("evidence:wrong",),
        )
        context = RecollectionFinalizationContext(
            tick=1,
            source_state_digest="sha256:test",
            objective_provenance=wrong_provenance,
        )
        with self.assertRaises(ValueError):
            finalize_recollection_event(
                candidate=candidate,
                decision=decision,
                context=context,
            )

    def test_objective_provenance_does_not_affect_source_monitoring_decision(self):
        candidate = self.candidate()
        cues = self.lived_cues()

        before = monitor_recollection_source(
            candidate_id=candidate.candidate_id,
            cues=cues,
        )
        # Objective truth exists only at finalization. The source monitor cannot
        # receive either of these mutually incompatible audit classifications.
        reconstructed = ObjectiveProvenance(
            evidence_class="reconstructed_preawakening_memory",
            source="archive",
            record_ids=candidate.protected_evidence_refs,
        )
        lived = ObjectiveProvenance(
            evidence_class="lived_runtime_memory",
            source="world",
            record_ids=candidate.protected_evidence_refs,
        )
        self.assertNotEqual(reconstructed.evidence_class, lived.evidence_class)

        after = monitor_recollection_source(
            candidate_id=candidate.candidate_id,
            cues=cues,
        )
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
