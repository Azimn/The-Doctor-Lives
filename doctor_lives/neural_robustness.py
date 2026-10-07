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
from typing import Any, Callable, Iterable

import numpy as np

from .neural import PretoriusRecurrentSubstrate
from .neural_characterization import (
    DECISIVE_SEEDS,
    PROTOCOL_VERSION,
    Stimulus,
    _run_rows,
    evaluation_probes,
    representational_summary,
    sha256_json,
)
from .neural_lesions import (
    CAUSAL_CORE_FRACTION,
    _file_sha256,
    _load_json,
    _mean_expected_probability,
    _mean_pairwise_js,
    _validate_source_artifacts,
    learned_recurrent_delta,
    rank_causal_core,
    revert_learned_edges,
    verify_recurrent_topology,
)

ROBUSTNESS_PROTOCOL_VERSION = "neural-convergence-robustness-b07-v1"
RECURRENT_WEIGHT_CLIP_FRACTIONS = (0.75, 0.50)
DELTA_CLIP_QUANTILES = (0.95, 0.75)
MODEST_WEIGHT_PERTURBATION_FRACTION = 0.02
HIGH_CHANGE_FRACTION = CAUSAL_CORE_FRACTION
EVALUATION_STEPS = 512


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


def _array_sha256(values: np.ndarray) -> str:
    array = np.ascontiguousarray(values)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(str(tuple(array.shape)).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def verify_sign_contract(net: PretoriusRecurrentSubstrate) -> dict[str, Any]:
    values = np.asarray(net.W.data, dtype=np.float64)
    edge_is_exc = net.excitatory[net.pre_idx]
    limit = float(net.cfg["max_abs_weight"])
    exc_wrong = int(np.count_nonzero(values[edge_is_exc] < -1e-12))
    inh_wrong = int(np.count_nonzero(values[~edge_is_exc] > 1e-12))
    nonfinite = int(np.count_nonzero(~np.isfinite(values)))
    over_limit = int(np.count_nonzero(np.abs(values) > limit + 1e-7))
    return {
        "pass": bool(exc_wrong == 0 and inh_wrong == 0 and nonfinite == 0 and over_limit == 0),
        "excitatory_wrong_sign_count": exc_wrong,
        "inhibitory_wrong_sign_count": inh_wrong,
        "nonfinite_weight_count": nonfinite,
        "over_configured_limit_count": over_limit,
        "max_abs_weight_observed": float(np.max(np.abs(values))) if values.size else 0.0,
        "configured_max_abs_weight": limit,
    }


def permute_delta_within_ei(
    delta: np.ndarray,
    net: PretoriusRecurrentSubstrate,
    seed: int,
) -> np.ndarray:
    values = np.asarray(delta, dtype=np.float32)
    if values.shape != net.W.data.shape:
        raise ValueError("delta shape does not match recurrent edge vector")
    edge_is_exc = net.excitatory[net.pre_idx]
    rng = np.random.default_rng(int(seed) * 31337 + 707)
    result = values.copy()
    for is_exc in (True, False):
        indices = np.flatnonzero(edge_is_exc == is_exc)
        shuffled = values[indices].copy()
        rng.shuffle(shuffled)
        result[indices] = shuffled
    return result


def ordinary_edge_indices(
    delta: np.ndarray,
    net: PretoriusRecurrentSubstrate,
    high_change_indices: np.ndarray,
) -> np.ndarray:
    values = np.abs(np.asarray(delta, dtype=np.float64))
    targeted = np.asarray(high_change_indices, dtype=np.int64)
    if values.ndim != 1 or values.shape != net.W.data.shape:
        raise ValueError("delta must match recurrent edge vector")
    edge_is_exc = net.excitatory[net.pre_idx]
    targeted_mask = np.zeros(values.size, dtype=bool)
    targeted_mask[targeted] = True
    chosen: list[np.ndarray] = []
    for is_exc in (True, False):
        needed = int(np.count_nonzero(edge_is_exc[targeted] == is_exc))
        if needed == 0:
            continue
        candidates = np.flatnonzero((edge_is_exc == is_exc) & ~targeted_mask)
        if candidates.size < needed:
            raise ValueError("insufficient ordinary edges for E/I-matched comparison")
        median = float(np.median(values[candidates]))
        order = np.lexsort((candidates, np.abs(values[candidates] - median)))
        chosen.append(candidates[order[:needed]].astype(np.int64, copy=False))
    result = np.sort(np.concatenate(chosen))
    if result.size != targeted.size:
        raise RuntimeError("ordinary comparison size differs from high-change set")
    return result


def project_delta_by_weight_quantile(
    donor_stabilized: PretoriusRecurrentSubstrate,
    donor_developed: PretoriusRecurrentSubstrate,
    recipient: PretoriusRecurrentSubstrate,
) -> np.ndarray:
    delta = learned_recurrent_delta(donor_stabilized, donor_developed).astype(np.float64)
    donor_ei = donor_stabilized.excitatory[donor_stabilized.pre_idx]
    recipient_ei = recipient.excitatory[recipient.pre_idx]
    projected = np.zeros(recipient.W.data.size, dtype=np.float64)

    for is_exc in (True, False):
        donor_idx = np.flatnonzero(donor_ei == is_exc)
        recipient_idx = np.flatnonzero(recipient_ei == is_exc)
        if donor_idx.size == 0 or recipient_idx.size == 0:
            raise ValueError("both donor and recipient require E/I edge support")
        donor_order = donor_idx[np.lexsort((donor_idx, np.abs(donor_stabilized.W.data[donor_idx])))]
        recipient_order = recipient_idx[np.lexsort((recipient_idx, np.abs(recipient.W.data[recipient_idx])))]
        source_q = (np.arange(donor_order.size, dtype=np.float64) + 0.5) / donor_order.size
        target_q = (np.arange(recipient_order.size, dtype=np.float64) + 0.5) / recipient_order.size
        projected_values = np.interp(target_q, source_q, delta[donor_order])
        projected[recipient_order] = projected_values

    return projected.astype(np.float32)


def apply_delta(
    net: PretoriusRecurrentSubstrate,
    delta: np.ndarray,
) -> dict[str, Any]:
    values = np.asarray(delta, dtype=np.float32)
    if values.shape != net.W.data.shape:
        raise ValueError("delta shape does not match target recurrent edge vector")
    before = net.W.data.copy()
    raw = before + values
    net.W.data[:] = raw
    net._enforce_sign_and_bounds()
    changed_by_contract = int(np.count_nonzero(net.W.data != raw))
    return {
        "delta_l2": float(np.linalg.norm(values.astype(np.float64))),
        "delta_max_abs": float(np.max(np.abs(values))) if values.size else 0.0,
        "contract_adjusted_edge_count": changed_by_contract,
    }


def clip_recurrent_weights(
    net: PretoriusRecurrentSubstrate,
    fraction: float,
) -> dict[str, Any]:
    fraction = float(fraction)
    if not 0.0 < fraction <= 1.0:
        raise ValueError("weight clip fraction must be in (0, 1]")
    limit = fraction * float(net.cfg["max_abs_weight"])
    before = net.W.data.copy()
    net.W.data[:] = np.clip(net.W.data, -limit, limit)
    net._enforce_sign_and_bounds()
    return {
        "fraction_of_configured_limit": fraction,
        "absolute_limit": limit,
        "affected_edge_count": int(np.count_nonzero(before != net.W.data)),
    }


def clip_delta_by_quantile(delta: np.ndarray, quantile: float) -> tuple[np.ndarray, dict[str, Any]]:
    values = np.asarray(delta, dtype=np.float32)
    quantile = float(quantile)
    if not 0.0 < quantile <= 1.0:
        raise ValueError("delta clip quantile must be in (0, 1]")
    threshold = float(np.quantile(np.abs(values.astype(np.float64)), quantile))
    clipped = np.clip(values, -threshold, threshold).astype(np.float32, copy=False)
    return clipped, {
        "quantile": quantile,
        "absolute_threshold": threshold,
        "affected_edge_count": int(np.count_nonzero(values != clipped)),
    }


def perturb_recurrent_weights(
    net: PretoriusRecurrentSubstrate,
    seed: int,
    fraction: float = MODEST_WEIGHT_PERTURBATION_FRACTION,
) -> dict[str, Any]:
    fraction = float(fraction)
    if not 0.0 < fraction < 1.0:
        raise ValueError("perturbation fraction must be in (0, 1)")
    rng = np.random.default_rng(int(seed) * 65537 + 70707)
    multiplier = rng.uniform(1.0 - fraction, 1.0 + fraction, size=net.W.data.size).astype(np.float32)
    before = net.W.data.copy()
    net.W.data[:] = net.W.data * multiplier
    net._enforce_sign_and_bounds()
    relative = np.divide(
        np.abs(net.W.data.astype(np.float64) - before.astype(np.float64)),
        np.maximum(np.abs(before.astype(np.float64)), 1e-12),
    )
    return {
        "fraction": fraction,
        "multiplier_min": float(np.min(multiplier)),
        "multiplier_max": float(np.max(multiplier)),
        "mean_relative_weight_change": float(np.mean(relative)),
        "max_relative_weight_change": float(np.max(relative)),
    }


def _condition_summary(
    name: str,
    net: PretoriusRecurrentSubstrate,
    probes: tuple[Stimulus, ...],
    reference_records: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], np.ndarray]:
    records, states = _run_rows(
        net,
        probes,
        learn=False,
        apply_outcomes=False,
        capture_states=True,
    )
    assert states is not None
    summary: dict[str, Any] = {
        "name": name,
        "mean_expected_action_probability": _mean_expected_probability(records),
        "recurrent_gain_estimate": float(net._estimate_recurrent_gain()),
        "representational_summary": representational_summary(states, probes),
        "sign_contract": verify_sign_contract(net),
    }
    if reference_records is not None:
        summary["mean_js_from_reference"] = _mean_pairwise_js(records, reference_records)
    return summary, records, states


