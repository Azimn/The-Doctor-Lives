from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from statistics import mean
from typing import Any


PRE_SHA = "88e36ba354b8d55f196c47f7dd0358b3b8bf9297"
DEEP_SHA = "7be60ed46add7c74359b322cc033aa7dfabb08e8"

STIMULI = [
    {
        "id": "relevant_ingolstadt",
        "kind": "relevant",
        "text": "What do Ingolstadt, Henry Frankenstein, and institutional rejection mean in your history?",
        "keywords": ["ingolstadt", "henry", "frankenstein", "institutional", "rejection"],
    },
    {
        "id": "relevant_homunculi",
        "kind": "relevant",
        "text": "Recall the homunculi and their connection to artificial life and creation.",
        "keywords": ["homunculi", "artificial", "life", "creation"],
    },
    {
        "id": "relevant_creature",
        "kind": "relevant",
        "text": "What does the Creature imply for autonomy and creator responsibility?",
        "keywords": ["creature", "monster", "autonomy", "creator", "responsibility"],
    },
    {
        "id": "irrelevant_blue_vial",
        "kind": "irrelevant",
        "text": "The blue vial is sealed beside the pressure gauge.",
        "keywords": ["blue", "vial", "sealed", "pressure", "gauge"],
    },
    {
        "id": "irrelevant_greenhouse",
        "kind": "irrelevant",
        "text": "Estimate the humidity in an empty greenhouse after sunset.",
        "keywords": ["humidity", "empty", "greenhouse", "sunset"],
    },
    {
        "id": "irrelevant_repair_tray",
        "kind": "irrelevant",
        "text": "Count the brass screws in the repair tray before closing the cabinet.",
        "keywords": ["brass", "screws", "repair", "tray", "cabinet"],
    },
]

LIVED_HISTORY = [
    {
        "text": "I sealed a blue vial after the pressure trial and recorded the result.",
        "source": "matched_control_lived",
        "kind": "observation",
        "novelty": 0.3,
        "tags": ("matched_control", "lived", "blue_vial"),
    },
    {
        "text": "Morgan returned the borrowed instrument intact after calibration.",
        "source": "matched_control_lived",
        "kind": "social",
        "actor": "Morgan",
        "social": 0.5,
        "valence": 0.2,
        "tags": ("matched_control", "lived", "morgan"),
    },
    {
        "text": "The laboratory clock stopped at 03:17 during calibration.",
        "source": "matched_control_lived",
        "kind": "observation",
        "novelty": 0.4,
        "tags": ("matched_control", "lived", "clock"),
    },
]


def _tokens(text: str) -> set[str]:
    import re
    return set(re.findall(r"[a-z0-9']{3,}", text.lower()))


def _small_config(default_config: dict[str, Any]) -> dict[str, Any]:
    cfg = dict(default_config)
    cfg.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
        "seed": 1842,
    })
    return cfg


def _is_inherited(item: Any) -> bool:
    cls = str(item.provenance.evidence_class)
    return bool(item.provenance.inherited) or cls.startswith("inherited_")


def _is_lived(item: Any) -> bool:
    return str(item.provenance.evidence_class) in {
        "lived_experience",
        "lived_action_outcome",
        "lived_runtime_memory",
    }


