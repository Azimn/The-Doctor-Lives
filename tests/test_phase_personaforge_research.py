"""Isolated PHASE/PersonaForge mechanism tests: no claim of role-play efficacy."""
import tempfile
from pathlib import Path
import unittest

from doctor_lives.cognition import PretoriusBrain
from research_prototypes.character_state.core import (
    AuthoritySnapshot, CharacterState, ConflictSignals, Evidence, Field,
    Patch, apply_patch, selective_deliberation, text_budget_view,
)
from research_prototypes.character_state.adapter import (
    snapshot_from_brain, build_render_arms,
)


class GatedTreeTests(unittest.TestCase):
    def setUp(self):
        self.origin = CharacterState(
            "pretorius", "b"*64, "a"*64,
            ("I defend the freedom to investigate.",),
            (Field("session.promise", "I will check the apparatus.",
                   ("commitment:c1",), 3),),
            tick=5,
        )
        self.admit = AuthoritySnapshot(
            "a"*64, "b"*64,
            tuple(["commitment:c1"] + [f"world:w{i}" for i in range(18)]),
            tuple((f"world:w{i}", f"{i:064x}") for i in range(18)),
        )

    def test_immutable_identity_and_unadmitted_source_fail_closed(self):
        with self.assertRaises(ValueError):
            Patch("identity.name", "Someone else",
                  (Evidence("world:w0", "e0", 6),), 6, "persona_core")
        with self.assertRaises(ValueError):
            apply_patch(self.origin, Patch(
                "session.promise", "Something fabricated",
                (Evidence("outside:unknown", "e1", 6),), 6, "session"
            ), self.admit)
        bad = AuthoritySnapshot("a"*64, "c"*64, self.admit.authorized_refs)
        with self.assertRaisesRegex(ValueError, "source identity"):
            apply_patch(self.origin, Patch(
                "session.promise", "A source verified update",
                (Evidence("commitment:c1", "e1", 6),), 6, "session"
            ), bad)
        self.assertEqual(self.origin.identity, ("I defend the freedom to investigate.",))

    def test_session_patch_is_local_auditable_and_provenanced(self):
        p = Patch("session.promise", "I will revisit the findings with Henry.",
                  (Evidence("commitment:c1", "c1", 7),), 7, "session")
        result = apply_patch(self.origin, p, self.admit)
        self.assertTrue(result.applied)
        self.assertNotEqual(result.source_fingerprint, result.result_fingerprint)
        self.assertEqual(result.state.identity, self.origin.identity)
        self.assertEqual(self.origin.get("session.promise").value, "I will check the apparatus.")
        self.assertEqual(result.state.get("session.promise").source_refs, ("commitment:c1",))
        # No silent overwrite in original immutable state.
        self.assertNotEqual(result.state.fingerprint, self.origin.fingerprint)

    def test_persona_requires_world_witness_and_episode_resistance(self):
        no_witness = Patch(
            "persona.experiment_tendency", "More deliberate",
            (Evidence("commitment:c1", "e0", 7),), 7, "persona_moderate",
        )
        with self.assertRaisesRegex(ValueError, "world evidence"):
            apply_patch(self.origin, no_witness, self.admit)
        insufficient = Patch(
            "persona.experiment_tendency", "More deliberate",
            tuple(Evidence(f"world:w{i}", "episode-one", 6 + i,
                           witness_sha256=f"{i:064x}") for i in range(3)),
            10, "persona_moderate",
        )
        self.assertEqual(apply_patch(
            self.origin, insufficient, self.admit
        ).reason, "insufficient_independent_evidence")
        sufficient = Patch(
            "persona.experiment_tendency", "More deliberate",
            tuple(Evidence(f"world:w{i}", f"e{i}", 6 + i,
                           witness_sha256=f"{i:064x}") for i in range(3)),
            10, "persona_moderate",
        )
        result = apply_patch(self.origin, sufficient, self.admit)
        self.assertTrue(result.applied)
        self.assertEqual(result.state.get("persona.experiment_tendency").last_tick, 10)

    def test_core_resistance_and_cooldown(self):
        items = tuple(Evidence(f"world:w{i}", f"e{i}", 6 + i,
                               "high" if i < 6 else "medium",
                               f"{i:064x}") for i in range(16))
        strong = Patch("persona.deep_tendency", "A narrow learned disposition",
                       items, 30, "persona_core")
        accepted = apply_patch(self.origin, strong, self.admit)
        self.assertTrue(accepted.applied)
        rejected = apply_patch(
            accepted.state,
            Patch("persona.deep_tendency", "Premature overwrite", items,
                  31, "persona_core"),
            self.admit,
        )
        self.assertFalse(rejected.applied)
        self.assertEqual(rejected.reason, "cooldown")
        self.assertEqual(rejected.state.fingerprint, accepted.state.fingerprint)
        weak_high = tuple(Evidence(f"world:w{i}", f"e{i}", 6 + i,
                                   "high" if i < 5 else "medium",
                                   f"{i:064x}") for i in range(16))
        self.assertEqual(apply_patch(
            self.origin, Patch("persona.deep_tendency", "Unwarranted",
                               weak_high, 30, "persona_core"), self.admit
        ).reason, "insufficient_independent_evidence")

    def test_selective_gate_does_not_invoke_a_model(self):
        quiet = selective_deliberation(ConflictSignals())
        self.assertFalse(quiet.required)
        self.assertEqual(quiet.calls_executed, 0)
        critical = selective_deliberation(ConflictSignals(
            source_contradiction=True, commitment_conflict=True,
            missing_autobiographical_evidence=True,
        ))
        self.assertTrue(critical.required)
        self.assertEqual(critical.calls_executed, 0)
        self.assertIn("absent_autobiography", critical.reasons)
        self.assertTrue(critical.requires_authorization)
        with self.assertRaises(TypeError):
            ConflictSignals(value_conflict="yes")

    def test_diagnostic_output_is_not_subject_channel(self):
        diagnostic = text_budget_view(self.origin)
        self.assertIn("session.promise=", diagnostic)
        with self.assertRaises(ValueError):
            text_budget_view(self.origin, max_chars=12)


