from __future__ import annotations

import unittest

from doctor_lives.phenomenology import (
    AwarenessLevel,
    ObjectiveProvenance,
    PhenomenalMode,
    PrivacyState,
)
from doctor_lives.projection import (
    BodilySignal,
    PhenomenalLeakError,
    ProjectionContext,
    assert_subject_text_safe,
    implementation_leaks,
    project_appraisal_feeling,
    project_bodily_sensation,
    project_impulse,
    project_uncertainty,
    project_relationship_feeling,
    project_concern,
    project_commitment,
)


class DeterministicProjectionTests(unittest.TestCase):
    def setUp(self):
        self.context = ProjectionContext(
            subject_id="subject-beta",
            tick=9,
            source_state_digest="sha256:mechanistic-state",
            awareness=AwarenessLevel.CONSCIOUS,
            privacy=PrivacyState.PRIVATE,
        )
        self.provenance = ObjectiveProvenance(
            evidence_class="mechanistic_projection",
            source="test-state",
            confidence=1.0,
            record_ids=("engineer-only-record",),
        )

    def test_projection_context_rejects_invalid_enum_values(self):
        with self.assertRaises(TypeError):
            ProjectionContext(
                subject_id="subject-beta",
                tick=1,
                source_state_digest="sha256:test",
                awareness="conscious",  # type: ignore[arg-type]
            )
        with self.assertRaises(TypeError):
            ProjectionContext(
                subject_id="subject-beta",
                tick=1,
                source_state_digest="sha256:test",
                privacy="private",  # type: ignore[arg-type]
            )

    def test_bodily_projection_hides_raw_value(self):
        event = project_bodily_sensation(
            context=self.context,
            signal=BodilySignal.COLD,
            level=0.31,
            provenance=self.provenance,
            source_state_refs=("thermal_discomfort",),
        )
        self.assertEqual(event.mode, PhenomenalMode.BODILY_SENSATION)
        self.assertEqual(event.subject_text, "I feel a little chilly.")
        self.assertNotIn("0.31", event.subject_text)
        self.assertNotIn("thermal_discomfort", event.subject_text)
        self.assertEqual(event.source_state_refs, ("thermal_discomfort",))

    def test_projection_is_deterministic_for_fixed_inputs(self):
        a = project_bodily_sensation(
            context=self.context,
            signal=BodilySignal.FATIGUE,
            level=0.72,
            provenance=self.provenance,
        )
        b = project_bodily_sensation(
            context=self.context,
            signal=BodilySignal.FATIGUE,
            level=0.72,
            provenance=self.provenance,
        )
        self.assertEqual(a, b)
        self.assertEqual(a.event_id, b.event_id)

    def test_appraisal_changes_subjective_meaning_with_control(self):
        low_control = project_appraisal_feeling(
            context=self.context,
            valence=-0.4,
            arousal=0.8,
            threat=0.8,
            control=0.2,
            novelty=0.3,
            provenance=self.provenance,
        )
        high_control = project_appraisal_feeling(
            context=self.context,
            valence=-0.4,
            arousal=0.8,
            threat=0.8,
            control=0.8,
            novelty=0.3,
            provenance=self.provenance,
        )
        self.assertEqual(low_control.subject_text, "I feel cornered.")
        self.assertEqual(
            high_control.subject_text,
            "This feels dangerous, but I feel ready to face it.",
        )
        self.assertNotEqual(low_control.event_id, high_control.event_id)

    def test_impulse_is_subjective_and_not_an_action(self):
        event = project_impulse(
            context=self.context,
            action_phrase="leave the room",
            strength=0.68,
            provenance=self.provenance,
        )
        self.assertEqual(event.mode, PhenomenalMode.IMPULSE)
        self.assertEqual(event.subject_text, "I strongly want to leave the room.")
        self.assertEqual(event.privacy, PrivacyState.PRIVATE)

    def test_uncertainty_uses_qualitative_first_person_certainty(self):
        uncertain = project_uncertainty(
            context=self.context,
            proposition="Henry intends to cooperate",
            confidence=0.52,
            provenance=self.provenance,
        )
        confident = project_uncertainty(
            context=self.context,
            proposition="Henry intends to cooperate",
            confidence=0.93,
            provenance=self.provenance,
        )
        self.assertEqual(uncertain.mode, PhenomenalMode.UNCERTAINTY)
        self.assertEqual(
            uncertain.subject_text,
            "I am not sure whether Henry intends to cooperate.",
        )
        self.assertNotIn("0.52", uncertain.subject_text)
        self.assertEqual(confident.mode, PhenomenalMode.BELIEF)
        self.assertEqual(
            confident.subject_text,
            "I am almost certain that Henry intends to cooperate.",
        )
        self.assertNotIn("0.93", confident.subject_text)

    def test_relationship_projection_can_hold_affiliation_and_distrust_together(self):
        event = project_relationship_feeling(
            context=self.context,
            actor_name="Morgan",
            trust=0.18,
            affiliation=0.77,
            provenance=self.provenance,
            source_state_refs=("relationship:morgan",),
        )
        self.assertEqual(event.mode, PhenomenalMode.FEELING)
        self.assertEqual(
            event.subject_text,
            "I want to remain close to Morgan, but I do not trust them.",
        )
        self.assertNotIn("0.18", event.subject_text)
        self.assertNotIn("0.77", event.subject_text)

    def test_concern_projection_does_not_expose_urgency_value(self):
        event = project_concern(
            context=self.context,
            subject_phrase="the unfinished apparatus",
            urgency=0.67,
            provenance=self.provenance,
            source_state_refs=("concern:apparatus",),
        )
        self.assertEqual(event.mode, PhenomenalMode.CONCERN)
        self.assertEqual(
            event.subject_text,
            "I am preoccupied with the unfinished apparatus.",
        )
        self.assertNotIn("0.67", event.subject_text)

    def test_commitment_projection_is_intention_not_external_expression(self):
        event = project_commitment(
            context=self.context,
            action_phrase="finish the apparatus",
            importance=0.74,
            provenance=self.provenance,
            source_state_refs=("commitment:apparatus",),
        )
        self.assertEqual(event.mode, PhenomenalMode.INTENTION)
        self.assertEqual(event.privacy, PrivacyState.PRIVATE)
        self.assertEqual(event.subject_text, "I am determined to finish the apparatus.")

    def test_leak_detector_blocks_implementation_native_content(self):
        text = "My state_pressure is 0.4 and memory_id=12."
        hits = implementation_leaks(text)
        self.assertIn("state_pressure", hits)
        self.assertIn("memory_id", hits)
        self.assertIn("raw_numeric_assignment", hits)
        with self.assertRaises(PhenomenalLeakError):
            assert_subject_text_safe(text)

    def test_leak_detector_allows_external_human_readable_measurement(self):
        assert_subject_text_safe("The thermometer reads thirteen degrees.")


if __name__ == "__main__":
    unittest.main()
