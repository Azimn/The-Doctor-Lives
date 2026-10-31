"""Read-only judge must fail, not invent a third autonomous activity."""
import tempfile
from pathlib import Path
import unittest
from tools.audit_three_uncoached import evaluate


class R4HonestyTests(unittest.TestCase):
    def test_missing_evidence_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate(Path(tmp))
            self.assertEqual(result["status"], "FAIL")
            self.assertFalse(result["three_distinct_uncoached"])
            self.assertEqual(result["distinct_valid_activity_kinds"], [])


if __name__ == "__main__":
    unittest.main()
