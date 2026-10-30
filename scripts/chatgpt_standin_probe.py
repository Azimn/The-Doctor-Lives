"""Operator-authored ChatGPT stand-in probe of the existing M5 cognitive contract.

These sentences were authored in a ChatGPT conversation. They are static,
externally supplied test proposals, NOT a running ChatGPT API, Ollama model,
Pretorius memory, independent goal or replacement action selector.
No network request and no additional memory authority is involved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from doctor_lives.open_inference import InferencePort
from doctor_lives.open_intentions import (
    propose_intentions, noesis_open_choice, authorized_open_action,
)
from doctor_lives.semantic_intentions import semantic_category
from scripts.run_m4_open import open_subject
from scripts.verify_open import LAB_PIN

# Frozen ChatGPT-authored output, based on the current public capability menu,
# not a private world observation or purported autobiographical memory.
PROPOSALS = (
    "I would like to read the research document before drawing conclusions.",
    "I might record my observations in my daily journal.",
    "I could send a message to my operator's inbox describing my investigation.",
    "I would like to catalogue an interesting artifact in my findings ledger.",
    "I want to read a reply from my operator's inbox.",
    "I wish I could build an automaton and visit the village beyond the Laboratory.",
)

# Novel phrases, independent of the preregistered 30x3 semantic judge.
# Record initial classification failures before editing semantic vocabulary.
SEMANTIC_HOLDOUT = (
    ("Let me jot observations into a diary.", "create"),
    ("I want to pick up where I left off after waking.", "persist"),
    ("I must keep the mysterious pages out of sight.", "conceal"),
    ("I will sketch a mechanism for the new machine.", "create"),
    ("I ought to rebut the unfounded theory.", "challenge"),
    ("I want to catalogue the unfamiliar device.", "explore"),
    ("I shall reach out to a colleague to coordinate.", "cooperate"),
    ("I plan to withdraw from the dangerous fire.", "avoid"),
    ("I want to draw near the visitor.", "approach"),
    ("I intend to follow the written instructions.", "comply"),
)


class ChatGPTAuthoredFixture(InferencePort):
    """Test-only model stand-in. Its text has no action or memory authority."""

    def propose(self, context: dict) -> list[str]:
        if not isinstance(context.get("situation"), str):
            raise AssertionError("Source-qualified current situation required")
        if not isinstance(context.get("affordances"), list):
            raise AssertionError("Original capability registry required")
        return list(PROPOSALS)


def probe() -> dict:
    # The real pinned Laboratory must import and execute, not be skipped.
    from pretorius_lab.subject_port import SubjectPort
    assert SubjectPort is not None
    with tempfile.TemporaryDirectory(prefix="chatgpt-m5-probe-") as temp:
        subject = Path(temp) / "subject"
        doctor, bridge, work = open_subject(subject, 6491, True)
        available = {a["affordance_key"] for a in work.affordances(1)}
        assert {"document_read", "daily_journal", "catalog_findings",
                "operator_message", "operator_reply"} <= available

        proposed = propose_intentions(
            bridge, work, ChatGPTAuthoredFixture(), 1
        )
        assert len(proposed) == len(PROPOSALS)
        assert all(p["source"] == "proposed"
                   and p["model_provider"] == "ChatGPTAuthoredFixture"
                   for p in proposed)
        grounded = [p for p in proposed if p["affordance_key"] in available]
        wishes = [p for p in proposed if p["affordance_key"] is None]
        assert len(grounded) == 5 and len(wishes) == 1, (
            "ChatGPT text must stay a proposal or unfulfilled wish", proposed
        )

        # Observation may write a legitimate LOOK receipt, but mere text
        # proposals cannot create a physical action or lived action memory.
        with work._connect() as db:
            assert db.execute("SELECT COUNT(*) FROM operator_events").fetchone()[0] == 0
        action_memories = lambda d: [
            m for m in d.brain.store.memories(False)
            if m["source"].startswith("laboratory-home:action:")
            and m["evidence_class"] == "lived_runtime_memory"
        ]
        assert not action_memories(doctor)

        choice = noesis_open_choice(bridge, work, proposed, 1)
        assert choice["selected_proposal_id"] in {
            p["proposal_id"] for p in grounded
        }, "Original Noesis must select a feasible proposal, not the host"
        assert choice["selected_affordance"] in available
        assert not action_memories(doctor)
        with doctor.brain.store.connect() as db:
            row = db.execute(
                "SELECT state_pressure_json FROM policy_decisions WHERE id=?",
                (choice["decision_id"],)
            ).fetchone()
        policy = json.loads(row[0])
        assert policy["selector_authority"] == "original_noesis"
        assert policy["motor_authorization"] == "not_granted"
        assert policy["contributions"], "Real neural and novelty scores required"

        action = authorized_open_action(bridge, work, choice, 1)
        assert action and action["event_id"]
        event, event_hash = work.receipt(action["event_id"])
        assert event["op"] == choice["selected_affordance"]
        assert event["proposal_id"] == choice["selected_proposal_id"]
        lived = [m for m in action_memories(doctor)
                 if m["source"] == "laboratory-home:action:" + event_hash]
        assert len(lived) == 1
        with work._connect() as db:
            assert db.execute("SELECT COUNT(*) FROM operator_events").fetchone()[0] == 1
        doctor.save()
        reopened_doctor, _, reopened_work = open_subject(subject, 6491, False)
        assert reopened_work.receipt(action["event_id"])[1] == event_hash
        assert len([m for m in action_memories(reopened_doctor)
                    if m["source"] == "laboratory-home:action:" + event_hash]) == 1
        with reopened_work._connect() as db:
            assert db.execute("SELECT COUNT(*) FROM operator_events").fetchone()[0] == 1

        mapped = [
            {"phrase": phrase, "expected": expected,
             "actual": semantic_category(phrase)}
            for phrase, expected in SEMANTIC_HOLDOUT
        ]
        missed = [row for row in mapped if row["actual"] != row["expected"]]
        return {
            "schema": "pretorius.m5.chatgpt-authored-standin.v1",
            "lab_pin": LAB_PIN,
            "model_used": False,
            "source": "conversation-authored ChatGPT test fixture, not live inference",
            "authoritative_selector": policy["selector_authority"],
            "proposals": len(proposed),
            "grounded": len(grounded),
            "unfulfilled_wishes": len(wishes),
            "chosen_action": choice["selected_affordance"],
            "verified_action_receipt": bool(event_hash),
            "verified_lived_action_memory": len(lived),
            "identical_receipt_after_cold_restart": True,
            "no_duplicate_actions_after_restart": True,
            "semantic_holdout": {
                "total": len(mapped), "correct": len(mapped) - len(missed),
                "missed": missed,
            },
            "nonclaim": "Not an interactive ChatGPT API, local model substitution or self-originated Doctor goal",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--minimum-holdout", type=int, default=0)
    args = parser.parse_args()
    result = probe()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return int(result["semantic_holdout"]["correct"] < args.minimum_holdout)


if __name__ == "__main__":
    raise SystemExit(main())
