"""Read-only append chain and operator input provenance negatives."""
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.preview_ledger import append_activity, read_activity_ledger


class PreviewEvidenceTests(unittest.TestCase):
    def test_append_order_hash_and_external_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root.joinpath("state").mkdir()
            append_activity(root, event="operator_start", external_input=True)
            append_activity(root, event="host_observation", external_input=False,
                            fields={"chosen_by": "host_scheduler", "autonomy_proven": False})
            records = read_activity_ledger(root)
            self.assertEqual(len(records), 2)
            self.assertTrue(records[0]["external_input"])
            self.assertFalse(records[1]["external_input"])
            self.assertEqual(records[1]["previous_sha256"], records[0]["sha256"])
            self.assertEqual(len(records[0]["runtime_code_sha256"]), 64)
            self.assertFalse(records[1]["source_attestation_independent"])

    def test_edit_and_torn_record_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            append_activity(root, event="operator_start", external_input=True)
            log = root / "preview-activity.jsonl"
            record = json.loads(log.read_text())
            record["external_input"] = False
            log.write_text(json.dumps(record) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "digest"):
                read_activity_ledger(root)
            with self.assertRaises(RuntimeError):
                append_activity(root, event="host_observation", external_input=False)
            log.write_text('{"incomplete":', encoding="utf-8")
            with self.assertRaises(RuntimeError):
                read_activity_ledger(root)

    def test_symlink_evidence_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authority = root / "original.sqlite3"
            authority.write_bytes(b"original authority")
            target = root / "preview-activity.jsonl"
            try:
                target.symlink_to(authority)
            except (OSError, NotImplementedError):
                self.skipTest("No symlink permission")
            with self.assertRaises(ValueError):
                append_activity(root, event="operator_start", external_input=True)
            self.assertEqual(authority.read_bytes(), b"original authority")


if __name__ == "__main__":
    unittest.main()
