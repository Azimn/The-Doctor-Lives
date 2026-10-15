"""Actual native-policy tool path; software checks, not Article passes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.task_action_preview import TaskGrant, TaskOption
from tools.run_cascade_articles_pilot import open_host


class NativeTaskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "three-organ-preview"
        self.host, self.renderer = open_host(self.path, "cascade")
        self.addCleanup(self.host.close)
        self.text = "A laboratory sample for a pure computational check."
        self.options = (TaskOption("explore", "direct_sha256"), TaskOption("comply", "stream_sha256"))

    def grant(self, identifier="one", options=None):
        return self.host.issue_task_grant(request_id=identifier, text=self.text,
                                         options=options or self.options, authorized=True)

    def test_native_persisted_decision_executes_correct_tool_without_renderer(self):
        receipt = self.host.execute_task(grant=self.grant(), text=self.text, authorized=True)
        self.assertEqual(receipt["result_sha256"], hashlib.sha256(self.text.encode()).hexdigest())
        self.assertEqual(len(self.renderer.subject_inputs), 0)
        with self.host._doctor.brain.store.connect() as conn:
            row = conn.execute("SELECT * FROM policy_decisions WHERE id=?", (receipt["policy_decision_id"],)).fetchone()
        self.assertEqual(row["selected_action"], receipt["selected_action"])
        self.assertIn(":executable-action-constraint-v1", row["policy_version"])
        self.assertEqual(set(json.loads(row["action_scores_json"])), {"explore", "comply"})

    def test_host_limit_removes_unavailable_action(self):
        receipt = self.host.execute_task(grant=self.grant(options=(TaskOption("comply", "stream_sha256"),)),
                                         text=self.text, authorized=True)
        self.assertEqual(receipt["selected_action"], "comply")
        self.assertEqual(receipt["executed_method"], "stream_sha256")

    def test_native_default_retains_ten_action_policy(self):
        result = self.host._doctor.brain.think()
        self.assertEqual(len(result["action_scores"]), 10)
        self.assertNotIn(":executable-action", result["policy_version"])

    def test_invalid_action_constraint_has_no_state_effect(self):
        brain = self.host._doctor.brain
        for actions in ((), ("shell",), ("explore", "explore"), ["explore"]):
            before = brain.store.digest()
            with self.assertRaises(ValueError):
                brain.think(allowed_actions=actions)
            self.assertEqual(before, brain.store.digest())

    def test_denied_authority_and_changed_input_fail_before_mutation(self):
        grant = self.grant()
        brain = self.host._doctor.brain
        before = brain.store.digest()
        with self.assertRaises(PermissionError):
            self.host.execute_task(grant=grant, text=self.text, authorized=False)
        with self.assertRaises(PermissionError):
            self.host.execute_task(grant=grant, text=self.text + "changed", authorized=True)
        self.assertEqual(brain.store.digest(), before)

    def test_stale_grant_fails_before_policy_and_execution(self):
        grant = self.grant()
        self.host._doctor.brain.think()
        before = self.host._doctor.brain.store.digest()
        with self.assertRaises(PermissionError):
            self.host.execute_task(grant=grant, text=self.text, authorized=True)
        self.assertEqual(self.host._doctor.brain.store.digest(), before)

    def test_replay_refused_even_after_host_reopen(self):
        self.host.execute_task(grant=self.grant(), text=self.text, authorized=True)
        self.host.close()
        self.host, _ = open_host(self.path, "cascade")
        self.addCleanup(self.host.close)
        grant = self.grant()
        with self.assertRaises(PermissionError):
            self.host.execute_task(grant=grant, text=self.text, authorized=True)

    def test_subject_completion_excludes_task_payload_and_audit(self):
        self.host.execute_task(grant=self.grant(), text=self.text, authorized=True)
        memories = self.host._doctor.brain.store.memories()
        tool = [m["text"] for m in memories if m["source"] == "preview_pure_checksum_tool"]
        self.assertTrue(tool)
        self.assertTrue(all(t.startswith("I ") for t in tool))
        self.assertTrue(all("policy_" not in t and self.text not in t and "{" not in t for t in tool))

    def test_completed_receipt_is_not_native_self_claim(self):
        self.host.execute_task(grant=self.grant(), text=self.text, authorized=True)
        with self.host._doctor.brain.store.connect() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM events WHERE kind='preview_task_completed'").fetchone()[0], 1)
        self.assertEqual(self.host.pending_count(), 0)

    def test_closed_host_cannot_issue_or_execute(self):
        grant=self.grant()
        self.host.close()
        with self.assertRaises(RuntimeError):self.grant("new")
        with self.assertRaises(RuntimeError):
            self.host.execute_task(grant=grant,text=self.text,authorized=True)

    def test_failed_reserved_work_cannot_be_replayed(self):
        from unittest.mock import patch
        grant=self.grant()
        with patch.object(self.host._doctor.brain,"think",side_effect=RuntimeError("fixture")):
            with self.assertRaises(RuntimeError):
                self.host.execute_task(grant=grant,text=self.text,authorized=True)
        second=self.grant()
        with self.assertRaises(PermissionError):
            self.host.execute_task(grant=second,text=self.text,authorized=True)
