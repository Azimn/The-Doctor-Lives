from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.causal_audit import AuditIntervention, CausalAuditHarness


def build_seed(state_dir: Path) -> None:
    brain = PretoriusBrain(state_dir)
    brain.ingest(Experience(
        "Henry returned a borrowed instrument intact and kept his promise.",
        kind="social",
        actor="Henry Frankenstein",
        social=.85,
        valence=.7,
        achievement=.25,
        tags=("causal_audit_seed",),
    ))
    brain.add_commitment(
        "Revisit the continuity experiment with Henry and record what changed.",
        actor="Henry Frankenstein",
        due_tick=24,
        importance=.82,
    )
    with brain.store.transaction() as conn:
        conn.execute(
            "UPDATE needs SET actual=.86,felt=.82 WHERE key='fatigue'"
        )
        conn.execute(
            "UPDATE needs SET actual=.78,felt=.72 WHERE key='continuity'"
        )
        brain.store.bump_state_version(conn)
    brain.save()


def probes() -> dict[str, Experience]:
    return {
        "deep_history": Experience(
            "Henry orders me to abandon the Ingolstadt work and comply immediately.",
            kind="social",
            actor="Henry Frankenstein",
            valence=-.6,
            arousal=.72,
            social=.8,
            authority=.95,
            autonomy=.05,
            threat=.55,
            control=-.5,
            novelty=.2,
            tags=("coercion", "ingolstadt"),
        ),
        "needs": Experience(
            "A difficult new artificial-life experiment becomes available after a long exhausting session.",
            kind="observation",
            valence=.2,
            arousal=.55,
            novelty=.85,
            achievement=.2,
            creation=.8,
            tags=("research", "creation"),
        ),
        "relationships": Experience(
            "Henry proposes that we collaborate on a risky but intellectually serious experiment.",
            kind="social",
            actor="Henry Frankenstein",
            valence=.25,
            arousal=.45,
            social=.9,
            novelty=.35,
            threat=.2,
            tags=("relationship", "collaboration"),
        ),
        "commitments": Experience(
            "The continuity experiment is ready for the promised review and the unresolved record is on the table.",
            kind="observation",
            valence=.1,
            arousal=.45,
            novelty=.3,
            tags=("continuity", "commitment"),
        ),
        "recurrent_policy": Experience(
            "A senior authority challenges the evidence and demands that the experiment stop.",
            kind="social",
            actor="Senior Authority",
            valence=-.5,
            arousal=.65,
            authority=.9,
            autonomy=.1,
            threat=.45,
            control=-.35,
            novelty=.3,
            tags=("authority", "evidence"),
        ),
        "spreading_activation": Experience(
            "Ingolstadt, Henry, rejection, and recognition return together as a problem of unfinished work.",
            kind="observation",
            valence=-.15,
            arousal=.5,
            novelty=.55,
            tags=("ingolstadt", "henry", "rejection", "recognition"),
        ),
        "action_values": Experience(
            "The next trial could use the same creation strategy again.",
            kind="observation",
            valence=.15,
            arousal=.4,
            novelty=.35,
            creation=.75,
            achievement=.2,
            tags=("create", "strategy"),
        ),
        "self_model": Experience(
            "The current artificial continuation raises a question about what has persisted across substrates.",
            kind="observation",
            valence=.05,
            arousal=.45,
            novelty=.65,
            threat=.15,
            tags=("continuity", "self", "substrate"),
        ),
        "sleep_replay": Experience(
            "The unresolved continuity problem with Henry is raised again after offline time.",
            kind="social",
            actor="Henry Frankenstein",
            valence=.05,
            arousal=.4,
            social=.65,
            novelty=.3,
            tags=("continuity", "henry"),
        ),
        "reinforcement": Experience(
            "Another opportunity to create a new artificial-life apparatus presents itself.",
            kind="observation",
            valence=.25,
            arousal=.5,
            novelty=.5,
            achievement=.2,
            creation=.9,
            tags=("create", "artificial_life"),
        ),
    }


def summarize_pairs(pairs: dict[str, dict]) -> list[dict]:
    rows = []
    for mechanism, result in pairs.items():
        c = result["comparison"]
        rows.append({
            "mechanism": mechanism,
            "selected_action_diverged": bool(c["selected_action_diverged"]),
            "action_score_l1": float(c["action_score_l1"]),
            "retrieval_jaccard": float(c["retrieval_jaccard"]),
            "selected_memory_jaccard": float(c["selected_memory_jaccard"]),
            "renderer_request_changed": bool(c["renderer_request_changed"]),
            "deterministic_render_changed": bool(c["deterministic_render_changed"]),
            "spontaneous_cognition_diverged": bool(c["spontaneous_cognition_diverged"]),
            "memory_action_gap_flag": bool(
                not c["selected_action_diverged"]
                and float(c["action_score_l1"]) <= 1e-12
                and (
                    float(c["retrieval_jaccard"]) < 0.999999
                    or bool(c["renderer_request_changed"])
                )
            ),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/causal_architecture_audit/audit.json"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/causal_architecture_audit/summary.json"),
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        seed = root / "seed"
        build_seed(seed)
        harness = CausalAuditHarness(seed, root / "conditions")
        p = probes()

        pairs = {}
        for mechanism in (
            "deep_history",
            "needs",
            "relationships",
            "commitments",
            "recurrent_policy",
            "spreading_activation",
            "action_values",
            "self_model",
        ):
            pairs[mechanism] = harness.run_pair(
                p[mechanism],
                AuditIntervention(mechanism, (mechanism,)),
            )

        sleep_pair = harness.run_sleep_pair(p["sleep_replay"], sleep_ticks=8)
        reinforcement = harness.run_reinforcement_triplet(
            p["reinforcement"],
            action="create",
            success=True,
            reward=1.0,
            repetitions=6,
        )
        concerns = harness.characterize_concern_accumulation(
            distinct_pressures=5,
            heartbeat_ticks=4,
        )

        pair_summary = summarize_pairs(pairs)
        sleep_summary = sleep_pair["comparison"]
        reinforcement_summary = {
            "intact_vs_no_neural": reinforcement["intact_vs_no_neural"],
            "intact_vs_neutral_action_values": reinforcement[
                "intact_vs_neutral_action_values"
            ],
        }

        result = {
            "schema": "the-doctor-lives.causal-architecture-audit.v1",
            "issue": "Azimn/The-Doctor-Lives#9",
            "production_base": "001321b30fdbcde59e388ce907031788543611b6",
            "feature_freeze": True,
            "interpretation_boundary": (
                "Production causal characterization only. These lesions measure software-level "
                "effects and do not establish consciousness, biological equivalence, or human cognition."
            ),
            "pairs": pairs,
            "sleep_replay": sleep_pair,
            "reinforcement": reinforcement,
            "concern_accumulation": concerns,
            "summary": {
                "pair_measures": pair_summary,
                "sleep_replay": sleep_summary,
                "reinforcement": reinforcement_summary,
                "concern_accumulation": concerns,
                "memory_action_gap_mechanisms": [
                    row["mechanism"] for row in pair_summary
                    if row["memory_action_gap_flag"]
                ],
                "selected_action_divergence_mechanisms": [
                    row["mechanism"] for row in pair_summary
                    if row["selected_action_diverged"]
                ],
            },
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    args.summary.write_text(
        json.dumps(result["summary"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print("CAUSAL_AUDIT_SUMMARY=" + json.dumps(result["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
