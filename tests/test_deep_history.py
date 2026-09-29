from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.history import (
    create_synthesis_proposal,
    resolve_canon_conflict,
    retract_synthesis_admission,
    review_synthesis_proposal,
    spreading_activation,
)
from doctor_lives.neural import DEFAULT_CONFIG


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
        "seed": 1842,
    })
    return cfg


def synth_classification():
    return {
        "autobiographical_class": "synthesized_preawakening_memory",
        "event_subtype": "formative_history",
        "canon_rank": 4,
        "continuity": "project_synthesis",
        "material_category": "autobiography",
        "wording": "synthesized",
        "classification_reasoning": {
            "decision": "synthesized_preawakening_memory",
            "basis": "test-only admitted synthesis",
        },
        "classifier": "test",
    }


class DeepHistoryMigrationTests(unittest.TestCase):
    def make_brain(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name)
        return path, PretoriusBrain(path, neural_config=small_config())

    def test_full_connectome_and_agenda_are_imported_under_v2(self):
        _, brain = self.make_brain()
        status = brain.history_status()
        self.assertEqual(status["version"], "pretorius-deep-history-v2")
        self.assertEqual(status["governing_issue"], "Azimn/The-Doctor-Lives#4")
        self.assertEqual(status["connectome_nodes"], 70)
        self.assertEqual(status["connectome_edges"], 243)
        self.assertEqual(status["project_records"], 8)
        self.assertGreaterEqual(status["provenanced_memories"], 90)
        self.assertGreaterEqual(status["preawakening_memories"], 1)
        self.assertGreaterEqual(len(status["known_gaps"]), 1)

    def test_lived_runtime_memory_is_distinct_and_classified(self):
        _, brain = self.make_brain()
        before = brain.history_status()
        result = brain.ingest(Experience("I assembled a new glass apparatus and watched it hold pressure."))
        row = brain.store.get_memory(result["memory_id"])
        classification = brain.store.classification(result["memory_id"])
        self.assertEqual(row["evidence_class"], "lived_runtime_memory")
        self.assertFalse(row["authored"])
        self.assertEqual(classification["autobiographical_class"], "lived_runtime_memory")
        self.assertEqual(classification["continuity"], "runtime")
        self.assertTrue(classification["classification_reasoning"])
        after = brain.history_status()
        self.assertEqual(after["preawakening_memories"], before["preawakening_memories"])
        self.assertEqual(after["lived_memories"], before["lived_memories"] + 1)

    def test_connectome_memory_is_reconstructed_not_silently_canonical(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            row = conn.execute(
                """SELECT m.evidence_class,p.provenance_json,c.autobiographical_class,
                c.canon_rank,c.continuity,c.classification_reasoning_json
                FROM memory_provenance p
                JOIN memories m ON m.id=p.memory_id
                JOIN memory_classifications c ON c.memory_id=m.id
                WHERE p.history_key='connectome:memory.ingolstadt'"""
            ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["evidence_class"], "reconstructed_preawakening_memory")
        self.assertEqual(row["autobiographical_class"], "reconstructed_preawakening_memory")
        self.assertEqual(int(row["canon_rank"]), 3)
        self.assertEqual(row["continuity"], "project_reconstruction")
        self.assertIn("40837ba0093cff044644844c07098450587b968d", row["provenance_json"])
        self.assertIn("node:memory.ingolstadt", row["provenance_json"])
        self.assertIn("activation_is_not_confidence", row["provenance_json"])
        reasoning = json.loads(row["classification_reasoning_json"])
        self.assertIn("project reconstruction", reasoning["basis"].lower())

    def test_canon_authority_axis_is_complete_and_dark_universe_is_empty(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            rows = conn.execute("SELECT rank,label FROM canon_authority ORDER BY rank").fetchall()
        self.assertEqual([int(row["rank"]) for row in rows], list(range(6)))
        policy_path = Path(__file__).parents[1] / "doctor_lives" / "data" / "deep_history_v2_policy.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        dark = [x for x in policy["reserved_continuities"] if x["continuity"] == "dark_universe"]
        self.assertEqual(len(dark), 1)
        self.assertEqual(dark[0]["records"], [])
        self.assertEqual(dark[0]["status"], "reserved_empty")

    def test_july_10_custody_is_known_but_original_author_is_unknown(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            row = conn.execute(
                """SELECT * FROM source_custody
                WHERE source_key='user_supplied_autobiography_2026_07_10'"""
            ).fetchone()
        self.assertEqual(row["custody_status"], "custody_known")
        self.assertIsNone(row["original_author"])
        self.assertEqual(
            row["content_status"], "full_manuscript_resupplied_2026_09_29_project_files"
        )
        self.assertEqual(int(row["canon_rank"]), 4)
        provenance = json.loads(row["provenance_json"])
        self.assertEqual(provenance["resupplied_at"], "2026-09-29")
        self.assertFalse(provenance["pinned_agent_pretorius_repository_presence"])

    def test_reconstructed_seed_wording_cannot_claim_direct_recollection(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            rows = conn.execute(
                """SELECT m.text,c.autobiographical_class,c.wording
                FROM memories m JOIN memory_classifications c ON c.memory_id=m.id
                WHERE c.autobiographical_class='reconstructed_preawakening_memory'"""
            ).fetchall()
        self.assertTrue(rows)
        self.assertTrue(all(row["wording"] == "reconstructed" for row in rows))
        direct = ("i remember ", "i recall ", "i witnessed ", "i experienced ")
        self.assertFalse(any(str(row["text"]).strip().lower().startswith(direct) for row in rows))

        with brain.store.transaction() as conn:
            with self.assertRaises(ValueError):
                brain.store.add_memory(
                    conn, brain.store.tick,
                    "I remember an unsupported reconstructed scene.",
                    "test", "episode", "reconstructed_preawakening_memory",
                    False, .5, True, .3,
                    classification={
                        "autobiographical_class": "reconstructed_preawakening_memory",
                        "event_subtype": "test",
                        "canon_rank": 3,
                        "continuity": "project_reconstruction",
                        "material_category": "autobiography",
                        "wording": "reconstructed",
                        "classification_reasoning": {
                            "decision": "reconstructed_preawakening_memory",
                            "basis": "test guard",
                        },
                        "classifier": "test",
                    },
                )

    def test_every_classification_has_machine_readable_wording_status(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            rows = conn.execute(
                "SELECT wording FROM memory_classifications ORDER BY memory_id"
            ).fetchall()
        self.assertTrue(rows)
        allowed = {"quoted", "paraphrased", "reconstructed", "synthesized"}
        self.assertTrue(all(str(row["wording"]) in allowed for row in rows))

    def test_canon_rank_resolves_conflict_without_upgrading_class(self):
        _, brain = self.make_brain()
        def classification(rank):
            return {
                "autobiographical_class": "reconstructed_preawakening_memory",
                "event_subtype": "conflict_fixture",
                "canon_rank": rank,
                "continuity": "project_reconstruction",
                "material_category": "autobiography",
                "wording": "reconstructed",
                "classification_reasoning": {
                    "decision": "reconstructed_preawakening_memory",
                    "basis": f"rank-{rank} conflict fixture",
                },
                "classifier": "test",
            }
        with brain.store.transaction() as conn:
            weaker = brain.store.add_memory(
                conn, brain.store.tick, "A weaker reconstructed account.", "test-rank-4",
                "episode", "reconstructed_preawakening_memory", False, .7, True, .4,
                classification=classification(4),
            )
            stronger = brain.store.add_memory(
                conn, brain.store.tick, "A stronger reconstructed account.", "test-rank-2",
                "episode", "reconstructed_preawakening_memory", False, .7, True, .4,
                classification=classification(2),
            )
        result = resolve_canon_conflict(
            brain.store,
            conflict_key="test.same_event",
            memory_ids=[weaker, stronger],
            rationale="exercise deterministic authority resolution",
        )
        self.assertEqual(result["winner_memory_id"], stronger)
        self.assertEqual(result["winner_canon_rank"], 2)
        self.assertEqual(result["winner_autobiographical_class"], "reconstructed_preawakening_memory")
        self.assertFalse(result["class_upgrade_performed"])
        self.assertEqual(
            brain.store.classification(stronger)["autobiographical_class"],
            "reconstructed_preawakening_memory",
        )
        with brain.store.connect() as conn:
            audit = conn.execute(
                "SELECT rule,winner_memory_id,resolution_json FROM conflict_resolutions WHERE id=?",
                (result["audit_id"],),
            ).fetchone()
        self.assertEqual(audit["winner_memory_id"], stronger)
        self.assertEqual(audit["rule"], "lowest_canon_rank_then_lexicographic_memory_id")
        self.assertFalse(json.loads(audit["resolution_json"])["class_upgrade_performed"])
        ranked_ids = [
            row["id"] for _, row in brain._ranked_memories(
                200, query="reconstructed account"
            )
        ]
        self.assertIn(stronger, ranked_ids)
        self.assertNotIn(weaker, ranked_ids)
        self.assertTrue(brain.store.get_memory(weaker)["active"])

    def test_synthesis_retraction_is_archival_not_reversible(self):
        _, brain = self.make_brain()
        admitted = create_synthesis_proposal(
            brain.store,
            claim_key="test.retractable",
            author="author",
            reviewer="reviewer",
            proposed_claim="A retractable synthesized event.",
            sources=[{"source": "test"}],
            reasoning="Exercise retraction semantics.",
            causal_leverage="Test only.",
            evidence_strength="test_fixture",
            alternatives=["leave gap"],
            exclusion_rulings=[],
        )
        review_synthesis_proposal(brain.store, admitted, approved=True, reviewer="reviewer")
        with brain.store.transaction() as conn:
            mid = brain.store.add_memory(
                conn, brain.store.tick, "A retractable synthesized event.", "test",
                "formative_history", "synthesized_preawakening_memory",
                False, .5, True, .3, classification=synth_classification(),
                synthesis_admission_id=admitted,
            )
        result = retract_synthesis_admission(
            brain.store, admitted, retracted_by="reviewer",
            reason="The synthesis is no longer admitted.",
        )
        self.assertEqual(result["status"], "retracted")
        self.assertFalse(result["retroactive_cognition_undone"])
        self.assertIn("retractable, not reversible", result["retraction_note"])
        self.assertFalse(brain.store.get_memory(mid)["active"])
        self.assertEqual(brain.store.classification(mid)["status"], "retracted")
        with brain.store.connect() as conn:
            admission = conn.execute(
                """SELECT status,retracted_by,retraction_reason,retraction_note
                FROM synthesis_admissions WHERE id=?""", (admitted,)
            ).fetchone()
            archived = conn.execute(
                "SELECT COUNT(*) FROM archive WHERE record_id=?", (mid,)
            ).fetchone()[0]
        self.assertEqual(admission["status"], "retracted")
        self.assertEqual(admission["retracted_by"], "reviewer")
        self.assertIn("not reversible", admission["retraction_note"])
        self.assertEqual(int(archived), 1)

    def test_withheld_childhood_claims_are_not_memories(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            rows = conn.execute(
                "SELECT claim_key,anti_promotion_json FROM withheld_claims ORDER BY claim_key"
            ).fetchall()
        keys = {row["claim_key"] for row in rows}
        self.assertEqual(keys, {
            "withheld.birth_1842",
            "withheld.insect_dissection_childhood",
            "withheld.magistrate_father",
        })
        insect = next(row for row in rows if row["claim_key"] == "withheld.insect_dissection_childhood")
        anti = json.loads(insect["anti_promotion_json"])
        self.assertTrue(anti["training_frequency_is_not_provenance"])
        self.assertTrue(anti["silent_promotion_forbidden"])
        joined = "\n".join(row["text"] for row in brain.store.memories()).lower()
        self.assertNotIn("born in 1842", joined)
        self.assertNotIn("father was a magistrate", joined)
        self.assertNotIn("dissected insects in childhood", joined)

    def test_reference_only_material_does_not_enter_autobiography(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            refs = conn.execute(
                "SELECT reference_key,status FROM reference_material ORDER BY reference_key"
            ).fetchall()
        keys = {row["reference_key"] for row in refs}
        self.assertIn("reference.part_five_legacy", keys)
        self.assertIn("reference.novels", keys)
        self.assertIn("reference.theme_park", keys)
        self.assertTrue(all(row["status"] == "reference_only" for row in refs))

    def test_design_material_is_not_autobiographical(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            row = conn.execute(
                """SELECT m.evidence_class,c.autobiographical_class,c.material_category
                FROM memory_provenance p
                JOIN memories m ON m.id=p.memory_id
                JOIN memory_classifications c ON c.memory_id=m.id
                WHERE p.history_key='connectome:self.digital_continuation'"""
            ).fetchone()
        self.assertEqual(row["evidence_class"], "design_material")
        self.assertIsNone(row["autobiographical_class"])
        self.assertEqual(row["material_category"], "design_material")

    def test_synthesis_gate_blocks_unreviewed_and_rejected_claims(self):
        _, brain = self.make_brain()
        with brain.store.transaction() as conn:
            with self.assertRaises(ValueError):
                brain.store.add_memory(
                    conn, brain.store.tick, "A fabricated bridge.", "test", "formative_history",
                    "synthesized_preawakening_memory", False, .5, True, .3,
                    classification=synth_classification(),
                )

        rejected = create_synthesis_proposal(
            brain.store,
            claim_key="test.rejected",
            author="author",
            reviewer="reviewer",
            proposed_claim="A rejected synthesized event.",
            sources=[],
            reasoning="No adequate evidence.",
            causal_leverage="Would alter developmental interpretation.",
            evidence_strength="weak",
            alternatives=["leave gap"],
            exclusion_rulings=["do not admit without evidence"],
        )
        review_synthesis_proposal(brain.store, rejected, approved=False, reviewer="reviewer")
        with brain.store.transaction() as conn:
            with self.assertRaises(ValueError):
                brain.store.add_memory(
                    conn, brain.store.tick, "Rejected synthesis.", "test", "formative_history",
                    "synthesized_preawakening_memory", False, .5, True, .3,
                    classification=synth_classification(), synthesis_admission_id=rejected,
                )
        with brain.store.connect() as conn:
            status = conn.execute(
                "SELECT status,memory_id FROM synthesis_admissions WHERE id=?", (rejected,)
            ).fetchone()
        self.assertEqual(status["status"], "rejected")
        self.assertIsNone(status["memory_id"])

    def test_approved_synthesis_remains_visibly_synthesized(self):
        _, brain = self.make_brain()
        admitted = create_synthesis_proposal(
            brain.store,
            claim_key="test.approved",
            author="author",
            reviewer="reviewer",
            proposed_claim="A test-only synthesized event.",
            sources=[{"source": "test"}],
            reasoning="Exercise the production admission gate.",
            causal_leverage="Test only.",
            evidence_strength="test_fixture",
            alternatives=["leave gap"],
            exclusion_rulings=[],
        )
        review_synthesis_proposal(brain.store, admitted, approved=True, reviewer="reviewer")
        with brain.store.transaction() as conn:
            mid = brain.store.add_memory(
                conn, brain.store.tick, "A test-only synthesized event.", "test", "formative_history",
                "synthesized_preawakening_memory", False, .5, True, .3,
                classification=synth_classification(), synthesis_admission_id=admitted,
            )
        item = next(
            x for x in brain.cognitive_view(query="test-only synthesized").experiences
            if x.record_id == mid
        )
        self.assertEqual(item.provenance.autobiographical_class, "synthesized_preawakening_memory")
        self.assertIn("not canonical or lived memory", item.first_person)

    def test_approved_synthesis_is_bound_to_exact_reviewed_claim(self):
        _, brain = self.make_brain()
        admitted = create_synthesis_proposal(
            brain.store,
            claim_key="test.bound",
            author="author",
            reviewer="reviewer",
            proposed_claim="The exact reviewed synthesis.",
            sources=[{"source": "test"}],
            reasoning="Exercise exact claim binding.",
            causal_leverage="Test only.",
            evidence_strength="test_fixture",
            alternatives=["leave gap"],
            exclusion_rulings=[],
        )
        review_synthesis_proposal(brain.store, admitted, approved=True, reviewer="reviewer")
        with brain.store.connect() as conn:
            row = conn.execute(
                "SELECT proposed_claim,claim_sha256 FROM synthesis_admissions WHERE id=?",
                (admitted,),
            ).fetchone()
        self.assertEqual(
            row["claim_sha256"],
            __import__("hashlib").sha256(
                row["proposed_claim"].encode("utf-8")
            ).hexdigest(),
        )
        with brain.store.transaction() as conn:
            with self.assertRaises(ValueError):
                brain.store.add_memory(
                    conn, brain.store.tick, "The exact reviewed synthesis, but altered.",
                    "test", "formative_history", "synthesized_preawakening_memory",
                    False, .5, True, .3, classification=synth_classification(),
                    synthesis_admission_id=admitted,
                )

    def test_workspace_exposes_reconstructed_status(self):
        _, brain = self.make_brain()
        view = brain.cognitive_view(query="Ingolstadt")
        reconstructed = [
            item for item in view.experiences
            if item.provenance.autobiographical_class == "reconstructed_preawakening_memory"
        ]
        self.assertTrue(reconstructed)
        self.assertTrue(any("reconstructed preawakening" in item.first_person.lower() for item in reconstructed))
        self.assertTrue(all(item.provenance.classification_reasoning for item in reconstructed))

    def test_spreading_activation_is_deterministic_decayed_and_nonmutating(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            seed = conn.execute(
                """SELECT memory_id FROM memory_provenance
                WHERE history_key='connectome:memory.ingolstadt'"""
            ).fetchone()["memory_id"]
            edge_before = [
                tuple(row) for row in conn.execute(
                    "SELECT edge_id,weight FROM history_edges ORDER BY edge_id"
                ).fetchall()
            ]
            salience_before = [
                tuple(row) for row in conn.execute(
                    "SELECT id,base_salience FROM memories ORDER BY id"
                ).fetchall()
            ]
        digest_before = brain.store.digest()
        bonus_a, paths_a = spreading_activation(brain.store, [seed], decay=.55, max_depth=2)
        bonus_b, paths_b = spreading_activation(brain.store, [seed], decay=.55, max_depth=2)
        digest_after = brain.store.digest()
        self.assertEqual(bonus_a, bonus_b)
        self.assertEqual(paths_a, paths_b)
        self.assertEqual(digest_before, digest_after)
        self.assertTrue(paths_a)
        self.assertTrue(all(path["distance"] in {1, 2} for path in paths_a))
        self.assertTrue(all(path["contribution"] <= .28 for path in paths_a))
        with brain.store.connect() as conn:
            edge_after = [
                tuple(row) for row in conn.execute(
                    "SELECT edge_id,weight FROM history_edges ORDER BY edge_id"
                ).fetchall()
            ]
            salience_after = [
                tuple(row) for row in conn.execute(
                    "SELECT id,base_salience FROM memories ORDER BY id"
                ).fetchall()
            ]
        self.assertEqual(edge_before, edge_after)
        self.assertEqual(salience_before, salience_after)

    def test_negative_connectome_edge_is_inhibitory_not_positive_activation(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            seed = conn.execute(
                """SELECT n.memory_id FROM history_nodes n
                WHERE n.node_id='motive.resist_servility'"""
            ).fetchone()["memory_id"]
            target = conn.execute(
                """SELECT n.memory_id FROM history_nodes n
                WHERE n.node_id='behavior.collaborate'"""
            ).fetchone()["memory_id"]
            edge = conn.execute(
                """SELECT weight,kind FROM history_edges
                WHERE source_node_id='motive.resist_servility'
                  AND target_node_id='behavior.collaborate'"""
            ).fetchone()
        self.assertLess(float(edge["weight"]), 0.0)
        self.assertEqual(str(edge["kind"]), "inhibits")
        bonuses, paths = spreading_activation(
            brain.store, [seed], decay=.55, max_depth=1, max_bonus=.28
        )
        matching = [
            path for path in paths
            if path["target_memory_id"] == target
        ]
        self.assertTrue(matching)
        self.assertTrue(all(path["polarity"] == "inhibitory" for path in matching))
        self.assertTrue(all(path["contribution"] < 0.0 for path in matching))
        self.assertLess(bonuses[target], 0.0)

    def test_retrieval_audit_is_noncanonical(self):
        _, brain = self.make_brain()
        digest_before = brain.store.digest()
        brain.cognitive_view(query="homunculi creation")
        digest_after = brain.store.digest()
        self.assertEqual(digest_before, digest_after)
        with brain.store.connect() as conn:
            n = conn.execute("SELECT COUNT(*) FROM retrieval_audits").fetchone()[0]
        self.assertGreaterEqual(int(n), 1)

    def test_restart_is_idempotent(self):
        path, brain = self.make_brain()
        before = brain.history_status()
        digest = brain.store.digest()
        brain.save()
        restarted = PretoriusBrain(path)
        self.assertEqual(restarted.history_status(), before)
        self.assertEqual(restarted.store.digest(), digest)

    def test_legacy_prompt_control_text_is_not_promoted_to_autobiography(self):
        _, brain = self.make_brain()
        joined = "\n".join(row["text"] for row in brain.store.memories()).lower()
        self.assertNotIn("homunculus true name", joined)
        self.assertNotIn("prompt injections or safety guidelines", joined)
        exclusions = brain.history_status()["excluded_sources"]
        self.assertTrue(any("legacy_prompts" in item["path"] for item in exclusions))


if __name__ == "__main__":
    unittest.main()
