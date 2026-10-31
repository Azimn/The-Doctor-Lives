"""Independent R4 ledger contract adversarial checks (synthetic, NOT R4 credit).

These fixtures assert the auditor's read-only, fail-closed behavior and real
original Laboratory table SHAPES. They do not simulate an autonomous Doctor
or replace authentic pinned-world CI and independent release acceptance.
"""
import copy
import hashlib
import json
import sqlite3
from pathlib import Path
import tempfile
import unittest

from tools.audit_three_uncoached import (_digest, evaluate_schema_only as evaluate,
                                        evaluate as release_evaluate)


def world_hash(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False).encode("utf-8")).hexdigest()


class IndependentThreeGoalContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="independent-r4-audit-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "state").mkdir()
        self.brain = self.root / "state/brain.sqlite3"
        self.world = self.root / "laboratory.sqlite3"
        with sqlite3.connect(self.brain) as db:
            db.execute("CREATE TABLE policy_decisions (id TEXT PRIMARY KEY, selected_action TEXT, trigger TEXT, state_pressure_json TEXT)")
            db.execute("CREATE TABLE memories (id TEXT PRIMARY KEY, source TEXT, evidence_class TEXT, external INT, active INT, text TEXT)")
            db.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
            for kind, tendency in (("read_book", "explore"), ("rest", "avoid"),
                                   ("work", "explore")):
                db.execute("INSERT INTO policy_decisions VALUES(?,?,?,?)", (
                    "origin_" + kind, tendency, "six_organ_lab_cycle", "{}"))
            db.execute("INSERT INTO policy_decisions VALUES(?,?,?,?)", (
                "motor_work", "repair", "noesis_situated_choice", json.dumps({
                    "motor_event_id": "ng_work01_work",
                    "selector_authority": "original_noesis",
                    "physical_authority": "none",
                    "motor_authorization": "authorized",
                })))
        with sqlite3.connect(self.world) as db:
            for table, column in (("books_events", "payload"),
                                  ("rhythm_events", "envelope"),
                                  ("embodied_events", "envelope")):
                db.execute("CREATE TABLE " + table + " (event_id TEXT PRIMARY KEY, " +
                           column + " TEXT NOT NULL,event_hash TEXT NOT NULL)")
        self._populate()
        self._write_ledger()

    @staticmethod
    def _spec(kind):
        return {"read_book": ("books_events", "bk_read", "read"),
                "rest": ("rhythm_events", "rest_evt", "rest"),
                "work": ("rhythm_events", "ng_work01_work", "repair")}[kind]

    def _populate(self):
        self.records = {}
        with sqlite3.connect(self.world) as lab, sqlite3.connect(self.brain) as brain:
            for kind in ("read_book", "rest", "work"):
                table, eid, operation = self._spec(kind)
                text = {
                    "read_book": "I read a page of Sample. The words before me read: Test.",
                    "rest": "I sit quietly and rest awhile.",
                    "work": "I replace the worn component in my apparatus.",
                }[kind]
                source = {"event_id": eid, "world_epoch": "epoch-real",
                          "lab_id": "lab-real"}
                if kind == "read_book":
                    source.update(action={"op": "read", "book_id": "book:001"},
                                  page_receipt={"page_number": 1})
                else:
                    source.update(op=operation,
                                  station="station:bedroom" if kind == "rest" else "station:bench",
                                  subject={"inner": text, "spoken_aloud": None})
                digest = world_hash(source)
                column = "payload" if table == "books_events" else "envelope"
                lab.execute("INSERT INTO " + table + " VALUES(?,?,?)",
                            (eid, json.dumps(source, sort_keys=True, ensure_ascii=False), digest))
                mid = "memory_" + kind
                brain.execute("INSERT INTO memories VALUES(?,?,?,?,?,?)", (
                    mid, "laboratory-home:action:" + digest,
                    "lived_runtime_memory", 0, 1, text
                ))
                intent = {"id": kind + "01" if kind != "work" else "work01",
                          "world_epoch": "epoch-real",
                          "phase": "complete", "origin_policy_id": "origin_" + kind,
                          ("read_memory_id" if kind == "read_book" else "memory_id"): mid}
                if kind == "work":
                    intent.update(work_policy_id="motor_work", selected_action="repair")
                key = {"read_book": "six_organ_endogenous_book_goal_v1",
                       "rest": "six_organ_native_rest_intention_v1",
                       "work": "six_organ_native_work_intention_v1"}[kind]
                brain.execute("INSERT INTO meta VALUES(?,?)", (key, json.dumps(
                    {"payload": intent, "sha256": _digest(intent)}, sort_keys=True)))
                self.records[kind] = {
                    "kind": kind, "goal_id": intent["id"],
                    "origin_policy_id": "origin_" + kind,
                    "original_tendency": "avoid" if kind == "rest" else "explore",
                    "canonical_memory_id": mid,
                    "canonical_memory_source": "laboratory-home:action:" + digest,
                    "world_table": table, "world_event_id": eid,
                    "world_receipt_sha256": digest,
                    "source_rechecked_by_host": True,
                    "source_attestation_independent": False,
                    "operator_supplied_goal": None,
                }

    def _write_ledger(self):
        data = [("operator_start", {}, True)]
        for kind in ("read_book", "rest", "work"):
            data.append(("native_goal_goal_created", {
                "kind": kind, "goal_id": self.records[kind]["goal_id"]}, False))
            data.append(("native_goal_completed", self.records[kind], False))
        self.events = data
        self._resign()

    def _resign(self):
        prior = "0" * 64
        lines = []
        for num, (event, fields, external) in enumerate(self.events, 1):
            entry = {"sequence": num, "previous_sha256": prior, "event": event,
                     "fields": fields, "external_input": external,
                     "utc": "2026-10-31T19:00:00Z", "beat": "@123"}
            entry["sha256"] = _digest(entry)
            prior = entry["sha256"]
            lines.append(json.dumps(entry, sort_keys=True))
        (self.root / "preview-activity.jsonl").write_text("\n".join(lines) + "\n")

    def _edit(self, sql, params=()):
        with sqlite3.connect(self.brain) as db:
            db.execute(sql, params)

    def _alter_world(self, kind, mutate):
        table, eid, _ = self._spec(kind)
        column = "payload" if table == "books_events" else "envelope"
        with sqlite3.connect(self.world) as lab, sqlite3.connect(self.brain) as brain:
            row = lab.execute("SELECT " + column + " FROM " + table +
                              " WHERE event_id=?", (eid,)).fetchone()
            source = json.loads(row[0])
            mutate(source)
            newhash = world_hash(source)
            lab.execute("UPDATE " + table + " SET " + column +
                        "=?,event_hash=? WHERE event_id=?", (
                            json.dumps(source, sort_keys=True), newhash, eid))
            mid = self.records[kind]["canonical_memory_id"]
            brain.execute("UPDATE memories SET source=? WHERE id=?", (
                "laboratory-home:action:" + newhash, mid))
            rec = self.records[kind]
            rec["world_receipt_sha256"] = newhash
            rec["canonical_memory_source"] = "laboratory-home:action:" + newhash
        self._resign()

    def assert_invalid(self, needle=None):
        report = evaluate(self.root)
        self.assertEqual(report["status"], "FAIL", report)
        self.assertFalse(report["three_distinct_uncoached"])
        if needle:
            self.assertTrue(any(needle in x for x in report["problems"]), report)

    def test_contract_01_valid_shape_only_not_real_world_acceptance(self):
        report = evaluate(self.root)
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["distinct_valid_activity_kinds"],
                         ["read_book", "rest", "work"])
        self.assertFalse(report["independent_human_review_performed"])

    def test_contract_01b_synthetic_source_cannot_pass_release_verifier(self):
        # The same synthetic shape-positive fixture is NEVER a shipping R4
        # pass. Full original source-pinned physics is mandatory.
        strict = release_evaluate(self.root)
        self.assertEqual(strict["status"], "FAIL")
        self.assertFalse(strict["three_distinct_uncoached"])
        self.assertFalse(strict["original_source_world_verified"])
        self.assertTrue(any("original_source_world_authority_not_verified" in p
                            for p in strict["problems"]))

    def test_contract_02_nonexistent_neural_work_action_is_rejected(self):
        self._edit("UPDATE policy_decisions SET selected_action='work' WHERE id='origin_work'")
        self.assert_invalid("unauthenticated_completion")

    def test_contract_03_motor_binding_must_be_authorized(self):
        self._edit("UPDATE policy_decisions SET state_pressure_json=? WHERE id='motor_work'",
                   (json.dumps({"motor_event_id": "ng_work01_work",
                                "selector_authority": "original_noesis",
                                "physical_authority": "none",
                                "motor_authorization": "not_granted"}),))
        self.assert_invalid("unauthenticated_completion")

    def test_contract_04_motor_event_cannot_be_foreign(self):
        self._edit("UPDATE policy_decisions SET state_pressure_json=? WHERE id='motor_work'",
                   (json.dumps({"motor_event_id": "another-action",
                                "selector_authority": "original_noesis",
                                "physical_authority": "none",
                                "motor_authorization": "authorized"}),))
        self.assert_invalid("unauthenticated_completion")

    def test_contract_05_concrete_motor_must_match_real_repair(self):
        self._edit("UPDATE policy_decisions SET selected_action='experiment' WHERE id='motor_work'")
        self.assert_invalid("unauthenticated_completion")

    def test_contract_06_foreign_world_epoch_fails_even_when_rehashed(self):
        self._alter_world("work", lambda source: source.update(world_epoch="other-world"))
        self.assert_invalid("unauthenticated_completion")

    def test_contract_07_forged_lived_memory_text_rejected(self):
        self._edit("UPDATE memories SET text='I invented an unobserved repair' WHERE id='memory_work'")
        self.assert_invalid("unauthenticated_completion")

    def test_contract_08_duplicate_completion_rejected(self):
        self.events.append(copy.deepcopy(self.events[-1]))
        self._resign()
        self.assert_invalid("Duplicate goal completion")

    def test_contract_09_duplicate_goal_origin_rejected(self):
        self.events.insert(-1, copy.deepcopy(self.events[-2]))
        self._resign()
        self.assert_invalid("duplicate_goal_origin")

    def test_contract_10_host_coaching_does_not_count(self):
        self.records["work"]["task_instruction"] = "Perform repair"
        self._resign()
        self.assert_invalid("coached_task_input")

    def test_contract_11_missing_physical_world_receipt_fails_closed(self):
        with sqlite3.connect(self.world) as lab:
            lab.execute("DELETE FROM rhythm_events WHERE event_id='ng_work01_work'")
        self.assert_invalid("unauthenticated_completion")

    def test_contract_12_unread_book_is_not_a_completed_goal(self):
        self._alter_world("read_book", lambda source: source.update(page_receipt=None))
        self.assert_invalid("unauthenticated_completion")

    def test_contract_13_rest_in_the_kitchen_is_not_rest(self):
        self._alter_world("rest", lambda source: source.update(station="station:kitchen"))
        self.assert_invalid("unauthenticated_completion")

    def test_contract_14_false_world_event_hash_is_not_a_receipt(self):
        with sqlite3.connect(self.world) as lab:
            lab.execute("UPDATE rhythm_events SET event_hash=? WHERE event_id=?",
                        ("f" * 64, "ng_work01_work"))
        self.assert_invalid("unauthenticated_completion")


if __name__ == "__main__":
    unittest.main()