def _repeatable_condition(
    name: str,
    builder: Callable[[], PretoriusRecurrentSubstrate],
    probes: tuple[Stimulus, ...],
    reference_records: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], np.ndarray]:
    first_summary, first_records, first_states = _condition_summary(
        name, builder(), probes, reference_records
    )
    second_summary, second_records, second_states = _condition_summary(
        name, builder(), probes, reference_records
    )
    first_summary["fixed_seed_rerun_record_exact_match"] = bool(first_records == second_records)
    first_summary["fixed_seed_rerun_state_exact_match"] = bool(np.array_equal(first_states, second_states))
    first_summary["fixed_seed_rerun_exact_match"] = bool(
        first_summary["fixed_seed_rerun_record_exact_match"]
        and first_summary["fixed_seed_rerun_state_exact_match"]
    )
    return first_summary, first_records, first_states


def _validate_b06_artifact(
    b06_dir: Path,
    seed: int,
    control_dir: Path,
    challenger_dir: Path,
    stabilized: PretoriusRecurrentSubstrate,
    developed: PretoriusRecurrentSubstrate,
) -> dict[str, Any]:
    result = _load_json(b06_dir / "result.json")
    if result.get("status") != "complete" or int(result.get("seed", -1)) != int(seed):
        raise ValueError("B06 artifact is incomplete or has wrong seed")
    if result.get("profile") != "neural_convergence_v05":
        raise ValueError("B06 profile mismatch")
    if result["source_artifacts"]["b04_result_json_sha256"] != _file_sha256(control_dir / "result.json"):
        raise ValueError("B06 B04 source hash does not match downloaded B04 artifact")
    if result["source_artifacts"]["b05_result_json_sha256"] != _file_sha256(challenger_dir / "result.json"):
        raise ValueError("B06 B05 source hash does not match downloaded B05 artifact")
    mask_path = b06_dir / result["artifacts"]["lesion_masks"]["path"]
    if _file_sha256(mask_path) != result["artifacts"]["lesion_masks"]["sha256"]:
        raise ValueError("B06 lesion-mask hash mismatch")
    with np.load(mask_path, allow_pickle=False) as payload:
        stored_delta = np.asarray(payload["learned_delta"], dtype=np.float32)
        stored_targeted = np.asarray(payload["targeted_indices"], dtype=np.int64)
    current_delta = learned_recurrent_delta(stabilized, developed)
    current_targeted = rank_causal_core(current_delta, fraction=HIGH_CHANGE_FRACTION)
    if not np.array_equal(stored_delta, current_delta):
        raise ValueError("B06 learned delta does not match B05 checkpoints")
    if not np.array_equal(stored_targeted, current_targeted):
        raise ValueError("B06 targeted core does not match B07 recomputation")
    return result


