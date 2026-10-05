from __future__ import annotations

import json
import unittest
from dataclasses import FrozenInstanceError

from doctor_lives.phenomenology import (
    AwarenessLevel,
    CertaintyBand,
    IntensityBand,
    ObjectiveProvenance,
    PhenomenalEvent,
    PhenomenalLeakError,
    PhenomenalMode,
    PrivacyState,
    Recollection,
    SubjectiveSourceAttribution,
    SubjectiveSourceKind,
    VividnessBand,
)


class PhenomenalSchemaTests(unittest.TestCase):
    def make_event(
        self,
        *,
        subject_id: str = "subject-alpha",
        provenance: ObjectiveProvenance | None = None,
        text: str = "Something about this makes me uneasy.",
        mode: PhenomenalMode = PhenomenalMode.FEELING,
        source_state_refs=("need:threat", "relationship:visitor"),
        source_event_refs=("event-2",),
        object_refs=("actor:visitor",),
    ) -> PhenomenalEvent:
        return PhenomenalEvent(
            tick=12,
            subject_id=subject_id,
            mode=mode,
            awareness=AwarenessLevel.CONSCIOUS,
            canonical_first_person=text,
            privacy=PrivacyState.PRIVATE,
            projection_rule_version="uppb-p1h",
            source_state_digest="sha256:test-state",
            objective_provenance=provenance
            or ObjectiveProvenance(
                evidence_class="lived_runtime_memory",
                source="world-observation",
                confidence=0.91,
                record_ids=("record-7",),
            ),
            subjective_source=SubjectiveSourceAttribution(
                SubjectiveSourceKind.LIVED,
                CertaintyBand.HIGH,
            ),
            subjective_certainty=CertaintyBand.MODERATE,
            subjective_vividness=VividnessBand.MODERATE,
            subjective_intensity=IntensityBand.MILD,
            source_state_refs=source_state_refs,
            source_event_refs=source_event_refs,
            object_refs=object_refs,
        )

    def test_schema_is_character_agnostic(self):
        event = self.make_event(subject_id="non-pretorius-test-subject")
        self.assertEqual(event.subject_id, "non-pretorius-test-subject")
        self.assertNotIn("pretorius", event.subject_text.lower())

    def test_event_is_deeply_immutable_and_normalizes_mutable_sequences(self):
        record_ids = ["record-7"]
        state_refs = ["need:threat"]
        event_refs = ["event-2"]
        object_refs = ["actor:visitor"]
        provenance = ObjectiveProvenance(
            evidence_class="lived_runtime_memory",
            source="world-observation",
            record_ids=record_ids,
        )
        event = self.make_event(
            provenance=provenance,
            source_state_refs=state_refs,
            source_event_refs=event_refs,
            object_refs=object_refs,
        )

        record_ids.append("record-8")
        state_refs.append("need:other")
        event_refs.append("event-3")
        object_refs.append("actor:other")

        self.assertEqual(provenance.record_ids, ("record-7",))
        self.assertEqual(event.source_state_refs, ("need:threat",))
        self.assertEqual(event.source_event_refs, ("event-2",))
        self.assertEqual(event.object_refs, ("actor:visitor",))

        with self.assertRaises(FrozenInstanceError):
            event.canonical_first_person = "Changed"  # type: ignore[misc]

    def test_invalid_enum_injection_fails_closed(self):
        base = dict(
            tick=1,
            subject_id="subject-alpha",
            awareness=AwarenessLevel.CONSCIOUS,
            canonical_first_person="I feel uneasy.",
            privacy=PrivacyState.PRIVATE,
            projection_rule_version="uppb-p1h",
            source_state_digest="sha256:state",
            objective_provenance=ObjectiveProvenance("test", "test"),
        )
        with self.assertRaises(TypeError):
            PhenomenalEvent(mode="feeling", **base)  # type: ignore[arg-type]

        invalid_awareness = dict(base)
        invalid_awareness["mode"] = PhenomenalMode.FEELING
        invalid_awareness["awareness"] = "conscious"
        with self.assertRaises(TypeError):
            PhenomenalEvent(**invalid_awareness)  # type: ignore[arg-type]

        invalid_privacy = dict(base)
        invalid_privacy["mode"] = PhenomenalMode.FEELING
        invalid_privacy["privacy"] = "private"
        with self.assertRaises(TypeError):
            PhenomenalEvent(**invalid_privacy)  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            SubjectiveSourceAttribution(kind="lived")  # type: ignore[arg-type]

    def test_direct_canonical_leak_construction_is_rejected(self):
        with self.assertRaises(PhenomenalLeakError):
            PhenomenalEvent(
                tick=1,
                subject_id="subject-alpha",
                mode=PhenomenalMode.INTERNAL_THOUGHT,
                awareness=AwarenessLevel.CONSCIOUS,
                canonical_first_person="My state_pressure=0.4 and memory_id=12.",
                privacy=PrivacyState.PRIVATE,
                projection_rule_version="uppb-p1h",
                source_state_digest="sha256:state",
                objective_provenance=ObjectiveProvenance("test", "test"),
            )

    def test_subject_text_exposes_subjective_content_not_audit_provenance(self):
        event = self.make_event()
        self.assertEqual(
            event.subject_text,
            "Something about this makes me uneasy.",
        )
        self.assertNotIn("lived_runtime_memory", event.subject_text)
        self.assertNotIn("record-7", event.subject_text)
        self.assertNotIn("0.91", event.subject_text)

    def test_same_subjective_content_different_provenance_has_distinct_event_identity(self):
        lived = self.make_event(
            provenance=ObjectiveProvenance(
                "lived_runtime_memory",
                "world-observation",
                record_ids=("live-1",),
            ),
            text="I remember Henry standing beside me.",
            mode=PhenomenalMode.RECOLLECTION,
        )
        reconstructed = self.make_event(
            provenance=ObjectiveProvenance(
                "reconstructed_preawakening_memory",
                "archival-reconstruction",
                record_ids=("archive-19",),
            ),
            text="I remember Henry standing beside me.",
            mode=PhenomenalMode.RECOLLECTION,
        )
        self.assertEqual(lived.content_fingerprint, reconstructed.content_fingerprint)
        self.assertNotEqual(lived.lineage_fingerprint, reconstructed.lineage_fingerprint)
        self.assertNotEqual(lived.event_id, reconstructed.event_id)

    def test_objective_and_subjective_provenance_can_disagree(self):
        event = PhenomenalEvent(
            tick=33,
            subject_id="subject-alpha",
            mode=PhenomenalMode.RECOLLECTION,
            awareness=AwarenessLevel.FOCAL,
            canonical_first_person="I remember Henry standing beside me.",
            privacy=PrivacyState.POTENTIALLY_REPORTABLE,
            projection_rule_version="uppb-p1h",
            source_state_digest="sha256:memory-state",
            objective_provenance=ObjectiveProvenance(
                evidence_class="reconstructed_preawakening_memory",
                source="archival-reconstruction",
                confidence=0.78,
                record_ids=("archive-19",),
            ),
            subjective_source=SubjectiveSourceAttribution(
                SubjectiveSourceKind.LIVED,
                CertaintyBand.HIGH,
            ),
            subjective_certainty=CertaintyBand.HIGH,
            subjective_vividness=VividnessBand.VIVID,
            subjective_intensity=IntensityBand.MODERATE,
        )
        self.assertEqual(
            event.objective_provenance.evidence_class,
            "reconstructed_preawakening_memory",
        )
        self.assertEqual(event.subjective_source.kind, SubjectiveSourceKind.LIVED)
        self.assertEqual(event.subject_text, "I remember Henry standing beside me.")

    def test_stable_json_is_deterministic_and_contains_engineer_lineage(self):
        event = self.make_event()
        first = event.stable_json()
        second = event.stable_json()
        self.assertEqual(first, second)
        decoded = json.loads(first)
        self.assertEqual(decoded["subject_id"], "subject-alpha")
        self.assertEqual(
            decoded["objective_provenance"]["record_ids"],
            ["record-7"],
        )
        self.assertEqual(decoded["event_id"], event.event_id)

    def test_recollection_has_one_subjective_provenance_authority(self):
        event = PhenomenalEvent(
            tick=4,
            subject_id="subject-alpha",
            mode=PhenomenalMode.RECOLLECTION,
            awareness=AwarenessLevel.CONSCIOUS,
            canonical_first_person="I remember the demonstration.",
            privacy=PrivacyState.PRIVATE,
            projection_rule_version="uppb-p1h",
            source_state_digest="sha256:state",
            objective_provenance=ObjectiveProvenance(
                evidence_class="reconstructed_preawakening_memory",
                source="protected-archive",
            ),
            subjective_source=SubjectiveSourceAttribution(
                SubjectiveSourceKind.LIVED,
                CertaintyBand.HIGH,
            ),
            subjective_certainty=CertaintyBand.HIGH,
            subjective_vividness=VividnessBand.VIVID,
        )
        refs = ["trace-1"]
        recollection = Recollection(
            event=event,
            trace_refs=refs,
            fragmented=True,
            omitted_detail_refs=["detail-2"],
        )
        refs.append("trace-2")
        self.assertEqual(recollection.trace_refs, ("trace-1",))
        self.assertEqual(recollection.subjective_source, event.subjective_source)
        self.assertEqual(recollection.subjective_certainty, event.subjective_certainty)
        self.assertEqual(recollection.vividness, event.subjective_vividness)
        self.assertEqual(recollection.subject_text, "I remember the demonstration.")

        with self.assertRaises(TypeError):
            Recollection(
                event=event,
                trace_refs=("trace-1",),
                fragmented="yes",  # type: ignore[arg-type]
            )

    def test_recollection_requires_recollection_mode_and_trace(self):
        nonmemory = self.make_event()
        with self.assertRaises(ValueError):
            Recollection(event=nonmemory, trace_refs=("trace-1",))

        memory = self.make_event(
            text="I remember the demonstration.",
            mode=PhenomenalMode.RECOLLECTION,
        )
        with self.assertRaises(ValueError):
            Recollection(event=memory, trace_refs=())

    def test_invalid_objective_confidence_fails_closed(self):
        with self.assertRaises(ValueError):
            ObjectiveProvenance(
                evidence_class="test",
                source="test",
                confidence=1.5,
            )


if __name__ == "__main__":
    unittest.main()
