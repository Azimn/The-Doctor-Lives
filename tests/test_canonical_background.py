import tempfile
from pathlib import Path
import unittest
from doctor_lives.canonical_background import BackgroundLease,issue,wake,revoke
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.neural import DEFAULT_CONFIG

class CanonicalBackgroundTests(unittest.TestCase):
    def test_bounded_original_wake_survives_restart(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"doctor"
            cfg=dict(DEFAULT_CONFIG)
            cfg.update(neurons=128,sensory_dim=64,avg_recurrent_degree=8,input_degree=4,action_population_size=8,seed=1842)
            rt=SixOrganRuntime.open(p,neural_config=cfg)
            rt.checkpoint()
            issue(p,BackgroundLease("lease",2,1,10,1000),authorized=True)
            args=dict(lease_id="lease",wake_id="one",now_ms=10,ticks=1,authorized=True)
            first=wake(p,**args)
            self.assertEqual(first["after_tick"],first["before_tick"]+1)
            self.assertEqual(first["external_actions"],0)
            self.assertTrue(wake(p,**args)["replayed_receipt"])
            self.assertEqual(SixOrganRuntime.open(p)._port.brain.store.tick,first["after_tick"])
            with self.assertRaises(PermissionError):
                wake(p,lease_id="lease",wake_id="two",now_ms=11,authorized=True)
            wake(p,lease_id="lease",wake_id="two",now_ms=20,authorized=True)
            with self.assertRaises(PermissionError):
                wake(p,lease_id="lease",wake_id="three",now_ms=30,authorized=True)
            revoke(p,"lease",authorized=True)
