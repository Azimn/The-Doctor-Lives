from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any, Iterable

import numpy as np

from .neural import PretoriusRecurrentSubstrate
from .neural_characterization import (
    DECISIVE_SEEDS,
    DEVELOPMENT_BLOCK_LENGTH,
    PROTOCOL_VERSION,
    Stimulus,
    _evaluate_clone,
    _run_rows,
    developmental_exposure,
    evaluation_probes,
    jensen_shannon_divergence,
    representational_summary,
    sha256_json,
)

LESION_PROTOCOL_VERSION = "neural-convergence-causal-lesions-b06-v1"
CAUSAL_CORE_FRACTION = 0.05
LESION_EVALUATION_STEPS = 512
RELEARNING_STEPS = 3584
RELEARNING_BLOCKS = 7


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_sha() -> str:
    value = os.environ.get("GITHUB_SHA")
    if value:
        return value
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip() or "local-unpinned"
    except Exception:
        return "local-unpinned"


def _runtime_metadata() -> dict[str, Any]:
    versions: dict[str, str | None] = {}
    try:
        from importlib.metadata import version
        versions["numpy"] = version("numpy")
        versions["scipy"] = version("scipy")
    except Exception:
        versions["numpy"] = getattr(np, "__version__", None)
        versions["scipy"] = None
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
        "platform": platform.platform(),
        **versions,
    }


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _array_sha256(values: np.ndarray) -> str:
    array = np.ascontiguousarray(values)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(str(tuple(array.shape)).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _mean_expected_probability(records: Iterable[dict[str, Any]]) -> float:
    values: list[float] = []
    for record in records:
        expected = record.get("expected_action")
        if expected is not None:
            values.append(float(record["scores"][expected]))
    if not values:
        raise ValueError("no expected-action records available")
    return float(np.mean(values))


def _mean_pairwise_js(
    left: Iterable[dict[str, Any]],
    right: Iterable[dict[str, Any]],
) -> float:
    values = [
        jensen_shannon_divergence(a["scores"], b["scores"])
        for a, b in zip(left, right)
    ]
    if not values:
        raise ValueError("no paired records available")
    return float(np.mean(values))


def verify_recurrent_topology(
    stabilized: PretoriusRecurrentSubstrate,
    developed: PretoriusRecurrentSubstrate,
) -> None:
    if stabilized.n != developed.n:
        raise ValueError("checkpoint neuron counts differ")
    if not np.array_equal(stabilized.W.indptr, developed.W.indptr):
        raise ValueError("checkpoint recurrent CSR indptr differs")
    if not np.array_equal(stabilized.W.indices, developed.W.indices):
        raise ValueError("checkpoint recurrent CSR indices differ")
    if not np.array_equal(stabilized.excitatory, developed.excitatory):
        raise ValueError("checkpoint E/I assignment differs")
    if stabilized.W.data.shape != developed.W.data.shape:
        raise ValueError("checkpoint recurrent data shapes differ")


def learned_recurrent_delta(
    stabilized: PretoriusRecurrentSubstrate,
    developed: PretoriusRecurrentSubstrate,
) -> np.ndarray:
    verify_recurrent_topology(stabilized, developed)
    return (
        np.asarray(developed.W.data, dtype=np.float32)
        - np.asarray(stabilized.W.data, dtype=np.float32)
    ).astype(np.float32, copy=False)


def rank_causal_core(
    delta: np.ndarray,
    fraction: float = CAUSAL_CORE_FRACTION,
) -> np.ndarray:
    values = np.asarray(delta, dtype=np.float64)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("learned recurrent delta must be a non-empty vector")
    if not 0.0 < float(fraction) <= 1.0:
        raise ValueError("causal-core fraction must be in (0, 1]")
    count = max(1, int(np.ceil(values.size * float(fraction))))
    edge_index = np.arange(values.size, dtype=np.int64)
    order = np.lexsort((edge_index, -np.abs(values)))
    return np.sort(order[:count].astype(np.int64, copy=False))


def matched_random_core(
    developed: PretoriusRecurrentSubstrate,
    targeted_indices: np.ndarray,
    seed: int,
) -> np.ndarray:
    targeted = np.asarray(targeted_indices, dtype=np.int64)
    if targeted.ndim != 1 or targeted.size == 0:
        raise ValueError("targeted indices must be a non-empty vector")
    if len(np.unique(targeted)) != targeted.size:
        raise ValueError("targeted indices must be unique")
    if int(targeted.min()) < 0 or int(targeted.max()) >= developed.W.data.size:
        raise ValueError("targeted index outside recurrent edge range")

    edge_is_exc = developed.excitatory[developed.pre_idx]
    targeted_mask = np.zeros(developed.W.data.size, dtype=bool)
    targeted_mask[targeted] = True
    rng = np.random.default_rng(int(seed) * 16127 + 606)
    chosen: list[np.ndarray] = []

    for is_exc in (True, False):
        count = int(np.count_nonzero(edge_is_exc[targeted] == is_exc))
        if count == 0:
            continue
        candidates = np.flatnonzero((edge_is_exc == is_exc) & ~targeted_mask)
        if candidates.size < count:
            raise ValueError("insufficient edges for E/I-matched random lesion")
        chosen.append(
            np.asarray(rng.choice(candidates, size=count, replace=False), dtype=np.int64)
        )

    result = np.sort(np.concatenate(chosen))
    if result.size != targeted.size:
        raise RuntimeError("matched random lesion size differs from targeted lesion")
    if np.intersect1d(result, targeted).size:
        raise RuntimeError("matched random lesion overlaps targeted lesion")
    return result


def revert_learned_edges(
    net: PretoriusRecurrentSubstrate,
    stabilized: PretoriusRecurrentSubstrate,
    indices: np.ndarray | None = None,
) -> None:
    verify_recurrent_topology(stabilized, net)
    if indices is None:
        net.W.data[:] = stabilized.W.data
    else:
        selected = np.asarray(indices, dtype=np.int64)
        net.W.data[selected] = stabilized.W.data[selected]


def transplant_full_delta(
    baseline: PretoriusRecurrentSubstrate,
    stabilized: PretoriusRecurrentSubstrate,
    developed: PretoriusRecurrentSubstrate,
) -> None:
    verify_recurrent_topology(stabilized, developed)
    verify_recurrent_topology(stabilized, baseline)
    baseline.W.data[:] = stabilized.W.data + learned_recurrent_delta(
        stabilized, developed
    )


def _condition_summary(
    name: str,
    net: PretoriusRecurrentSubstrate,
    probes: tuple[Stimulus, ...],
    intact_records: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], np.ndarray]:
    records, states = _run_rows(
        net,
        probes,
        learn=False,
        apply_outcomes=False,
        capture_states=True,
    )
    assert states is not None
    summary = {
        "name": name,
        "mean_expected_action_probability": _mean_expected_probability(records),
        "recurrent_gain_estimate": float(net._estimate_recurrent_gain()),
        "representational_summary": representational_summary(states, probes),
        "network_after_evaluation": {
            "tick": int(net.tick),
            "state_gain": float(net.state_gain),
            "recurrent_gain_recorded": (
                None
                if net.last_recurrent_gain is None
                else float(net.last_recurrent_gain)
            ),
        },
    }
    if intact_records is not None:
        summary["mean_js_from_intact"] = _mean_pairwise_js(records, intact_records)
    return summary, records, states


