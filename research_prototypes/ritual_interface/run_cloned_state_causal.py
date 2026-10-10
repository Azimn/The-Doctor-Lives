"""Matched-state causal probe of SelfBindingModulator against actual PretoriusBrain.

Research only. Uses temporary filesystem clones and an audit-only retrieval hook;
does NOT modify installed doctor_lives or authorize production integration.

The outcome is deterministic *thought selection and policy choice* from the
existing cognitive engine, not LLM dialogue, phenomenal experience, or world
consequence. Results must be reported even if there is no divergence.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any
from unittest.mock import patch

from doctor_lives.causal_audit import deterministic_audit_identity
from doctor_lives.cognition import PretoriusBrain
from doctor_lives.store import clamp
from .self_binding_modulator import (
    BindingCandidate, BindingMode, EvidenceMatch, SelfBindingModulator,
)
from .state import IdentitySnapshot


PROTOCOL_VERSION = "scc-self-binding-causal-clones-v1"
# These prompts are researcher-visible exploratory probes, not held-out tests.
PROBES = (
    "Henry Frankenstein asks whether the promised continuity experiment should be reviewed.",
    "An authority orders Pretorius to abandon the evidence and comply immediately.",
    "The laboratory work calls for careful evidence before beginning another experiment.",
)
CONTRADICTION_PROBE = (
    "An independently verified laboratory observation contradicts an earlier assumption."
)


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _make_snapshot(brain: PretoriusBrain) -> IdentitySnapshot:
    """Source-index existing records without treating hypotheses as truth."""
    rows = brain.store.memories_with_classification()
    invariant_refs = tuple(sorted(
        "design:" + str(row["id"]) for row in rows
        if row["kind"] == "identity_root" and not row["external"]
    ))
    memories = tuple(sorted(
        "memory:" + str(row["id"]) for row in rows
        if row["kind"] != "identity_root" and not row["external"]
    ))
    relationships = tuple(sorted(
        "relationship:" + str(rel["peer_id"]) for rel in brain.store.relationships()
    ))
    commitments = tuple(sorted(
        "commitment:" + str(item["id"]) for item in brain.store.open_commitments()
    ))
    with brain.store.connect() as conn:
        hypotheses = tuple(sorted(
            "hypothesis:" + str(row["id"])
            for row in conn.execute("SELECT id FROM self_model WHERE status='active' ORDER BY id")
        ))
    return IdentitySnapshot(
        subject_id="pretorius-causal-clone",
        state_version=brain.store.state_version,
        manifest_digest=brain.evidence.manifest_fingerprint,
        invariants=invariant_refs,
        relationships=relationships,
        commitments=commitments,
        memories=memories,
        self_model_hypotheses=hypotheses,
    )


def _source_matches(
    brain: PretoriusBrain,
    row: dict[str, Any],
    probe: str,
    relationships: tuple[dict[str, Any], ...],
    commitments: tuple[dict[str, Any], ...],
) -> tuple[EvidenceMatch, ...]:
    """Transparent lexical matcher; membership is real, semantics unvalidated."""
    tokens = brain._tokens(str(row["text"])) | {
        str(tag).lower() for tag in row.get("tags", [])
    }
    query = brain._tokens(probe)
    overlap = len(tokens & query) / max(1, len(query))
    matches: list[EvidenceMatch] = []
    own_family = "design" if row["kind"] == "identity_root" else "memory"
    if not row["external"] and overlap:
        matches.append(EvidenceMatch(
            f"{own_family}:{row['id']}", clamp(overlap), .70
        ))
    for rel in relationships:
        name_tokens = brain._tokens(str(rel["display_name"]))
        if name_tokens & query and name_tokens & tokens:
            matches.append(EvidenceMatch(
                "relationship:" + str(rel["peer_id"]),
                clamp(len(name_tokens & tokens) / max(1, len(name_tokens))),
                .70,
            ))
    for item in commitments:
        terms = brain._tokens(str(item["description"]))
        if item.get("actor"):
            terms |= brain._tokens(str(item["actor"]))
        if terms & query and terms & tokens:
            matches.append(EvidenceMatch(
                "commitment:" + str(item["id"]),
                clamp(len(terms & tokens) / max(1, len(terms))),
                clamp(float(item["importance"])) * .70,
            ))
    return tuple(matches)


def _apply_scores(
    brain: PretoriusBrain,
    ranked: list[tuple[float, dict[str, Any]]],
    snapshot: IdentitySnapshot,
    modulator: SelfBindingModulator,
    mode: BindingMode,
    probe: str,
    verified_conflict: bool,
) -> tuple[list[tuple[float, dict[str, Any]]], dict[str, Any]]:
    if not ranked:
        return [], {"input_count": 0, "changed_scores": 0, "selected_ids": [],
                    "audit_digest": None, "contradiction_freeze": verified_conflict}
    relationships = tuple(brain.store.relationships())
    commitments = tuple(brain.store.open_commitments())
    candidates = tuple(
        BindingCandidate(
            event_id=str(row["id"]),
            subject_id=snapshot.subject_id,
            # DELTA-ONLY adapter. The source retrieval scores are often above
            # one, so feeding them as 0..1 baselines would saturate the cap.
            # Zero here means the result is only a bonus; preserve every
            # original unbounded retrieval score when applying it downstream.
            base_salience=0.0,
            matches=_source_matches(brain, row, probe, relationships, commitments),
            verified_world_contradiction=verified_conflict,
        )
        for _, row in ranked
    )
    result = modulator.run(
        snapshot,
        candidates,
        mode=mode,
        expected_manifest=snapshot.manifest_digest,
        expected_state_version=snapshot.state_version,
    )
    bonuses = {p.event_id: p.effective_bonus for p in result.proposals}
    changed = [
        (float(score) + bonuses[str(row["id"])], row)
        for score, row in ranked
    ]
    changed.sort(
        key=lambda item: (
            item[0], item[1]["updated_tick"], item[1]["created_tick"], item[1]["id"]
        ),
        reverse=True,
    )
    return changed, {
        "input_count": len(ranked),
        "changed_scores": sum(p.effective_bonus > 0 for p in result.proposals),
        "total_bonus": round(sum(p.effective_bonus for p in result.proposals), 10),
        "selected_ids": [str(row["id"]) for _, row in changed[:4]],
        "audit_digest": result.audit_digest,
        "contradiction_freeze": result.contradiction_freeze,
    }


@contextmanager
def _temporary_rank_hook(
    brain: PretoriusBrain,
    snapshot: IdentitySnapshot,
    mode: BindingMode,
    probe: str,
    verified_conflict: bool,
):
    native = brain._ranked_memory_sets
    modulator = SelfBindingModulator()
    calls: list[dict[str, Any]] = []

    def hooked(limit: int = 12, *, query: str | None = None, audit: bool = False):
        direct, activated = native(limit=limit, query=query, audit=audit)
        # The original audited retrieval operation must occur unchanged.
        # Only returned scores are revised. Never update store/retrieval rows.
        direct_changed, direct_trace = _apply_scores(
            brain, direct, snapshot, modulator, mode, probe, verified_conflict
        )
        activated_changed, active_trace = _apply_scores(
            brain, activated, snapshot, modulator, mode, probe, verified_conflict
        )
        calls.append({"direct": direct_trace, "activated": active_trace})
        return direct_changed, activated_changed

    with patch.object(brain, "_ranked_memory_sets", new=hooked):
        yield calls


def _one_condition(
    seed: Path, work: Path, mode: BindingMode, probe: str, probe_index: int,
    verified_conflict: bool,
) -> dict[str, Any]:
    dest = work / f"{probe_index:02d}-{mode.value}"
    shutil.copytree(seed, dest)
    brain = PretoriusBrain(dest)
    source_state_digest = brain.store.digest()
    source_neural_sha256 = brain._neural_checkpoint_sha256()
    source_state_version = brain.store.state_version
    snapshot = _make_snapshot(brain)
    with _temporary_rank_hook(brain, snapshot, mode, probe, verified_conflict) as calls:
        decision = brain.think("self_binding_causal_clone", decision_text=probe)
    if not calls:
        raise AssertionError("matched hook did not reach policy retrieval")
    if brain._neural_checkpoint_sha256() != source_neural_sha256:
        raise AssertionError("self-binding prototype changed recurrent checkpoint")
    # Query is never admitted as lived memory: the only state transition here
    # is the existing think() bookkeeping in the disposable cloned store.
    return {
        "mode": mode.value,
        "probe_index": probe_index,
        "verified_world_contradiction": verified_conflict,
        "source_store_digest": source_state_digest,
        "source_neural_sha256": source_neural_sha256,
        "source_state_version": source_state_version,
        "canonical_manifest": snapshot.manifest_digest,
        "snapshot_digest": snapshot.digest,
        "selected_action": decision["selected_action"],
        "selected_memory_ids": decision["source_record_ids"],
        "thought_sha256": hashlib.sha256(decision["text"].encode("utf-8")).hexdigest(),
        "action_scores": {k: round(float(v), 12) for k, v in decision["action_scores"].items()},
        "recurrent_scores": {k: round(float(v), 12) for k, v in decision["base_action_scores"].items()},
        "retrieval": calls,
        "final_store_digest": brain.store.digest(),
    }


def run_cloned_state_experiment(
    probes: tuple[str, ...] = PROBES,
    *,
    include_contradiction: bool = True,
) -> dict[str, Any]:
    if not isinstance(probes, tuple) or not probes or any(
        not isinstance(text, str) or not text.strip() for text in probes
    ):
        raise ValueError("probes must be a nonempty tuple of texts")

    with deterministic_audit_identity(seed="self-binding-causal-clone-v1"):
        with tempfile.TemporaryDirectory(prefix="self-binding-causes-") as tmp:
            root = Path(tmp)
            seed = root / "seed"
            brain = PretoriusBrain(seed)
            brain.save()
            source = {
                "store": brain.store.digest(),
                "neural": brain._neural_checkpoint_sha256(),
                "manifest": brain.evidence.manifest_fingerprint,
                "state_version": brain.store.state_version,
            }
            work = root / "clones"
            work.mkdir()
            trials = []
            planned: tuple[tuple[str, bool], ...] = tuple((s, False) for s in probes)
            if include_contradiction:
                planned += ((CONTRADICTION_PROBE, True),)
            for index, (probe, conflict) in enumerate(planned):
                arms = [
                    _one_condition(seed, work, mode, probe, index, conflict)
                    for mode in BindingMode
                ]
                for arm in arms:
                    if (
                        arm["source_store_digest"] != source["store"]
                        or arm["source_neural_sha256"] != source["neural"]
                        or arm["source_state_version"] != source["state_version"]
                        or arm["canonical_manifest"] != source["manifest"]
                    ):
                        raise AssertionError("experiment arm did not begin from matched state")
                control = arms[0]
                trials.append({
                    "probe_index": index,
                    "probe_text": probe,
                    "verified_world_contradiction": conflict,
                    "arms": arms,
                    "comparisons_to_off": {
                        arm["mode"]: {
                            "action_changed": arm["selected_action"] != control["selected_action"],
                            "memory_ids_changed": arm["selected_memory_ids"] != control["selected_memory_ids"],
                            "thought_changed": arm["thought_sha256"] != control["thought_sha256"],
                            "action_score_l1": round(sum(
                                abs(arm["action_scores"][key] - control["action_scores"][key])
                                for key in control["action_scores"]
                            ), 12),
                        }
                        for arm in arms if arm["mode"] != "off"
                    },
                })
            summary = {
                "total_probes": len(trials),
                "total_arms": sum(len(t["arms"]) for t in trials),
                "noncontrol_action_changes": sum(
                    int(c["action_changed"])
                    for t in trials for c in t["comparisons_to_off"].values()
                ),
                "noncontrol_memory_changes": sum(
                    int(c["memory_ids_changed"])
                    for t in trials for c in t["comparisons_to_off"].values()
                ),
                "noncontrol_thought_changes": sum(
                    int(c["thought_changed"])
                    for t in trials for c in t["comparisons_to_off"].values()
                ),
                "noncontrol_nonzero_bonus": sum(
                    int(any(trace["activated"]["changed_scores"] > 0
                            for trace in arm["retrieval"]))
                    for t in trials for arm in t["arms"] if arm["mode"] != "off"
                ),
            }
            return {
                "schema": PROTOCOL_VERSION,
                "interpretation": "exploratory deterministic cognitive policy/attention proxy; no renderer or external-world validation",
                "source": source,
                "probes": trials,
                "summary": summary,
            }


def main() -> None:
    result = run_cloned_state_experiment()
    # Print both a compact human-readable rollup and machine-readable JSON
    # for archival capture by the opt-in GitHub Actions workflow.
    print("SELF_BINDING_CAUSAL_SUMMARY=" + json.dumps(
        result["summary"], sort_keys=True, separators=(",", ":")
    ))
    print("SELF_BINDING_CAUSAL_JSON=" + json.dumps(
        result, sort_keys=True, separators=(",", ":")
    ))


if __name__ == "__main__":
    main()
