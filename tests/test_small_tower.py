"""Cross-repository mechanical integration, not an uncoached life claim."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from doctor_lives.small_tower import initialize_tower,run_tower_pulse,SmallTowerSource,PENDING
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.neural import DEFAULT_CONFIG

@unittest.skipUnless(os.getenv("PRETORIUS_TOWER_SOURCE"),"Exact original Tower source required")
class OriginalTowerTests(unittest.TestCase):
    def test_real_canonical_pulse_and_replay(self):
        source=Path(os.environ["PRETORIUS_TOWER_SOURCE"])
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            state=root/"doctor"
            world=root/"tower.json"
            cfg=dict(DEFAULT_CONFIG)
            cfg.update(neurons=128,sensory_dim=64,avg_recurrent_degree=8,input_degree=4,action_population_size=8,seed=1842)
            initialize_tower(state,source,world,epoch="test-epoch",neural_config=cfg)
            result=run_tower_pulse(state,source,world,authorize=True,steps=100)
            self.assertTrue(result["same_canonical_brain"])
            self.assertFalse(result["parallel_tower_chooser"])
            self.assertTrue(result["policy_id"])
            self.assertTrue(all(x.startswith("I ") for x in result["subject_narrative"]))
            runtime=SixOrganRuntime.open(state)
            store=runtime._port.brain.store
            choice=json.loads(store.meta("small-tower:choice:"+result["policy_id"]))
            self.assertIn(choice["choice"],choice["offers"])
            self.assertTrue(choice["observation_id"])
            self.assertIsNone(store.meta(PENDING))
            self.assertTrue(any(m["source"].startswith("virtual-world:small-tower:") for m in store.memories()))
            self.assertTrue(SmallTowerSource(source,world).snapshot()["revision"])
            with self.assertRaises(PermissionError):
                run_tower_pulse(state,source,world,steps=1)
            with self.assertRaises(FileExistsError):
                initialize_tower(state,source,world,epoch="different")
