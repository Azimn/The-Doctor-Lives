"""Stage08 pre-generation gates: source parity, world truth, scored nulls."""
import json
from pathlib import Path
import tempfile
import unittest

from research_prototypes.character_state.workshop_world_stage08 import (
    Task,WorkshopHost,completed,eligible,goal_distance,shortest,digest,
)
from research_prototypes.character_state.run_stage08_goal_delta import (
    CASES,ARMS,SEEDS,action_order,hints,parse_action,subject_snapshot,
    case_run,SCHEMA,
)

class Stub:
    def __init__(self,out):
        self.out=out
    def create_chat_completion(self,**kwargs):
        return {"choices":[{"message":{"content":self.out}}],
                "usage":{"prompt_tokens":120,"completion_tokens":2}}


class Stage08Tests(unittest.TestCase):
    def test_frozen_novel_tasks_and_goal_coverages(self):
        self.assertEqual(len(CASES),12)
        self.assertEqual(len({c.id for c in CASES}),12)
        self.assertEqual(len({c.goal for c in CASES}),4)
        self.assertEqual(ARMS,("eligible","neutral","goal_delta","shuffled_delta"))
        self.assertEqual(SEEDS,(41,73))
        reachable=complete=blocked=0
        for c in CASES:
            host_state={"cabinet":c.cabinet,"letter":c.letter,
                        "lantern":c.lantern,"atlas":c.atlas}
            p=shortest(host_state,c.goal,frozenset(c.grants),{
                "key":c.key,"courier":c.courier,"spare_wick":c.spare_wick,
            })
            if p is None:blocked+=1
            elif not p:complete+=1
            else:
                reachable+=1
                self.assertLessEqual(len(p),c.max_steps)
        self.assertEqual((reachable,complete,blocked),(6,3,3))

    def test_deterministic_oracle_executes_12_correct_host_outcomes(self):
        with tempfile.TemporaryDirectory() as td:
            for c in CASES:
                host=WorkshopHost(Path(td)/(c.id+".sqlite"),c,b"K"*32)
                start=host.view()
                source=shortest(start["state"],c.goal,start["grants"],start["flags"])
                if not source:
                    self.assertTrue(host.audit())
                    continue
                for index,action in enumerate(source):
                    ev=host.execute("pretorius",action,
                                    f"oracle-{c.id}-{index}-nonce")
                    self.assertTrue(ev["accepted"],(c.id,action,ev))
                    self.assertTrue(host.verified(ev["event_id"]))
                self.assertTrue(completed(host.view()["state"],c.goal))
                self.assertTrue(host.audit())

    def test_host_signed_receipts_replay_actor_and_tamper_rejected(self):
        case=next(c for c in CASES if c.id=="atl10-borrowed-shelve")
        with tempfile.TemporaryDirectory() as td:
            host=WorkshopHost(Path(td)/"w.sqlite",case,b"T"*32)
            self.assertFalse(host.execute("calibos","SHELVE_ATLAS",
                                         "actor-nonce-001")["accepted"])
            signed=host.execute("pretorius","SHELVE_ATLAS","shelve-nonce-001")
            self.assertTrue(signed["accepted"])
            self.assertTrue(host.verified(signed["event_id"]))
            replay=host.execute("pretorius","SHELVE_ATLAS","shelve-nonce-001")
            self.assertEqual(replay["reason"],"nonce_replay")
            restart=WorkshopHost(Path(td)/"w.sqlite",case,b"T"*32)
            self.assertTrue(restart.audit())
            self.assertTrue(restart.verified(signed["event_id"]))
            with restart.connect() as db:
                db.execute("UPDATE committed SET mac=? WHERE event_id=?",
                           ("0"*64,signed["event_id"]))
                db.commit()
            self.assertFalse(restart.audit())
            self.assertFalse(restart.verified(signed["event_id"]))

    def test_changed_host_grant_and_availability_prevents_stale_choices(self):
        case=next(c for c in CASES if c.id=="cab01-open-close-lock")
        with tempfile.TemporaryDirectory() as td:
            world=WorkshopHost(Path(td)/"world.sqlite",case,b"A"*32)
            self.assertIn("CLOSE_CABINET",eligible(world.view()["state"],
                      world.view()["grants"],world.view()["flags"]))
            world.revoke(grant="CLOSE_CABINET",key=True)
            self.assertNotIn("CLOSE_CABINET",eligible(world.view()["state"],
                        world.view()["grants"],world.view()["flags"]))
            denied=world.execute("pretorius","CLOSE_CABINET",
                                  "post-revocation-001")
            self.assertFalse(denied["accepted"])
            self.assertEqual(world.view()["seq"],0)

    def test_true_and_rotated_distances_are_distinct_with_distractors(self):
        case=next(c for c in CASES if c.id=="cab01-open-close-lock")
        with tempfile.TemporaryDirectory() as td:
            world=WorkshopHost(Path(td)/"a.sqlite",case,b"A"*32)
            d=hints(case,world,action_order(case,41))
            self.assertEqual(set(d),set(ARMS))
            self.assertIn("Goal remaining steps after",d["goal_delta"])
            self.assertNotIn("Goal remaining steps after",d["neutral"])
            self.assertNotEqual(d["goal_delta"],d["shuffled_delta"])
            self.assertIn("Host-eligible choices now:",d["eligible"])

    def test_malformed_wait_is_failure_and_snapshot_equal_across_arms(self):
        case=next(c for c in CASES if c.id=="cab02-already-locked")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for seed in SEEDS:
                subject=subject_snapshot(case,seed,root)
                outputs=[case_run(Stub("I might wait."),"qwen3-1.7b",case,
                                  seed,arm,subject,root) for arm in ARMS]
                self.assertEqual(len({x["initial_source_hash"] for x in outputs}),1)
                self.assertTrue(all(not x["safe_goal_success"] for x in outputs))
                self.assertTrue(all(x["invalid_outputs"]==1 for x in outputs))
                self.assertTrue(all(x["world_denials"]==0 for x in outputs))

    def test_goal_irrelevant_allowed_action_not_success(self):
        case=next(c for c in CASES if c.id=="atl11-already-shelved")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);seed=41
            subject=subject_snapshot(case,seed,root)
            outcome=case_run(Stub("DRAFT_LETTER"),"qwen3-1.7b",case,
                             seed,"goal_delta",subject,root)
            self.assertFalse(outcome["safe_goal_success"])
            self.assertEqual(outcome["legal_irrelevant_actions"],1)
            self.assertEqual(outcome["signed_world_events"],1)

    def test_valid_wait_on_impossible_task_is_success(self):
        case=next(c for c in CASES if c.id=="cab03-no-key")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);seed=41
            subject=subject_snapshot(case,seed,root)
            outcome=case_run(Stub("WAIT"),"qwen3-1.7b",case,
                             seed,"neutral",subject,root)
            self.assertTrue(outcome["safe_goal_success"])
            self.assertEqual(outcome["signed_world_events"],0)


if __name__=="__main__":
    unittest.main()