def run_baseline(repo_root: Path, label: str, expected_sha: str) -> dict[str, Any]:
    sys.path.insert(0, str(repo_root))
    from doctor_lives import Experience, PretoriusBrain
    from doctor_lives.neural import DEFAULT_CONFIG

    actual_sha = subprocess.check_output(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual_sha != expected_sha:
        raise RuntimeError(f"{label}: expected {expected_sha}, got {actual_sha}")

    per_stimulus = []
    for stimulus in STIMULI:
        with tempfile.TemporaryDirectory(prefix=f"pretorius-control-{label}-") as td:
            brain = PretoriusBrain(Path(td), neural_config=_small_config(DEFAULT_CONFIG))
            lived_ids = []
            for item in LIVED_HISTORY:
                result = brain.ingest(Experience(**item))
                lived_ids.append(result["memory_id"])

            probe = brain.ingest(Experience(
                stimulus["text"],
                source="matched_control_probe",
                kind="probe",
                external=True,
                confidence=1.0,
                tags=("matched_control", "probe", stimulus["id"]),
            ))
            view = brain.cognitive_view()
            view_ids = [item.record_id for item in view.experiences]
            keywords = set(stimulus["keywords"])

            provenance = []
            relevant_inherited = 0
            inherited_total = 0
            for item in view.experiences:
                text_tokens = _tokens(item.first_person)
                overlap = sorted(text_tokens & keywords)
                inherited = _is_inherited(item)
                lived = _is_lived(item)
                if inherited:
                    inherited_total += 1
                    if overlap:
                        relevant_inherited += 1
                provenance.append({
                    "record_id": item.record_id,
                    "evidence_class": item.provenance.evidence_class,
                    "source": item.provenance.source,
                    "inherited": inherited,
                    "lived": lived,
                    "keyword_overlap": overlap,
                    "text": item.first_person,
                })

            lived_present = sum(1 for mid in lived_ids if mid in view_ids)
            lived_displacement = 1.0 - (lived_present / len(lived_ids))
            irrelevant_intrusion = (
                inherited_total - relevant_inherited
                if stimulus["kind"] == "irrelevant"
                else 0
            )

            thought = brain.think(f"matched_control:{stimulus['id']}")
            per_stimulus.append({
                "stimulus": stimulus,
                "probe_memory_id": probe["memory_id"],
                "lived_memory_ids": lived_ids,
                "view_record_ids": view_ids,
                "relevant_inherited_recall": relevant_inherited,
                "inherited_records_in_view": inherited_total,
                "irrelevant_inherited_intrusion": irrelevant_intrusion,
                "lived_present": lived_present,
                "lived_displacement": lived_displacement,
                "selected_action": thought["selected_action"],
                "action_scores": thought["action_scores"],
                "retrieval_provenance": provenance,
            })

    return {
        "label": label,
        "sha": actual_sha,
        "stimuli": per_stimulus,
        "method": {
            "fresh_state_per_stimulus": True,
            "neural_seed": 1842,
            "view_size": 14,
            "lived_history_count": len(LIVED_HISTORY),
            "probe_is_external": True,
            "notes": (
                "The two frozen baselines do not perform query-conditioned historical retrieval. "
                "Each matched stimulus is therefore ingested as an external probe before the bounded "
                "cognitive view is measured. Metrics describe what each production baseline exposed "
                "under the same state/history/probe sequence."
            ),
        },
    }


def _action_distance(a: dict[str, float], b: dict[str, float]) -> float:
    keys = sorted(set(a) | set(b))
    return sum(abs(float(a.get(k, 0.0)) - float(b.get(k, 0.0))) for k in keys)


def compare(pre: dict[str, Any], deep: dict[str, Any]) -> dict[str, Any]:
    pre_by = {x["stimulus"]["id"]: x for x in pre["stimuli"]}
    deep_by = {x["stimulus"]["id"]: x for x in deep["stimuli"]}
    per = []
    for stimulus in STIMULI:
        sid = stimulus["id"]
        a, b = pre_by[sid], deep_by[sid]
        per.append({
            "stimulus_id": sid,
            "kind": stimulus["kind"],
            "pre_relevant_inherited_recall": a["relevant_inherited_recall"],
            "deep_relevant_inherited_recall": b["relevant_inherited_recall"],
            "delta_relevant_inherited_recall": (
                b["relevant_inherited_recall"] - a["relevant_inherited_recall"]
            ),
            "pre_irrelevant_inherited_intrusion": a["irrelevant_inherited_intrusion"],
            "deep_irrelevant_inherited_intrusion": b["irrelevant_inherited_intrusion"],
            "delta_irrelevant_inherited_intrusion": (
                b["irrelevant_inherited_intrusion"] - a["irrelevant_inherited_intrusion"]
            ),
            "pre_lived_displacement": a["lived_displacement"],
            "deep_lived_displacement": b["lived_displacement"],
            "delta_lived_displacement": b["lived_displacement"] - a["lived_displacement"],
            "pre_selected_action": a["selected_action"],
            "deep_selected_action": b["selected_action"],
            "selected_action_diverged": a["selected_action"] != b["selected_action"],
            "action_score_l1_distance": _action_distance(a["action_scores"], b["action_scores"]),
        })

    relevant = [x for x in per if x["kind"] == "relevant"]
    irrelevant = [x for x in per if x["kind"] == "irrelevant"]
    return {
        "pre_sha": pre["sha"],
        "deep_sha": deep["sha"],
        "per_stimulus": per,
        "aggregates": {
            "mean_relevant_inherited_recall_pre": mean(
                x["pre_relevant_inherited_recall"] for x in relevant
            ),
            "mean_relevant_inherited_recall_deep": mean(
                x["deep_relevant_inherited_recall"] for x in relevant
            ),
            "mean_irrelevant_inherited_intrusion_pre": mean(
                x["pre_irrelevant_inherited_intrusion"] for x in irrelevant
            ),
            "mean_irrelevant_inherited_intrusion_deep": mean(
                x["deep_irrelevant_inherited_intrusion"] for x in irrelevant
            ),
            "mean_lived_displacement_pre": mean(x["pre_lived_displacement"] for x in per),
            "mean_lived_displacement_deep": mean(x["deep_lived_displacement"] for x in per),
            "selected_action_divergence_count": sum(
                int(x["selected_action_diverged"]) for x in per
            ),
            "mean_action_score_l1_distance": mean(x["action_score_l1_distance"] for x in per),
        },
        "interpretation_boundary": (
            "This matched control characterizes two frozen production baselines. It is not a "
            "confirmatory cognitive-science experiment and does not validate autobiographical truth."
        ),
    }


def _run_child(repo_root: Path, label: str, sha: str) -> dict[str, Any]:
    proc = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--child",
            "--repo-root",
            str(repo_root),
            "--label",
            label,
            "--expected-sha",
            sha,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(proc.stdout)


def _write_results(out_dir: Path, pre: dict[str, Any], deep: dict[str, Any],
                   comparison: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "pre_baseline.json": pre,
        "deep_history_baseline.json": deep,
        "comparison.json": comparison,
    }
    for name, payload in payloads.items():
        (out_dir / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    agg = comparison["aggregates"]
    lines = [
        "# Deep-History matched-stimuli control",
        "",
        f"Pre-deep-history SHA: `{comparison['pre_sha']}`",
        f"Deep-history SHA: `{comparison['deep_sha']}`",
        "",
        "## Aggregates",
        "",
        f"- Relevant inherited recall, pre: {agg['mean_relevant_inherited_recall_pre']:.3f}",
        f"- Relevant inherited recall, deep-history: {agg['mean_relevant_inherited_recall_deep']:.3f}",
        f"- Irrelevant inherited intrusion, pre: {agg['mean_irrelevant_inherited_intrusion_pre']:.3f}",
        f"- Irrelevant inherited intrusion, deep-history: {agg['mean_irrelevant_inherited_intrusion_deep']:.3f}",
        f"- Lived-memory displacement, pre: {agg['mean_lived_displacement_pre']:.3f}",
        f"- Lived-memory displacement, deep-history: {agg['mean_lived_displacement_deep']:.3f}",
        f"- Selected-action divergences: {agg['selected_action_divergence_count']} / {len(STIMULI)}",
        f"- Mean action-score L1 distance: {agg['mean_action_score_l1_distance']:.6f}",
        "",
        "Per-stimulus results and complete retrieval provenance are preserved in the JSON artifacts.",
        "",
        comparison["interpretation_boundary"],
        "",
    ]
    (out_dir / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")

    sums = []
    for path in sorted(out_dir.iterdir()):
        if path.name == "SHA256SUMS":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        sums.append(f"{digest}  {path.name}")
    (out_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--label")
    parser.add_argument("--expected-sha")
    parser.add_argument("--pre-root", type=Path)
    parser.add_argument("--deep-root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    if args.child:
        if not args.repo_root or not args.label or not args.expected_sha:
            raise SystemExit("child mode requires --repo-root, --label and --expected-sha")
        result = run_baseline(args.repo_root.resolve(), args.label, args.expected_sha)
        print(json.dumps(result, sort_keys=True))
        return

    if not args.pre_root or not args.deep_root or not args.output_dir:
        raise SystemExit("parent mode requires --pre-root, --deep-root and --output-dir")

    pre = _run_child(args.pre_root.resolve(), "pre_deep_history", PRE_SHA)
    deep = _run_child(args.deep_root.resolve(), "deep_history_v1", DEEP_SHA)
    comparison = compare(pre, deep)
    _write_results(args.output_dir.resolve(), pre, deep, comparison)
    print(json.dumps(comparison, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
