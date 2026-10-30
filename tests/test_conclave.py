"""Acceptance tests for the opt-in Conclave kernel and its authority boundary."""
import tempfile
import unittest
from pathlib import Path

from doctor_lives.conclave import (
    Conclave, Stimulus, GEOMANCY_NAMES, SPOKES, _add_figures,
)
from doctor_lives.store import BrainStore


class ConclaveKernelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "brain.sqlite3"
        self.store = BrainStore(self.path)
        self.kernel = Conclave(self.store, enabled=True)
        self.stimulus = Stimulus(
            source_event_id="report:raven001",
            source_kind="reported",
            context_key="garden_1",
            text="A raven flew through the cold moonlight over the garden.",
        )

    def _event_fixture(self, id_, *, verified: bool):
        # Mirror canonical _ingest_verified_laboratory semantics. A WORLD
        # report is external=True, NOT a verified firsthand observation.
        source = ("laboratory-home:observe:fixture" if verified
                  else "laboratory-home:report:fixture")
        with self.store.transaction() as db:
            db.execute(
                """INSERT INTO events
                (id,tick,created_at,kind,source,payload_json,evidence_class,
                 external,confidence,parent_id)
                VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (id_, 2, "2026-10-29T00:00:00+00:00",
                 "observation" if verified else "report", source, "{}",
                 "lived_runtime_memory" if verified else "external_statement",
                 0 if verified else 1, 1.0, None),
            )
            if verified:
                db.execute(
                    """INSERT INTO memories
                    (id,created_tick,updated_tick,kind,text,source,
                     evidence_class,external,confidence,authored,base_salience,
                     rehearsal_count,tags_json,active,source_event_id)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    ("mem:" + id_, 2, 2, "observation", "A verified perception",
                     source, "lived_runtime_memory", 0, 1.0, 0,
                     0.6, 0, "[]", 1, id_),
                )

    def test_opt_in_requires_canonical_store(self):
        with self.assertRaises(PermissionError):
            Conclave(self.store)
        with self.assertRaises(TypeError):
            Conclave(str(self.path), enabled=True)

    def test_five_distinct_historical_methods_emit_non_authoritative_readings(self):
        readings = self.kernel.interpret(self.stimulus)
        self.assertEqual(len(readings), 5)
        self.assertEqual(len({r.tradition_id for r in readings}), 5)
        self.assertEqual(len(SPOKES), 5)
        self.assertTrue(all(r.source_kind == "reported" for r in readings))
        self.assertTrue(all(r.source_work and r.question for r in readings))
        self.assertTrue(all(r.state == "generated" for r in readings))
        self.assertTrue(all(r.truth_status == "neither" for r in readings))
        wheel = next(r for r in readings if r.tradition_id == "agrippan-wheel")
        self.assertIn("intellectual=unassigned", wheel.method_trace)
        self.assertIn("composed_causal_edge=forbidden", wheel.method_trace)

    def test_replay_is_idempotent_and_preserves_state(self):
        initial = self.kernel.interpret(self.stimulus)
        rid = initial[0].id
        self.kernel.transition(rid, "contested", reason="rival symbolic reading")
        self.kernel.add_support(
            rid, evidence_ref="report:s1", direction="for",
            source_kind="reported", note="a person's testimony",
        )
        again = self.kernel.interpret(self.stimulus)
        self.assertEqual([r.id for r in initial], [r.id for r in again])
        self.assertEqual(again[0].state, "contested")
        self.assertEqual(again[0].truth_status, "supported")
        with self.store.connect() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM conclave_readings"
            ).fetchone()[0], 5)
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM conclave_transitions"
            ).fetchone()[0], 1)

    def test_persisted_both_neither_contradiction_and_dormancy(self):
        first, second = self.kernel.interpret(
            self.stimulus, spokes=("agrippan-wheel", "llullian-ars"))
        self.kernel.mark_conflict(
            first.id, second.id, conflict_type="methodological",
            note="correspondence versus constrained question",
        )
        self.kernel.add_support(
            first.id, evidence_ref="report:yes", direction="for",
            source_kind="reported", note="symbolic testimony",
        )
        self.kernel.add_support(
            first.id, evidence_ref="report:no", direction="against",
            source_kind="reported", note="counter-testimony",
        )
        self.kernel.transition(second.id, "dormant", reason="not pressing")
        reopened = Conclave(BrainStore(self.path), enabled=True)
        rows = {r.id: r for r in reopened.readings("garden_1")}
        self.assertEqual(rows[first.id].truth_status, "both")
        self.assertEqual(rows[second.id].truth_status, "neither")
        self.assertEqual(rows[second.id].state, "dormant")
        self.assertEqual(len(reopened.conflicts("garden_1")), 1)
        self.assertEqual(reopened.conflicts("garden_1")[0]["conflict_type"],
                         "methodological")

    def test_world_verified_without_actual_canonical_event_denied(self):
        with self.assertRaises(PermissionError):
            self.kernel.interpret(Stimulus(
                "world:fiction", "world_verified", "garden_1", "fire"
            ))
        self._event_fixture("world:report1", verified=False)
        with self.assertRaises(PermissionError):
            self.kernel.interpret(Stimulus(
                "world:report1", "world_verified", "garden_1", "fire"
            ))
        self._event_fixture("world:real1", verified=True)
        admitted = self.kernel.interpret(Stimulus(
            "world:real1", "world_verified", "garden_1", "fire"
        ), spokes=("agrippan-wheel",))
        self.assertEqual(admitted[0].source_kind, "world_verified")

    def test_no_dream_source_laundering(self):
        dream = Stimulus("dream:d1", "dreamed", "sleep_1",
                         "A raven made the moon into a stone.")
        readings = self.kernel.interpret(dream)
        self.assertTrue(readings)
        self.assertTrue(all(r.source_kind == "dreamed" for r in readings))
        with self.assertRaises(PermissionError):
            self.kernel.add_support(
                readings[0].id, evidence_ref="dream:d1", direction="for",
                source_kind="world_verified", note="false receipt",
            )
        self.assertEqual(self.kernel.readings("sleep_1")[0].truth_status, "neither")

    def test_explicit_uninterpretability_and_independent_opt_out(self):
        blank_symbol = Stimulus("report:dry", "reported", "ordinary",
                                "A receipt was stamped.")
        result = self.kernel.interpret(
            blank_symbol, spokes=("agrippan-wheel",))
        self.assertEqual(result, ())
        self.assertEqual(self.kernel.interpret(blank_symbol, spokes=()), ())
        self.assertEqual(self.kernel.readings("ordinary"), ())

    def test_invalid_provenance_and_budgets(self):
        with self.assertRaises(ValueError):
            self.kernel.interpret(Stimulus("a", "world_actual", "b", "x"))
        with self.assertRaises(ValueError):
            self.kernel.interpret(self.stimulus, spokes=("unreviewed",))
        with self.assertRaises(ValueError):
            self.kernel.interpret(self.stimulus, spokes=("llullian-ars",) * 2)
        with self.assertRaises(ValueError):
            self.kernel.interpret(self.stimulus, max_spokes=99)

    def test_conflicts_need_same_context_and_do_not_collapse(self):
        a = self.kernel.interpret(
            self.stimulus, spokes=("llullian-ars",))[0]
        other = self.kernel.interpret(
            Stimulus("report:other", "reported", "street", "A moon"),
            spokes=("llullian-ars",))[0]
        with self.assertRaises(ValueError):
            self.kernel.mark_conflict(a.id, other.id, conflict_type="symbolic",
                                      note="different contexts")
        self.assertEqual(len(self.kernel.readings("garden_1")), 1)

    def test_mnemonic_cues_not_autobiographical_writes(self):
        self.kernel.interpret(self.stimulus)
        cues = self.kernel.cues("garden_1")
        self.assertTrue(cues)
        self.assertIn("report:raven001", cues)
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM memories").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM policy_decisions").fetchone()[0], 0)

    def test_geomantic_shield_parity_and_determinism(self):
        a = self.kernel.interpret(self.stimulus, spokes=("geomantic-shield",))[0]
        b = self.kernel.interpret(self.stimulus, spokes=("geomantic-shield",))[0]
        self.assertEqual(a.id, b.id)
        self.assertEqual(a.method_trace, b.method_trace)
        self.assertIn("judge=", a.method_trace)
        self.assertEqual(_add_figures((1, 1, 2, 2), (1, 2, 2, 1)),
                         (2, 1, 2, 1))
        self.assertEqual(len(GEOMANCY_NAMES), 16)
        self.assertEqual(len(set(GEOMANCY_NAMES.values())), 16)
        patterns = {
            "Via": (1, 1, 1, 1),
            "Populus": (2, 2, 2, 2),
            "Conjunctio": (2, 1, 1, 2),
            "Carcer": (1, 2, 2, 1),
            "Fortuna Major": (2, 2, 1, 1),
            "Fortuna Minor": (1, 1, 2, 2),
            "Acquisitio": (2, 1, 2, 1),
            "Amissio": (1, 2, 1, 2),
            "Laetitia": (1, 2, 2, 2),
            "Tristitia": (2, 2, 2, 1),
            "Puella": (1, 2, 1, 1),
            "Puer": (1, 1, 2, 1),
            "Albus": (2, 2, 1, 2),
            "Rubeus": (2, 1, 2, 2),
            "Caput Draconis": (2, 1, 1, 1),
            "Cauda Draconis": (1, 1, 1, 2),
        }
        self.assertEqual(
            {name: dots for dots, name in GEOMANCY_NAMES.items()},
            patterns,
        )
        # A valid Judge must have an even number of single dots.
        allowed_judges = {"Via", "Populus", "Conjunctio", "Carcer",
                          "Fortuna Major", "Fortuna Minor",
                          "Acquisitio", "Amissio"}
        self.assertEqual(
            {name for dots, name in GEOMANCY_NAMES.items()
             if sum(dot == 1 for dot in dots) % 2 == 0},
            allowed_judges,
        )

    def test_states_are_audit_history_not_deletions(self):
        r = self.kernel.interpret(self.stimulus, spokes=("brunian-memory",))[0]
        self.kernel.transition(r.id, "noticed", reason="cue noticed")
        self.kernel.transition(r.id, "withdrawn", reason="unhelpful")
        self.assertEqual(self.kernel.cues("garden_1"), ())
        self.assertEqual(self.kernel.readings("garden_1")[0].state, "withdrawn")
        with self.store.connect() as db:
            changes = list(db.execute(
                "SELECT old_state,new_state FROM conclave_transitions ORDER BY revision"
            ))
        self.assertEqual([(x[0], x[1]) for x in changes],
                         [("generated", "noticed"), ("noticed", "withdrawn")])


if __name__ == "__main__":
    unittest.main()
