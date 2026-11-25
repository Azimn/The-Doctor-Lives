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
        self.assertFalse(choice["host_mapped_abstract_tendency"])
        self.assertEqual(choice["selector_authority"], "original_noesis")
        from doctor_lives.tower_affectus import weather_for
        weather = weather_for(runtime)
        self.assertGreaterEqual(weather.tick, choice["affectus"]["tick"])
        self.assertEqual(len(choice["affectus"]["digest"]), 64)
        from hashlib import sha256
        source_ref = store.get_memory(choice["observation_id"])["source"]
        weather_receipt = json.loads(store.meta(
            "affectus:tower-event:" + sha256(source_ref.encode()).hexdigest()))
        self.assertEqual(weather_receipt["source_record"]["memory_id"], choice["observation_id"])
        scene = json.loads(store.meta("sensus:tower-scene:" + sha256(source_ref.encode()).hexdigest()))
        self.assertEqual(scene["source_memory_id"], choice["observation_id"])
        self.assertEqual(scene["working_state_sha256"], choice["sensus"]["working_state_sha256"])
        self.assertTrue(scene["admitted_lines"])
        self.assertEqual(" ".join(scene["admitted_lines"]), store.get_memory(choice["observation_id"])["text"])
        self.assertFalse(scene["world_authority"])
        self.assertIn("hearing", scene["absent_channels"])
        from contextlib import closing
        with closing(store.connect()) as db:
            policy = db.execute("SELECT selected_action,state_pressure_json FROM policy_decisions "
                                "WHERE id=?", (result["policy_id"],)).fetchone()
        self.assertEqual(policy["selected_action"], result["choice"])
        from doctor_lives.tower_telos import intention_id
        rid = intention_id(result["policy_id"])
        with closing(store.connect()) as db:
            intent = db.execute("SELECT * FROM commitments WHERE id=?", (rid,)).fetchone()
        self.assertIsNotNone(intent)
        self.assertEqual(intent["source"], "telos:native:tower:" + result["policy_id"])
        self.assertIn(intent["status"], ("open", "kept", "broken"))
        with self.assertRaises(PermissionError):
            runtime._port.brain.resolve_commitment(rid, "invented completion")
        if intent["status"] != "open":
            outcome = json.loads(store.meta("telos:tower-outcome:" + result["policy_id"]))
            self.assertEqual(outcome["commitment_id"], rid)
            self.assertEqual(outcome["status"], intent["status"])
            self.assertEqual(store.get_memory(outcome["source_memory_id"])["text"], intent["outcome"])
        appraisals = json.loads(policy["state_pressure_json"])
        self.assertEqual(appraisals["abstract_policy_id"], choice["abstract_policy_id"])
        self.assertEqual(set(appraisals["offer_appraisals"]), set(choice["offers"]))
        reflection = appraisals["conclave"]
        from doctor_lives.conclave import Conclave
        observation = store.get_memory(choice["observation_id"])
        self.assertEqual(reflection["source_event_id"], observation["source_event_id"])
        self.assertTrue(reflection["reading_ids"])
        self.assertTrue(reflection["retrieval_cues"])
        self.assertFalse(reflection["motor_authority"])
        self.assertFalse(reflection["lived_fact_authority"])
        reopened = Conclave(store, enabled=True)
        readings = reopened.readings(reflection["context_key"])
        self.assertEqual(set(reflection["reading_ids"]), {r.id for r in readings})
        self.assertEqual(list(reopened.cues(reflection["context_key"])),
                         reflection["retrieval_cues"])
        self.assertTrue(all(r.source_event_id == observation["source_event_id"]
                            for r in readings))
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
            self.assertEqual(recovered["background_every_source_ticks"],
                             small_tower.DEFAULT_BACKGROUND_EVERY_TICKS)
            self.assertEqual(recovered["new_source_ticks"],0)
            recovered_clock = recovered["background_clock"]
            self.assertEqual(recovered_clock["source_ticks"],
                             recovered["recovered_source_ticks"])
            self.assertEqual(recovered_clock["since_wake"],
                             recovered["recovered_source_ticks"])
            self.assertEqual(provider.snapshot(),committed)
            recovered_store = SixOrganRuntime.open(state)._port.brain.store
            self.assertIsNone(recovered_store.meta(PENDING))
            from contextlib import closing
            from doctor_lives.tower_telos import intention_id
            with closing(recovered_store.connect()) as db:
                count = db.execute("SELECT COUNT(*) FROM commitments WHERE id=?",
                                   (intention_id(pending["policyRef"]),)).fetchone()[0]
            self.assertEqual(count, 1)
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


    def test_concrete_competition_reads_relevant_canonical_commitment(self):
        # Controlled integration test, not independent-goal credit.
        from doctor_lives.virtual_world_port import VirtualWorldEnvironmentPort
        from doctor_lives.noesis_situated_choice import select_world_affordance
        from contextlib import closing
        source = Path(os.environ["PRETORIUS_TOWER_SOURCE"])
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._cleanup, temp)
        state, world = Path(temp.name)/"doctor", Path(temp.name)/"tower.json"
        cfg = dict(DEFAULT_CONFIG)
        cfg.update(neurons=128,sensory_dim=64,avg_recurrent_degree=8,input_degree=4,
                   action_population_size=8,seed=1842)
        initialize_tower(state,source,world,epoch="concrete-commitment",neural_config=cfg)
        provider = SmallTowerSource(source,world)
        snapshot = provider.snapshot()
        runtime = SixOrganRuntime.open(state)
        brain = runtime._port.brain
        port = VirtualWorldEnvironmentPort(runtime,provider,authorized=True)
        observation = port._admit(provider._observation(snapshot),kind="observation")
        offers = snapshot["offers"]
        terms = {o["key"]:brain._tokens(o["key"].replace("_"," ") + " " + o["text"][8:])
                 for o in offers}
        unique = [(key,term) for key in sorted(terms) for term in sorted(terms[key])
                  if all(term not in other for k,other in terms.items() if k != key)]
        self.assertGreater(len(offers),1)
        self.assertTrue(unique)
        target, term = unique[0]
        kwargs = dict(observation_memory_id=observation.memory_id,
                      observation_source=brain.store.get_memory(observation.memory_id)["source"],
                      narrative=snapshot["narrative"], offers=offers,
                      affordance_map=small_tower.MAP, regulatory_pressure={})
        baseline = select_world_affordance(brain,**kwargs)
        commitment = brain.add_commitment(term,importance=1.0)
        changed = select_world_affordance(brain,**kwargs)
        self.assertIn(commitment,changed["appraisals"][target]["source_ids"]["commitments"])
        self.assertGreater(changed["appraisals"][target]["commitment"],
                           baseline["appraisals"][target]["commitment"])
        for key in terms:
            if key != target:
                self.assertNotIn(commitment,changed["appraisals"][key]["source_ids"]["commitments"])
        self.assertEqual(provider.snapshot(),snapshot)
        with closing(brain.store.connect()) as db:
            row = db.execute("SELECT selected_action FROM policy_decisions WHERE id=?",
                             (changed["policy_decision_id"],)).fetchone()
        self.assertEqual(row["selected_action"],changed["selected_action"])
