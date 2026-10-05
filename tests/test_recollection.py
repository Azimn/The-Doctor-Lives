from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from doctor_lives.phenomenology import PhenomenalEvent
from doctor_lives.recollection import (
    MemoryTrace,
    ProtectedEvidenceRef,
    ReconstructionConfig,
    RecollectionCandidate,
    RetrievalEpisode,
    TraceDetail,
    reconstruct_recollection,
)


class RecollectionArchitectureTests(unittest.TestCase):
    def evidence(self, label: str = "demo") -> ProtectedEvidenceRef:
        return ProtectedEvidenceRef(
            evidence_id=f"evidence:{label}",
            digest=f"sha256:{label}",
        )

    def trace(self) -> MemoryTrace:
        detail_one_terms = ["window", "rain"]
        details = [
            TraceDetail(
                detail_id="detail:window",
                text="Rain struck the laboratory window",
                cue_terms=detail_one_terms,
            ),
            TraceDetail(
                detail_id="detail:henry",
                text="Henry stood near the apparatus",
                cue_terms=("henry", "apparatus"),
            ),
        ]
        trace = MemoryTrace(
            subject_id="subject-memory",
            version=0,
            protected_evidence=[self.evidence()],
            gist="The demonstration took place in the laboratory",
            details=details,
            temporal_cues=["evening"],
            actor_refs=["actor:henry"],
            object_refs=["object:apparatus"],
            encoding_affect=["tense"],
            source_cues=["visual-richness", "familiar-setting"],
            strength=0.78,
            accessibility=0.72,
            familiarity=0.81,
        )
        detail_one_terms.append("mutated")
        details.append(
            TraceDetail(
                detail_id="detail:late",
                text="This should not enter the existing trace",
            )
        )
        return trace

    def episode(
        self,
        trace: MemoryTrace,
        *,
        episode_id: str = "episode-001",
        cue_text: str = "rain at the window",
        tick: int = 20,
    ) -> RetrievalEpisode:
        return RetrievalEpisode(
            episode_id=episode_id,
            subject_id=trace.subject_id,
            tick=tick,
            cue_text=cue_text,
            candidate_trace_ids=[trace.trace_id],
            context_refs=["room:laboratory"],
            subject_state_digest="sha256:subject-state",
        )

    def test_memory_trace_is_deeply_immutable_snapshot(self):
        trace = self.trace()
        self.assertEqual(len(trace.details), 2)
        self.assertEqual(trace.temporal_cues, ("evening",))
        self.assertEqual(trace.actor_refs, ("actor:henry",))
        self.assertEqual(trace.details[0].cue_terms, ("window", "rain"))
        with self.assertRaises(FrozenInstanceError):
            trace.gist = "changed"  # type: ignore[misc]

    def test_duplicate_detail_ids_within_trace_fail_closed(self):
        with self.assertRaises(ValueError):
            MemoryTrace(
                subject_id="subject-memory",
                version=0,
                protected_evidence=(self.evidence("dup-detail"),),
                gist="A scene with ambiguous local detail identity",
                details=(
                    TraceDetail(
                        detail_id="detail:henry",
                        text="Henry stood near the apparatus",
                    ),
                    TraceDetail(
                        detail_id="detail:henry",
                        text="Henry stood by the doorway",
                    ),
                ),
            )

    def test_duplicate_evidence_ids_within_trace_fail_closed(self):
        with self.assertRaises(ValueError):
            MemoryTrace(
                subject_id="subject-memory",
                version=0,
                protected_evidence=(
                    ProtectedEvidenceRef("evidence:same", "sha256:first"),
                    ProtectedEvidenceRef("evidence:same", "sha256:second"),
                ),
                gist="A trace cannot ambiguously bind one evidence identifier twice",
            )

    def test_recollection_candidate_cannot_be_constructed_directly(self):
        with self.assertRaises(TypeError):
            RecollectionCandidate(
                subject_id="subject-memory",
                retrieval_episode_id="episode-fabricated",
                retrieval_episode_fingerprint="fabricated-fingerprint",
                reconstruction_config_fingerprint="fabricated-config",
                reconstruction_rule_version="uppb-p4-v1",
                trace_ids=("trace_x",),
                protected_evidence_refs=("evidence:x",),
                reconstructed_scene="Henry was definitely there.",
                included_detail_refs=("trace_x:invented",),
                omitted_detail_refs=(),
                vividness=None,  # type: ignore[arg-type]
                content_confidence=1.0,
                fragmented=False,
                blended=False,
                reconstruction_operations=("retrieve_details",),
            )

    def test_recall_does_not_mutate_protected_evidence_or_trace(self):
        trace = self.trace()
        episode = self.episode(trace)
        evidence_digest_before = trace.protected_evidence_digest
        trace_digest_before = trace.snapshot_digest
        evidence_json_before = tuple(
            (ref.evidence_id, ref.digest) for ref in trace.protected_evidence
        )

        candidate = reconstruct_recollection(
            [trace],
            episode,
            config=ReconstructionConfig(max_details=1),
        )

        self.assertIsInstance(candidate, RecollectionCandidate)
        self.assertEqual(trace.protected_evidence_digest, evidence_digest_before)
        self.assertEqual(trace.snapshot_digest, trace_digest_before)
        self.assertEqual(
            tuple((ref.evidence_id, ref.digest) for ref in trace.protected_evidence),
            evidence_json_before,
        )
        self.assertNotIsInstance(candidate, PhenomenalEvent)
        self.assertFalse(hasattr(candidate, "subjective_source"))

    def test_same_trace_different_cues_can_change_reconstruction_without_trace_change(self):
        trace = self.trace()
        digest_before = trace.snapshot_digest

        rain = reconstruct_recollection(
            [trace],
            self.episode(trace, episode_id="episode-rain", cue_text="rain window"),
            config=ReconstructionConfig(max_details=1),
        )
        henry = reconstruct_recollection(
            [trace],
            self.episode(trace, episode_id="episode-henry", cue_text="Henry apparatus"),
            config=ReconstructionConfig(max_details=1),
        )

        self.assertEqual(
            rain.included_detail_refs,
            (f"{trace.trace_id}:detail:window",),
        )
        self.assertEqual(
            henry.included_detail_refs,
            (f"{trace.trace_id}:detail:henry",),
        )
        self.assertNotEqual(rain.reconstructed_scene, henry.reconstructed_scene)
        self.assertEqual(trace.snapshot_digest, digest_before)

    def test_identical_inputs_reconstruct_deterministically(self):
        trace = self.trace()
        episode = self.episode(trace)
        config = ReconstructionConfig(max_details=1)
        first = reconstruct_recollection([trace], episode, config=config)
        second = reconstruct_recollection([trace], episode, config=config)
        self.assertEqual(first, second)
        self.assertEqual(first.candidate_digest, second.candidate_digest)

    def test_distinct_retrieval_episodes_have_distinct_occurrence_identity(self):
        trace = self.trace()
        first_episode = self.episode(
            trace,
            episode_id="episode-first",
            cue_text="rain window",
            tick=20,
        )
        second_episode = self.episode(
            trace,
            episode_id="episode-second",
            cue_text="rain window",
            tick=20,
        )
        first = reconstruct_recollection(
            [trace],
            first_episode,
            config=ReconstructionConfig(max_details=1),
        )
        second = reconstruct_recollection(
            [trace],
            second_episode,
            config=ReconstructionConfig(max_details=1),
        )
        self.assertEqual(first.reconstructed_scene, second.reconstructed_scene)
        self.assertNotEqual(first_episode.occurrence_fingerprint, second_episode.occurrence_fingerprint)
        self.assertNotEqual(first.candidate_id, second.candidate_id)

    def test_reused_episode_id_with_changed_episode_state_stays_distinct(self):
        trace = self.trace()
        first_episode = RetrievalEpisode(
            episode_id="episode-reused",
            subject_id=trace.subject_id,
            tick=20,
            cue_text="rain window",
            candidate_trace_ids=(trace.trace_id,),
            context_refs=("context:first",),
            subject_state_digest="sha256:same-state",
        )
        second_episode = RetrievalEpisode(
            episode_id="episode-reused",
            subject_id=trace.subject_id,
            tick=20,
            cue_text="rain window",
            candidate_trace_ids=(trace.trace_id,),
            context_refs=("context:second",),
            subject_state_digest="sha256:same-state",
        )
        config = ReconstructionConfig(max_details=1)
        first = reconstruct_recollection([trace], first_episode, config=config)
        second = reconstruct_recollection([trace], second_episode, config=config)

        self.assertEqual(first.reconstructed_scene, second.reconstructed_scene)
        self.assertNotEqual(
            first_episode.occurrence_fingerprint,
            second_episode.occurrence_fingerprint,
        )
        self.assertEqual(
            first.retrieval_episode_fingerprint,
            first_episode.occurrence_fingerprint,
        )
        self.assertEqual(
            second.retrieval_episode_fingerprint,
            second_episode.occurrence_fingerprint,
        )
        self.assertNotEqual(first.candidate_id, second.candidate_id)

    def test_reconstruction_config_is_bound_even_when_visible_content_matches(self):
        trace = self.trace()
        episode = self.episode(trace, episode_id="episode-config")
        loose = ReconstructionConfig(max_details=1, minimum_detail_score=0.0)
        stricter = ReconstructionConfig(max_details=1, minimum_detail_score=0.1)

        first = reconstruct_recollection([trace], episode, config=loose)
        second = reconstruct_recollection([trace], episode, config=stricter)

        self.assertEqual(first.reconstructed_scene, second.reconstructed_scene)
        self.assertNotEqual(loose.fingerprint, stricter.fingerprint)
        self.assertEqual(first.reconstruction_config_fingerprint, loose.fingerprint)
        self.assertEqual(second.reconstruction_config_fingerprint, stricter.fingerprint)
        self.assertEqual(
            first.reconstruction_rule_version,
            episode.reconstruction_rule_version,
        )
        self.assertNotEqual(first.candidate_id, second.candidate_id)

    def test_partial_recollection_prefers_omission_over_invention(self):
        trace = self.trace()
        candidate = reconstruct_recollection(
            [trace],
            self.episode(trace),
            config=ReconstructionConfig(max_details=1),
        )
        known_detail_text = {
            f"{trace.trace_id}:{detail.detail_id}": detail.text
            for detail in trace.details
        }
        self.assertEqual(len(candidate.included_detail_refs), 1)
        self.assertEqual(len(candidate.omitted_detail_refs), 1)
        self.assertTrue(candidate.fragmented)
        self.assertIn("omit_details", candidate.reconstruction_operations)
        for detail_ref in candidate.included_detail_refs:
            self.assertIn(
                known_detail_text[detail_ref].rstrip("."),
                candidate.reconstructed_scene,
            )
        omitted_text = known_detail_text[candidate.omitted_detail_refs[0]].rstrip(".")
        self.assertNotIn(omitted_text, candidate.reconstructed_scene)

    def test_blended_recollection_retains_all_trace_lineage(self):
        first = self.trace()
        second = MemoryTrace(
            subject_id=first.subject_id,
            version=0,
            protected_evidence=(self.evidence("corridor"),),
            gist="A later conversation took place in the corridor",
            details=(
                TraceDetail(
                    detail_id="detail:corridor-henry",
                    text="Henry mentioned the apparatus",
                    cue_terms=("henry", "apparatus"),
                ),
            ),
            strength=0.70,
            accessibility=0.66,
            familiarity=0.74,
            competing_trace_ids=(first.trace_id,),
        )
        episode = RetrievalEpisode(
            episode_id="episode-blend",
            subject_id=first.subject_id,
            tick=25,
            cue_text="Henry and the apparatus",
            candidate_trace_ids=(first.trace_id, second.trace_id),
            context_refs=("context:discussion",),
            subject_state_digest="sha256:blend-state",
        )
        candidate = reconstruct_recollection(
            [first, second],
            episode,
            config=ReconstructionConfig(max_details=2),
        )
        self.assertTrue(candidate.blended)
        self.assertEqual(candidate.trace_ids, (first.trace_id, second.trace_id))
        self.assertEqual(
            candidate.protected_evidence_refs,
            ("evidence:demo", "evidence:corridor"),
        )
        self.assertIn("blend_traces", candidate.reconstruction_operations)

    def test_blended_detail_lineage_names_exact_source_trace(self):
        first = self.trace()
        second = MemoryTrace(
            subject_id=first.subject_id,
            version=0,
            protected_evidence=(self.evidence("second"),),
            gist="A second related scene",
            details=(
                TraceDetail(
                    detail_id="detail:henry",
                    text="Henry spoke near the doorway",
                    cue_terms=("henry", "doorway"),
                ),
            ),
            strength=0.71,
            accessibility=0.69,
            familiarity=0.72,
        )
        episode = RetrievalEpisode(
            episode_id="episode-detail-lineage",
            subject_id=first.subject_id,
            tick=27,
            cue_text="Henry doorway apparatus",
            candidate_trace_ids=(first.trace_id, second.trace_id),
        )
        candidate = reconstruct_recollection(
            [first, second],
            episode,
            config=ReconstructionConfig(max_details=3),
        )
        self.assertTrue(
            any(ref.startswith(first.trace_id + ":") for ref in candidate.included_detail_refs)
        )
        self.assertTrue(
            any(ref.startswith(second.trace_id + ":") for ref in candidate.included_detail_refs)
        )
        self.assertEqual(
            len(candidate.included_detail_refs),
            len(set(candidate.included_detail_refs)),
        )

    def test_episode_candidate_set_must_exactly_match_supplied_traces(self):
        trace = self.trace()
        episode = RetrievalEpisode(
            episode_id="episode-mismatch",
            subject_id=trace.subject_id,
            tick=2,
            cue_text="laboratory",
            candidate_trace_ids=(trace.trace_id, "trace:missing"),
        )
        with self.assertRaises(ValueError):
            reconstruct_recollection([trace], episode)

    def test_reconstruction_rejects_cross_subject_trace(self):
        trace = self.trace()
        other = MemoryTrace(
            subject_id="different-subject",
            version=0,
            protected_evidence=(self.evidence("other"),),
            gist="Another event",
        )
        episode = RetrievalEpisode(
            episode_id="episode-cross-subject",
            subject_id=trace.subject_id,
            tick=3,
            cue_text="event",
            candidate_trace_ids=(trace.trace_id, other.trace_id),
        )
        with self.assertRaises(ValueError):
            reconstruct_recollection([trace, other], episode)


if __name__ == "__main__":
    unittest.main()
