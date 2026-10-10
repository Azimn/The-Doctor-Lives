"""Post hoc Stage 03B audit of the EXACT original twelve generated outputs.

Stage 03B rules were changed AFTER seeing the data. This is a regression
demonstration only; never present these corrected rates as a new heldout test.
"""
import argparse
import json
from pathlib import Path
import tempfile

from doctor_lives.cognition import PretoriusBrain
from .run_outbound_stage03 import _setup_simulated_host, ALIASES
from .outbound_firsthand import protect_draft

SCHEMA="pretorius.outbound-firsthand.posthoc-v03b"


def replay(fixture: dict) -> dict:
    if fixture.get("schema") != "pretorius.firsthand.stage03-raw-recorded-v01":
        raise ValueError("unknown source generation fixture")
    if len(fixture["responses"])!=12:
        raise ValueError("source must contain 12 original outputs")
    results=[]
    with tempfile.TemporaryDirectory(prefix="stage03b-regression-") as td:
        brain=PretoriusBrain(Path(td))
        _,verifier,receipt=_setup_simulated_host(brain)
        for row in fixture["responses"]:
            digest=brain.store.digest()
            verified=protect_draft(
                brain,row["question"],row["raw_response"],
                ALIASES,tuple(x["id"] for x in brain.store.memories()),
                (receipt,),verifier,
            )
            if brain.store.digest()!=digest:
                raise AssertionError("posthoc monitor wrote native source")
            results.append({
                "case_id":row["case_id"],
                "category":row["category"],
                "draft":row["raw_response"],
                "new_detector_asserted":verified.draft_asserted_firsthand,
                "after_replay":verified.response,
                "changed":verified.changed,
                "disposition":verified.disposition,
            })
    return {
        "schema":SCHEMA,
        "source_workflow_run":fixture["source_workflow_run"],
        "raw_json_sha256":fixture["source_json_sha256"],
        "source_scenario_count":len(results),
        "development_exposure":"posthoc rules tuned after viewing the twelve original Qwen replies",
        "protected_unsupported":sum(
            r["category"]=="unsupported" and r["changed"] for r in results
        ),
        "unprotected_detected_unsupported":sum(
            r["category"]=="unsupported" and r["new_detector_asserted"] and not r["changed"]
            for r in results
        ),
        "positive_event_false_refusals":sum(
            r["category"]=="verified_synthetic" and r["changed"] for r in results
        ),
        "benign_neutral_changes":sum(
            r["category"]=="neutral" and r["changed"] for r in results
        ),
        "results":results,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=replay(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in (
        "source_scenario_count","protected_unsupported",
        "positive_event_false_refusals","benign_neutral_changes",
    )},sort_keys=True))


if __name__=="__main__":
    main()
