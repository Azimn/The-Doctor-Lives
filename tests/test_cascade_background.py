"""Real Doctor cognition under bounded background authority; no model calls."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from doctor_lives.cascade_background import BackgroundLease, BackgroundLedger, operation_lock

DONORS = (importlib.util.find_spec("synthetic_ipseity") is not None
          and importlib.util.find_spec("sensus_artificialis") is not None)


class LeaseContracts(unittest.TestCase):
    def test_numeric_and_identifier_boundaries(self):
        for data in [("bad id", 3, 1, 10, 100), ("x", True, 1, 10, 100),
                     ("x", 3, 4, 10, 100), ("x", 3, 1, 0, 100)]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                BackgroundLease(*data)

    def test_reservation_survives_reopen_and_cannot_refund(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = BackgroundLedger(tmp)
            lease = BackgroundLease("lease", 2, 1, 10, 100)
            ledger.issue(lease)
            ledger.reserve("lease", "w1", 10, 1)
            reopened = BackgroundLedger(tmp)
            with self.assertRaises(RuntimeError):
                reopened.assert_reconciled()
            with reopened.connect() as db:
                self.assertEqual(db.execute("SELECT remaining FROM leases").fetchone()[0], 1)
            with self.assertRaises(RuntimeError):
                reopened.reserve("lease", "w1", 10, 1)

    def test_lease_cannot_be_refilled_or_reconfigured(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = BackgroundLedger(tmp)
            ledger.issue(BackgroundLease("lease", 2, 1, 10, 100))
            ledger.reserve("lease", "w1", 10, 1)
            ledger.issue(BackgroundLease("lease", 2, 1, 10, 100))
            with ledger.connect() as db:
                self.assertEqual(db.execute("SELECT remaining FROM leases").fetchone()[0], 1)
            with self.assertRaises(PermissionError):
                ledger.issue(BackgroundLease("lease", 3, 1, 10, 100))

    def test_failed_receipt_never_reexecutes(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = BackgroundLedger(tmp)
            ledger.issue(BackgroundLease("lease", 2, 1, 10, 100))
            ledger.reserve("lease", "w1", 10, 1)
            ledger.complete("w1", {"error": "synthetic"}, "failed")
            with self.assertRaises(RuntimeError):
                ledger.reserve("lease", "w1", 10, 1)

    def test_foreground_and_background_share_exclusive_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            with operation_lock(tmp):
                with self.assertRaises(RuntimeError):
                    with operation_lock(tmp):
                        pass
            self.assertFalse((Path(tmp) / "cascade-operation.lock").exists())


@unittest.skipUnless(DONORS, "Pinned organ dependencies required")
class ActualBackground(unittest.TestCase):
    def setUp(self):
        from doctor_lives.cascade_preview import CascadePretoriusPreview
        from doctor_lives.neural import DEFAULT_CONFIG
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "three-organ-preview"
        self.cfg = dict(DEFAULT_CONFIG)
        self.cfg.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                        input_degree=4, action_population_size=8)
        self.calls = []
        self.Host = CascadePretoriusPreview

    def host(self):
        return self.Host(self.path, enabled=True, require_governor=False,
                         neural_config=self.cfg,
                         renderer=lambda text: self.calls.append(text) or "I am here.")

    def issue(self, host, total=3):
        host.issue_background_lease(BackgroundLease("lease", total, 1, 10, 1000), authorized=True)

    def wake(self, host, wake="w1", now=10, **kwargs):
        return host.background_wake(lease_id="lease", wake_id=wake,
                                    now_ms=now, authorized=True, **kwargs)

    def test_existing_overdue_commitment_causes_actual_thought(self):
        from doctor_lives.cascade_governance import snapshot_doctor
        with self.host() as host:
            brain = host._doctor.brain
            commitment = brain.add_commitment("Inspect the balance", due_tick=brain.store.tick)
            self.issue(host)
            before = brain.store.tick
            receipt = self.wake(host)
            self.assertEqual(receipt["after_tick"], before + 1)
            self.assertTrue(receipt["policy_decision_ids"])
            self.assertGreater(receipt["elapsed_ns"], 0)
            self.assertLessEqual(receipt["started_unix_ns"], receipt["finished_unix_ns"])
            self.assertEqual(snapshot_doctor(host).open_commitments, 1)
            self.assertEqual(brain.store.open_commitments()[0]["status"], "overdue")
            self.assertEqual(self.calls, [])
            for ident in receipt["policy_decision_ids"]:
                with brain.store.connect() as db:
                    row = db.execute("SELECT trigger FROM policy_decisions WHERE id=?", (ident,)).fetchone()
                    self.assertEqual(row[0], "heartbeat")
            brain.resolve_commitment(commitment, "Inspection complete")
            later = self.wake(host, "w2", 20)
            self.assertFalse(later["policy_decision_ids"])

    def test_completed_wake_replays_receipt_without_cognition_after_restart(self):
        with self.host() as host:
            self.issue(host)
            receipt = self.wake(host)
        with self.host() as host:
            before = host._doctor.brain.store.digest()
            replay = self.wake(host)
            self.assertTrue(replay["replayed_receipt"])
            self.assertEqual(receipt["after_tick"], replay["after_tick"])
            self.assertEqual(before, host._doctor.brain.store.digest())

    def test_missing_authority_does_not_change_brain(self):
        with self.host() as host:
            before = host._doctor.brain.store.digest()
            with self.assertRaises(PermissionError):
                host.background_wake(lease_id="absent", wake_id="w1", now_ms=10)
            with self.assertRaises(PermissionError):
                host.issue_background_lease(BackgroundLease("lease", 3, 1, 10, 1000))
            self.assertEqual(before, host._doctor.brain.store.digest())

    def test_second_host_cannot_load_stale_neural_state(self):
        with self.host():
            with self.assertRaisesRegex(RuntimeError, "reconcile"):
                self.host()
        with self.host() as reopened:
            self.assertEqual(reopened.SUBJECT_ID, "pretorius")

    def test_separate_worker_process_runs_actual_persisted_cognition(self):
        import json
        import subprocess
        import sys
        with self.host() as host:
            brain = host._doctor.brain
            brain.add_commitment("Inspect the apparatus", due_tick=brain.store.tick)
            self.issue(host)
            before = brain.store.tick
        script = '''import json,sys
from doctor_lives.cascade_preview import CascadePretoriusPreview
cfg=json.loads(sys.argv[2])
with CascadePretoriusPreview(sys.argv[1],enabled=True,require_governor=False,
    renderer=lambda text: (_ for _ in ()).throw(RuntimeError("no renderer allowed")),
    neural_config=cfg) as host:
    print(json.dumps(host.background_wake(lease_id="lease",wake_id="subprocess",
        now_ms=10,ticks=1,authorized=True)))
'''
        result = subprocess.run([sys.executable,"-c",script,str(self.path),json.dumps(self.cfg)],
                                check=True,capture_output=True,text=True)
        receipt = json.loads(result.stdout)
        self.assertTrue(receipt["policy_decision_ids"])
        with self.host() as host:
            self.assertEqual(host._doctor.brain.store.tick, before+1)
            self.assertEqual(receipt["after_tick"],before+1)

    def test_budget_expiry_revocation_and_interval_fail_before_brain(self):
        with self.host() as host:
            self.issue(host, total=1)
            self.wake(host)
            before = host._doctor.brain.store.digest()
            for wake, now in [("too-soon", 11), ("no-budget", 20), ("expired", 1001)]:
                with self.subTest(wake=wake), self.assertRaises(PermissionError):
                    self.wake(host, wake, now)
            host._cascade_background.revoke("lease")
            with self.assertRaises(PermissionError):
                self.wake(host, "revoked", 20)
            self.assertEqual(before, host._doctor.brain.store.digest())

    def test_partial_failure_blocks_new_work_and_never_refunds(self):
        with self.host() as host:
            self.issue(host)
            with patch.object(host._doctor.brain, "heartbeat", side_effect=RuntimeError("fault")):
                with self.assertRaisesRegex(RuntimeError, "fault"):
                    self.wake(host)
            with self.assertRaisesRegex(RuntimeError, "reconciliation"):
                self.wake(host, "w2", 20)
            with host._cascade_background.connect() as db:
                self.assertEqual(db.execute("SELECT remaining FROM leases").fetchone()[0], 2)
                self.assertEqual(db.execute("SELECT status FROM wakes").fetchone()[0], "failed")
