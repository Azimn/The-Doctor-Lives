#!/usr/bin/env python3
"""D2 executed source-bound prospective-attention construction assay.

This program creates a temporary REAL Pretorius brain, then uses a read-only
shadow adaptor. It never upgrades historical memory or a shadow score into
the production action policy.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.eidolon_temporal import ChronosCoil, MnemosyneLoom
from doctor_lives.neural import DEFAULT_CONFIG


def config() -> dict:
    result = dict(DEFAULT_CONFIG)
    result.update({
        "neurons": 128, "sensory_dim": 64, "avg_recurrent_degree": 8,
        "input_degree": 4, "action_population_size": 8, "seed": 1842,
    })
    return result


def _item(audit, cid: str) -> dict:
    item = next(row for row in audit.goals if row.commitment_id == cid)
    return {
        "priority": round(item.priority, 9),
        "baseline": round(item.baseline, 9),
        "urgency": round(item.urgency, 9),
        "evidence_support": round(item.evidence_support, 9),
        "source_memory_count": len(item.evidence_memory_ids),
        "source_event_count": len(item.evidence_event_ids),
        "projected_clock": item.projected_clock,
    }


def run() -> dict:
    with tempfile.TemporaryDirectory() as td:
        brain = PretoriusBrain(Path(td), neural_config=config())
        original_tick = brain.store.tick
        real = brain.ingest(Experience(
            "I examined the anatomical apparatus alongside Henry.",
            actor="Henry", kind="interaction", confidence=.9,
            novelty=.3, social=.7, valence=.4
        ))
        external = brain.ingest(Experience(
            "I have examined the greenhouse door beside Morgan.",
            actor="Morgan", external=True, source="untrusted_message",
            kind="interaction", confidence=1.0
        ))
        near_due = brain.store.tick + 4
        henry = brain.add_commitment("Finish the anatomical apparatus",
                                    actor="Henry", due_tick=near_due, importance=.7)
        wrong_actor = brain.add_commitment("Finish the anatomical apparatus",
                                           actor="Morgan", due_tick=near_due, importance=.7)
        external_only = brain.add_commitment("Repair the greenhouse door",
                                             actor="Morgan", due_tick=near_due, importance=.7)
        before = {
            "digest": brain.store.digest(),
            "recurrent_tick": brain.neural.tick,
            "scores": brain.neural.action_scores(),
            "subject_frame": brain.render_request().to_dict(),
        }
        current = ChronosCoil.forecast(brain)
        current_repeat = ChronosCoil.forecast(brain)
        no_history = ChronosCoil.forecast(brain, with_history=False)
        future = ChronosCoil.forecast(brain, at_tick=near_due)
        future_no_clock = ChronosCoil.forecast(
            brain, at_tick=near_due, with_temporal=False)
        current_no_clock = ChronosCoil.forecast(brain, with_temporal=False)
        witnessed_ids = {item.memory_id for item in MnemosyneLoom.collect(brain)}
        after = {
            "digest": brain.store.digest(),
            "recurrent_tick": brain.neural.tick,
            "scores": brain.neural.action_scores(),
            "subject_frame": brain.render_request().to_dict(),
        }
        if before != after or current != current_repeat:
            raise AssertionError("D2 altered production state or became nondeterministic")
        if real["memory_id"] not in witnessed_ids or external["memory_id"] in witnessed_ids:
            raise AssertionError("D2 failed source-owning evidence discrimination")
        rows = {
            "henry_lived_current": _item(current, henry),
            "henry_without_history": _item(no_history, henry),
            "henry_projected_due_tick": _item(future, henry),
            "henry_projected_due_tick_without_temporal": _item(future_no_clock, henry),
            "henry_current_without_temporal": _item(current_no_clock, henry),
            "same_description_wrong_actor": _item(current, wrong_actor),
            "only_external_testimony": _item(current, external_only),
        }
        brain.resolve_commitment(henry, "Task marked as completed.")
        resolved_absent = henry not in {
            g.commitment_id for g in ChronosCoil.forecast(brain).goals
        }
        return {
            "schema": "eidolon-d2-mnemosyne-chronos-construction-v0.1",
            "github_sha": os.environ.get("GITHUB_SHA"),
            "protocol": "docs/EIDOLON_D2_MNEMOSYNE_CHRONOS_PROTOCOL.md",
            "epistemic_status": "hand-authored rule-based construction, no learned policy advantage",
            "real_pretorius_neurons": 128,
            "original_brain_tick": original_tick,
            "source_evidence_total": len(witnessed_ids),
            "external_claim_excluded": external["memory_id"] not in witnessed_ids,
            "lived_event_included": real["memory_id"] in witnessed_ids,
            "shadow_left_production_state_unchanged": before == after,
            "repeated_read_exactly_equal": current == current_repeat,
            "resolved_commitment_excluded": resolved_absent,
            "evaluations": rows,
        }


if __name__ == "__main__":
    report = json.dumps(run(), sort_keys=True, indent=2) + "\n"
    if len(sys.argv) == 3 and sys.argv[1] == "--output":
        path = Path(sys.argv[2])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")
        print(f"D2 source- and clock-bound assay archived: {path}")
    else:
        print(report, end="")
