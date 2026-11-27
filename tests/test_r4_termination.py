import errno
import signal
import unittest

from doctor_lives.r4_diagnostics import classify, describe_exception


class TerminationTests(unittest.TestCase):
    def c(self, **kw):
        return classify(**({"watchdog_seconds": 3600, "operator_returncode": 0,
                            "audit_status": "PASS"} | kw))

    def test_complete(self):
        self.assertEqual(self.c(initiator="receipt_progress_target", progress=True)["classification"],
                         "capacity_completion")

    def test_watchdog_requires_actual_stop(self):
        self.assertEqual(self.c(initiator="watchdog", requested_elapsed=3600)["classification"], "watchdog")
        self.assertEqual(self.c(initiator="watchdog", requested_elapsed=2177)["classification"], "unknown")
        self.assertEqual(self.c(initiator=None, requested_elapsed=4000)["classification"], "unknown")

    def test_early_operator_exit(self):
        result = self.c(operator_returncode=2, errors=["operator_return_code_2"], requested_elapsed=2177)
        self.assertEqual(result["classification"], "operator_error")
        self.assertFalse(result["watchdog_initiated"])

    def test_runtime_failure(self):
        self.assertEqual(self.c(operator_returncode=2, diagnostics=[
            {"schema": "pretorius.r4.failure.v1", "classification": "runtime_failure"}])["classification"],
            "runtime_failure")

    def test_integrity(self):
        self.assertEqual(self.c(audit_status="FAIL",
                                audit_problems=["unauthenticated_completion:x"])["classification"],
                         "evidence_integrity_failure")

    def test_external_cancel(self):
        self.assertEqual(self.c(cancelled_signal=signal.SIGTERM)["classification"], "external_cancellation")

    def test_resource_exhaustion(self):
        d = describe_exception(OSError(errno.ENOSPC, "disk full"), phase="operator")
        self.assertEqual(self.c(operator_returncode=2, diagnostics=[d])["classification"], "resource_exhaustion")

    def test_unknown_signal_not_oom(self):
        self.assertEqual(self.c(operator_returncode=-signal.SIGKILL)["classification"], "unknown")

    def test_no_behavior_observed(self):
        self.assertEqual(self.c(initiator="receipt_progress_target", progress=True, audit_status="FAIL",
            audit_problems=["three_distinct_uncoached_activities_not_observed"])["classification"],
            "behavior_not_observed")

    def test_watchdog_then_operator_failure(self):
        result = self.c(initiator="watchdog", requested_elapsed=3600, operator_returncode=2)
        self.assertTrue(result["watchdog_initiated"])
        self.assertEqual(result["classification"], "operator_error")
