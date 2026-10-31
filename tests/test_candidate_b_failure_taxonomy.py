"""Independent monitor categories, without simulation or waiting four hours."""
import unittest
from doctor_lives.lab_failure_taxonomy import HealthSample, classify


class CandidateBFailureTaxonomy(unittest.TestCase):
    def sample(self, **changes):
        data = dict(process_alive=True, elapsed_seconds=120.0,
                    heartbeat_age_seconds=5.0,
                    last_physical_task_age_seconds=30.0,
                    verified_completed_tasks=1)
        data.update(changes)
        return HealthSample(**data)

    def test_process_exited_is_crash_not_stall(self):
        self.assertEqual(classify(self.sample(process_alive=False)), "crash")

    def test_alive_with_stale_heartbeat_is_stall(self):
        self.assertEqual(classify(self.sample(
            heartbeat_age_seconds=120.0)), "stall")

    def test_live_host_no_task_is_silent_skip(self):
        self.assertEqual(classify(self.sample(
            elapsed_seconds=650, verified_completed_tasks=0,
            last_physical_task_age_seconds=None)), "silent_skip")

    def test_live_host_task_gone_quiet_is_silent_skip(self):
        self.assertEqual(classify(self.sample(
            elapsed_seconds=1100,
            last_physical_task_age_seconds=950)), "silent_skip")

    def test_working_with_recent_receipt_is_active(self):
        self.assertEqual(classify(self.sample()), "active")

    def test_short_initialization_is_not_false_stall(self):
        self.assertEqual(classify(self.sample(
            elapsed_seconds=10, heartbeat_age_seconds=None)), "startup")

    def test_invalid_signed_task_count_rejected(self):
        with self.assertRaises(ValueError):
            classify(self.sample(verified_completed_tasks=-1))


if __name__ == "__main__":
    unittest.main()
