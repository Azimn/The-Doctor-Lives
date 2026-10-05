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
    PhenomenalMode,
    PrivacyState,
    Recollection,
    SubjectiveSourceAttribution,
    SubjectiveSourceKind,
    VividnessBand,
)


class PhenomenalSchemaTests(unittest.TestCase):
    def make_event(self, *, subject_id: str = "subject-alpha") -> PhenomenalEvent:
        return PhenomenalEvent(
            event_id="phen-001",
            tick=12,
            subject_id=subject_id,
            mode=PhenomenalMode.FEELING,
            awareness=AwarenessLevel.CONSCIOUS,
            canonical_first_person="Something about this makes me uneasy.",
            privacy=PrivacyState.PRIVATE,
            projection_rule_version="uppb-p1",
            source_state_digest="sha256:test-state",
            objective_provenance=ObjectiveProvenance(
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
            source_state_refs=("need:threat", "relationship:visitor"),
            source_event_refs=("event-2",),
            object_refs=("actor:visitor",),
        )

    def test_schema_is_character_agnostic(self):
        event = self.make_event(subject_id="non-pretorius-test-subject")
        self.assertEqual(event.subject_id, "non-pretorius-test-subject")
        self.assertNotIn("pretorius", event.subject_text.lower())

    def test_event_is_immutable(self):
        event = self.make_event()
        with self.assertRaises(FrozenInstanceError):
            event.canonical_first_person = "Changed"  # type: ignore[misc]

    def test_subject_text_exposes_subjective_content_not_audit_provenance(self):
        event = self.make_event()
        self.assertEqual(
            event.subject_text,
            "Something about this makes me uneasy.",
        )
        self.assertNotIn("lived_runtime_memory", event.subject_text)
        self.assertNotIn("record-7", event.subject_text)
        self.assertNotIn("0.91", event.subject_text)

    def test_objective_and_subjective_provenance_can_disagree(self):
        event = PhenomenalEvent(
            event_id="memory-phen-001",
            tick=33,
            subject_id="subject-alpha",
            mode=PhenomenalMode.RECOLLECTION,
            awareness=AwarenessLevel.FOCAL,
            canonical_first_person="I remember Henry standing beside me.",
            privacy=PrivacyState.POTENTIALLY_REPORTABLE,
            projection_rule_version="uppb-p1",
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
        self.assertEqual(
            decoded["subjective_source"]["kind"],
            SubjectiveSourceKind.LIVED,
        )

    def test_recollection_requires_recollection_mode_and_trace(self):
        event = PhenomenalEvent(
            event_id="recollect-1",
            tick=4,
            subject_id="subject-alpha",
            mode=PhenomenalMode.RECOLLECTION,
            awareness=AwarenessLevel.CONSCIOUS,
            canonical_first_person="I remember the demonstration.",
            privacy=PrivacyState.PRIVATE,
            projection_rule_version="uppb-p1",
            source_state_digest="sha256:state",
            objective_provenance=ObjectiveProvenance(
                evidence_class="reconstructed_preawakening_memory",
                source="protected-archive",
            ),
        )
        recollection = Recollection(
            event=event,
            trace_refs=("trace-1",),
            subjective_source=SubjectiveSourceAttribution(
                SubjectiveSourceKind.LIVED,
                CertaintyBand.MODERATE,
            ),
            subjective_certainty=CertaintyBand.HIGH,
            vividness=VividnessBand.VIVID,
        )
        self.assertEqual(recollection.subject_text, "I remember the demonstration.")

        with self.assertRaises(ValueError):
            Recollection(
                event=event,
                trace_refs=(),
                subjective_source=SubjectiveSourceAttribution(),
                subjective_certainty=CertaintyBand.MODERATE,
                vividness=VividnessBand.MODERATE,
            )

    def test_invalid_objective_confidence_fails_closed(self):
        with self.assertRaises(ValueError):
            ObjectiveProvenance(
                evidence_class="test",
                source="test",
                confidence=1.5,
            )


if __name__ == "__main__":
    unittest.main()
