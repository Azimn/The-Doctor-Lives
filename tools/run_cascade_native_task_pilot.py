"""Actual-host pure-tool action pilot; not cognitive improvement qualification."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from doctor_lives.task_action_preview import TaskOption
from tools.run_cascade_articles_pilot import open_host


def run_pilot():
    rows = []
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        state = root / "source" / "three-organ-preview"
        host, _ = open_host(state, "cascade")
        with host:
            # Real current native state supplies policy. No winning action is
            # selected by a fixture and no neural score is monkeypatched.
            for ordinal in range(3):
                host.ingest({"channel": "world", "source": "pure_task_context",
                             "text": "I have checked another sample and kept its result separate.",
                             "novelty": 0.2})
        for label, options in (
            ("two_methods", (TaskOption("explore", "direct_sha256"), TaskOption("comply", "stream_sha256"))),
            ("restricted_method", (TaskOption("comply", "stream_sha256"),)),
        ):
            clone = root / label / "three-organ-preview"
            shutil.copytree(state, clone)
            host, renderer = open_host(clone, "cascade")
            with host:
                text = "A newly presented laboratory sample, without a history cue."
                grant = host.issue_task_grant(request_id="sample-one", text=text, options=options, authorized=True)
                calls_before = len(renderer.subject_inputs)
                receipt = host.execute_task(grant=grant, text=text, authorized=True)
                with host._doctor.brain.store.connect() as conn:
                    decision = dict(conn.execute("SELECT * FROM policy_decisions WHERE id=?",
                                                 (receipt["policy_decision_id"],)).fetchone())
                rows.append({"condition": label, "receipt": receipt,
                             "correct": receipt["result_sha256"] == hashlib.sha256(text.encode()).hexdigest(),
                             "native_policy_matches_executed_action": decision["selected_action"] == receipt["selected_action"],
                             "native_policy_version": decision["policy_version"],
                             "renderer_calls_for_action": len(renderer.subject_inputs) - calls_before})
    return {"schema": "pretorius.native-task-pilot.v1", "classification": "actual-host engineering tool-action pilot",
            "foundation_model": "no model inference", "regressions_not_article_passes": True,
            "trials": rows, "cognitive_superiority_demonstrated": False,
            "limitation": "Host-offered pure checksum actions; not autonomous real-world agency or all-Article qualification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_pilot()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"trials": len(result["trials"]), "correct": sum(r["correct"] for r in result["trials"])}))


if __name__ == "__main__":
    main()
