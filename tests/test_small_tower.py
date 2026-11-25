"""Cross-repository mechanical integration, not an uncoached life claim."""
import gc
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from doctor_lives.small_tower import initialize_tower,run_tower_pulse,run_tower_life,SmallTowerSource,PENDING
from doctor_lives import small_tower
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.neural import DEFAULT_CONFIG

@unittest.skipUnless(os.getenv("PRETORIUS_TOWER_SOURCE"),"Exact original Tower source required")
class OriginalTowerTests(unittest.TestCase):
    def test_real_canonical_pulse_and_replay(self):
        source=Path(os.environ["PRETORIUS_TOWER_SOURCE"])
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._cleanup, temp)
        root=Path(temp.name)
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

    @staticmethod
    def _cleanup(temp):
        gc.collect()
        temp.cleanup()

    def test_unprompted_life_and_post_world_commit_recovery(self):
        source=Path(os.environ["PRETORIUS_TOWER_SOURCE"])
        with tempfile.TemporaryDirectory() as temp:
            state=Path(temp)/"doctor"
            world=Path(temp)/"tower.json"
            cfg=dict(DEFAULT_CONFIG)
            cfg.update(neurons=128,sensory_dim=64,avg_recurrent_degree=8,input_degree=4,
                       action_population_size=8,seed=1842)
            initialize_tower(state,source,world,epoch="life-recovery",neural_config=cfg)
            provider=SmallTowerSource(source,world)
            before=provider.snapshot()
            with self.assertRaises(PermissionError):
                run_tower_life(state,source,world,opportunities=3)
            with self.assertRaises(ValueError):
                run_tower_life(state,source,world,authorize=True,opportunities=0)
            self.assertEqual(provider.snapshot(),before)
            # The first admission reads the initial world. Interrupt only
            # after the original source has committed the reserved request.
            original=small_tower._admit_events
            calls=[]
            def interrupt_after_world(runtime, source_provider, port):
                calls.append(1)
                if len(calls)==2:
                    raise RuntimeError("simulated post-world interruption")
                return original(runtime,source_provider,port)
            with patch.object(small_tower,"_admit_events",side_effect=interrupt_after_world):
                with self.assertRaisesRegex(RuntimeError,"post-world interruption"):
                    run_tower_pulse(state,source,world,authorize=True,steps=100)
            committed=provider.snapshot()
            self.assertNotEqual(committed["revision"],before["revision"])
            pending=json.loads(SixOrganRuntime.open(state)._port.brain.store.meta(PENDING))
            recovered=run_tower_life(state,source,world,authorize=True,opportunities=1)
            self.assertEqual(recovered["pulses"][0]["request_id"],pending["id"])
            self.assertTrue(recovered["pulses"][0]["replayed"])
            self.assertEqual(recovered["new_source_ticks"],0)
            recovered_clock = recovered["background_clock"]
            self.assertEqual(recovered_clock["source_ticks"],
                             recovered["recovered_source_ticks"])
            self.assertEqual(recovered_clock["since_wake"],
                             recovered["recovered_source_ticks"])
            self.assertEqual(provider.snapshot(),committed)
            self.assertIsNone(SixOrganRuntime.open(state)._port.brain.store.meta(PENDING))
            # A separate invocation and newly authorized lease must retain
            # the exact committed source ticks, even with no eligible wake.
            split = run_tower_life(state,source,world,authorize=True,opportunities=1,
                                   steps=100,background_every_ticks=100000)
            self.assertFalse(split["background_receipts"])
            self.assertEqual(split["background_clock"]["source_ticks"],
                             recovered_clock["source_ticks"] + split["new_source_ticks"])
            self.assertEqual(split["background_clock"]["since_wake"],
                             split["background_clock"]["source_ticks"])
            self.assertIsNone(split["background_clock"]["pending_wake"])
            # Cold-open every opportunity through the actual canonical host.
            life=run_tower_life(state,source,world,authorize=True,opportunities=8,steps=100,
                                background_every_ticks=1)
            self.assertEqual(life["opportunities_completed"],8)
            self.assertFalse(life["operator_supplied_goals"])
            self.assertGreater(life["new_source_ticks"],0)
            self.assertEqual(len({p["request_id"] for p in life["pulses"]}),8)
            self.assertTrue(any(p["policy_id"] for p in life["pulses"]))
            self.assertGreater(provider.snapshot()["cursor"],committed["cursor"])
            self.assertTrue(life["background_receipts"])
            self.assertEqual(life["background_clock"]["source_ticks"],
                             split["background_clock"]["source_ticks"] + life["new_source_ticks"])
            self.assertIsNone(life["background_clock"]["pending_wake"])
            by_request={p["request_id"]:p for p in life["pulses"]}
            for wake in life["background_receipts"]:
                pulse=by_request[wake["wake_id"].removeprefix("tower:")]
                self.assertFalse(pulse["busy"])
                self.assertFalse(pulse["replayed"])
                self.assertEqual(wake["after_tick"],wake["before_tick"]+1)
                self.assertEqual(wake["external_actions"],0)
                self.assertEqual(wake["renderer_calls"],0)
                self.assertTrue(wake["mnemosyne_policy_id"])
            self.assertFalse(recovered["background_receipts"])
            store=SixOrganRuntime.open(state)._port.brain.store
            sources=[m["source"] for m in store.memories()
                     if m["source"].startswith("virtual-world:small-tower:")]
            self.assertGreater(len(sources),0)
            self.assertEqual(len(sources),len(set(sources)))
            self.assertIsNone(store.meta(PENDING))
