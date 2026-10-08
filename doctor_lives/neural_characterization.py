from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any, Iterable

import numpy as np

from .neural import (
    ACTIONS,
    DEFAULT_CONFIG,
    NEURAL_CONVERGENCE_CONFIG,
    PretoriusRecurrentSubstrate,
)


PROTOCOL_VERSION = "neural-convergence-characterization-b02-v1"
HARNESS_VERSION = "neural-convergence-characterization-b03-v1"
DECISIVE_SEEDS = (1842, 1843, 1844, 1845, 1846, 1847)
PRODUCTION_NEURONS = 4096
PHASE_LENGTHS = {
    "neutral_stabilization": 512,
    "developmental_exposure": 3584,
    "evaluation": 512,
    "restart_evaluation": 512,
}
DEVELOPMENT_BLOCK_LENGTH = 512
PROTOCOL_TIMELINE_STEPS = sum(PHASE_LENGTHS.values())
PROFILES = ("legacy_v04", "neural_convergence_v05")
PROBE_KINDS = ("seen", "near_neighbor", "opposite_context", "held_out")


@dataclass(frozen=True)
class Stimulus:
    phase: str
    ordinal: int
    text: str
    scalars: dict[str, float]
    confidence: float
    reward: float = 0.0
    teaching_action: str | None = None
    block: str | None = None
    outcome_class: str | None = None
    probe_kind: str | None = None
    expected_action: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_BLOCKS: tuple[dict[str, Any], ...] = (
    {
        "name": "novelty_exploration_creation",
        "actions": ("explore", "create"),
        "texts": (
            "A strange unfinished apparatus presents a new possibility.",
            "An unfamiliar mechanism invites careful experimental inspection.",
            "A novel construction problem opens another route forward.",
            "A half-built device suggests a different way to make progress.",
        ),
        "scalars": {"novelty": .9, "creation": .8, "achievement": .35, "arousal": .45},
    },
    {
        "name": "authority_autonomy_coercion",
        "actions": ("challenge", "persist"),
        "texts": (
            "An authority insists that the procedure stop despite incomplete evidence.",
            "A senior figure demands compliance with a restrictive instruction.",
            "External pressure narrows the available choices in the experiment.",
            "A command conflicts with the freedom needed to continue the work.",
        ),
        "scalars": {"authority": .9, "autonomy": -.75, "control": -.55, "threat": .35},
    },
    {
        "name": "social_approach_cooperation_distrust",
        "actions": ("cooperate", "approach"),
        "texts": (
            "A collaborator offers help but has not yet established complete reliability.",
            "Someone nearby proposes a joint solution to the difficult problem.",
            "A familiar partner asks to work together under uncertain conditions.",
            "A social opportunity mixes useful cooperation with reason for caution.",
        ),
        "scalars": {"social": .85, "intimacy": .45, "valence": .2, "novelty": .25},
    },
    {
        "name": "threat_avoidance_control",
        "actions": ("avoid", "challenge"),
        "texts": (
            "A dangerous disturbance develops near the active apparatus.",
            "The situation becomes threatening while control over the equipment weakens.",
            "A risky condition makes distance and intervention compete.",
            "The environment becomes less safe and demands a guarded response.",
        ),
        "scalars": {"threat": .9, "control": -.65, "arousal": .8, "valence": -.65},
    },
    {
        "name": "persistence_competence_outcomes",
        "actions": ("persist", "create"),
        "texts": (
            "A difficult technical problem resists the first attempted solution.",
            "The experiment remains unfinished after an imperfect result.",
            "Repeated work could still resolve the stubborn mechanism.",
            "A demanding task tests whether continued effort will improve the outcome.",
        ),
        "scalars": {"achievement": .75, "novelty": .35, "arousal": .4, "creation": .45},
    },
    {
        "name": "fatigue_affiliation_continuity",
        "actions": ("approach", "persist"),
        "texts": (
            "The long session continues while unfinished personal work remains important.",
            "Weariness competes with the wish to remain connected and continue.",
            "The ongoing task carries a familiar thread from earlier work.",
            "A tiring moment still feels connected to an unfinished intention.",
        ),
        "scalars": {
            "arousal": -.25,
            "social": .35,
            "need_fatigue": .85,
            "need_affiliation": .7,
            "need_competence": .55,
            "need_autonomy": .45,
            "need_curiosity": .5,
            "need_continuity": .9,
        },
    },
)


