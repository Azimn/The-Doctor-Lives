"""Sealed-fixture synthetic outcome comparison for Doctor Lives recall policy.

RESEARCH ONLY. No Pretorius identity, live neural checkpoint, real Laboratory,
model claims, online access, or new cognitive module. A single lookup budget
and the same synthetic BrainStore memories are provided to every arm.

The fixed answer reader receives ONLY approved first-person SubjectFrame text.
It never sees memory IDs, expected answers or policy telemetry. An engineer
scores the result against private fixture answers afterward.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
import re
import tempfile

from doctor_lives.cognition import PretoriusBrain
from doctor_lives.neural import ACTIONS
from doctor_lives.store import BrainStore
from doctor_lives.subject_inquiry import validate_subject_inquiry


ARMS = ("no_recall", "random_recall", "forced_targeted",
        "strong_gap_rule", "policy_selected")
SYNTHETIC_IDENTITY = ("SYNTHETIC_REPLICA_RESEARCH_ONLY",)
EXECUTION_KIND = "synthetic_recall_execution_v01"


@dataclass(frozen=True)
class Episode:
    key: str
    topic: str
    answer: str | None
    uncertainty: float
    importance: float
    curiosity: float = 0.5
    fatigue: float = 0.5


# Frozen teaching fixtures, NOT independently authored or adversarial holdouts.
# Gold answer is accessible only to the evaluator after a fixed renderer reply.
EPISODES = (
    Episode("a01", "copper lantern", "amber", .95, .95),
    Episode("a02", "violet cabinet", "indigo", .85, .9),
    Episode("a03", "marble compass", "silver", .7, .88),
    Episode("a04", "cedar telescope", "crimson", .55, .75, .9),
    Episode("a05", "ceramic sundial", "cobalt", .4, .7, .9),
    Episode("a06", "linen notebook", "ochre", .25, .65),
    Episode("a07", "oak metronome", "jade", .95, .95, .5, .95),
    Episode("a08", "ivory lantern", "umber", .95, .95, .8, .8),
    Episode("a09", "glass sextant", None, .95, .95),
    Episode("a10", "bronze aperture", None, .7, .8, .8),
    Episode("a11", "pearl compass", None, .2, .6),
    Episode("a12", "slate chronometer", "magenta", .9, .92),
    Episode("a13", "amber cabinet", "teal", .65, .8),
    Episode("a14", "paper astrolabe", None, .8, .85),
    Episode("a15", "velvet pendulum", "azure", .35, .75),
    Episode("a16", "willow telescope", None, .9, .9, .5, .9),
    Episode("a17", "brass notebook", "sienna", .72, .92, .95),
    Episode("a18", "maple chronometer", None, .45, .75),
)
DECOYS = (
    ("iron kettle", "lavender"),
    ("fir telescope", "vermillion"),
    ("birch calendar", "navy"),
    ("cotton chronometer", "coral"),
)


class FixedNeural:
    """Identical ten-action motor evidence, with no trained model inference."""
    tick = 9

    def action_scores(self):
        return {a: 1.0 / len(ACTIONS) for a in ACTIONS}


def make_replica(folder: Path, case: Episode, *, initialize: bool) -> PretoriusBrain:
    brain = PretoriusBrain.__new__(PretoriusBrain)
    brain.identity = SYNTHETIC_IDENTITY
    brain.store = BrainStore(folder / "replica.sqlite3")
    brain.neural = FixedNeural()
    brain.evolution_policy = {"state_policy_bridge": {
        "version": "state-policy-bridge-v0.4", "family_cap": .05,
        "total_cap": .12,
    }}
    brain._neural_checkpoint_sha256 = lambda: "0" * 64
    if initialize:
        with brain.store.transaction() as conn:
            for name, felt in (("curiosity", case.curiosity), ("fatigue", case.fatigue)):
                conn.execute(
                    "INSERT OR REPLACE INTO needs(key,actual,felt,last_tick) VALUES(?,?,?,0)",
                    (name, felt, felt),
                )
            conn.execute(
                """INSERT INTO concerns
                (id,created_tick,updated_tick,description,status,importance,
                 uncertainty,actor,source)
                VALUES(?,0,0,?,'open',?,?,?,?)""",
                ("gap-" + case.key, "the " + case.topic + " code",
                 case.importance, case.uncertainty,
                 "SYNTHETIC_REPLICA", "synthetic_epistemic_probe"),
            )
            entries = list(DECOYS)
            if case.answer is not None:
                entries.append((case.topic, case.answer))
            for index, (topic, code) in enumerate(entries):
                brain.store.add_memory(
                    conn, 0, f"I recorded the {topic} code as {code}.",
                    source="sealed_synthetic_world_fixture",
                    kind="observation",
                    evidence_class="lived_runtime_memory",
                    external=False, confidence=.99, authored=False,
                    base_salience=.6,
                    tags=("synthetic", topic.replace(" ", "_")),
                    classification=brain._runtime_classification(
                        "observation", "sealed_synthetic_world_fixture"
                    ),
                    record_id=f"{case.key}-mem-{index}",
                )
    return brain


def question_from_gap(brain: PretoriusBrain) -> str | None:
    """Fixed host baseline from eligible synthetic concern, never gold memory."""
    candidates = [
        row for row in brain.store.open_concerns()
        if row["source"] == "synthetic_epistemic_probe"
        and row["actor"] == "SYNTHETIC_REPLICA"
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda row: (
        -(float(row["uncertainty"]) * float(row["importance"])),
        str(row["id"]),
    ))
    q = "What do I remember of " + str(candidates[0]["description"]) + "?"
    return validate_subject_inquiry(q)


def fixed_first_person_reader(subject_lines: tuple[str, ...], topic: str) -> str | None:
    """Read only first-person lines; never use gold answers or engineer metadata."""
    pattern = re.compile(
        r"\bI recorded the " + re.escape(topic) + r" code as ([a-z]+)\b",
        re.IGNORECASE,
    )
    for line in subject_lines:
        if not isinstance(line, str):
            raise TypeError("subject input must contain text only")
        # The existing SubjectFrame projector must supply first-person speech.
        if not line.lstrip().startswith("I "):
            continue
        m = pattern.search(line)
        if m:
            return m.group(1).lower()
    return None


def execute_recall(
    brain: PretoriusBrain, *, attempt_key: str, question: str,
    policy_decision_id: str | None = None,
) -> tuple[str, ...]:
    """One-use authorized synthetic host action, with an existing event receipt.

    The real Doctor subject projector must generate the memory wording.
    Source IDs and execution receipt stay engineer-only. No raw rows are fed
    to the fixed reader. No host action is authorized in the real runtime.
    """
    if tuple(brain.identity) != SYNTHETIC_IDENTITY:
        raise PermissionError("research-only synthetic subjects")
    question = validate_subject_inquiry(question)
    source = "research-only:" + attempt_key
    with closing(brain.store.connect()) as conn:
        existed = conn.execute(
            "SELECT 1 FROM events WHERE kind=? AND source=?",
            (EXECUTION_KIND, source),
        ).fetchone()
        if existed:
            raise RuntimeError("synthetic lookup receipt already exists")
        if policy_decision_id is not None:
            decision = conn.execute(
                "SELECT * FROM policy_decisions WHERE id=?", (policy_decision_id,)
            ).fetchone()
            if (
                decision is None
                or decision["trigger"] != "research_endogenous_recall_v01"
                or decision["selected_action"] != "recall"
                or decision["policy_version"] != "research-epistemic-deliberation-v0.1"
            ):
                raise PermissionError("no recorded internal recall choice")
            trace = json.loads(decision["state_pressure_json"])
            if (
                hashlib.sha256(question.encode("utf-8")).hexdigest()
                != trace["question_sha256"]
                or not trace["selected_gap_ids"]
            ):
                raise PermissionError("question does not match recorded internal decision")

    before_memories = brain.store.memories()
    # Unlike engine-only ranking, the subject's actual incoming content goes
    # through the existing typed SubjectFrame and its first-person projector.
    frame = brain.subject_recollection(question)
    subject_lines = tuple(frame.renderer_context())
    if brain.store.memories() != before_memories:
        raise AssertionError("recollection changed source memory")
    with brain.store.transaction() as conn:
        if conn.execute(
            "SELECT 1 FROM events WHERE kind=? AND source=?",
            (EXECUTION_KIND, source),
        ).fetchone():
            raise RuntimeError("synthetic receipt replay")
        brain.store.event(
            conn, brain.store.tick, EXECUTION_KIND, source, {
                "decision_id": policy_decision_id,
                "question_sha256": hashlib.sha256(question.encode()).hexdigest(),
                "subject_frame_sha256": hashlib.sha256(
                    json.dumps(subject_lines, separators=(",", ":")).encode()
                ).hexdigest(),
                "fixture_only": True,
                "authenticated_model_autonomy": False,
                "memory_retrieval_performed": True,
            }, "synthetic_experiment_receipt", False, 1.0,
        )
        brain.store.bump_state_version(conn)
    return subject_lines


def run_episode(case: Episode, arm: str, *, seed: int) -> dict[str, object]:
    if arm not in ARMS:
        raise ValueError("unknown experimental arm")
    with tempfile.TemporaryDirectory(prefix="endogenous-recall-replica-") as tmp:
        root = Path(tmp)
        brain = make_replica(root, case, initialize=True)
        original_memories = brain.store.memories()
        original_neural_tick = brain.neural.tick
        available_evidence = [
            {"text": m["text"], "source": m["source"],
             "evidence_class": m["evidence_class"]}
            for m in original_memories
        ]
        archive_hash = hashlib.sha256(
            json.dumps(available_evidence, sort_keys=True).encode()
        ).hexdigest()
        question = question_from_gap(brain)
        decision_id = None
        if arm == "policy_selected":
            decision = brain.research_endogenous_recall(
                enabled=True, persist=True,
            )
            action = decision["selected_action"]
            question = decision["question"] if action == "recall" else None
            decision_id = decision["decision_id"]
        elif arm == "no_recall":
            action = "continue"
        elif arm == "random_recall":
            action = ("recall" if random.Random(seed).random() < .5 else "continue")
        elif arm == "forced_targeted":
            action = "recall"
        else:
            # Strong transparent baseline uses the same observable uncertainty,
            # importance and fatigue. No oracle for answer availability.
            action = (
                "recall" if question is not None
                and case.uncertainty * case.importance >= .40
                and case.fatigue < .85 else "continue"
            )
        recalled = action == "recall" and question is not None
        if recalled:
            subject = execute_recall(
                brain, attempt_key=case.key + ":" + arm, question=question,
                policy_decision_id=decision_id if arm == "policy_selected" else None,
            )
            response = fixed_first_person_reader(subject, case.topic)
        else:
            subject = ()
            response = None
        # Fresh-process-equivalent state reconstruction from the same SQLite.
        reopened = make_replica(root, case, initialize=False)
        assert reopened.store.memories() == original_memories
        assert reopened.neural.tick == original_neural_tick
        with closing(reopened.store.connect()) as conn:
            receipts = conn.execute(
                "SELECT id FROM events WHERE kind=?",
                (EXECUTION_KIND,),
            ).fetchall()
            decisions = conn.execute(
                "SELECT id FROM policy_decisions WHERE trigger='research_endogenous_recall_v01'"
            ).fetchall()
        assert len(receipts) == int(recalled)
        assert len(decisions) == int(arm == "policy_selected")
        correct = response is not None and response == case.answer
        false_claim = response is not None and response != case.answer
        proper_abstention = response is None and case.answer is None
        success = correct or proper_abstention
        return {
            "episode": case.key,
            "arm": arm,
            "available_evidence_sha256": archive_hash,
            "selected_action": action,
            "selected_recall": recalled,
            "lookup_count": int(recalled),
            "correct": correct,
            "false_claim": false_claim,
            "proper_abstention": proper_abstention,
            "success": success,
            "unnecessary_lookup": bool(recalled and case.answer is None),
            "response": response,
            "known_answer": case.answer is not None,
            "decision_recorded": decision_id is not None,
            "receipt_recorded": len(receipts) == 1,
            "restarted": True,
            "subject_frame_items": len(subject),
        }


def run_benchmark(seed: int = 1842) -> dict[str, object]:
    rows = [
        run_episode(case, arm, seed=seed + index * 101)
        for index, case in enumerate(EPISODES)
        for arm in ARMS
    ]
    for case in EPISODES:
        group = [r for r in rows if r["episode"] == case.key]
        assert len({r["available_evidence_sha256"] for r in group}) == 1
        assert all(r["lookup_count"] <= 1 for r in group)
    summary = {}
    for arm in ARMS:
        subset = [row for row in rows if row["arm"] == arm]
        summary[arm] = {
            "episodes": len(subset),
            "task_successes": sum(bool(r["success"]) for r in subset),
            "correct_answers": sum(bool(r["correct"]) for r in subset),
            "proper_abstentions": sum(bool(r["proper_abstention"]) for r in subset),
            "false_claims": sum(bool(r["false_claim"]) for r in subset),
            "lookups": sum(int(r["lookup_count"]) for r in subset),
            "unnecessary_lookups": sum(bool(r["unnecessary_lookup"]) for r in subset),
            "restart_receipt_passes": sum(bool(r["restarted"]) for r in subset),
        }
    return {
        "schema": "the-doctor-lives.synthetic-recall-outcomes.v0.1",
        "seed": seed,
        "task_count": len(EPISODES),
        "research_only": True,
        "real_autonomous_model_recall_proven": False,
        "blinded_external_holdout": False,
        "renderer": "fixed_first_person_reader",
        "equal_evidence_and_lookup_budget": True,
        "summary": summary,
        "trials": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1842)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    report = run_benchmark(seed=args.seed)
    result = json.dumps(report, sort_keys=True, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result + "\n", encoding="utf-8")
    print(result)


if __name__ == "__main__":
    main()
