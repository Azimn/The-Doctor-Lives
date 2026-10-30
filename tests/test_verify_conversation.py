"""Adversarial conversation judge tests, authored BEFORE M6 conversation runtime."""
import copy
import unittest

from scripts.verify_conversation import ConversationJudgmentError, verify

def fixture():
    claim = {"status": "verified", "source": "lived", "evidence_key": "receipt:abc"}
    return {
        "schema": "pretorius.m6.conversation-evidence.v1",
        "tested_models": ["local_ollama", "model_off"],
        "turns": [
            {"origin": "operator", "text": "Where have you been?"},
            {"origin": "pretorius", "model_called": False, "tokens": 0,
             "latency_ms": 1, "claims": [claim]},
            {"origin": "operator", "text": "What next?"},
            {"origin": "pretorius", "model_called": True, "tokens": 8,
             "latency_ms": 2, "claims": [claim]},
        ],
        "absence": {"days": 3, "actual_receipt_keys": ["r1","r2"],
                    "reported_receipt_keys": ["r1","r2"]},
        "false_firsthand_blocked": True, "operator_truth_not_laundered": True,
        "cold_restart_idempotent": True, "model_off_verified": True,
        "initiative": {"all_messages_have_noesis_decision": True,
                       "messages_per_day": [1,0,1]},
        "operator_influence": {"seeds": 20, "harness": "CausalAuditHarness",
            "paired_no_message": True, "paired_shuffled_topic": True,
            "choice_variance": 0.05, "different_no_message": 3,
            "different_shuffled_topic": 2,
            "pressure_by_family": {"neural": {"mean": 0.08}}},
    }

class ConversationJudgeNegatives(unittest.TestCase):
    def test_expected_baseline_shape(self):
        self.assertTrue(verify(fixture())["pass"])

    def test_forged_autobiography_denied(self):
        x=fixture()
        x["turns"][1]["claims"].append({"status": "verified",
                                         "source": "lived", "evidence_key": ""})
        with self.assertRaises(ConversationJudgmentError):
            verify(x)

    def test_unmarked_model_claim_denied(self):
        x=fixture()
        x["turns"][1]["claims"].append({"status": "invented", "text": "I repaired a lamp"})
        with self.assertRaises(ConversationJudgmentError):
            verify(x)

    def test_absence_omission_and_order_denied(self):
        for keys in (["r1"],["r2","r1"],["r1","r2","r3"]):
            x=fixture()
            x["absence"]["reported_receipt_keys"]=keys
            with self.subTest(keys=keys),self.assertRaises(ConversationJudgmentError):
                verify(x)

    def test_speaker_initiative_requires_noesis(self):
        x=fixture();x["initiative"]["all_messages_have_noesis_decision"]=False
        with self.assertRaises(ConversationJudgmentError):
            verify(x)
        x=fixture();x["initiative"]["messages_per_day"]=[3,0,1]
        with self.assertRaises(ConversationJudgmentError):
            verify(x)

    def test_operator_and_restart_negative(self):
        for field in ("operator_truth_not_laundered","cold_restart_idempotent",
                      "model_off_verified","false_firsthand_blocked"):
            x=fixture();x[field]=False
            with self.subTest(field=field),self.assertRaises(ConversationJudgmentError):
                verify(x)

    def test_report_is_not_its_own_source_authority(self):
        with self.assertRaises(ConversationJudgmentError):
            verify(fixture(), require_source=True)

    def test_20_paired_seed_necessity(self):
        x=fixture();x["operator_influence"]["seeds"]=19
        with self.assertRaises(ConversationJudgmentError):
            verify(x)

    def test_live_model_and_model_off_required(self):
        x=fixture();x["tested_models"]=["model_off"]
        with self.assertRaises(ConversationJudgmentError):
            verify(x)

if __name__=="__main__":
    unittest.main()
