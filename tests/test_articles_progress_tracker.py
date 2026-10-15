"""Regression checks for the standalone 34-Article progress tracker."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.render_articles_progress import (
    GATES, OUTPUT, SOURCE, WEIGHTS, progress_bar, render, score, validate,
)


class ProgressTrackerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_exactly_34_canonical_slots_and_separate_qualification(self):
        validate(self.data)
        self.assertEqual(
            [item["id"] for item in self.data["articles"]],
            list(range(1, 35)),
        )
        self.assertEqual(set(WEIGHTS), set(GATES))
        self.assertEqual(sum(WEIGHTS.values()), 100)
        self.assertEqual(len({a["title"] for a in self.data["articles"]}), 34)
        for item in self.data["articles"]:
            self.assertGreaterEqual(score(item), 1)
            self.assertLessEqual(score(item), 100)
            self.assertNotIn("progress", item)
            self.assertIn(item["qualification"],
                          ("Unassessable", "Supported", "Unsupported"))

    def test_generated_dashboard_cannot_drift_from_machine_record(self):
        expected = render(self.data)
        self.assertEqual(OUTPUT.read_text(encoding="utf-8"), expected)
        self.assertEqual(expected.count("| Unassessable |"), 34)

    def test_minimum_and_maximum_require_correct_gates(self):
        trial = deepcopy(self.data["articles"][0])
        trial["gates"] = {key: False for key in GATES}
        self.assertEqual(score(trial), 1)
        trial["gates"] = {key: True for key in GATES}
        self.assertEqual(score(trial), 100)

    def test_bar_is_20_blocks_with_exact_percent_label(self):
        for points in (1, 10, 35, 46, 60, 80, 100):
            self.assertEqual(len(progress_bar(points)), 20)
        self.assertEqual(progress_bar(100), "█" * 20)
        self.assertEqual(progress_bar(1), "░" * 20)
        for invalid in (0, 101, -1, 1.5, True):
            with self.assertRaises(ValueError):
                progress_bar(invalid)

    def test_bad_id_or_unsubstantiated_progress_rejected(self):
        wrong = deepcopy(self.data)
        wrong["articles"][4]["id"] = 4
        with self.assertRaisesRegex(ValueError, "original"):
            validate(wrong)

        wrong = deepcopy(self.data)
        wrong["articles"][5]["gates"]["independent_transfer"] = True
        with self.assertRaisesRegex(ValueError, "Transfer"):
            validate(wrong)

        wrong = deepcopy(self.data)
        for gate in GATES:
            wrong["articles"][5]["gates"][gate] = True
        validate(wrong)
        self.assertEqual(score(wrong["articles"][5]), 100)

    def test_supported_status_requires_separate_evidence(self):
        wrong = deepcopy(self.data)
        wrong["articles"][0]["qualification"] = "Supported"
        with self.assertRaisesRegex(ValueError, "assessment evidence"):
            validate(wrong)
        wrong["articles"][0]["qualification_evidence"] = [
            "https://example.org/independent-registered-assessment"
        ]
        validate(wrong)

    def test_document_provenance_must_be_explicit(self):
        wrong = deepcopy(self.data)
        wrong["source_document_sha256"] = "not-a-hash"
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            validate(wrong)
        wrong = deepcopy(self.data)
        wrong["articles"][0]["work_refs"] = ["#not-found"]
        with self.assertRaisesRegex(ValueError, "resolve"):
            validate(wrong)


if __name__ == "__main__":
    unittest.main()