def run_robustness(
    seed: int,
    control_dir: str | Path,
    challenger_dir: str | Path,
    b06_dir: str | Path,
    independent_control_dir: str | Path,
    independent_seed: int,
    output_dir: str | Path,
) -> dict[str, Any]:
    if int(seed) not in DECISIVE_SEEDS or int(independent_seed) not in DECISIVE_SEEDS:
        raise ValueError("B07 seeds must come from the preregistered decisive set")
    expected_independent = DECISIVE_SEEDS[(DECISIVE_SEEDS.index(int(seed)) + 1) % len(DECISIVE_SEEDS)]
    if int(independent_seed) != int(expected_independent):
        raise ValueError("independent topology seed must be the next preregistered seed cyclically")

    control_dir = Path(control_dir)
    challenger_dir = Path(challenger_dir)
    b06_dir = Path(b06_dir)
    independent_control_dir = Path(independent_control_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    control, challenger = _validate_source_artifacts(control_dir, challenger_dir, seed)
    independent_control = _load_json(independent_control_dir / "result.json")
    if independent_control.get("status") != "complete":
        raise ValueError("independent B04 artifact is incomplete")
    if independent_control.get("profile") != "legacy_v04":
        raise ValueError("independent B04 profile mismatch")
    if int(independent_control.get("seed", -1)) != int(independent_seed):
        raise ValueError("independent B04 seed mismatch")
    if int(independent_control["configuration"]["neurons"]) != 4096:
        raise ValueError("independent B04 artifact is not 4,096 units")

    b04_stabilized_path = control_dir / "phase1_stabilized.npz"
    b05_stabilized_path = challenger_dir / "phase1_stabilized.npz"
    b05_developed_path = challenger_dir / "phase2_developed.npz"
    independent_stabilized_path = independent_control_dir / "phase1_stabilized.npz"
    for path in (b04_stabilized_path, b05_stabilized_path, b05_developed_path, independent_stabilized_path):
        if not path.is_file():
            raise FileNotFoundError(f"required B07 checkpoint missing: {path}")

    b04_stabilized = PretoriusRecurrentSubstrate.load(b04_stabilized_path)
    b05_stabilized = PretoriusRecurrentSubstrate.load(b05_stabilized_path)
    b05_developed = PretoriusRecurrentSubstrate.load(b05_developed_path)
    independent_stabilized = PretoriusRecurrentSubstrate.load(independent_stabilized_path)
    verify_recurrent_topology(b05_stabilized, b05_developed)
    verify_recurrent_topology(b04_stabilized, b05_stabilized)
    if np.array_equal(independent_stabilized.W.indptr, b05_stabilized.W.indptr) and np.array_equal(
        independent_stabilized.W.indices, b05_stabilized.W.indices
    ):
        raise ValueError("independent topology unexpectedly matches donor topology")

    b06 = _validate_b06_artifact(
        b06_dir, seed, control_dir, challenger_dir, b05_stabilized, b05_developed
    )

    started_at = _utc_now()
    started = time.perf_counter()
    donor_delta = learned_recurrent_delta(b05_stabilized, b05_developed)
    high_change = rank_causal_core(donor_delta, fraction=HIGH_CHANGE_FRACTION)
    ordinary = ordinary_edge_indices(donor_delta, b05_developed, high_change)
    permuted_delta = permute_delta_within_ei(donor_delta, b05_stabilized, seed)
    independent_projection = project_delta_by_weight_quantile(
        b05_stabilized, b05_developed, independent_stabilized
    )

    transforms_path = out / "b07_transforms.npz"
    np.savez_compressed(
        transforms_path,
        learned_delta=donor_delta,
        permuted_delta=permuted_delta,
        high_change_indices=high_change,
        ordinary_indices=ordinary,
        independent_projection=independent_projection,
    )

    probes = evaluation_probes(seed)
    independent_probes = evaluation_probes(independent_seed)

    intact_summary, intact_records, _ = _repeatable_condition(
        "b05_developed_intact",
        lambda: PretoriusRecurrentSubstrate.load(b05_developed_path),
        probes,
    )
    b05_stabilized_summary, b05_stabilized_records, _ = _repeatable_condition(
        "b05_stabilized_sham",
        lambda: PretoriusRecurrentSubstrate.load(b05_stabilized_path),
        probes,
        intact_records,
    )
    b04_stabilized_summary, b04_stabilized_records, _ = _repeatable_condition(
        "b04_stabilized_recipient_sham",
        lambda: PretoriusRecurrentSubstrate.load(b04_stabilized_path),
        probes,
    )
    independent_stabilized_summary, independent_stabilized_records, _ = _repeatable_condition(
        "independent_b04_stabilized_recipient_sham",
        lambda: PretoriusRecurrentSubstrate.load(independent_stabilized_path),
        independent_probes,
    )

    def topology_transfer_builder() -> PretoriusRecurrentSubstrate:
        net = PretoriusRecurrentSubstrate.load(b04_stabilized_path)
        apply_delta(net, donor_delta)
        return net

    topology_summary, topology_records, _ = _repeatable_condition(
        "topology_matched_transfer_b05_delta_to_b04",
        topology_transfer_builder,
        probes,
        b04_stabilized_records,
    )

    def exact_sufficiency_builder() -> PretoriusRecurrentSubstrate:
        net = PretoriusRecurrentSubstrate.load(b05_stabilized_path)
        apply_delta(net, donor_delta)
        return net

    exact_summary, exact_records, _ = _repeatable_condition(
        "exact_delta_on_b05_stabilized",
        exact_sufficiency_builder,
        probes,
        b05_stabilized_records,
    )

    def permuted_builder() -> PretoriusRecurrentSubstrate:
        net = PretoriusRecurrentSubstrate.load(b05_stabilized_path)
        apply_delta(net, permuted_delta)
        return net

    permuted_summary, permuted_records, _ = _repeatable_condition(
        "ei_stratified_assignment_permutation",
        permuted_builder,
        probes,
        exact_records,
    )

    def independent_builder() -> PretoriusRecurrentSubstrate:
        net = PretoriusRecurrentSubstrate.load(independent_stabilized_path)
        apply_delta(net, independent_projection)
        return net

    independent_summary, independent_records, _ = _repeatable_condition(
        "independent_topology_functional_homology",
        independent_builder,
        independent_probes,
        independent_stabilized_records,
    )

    def high_change_builder() -> PretoriusRecurrentSubstrate:
        net = PretoriusRecurrentSubstrate.load(b05_developed_path)
        revert_learned_edges(net, b05_stabilized, high_change)
        return net

    high_summary, high_records, _ = _repeatable_condition(
        "high_change_edge_reversion",
        high_change_builder,
        probes,
        intact_records,
    )

    def ordinary_builder() -> PretoriusRecurrentSubstrate:
        net = PretoriusRecurrentSubstrate.load(b05_developed_path)
        revert_learned_edges(net, b05_stabilized, ordinary)
        return net

    ordinary_summary, ordinary_records, _ = _repeatable_condition(
        "ordinary_edge_reversion",
        ordinary_builder,
        probes,
        intact_records,
    )

    weight_clip_summaries: dict[str, Any] = {}
    for fraction in RECURRENT_WEIGHT_CLIP_FRACTIONS:
        name = f"developed_weight_clip_{int(round(fraction * 100))}pct_limit"

        def builder(f: float = fraction) -> PretoriusRecurrentSubstrate:
            net = PretoriusRecurrentSubstrate.load(b05_developed_path)
            clip_recurrent_weights(net, f)
            return net

        summary, records, _ = _repeatable_condition(name, builder, probes, intact_records)
        metadata_net = PretoriusRecurrentSubstrate.load(b05_developed_path)
        summary["clip_definition"] = clip_recurrent_weights(metadata_net, fraction)
        weight_clip_summaries[name] = summary

    delta_clip_summaries: dict[str, Any] = {}
    for quantile in DELTA_CLIP_QUANTILES:
        clipped_delta, clip_definition = clip_delta_by_quantile(donor_delta, quantile)
        name = f"delta_clip_q{int(round(quantile * 100))}"

        def builder(values: np.ndarray = clipped_delta) -> PretoriusRecurrentSubstrate:
            net = PretoriusRecurrentSubstrate.load(b05_stabilized_path)
            apply_delta(net, values)
            return net

        summary, records, _ = _repeatable_condition(name, builder, probes, exact_records)
        summary["clip_definition"] = clip_definition
        delta_clip_summaries[name] = summary

    def perturbation_builder() -> PretoriusRecurrentSubstrate:
        net = PretoriusRecurrentSubstrate.load(b05_developed_path)
        perturb_recurrent_weights(net, seed)
        return net

    perturb_summary, perturb_records, _ = _repeatable_condition(
        "developed_modest_2pct_weight_perturbation",
        perturbation_builder,
        probes,
        intact_records,
    )
    perturb_metadata_net = PretoriusRecurrentSubstrate.load(b05_developed_path)
    perturb_summary["perturbation_definition"] = perturb_recurrent_weights(
        perturb_metadata_net, seed
    )

    edge_is_exc = b05_developed.excitatory[b05_developed.pre_idx]
    delta_abs = np.abs(donor_delta.astype(np.float64))
    high_l2 = float(np.linalg.norm(donor_delta[high_change].astype(np.float64)))
    total_l2 = float(np.linalg.norm(donor_delta.astype(np.float64)))
    high_fraction_l2_sq = (
        float(high_l2 * high_l2 / (total_l2 * total_l2)) if total_l2 > 1e-15 else 0.0
    )

    all_condition_summaries = {
        "b05_developed_intact": intact_summary,
        "b05_stabilized_sham": b05_stabilized_summary,
        "b04_stabilized_recipient_sham": b04_stabilized_summary,
        "independent_b04_stabilized_recipient_sham": independent_stabilized_summary,
        "topology_matched_transfer": topology_summary,
        "exact_delta_sufficiency": exact_summary,
        "assignment_permutation": permuted_summary,
        "independent_topology_homology": independent_summary,
        "high_change_reversion": high_summary,
        "ordinary_edge_reversion": ordinary_summary,
        "modest_perturbation": perturb_summary,
        **weight_clip_summaries,
        **delta_clip_summaries,
    }
    fixed_seed_all_exact = all(
        bool(summary["fixed_seed_rerun_exact_match"])
        for summary in all_condition_summaries.values()
    )
    sign_contract_all_pass = all(
        bool(summary["sign_contract"]["pass"])
        for summary in all_condition_summaries.values()
    )

    topology_transfer_gain = (
        float(topology_summary["mean_expected_action_probability"])
        - float(b04_stabilized_summary["mean_expected_action_probability"])
    )
    exact_delta_gain = (
        float(exact_summary["mean_expected_action_probability"])
        - float(b05_stabilized_summary["mean_expected_action_probability"])
    )
    permutation_gain = (
        float(permuted_summary["mean_expected_action_probability"])
        - float(b05_stabilized_summary["mean_expected_action_probability"])
    )
    independent_gain = (
        float(independent_summary["mean_expected_action_probability"])
        - float(independent_stabilized_summary["mean_expected_action_probability"])
    )
    high_damage = (
        float(intact_summary["mean_expected_action_probability"])
        - float(high_summary["mean_expected_action_probability"])
    )
    ordinary_damage = (
        float(intact_summary["mean_expected_action_probability"])
        - float(ordinary_summary["mean_expected_action_probability"])
    )

    result: dict[str, Any] = {
        "schema": "the-doctor-lives.neural-robustness.b07.v1",
        "status": "complete",
        "protocol_version": PROTOCOL_VERSION,
        "robustness_protocol_version": ROBUSTNESS_PROTOCOL_VERSION,
        "repository_sha": _repo_sha(),
        "seed": int(seed),
        "independent_topology_seed": int(independent_seed),
        "profile": "neural_convergence_v05",
        "started_at_utc": started_at,
        "finished_at_utc": _utc_now(),
        "runtime": _runtime_metadata(),
        "evaluation_steps_per_condition": EVALUATION_STEPS,
        "curriculum_sha256": challenger["curriculum_sha256"],
        "outcome_schedule_sha256": challenger["outcome_schedule_sha256"],
        "configuration": challenger["configuration"],
        "configuration_sha256": challenger["configuration_sha256"],
        "source_artifacts": {
            "b04_repository_sha": control["repository_sha"],
            "b05_repository_sha": challenger["repository_sha"],
            "b06_repository_sha": b06["repository_sha"],
            "b04_result_json_sha256": _file_sha256(control_dir / "result.json"),
            "b05_result_json_sha256": _file_sha256(challenger_dir / "result.json"),
            "b06_result_json_sha256": _file_sha256(b06_dir / "result.json"),
            "independent_b04_result_json_sha256": _file_sha256(independent_control_dir / "result.json"),
            "b05_stabilized_checkpoint_sha256": _file_sha256(b05_stabilized_path),
            "b05_developed_checkpoint_sha256": _file_sha256(b05_developed_path),
            "b04_stabilized_checkpoint_sha256": _file_sha256(b04_stabilized_path),
            "independent_b04_stabilized_checkpoint_sha256": _file_sha256(independent_stabilized_path),
        },
        "probe_definition": {
            "topology_matched_transfer": (
                "Apply the exact B05 learned recurrent delta to the same-seed B04 phase1-stabilized checkpoint. "
                "B04 and B05 same-seed recurrent topology and E/I assignment must match exactly before transfer."
            ),
            "independent_topology_functional_homology": (
                "Project the donor B05 delta onto the next preregistered seed's B04 recurrent topology separately by E/I stratum, "
                "mapping donor delta values by donor baseline-weight quantile to recipient baseline-weight quantile."
            ),
            "assignment_permutation": (
                "Permute learned-delta assignments deterministically within excitatory and inhibitory edge strata on the original B05 topology, preserving each stratum's exact delta multiset."
            ),
            "high_change_vs_ordinary": (
                "Compare top 5 percent absolute learned-delta edge reversion against an equal-size, E/I-matched set closest to the median absolute learned-delta magnitude."
            ),
            "recurrent_weight_clipping": [float(x) for x in RECURRENT_WEIGHT_CLIP_FRACTIONS],
            "delta_clipping_quantiles": [float(x) for x in DELTA_CLIP_QUANTILES],
            "modest_perturbation": MODEST_WEIGHT_PERTURBATION_FRACTION,
            "fixed_seed_rerun": (
                "Every B07 condition is rebuilt independently twice within the same run and must match exactly in action records and recurrent-state snapshots."
            ),
        },
        "delta_distribution": {
            "edge_count": int(donor_delta.size),
            "nonzero_edge_count": int(np.count_nonzero(donor_delta)),
            "sha256": _array_sha256(donor_delta),
            "l2_norm": total_l2,
            "max_abs": float(np.max(delta_abs)) if delta_abs.size else 0.0,
            "median_abs": float(np.median(delta_abs)) if delta_abs.size else 0.0,
            "p95_abs": float(np.quantile(delta_abs, 0.95)) if delta_abs.size else 0.0,
            "p99_abs": float(np.quantile(delta_abs, 0.99)) if delta_abs.size else 0.0,
            "high_change_edge_count": int(high_change.size),
            "ordinary_edge_count": int(ordinary.size),
            "high_change_l2_fraction_squared": high_fraction_l2_sq,
            "high_change_exc_count": int(np.count_nonzero(edge_is_exc[high_change])),
            "ordinary_exc_count": int(np.count_nonzero(edge_is_exc[ordinary])),
            "permuted_delta_sha256": _array_sha256(permuted_delta),
            "independent_projection_sha256": _array_sha256(independent_projection),
        },
        "conditions": all_condition_summaries,
        "contrasts": {
            "topology_matched_transfer_gain_over_b04_stabilized": topology_transfer_gain,
            "exact_delta_gain_over_b05_stabilized": exact_delta_gain,
            "assignment_permutation_gain_over_b05_stabilized": permutation_gain,
            "assignment_permutation_minus_exact_gain": permutation_gain - exact_delta_gain,
            "independent_topology_homology_gain_over_recipient_stabilized": independent_gain,
            "high_change_reversion_damage": high_damage,
            "ordinary_edge_reversion_damage": ordinary_damage,
            "high_change_minus_ordinary_damage": high_damage - ordinary_damage,
            "modest_perturbation_damage": (
                float(intact_summary["mean_expected_action_probability"])
                - float(perturb_summary["mean_expected_action_probability"])
            ),
            "modest_perturbation_mean_js_from_intact": float(perturb_summary["mean_js_from_reference"]),
            "fixed_seed_rerun_all_exact": fixed_seed_all_exact,
            "sign_contract_all_conditions_pass": sign_contract_all_pass,
        },
        "artifacts": {
            "transforms": {
                "path": transforms_path.name,
                "sha256": _file_sha256(transforms_path),
            }
        },
        "computational_cost": {
            "wall_seconds": float(time.perf_counter() - started),
        },
        "interpretation_boundary": [
            "B07 measures transferability, distribution dependence, clipping sensitivity, sign integrity, and brittleness of the frozen 4,096-unit recurrent developmental mechanism.",
            "Topology-matched and independent-topology transfer concern recurrent developmental effects only and must not be described as identity transfer.",
            "A null transfer result is preserved as a valid scientific result, not a harness failure.",
            "Clipping and perturbation probes preserve the configured E/I sign contract; any sign-contract or non-finite failure is a hard integrity defect.",
            "B07 does not execute the reserved 16,384-unit scaling rung and cannot establish a universal scaling ceiling.",
            "No B07 result alone authorizes production promotion; B08 disposition remains required.",
        ],
    }
    result["artifact_sha256"] = sha256_json(result)
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def validate_robustness_protocol_surface() -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "robustness_protocol_version": ROBUSTNESS_PROTOCOL_VERSION,
        "seeds": list(DECISIVE_SEEDS),
        "independent_seed_rule": "next decisive seed cyclically",
        "evaluation_steps_per_condition": EVALUATION_STEPS,
        "high_change_fraction": HIGH_CHANGE_FRACTION,
        "recurrent_weight_clip_fractions": list(RECURRENT_WEIGHT_CLIP_FRACTIONS),
        "delta_clip_quantiles": list(DELTA_CLIP_QUANTILES),
        "modest_weight_perturbation_fraction": MODEST_WEIGHT_PERTURBATION_FRACTION,
        "assignment_permutation": "deterministic within E/I strata; exact per-stratum delta multiset preserved",
        "functional_homology": "E/I-stratified baseline-weight-quantile projection onto next preregistered seed topology",
        "fixed_seed_rerun": "all conditions independently rebuilt twice; exact action-record and state equality required",
    }