def _delta_similarity(current: np.ndarray, reference: np.ndarray) -> dict[str, float]:
    current64 = np.asarray(current, dtype=np.float64)
    reference64 = np.asarray(reference, dtype=np.float64)
    reference_norm = float(np.linalg.norm(reference64))
    current_norm = float(np.linalg.norm(current64))
    cosine = 0.0
    if reference_norm > 1e-15 and current_norm > 1e-15:
        cosine = float(
            np.dot(current64, reference64) / (current_norm * reference_norm)
        )
    return {
        "reference_norm": reference_norm,
        "current_norm": current_norm,
        "norm_ratio": (
            float(current_norm / reference_norm) if reference_norm > 1e-15 else 0.0
        ),
        "cosine_to_original_delta": cosine,
    }


def _validate_source_artifacts(
    control_dir: Path,
    challenger_dir: Path,
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    control = _load_json(control_dir / "result.json")
    challenger = _load_json(challenger_dir / "result.json")
    if int(seed) not in DECISIVE_SEEDS:
        raise ValueError(f"seed {seed} is not preregistered for B06")

    checks = (
        (control.get("profile") == "legacy_v04", "B04 profile mismatch"),
        (
            challenger.get("profile") == "neural_convergence_v05",
            "B05 profile mismatch",
        ),
        (int(control.get("seed", -1)) == int(seed), "B04 seed mismatch"),
        (int(challenger.get("seed", -1)) == int(seed), "B05 seed mismatch"),
        (control.get("status") == "complete", "B04 result incomplete"),
        (challenger.get("status") == "complete", "B05 result incomplete"),
        (
            control.get("protocol_version") == PROTOCOL_VERSION
            and challenger.get("protocol_version") == PROTOCOL_VERSION,
            "source protocol version mismatch",
        ),
        (
            control.get("curriculum_sha256")
            == challenger.get("curriculum_sha256"),
            "B04/B05 curriculum hash mismatch",
        ),
        (
            control.get("outcome_schedule_sha256")
            == challenger.get("outcome_schedule_sha256"),
            "B04/B05 outcome schedule hash mismatch",
        ),
        (
            int(control["configuration"]["neurons"]) == 4096
            and int(challenger["configuration"]["neurons"]) == 4096,
            "source artifact is not 4,096 units",
        ),
        (control.get("restart_exact_match") is True, "B04 restart check failed"),
        (
            challenger.get("restart_exact_match") is True,
            "B05 restart check failed",
        ),
    )
    for ok, message in checks:
        if not ok:
            raise ValueError(message)
    return control, challenger


def run_causal_lesions(
    seed: int,
    control_dir: str | Path,
    challenger_dir: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    control_dir = Path(control_dir)
    challenger_dir = Path(challenger_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    control, challenger = _validate_source_artifacts(
        control_dir, challenger_dir, seed
    )
    started_at = _utc_now()
    started = time.perf_counter()

    stabilized_path = challenger_dir / "phase1_stabilized.npz"
    developed_path = challenger_dir / "phase2_developed.npz"
    if not stabilized_path.is_file() or not developed_path.is_file():
        raise FileNotFoundError("B05 stabilized/developed checkpoints are required")
    if (
        _file_sha256(stabilized_path)
        != challenger["checkpoint_files"]["stabilized"]["sha256"]
    ):
        raise ValueError("B05 stabilized checkpoint hash mismatch")
    if (
        _file_sha256(developed_path)
        != challenger["checkpoint_files"]["developed"]["sha256"]
    ):
        raise ValueError("B05 developed checkpoint hash mismatch")

    stabilized = PretoriusRecurrentSubstrate.load(stabilized_path)
    developed = PretoriusRecurrentSubstrate.load(developed_path)
    verify_recurrent_topology(stabilized, developed)
    expected_neurons = int(challenger["configuration"]["neurons"])
    if stabilized.n != expected_neurons or developed.n != expected_neurons:
        raise ValueError("B05 checkpoint neuron count mismatch")
    if sha256_json(stabilized.cfg) != challenger["configuration_sha256"]:
        raise ValueError("B05 stabilized checkpoint config mismatch")
    if sha256_json(developed.cfg) != challenger["configuration_sha256"]:
        raise ValueError("B05 developed checkpoint config mismatch")

    delta = learned_recurrent_delta(stabilized, developed)
    targeted = rank_causal_core(delta)
    random_matched = matched_random_core(developed, targeted, seed)
    mask_path = out / "lesion_masks.npz"
    np.savez_compressed(
        mask_path,
        learned_delta=delta.astype(np.float32, copy=False),
        targeted_indices=targeted,
        random_matched_indices=random_matched,
    )

    probes = evaluation_probes(seed)
    development = developmental_exposure(seed)

    intact_net = PretoriusRecurrentSubstrate.load(developed_path)
    intact_summary, intact_records, intact_states = _condition_summary(
        "intact_developed_sham", intact_net, probes
    )
    preserved_restart_records = challenger["restart_probe_records"]
    if len(intact_records) != len(preserved_restart_records):
        raise RuntimeError("B06 intact sham record count differs from preserved B05 restart")
    intact_score_max_abs_diff = max(
        abs(float(current["scores"][action]) - float(preserved["scores"][action]))
        for current, preserved in zip(intact_records, preserved_restart_records)
        for action in current["scores"]
    )
    intact_score_match = intact_score_max_abs_diff <= 1e-12

    state_artifact_path = challenger_dir / challenger["state_artifact"]["path"]
    if not state_artifact_path.is_file():
        raise FileNotFoundError("B05 evaluation-state artifact is required")
    if _file_sha256(state_artifact_path) != challenger["state_artifact"]["sha256"]:
        raise ValueError("B05 evaluation-state artifact hash mismatch")
    with np.load(state_artifact_path, allow_pickle=False) as payload:
        preserved_restart_states = np.asarray(payload["restart"]).copy()
    if intact_states.shape != preserved_restart_states.shape:
        raise RuntimeError(
            "B06 intact sham state shape differs from preserved B05 restart state"
        )
    state_abs_diff = np.abs(
        intact_states.astype(np.float64)
        - preserved_restart_states.astype(np.float64)
    )
    intact_state_match = np.array_equal(intact_states, preserved_restart_states)
    intact_state_max_abs_diff = float(np.max(state_abs_diff))
    intact_state_mean_abs_diff = float(np.mean(state_abs_diff))
    intact_state_different_values = int(np.count_nonzero(state_abs_diff))
    intact_sham_score_contract_match = intact_score_match
    if not intact_sham_score_contract_match:
        raise RuntimeError(
            "B06 intact sham does not satisfy the preserved B05 behavioral restart tolerance"
        )

    necessity_net = PretoriusRecurrentSubstrate.load(developed_path)
    revert_learned_edges(necessity_net, stabilized)
    necessity_summary, _, _ = _condition_summary(
        "necessity_full_delta_reversion",
        necessity_net,
        probes,
        intact_records,
    )

    sufficiency_sham_net = PretoriusRecurrentSubstrate.load(stabilized_path)
    sufficiency_sham_summary, _, _ = _condition_summary(
        "sufficiency_stabilized_sham",
        sufficiency_sham_net,
        probes,
        intact_records,
    )

    sufficiency_net = PretoriusRecurrentSubstrate.load(stabilized_path)
    transplant_full_delta(sufficiency_net, stabilized, developed)
    sufficiency_summary, _, _ = _condition_summary(
        "sufficiency_full_delta_transplant",
        sufficiency_net,
        probes,
        intact_records,
    )

    targeted_net = PretoriusRecurrentSubstrate.load(developed_path)
    revert_learned_edges(targeted_net, stabilized, targeted)
    targeted_summary, _, _ = _condition_summary(
        "causal_core_targeted_top_5pct",
        targeted_net,
        probes,
        intact_records,
    )

    random_net = PretoriusRecurrentSubstrate.load(developed_path)
    revert_learned_edges(random_net, stabilized, random_matched)
    random_summary, _, _ = _condition_summary(
        "causal_core_random_ei_matched_5pct",
        random_net,
        probes,
        intact_records,
    )

    b04_pre = _mean_expected_probability(
        control["predevelopment_probe_records"]
    )
    b04_post = _mean_expected_probability(
        control["evaluation_probe_records"]
    )
    b05_pre = _mean_expected_probability(
        challenger["predevelopment_probe_records"]
    )
    b05_post = _mean_expected_probability(
        challenger["evaluation_probe_records"]
    )
    intact_mean = float(
        intact_summary["mean_expected_action_probability"]
    )
    necessity_mean = float(
        necessity_summary["mean_expected_action_probability"]
    )
    suff_sham_mean = float(
        sufficiency_sham_summary["mean_expected_action_probability"]
    )
    suff_mean = float(
        sufficiency_summary["mean_expected_action_probability"]
    )
    targeted_mean = float(
        targeted_summary["mean_expected_action_probability"]
    )
    random_mean = float(
        random_summary["mean_expected_action_probability"]
    )
    control_change = b04_post - b04_pre
    challenger_change = b05_post - b05_pre

    relearning_net = PretoriusRecurrentSubstrate.load(developed_path)
    revert_learned_edges(relearning_net, stabilized)
    relearning: list[dict[str, Any]] = []
    for block_index in range(RELEARNING_BLOCKS):
        rows = development[
            block_index * DEVELOPMENT_BLOCK_LENGTH:
            (block_index + 1) * DEVELOPMENT_BLOCK_LENGTH
        ]
        _run_rows(
            relearning_net,
            rows,
            learn=True,
            apply_outcomes=True,
        )
        checkpoint = out / f"relearning_block_{block_index + 1}.npz"
        relearning_net.save(checkpoint)
        block_records, _ = _evaluate_clone(checkpoint, probes)
        current_delta = learned_recurrent_delta(
            stabilized, relearning_net
        )
        relearning.append(
            {
                "block_index": block_index + 1,
                "block": rows[0].block,
                "mean_expected_action_probability": (
                    _mean_expected_probability(block_records)
                ),
                "mean_js_from_original_intact": _mean_pairwise_js(
                    block_records, intact_records
                ),
                "delta_similarity": _delta_similarity(
                    current_delta, delta
                ),
            }
        )
        checkpoint.unlink(missing_ok=True)

    final_relearned_checkpoint = out / "relearned_final.npz"
    relearning_net.save(final_relearned_checkpoint)

    elapsed = time.perf_counter() - started
    result: dict[str, Any] = {
        "schema": "the-doctor-lives.neural-causal-lesions.b06.v1",
        "status": "complete",
        "protocol_version": PROTOCOL_VERSION,
        "lesion_protocol_version": LESION_PROTOCOL_VERSION,
        "repository_sha": _repo_sha(),
        "seed": int(seed),
        "profile": "neural_convergence_v05",
        "started_at_utc": started_at,
        "finished_at_utc": _utc_now(),
        "runtime": _runtime_metadata(),
        "phase_lengths": {
            "lesion_evaluation_per_condition": LESION_EVALUATION_STEPS,
            "relearning": RELEARNING_STEPS,
            "relearning_blocks": RELEARNING_BLOCKS,
        },
        "curriculum_sha256": challenger["curriculum_sha256"],
        "outcome_schedule_sha256": challenger[
            "outcome_schedule_sha256"
        ],
        "configuration": challenger["configuration"],
        "configuration_sha256": challenger[
            "configuration_sha256"
        ],
        "source_artifacts": {
            "b04_repository_sha": control["repository_sha"],
            "b05_repository_sha": challenger["repository_sha"],
            "b04_result_json_sha256": _file_sha256(
                control_dir / "result.json"
            ),
            "b05_result_json_sha256": _file_sha256(
                challenger_dir / "result.json"
            ),
            "b05_stabilized_checkpoint_sha256": _file_sha256(
                stabilized_path
            ),
            "b05_developed_checkpoint_sha256": _file_sha256(
                developed_path
            ),
            "b05_evaluation_states_sha256": _file_sha256(
                state_artifact_path
            ),
        },
        "lesion_definition": {
            "necessity": (
                "Load the B05 developed checkpoint and replace every recurrent "
                "weight with its B05 phase1-stabilized value while preserving "
                "recurrent topology and all other developed checkpoint state."
            ),
            "sufficiency": (
                "Load the B05 phase1-stabilized checkpoint and add the exact full "
                "learned recurrent delta, importing no developed motor, bias, "
                "eligibility, tag, state, or RNG state."
            ),
            "causal_core_rank_metric": (
                "absolute developed-minus-stabilized recurrent-weight delta"
            ),
            "causal_core_fraction": CAUSAL_CORE_FRACTION,
            "causal_core_tie_break": (
                "ascending recurrent CSR data index"
            ),
            "matched_random_control": (
                "Deterministic seed-derived non-target sampling matched exactly "
                "to targeted excitatory/inhibitory edge counts."
            ),
            "relearning": (
                "Start from the B05 developed checkpoint after the full necessity "
                "lesion, then replay the original 3,584-step developmental exposure "
                "with the same learning, reinforcement, and outcome-capture interfaces."
            ),
        },
        "delta": {
            "edge_count": int(delta.size),
            "nonzero_edge_count": int(np.count_nonzero(delta)),
            "l2_norm": float(
                np.linalg.norm(delta.astype(np.float64))
            ),
            "max_abs": (
                float(np.max(np.abs(delta))) if delta.size else 0.0
            ),
            "sha256": _array_sha256(delta),
        },
        "causal_core": {
            "targeted_edge_count": int(targeted.size),
            "random_edge_count": int(random_matched.size),
            "targeted_indices_sha256": _array_sha256(targeted),
            "random_indices_sha256": _array_sha256(random_matched),
            "targeted_exc_count": int(
                np.count_nonzero(
                    developed.excitatory[
                        developed.pre_idx[targeted]
                    ]
                )
            ),
            "random_exc_count": int(
                np.count_nonzero(
                    developed.excitatory[
                        developed.pre_idx[random_matched]
                    ]
                )
            ),
        },
        "preserved_baselines": {
            "b04_pre_mean_expected_action_probability": b04_pre,
            "b04_post_mean_expected_action_probability": b04_post,
            "b04_change": control_change,
            "b05_pre_mean_expected_action_probability": b05_pre,
            "b05_post_mean_expected_action_probability": b05_post,
            "b05_change": challenger_change,
            "paired_candidate_effect": (
                challenger_change - control_change
            ),
        },
        "conditions": {
            "intact_developed_sham": intact_summary,
            "necessity_full_delta_reversion": necessity_summary,
            "sufficiency_stabilized_sham": (
                sufficiency_sham_summary
            ),
            "sufficiency_full_delta_transplant": (
                sufficiency_summary
            ),
            "causal_core_targeted_top_5pct": targeted_summary,
            "causal_core_random_ei_matched_5pct": random_summary,
        },
        "causal_contrasts": {
            "intact_sham_behavioral_match_to_b05_restart": (
                intact_sham_score_contract_match
            ),
            "intact_sham_score_max_abs_diff": intact_score_max_abs_diff,
            "intact_sham_state_exact_match": intact_state_match,
            "intact_sham_state_max_abs_diff": intact_state_max_abs_diff,
            "intact_sham_state_mean_abs_diff": intact_state_mean_abs_diff,
            "intact_sham_state_different_values": intact_state_different_values,
            "necessity_damage_expected_action_probability": (
                intact_mean - necessity_mean
            ),
            "necessity_paired_effect_after_lesion": (
                (necessity_mean - b05_pre) - control_change
            ),
            "sufficiency_transplant_gain_over_stabilized_sham": (
                suff_mean - suff_sham_mean
            ),
            "sufficiency_fraction_of_b05_profile_change": (
                (suff_mean - suff_sham_mean) / challenger_change
                if abs(challenger_change) > 1e-12
                else None
            ),
            "targeted_damage_expected_action_probability": (
                intact_mean - targeted_mean
            ),
            "random_damage_expected_action_probability": (
                intact_mean - random_mean
            ),
            "targeted_minus_random_damage": (
                random_mean - targeted_mean
            ),
            "targeted_vs_random_mean_js_difference": (
                float(targeted_summary["mean_js_from_intact"])
                - float(random_summary["mean_js_from_intact"])
            ),
        },
        "relearning": relearning,
        "artifacts": {
            "lesion_masks": {
                "path": mask_path.name,
                "sha256": _file_sha256(mask_path),
            },
            "relearned_final_checkpoint": {
                "path": final_relearned_checkpoint.name,
                "sha256": _file_sha256(
                    final_relearned_checkpoint
                ),
                "size_bytes": int(
                    final_relearned_checkpoint.stat().st_size
                ),
            },
        },
        "computational_cost": {
            "wall_seconds": float(elapsed),
        },
        "interpretation_boundary": [
            "B06 tests causal contribution of learned recurrent change under the frozen B02 protocol.",
            "Necessity and sufficiency are asymmetric by design: necessity preserves developed non-recurrent state; sufficiency imports only recurrent delta into the stabilized baseline.",
            "Cross-run recurrent-state bitwise equality is recorded diagnostically but is not a B06 validity gate because B05 preregistered exact restart equality within each characterization run, not across heterogeneous GitHub runner hardware. The B06 sham hard gate uses the preserved B05 behavioral tolerance of 1e-12.",
            "A favorable lesion contrast does not establish identity transfer, consciousness, or biological equivalence.",
            "No B06 result alone authorizes production promotion; B07 and B08 remain required.",
        ],
    }
    result["artifact_sha256"] = sha256_json(result)
    (out / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return result


def validate_lesion_protocol_surface() -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "lesion_protocol_version": LESION_PROTOCOL_VERSION,
        "seeds": list(DECISIVE_SEEDS),
        "causal_core_fraction": CAUSAL_CORE_FRACTION,
        "causal_core_rank_metric": (
            "absolute developed-minus-stabilized recurrent-weight delta"
        ),
        "random_control": (
            "E/I-stratified, size-matched, non-overlapping, deterministic by seed"
        ),
        "lesion_evaluation_steps": LESION_EVALUATION_STEPS,
        "relearning_steps": RELEARNING_STEPS,
        "relearning_blocks": RELEARNING_BLOCKS,
    }