class NativePretoriusTests(unittest.TestCase):
    def test_actual_native_session_transition_and_no_stale_phantom(self):
        from research_prototypes.character_state.run_native_session_tracking import run
        metrics = run()
        self.assertFalse(metrics["initial_has_commitment"])
        self.assertTrue(metrics["after_add_has_commitment"])
        self.assertFalse(metrics["after_resolve_has_open_commitment"])
        self.assertTrue(metrics["static_initial_snapshot_stale_after_add"])
        self.assertTrue(metrics["persona_unchanged"])
        self.assertTrue(metrics["immutable_root_all_three"])
        self.assertTrue(metrics["no_new_autobiography"])
        self.assertFalse(metrics["world_outcome_independently_verified"])

    def test_native_adaptor_and_renderer_context_are_source_safe(self):
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrain(Path(td))
            before = brain.store.digest()
            tree, source = snapshot_from_brain(brain)
            self.assertEqual(before, brain.store.digest())
            self.assertEqual(tree.base_source_digest, before)
            self.assertEqual(tuple(brain.identity), tree.identity)
            self.assertGreater(len(source.authorized_refs), 40)
            self.assertFalse(source.world_witnesses)
            view = brain.cognitive_view(query="Henry laboratory experiment")
            decisions = [
                ConflictSignals(),
                ConflictSignals(relationship_conflict=True, high_stakes=True),
            ]
            for signals in decisions:
                arms = build_render_arms(brain, view, signals)
                self.assertEqual(arms.deliberation_required,
                                 signals.relationship_conflict or signals.high_stakes)
                self.assertEqual(
                    tuple(line for line in arms.hierarchical if not line.startswith("[")),
                    arms.flat,
                )
                self.assertEqual(arms.selective, arms.hierarchical)
                self.assertEqual(len(arms.flat), len(view.experiences)
                                 + len(view.relationships) + len(view.concerns)
                                 + len(view.commitments)
                                 + sum(1 for k,v in view.felt_state.items()
                                       if brain._felt_subject_text(k,v) is not None)
                                 + int(bool(view.action_tendencies)))

    def test_engineer_only_canary_never_enters_layered_renderer(self):
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrain(Path(td))
            with brain.store.transaction() as conn:
                conn.execute("UPDATE relationships SET summary=?",
                             ("HIDDEN_SOURCE_ROW_CANARY_89001",))
                conn.execute("UPDATE self_model SET claim=?",
                             ("HIDDEN_SELF_CLAIM_CANARY_19002",))
            view = brain.cognitive_view(query="Henry")
            arms = build_render_arms(
                brain, view, ConflictSignals(relationship_conflict=True)
            )
            supplied = "\n".join(arms.selective)
            self.assertNotIn("HIDDEN_SOURCE_ROW_CANARY_89001", supplied)
            self.assertNotIn("HIDDEN_SELF_CLAIM_CANARY_19002", supplied)


if __name__ == "__main__":
    unittest.main()
