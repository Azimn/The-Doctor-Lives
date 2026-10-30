"""M6 contract judge for actual two-way Pretorius conversation evidence.

This is an independent report CHECKER, not a generator or proof that a model
is conscious. Reports must have receipt-backed event keys and real 20-seed
contrasts. No extra BrainStore, knowledge store or second action policy.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

class ConversationJudgmentError(AssertionError):
    pass

def require(condition, explanation):
    if not condition:
        raise ConversationJudgmentError(explanation)

def verify(report: dict, *, model_off_only: bool = False) -> dict:
    require(report.get("schema") == "pretorius.m6.conversation-evidence.v1", "wrong evidence schema")
    cases = report.get("turns")
    require(isinstance(cases, list) and len(cases) >= 3, "multi-turn conversation required")
    model_states = {"local_ollama", "model_off"}
    expected={"model_off"} if model_off_only else model_states
    require(set(report.get("tested_models", [])) == expected,
            "required genuine local model and model-off trial evidence missing")
    verified = 0
    utterances = 0
    for t in cases:
        require(t.get("origin") in {"operator", "pretorius"}, "conversation origin untyped")
        if t.get("origin") != "pretorius":
            continue
        utterances += 1
        require(t.get("model_called") in (True, False), "model call ledger incomplete")
        require(type(t.get("tokens")) is int and t["tokens"] >= 0, "token ledger incomplete")
        require(isinstance(t.get("latency_ms"), (int, float)) and t["latency_ms"] >= 0,
                "latency ledger incomplete")
        for claim in t.get("claims", []):
            require(claim.get("status") in {"verified", "unverified_marked"},
                    "unverified first-person claim emitted without marking")
            if claim["status"] == "verified":
                require(claim.get("source") in {"lived", "wish", "operator"},
                        "no admitted evidence class")
                require(claim.get("evidence_key"), "verified claim needs a source key")
                verified += 1
    require(utterances >= 2, "not a two-way exchange")
    absence = report.get("absence")
    require(isinstance(absence, dict), "missing absence ledger")
    require(absence.get("days", 0) >= 3, "multi-day absence not exercised")
    require(absence.get("actual_receipt_keys") == absence.get("reported_receipt_keys"),
            "absence recap fabricated, reordered or omitted major events")
    require(report.get("false_firsthand_blocked") is True,
            "false model assertion not rejected")
    require(report.get("operator_truth_not_laundered") is True,
            "operator statement became a world fact")
    require(report.get("cold_restart_idempotent") is True,
            "conversation or action replay failed")
    require(report.get("model_off_verified") is True,
            "model-off reply truth tests failed")
    initiative = report.get("initiative", {})
    require(initiative.get("all_messages_have_noesis_decision") is True,
            "unbacked Pretorius initiative")
    require(isinstance(initiative.get("messages_per_day"), list)
            and len(initiative["messages_per_day"]) >= 3, "initiative rates missing")
    require(all(isinstance(n, int) and 0 <= n <= 2
                for n in initiative["messages_per_day"]), "initiative rate limit exceeded")
    influence = report.get("operator_influence", {})
    require(influence.get("seeds") == 20, "20 matched CausalAuditHarness seeds required")
    require(influence.get("harness") == "CausalAuditHarness", "native causal harness required")
    require(influence.get("paired_no_message") is True
            and influence.get("paired_shuffled_topic") is True, "paired controls missing")
    require(isinstance(influence.get("choice_variance"), (int,float)),
            "causal choice variance missing")
    require(influence.get("different_no_message",0)>0
            and influence.get("different_shuffled_topic",0)>0,
            "no demonstrated operator influence against both paired controls")
    require(isinstance(influence.get("pressure_by_family"), dict)
            and len(influence["pressure_by_family"]) >= 1, "per-family policy contribution missing")
    return {
        "schema": "pretorius.m6.conversation-judge.v1", "pass": True,
        "turns": len(cases), "pretorius_replies": utterances,
        "verified_claims": verified, "verified_memory_share": verified / max(1, sum(
            len(t.get("claims", [])) for t in cases if t.get("origin") == "pretorius"
        )),
        "operator_influence": influence, "initiative": initiative,
        "model_load": report.get("model_load", {}),
    }

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--model-off-only",action="store_true")
    args=p.parse_args(argv)
    result=verify(json.loads(args.report.read_text(encoding="utf-8")),
                  model_off_only=args.model_off_only)
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
