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

class TowerDevelopmentAppraisalTests(unittest.TestCase):
    def test_donor_felt_report_uses_subject_words_not_numeric_state(self):
        from doctor_lives.tower_affectus import felt_words
        self.assertEqual(felt_words("valence:0.25v arousal:0.00~ security:0.00~ fatigue:-0.25~"),
                         ("I feel rather pleased.","I feel my mood sinking.","I feel rested."))
        with self.assertRaises(PermissionError):
            felt_words("valence:3.00^ arousal:0.00~ security:0.00~ fatigue:0.00~")

    def test_prospective_routing_uses_only_known_edges(self):
        from doctor_lives.tower_prospective import first_step
        graph = {"library": {"kitchen"}, "kitchen": {"garden"}, "garden": set()}
        self.assertEqual(first_step(graph, "library", "garden"), "move_kitchen")
        self.assertIsNone(first_step(graph, "garden", "library"))
        self.assertIsNone(first_step(graph, "library", "laboratory"))
        self.assertIsNone(first_step(graph, "library", "library"))

    def test_bodily_and_intellectual_pressure_routes_from_perceived_exits(self):
        from doctor_lives.tower_regulation import appraisal
        remembered = [
            "I am in my bedchamber. I can make my way to my library.",
            "I am in my library. I can make my way to my bedchamber. I can make my way to my kitchen and hearth.",
            "I am in my kitchen and hearth. I can make my way to my library. I can make my way to my garden path.",
        ]
        garden = ["I am in my garden path.", "I am getting tired."]
        garden_offers = [{"key":"walk"}, {"key":"move_kitchen"}]
        self.assertEqual(appraisal(garden,garden_offers,remembered),{"move_kitchen":.16})
        self.assertEqual(appraisal(garden,garden_offers,[]),{})
        self.assertEqual(appraisal(garden,[{"key":"walk"}],remembered),{})
        bedroom = ["I am in my bedchamber.", "I long for something to occupy my mind."]
        bedroom_offers = [{"key":"rest"}, {"key":"sleep"}, {"key":"move_library"}]
        self.assertEqual(appraisal(bedroom,bedroom_offers,remembered),{"move_library":.09})
        worn = ["I am in my bedchamber.", "I feel worn out and find it hard to concentrate."]
        self.assertEqual(appraisal(worn,bedroom_offers,remembered),{"rest":.08,"sleep":.20})
        tired = ["I am in my bedchamber.", "I am getting tired."]
        pressure = appraisal(tired,bedroom_offers,remembered)
        self.assertEqual(pressure,{"rest":.045,"sleep":.16})
        self.assertGreater(pressure["sleep"],pressure["rest"])
        self.assertEqual(appraisal(tired,[{"key":"rest"}],remembered),{"rest":.045})
        self.assertEqual(appraisal(["I am in my bedchamber."],bedroom_offers,remembered),{})

    def test_remembered_supply_need_survives_departure_until_verified_attempt(self):
        from doctor_lives.tower_regulation import supply_appraisal
        shortage = "I can see Stores shelf. I can see that my fuel is running low."
        self.assertEqual(supply_appraisal(shortage,set(),{"gather_fuel","walk"}),{"gather_fuel":.16})
        self.assertEqual(supply_appraisal(shortage,{"I gathered fallen wood for the hearth."},{"gather_fuel"}),{})
        self.assertEqual(supply_appraisal("I can see Stores shelf.",set(),{"gather_fuel"}),{})
        self.assertEqual(supply_appraisal("I can see that my fuel is running low.",set(),{"gather_fuel"}),{})
        self.assertEqual(supply_appraisal(shortage,set(),{"walk"}),{})

    def test_supply_route_respects_recent_unavailable_offers_and_need_satisfaction(self):
        from doctor_lives.tower_regulation import appraisal, supply_route
        food = "I can see Stores shelf. I can see that my edible provisions are running low."
        self.assertEqual(supply_route(food,set(),{"move_garden"},{"walk"},3),{})
        self.assertEqual(supply_route(food,set(),{"move_garden"},{"walk"},100),{"move_garden":.18})
        self.assertEqual(supply_route(food,set(),{"move_garden"},{"tend"},3),{"move_garden":.18})
        self.assertEqual(supply_route(food,{"I tended the patch beside the tower."},{"move_garden"}),{})
        mixed = food + " I can see that my water is running low."
        self.assertEqual(supply_route(mixed,set(),{"move_garden"},{"draw_water"},3),{"move_garden":.16})
        offers = [{"key":"eat"},{"key":"cook"},{"key":"move_library"}]
        self.assertEqual(appraisal(["I am in my kitchen and hearth."],offers,[]),{"eat":-.16,"cook":-.16})
        self.assertEqual(appraisal(["I am in my kitchen and hearth.","I could do with something to eat."],offers,[]),{"eat":.16,"cook":.075})
        self.assertEqual(appraisal(["I am in my kitchen and hearth.","I am painfully hungry."],offers,[]),{"eat":.20,"cook":.10})

    def test_prospective_needs_defer_without_removing_owned_intention(self):
        from doctor_lives.tower_prospective import deferred_need
        stores = "I can see Stores shelf."
        hungry = "I could do with something to eat."
        self.assertEqual(deferred_need("cook","I am in my library.",stores,None,"library",{"move_kitchen"}),"appetite_satisfied")
        self.assertIsNone(deferred_need("cook",hungry,stores,None,"library",{"move_kitchen"}))
        self.assertEqual(deferred_need("gather_fuel","I am in my library.",stores,None,"library",{"move_kitchen"}),"last_observed_supply_not_low")
        low = stores + " I can see that my fuel is running low."
        self.assertIsNone(deferred_need("gather_fuel","I am in my garden path.",low,None,"garden",{"gather_fuel"}))
        self.assertEqual(deferred_need("tend","I am in my kitchen and hearth.",stores+" I can see that my edible provisions are running low.",{"offers":["walk"],"elapsed":3},"kitchen",{"move_garden"}),"recently_observed_unavailable")
        self.assertIsNone(deferred_need("rest","I am in my bedchamber.",stores,None,"bedchamber",{"rest"}))

    def test_owned_unavailable_activity_defers_travel_until_recheck(self):
        from doctor_lives.tower_prospective import unavailable_activity
        known = {"library":{"offers":["diary"],"elapsed":3}}
        self.assertEqual(unavailable_activity("read","library","library",{"diary"},{}),"currently_unavailable")
        self.assertEqual(unavailable_activity("read","library","kitchen",{"move_library"},known),"recently_observed_unavailable")
        self.assertIsNone(unavailable_activity("read","library","library",{"read"},known))
        known["library"]["elapsed"]=100
        self.assertIsNone(unavailable_activity("read","library","kitchen",{"move_library"},known))
        self.assertIsNone(unavailable_activity("read","library","kitchen",{"move_library"},{}))

    def test_finite_tea_shortage_does_not_reactivate_by_elapsed_time(self):
        from doctor_lives.tower_prospective import unavailable_activity
        scene = "I am in my kitchen and hearth. I can see Kettle. I can see Stores shelf. I can see that my tea is running low."
        prior = {"offers":["eat","cook"],"elapsed":800,"observed_text":scene,
                 "replenishment_memory_ids":[]}
        known = {"kitchen":prior}
        self.assertEqual(unavailable_activity("tea","kitchen","garden",{"move_kitchen"},known),
                         "awaiting_observed_replenishment")
        self.assertIsNone(unavailable_activity("tea","kitchen","kitchen",{"tea"},known))
        self.assertEqual(unavailable_activity("tea","kitchen","kitchen",{"eat"},known),
                         "currently_unavailable")
        prior["replenishment_memory_ids"] = ["verified-source-outcome"]
        self.assertIsNone(unavailable_activity("tea","kitchen","garden",{"move_kitchen"},known))
        prior["replenishment_memory_ids"] = []
        prior["observed_text"] = "I am in my kitchen and hearth. I can see Kettle."
        self.assertIsNone(unavailable_activity("tea","kitchen","garden",{"move_kitchen"},known))

    def test_repeated_single_activity_is_not_a_procedural_sequence(self):
        from doctor_lives.tower_procedure import appraise
        episodes = [{"action":"rest","room":"bedchamber","success":True,
                     "source":"source-"+str(i),"memory_id":"memory-"+str(i)}
                    for i in range(6)]
        scores,ids = appraise(episodes,"bedchamber",("rest","sleep"))
        self.assertEqual(scores,{"rest":0.0,"sleep":0.0})
        self.assertEqual(ids,{"rest":[],"sleep":[]})

    def test_procedural_sequence_requires_independent_success_and_current_cue(self):
        from doctor_lives.tower_procedure import appraise, CAP
        def event(action,i,success=True,room="I am in my kitchen and hearth."):
            return {"action":action,"room":room,"success":success,
                    "source":"event-"+str(i),"memory_id":"mem-"+str(i)}
        room="I am in my kitchen and hearth."
        pair=[event("cook",1),event("tea",2)]
        history=pair+[event("cook",3),event("tea",4),event("cook",5)]
        scores,ids=appraise(history,room,("tea","eat"))
        self.assertEqual(scores["tea"],CAP)
        self.assertEqual(ids["tea"],["mem-1","mem-2","mem-3","mem-4"])
        self.assertEqual(appraise(pair+[event("cook",3)],room,("tea",))[0]["tea"],0)
        self.assertEqual(appraise(history+[event("tea",6,False),event("cook",7)],room,("tea",))[0]["tea"],0)
        self.assertEqual(appraise(history,"another room",("tea",))[0]["tea"],0)

    def test_independent_outcomes_saturate_and_reverse(self):
        from doctor_lives.tower_development import _appraise
        good = [("work", True, "memory-" + str(i), "source-" + str(i))
                for i in range(6)]
        scores, used = _appraise(good + good, ("work", "read"))
        self.assertEqual(len(used["work"]), 4)
        self.assertAlmostEqual(scores["work"], .015 * 1.875)
        self.assertEqual(scores["read"], 0.0)
        reversed_scores, _ = _appraise([("work", False, "failure", "new")] + good,
                                      ("work", "read"))
        self.assertLess(reversed_scores["work"], 0.0)
        duplicated, ids = _appraise([good[0]] * 6, ("work",))
        self.assertEqual(ids["work"], ["memory-0"])
        self.assertEqual(duplicated["work"], .015)


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
        body = json.loads(store.meta("corpus:tower-body:" + sha256(source_ref.encode()).hexdigest()))
        self.assertEqual(body["source_memory_id"], choice["observation_id"])
        self.assertEqual(body["band"], choice["corpus"]["band"])
        self.assertFalse(body["world_authority"])
        self.assertFalse(body["motor_authority"])
        if body["projection_applied"]:
            self.assertGreaterEqual(body["felt_projection"], .05)
            self.assertLessEqual(body["felt_projection"], .95)
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
        from doctor_lives.tower_ipseity import TowerIpseity, RECORD
        history=TowerIpseity(runtime._port.brain).verify_history()
        audit=appraisals["ipseity"]
        self.assertTrue(audit["required"])
        admission=next(h for h in history if h["key"]==audit["admission_key"])
        self.assertEqual(admission["sha256"],audit["admission_sha256"])
        self.assertEqual({h["subject"] for h in history},{"pretorius"})
        self.assertTrue(any(h["key"]==RECORD+"decision:"+result["policy_id"] for h in history))
        self.assertTrue(any(h["phase"]=="affect" and any(i["organ"]=="Affectus" for i in h["content"]) for h in history))
        self.assertEqual(set(appraisals["offer_appraisals"]), set(choice["offers"]))
        procedure = appraisals["procedural_memory"]
        self.assertTrue(procedure["enabled"])
        self.assertEqual(set(procedure["contributions"]),set(choice["offers"]))
        self.assertTrue(all(0 <= v <= .025 for v in procedure["contributions"].values()))
        prospective = appraisals["prospective_goals"]
        self.assertEqual(set(prospective["scores"]), set(choice["offers"]))
        self.assertTrue(all(0 <= v <= .065 for v in prospective["scores"].values()))
        self.assertEqual(prospective["active_ids"], [])
        developmental = appraisals["developmental_history"]
        self.assertTrue(developmental["enabled"])
        self.assertEqual(set(developmental["contributions"]), set(choice["offers"]))
        self.assertTrue(all(abs(v) <= .08 for v in developmental["contributions"].values()))
        self.assertTrue(all(not ids for ids in developmental["source_memory_ids"].values()))
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
                                background_every_ticks=1,background_during_activity=False)
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
                self.assertFalse(wake["during_activity"])
                self.assertTrue(wake["physical_revision_unchanged"])
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


    def test_private_cognition_while_body_is_occupied(self):
        source=Path(os.environ["PRETORIUS_TOWER_SOURCE"])
        with tempfile.TemporaryDirectory() as temp:
            state=Path(temp)/"doctor"
            world=Path(temp)/"tower.json"
            cfg=dict(DEFAULT_CONFIG)
            cfg.update(neurons=128,sensory_dim=64,avg_recurrent_degree=8,input_degree=4,
                       action_population_size=8,seed=1842)
            initialize_tower(state,source,world,epoch="busy-private-thought",neural_config=cfg)
            report=run_tower_life(state,source,world,authorize=True,opportunities=3,
                                  steps=1,background_every_ticks=1)
            self.assertTrue(report["background_during_activity"])
            self.assertTrue(report["background_receipts"])
            occupied=[w for w in report["background_receipts"] if w["during_activity"]]
            self.assertTrue(occupied)
            for wake in occupied:
                self.assertTrue(wake["physical_revision_unchanged"])
                self.assertEqual(wake["external_actions"],0)
                self.assertEqual(wake["renderer_calls"],0)
                self.assertTrue(wake["mnemosyne_policy_id"])
            self.assertIsNone(report["background_clock"]["pending_wake"])

    def test_own_past_commitment_changes_real_tower_action_under_matched_ipseity_impairment(self):
        # Controlled causal example, not an uncoached life trial. Use the actual
        # original physical source and original Noesis, never fake a receipt,
        # memory, policy, chosen action or prospective goal.
        import shutil
        from contextlib import closing, nullcontext
        from doctor_lives import noesis_situated_choice as n
        from doctor_lives.tower_ipseity import TowerIpseity
        from doctor_lives.tower_prospective import PREFIX
        source=Path(os.environ["PRETORIUS_TOWER_SOURCE"])
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            base=root/"base";base.mkdir()
            state=base/"doctor";world=base/"tower.json"
            cfg=dict(DEFAULT_CONFIG)
            cfg.update(neurons=128,sensory_dim=64,avg_recurrent_degree=8,input_degree=4,
                       action_population_size=8,seed=1842)
            initialize_tower(state,source,world,epoch="owned-intention-causal",neural_config=cfg)
            original=n.select_world_affordance
            def pulse(directory, pressure, impaired=False):
                # Only the bounded competition inputs are controlled. Actual
                # Noesis selects and the real source executes the winning choice.
                def compete(*args,**kwargs):
                    kwargs["regulatory_pressure"]=pressure
                    return original(*args,**kwargs)
                lesion=(patch.object(TowerIpseity,"commitment_event",return_value=None)
                        if impaired else nullcontext())
                with patch.object(n,"select_world_affordance",side_effect=compete),lesion:
                    return run_tower_pulse(directory/"doctor",source,directory/"tower.json",
                                           authorize=True,steps=1000)
            for action in ("rest","move_library","move_bedchamber"):
                chosen=pulse(base,{action:.20})
                self.assertEqual(chosen["choice"],action)
                self.assertFalse(chosen["source_receipt"]["busy"])
            rt=SixOrganRuntime.open(state)
            store=rt._port.brain.store
            with closing(store.connect()) as db:
                rows=db.execute("SELECT * FROM commitments WHERE source LIKE ? AND status='open'",
                                (PREFIX+"%",)).fetchall()
            self.assertEqual(len(rows),1)
            goal=dict(rows[0]);rid=goal["id"]
            self.assertEqual(goal["description"],"return to bedchamber to rest")
            prior=json.loads(store.meta("telos:tower-prospective:"+rid))
            first_person="I still intend to "+goal["description"]+"."
            self.assertTrue(store.get_memory(prior["prior_memory_id"])["source"].startswith("virtual-world:small-tower:"))
            before=store.digest()
            del rt,store
            gc.collect()
            def branch(name):
                destination=root/name
                shutil.copytree(base,destination)
                return destination
            def audit(directory,result):
                rt=SixOrganRuntime.open(directory/"doctor")
                store=rt._port.brain.store
                with closing(store.connect()) as db:
                    row=db.execute("SELECT state_pressure_json FROM policy_decisions WHERE id=?",
                                   (result["policy_id"],)).fetchone()
                return json.loads(row["state_pressure_json"])
            # Calibrate a matched near-boundary competition on disposable
            # copies, then run both fresh branches from the unchanged history.
            # This is an openly disclosed engineering causal intervention.
            x,y=branch("probe-intact"),branch("probe-impaired")
            intact=audit(x,pulse(x,{}))
            impaired=audit(y,pulse(y,{},True))
            self.assertEqual(intact["ipseity"]["owned_commitments"][rid],first_person)
            self.assertNotIn(rid,impaired["ipseity"]["owned_commitments"])
            self.assertGreater(intact["prospective_goals"]["scores"]["rest"],0)
            self.assertEqual(impaired["prospective_goals"]["scores"]["rest"],0)
            a,b=intact["candidate_final_scores"],impaired["candidate_final_scores"]
            pressure=None;competitor=None
            for other in sorted(set(a)-{"rest"}):
                di,dl=a["rest"]-a[other],b["rest"]-b[other]
                if di<=dl+1e-8: continue
                delta=-(di+dl)/2
                proposed={"rest":.10+delta/2,other:.10-delta/2}
                if not all(0<=v<=.20 for v in proposed.values()):continue
                if (max(sorted(a),key=lambda k:a[k]+proposed.get(k,0))=="rest"
                        and max(sorted(b),key=lambda k:b[k]+proposed.get(k,0))==other):
                    pressure,competitor=proposed,other
                    break
            self.assertIsNotNone(pressure,"No matched choice-changing pressure found")
            normal,lesion=branch("intact"),branch("impaired")
            for directory in (normal,lesion):
                self.assertEqual(SixOrganRuntime.open(directory/"doctor")._port.brain.store.digest(),before)
            i=pulse(normal,pressure)
            l=pulse(lesion,pressure,True)
            self.assertEqual(i["choice"],"rest")
            self.assertEqual(l["choice"],competitor)
            self.assertNotEqual(i["choice"],l["choice"])
            reports={}
            for label,directory,result in (("intact",normal,i),("impaired",lesion,l)):
                rt=SixOrganRuntime.open(directory/"doctor")
                store=rt._port.brain.store
                source_snapshot=SmallTowerSource(source,directory/"tower.json").snapshot()
                events=[e for e in source_snapshot["events"] if e["policyRef"]==result["policy_id"]
                        and e["kind"]=="completed"]
                self.assertEqual(len(events),1)
                with closing(store.connect()) as db:
                    status=db.execute("SELECT status FROM commitments WHERE id=?",(rid,)).fetchone()["status"]
                self.assertEqual(status,"kept" if label=="intact" else "open")
                evidence=audit(directory,result)
                history=TowerIpseity(rt._port.brain).verify_history()
                frame=next(e for e in history if e["key"]==evidence["ipseity"]["admission_key"])
                reports[label]={"choice":result["choice"],"policy_id":result["policy_id"],
                    "first_person_frame":frame,"physical_event":events[0],"goal_status":status,
                    "owned_commitments":evidence["ipseity"]["owned_commitments"]}
            trace={"controlled_not_uncoached":True,"same_pre_state_sha256":before,
                   "original_goal":goal,"origin":prior,"first_person":first_person,
                   "matched_competing_pressure":pressure,"branches":reports,
                   "lesion":"withhold re-owned Telos first-person experience only"}
            print("IPSEITY_CAUSAL_TRACE="+json.dumps(trace,sort_keys=True))
            if os.getenv("PRETORIUS_IPSEITY_TRACE"):
                Path(os.environ["PRETORIUS_IPSEITY_TRACE"]).write_text(json.dumps(trace,indent=2),encoding="utf-8")
            gc.collect()

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
        # The bound product must deny the historical unowned fixture before
        # generating any readings, decisions or other state mutations.
        before = brain.store.digest()
        with self.assertRaisesRegex(PermissionError, "Bound Tower choice"):
            select_world_affordance(brain, **kwargs)
        self.assertEqual(brain.store.digest(), before)
        from doctor_lives.tower_ipseity import TowerIpseity
        subject = TowerIpseity(brain)
        bound = dict(kwargs, tower_provider=provider, subject=subject)
        baseline_owned = select_world_affordance(brain, **bound)
        commitment = brain.add_commitment(term, importance=1.0)
        changed_owned = select_world_affordance(brain, **bound)
        for appraisal in changed_owned["appraisals"].values():
            self.assertNotIn(commitment, appraisal["source_ids"]["commitments"])
        self.assertEqual(changed_owned["appraisals"][target]["commitment"],
                         baseline_owned["appraisals"][target]["commitment"])
        self.assertEqual(provider.snapshot(),snapshot)

        # Keep the original positive appraisal control on an isolated,
        # explicitly unbound copy. Never remove the product's binding.
        import shutil
        brain.save()
        control_state = Path(temp.name)/"legacy-control"
        shutil.copytree(state, control_state)
        control = SixOrganRuntime.open(control_state)._port.brain
        with control.store.transaction() as db:
            db.execute("DELETE FROM meta WHERE key='small-tower:world-binding-v1'")
            db.execute("DELETE FROM commitments WHERE id=?", (commitment,))
        brain = control
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