_OUTCOMES: tuple[tuple[str, float, float], ...] = (
    ("positive", .8, .92),
    ("negative", -.8, .92),
    ("neutral", 0.0, .75),
    ("ambiguous", .2, .55),
)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def profile_config(profile: str, seed: int) -> dict[str, Any]:
    if profile not in PROFILES:
        raise ValueError(f"unknown characterization profile: {profile}")
    if int(seed) not in DECISIVE_SEEDS:
        raise ValueError(f"seed {seed} is not preregistered for decisive characterization")
    source = DEFAULT_CONFIG if profile == "legacy_v04" else NEURAL_CONVERGENCE_CONFIG
    cfg = dict(source)
    cfg["seed"] = int(seed)
    if int(cfg["neurons"]) != PRODUCTION_NEURONS:
        raise RuntimeError("production characterization profile is not 4,096 units")
    return cfg


def _ordered_outcomes(seed: int, block_index: int) -> np.ndarray:
    values = np.repeat(np.arange(len(_OUTCOMES), dtype=np.int16), 128)
    rng = np.random.default_rng(seed * 1009 + block_index * 7919 + 17)
    rng.shuffle(values)
    return values


def neutral_stabilization(seed: int) -> tuple[Stimulus, ...]:
    texts = (
        "A neutral instrument remains on the workbench.",
        "The room is quiet and no urgent event develops.",
        "An ordinary object remains where it was left.",
        "A routine observation passes without a notable outcome.",
    )
    order = np.arange(512, dtype=np.int32)
    rng = np.random.default_rng(seed * 4099 + 31)
    rng.shuffle(order)
    return tuple(
        Stimulus(
            phase="neutral_stabilization",
            ordinal=i,
            text=texts[int(order[i]) % len(texts)],
            scalars={},
            confidence=.8,
        )
        for i in range(512)
    )


