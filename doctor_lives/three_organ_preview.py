"""Opt-in, isolated THREE-COMPONENT Pretorius preview host.

Sensus is the evidence-preserving scene binder, Doctor's EXISTING policy owns
endogenous-recall selection, and Synthetic Ipseity is the ONLY renderer path.
This is a preview, not a production promotion or an authorized rewrite of
the Sensus donor's separately blinded experiments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import re
import sys
import time
from typing import Callable, Iterable

from .preview_scene_journal import PreviewSceneJournal, PreviewSceneConflict
from uuid import uuid4

from .ipseity_integration import DoctorSyntheticIpseitySession
from .ipseity_local import build_local_renderer
from .subject_inquiry import validate_subject_inquiry

try:
    from sensus_artificialis import Evidence, Percept, Sensus, ObjectFile, SCHEMA_VERSION
    from sensus_artificialis import core as _sensus_core
except ImportError as exc:
    raise ImportError(
        "Three-organ preview requires the exact reviewed Sensus donor on PYTHONPATH"
    ) from exc


_EXPECTED_SENSUS_SCHEMA = "sensus.scene.v0.1"
_PINNED_SENSUS_COMMIT = "802e459ee68950414347d5fa324484c034f57b81"
_PINNED_SENSUS_CORE_BLOB = "507cd9f75af04353b5e42d67fb60c147acff5ffb"


def _require_pinned_sensus() -> None:
    """Check donor commit identity and the imported code bytes."""
    core_path = Path(_sensus_core.__file__).resolve()
    root = core_path.parent.parent
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=4, check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("Sensus preview requires a reviewed Git checkout") from exc
    if result.stdout.strip() != _PINNED_SENSUS_COMMIT:
        raise RuntimeError("Unreviewed Sensus commit; preview refuses to start")
    source = core_path.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(source)).encode("ascii") + b"\0" + source).hexdigest()
    if git_blob != _PINNED_SENSUS_CORE_BLOB:
        raise RuntimeError("Dirty or substituted Sensus core; preview refuses to start")

_ALLOWED_OBSERVED_CHANNELS = frozenset({
    "vision", "hearing", "instrument", "touch",
})
_SAFE_OBSERVED_PHRASE = re.compile(r"^[a-zA-Z0-9 ,.'-]{1,90}$")


class ThreeOrganPretoriusPreview(DoctorSyntheticIpseitySession):
    """Experimental full Doctor brain with a real three-component cycle.

    The trusted host provides typed, independently authenticated source refs.
    Possessing a syntactically valid Percept is never source authentication.
    Only observed unconflicted world claims and reported User speech are
    admitted to Doctor. A contradictory observed scene opens an EPISTEMIC
    CONCERN, not a fabricated observation or memory.
    """

    def __init__(
        self, state_dir: str | Path, *,
        renderer: Callable[[str], str],
        enabled: bool = False,
        neural_config: dict | None = None,
    ):
        path = Path(state_dir)
        if not enabled:
            raise PermissionError("Explicit three-organ preview opt-in required")
        if path.name != "three-organ-preview":
            raise ValueError("Preview state directory must be named three-organ-preview")
        if SCHEMA_VERSION != _EXPECTED_SENSUS_SCHEMA:
            raise RuntimeError("Unreviewed Sensus scene schema")
        _require_pinned_sensus()
        super().__init__(
            path, renderer=renderer,
            epoch_id="pretorius-three-organ-preview-v1",
            neural_config=neural_config,
        )
        self._journal = PreviewSceneJournal(path)
        self._sensus = Sensus()
        snapshot = self._journal.snapshot()
        if snapshot:
            self._sensus._last_tick = int(snapshot["last_tick"])
            self._sensus._next_id = int(snapshot["next_id"])
            self._sensus._files = {
                row["object_id"]: ObjectFile(
                    row["object_id"], tuple(tuple(pair) for pair in row["features"]),
                    int(row["last_seen_tick"]),
                )
                for row in snapshot["files"]
            }
        self._scene_tick = max(
            self._doctor.brain.store.tick + 1,
            (self._sensus._last_tick + 1),
        )
        self._internal_question: str | None = None
        self.bind_recollection_controller(self._choose_internal_question)

    def _choose_internal_question(self) -> str:
        if self._internal_question is None:
            raise RuntimeError("No policy-selected internal recollection pending")
        return self._internal_question

    @staticmethod
    def _claim_record(claim: Percept) -> dict:
        """Engineer-only source assertion, never passed to SubjectFrame."""
        return {
            "event_id": claim.event_id, "source_ref": claim.source_ref,
            "channel": claim.channel, "evidence": claim.evidence.value,
            "tick": claim.tick, "attribute": claim.attribute,
            "value": claim.value, "confidence": claim.confidence,
            "object_hint": claim.object_hint, "features": claim.features,
        }

    def _record_conflict_as_epistemic_concern(
        self, attribute: str, object_id: str, claims: tuple[dict, ...],
        identifier: str,
    ) -> str:
        if not _SAFE_OBSERVED_PHRASE.fullmatch(attribute):
            raise ValueError("Untrusted conflict attribute cannot form a subject cue")
        description = "the " + attribute.strip()
        validate_subject_inquiry(f"What do I remember of {description}?")
        brain = self._doctor.brain
        with brain.store.connect() as db:
            existing = db.execute(
                "SELECT id,description FROM concerns WHERE id=?", (identifier,),
            ).fetchone()
            if existing:
                check = db.execute(
                    "SELECT outcome FROM concern_events WHERE concern_id=? "
                    "AND transition='opened' AND source='preview_sensus_conflict'",
                    (identifier,),
                ).fetchone()
                expected_claims = list(claims)
                if not check or json.loads(check["outcome"])["claims"] != expected_claims:
                    raise PreviewSceneConflict("Conflicting durable concern receipt")
                return identifier
        evidence = {
            "schema": "pretorius.preview.conflict-evidence.v1",
            "attribute": attribute, "object_id": object_id,
            "claims": list(claims),
            "resolution": None, "downstream_effect": "open_epistemic_pressure",
        }
        with brain.store.transaction() as conn:
            conn.execute(
                """INSERT INTO concerns
                (id,created_tick,updated_tick,description,status,importance,
                 uncertainty,actor,source)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (identifier, brain.store.tick, brain.store.tick, description,
                 "open", 0.95, 0.95, "PREVIEW_HOST", "preview_sensus_conflict"),
            )
            conn.execute(
                """INSERT INTO concern_events
                (id,concern_id,tick,created_at,transition,outcome,actor,source)
                VALUES(?,?,?,?,?,?,?,?)""",
                ("preview-evidence-" + identifier, identifier, brain.store.tick,
                 __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
                 "opened", json.dumps(evidence, sort_keys=True),
                 "PREVIEW_HOST", "preview_sensus_conflict"),
            )
            brain.store.bump_state_version(conn)
        return identifier

    def _resolve_corrob_observations(self, claim_records: list[dict]) -> tuple[str, ...]:
        """Later independent matching observations may settle a gap.

        Recollection alone is never proof that a disputed world claim is true.
        """
        by_attribute: dict[str, list[Percept]] = {}
        for claim in claim_records:
            if claim['evidence'] == Evidence.OBSERVED.value and claim['confidence'] >= 0.60:
                by_attribute.setdefault(claim['attribute'], []).append(claim)
        with self._doctor.brain.store.connect() as conn:
            concerns = conn.execute(
                "SELECT id FROM concerns WHERE status='open' "
                "AND source='preview_sensus_conflict'"
            ).fetchall()
            source_rows = conn.execute(
                "SELECT concern_id,outcome FROM concern_events "
                "WHERE transition='opened' AND source='preview_sensus_conflict'"
            ).fetchall()
        evidence_rows = {row["concern_id"]: row["outcome"] for row in source_rows}
        resolved = []
        for gap in concerns:
            old = evidence_rows.get(gap["id"])
            if not old:
                continue
            evidence = json.loads(old)
            claims = by_attribute.get(evidence["attribute"], [])
            if len({c["source_ref"] for c in claims}) < 2 or len({c["value"] for c in claims}) != 1:
                continue
            former = evidence["claims"]
            former_hints = {c["object_hint"] for c in former if c["object_hint"]}
            if not former_hints or not any(c["object_hint"] in former_hints for c in claims):
                continue
            if any(c["source_ref"] in {x["source_ref"] for x in former} for c in claims):
                continue
            outcome = {
                "schema": "pretorius.preview.conflict-resolution.v1",
                "reason": "two_independent_later_observations_agree",
                "original_evidence": evidence,
                "resolution": claims,
                "downstream_effect": "remove_gap_from_future_policy_candidates",
            }
            self._doctor.brain.close_concern(
                gap["id"], json.dumps(outcome, sort_keys=True),
                actor="PREVIEW_HOST", source="preview_verified_observation_resolution",
            )
            resolved.append(gap["id"])
        return tuple(resolved)

    def cycle(
        self, percepts: Iterable[Percept], *,
        trusted_source_refs: frozenset[str],
        now_ms: int,
    ) -> dict:
        """One guarded scene → Doctor policy → Ipseity first-person delivery.

        Never give raw Scene, conflict values, ledger rows or policy telemetry
        to the model. The returned engineer receipt must not be fed back as
        a model-visible event.
        """
        if self.pending_count():
            raise RuntimeError("Pending first-person delivery: resume first")
        if type(trusted_source_refs) is not frozenset:
            raise TypeError("Trusted host must supply a frozen source allowlist")
        items = tuple(percepts)
        if not items or any(type(p) is not Percept for p in items):
            raise TypeError("Nonempty typed Sensus Percept input required")
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError("now_ms must be nonnegative integer")
        for p in items:
            if p.source_ref not in trusted_source_refs:
                raise PermissionError("Percept source is not authenticated by host")
            if p.tick != self._scene_tick:
                raise ValueError("Percept tick differs from the trusted host scene tick")
            if p.evidence is Evidence.OBSERVED:
                if (
                    p.channel not in _ALLOWED_OBSERVED_CHANNELS
                    or not _SAFE_OBSERVED_PHRASE.fullmatch(p.attribute)
                    or not _SAFE_OBSERVED_PHRASE.fullmatch(p.value)
                ):
                    raise ValueError("Unsafe or unrecognized observed-percept shape")
            elif p.evidence is Evidence.REPORTED:
                if p.channel != "conversation" or p.attribute != "message":
                    raise ValueError("Reported percept must remain a communication")
                if not p.value.strip() or len(p.value) > 800:
                    raise ValueError("Invalid reported message")
            else:
                # These may participate in Sensus scenes but cannot enter
                # Doctor as direct physical observations.
                pass

        if self._journal.active():
            raise PreviewSceneConflict("Interrupted scene must be resumed first")
        if len({p.source_ref for p in items}) != len(items):
            raise ValueError("Distinct Percepts require unique authenticated sources")
        scene = self._sensus.step(self._scene_tick, items)
        operations = []
        gaps = []
        admitted = 0
        latest_message = None
        for obj in scene.objects:
            if obj.contested_attributes:
                for conflict in scene.conflicts:
                    if conflict.object_id != obj.object_id or conflict.status != "vetoed":
                        continue
                    relevant = tuple(c for c in obj.claims if c.attribute == conflict.attribute)
                    observed = {c.value for c in relevant if c.evidence is Evidence.OBSERVED}
                    if len(observed) < 2:
                        continue
                    digest = hashlib.sha256(json.dumps(
                        [scene.tick, obj.object_id, conflict.attribute,
                         sorted(c.event_id for c in relevant)],
                        sort_keys=True,
                    ).encode("utf-8")).hexdigest()[:32]
                    identifier = "preview-gap-" + digest
                    gaps.append(identifier)
                    operations.append({
                        "kind": "gap", "id": identifier,
                        "attribute": conflict.attribute, "object_id": obj.object_id,
                        "claims": [self._claim_record(c) for c in relevant],
                    })
                continue
            records = [self._claim_record(c) for c in obj.claims]
            if any(c.evidence is Evidence.OBSERVED for c in obj.claims):
                operations.append({"kind": "resolve", "claims": records})
            for claim in obj.claims:
                if claim.evidence is Evidence.OBSERVED:
                    operations.append({
                        "kind": "ingest",
                        "event": {"channel": "world",
                                  "text": f"The {claim.attribute} is {claim.value}.",
                                  "source": "preview-verified-world:"
                                    + claim.source_ref + ":" + claim.event_id,
                                  "novelty": 0.35},
                    })
                    admitted += 1
                elif claim.evidence is Evidence.REPORTED:
                    operations.append({
                        "kind": "ingest",
                        "event": {"channel": "user", "actor": "User",
                                  "source": "preview-verified-user:"
                                    + claim.source_ref + ":" + claim.event_id,
                                  "text": claim.value},
                    })
                    latest_message = claim.value
                    admitted += 1

        snapshot = {
            "last_tick": self._sensus._last_tick,
            "next_id": self._sensus._next_id,
            "files": [
                {"object_id": x.object_id, "features": x.features,
                 "last_seen_tick": x.last_seen_tick}
                for x in self._sensus.recent_object_files
            ],
        }
        payload = {
            "scene_tick": scene.tick, "scene_schema": scene.schema_version,
            "scene_conflicts": len(scene.conflicts),
            "scene_object_ids": [o.object_id for o in scene.objects],
            "admitted_percepts": admitted,
            "new_epistemic_gap_ids": gaps,
            "latest_reported_message": latest_message,
            "before_brain_tick": self._doctor.brain.store.tick,
            "operations": operations,
        }
        self._journal.begin(payload, snapshot)
        self._scene_tick += 1
        self._checkpoint("scene_built")
        return self._continue_scene(now_ms=now_ms)

    def _checkpoint(self, name: str) -> None:
        """Injectable deterministic kill point; inert in normal execution."""

    def _apply_scene_operation(self, operation: dict, before_tick: int) -> None:
        kind = operation["kind"]
        if kind == "gap":
            self._record_conflict_as_epistemic_concern(
                operation["attribute"], operation["object_id"],
                tuple(operation["claims"]), identifier=operation["id"],
            )
        elif kind == "resolve":
            self._resolve_corrob_observations(operation["claims"])
        elif kind == "ingest":
            event = operation["event"]
            with self._doctor.brain.store.connect() as conn:
                rows = conn.execute(
                    "SELECT id,tick FROM events WHERE source=? AND tick>?",
                    (event["source"], before_tick),
                ).fetchall()
            if len(rows) > 1:
                raise PreviewSceneConflict("Duplicate persisted Doctor admission")
            if not rows:
                self.ingest(event)
            else:
                # An already recorded admission is never replayed. Any neural
                # checkpoint gap requires separate operator reconciliation.
                if self._doctor.brain.neural.tick <= 0:
                    raise PreviewSceneConflict("Neural checkpoint cannot certify ingress")
        else:
            raise PreviewSceneConflict("Unknown scene journal operation")

    def _recover_decision(self, boundary: int) -> dict | None:
        with self._doctor.brain.store.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM policy_decisions WHERE rowid>? AND "
                "policy_version='preview-epistemic-deliberation-v0.1' "
                "ORDER BY rowid", (boundary,),
            ).fetchall()
            if not rows:
                return None
            if len(rows) != 1:
                raise PreviewSceneConflict("Ambiguous recovered decision history")
            row = rows[0]
            audit = json.loads(row["state_pressure_json"])
            ids = json.loads(row["selected_record_ids_json"])
            question = None
            if row["selected_action"] == "recall":
                if len(ids) != 1:
                    raise PreviewSceneConflict("Recollection decision missing one gap")
                gap = conn.execute(
                    "SELECT description FROM concerns WHERE id=?", (ids[0],),
                ).fetchone()
                if gap is None:
                    raise PreviewSceneConflict("Recollection concern no longer exists")
                question = f"What do I remember of {gap['description']}?"
                validate_subject_inquiry(question)
                if hashlib.sha256(question.encode("utf-8")).hexdigest() != audit["question_sha256"]:
                    raise PreviewSceneConflict("Recovered question hash mismatch")
            return {
                "selected_action": row["selected_action"], "decision_id": row["id"],
                "question": question, "source_gap_id": ids[0] if ids else None,
                "audit": audit,
            }

    def _resolved_gap_ids(self, payload: dict) -> list[str]:
        refs = {
            c["event_id"]
            for op in payload["operations"] if op["kind"] == "resolve"
            for c in op["claims"]
        }
        found = []
        with self._doctor.brain.store.connect() as conn:
            rows = conn.execute(
                "SELECT id,resolution FROM concerns WHERE status='resolved' "
                "AND source='preview_sensus_conflict'"
            ).fetchall()
            for row in rows:
                data = json.loads(row["resolution"])
                if any(c["event_id"] in refs for c in data.get("resolution", ())):
                    found.append(row["id"])
        return found

    def _continue_scene(self, *, now_ms: int) -> dict:
        record = self._journal.active()
        if record is None:
            raise PreviewSceneConflict("No incomplete scene")
        key = record["id"]
        payload = record["payload"]
        if record["stage"] == "scene_built":
            for index in range(record["op_index"], len(payload["operations"])):
                op = payload["operations"][index]
                self._apply_scene_operation(op, payload["before_brain_tick"])
                self._checkpoint("applied_operation")
                self._journal.step(key, index)
                self._checkpoint("journaled_operation")
            self._journal.stage(key, "scene_built", "admitted")
            self._checkpoint("admitted")
            record = self._journal.active()
        if record["stage"] == "admitted":
            if record["decision_before"] is None:
                with self._doctor.brain.store.connect() as conn:
                    last = conn.execute(
                        "SELECT COALESCE(MAX(rowid),0) FROM policy_decisions"
                    ).fetchone()[0]
                self._journal.decision_boundary(key, int(last))
                record = self._journal.active()
            decision = record.get("decision") or self._recover_decision(
                record["decision_before"]
            )
            if decision is None:
                decision = self._doctor.brain.research_endogenous_recall(
                    enabled=True, persist=True, preview_live=True,
                )
            self._checkpoint("decision_persisted")
            self._journal.set_decision(key, decision)
            self._journal.stage(key, "admitted", "decided")
            self._checkpoint("decided")
            record = self._journal.active()
        if record["stage"] == "decided":
            if record["publish_before"] is None:
                self._journal.publish_boundary(key, self._ipseity.checkpoint().last_sequence)
                record = self._journal.active()
            if not self.pending_count():
                if self._ipseity.checkpoint().last_sequence > record["publish_before"]:
                    # The renderer already acknowledged a frame before this
                    # journal marked it published; never infer/repeat an output.
                    self._journal.stage(key, "decided", "published")
                    self._journal.stage(key, "published", "delivered")
                    raise PreviewSceneConflict(
                        "Previously acknowledged delivery; operator must verify output"
                    )
                decision = record["decision"]
                if decision["selected_action"] == "recall":
                    self._internal_question = decision["question"]
                    self.publish_recollection()
                else:
                    self._internal_question = None
                    self.publish_current(user_input=payload["latest_reported_message"])
            self._checkpoint("published_not_journaled")
            self._journal.stage(key, "decided", "published")
            self._checkpoint("published")
            record = self._journal.active()
        if record["stage"] != "published":
            raise PreviewSceneConflict("Unrecognized preview scene stage")
        delivery = self.deliver_next(now_ms=now_ms)
        if delivery is None:
            raise RuntimeError("First-person frame leased; delivery not acknowledged")
        self._checkpoint("delivery_acknowledged")
        self._journal.stage(key, "published", "delivered")
        self._checkpoint("delivered")
        decision = record["decision"]
        return {
            "schema": "pretorius.three-organ-preview.v1",
            "answer": delivery.response,
            "scene_schema": payload["scene_schema"],
            "scene_conflicts": payload["scene_conflicts"],
            "scene_object_ids": payload["scene_object_ids"],
            "admitted_percepts": payload["admitted_percepts"],
            "new_epistemic_gap_ids": payload["new_epistemic_gap_ids"],
            "resolved_epistemic_gap_ids": self._resolved_gap_ids(payload),
            "endogenous_decision_id": decision["decision_id"],
            "endogenous_action": decision["selected_action"],
            "recollection_selected": decision["selected_action"] == "recall",
            "ipseity_pending": self.pending_count(),
            "engineer_only": True,
            "not_production_approved": True,
        }

    def resume_preview(self, *, now_ms: int) -> str:
        """Resume stored scene operations, without re-running Sensus or policy."""
        if self._journal.active():
            return self._continue_scene(now_ms=now_ms)["answer"]
        if not self.pending_count():
            raise RuntimeError("No pending first-person delivery")
        delivery = self.deliver_next(now_ms=now_ms)
        if delivery is None:
            raise RuntimeError("A prior worker holds the subject-frame lease")
        return delivery.response

    def close(self) -> None:
        try:
            self._journal.close()
        finally:
            super().close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="doctor-lives-three-organ-preview",
        description="Isolated, opt-in Sensus → Doctor policy → Ipseity preview",
    )
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--model", default="qwen3:1.5b")
    parser.add_argument("--enable-experimental-preview", action="store_true")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--say", help="Reported User speech, not world observation")
    mode.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    # No package initialization occurs before explicit opt-in and isolation.
    if not args.enable_experimental_preview:
        parser.error("--enable-experimental-preview is required")
    if args.state.name != "three-organ-preview":
        parser.error("--state must be a dedicated three-organ-preview directory")
    with ThreeOrganPretoriusPreview(
        args.state, enabled=True, renderer=build_local_renderer(args.model),
    ) as host:
        when = int(time.time() * 1000)
        if args.resume:
            result = host.resume_preview(now_ms=when)
        else:
            # Authenticated by the local application as an external User
            # message, not elevated to visual/physical evidence.
            source = "preview-cli:local-user"
            percept = Percept(
                event_id="reported-" + uuid4().hex,
                channel="conversation", evidence=Evidence.REPORTED,
                source_ref=source, tick=host._scene_tick,
                attribute="message", value=args.say, confidence=0.8,
            )
            receipt = host.cycle(
                (percept,), trusted_source_refs=frozenset({source}),
                now_ms=when,
            )
            result = receipt["answer"]
        sys.stdout.write(result + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
