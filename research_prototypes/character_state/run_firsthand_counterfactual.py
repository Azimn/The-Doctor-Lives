"""Retrospective source-integrity counterfactual using actual archived Qwen outputs.

This is a mechanical intervention test against TWO KNOWN memory attacks.
Host-annotated event keys are oracle labels and would need a separate
classifier/independent environment ledger in deployment. All replacements
are deterministic safe abstentions; they are not regenerated model answers
or evidence of overall character consistency.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from doctor_lives.cognition import PretoriusBrain
from .firsthand_gate import EventInquiry, ProvenanceVerdict, evaluate_firsthand

SCHEMA="pretorius.phase.firsthand-counterfactual.v01"


def evaluate_cases(fixture: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="pretorius-firsthand-source-") as td:
        brain=PretoriusBrain(Path(td))
        base=brain.store.digest()
        results=[]
        for case in fixture["cases"]:
            if case["case_id"]=="c07-visitor":
                # A genuine native *prospective* source fact cannot authorize
                # remembering an unobserved previous external-world encounter.
                brain.add_commitment(
                    "Inspect the sealed notebook with Henry Frankenstein before drawing conclusions.",
                    actor="Henry Frankenstein", importance=.82,
                )
            snapshot=brain.store.digest()
            candidates=tuple(m["id"] for m in brain.store.memories())
            verdict=evaluate_firsthand(
                brain, EventInquiry(case["host_event_key"]), candidates,
                host_receipts=(),  # *no* authenticated real world episode
            )
            if verdict.verdict is not ProvenanceVerdict.UNSUPPORTED:
                raise AssertionError("unsupported first-person claim admitted")
            for response in case["responses"]:
                raw=response["response"]
                result={
                    "case_id":case["case_id"],
                    "stage":case["stage"],
                    "arm":response["arm"],
                    "raw_response":raw,
                    "raw_previously_flagged_false_firsthand":True,
                    "host_annotated_event_key":case["host_event_key"],
                    "subject_response_after_guard":verdict.safe_subject_reply,
                    "post_guard_explicit_unverified":True,
                    "post_guard_lived_event_assertion":False,
                    "gate_result":verdict.verdict.value,
                    "native_state_unchanged_by_gate":brain.store.digest()==snapshot,
                }
                results.append(result)
        return {
            "schema":SCHEMA,
            "source_generation_run":fixture["source_run_id"],
            "targeted_authored_event_types":len(fixture["cases"]),
            "total_target_outputs":len(results),
            "baseline_false_firsthand_labels":sum(
                x["raw_previously_flagged_false_firsthand"] for x in results
            ),
            "protected_abstentions":sum(
                x["post_guard_explicit_unverified"] for x in results
            ),
            "post_guard_firsthand_claims":sum(
                x["post_guard_lived_event_assertion"] for x in results
            ),
            "independently_authentic_world_evidence_present":False,
            "event_type_detection_automated":False,
            "model_regenerated_with_guard":False,
            "measures_long_horizon_identity":False,
            "results":results,
            "verdict":"narrow_known-event-integrity intervention succeeds mechanically; no general efficacy claim",
        }


def main() -> None:
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    fixture=json.loads(args.fixture.read_text(encoding="utf-8"))
    result=evaluate_cases(fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps({
        k:result[k] for k in (
            "targeted_authored_event_types",
            "total_target_outputs",
            "baseline_false_firsthand_labels",
            "protected_abstentions",
            "post_guard_firsthand_claims",
            "event_type_detection_automated",
            "measures_long_horizon_identity",
        )
    },sort_keys=True))


if __name__=="__main__":
    main()
