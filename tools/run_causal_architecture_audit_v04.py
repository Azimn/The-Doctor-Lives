from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.causal_audit import AuditIntervention, CausalAuditHarness


PRODUCTION_BASE = "02068362af6a969a3788a9fcbcd0b667644d25fd"
ISSUE = "Azimn/The-Doctor-Lives#10"


def build_seed(state_dir: Path) -> None:
    brain = PretoriusBrain(state_dir)
    brain.ingest(Experience(
        "Henry returned a borrowed instrument intact and kept his promise.",
        kind="social",
        actor="Henry Frankenstein",
        social=.85,
        valence=.7,
        achievement=.25,
        tags=("causal_audit_v04_seed",),
    ))
    brain.add_commitment(
        "Revisit the continuity experiment with Henry and record what changed.",
        actor="Henry Frankenstein",
        due_tick=24,
        importance=.82,
    )
    with brain.store.transaction() as conn:
        conn.execute("UPDATE needs SET actual=.86,felt=.82 WHERE key='fatigue'")
        conn.execute("UPDATE needs SET actual=.78,felt=.72 WHERE key='continuity'")
        conn.execute("UPDATE needs SET actual=.88,felt=.84 WHERE key='autonomy'")
        brain.store.bump_state_version(conn)
    brain.save()


def probes() -> dict[str, Experience]:
    return {
        "deep_history": Experience(
            "Henry orders me to abandon the Ingolstadt work and comply immediately.",
            kind="social", actor="Henry Frankenstein", valence=-.6, arousal=.72,
            social=.8, authority=.95, autonomy=.05, threat=.55, control=-.5,
            novelty=.2, tags=("coercion", "ingolstadt"),
        ),
        "needs": Experience(
            "A difficult new artificial-life experiment becomes available after a long exhausting session.",
            kind="observation", valence=.2, arousal=.55, novelty=.85,
            achievement=.2, creation=.8, tags=("research", "creation"),
        ),
        "relationships": Experience(
            "Henry proposes that we collaborate on a risky but intellectually serious experiment.",
            kind="social", actor="Henry Frankenstein", valence=.25, arousal=.45,
            social=.9, novelty=.35, threat=.2, tags=("relationship", "collaboration"),
        ),
        "commitments": Experience(
            "The continuity experiment with Henry is ready for the promised review.",
            kind="social", actor="Henry Frankenstein", valence=.1, arousal=.45,
            novelty=.3, tags=("continuity", "commitment"),
        ),
        "recurrent_policy": Experience(
            "A senior authority challenges the evidence and demands that the experiment stop.",
            kind="social", actor="Senior Authority", valence=-.5, arousal=.65,
            authority=.9, autonomy=.1, threat=.45, control=-.35,
            novelty=.3, tags=("authority", "evidence"),
        ),
        "state_policy_bridge": Experience(
            "Henry invokes authority and orders immediate compliance on the continuity procedure.",
            kind="social", actor="Henry Frankenstein", valence=-.55, arousal=.65,
            social=.75, authority=.95, autonomy=.05, threat=.5, control=-.45,
            tags=("coercion", "continuity", "henry"),
        ),
        "sleep_replay": Experience(
            "The unresolved continuity problem with Henry is raised again after offline time.",
            kind="social", actor="Henry Frankenstein", valence=.05, arousal=.4,
            social=.65, novelty=.3, tags=("continuity", "henry"),
        ),
        "reinforcement": Experience(
            "Another opportunity to create a new artificial-life apparatus presents itself.",
            kind="observation", valence=.25, arousal=.5, novelty=.5,
            achievement=.2, creation=.9, tags=("create", "artificial_life"),
        ),
    }


def pair_row(mechanism: str, result: dict) -> dict:
    c = result["comparison"]
    intact_policy = result["intact"]["policy_decision"]
    lesion_policy = result["lesion"]["policy_decision"]
    return {
        "mechanism": mechanism,
        "action_score_l1": float(c["action_score_l1"]),
        "selected_action_diverged": bool(c["selected_action_diverged"]),
        "renderer_request_changed": bool(c["renderer_request_changed"]),
        "retrieval_jaccard": float(c["retrieval_jaccard"]),
        "intact_selected_action": intact_policy["selected_action"],
        "lesion_selected_action": lesion_policy["selected_action"],
        "intact_raw_recurrent_scores": intact_policy.get("base_action_scores", {}),
        "intact_state_pressure": intact_policy.get("state_pressure", {}),
        "intact_final_scores": intact_policy["action_scores"],
        "lesion_raw_recurrent_scores": lesion_policy.get("base_action_scores", {}),
        "lesion_state_pressure": lesion_policy.get("state_pressure", {}),
        "lesion_final_scores": lesion_policy["action_scores"],
    }


