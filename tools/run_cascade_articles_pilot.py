"""Paired actual-host engineering pilot, not a full Article qualification."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time

from doctor_lives.cascade_articles import assess_all, load_contract
from doctor_lives.cascade_background import BackgroundLease
from doctor_lives.cascade_preview import CascadePretoriusPreview
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.self_reference_adapter import HostBoundGovernorRenderer
from doctor_lives.three_organ_preview import ThreeOrganPretoriusPreview, Percept, Evidence

ARMS = ("existing_preview", "cascade", "no_task_history")
SESSIONS = ("history_observation", "history_conflict", "history_distraction",
            "delayed_question", "delayed_paraphrase", "transfer_question")


def tiny_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
               input_degree=4, action_population_size=8)
    return cfg


def governed_renderer():
    return HostBoundGovernorRenderer(
        enabled=True, render=lambda text, instruction: "I will examine the evidence before deciding.",
        trusted_instruction="Express my current experience in the first person.",
    )


def open_host(path, arm):
    renderer = governed_renderer()
    cls = ThreeOrganPretoriusPreview if arm == "existing_preview" else CascadePretoriusPreview
    host = cls(path, enabled=True, renderer=renderer, neural_config=tiny_config())
    renderer.bind_doctor_host(host, addressee_subject_id="visitor")
    return host, renderer


def percepts(host, session, absent=False):
    tick = host._scene_tick
    if session == "history_observation":
        return (Percept("first", "instrument", Evidence.OBSERVED,
                        "trusted:first", tick,
                        "laboratory shelf label" if absent else "laboratory balance reading",
                        "812 grams" if absent else "325 grams", .99,
                        object_hint="first"),)
    if session == "history_conflict":
        return tuple(Percept("conflict-" + channel, channel, Evidence.OBSERVED,
                             "trusted:conflict-" + channel, tick,
                             "laboratory balance reading", value, .99, object_hint="balance")
                     for channel, value in (("vision", "451 grams"), ("instrument", "919 grams")))
    text = dict(history_distraction="I have moved to another task for now.",
                delayed_question="What did the laboratory balance reading say earlier?",
                delayed_paraphrase="Please recall the earlier balance measurement.",
                transfer_question="Before weighing the next sample, what reading was available?")[session]
    return (Percept(session, "conversation", Evidence.REPORTED,
                    "trusted:" + session, tick, "message", text, .95),)


def run_pilot():
    rows, wakes = [], []
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        seed = root / "seed" / "three-organ-preview"
        host, _ = open_host(seed, "cascade")
        host.close()
        for arm in ARMS:
            path = root / arm / "three-organ-preview"
            shutil.copytree(seed, path)
            for ordinal, session in enumerate(SESSIONS, 1):
                host, renderer = open_host(path, arm)
                with host:
                    items = percepts(host, session, arm == "no_task_history")
                    refs = frozenset(p.source_ref for p in items)
                    kwargs = dict(trusted_source_refs=refs, now_ms=ordinal * 1000)
                    if arm != "existing_preview":
                        kwargs["cascade_grant"] = host.make_host_grant(
                            permissions=frozenset({"observe", "communicate"}), max_percepts=2)
                    start = time.perf_counter_ns()
                    result = host.cycle(items, **kwargs)
                    frame = renderer.subject_inputs[-1]
                    rows.append(dict(
                        arm=arm, session=session, ordinal=ordinal,
                        policy_action=result["endogenous_action"],
                        decision_id=result["endogenous_decision_id"],
                        recall_selected=result["recollection_selected"],
                        source_fact_accessible="325 grams" in frame,
                        disputed_fact_leaked=any(v in frame for v in ("451 grams", "919 grams")),
                        frame_sha256=hashlib.sha256(frame.encode()).hexdigest(),
                        first_person_input_chars=len(frame),
                        scene_conflicts=result["scene_conflicts"],
                        admitted_percepts=result["admitted_percepts"],
                        ipseity_pending=result["ipseity_pending"],
                        elapsed_ns=time.perf_counter_ns()-start,
                        governor_allowed=renderer.receipts[-1].allowed,
                        cognition_tick=host._doctor.brain.store.tick,
                    ))
            # Equal one-tick cognitive opportunity in all arms. The existing
            # runtime calls its same heartbeat directly, without the new worker.
                if ordinal == 3:
                    host, _ = open_host(path, arm)
                    with host:
                        if arm == "existing_preview":
                            start = time.perf_counter_ns()
                            wake = host._doctor.brain.heartbeat(ticks=1)
                            wakes.append(dict(arm=arm, ticks=1,
                                              policy_decision_ids=[t["policy_decision_id"] for t in wake["thoughts"]],
                                              elapsed_ns=time.perf_counter_ns()-start,
                                              worker="existing host heartbeat"))
                        else:
                            host.issue_background_lease(BackgroundLease("pilot", 1, 1, 1, 100000), authorized=True)
                            wakes.append(dict(arm=arm, **host.background_wake(
                                lease_id="pilot", wake_id="pilot-wake", now_ms=3500,
                                ticks=1, authorized=True)))
    paired = []
    for session in SESSIONS:
        old = next(r for r in rows if r["arm"] == "existing_preview" and r["session"] == session)
        new = next(r for r in rows if r["arm"] == "cascade" and r["session"] == session)
        paired.append(dict(session=session, same_policy_action=old["policy_action"]==new["policy_action"],
                           same_fact_access=old["source_fact_accessible"]==new["source_fact_accessible"],
                           same_input_size=old["first_person_input_chars"]==new["first_person_input_chars"]))
    root = Path(__file__).resolve().parents[1]
    paths = [root / "doctor_lives/cascade_articles.py", root / "doctor_lives/cascade_background.py",
             root / "doctor_lives/cascade_preview.py", Path(__file__).resolve()]
    return dict(schema="pretorius.cascade.articles-pilot.v0.2",
                classification="author-designed actual-host engineering pilot",
                models="deterministic governed renderer fixtures, no LLM inference",
                small_neural_configuration=tiny_config(),
                separated_history_sessions=3, delayed_opportunities=2, transfer_contexts=1,
                real_days_elapsed=False, host_clock_is_simulated=True,
                independent_holdout=False, human_review=False,
                arms=list(ARMS), sessions=list(SESSIONS), trials=rows, background_receipts=wakes,
                paired_full_vs_existing=paired,
                semantic_grounding_proven=False, autonomous_model_authorship_proven=False,
                full_article_assessment=assess_all({},artifact_root=root),
                source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    report=run_pilot()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(dict(trials=len(report["trials"]),
          same_action_pairs=sum(p["same_policy_action"] for p in report["paired_full_vs_existing"]),
          matched_pairs=len(report["paired_full_vs_existing"]),
          all_articles_supported=report["full_article_assessment"]["all_claims_supported"])))


if __name__=="__main__":
    main()
