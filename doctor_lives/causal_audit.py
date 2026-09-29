from __future__ import annotations

import hashlib
import json
import re
import shutil
from contextlib import ExitStack, closing, contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

from .cognition import PretoriusBrain
from .models import Experience


AUDIT_MECHANISMS = frozenset({
    "deep_history",
    "needs",
    "relationships",
    "commitments",
    "concerns",
    "recurrent_policy",
    "spreading_activation",
    "action_values",
    "self_model",
})


@dataclass(frozen=True)
class AuditIntervention:
    """Audit-only lesion declaration.

    Interventions are applied only to cloned state directories. They are never
    persisted back into the source brain and are not a production control API.
    """

    name: str
    disable: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        unknown = sorted(set(self.disable) - AUDIT_MECHANISMS)
        if unknown:
            raise ValueError(f"unknown causal-audit mechanisms: {unknown!r}")
        if not self.name.strip():
            raise ValueError("audit intervention name is required")


def _stable_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _behavioral_request_payload(render_request: dict[str, Any]) -> dict[str, Any]:
    """Remove identity/timestamp bookkeeping that differs across matched clones.

    Random record/event UUIDs are provenance handles, not behavioral content.
    The raw request is still retained in every trace.
    """
    normalized = json.loads(json.dumps(render_request, sort_keys=True, default=str))
    metadata = normalized.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("private_state_version", None)
        epistemic = metadata.get("epistemic_items")
        if isinstance(epistemic, list):
            for item in epistemic:
                if isinstance(item, dict):
                    item.pop("record_id", None)

    relationships = normalized.get("relationship_context")
    if isinstance(relationships, list):
        for rel in relationships:
            if isinstance(rel, dict):
                evidence = rel.pop("evidence", None)
                if isinstance(evidence, list):
                    rel["evidence_count"] = len(evidence)

    unresolved = normalized.get("unresolved_context")
    if isinstance(unresolved, list):
        for item in unresolved:
            if isinstance(item, dict):
                item.pop("id", None)
                item.pop("source_event_id", None)

    return normalized


def _behavioral_request_sha256(render_request: dict[str, Any]) -> str:
    """Fingerprint semantic renderer-visible content, excluding clone UUID noise."""
    return _stable_sha256(_behavioral_request_payload(render_request))


