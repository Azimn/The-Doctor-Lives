"""Candidate B operator session attribution, without original-world fixtures."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from doctor_lives.preview_ledger import read_activity_ledger
from doctor_lives.preview_operator import _unclosed_prior_session, run


class SessionAttributionTests(unittest.TestCase):
    def test_only_actual_unclosed_session_counts(self):
        mode = {"event": "operator_native_mode_selected", "sequence": 1}
        start = {"event": "operator_start", "sequence": 2}
        pulse = {"event": "native_goal_no_situated_goal", "sequence": 3}
        stop = {"event": "operator_stop", "sequence": 4}
        resume = {"event": "operator_resume", "sequence": 5}
        self.assertIsNone(_unclosed_prior_session([]))
        self.assertIsNone(_unclosed_prior_session([mode]))
        self.assertEqual(_unclosed_prior_session([mode, start, pulse]), start)
        self.assertIsNone(_unclosed_prior_session([mode, start, pulse, stop]))
        self.assertIsNone(_unclosed_prior_session([start, stop, mode]))
        self.assertEqual(_unclosed_prior_session(
            [start, stop, resume, pulse]), resume)

    def test_native_fresh_start_is_not_a_false_crash_but_unclosed_prior_is(self):
        with TemporaryDirectory(prefix="candidate-b-operator-session-") as root:
            workspace = Path(root)
            (workspace / "state").mkdir()
            (workspace / "state" / "brain.sqlite3").touch()
            (workspace / "state" / "pretorius_recurrent.npz").touch()
            (workspace / "laboratory.sqlite3").touch()
            donor = workspace / "reviewed-donor"
            donor.mkdir()

            # Deliberate injected termination tests ledger attribution only.
            # They are NOT evidence of an actual external OS hard kill.
            with patch("doctor_lives.preview_operator.verify_donors", return_value=donor), \
                 patch("doctor_lives.preview_operator.select_native", return_value=True), \
                 patch("doctor_lives.preview_operator.configured_source", return_value=donor), \
                 patch("doctor_lives.preview_operator.native_step",
                       side_effect=KeyboardInterrupt("injected process exit")):
                with self.assertRaises(KeyboardInterrupt):
                    run(workspace, native_source=donor)
                fresh = read_activity_ledger(workspace)
                self.assertEqual([x["event"] for x in fresh], [
                    "operator_native_mode_selected", "operator_start",
                    "native_goal_opportunity_started"])
                self.assertNotIn("unexpected_termination",
                                 [x["event"] for x in fresh])
                with self.assertRaises(KeyboardInterrupt):
                    run(workspace, resume=True)

            after = read_activity_ledger(workspace)
            unexpected = [x for x in after if x["event"] == "unexpected_termination"]
            self.assertEqual(len(unexpected), 1)
            self.assertEqual(unexpected[0]["fields"]["previous_sequence"],
                             fresh[-1]["sequence"])
            self.assertEqual(unexpected[0]["fields"]["previous_session_sequence"],
                             fresh[1]["sequence"])
            self.assertIs(unexpected[0]["fields"]["external_os_kill_verified"], False)
            self.assertEqual([x["event"] for x in after][-3:], [
                "unexpected_termination", "operator_resume",
                "native_goal_opportunity_started"])


if __name__ == "__main__":
    unittest.main()