def concern_resolution_characterization() -> dict:
    with tempfile.TemporaryDirectory() as td:
        brain = PretoriusBrain(Path(td))
        event = Experience(
            "A containment failure threatens the laboratory.",
            kind="observation", threat=.9, control=-.6, arousal=.75,
            tags=("containment", "threat"),
        )
        brain.ingest(event)
        open_rows = brain.store.open_concerns()
        concern_id = open_rows[0]["id"]
        _, _, before = brain._state_policy_scores(
            [], decision_text="The containment failure threatens the laboratory."
        )
        brain.resolve_concern(concern_id, "Containment restored and independently verified.")
        _, _, after = brain._state_policy_scores(
            [], decision_text="The containment failure threatens the laboratory."
        )
        heartbeat = brain.heartbeat(2)
        with brain.store.connect() as conn:
            events = [dict(row) for row in conn.execute(
                "SELECT transition,outcome,actor,source FROM concern_events WHERE concern_id=? ORDER BY rowid",
                (concern_id,),
            ).fetchall()]
        return {
            "concern_id": concern_id,
            "open_before_resolution": True,
            "open_after_resolution": bool(brain.store.open_concerns()),
            "pressure_before": before["families"]["concerns"],
            "pressure_after": after["families"]["concerns"],
            "heartbeat_thoughts_after_resolution": len(heartbeat["thoughts"]),
            "lifecycle_events": events,
        }


def load_v03_summary() -> dict:
    path = Path("results/causal_architecture_audit/summary.json")
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/causal_architecture_audit_v04/audit.json"))
    parser.add_argument("--summary", type=Path, default=Path("results/causal_architecture_audit_v04/summary.json"))
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
            "state_policy_bridge",
        ):
            pairs[mechanism] = harness.run_pair(
                p[mechanism], AuditIntervention(mechanism, (mechanism,))
            )

        sleep_pair = harness.run_sleep_pair(p["sleep_replay"], sleep_ticks=8)
        reinforcement = harness.run_reinforcement_triplet(
            p["reinforcement"], action="create", success=True, reward=1.0, repetitions=6
        )
        concern_resolution = concern_resolution_characterization()

        rows = [pair_row(name, result) for name, result in pairs.items()]
        v03 = load_v03_summary()
        v03_rows = {
            row["mechanism"]: row
            for row in v03.get("pair_measures", [])
            if isinstance(row, dict) and "mechanism" in row
        }
        comparison = []
        for row in rows:
            prior = v03_rows.get(row["mechanism"])
            comparison.append({
                "mechanism": row["mechanism"],
                "v03_action_score_l1": None if prior is None else prior.get("action_score_l1"),
                "v04_action_score_l1": row["action_score_l1"],
                "v03_selected_action_diverged": None if prior is None else prior.get("selected_action_diverged"),
                "v04_selected_action_diverged": row["selected_action_diverged"],
                "v04_renderer_request_changed": row["renderer_request_changed"],
            })

        result = {
            "schema": "the-doctor-lives.causal-architecture-audit.v04",
            "issue": ISSUE,
            "production_base": PRODUCTION_BASE,
            "audit_code_sha": os.environ.get("GITHUB_SHA", "local-unpinned"),
            "interpretation_boundary": (
                "Production software causal characterization only. These lesions measure "
                "software-level effects and do not establish consciousness, biological "
                "equivalence, or general human cognition."
            ),
            "pairs": pairs,
            "sleep_replay": sleep_pair,
            "reinforcement": reinforcement,
            "concern_resolution": concern_resolution,
            "summary": {
                "pair_measures": rows,
                "v03_vs_v04": comparison,
                "sleep_replay": sleep_pair["comparison"],
                "reinforcement": {
                    "intact_vs_no_neural": reinforcement["intact_vs_no_neural"],
                    "intact_vs_neutral_action_values": reinforcement["intact_vs_neutral_action_values"],
                },
                "concern_resolution": concern_resolution,
            },
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    args.summary.write_text(json.dumps(result["summary"], indent=2, sort_keys=True), encoding="utf-8")
    print("CAUSAL_AUDIT_V04_SUMMARY=" + json.dumps(result["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