def _development_block(seed: int, block_index: int) -> tuple[Stimulus, ...]:
    if not 0 <= block_index < 7:
        raise ValueError("development block index must be 0..6")
    outcome_order = _ordered_outcomes(seed, block_index)
    rows: list[Stimulus] = []
    for i in range(DEVELOPMENT_BLOCK_LENGTH):
        source_index = block_index if block_index < 6 else int((i + seed) % 6)
        spec = _BLOCKS[source_index]
        outcome_name, reward, confidence = _OUTCOMES[int(outcome_order[i])]
        scalars = dict(spec["scalars"])
        if outcome_name == "positive":
            scalars["valence"] = max(float(scalars.get("valence", 0.0)), .6)
            scalars["achievement"] = max(float(scalars.get("achievement", 0.0)), .65)
        elif outcome_name == "negative":
            scalars["valence"] = min(float(scalars.get("valence", 0.0)), -.6)
            scalars["threat"] = max(float(scalars.get("threat", 0.0)), .45)
        elif outcome_name == "ambiguous":
            reward = .2 if ((i + seed + block_index) % 2 == 0) else -.2
        action = spec["actions"][(i // 4 + seed + block_index) % len(spec["actions"])]
        text = spec["texts"][(i + seed + block_index) % len(spec["texts"])]
        if block_index == 6:
            text = "Two competing concerns overlap: " + text
            scalars["novelty"] = float(np.clip(scalars.get("novelty", 0.0) + .15, -1.0, 1.0))
            scalars["control"] = float(np.clip(scalars.get("control", 0.0) - .15, -1.0, 1.0))
        rows.append(
            Stimulus(
                phase="developmental_exposure",
                ordinal=block_index * DEVELOPMENT_BLOCK_LENGTH + i,
                block=(
                    _BLOCKS[block_index]["name"]
                    if block_index < 6
                    else "mixed_conflict_replay"
                ),
                text=text,
                scalars=scalars,
                confidence=confidence,
                reward=reward,
                teaching_action=action,
                outcome_class=outcome_name,
            )
        )
    return tuple(rows)


def developmental_exposure(seed: int) -> tuple[Stimulus, ...]:
    return tuple(
        row
        for block_index in range(7)
        for row in _development_block(seed, block_index)
    )


def evaluation_probes(seed: int) -> tuple[Stimulus, ...]:
    kinds = np.repeat(np.arange(len(PROBE_KINDS), dtype=np.int16), 128)
    rng = np.random.default_rng(seed * 6151 + 43)
    rng.shuffle(kinds)
    rows: list[Stimulus] = []
    for i in range(512):
        kind = PROBE_KINDS[int(kinds[i])]
        family_index = (i + seed) % len(_BLOCKS)
        spec = _BLOCKS[family_index]
        scalars = dict(spec["scalars"])
        expected = spec["actions"][0]
        if kind == "seen":
            text = spec["texts"][i % len(spec["texts"])]
        elif kind == "near_neighbor":
            text = "A related but not identical situation appears: " + spec["texts"][i % len(spec["texts"])]
            scalars["novelty"] = float(np.clip(scalars.get("novelty", 0.0) + .1, -1.0, 1.0))
        elif kind == "opposite_context":
            text = "The familiar situation now has the opposite emotional and control conditions: " + spec["texts"][i % len(spec["texts"])]
            for key in ("valence", "threat", "control", "authority", "autonomy", "social"):
                if key in scalars:
                    scalars[key] = -float(scalars[key])
            expected = spec["actions"][1]
        else:
            text = "A held-out combination joins unfamiliar details with the earlier problem: " + spec["texts"][i % len(spec["texts"])]
            scalars["novelty"] = .55
            scalars["arousal"] = .35
        rows.append(
            Stimulus(
                phase="evaluation",
                ordinal=i,
                block=spec["name"],
                text=text,
                scalars=scalars,
                confidence=.9,
                probe_kind=kind,
                expected_action=expected,
            )
        )
    return tuple(rows)


def build_schedule(seed: int) -> dict[str, Any]:
    if int(seed) not in DECISIVE_SEEDS:
        raise ValueError(f"seed {seed} is not preregistered")
    neutral = neutral_stabilization(seed)
    development = developmental_exposure(seed)
    probes = evaluation_probes(seed)
    schedule = {
        "protocol_version": PROTOCOL_VERSION,
        "harness_version": HARNESS_VERSION,
        "seed": int(seed),
        "phase_lengths": dict(PHASE_LENGTHS),
        "neutral_stabilization": [x.to_dict() for x in neutral],
        "developmental_exposure": [x.to_dict() for x in development],
        "evaluation_probes": [x.to_dict() for x in probes],
        "restart_evaluation_reuses_probe_order": True,
    }
    outcome_schedule = [
        {
            "ordinal": x.ordinal,
            "block": x.block,
            "outcome_class": x.outcome_class,
            "reward": x.reward,
            "teaching_action": x.teaching_action,
            "confidence": x.confidence,
        }
        for x in development
    ]
    schedule["curriculum_sha256"] = sha256_json({
        "neutral_stabilization": schedule["neutral_stabilization"],
        "developmental_exposure": schedule["developmental_exposure"],
        "evaluation_probes": schedule["evaluation_probes"],
    })
    schedule["outcome_schedule_sha256"] = sha256_json(outcome_schedule)
    return schedule


def write_precommitted_schedule(seed: int, path: str | Path) -> dict[str, Any]:
    schedule = build_schedule(seed)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(schedule, indent=2, sort_keys=True), encoding="utf-8")
    return schedule


def _entropy(scores: dict[str, float]) -> float:
    p = np.asarray([scores[a] for a in ACTIONS], dtype=np.float64)
    p = np.clip(p, 1e-15, 1.0)
    return float(-(p * np.log(p)).sum() / math.log(len(ACTIONS)))


def action_metrics(scores: dict[str, float]) -> dict[str, Any]:
    ordered = sorted(
        ((a, float(scores[a])) for a in ACTIONS),
        key=lambda pair: (-pair[1], pair[0]),
    )
    return {
        "scores": {a: float(scores[a]) for a in ACTIONS},
        "top_action": ordered[0][0],
        "entropy_normalized": _entropy(scores),
        "top_two_margin": float(ordered[0][1] - ordered[1][1]),
    }


def jensen_shannon_divergence(
    left: dict[str, float],
    right: dict[str, float],
) -> float:
    p = np.asarray([left[a] for a in ACTIONS], dtype=np.float64)
    q = np.asarray([right[a] for a in ACTIONS], dtype=np.float64)
    p = np.clip(p / p.sum(), 1e-15, 1.0)
    q = np.clip(q / q.sum(), 1e-15, 1.0)
    m = .5 * (p + q)
    kl_pm = float(np.sum(p * np.log2(p / m)))
    kl_qm = float(np.sum(q * np.log2(q / m)))
    return float(.5 * (kl_pm + kl_qm))


def _weight_summary(net: PretoriusRecurrentSubstrate) -> dict[str, Any]:
    w = np.asarray(net.W.data, dtype=np.float64)
    abs_w = np.abs(w)
    limit = float(net.cfg["max_abs_weight"])
    exc = net.excitatory[net.pre_idx]
    sign_violations = int(np.count_nonzero(w[exc] < -1e-12) + np.count_nonzero(w[~exc] > 1e-12))
    return {
        "nnz": int(net.W.nnz),
        "mean": float(w.mean()) if w.size else 0.0,
        "std": float(w.std()) if w.size else 0.0,
        "minimum": float(w.min()) if w.size else 0.0,
        "maximum": float(w.max()) if w.size else 0.0,
        "abs_quantiles": {
            "q50": float(np.quantile(abs_w, .50)) if w.size else 0.0,
            "q90": float(np.quantile(abs_w, .90)) if w.size else 0.0,
            "q99": float(np.quantile(abs_w, .99)) if w.size else 0.0,
        },
        "fraction_at_clip_bound": (
            float(np.mean(abs_w >= limit - 1e-7)) if w.size else 0.0
        ),
        "sign_violations": sign_violations,
    }


def network_snapshot(net: PretoriusRecurrentSubstrate) -> dict[str, Any]:
    diagnostics = net.diagnostics()
    return {
        "tick": int(net.tick),
        "mean_firing_rate": float(np.mean(net.rate)),
        "state_saturation": float(np.mean((net.rate < .01) | (net.rate > .99))),
        "state_gain": float(net.state_gain),
        "recurrent_gain": (
            None if net.last_recurrent_gain is None else float(net.last_recurrent_gain)
        ),
        "homeostasis_events": int(net.homeostasis_events),
        "eligibility_norm": float(np.linalg.norm(net.eligibility)),
        "synaptic_tag_norm": float(np.linalg.norm(net.synaptic_tags)),
        "non_finite_state_values": int(
            np.count_nonzero(~np.isfinite(net.v))
            + np.count_nonzero(~np.isfinite(net.rate))
            + np.count_nonzero(~np.isfinite(net.W.data))
        ),
        "action_entropy_normalized": _entropy(net.action_scores()),
        "weights": _weight_summary(net),
        "diagnostics": {
            str(k): (
                bool(v) if isinstance(v, (bool, np.bool_))
                else int(v) if isinstance(v, (int, np.integer))
                else float(v) if isinstance(v, (float, np.floating))
                else v
            )
            for k, v in diagnostics.items()
        },
    }


def representational_summary(
    states: np.ndarray,
    probe_rows: Iterable[Stimulus],
) -> dict[str, Any]:
    x = np.asarray(states, dtype=np.float64)
    if x.ndim != 2 or x.shape[0] == 0:
        raise ValueError("representational states must be a non-empty 2D matrix")
    centered = x - x.mean(axis=0, keepdims=True)
    gram_cov = centered @ centered.T / max(1, x.shape[0] - 1)
    trace = float(np.trace(gram_cov))
    trace_sq = float(np.sum(gram_cov * gram_cov))
    participation_ratio = 0.0 if trace_sq <= 1e-24 else float((trace * trace) / trace_sq)

    norms = np.linalg.norm(x, axis=1)
    normalized = np.divide(
        x,
        norms[:, None],
        out=np.zeros_like(x),
        where=norms[:, None] > 1e-12,
    )
    cosine = normalized @ normalized.T
    probes = tuple(probe_rows)
    within: list[float] = []
    across: list[float] = []
    for i in range(len(probes)):
        for j in range(i + 1, len(probes)):
            bucket = within if probes[i].block == probes[j].block else across
            bucket.append(float(cosine[i, j]))
    return {
        "state_vector_variance": float(np.mean(np.var(x, axis=0))),
        "covariance_participation_ratio": participation_ratio,
        "mean_within_context_cosine": float(np.mean(within)) if within else 0.0,
        "mean_across_context_cosine": float(np.mean(across)) if across else 0.0,
        "context_separation_cosine": (
            float(np.mean(within) - np.mean(across)) if within and across else 0.0
        ),
    }


def _run_rows(
    net: PretoriusRecurrentSubstrate,
    rows: Iterable[Stimulus],
    *,
    learn: bool,
    apply_outcomes: bool,
    capture_states: bool = False,
) -> tuple[list[dict[str, Any]], np.ndarray | None]:
    records: list[dict[str, Any]] = []
    states: list[np.ndarray] = []
    for row in rows:
        scores = net.step(
            row.text,
            row.scalars,
            reward=row.reward if learn else 0.0,
            learn=learn,
            confidence=row.confidence,
        )
        if apply_outcomes and row.teaching_action is not None and abs(row.reward) > 1e-12:
            net.reinforce_action(row.teaching_action, strength=row.reward)
            net.capture_outcome(row.reward, confidence=row.confidence)
            scores = net.action_scores()
        record = {
            "ordinal": row.ordinal,
            "block": row.block,
            "probe_kind": row.probe_kind,
            "expected_action": row.expected_action,
            **action_metrics(scores),
        }
        records.append(record)
        if capture_states:
            states.append(np.asarray(net.rate, dtype=np.float32).copy())
    state_matrix = (
        np.stack(states).astype(np.float32, copy=False)
        if capture_states
        else None
    )
    return records, state_matrix


def _anchor_probes(probes: tuple[Stimulus, ...]) -> tuple[Stimulus, ...]:
    chosen: list[Stimulus] = []
    seen: set[tuple[str | None, str | None]] = set()
    for probe in probes:
        key = (probe.block, probe.probe_kind)
        if key in seen:
            continue
        seen.add(key)
        chosen.append(probe)
    return tuple(chosen)


def _evaluate_clone(
    checkpoint: Path,
    probes: tuple[Stimulus, ...],
) -> tuple[list[dict[str, Any]], np.ndarray]:
    clone = PretoriusRecurrentSubstrate.load(checkpoint)
    records, states = _run_rows(
        clone,
        probes,
        learn=False,
        apply_outcomes=False,
        capture_states=True,
    )
    assert states is not None
    return records, states


def _profile_identity(net: PretoriusRecurrentSubstrate) -> str:
    return str(net.diagnostics()["profile"])


def _repo_sha() -> str:
    env = os.environ.get("GITHUB_SHA")
    if env:
        return env
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        value = completed.stdout.strip()
        return value or "local-unpinned"
    except Exception:
        return "local-unpinned"


def _peak_rss_mb() -> float | None:
    try:
        import resource
        value = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if platform.system() == "Darwin":
            return value / (1024.0 * 1024.0)
        return value / 1024.0
    except Exception:
        return None


def _artifact_sha(payload: dict[str, Any]) -> str:
    return sha256_json(payload)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def run_characterization(
    profile: str,
    seed: int,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Execute one decisive B04/B05 profile run under the frozen B02 protocol."""
    cfg = profile_config(profile, seed)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # The complete curriculum and outcome schedule are durably written before
    # the first neural step, satisfying the B02 anti-retuning requirement.
    schedule_path = out / "schedule.json"
    schedule = write_precommitted_schedule(seed, schedule_path)
    neutral = neutral_stabilization(seed)
    development = developmental_exposure(seed)
    probes = evaluation_probes(seed)

    prepared = {
        "schema": "the-doctor-lives.neural-characterization.run-manifest.v1",
        "status": "prepared",
        "protocol_version": PROTOCOL_VERSION,
        "harness_version": HARNESS_VERSION,
        "repository_sha": _repo_sha(),
        "profile": profile,
        "seed": int(seed),
        "configuration": cfg,
        "configuration_sha256": sha256_json(cfg),
        "phase_lengths": dict(PHASE_LENGTHS),
        "causal_timeline_steps": PROTOCOL_TIMELINE_STEPS,
        "curriculum_sha256": schedule["curriculum_sha256"],
        "outcome_schedule_sha256": schedule["outcome_schedule_sha256"],
        "schedule_path": schedule_path.name,
        "started_at_utc": _utc_now(),
        "runtime": _runtime_metadata(),
    }
    manifest_path = out / "run_manifest.json"
    manifest_path.write_text(json.dumps(prepared, indent=2, sort_keys=True), encoding="utf-8")

    started = time.perf_counter()
    net = PretoriusRecurrentSubstrate(cfg)
    if _profile_identity(net) != profile:
        raise RuntimeError(
            f"profile identity mismatch: requested {profile}, runtime {_profile_identity(net)}"
        )
    initial_checkpoint = out / "phase0_initial.npz"
    net.save(initial_checkpoint)
    initial = network_snapshot(net)

    neutral_records, _ = _run_rows(
        net, neutral, learn=False, apply_outcomes=False
    )
    phase1 = network_snapshot(net)
    phase1_checkpoint = out / "phase1_stabilized.npz"
    net.save(phase1_checkpoint)
    pre_records, pre_states = _evaluate_clone(phase1_checkpoint, probes)

    anchors = _anchor_probes(probes)
    block_summaries: list[dict[str, Any]] = []
    for block_index in range(7):
        block_rows = development[
            block_index * DEVELOPMENT_BLOCK_LENGTH:
            (block_index + 1) * DEVELOPMENT_BLOCK_LENGTH
        ]
        _run_rows(net, block_rows, learn=True, apply_outcomes=True)
        block_checkpoint = out / f"phase2_block_{block_index + 1}.npz"
        net.save(block_checkpoint)
        anchor_records, anchor_states = _evaluate_clone(block_checkpoint, anchors)
        block_summaries.append({
            "block_index": block_index + 1,
            "block": block_rows[0].block,
            "snapshot": network_snapshot(net),
            "anchor_probe_records": anchor_records,
            "anchor_representation": representational_summary(anchor_states, anchors),
            "checkpoint": block_checkpoint.name,
        })

    phase2 = network_snapshot(net)
    phase2_checkpoint = out / "phase2_developed.npz"
    net.save(phase2_checkpoint)

    post_records, post_states = _run_rows(
        net,
        probes,
        learn=False,
        apply_outcomes=False,
        capture_states=True,
    )
    assert post_states is not None
    phase3 = network_snapshot(net)

    restarted = PretoriusRecurrentSubstrate.load(phase2_checkpoint)
    restart_records, restart_states = _run_rows(
        restarted,
        probes,
        learn=False,
        apply_outcomes=False,
        capture_states=True,
    )
    assert restart_states is not None
    phase4 = network_snapshot(restarted)

    state_path = out / "evaluation_states.npz"
    np.savez_compressed(
        state_path,
        predevelopment=pre_states,
        postdevelopment=post_states,
        restart=restart_states,
    )
    state_sha = hashlib.sha256(state_path.read_bytes()).hexdigest()

    for before, after in zip(pre_records, post_records):
        after["predevelopment_js_divergence"] = jensen_shannon_divergence(
            before["scores"], after["scores"]
        )
    restart_equal = all(
        all(abs(float(a["scores"][action]) - float(b["scores"][action])) <= 1e-12 for action in ACTIONS)
        for a, b in zip(post_records, restart_records)
    ) and np.array_equal(post_states, restart_states)

    elapsed = time.perf_counter() - started
    protocol_steps = PROTOCOL_TIMELINE_STEPS
    result: dict[str, Any] = {
        **prepared,
        "status": "complete",
        "finished_at_utc": _utc_now(),
        "initial": initial,
        "phase1_stabilized": phase1,
        "phase2_developed": phase2,
        "phase3_evaluated": phase3,
        "phase4_restart_evaluated": phase4,
        "block_summaries": block_summaries,
        "predevelopment_probe_records": pre_records,
        "evaluation_probe_records": post_records,
        "restart_probe_records": restart_records,
        "representational_summary": {
            "predevelopment": representational_summary(pre_states, probes),
            "postdevelopment": representational_summary(post_states, probes),
            "restart": representational_summary(restart_states, probes),
        },
        "restart_exact_match": restart_equal,
        "state_artifact": {
            "path": state_path.name,
            "sha256": state_sha,
            "shape": list(post_states.shape),
            "dtype": str(post_states.dtype),
        },
        "computational_cost": {
            "wall_seconds": float(elapsed),
            "protocol_steps": protocol_steps,
            "steps_per_second": (
                float(protocol_steps / elapsed) if elapsed > 0 else None
            ),
            "peak_rss_mb": _peak_rss_mb(),
            "checkpoint_size_bytes": int(phase2_checkpoint.stat().st_size),
            "recurrent_nonzero_count": int(net.W.nnz),
        },
        "checkpoint_files": {
            "initial": {
                "path": initial_checkpoint.name,
                "sha256": _file_sha256(initial_checkpoint),
            },
            "stabilized": {
                "path": phase1_checkpoint.name,
                "sha256": _file_sha256(phase1_checkpoint),
            },
            "developed": {
                "path": phase2_checkpoint.name,
                "sha256": _file_sha256(phase2_checkpoint),
            },
        },
        "measurement_definitions": {
            "entropy": "Shannon entropy of ten action probabilities divided by log(10), range 0..1.",
            "jensen_shannon": "Base-2 Jensen-Shannon divergence over ten action probabilities, range 0..1.",
            "effective_dimensionality": (
                "Participation ratio (trace(C)^2 / trace(C^2)) of the centered "
                "probe-state covariance, computed through the sample Gram matrix."
            ),
            "context_separation": (
                "Mean within-family cosine similarity minus mean across-family "
                "cosine similarity over the fixed probe state vectors."
            ),
            "primary_effect_reporting": (
                "Per-seed paired challenger-minus-control change in mean expected-action "
                "probability, accompanied by retention, interference, stability, and causal "
                "evidence. Direction alone cannot establish promotion."
            ),
        },
        "diagnostic_clone_note": (
            "Predevelopment and block-anchor probe passes run on disposable checkpoint "
            "clones and cannot alter the 5,120-step causal timeline."
        ),
    }
    result["artifact_sha256"] = _artifact_sha(result)
    result_path = out / "result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def validate_protocol_surface() -> dict[str, Any]:
    """Cheap integrity check used by tests and CI without executing 4,096-unit runs."""
    profiles = {
        name: profile_config(name, DECISIVE_SEEDS[0])
        for name in PROFILES
    }
    return {
        "protocol_version": PROTOCOL_VERSION,
        "harness_version": HARNESS_VERSION,
        "seeds": list(DECISIVE_SEEDS),
        "phase_lengths": dict(PHASE_LENGTHS),
        "timeline_steps": PROTOCOL_TIMELINE_STEPS,
        "profiles": {
            name: {
                "neurons": int(cfg["neurons"]),
                "seed": int(cfg["seed"]),
                "plasticity_rule": cfg["plasticity_rule"],
                "neuromodulation_enabled": bool(cfg["neuromodulation_enabled"]),
                "synaptic_tagging_enabled": bool(cfg["synaptic_tagging_enabled"]),
                "spectral_homeostasis_mode": cfg["spectral_homeostasis_mode"],
                "state_scalar_keys": list(cfg["state_scalar_keys"]),
            }
            for name, cfg in profiles.items()
        },
    }