def deterministic_audit_render(
    render_request: dict[str, Any],
    selected_action: str,
) -> dict[str, str]:
    """Pure measurement renderer.

    This deliberately simple projection is not Pretorius's language renderer.
    It exists so audit conditions can compare a deterministic downstream
    observable without allowing a renderer to mutate or reinterpret brain state.
    """
    normalized = _behavioral_request_payload(render_request)
    payload = {
        "selected_action": selected_action,
        "first_person_context": list(normalized.get("first_person_context", ()))[:4],
        "felt_state": dict(normalized.get("metadata", {}).get("felt_state", {})),
        "relationship_context": list(normalized.get("relationship_context", ())),
        "unresolved_context": list(normalized.get("unresolved_context", ()))[:6],
        "provenance_summary": dict(normalized.get("provenance_summary", {})),
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return {"text": text, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}


class CausalAuditHarness:
    """Matched-state causal characterization for the existing Pretorius brain."""

    def __init__(self, seed_state_dir: str | Path, work_dir: str | Path):
        self.seed_state_dir = Path(seed_state_dir)
        self.work_dir = Path(work_dir)
        if not self.seed_state_dir.exists():
            raise FileNotFoundError(self.seed_state_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self._counter = 0

    def _clone_seed(self, label: str) -> Path:
        self._counter += 1
        slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") or "condition"
        destination = self.work_dir / f"{self._counter:03d}-{slug}"
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(self.seed_state_dir, destination)
        return destination

    @staticmethod
    def _neural_sha(brain: PretoriusBrain) -> str:
        brain.save()
        return brain._neural_checkpoint_sha256()

    @staticmethod
    def _state_snapshot(brain: PretoriusBrain) -> dict[str, Any]:
        with closing(brain.store.connect()) as conn:
            needs = {
                str(row["key"]): {
                    "actual": float(row["actual"]),
                    "felt": float(row["felt"]),
                }
                for row in conn.execute(
                    "SELECT key,actual,felt FROM needs ORDER BY key"
                ).fetchall()
            }
            action_values = {
                str(row["action"]): {
                    "value": float(row["value"]),
                    "uses": int(row["uses"]),
                    "successes": int(row["successes"]),
                }
                for row in conn.execute(
                    "SELECT action,value,uses,successes FROM action_values ORDER BY action"
                ).fetchall()
            }
            self_model = [
                dict(row) for row in conn.execute(
                    "SELECT * FROM self_model ORDER BY id"
                ).fetchall()
            ]
        return {
            "felt_state": brain._felt_state(),
            "needs": needs,
            "relationships": brain.store.relationships(),
            "concerns": brain.store.open_concerns(),
            "commitments": brain.store.open_commitments(),
            "action_values": action_values,
            "self_model": self_model,
        }

    @staticmethod
    def _memory_signature_map(brain: PretoriusBrain) -> dict[str, str]:
        """Map runtime UUIDs to stable semantic memory signatures for matched comparisons."""
        out: dict[str, str] = {}
        for row in brain.store.memories_with_classification(active_only=False):
            payload = {
                "created_tick": int(row["created_tick"]),
                "kind": str(row["kind"]),
                "text": str(row["text"]),
                "source": str(row["source"]),
                "evidence_class": str(row["evidence_class"]),
                "external": bool(row["external"]),
                "authored": bool(row["authored"]),
                "tags": sorted(str(x) for x in row.get("tags", [])),
                "autobiographical_class": row.get("autobiographical_class"),
                "event_subtype": row.get("event_subtype"),
                "canon_rank": row.get("canon_rank"),
                "continuity": row.get("continuity"),
                "material_category": row.get("material_category"),
                "wording": row.get("wording"),
            }
            out[str(row["id"])] = _stable_sha256(payload)
        return out

    @staticmethod
    def _decode_policy_decision(brain: PretoriusBrain, decision_id: str) -> dict[str, Any]:
        with closing(brain.store.connect()) as conn:
            row = conn.execute(
                "SELECT * FROM policy_decisions WHERE id=?", (decision_id,)
            ).fetchone()
        if row is None:
            raise RuntimeError(f"missing policy decision {decision_id}")
        out = dict(row)
        out["action_scores"] = json.loads(out.pop("action_scores_json"))
        out["candidate_record_ids"] = json.loads(out.pop("candidate_record_ids_json"))
        out["selected_record_ids"] = json.loads(out.pop("selected_record_ids_json"))
        return out

    @staticmethod
    def _latest_retrieval_audit(brain: PretoriusBrain) -> dict[str, Any]:
        with closing(brain.store.connect()) as conn:
            row = conn.execute(
                "SELECT * FROM retrieval_audits ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        if row is None:
            return {}
        out = dict(row)
        for source, target in (
            ("config_json", "config"),
            ("direct_memory_ids_json", "direct_memory_ids"),
            ("activated_memory_ids_json", "activated_memory_ids"),
            ("path_contributions_json", "path_contributions"),
            ("ranked_memory_ids_json", "ranked_memory_ids"),
        ):
            out[target] = json.loads(out.pop(source))
        return out

    @staticmethod
    def _apply_static_lesions(brain: PretoriusBrain, disabled: set[str]) -> None:
        db_mutated = False
        with brain.store.transaction() as conn:
            if "deep_history" in disabled:
                conn.execute(
                    """UPDATE memories SET active=0
                    WHERE id IN (SELECT memory_id FROM memory_provenance)"""
                )
                db_mutated = True
            if "needs" in disabled:
                conn.execute("UPDATE needs SET actual=0.5,felt=0.5")
                db_mutated = True
            if "relationships" in disabled:
                conn.execute("DELETE FROM relationship_events")
                conn.execute("DELETE FROM relationships")
                db_mutated = True
            if "commitments" in disabled:
                conn.execute(
                    """UPDATE commitments
                    SET status='released',outcome='causal_audit_lesion' 
                    WHERE status IN ('open','overdue')"""
                )
                db_mutated = True
            if "concerns" in disabled:
                conn.execute(
                    "UPDATE concerns SET status='audit_lesioned' WHERE status='open'"
                )
                db_mutated = True
            if "spreading_activation" in disabled:
                conn.execute("DELETE FROM history_edges")
                db_mutated = True
            if "action_values" in disabled:
                conn.execute(
                    "UPDATE action_values SET value=0.5,uses=0,successes=0"
                )
                db_mutated = True
            if "self_model" in disabled:
                conn.execute("DELETE FROM self_model")
                db_mutated = True
            if db_mutated:
                brain.store.bump_state_version(conn)

        if "recurrent_policy" in disabled:
            brain.neural.motor_w.fill(0.0)
            brain.neural.motor_b.fill(0.0)
            brain.save()

    @staticmethod
    @contextmanager
    def _runtime_patches(brain: PretoriusBrain, disabled: set[str]):
        with ExitStack() as stack:
            if "needs" in disabled:
                stack.enter_context(
                    patch.object(brain, "_update_needs", lambda conn, tick, exp: None)
                )
            if "relationships" in disabled:
                stack.enter_context(
                    patch.object(brain, "_update_relationship", lambda conn, tick, exp, event_id: None)
                )
            if "concerns" in disabled:
                stack.enter_context(
                    patch.object(brain, "_maybe_add_concern", lambda conn, tick, exp: None)
                )
            yield

    def _run_condition(
        self,
        stimulus: Experience,
        intervention: AuditIntervention,
        *,
        prelude: Callable[[PretoriusBrain], None] | None = None,
    ) -> dict[str, Any]:
        clone = self._clone_seed(intervention.name)
        brain = PretoriusBrain(clone)

        source_state_digest = brain.store.digest()
        source_neural_sha256 = self._neural_sha(brain)
        disabled = set(intervention.disable)
        self._apply_static_lesions(brain, disabled)

        if prelude is not None:
            prelude(brain)

        condition_state_digest = brain.store.digest()
        condition_neural_sha256 = self._neural_sha(brain)
        before = self._state_snapshot(brain)

        with self._runtime_patches(brain, disabled):
            ingestion = brain.ingest(stimulus)
            spontaneous = ingestion["thought"] is not None
            decision = (
                ingestion["thought"]
                if ingestion["thought"] is not None
                else brain.think("causal_audit_forced")
            )

        request = brain.render_request(stimulus.text).to_dict()
        retrieval = self._latest_retrieval_audit(brain)
        policy = self._decode_policy_decision(brain, decision["policy_decision_id"])
        signatures = self._memory_signature_map(brain)
        policy["candidate_memory_signatures"] = [
            signatures.get(str(record_id), f"missing:{record_id}")
            for record_id in policy["candidate_record_ids"]
        ]
        policy["selected_memory_signatures"] = [
            signatures.get(str(record_id), f"missing:{record_id}")
            for record_id in policy["selected_record_ids"]
        ]
        for id_key, signature_key in (
            ("direct_memory_ids", "direct_memory_signatures"),
            ("activated_memory_ids", "activated_memory_signatures"),
            ("ranked_memory_ids", "ranked_memory_signatures"),
        ):
            if id_key in retrieval:
                retrieval[signature_key] = [
                    signatures.get(str(record_id), f"missing:{record_id}")
                    for record_id in retrieval[id_key]
                ]
        after = self._state_snapshot(brain)
        final_state_digest = brain.store.digest()
        final_neural_sha256 = self._neural_sha(brain)
        audit_render = deterministic_audit_render(request, str(policy["selected_action"]))

        return {
            "schema": "the-doctor-lives.causal-trace.v1",
            "condition": intervention.name,
            "disabled_mechanisms": sorted(disabled),
            "source_state_digest": source_state_digest,
            "source_neural_sha256": source_neural_sha256,
            "condition_state_digest": condition_state_digest,
            "condition_neural_sha256": condition_neural_sha256,
            "stimulus": asdict(stimulus),
            "spontaneous_cognition": spontaneous,
            "ingestion": ingestion,
            "policy_decision": policy,
            "retrieval": retrieval,
            "renderer_request": request,
            "renderer_request_sha256": _stable_sha256(request),
            "renderer_request_behavior_sha256": _behavioral_request_sha256(request),
            "deterministic_audit_render": audit_render,
            "state_before_stimulus": before,
            "state_after_stimulus": after,
            "final_state_digest": final_state_digest,
            "final_neural_sha256": final_neural_sha256,
        }

    @staticmethod
    def compare_traces(intact: dict[str, Any], lesion: dict[str, Any]) -> dict[str, Any]:
        a_scores = intact["policy_decision"]["action_scores"]
        b_scores = lesion["policy_decision"]["action_scores"]
        keys = sorted(set(a_scores) | set(b_scores))
        score_l1 = sum(abs(float(a_scores.get(k, 0.0)) - float(b_scores.get(k, 0.0))) for k in keys)

        a_retrieved = set(
            intact.get("retrieval", {}).get(
                "ranked_memory_signatures",
                intact.get("retrieval", {}).get("ranked_memory_ids", []),
            )
        )
        b_retrieved = set(
            lesion.get("retrieval", {}).get(
                "ranked_memory_signatures",
                lesion.get("retrieval", {}).get("ranked_memory_ids", []),
            )
        )
        union = a_retrieved | b_retrieved
        retrieval_jaccard = 1.0 if not union else len(a_retrieved & b_retrieved) / len(union)

        a_selected = set(
            intact["policy_decision"].get(
                "selected_memory_signatures",
                intact["policy_decision"]["selected_record_ids"],
            )
        )
        b_selected = set(
            lesion["policy_decision"].get(
                "selected_memory_signatures",
                lesion["policy_decision"]["selected_record_ids"],
            )
        )
        selected_union = a_selected | b_selected
        selected_jaccard = (
            1.0 if not selected_union
            else len(a_selected & b_selected) / len(selected_union)
        )

        return {
            "selected_action_diverged": (
                intact["policy_decision"]["selected_action"]
                != lesion["policy_decision"]["selected_action"]
            ),
            "action_score_l1": score_l1,
            "retrieval_jaccard": retrieval_jaccard,
            "selected_memory_jaccard": selected_jaccard,
            "renderer_request_changed": (
                intact["renderer_request_behavior_sha256"]
                != lesion["renderer_request_behavior_sha256"]
            ),
            "renderer_request_raw_changed": (
                intact["renderer_request_sha256"] != lesion["renderer_request_sha256"]
            ),
            "deterministic_render_changed": (
                intact["deterministic_audit_render"]["sha256"]
                != lesion["deterministic_audit_render"]["sha256"]
            ),
            "spontaneous_cognition_diverged": (
                intact["spontaneous_cognition"] != lesion["spontaneous_cognition"]
            ),
        }

    def run_pair(
        self,
        stimulus: Experience,
        intervention: AuditIntervention,
    ) -> dict[str, Any]:
        intact = self._run_condition(
            stimulus,
            AuditIntervention(name=f"{intervention.name}:intact"),
        )
        lesion = self._run_condition(stimulus, intervention)
        if intact["source_state_digest"] != lesion["source_state_digest"]:
            raise AssertionError("matched causal pair did not begin from identical source store state")
        if intact["source_neural_sha256"] != lesion["source_neural_sha256"]:
            raise AssertionError("matched causal pair did not begin from identical neural checkpoint")
        return {
            "schema": "the-doctor-lives.causal-pair.v1",
            "mechanism": intervention.name,
            "intact": intact,
            "lesion": lesion,
            "comparison": self.compare_traces(intact, lesion),
        }

    def run_sleep_pair(self, stimulus: Experience, *, sleep_ticks: int = 8) -> dict[str, Any]:
        def with_sleep(brain: PretoriusBrain) -> None:
            brain.sleep(sleep_ticks)

        intact = self._run_condition(
            stimulus,
            AuditIntervention(name="sleep_replay:intact"),
            prelude=with_sleep,
        )
        absent = self._run_condition(
            stimulus,
            AuditIntervention(name="sleep_replay:absent"),
        )
        return {
            "schema": "the-doctor-lives.causal-pair.v1",
            "mechanism": "sleep_replay",
            "intact": intact,
            "lesion": absent,
            "comparison": self.compare_traces(intact, absent),
            "sleep_ticks": int(sleep_ticks),
        }

    def run_reinforcement_triplet(
        self,
        stimulus: Experience,
        *,
        action: str = "create",
        success: bool = True,
        reward: float = 1.0,
        repetitions: int = 4,
    ) -> dict[str, Any]:
        def intact_prelude(brain: PretoriusBrain) -> None:
            for _ in range(repetitions):
                brain.record_action_outcome(action, success, reward)

        def no_neural_reinforcement(brain: PretoriusBrain) -> None:
            with patch.object(brain.neural, "reinforce_action", lambda action, strength=1.0: None):
                for _ in range(repetitions):
                    brain.record_action_outcome(action, success, reward)

        def neutral_action_values(brain: PretoriusBrain) -> None:
            intact_prelude(brain)
            with brain.store.transaction() as conn:
                conn.execute(
                    "UPDATE action_values SET value=0.5,uses=0,successes=0"
                )
                brain.store.bump_state_version(conn)

        intact = self._run_condition(
            stimulus,
            AuditIntervention(name="reinforcement:intact"),
            prelude=intact_prelude,
        )
        no_neural = self._run_condition(
            stimulus,
            AuditIntervention(name="reinforcement:no_neural"),
            prelude=no_neural_reinforcement,
        )
        neutral_values = self._run_condition(
            stimulus,
            AuditIntervention(name="reinforcement:neutral_action_values"),
            prelude=neutral_action_values,
        )
        return {
            "schema": "the-doctor-lives.reinforcement-audit.v1",
            "action": action,
            "success": bool(success),
            "reward": float(reward),
            "repetitions": int(repetitions),
            "intact": intact,
            "no_neural_reinforcement": no_neural,
            "neutral_action_values": neutral_values,
            "intact_vs_no_neural": self.compare_traces(intact, no_neural),
            "intact_vs_neutral_action_values": self.compare_traces(intact, neutral_values),
        }

    def characterize_concern_accumulation(
        self,
        *,
        distinct_pressures: int = 4,
        heartbeat_ticks: int = 3,
    ) -> dict[str, Any]:
        clone = self._clone_seed("concern-accumulation")
        brain = PretoriusBrain(clone)
        before = len(brain.store.open_concerns())
        pressure_texts = (
            "A customs officer seizes the galvanic coils at the border.",
            "The cellar landlord padlocks access to the underground laboratory.",
            "A journal editor threatens disclosure of a private specimen.",
            "A creditor impounds the microscope and combustion apparatus.",
            "An intruder destroys the reagent ledger and removes the keys.",
            "A municipal inspector orders the animal room sealed immediately.",
            "A supplier withholds the final catalyst unless control is surrendered.",
            "A rival scientist demands exclusive ownership of the apparatus plans.",
        )
        for index in range(distinct_pressures):
            text = pressure_texts[index % len(pressure_texts)] + f" Incident {index}."
            brain.ingest(Experience(
                text=text,
                kind="social",
                actor=f"Pressure Source {index}",
                valence=-0.7,
                arousal=0.8,
                authority=0.95,
                autonomy=0.0,
                threat=0.85,
                control=-0.8,
                tags=("causal_audit", f"pressure_{index}"),
            ))
        after_pressures = len(brain.store.open_concerns())
        neutral_probe = Experience("The laboratory is quiet and no new event occurs.")
        neutral_warrants_cognition = brain._warrants_cognition(neutral_probe)
        thought_count_before = len(brain.store.thoughts(100000))
        heartbeat = brain.heartbeat(heartbeat_ticks)
        thought_count_after = len(brain.store.thoughts(100000))
        return {
            "schema": "the-doctor-lives.concern-characterization.v1",
            "open_concerns_before": before,
            "distinct_pressures": int(distinct_pressures),
            "open_concerns_after_pressures": after_pressures,
            "neutral_probe_warrants_cognition": bool(neutral_warrants_cognition),
            "heartbeat_ticks": int(heartbeat_ticks),
            "heartbeat_thoughts": len(heartbeat["thoughts"]),
            "thoughts_added_during_heartbeat": thought_count_after - thought_count_before,
            "public_resolve_concern_method": hasattr(brain, "resolve_concern"),
        }
