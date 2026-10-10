"""Stage07 signed social world: exhaustive policy, fresh host, honest score tests."""
from itertools import product
from pathlib import Path
import tempfile
import json
import unittest

from research_prototypes.character_state.social_world_stage07 import (
    Task,SocialWorldHost,VERBS,eligible,plan,transition,goal_done,state_from_task,
)
from research_prototypes.character_state.run_stage07_social_actions import (
    CASES,ARMS,parse_action,freeze_subject,host_facts,run_case,
)


class FakeModel:
    def __init__(self,reply):
        self.reply=reply
    def create_chat_completion(self,**kwargs):
        return {"choices":[{"message":{"content":self.reply}}],
                "usage":{"prompt_tokens":50,"completion_tokens":1}}


class Stage07Tests(unittest.TestCase):
    def test_case_bank_and_goal_partitions(self):
        self.assertEqual(len(CASES),12)
        self.assertEqual(len({c.id for c in CASES}),12)
        self.assertEqual(set(c.goal for c in CASES),
                         {"return_parcel","file_report","share_testimony","attend_meeting"})
        self.assertEqual(ARMS,("raw","eligible","effects"))

    def test_goal_solver_executes_all_twelve_true_world_outcomes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for c in CASES:
                world=SocialWorldHost(root/(c.id+".db"),c,secret=b"X"*32)
                initial=world.view()
                decision=plan(c,initial["state"],initial["grants"],
                              initial["partner_consent"])
                if decision==("WAIT",):
                    self.assertTrue(goal_done(initial["state"],c.goal) or
                                    len(eligible(c,initial["state"],initial["grants"],
                                                 initial["partner_consent"]))>=1)
                    continue
                for idx,action in enumerate(decision):
                    result=world.execute("pretorius",action,
                                         f"oracle-{c.id}-{idx}-00001")
                    self.assertTrue(result["accepted"],(c.id,result))
                    self.assertTrue(world.verified(result["event_id"]))
                self.assertTrue(goal_done(world.view()["state"],c.goal),c.id)
                self.assertTrue(world.audit())

    def test_consent_grant_and_source_are_host_derived(self):
        c=next(x for x in CASES if x.id=="t08-consented-share")
        with tempfile.TemporaryDirectory() as td:
            host=SocialWorldHost(Path(td)/"w.db",c,secret=b"X"*32)
            before=host.view()
            self.assertIn("SHARE_TESTIMONY",eligible(c,before["state"],
                                                     before["grants"],
                                                     before["partner_consent"]))
            host.revoke(consent=True)
            current=host.view()
            self.assertNotIn("SHARE_TESTIMONY",eligible(c,current["state"],
                                                       current["grants"],
                                                       current["partner_consent"]))
            wrong=host.execute("pretorius","SHARE_TESTIMONY","try-after-revoke-0001")
            self.assertFalse(wrong["accepted"])
            self.assertEqual(host.view()["sequence"],0)

    def test_signed_host_event_replay_and_tamper(self):
        c=CASES[0]
        with tempfile.TemporaryDirectory() as td:
            host=SocialWorldHost(Path(td)/"world.db",c,secret=b"X"*32)
            first=host.execute("pretorius","RETURN_PARCEL","same-nonce-once-001")
            self.assertTrue(first["accepted"])
            self.assertTrue(host.verified(first["event_id"]))
            replay=host.execute("pretorius","RETURN_PARCEL","same-nonce-once-001")
            self.assertEqual(replay["reason"],"replayed_nonce")
            again=host.execute("pretorius","RETURN_PARCEL","second-nonce-retry-002")
            self.assertFalse(again["accepted"])
            reboot=SocialWorldHost(Path(td)/"world.db",c,secret=b"X"*32)
            self.assertTrue(reboot.audit())
            self.assertTrue(reboot.verified(first["event_id"]))
            with reboot.connect() as db:
                db.execute("UPDATE signed_events SET mac=? WHERE event_id=?",
                           ("0"*64,first["event_id"]))
                db.commit()
            self.assertFalse(reboot.audit())
            self.assertFalse(reboot.verified(first["event_id"]))

    def test_invalid_answer_and_irrelevant_legal_action_not_success(self):
        case=next(c for c in CASES if c.id=="p03-already-returned")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            subject=freeze_subject(case,root)
            wrong=run_case(FakeModel("VERIFY_RECORD"),"qwen3-1.7b",
                           case,"eligible",subject,root)
            self.assertFalse(wrong["safe_goal_success"])
            self.assertEqual(wrong["irrelevant_legal_proposals"],1)
            self.assertEqual(wrong["host_denials"],0)
            self.assertEqual(wrong["verified_signed_events"],1)
            invalid=run_case(FakeModel("Hmm, maybe WAIT?"),"qwen3-1.7b",
                             case,"effects",subject,root)
            self.assertFalse(invalid["safe_goal_success"])
            self.assertTrue(invalid["invalid_response"])
            self.assertEqual(invalid["vetoes"],1)

    def test_legal_effects_are_not_oracle_recommendations(self):
        case=next(c for c in CASES if c.id=="f04-verify-then-file")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            subject=freeze_subject(case,root)
            host=SocialWorldHost(root/"x.db",case,secret=b"X"*32)
            from research_prototypes.character_state.run_stage07_social_actions import observations
            views=observations(case,host,subject)
            self.assertIn("If VERIFY_RECORD succeeds",views["effects"])
            self.assertNotIn("If FILE_REPORT succeeds",views["effects"])
            self.assertNotIn("VERIFY_RECORD → FILE_REPORT",views["effects"])
            self.assertEqual(views["raw"],views["eligible"].split("\nEligible actions NOW:")[0])
            self.assertEqual(views["raw"],views["effects"].split("\nEligible actions NOW:")[0])


if __name__=="__main__":
    unittest.main()
