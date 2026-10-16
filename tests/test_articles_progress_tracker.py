"""Regression checks for the standalone 34-Article progress tracker."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.render_articles_progress import (
    ENV_SOURCE, GATES, OUTPUT, SOURCE, WEIGHTS, progress_bar, render, score,
    validate, validate_environment_plan,
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

    def test_article7_causal_controls_are_tied_to_complete_physical_receipts(self):
        motive = self.data["articles"][6]
        self.assertEqual(motive["id"], 7)
        self.assertTrue(motive["gates"]["causal_controls"])
        self.assertFalse(motive["gates"]["independent_transfer"])
        self.assertEqual(score(motive), 80)
        self.assertEqual(motive["qualification"], "Unassessable")
        self.assertIn("Article07-isolated25", motive["work_refs"])
        source = SOURCE.parents[1] / "results" / "cascade" / (
            "ARTICLE_07_ISOLATED_MOTIVATION_CAUSAL_20261016.json")
        report = json.loads(source.read_text(encoding="utf-8"))
        self.assertEqual(report["schema"],
                         "articles34-motivation-isolated-interventions.v1")
        self.assertEqual(report["article"], 7)
        self.assertEqual(report["qualification"], "UNASSESSABLE")
        self.assertEqual(len(report["trials"]), 25)
        self.assertGreater(report["totals"]["native_plus_motives"],
                           report["totals"]["body_motive_lesion"])
        self.assertEqual(report["totals"]["native_plus_motives"], 5)
        self.assertEqual(report["totals"]["numeric_state_rules"], 5)
        for name in report["case_definitions"]:
            arms = [x for x in report["trials"] if x["case"] == name]
            self.assertEqual(len(arms), 5)
            self.assertEqual(len(set(x["engineered_initial_fixture_sha256"]
                                     for x in arms)), 1)
            self.assertEqual(len(set(
                x["episodes"][0]["first_person_frame_sha256"] for x in arms
            )), 1)
            self.assertTrue(all(x["world_verification"] for x in arms))
        dual = next(x for x in report["trials"]
                    if x["case"] == "wear_and_fatigue" and
                    x["arm"] == "native_plus_motives")
        self.assertTrue(dual["completed_scored_sequence"])
        self.assertEqual(dual["actual_sequence"], ["rest", "repair"])
        self.assertLessEqual(dual["total_physical_actions"], 12)

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

    def test_environment_classification_accounts_for_all_34_articles(self):
        venue = json.loads(ENV_SOURCE.read_text(encoding="utf-8"))
        validate_environment_plan(self.data, venue)
        counts = {key: sum(article["minimum_setting"] == key
                           for article in venue["articles"])
                  for key in venue["setting_labels"]}
        self.assertEqual(counts, {"current_lab": 12, "expanded_lab": 15,
                                  "independent_partner": 6, "community": 1})
        self.assertEqual(
            [article["id"] for article in venue["articles"]
             if article["minimum_setting"] in venue["social_settings"]],
            [5, 6, 11, 25, 32, 33, 34])

    def test_environment_changes_do_not_inflate_engineering_progress(self):
        venue = json.loads(ENV_SOURCE.read_text(encoding="utf-8"))
        before = [score(article) for article in self.data["articles"]]
        revised = deepcopy(venue)
        revised["articles"][1]["minimum_setting"] = "current_lab"
        validate_environment_plan(self.data, revised)
        self.assertEqual(
            [score(article) for article in self.data["articles"]], before)
        malformed = deepcopy(venue)
        malformed["articles"][5]["minimum_setting"] = "imaginary_land"
        with self.assertRaisesRegex(ValueError, "Unrecognized"):
            validate_environment_plan(self.data, malformed)

    def test_partner_dependence_must_be_explained(self):
        venue = json.loads(ENV_SOURCE.read_text(encoding="utf-8"))
        malformed = deepcopy(venue)
        malformed["articles"][4]["additional_dependency"] = ""
        with self.assertRaisesRegex(ValueError, "Social Articles"):
            validate_environment_plan(self.data, malformed)

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
