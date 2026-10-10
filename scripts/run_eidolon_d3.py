#!/usr/bin/env python3
"""Execute one designed matched-clone Eidolon D3 policy plumbing test.

This uses a deterministic synthetic ten-action recurrent distribution, NOT a
measured Pretorius phenotype. The resulting action is a cognitive policy
tendency selected by Pretorius.think(), not an executed external action.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.eidolon_choice import run_disposable_policy_probe
from doctor_lives.neural import ACTIONS, DEFAULT_CONFIG


CONTROL = {action: 0.09625 for action in ACTIONS}
CONTROL["challenge"] = 0.120
CONTROL["persist"] = 0.110
assert abs(sum(CONTROL.values()) - 1.0) < 1e-12

CASES = (
    ("sham", False, True, True),
    ("intact", True, True, True),
    ("history_lesion", True, False, True),
    ("clock_lesion", True, True, False),
)


def small_config() -> dict:
    config = dict(DEFAULT_CONFIG)
    config.update({
        "neurons": 128, "sensory_dim": 64,
        "avg_recurrent_degree": 8, "input_degree": 4,
        "action_population_size": 8, "seed": 1842,
    })
    return config


def main() -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        source_dir = root / "source"
        source = PretoriusBrain(source_dir, neural_config=small_config())
        episode = source.ingest(Experience(
            "I examined the anatomical apparatus alongside Henry.",
            actor="Henry", kind="interaction", confidence=.9,
            novelty=.3, social=.7, valence=.4
        ))
        commitment_id = source.add_commitment(
            "Finish the anatomical apparatus",
            actor="Henry",
            due_tick=source.store.tick,
            importance=.8,
        )
        source.save()
        source_digest = source.store.digest()
        source_tick = source.neural.tick
        source_checkpoint = source._neural_checkpoint_sha256()

        outcomes: dict[str, dict] = {}
        for name, enable, history, temporal in CASES:
            clone_dir = root / name
            shutil.copytree(source_dir, clone_dir)
            (clone_dir / ".eidolon_disposable_clone").write_text(
                "single-use research clone; no production rights\n",
                encoding="utf-8",
            )
            clone = PretoriusBrain(clone_dir)
            equal_before = (
                clone.store.digest() == source_digest
                and clone.neural.tick == source_tick
                and clone._neural_checkpoint_sha256() == source_checkpoint
            )
            if not equal_before:
                raise AssertionError("D3 clone starting state does not match parent")
            # Explicit common controlled decoder / action distribution.
            clone.neural.action_scores = lambda: dict(CONTROL)
            result = run_disposable_policy_probe(
                clone, enabled=enable,
                with_history=history, with_temporal=temporal,
            )
            recorded = clone.store.thoughts(limit=1)
            if not recorded:
                raise AssertionError("Pretorius did not persist a cognitive thought")
            if clone._neural_checkpoint_sha256() != source_checkpoint:
                raise AssertionError("D3 unexpectedly modified recurrent checkpoint")
            outcomes[name] = {
                "selected_action": result.selected_action,
                "intervention_applied": result.injected,
                "source_commitment_in_gate": commitment_id in result.source_commitments,
                "source_episode_witness_in_gate": episode["event_id"] in result.source_evidence_events,
                "base_challenge": round(result.base_scores["challenge"], 9),
                "base_persist": round(result.base_scores["persist"], 9),
                "chosen_challenge": round(result.chosen_scores["challenge"], 9),
                "chosen_persist": round(result.chosen_scores["persist"], 9),
                "persisted_thought_count": len(recorded),
                "selected_memory_count": result.selected_memory_count,
                "identical_parent_state_at_clone_start": equal_before,
            }
        expected = {
            "sham": "challenge", "intact": "persist",
            "history_lesion": "challenge", "clock_lesion": "challenge",
        }
        for arm, action in expected.items():
            if outcomes[arm]["selected_action"] != action:
                raise AssertionError(
                    f"{arm} expected {action}, got {outcomes[arm]['selected_action']}"
                )
        return {
            "schema": "eidolon-d3-disposable-clone-policy-construction-v0.1",
            "github_sha": os.environ.get("GITHUB_SHA"),
            "precommitted_protocol": "docs/EIDOLON_D3_CLONED_POLICY_PROTOCOL.md",
            "epistemic_status": "synthetic controlled margin and hand-chosen goal; plumbing verification only",
            "parent_database_unchanged": source.store.digest() == source_digest,
            "parent_recurrent_tick_unchanged": source.neural.tick == source_tick,
            "parent_checkpoint_unchanged": source._neural_checkpoint_sha256() == source_checkpoint,
            "controlled_recurrent_action_distribution": CONTROL,
            "conditions": outcomes,
        }


if __name__ == "__main__":
    report = json.dumps(main(), indent=2, sort_keys=True) + "\n"
    if len(sys.argv) == 3 and sys.argv[1] == "--output":
        p = Path(sys.argv[2])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(report, encoding="utf-8")
        print(f"Eidolon D3 matched-clone assay: {p}")
    else:
        print(report, end="")
