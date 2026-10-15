"""Post-hoc factorial diagnosis of the exposed v0.2 delayed-paraphrase miss.

No runtime defaults, historical result, canonical memory or donor are changed.
This is not a new semantic-retrieval benchmark or an external-world success.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch

from doctor_lives.cascade_background import BackgroundLease
from tools.run_cascade_articles_pilot import open_host, percepts


def cycle(host, items, now):
    return host.cycle(
        items, trusted_source_refs=frozenset(p.source_ref for p in items), now_ms=now,
        cascade_grant=host.make_host_grant(
            permissions=frozenset({"observe", "communicate"}), max_percepts=2))


def run_diagnostic():
    rows = []
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        checkpoint = root / "checkpoint" / "three-organ-preview"
        for ordinal, session in enumerate(("history_observation", "history_conflict",
                                           "history_distraction", "delayed_question"), 1):
            host, _ = open_host(checkpoint, "cascade")
            with host:
                cycle(host, percepts(host, session), ordinal * 1000)
            if ordinal == 3:
                host, _ = open_host(checkpoint, "cascade")
                with host:
                    host.issue_background_lease(BackgroundLease("pilot", 1, 1, 1, 100000), authorized=True)
                    host.background_wake(lease_id="pilot", wake_id="pilot-wake",
                                         now_ms=3500, ticks=1, authorized=True)
        for prompt_kind in ("original_wording", "paraphrase"):
            for cooldown in (2, 1):
                path = root / f"{prompt_kind}-{cooldown}" / "three-organ-preview"
                shutil.copytree(checkpoint, path)
                host, renderer = open_host(path, "cascade")
                with host:
                    before = host._doctor.brain.store.digest()
                    items = percepts(host, "delayed_paraphrase")
                    if prompt_kind == "original_wording":
                        items = tuple(replace(p, value="What did the laboratory balance reading say earlier?") for p in items)
                    brain = host._doctor.brain
                    original = brain.research_endogenous_recall
                    captured = []

                    def instrumented(**kwargs):
                        # A declared policy-parameter intervention on an isolated
                        # copy, not a production fix or a deletion of history.
                        kwargs["cooldown_ticks"] = cooldown
                        check = brain.store.digest()
                        forecast = original(**{**kwargs, "persist": False})
                        if brain.store.digest() != check:
                            raise RuntimeError("Non-persisting policy probe changed state")
                        actual = original(**kwargs)
                        if forecast["selected_action"] != actual["selected_action"]:
                            raise RuntimeError("Prediction and committed policy diverged")
                        captured.append(actual)
                        return actual

                    with patch.object(brain, "research_endogenous_recall", side_effect=instrumented):
                        result = cycle(host, items, 5000)
                    if len(captured) != 1:
                        raise RuntimeError("Expected exactly one actual Doctor policy selection")
                    decision = captured[0]
                    frame = renderer.subject_inputs[-1]
                    with brain.store.connect() as db:
                        persisted = db.execute(
                            "SELECT selected_action,state_pressure_json FROM policy_decisions WHERE id=?",
                            (result["endogenous_decision_id"],)).fetchone()
                    stored_audit = json.loads(persisted["state_pressure_json"])
                    rows.append(dict(
                        wording=prompt_kind, cooldown_ticks=cooldown,
                        pre_session_state_digest=before,
                        policy_action=result["endogenous_action"],
                        persisted_action=persisted["selected_action"],
                        cooldown_active=stored_audit["information_need_family"]["cooldown_active"],
                        information_need=stored_audit["information_need_family"]["recall_pressure"],
                        raw_scores=stored_audit["deliberative_raw_scores"],
                        source_fact_accessible="325 grams" in frame,
                        disputed_fact_leaked=any(x in frame for x in ("451 grams", "919 grams")),
                        subject_input_sha256=hashlib.sha256(frame.encode()).hexdigest(),
                        decision_id=result["endogenous_decision_id"],
                        governor_allowed=renderer.receipts[-1].allowed,
                    ))
    source_root = Path(__file__).resolve().parents[1]
    paths = ("tools/run_cascade_cooldown_diagnostic.py", "tools/run_cascade_articles_pilot.py",
             "doctor_lives/cognition.py", "doctor_lives/three_organ_preview.py")
    return dict(schema="pretorius.cascade.cooldown-diagnostic.v1",
                classification="post-hoc author-designed mechanism diagnosis of an exposed miss",
                baseline_commit="09df2169b6d9359336d9dbec93888f56af0613c9",
                manipulated_factors=["user-message wording", "cooldown policy parameter"],
                common_checkpoint=len({r["pre_session_state_digest"] for r in rows}) == 1,
                runtime_defaults_changed=False, real_llm_calls=0,
                external_task_outcomes_measured=False, semantic_generalization_tested=False,
                independent_holdout=False, trials=rows,
                source_sha256={p:hashlib.sha256((source_root / p).read_bytes()).hexdigest() for p in paths})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run_diagnostic()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
