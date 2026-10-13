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
from .models import SubjectFrame
from .phenomenology import (
    AwarenessLevel, CertaintyBand, ObjectiveProvenance, PhenomenalEvent,
    PhenomenalMode, PrivacyState, SubjectiveSourceAttribution,
    SubjectiveSourceKind,
)

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
_PINNED_SENSUS_INIT_BLOB = "ac434e8d41119ca11a91948e3c0dd7aca3fa3660"


def _require_pinned_sensus() -> None:
    """Check donor commit identity and the imported code bytes."""
    core_path = Path(_sensus_core.__file__).resolve()
    root = core_path.parent.parent
    git_dir = root / ".git"
    if not git_dir.is_dir():
        raise RuntimeError("Sensus preview requires a reviewed Git checkout")
    head_text = (git_dir / "HEAD").read_text(encoding="ascii").strip()
    if head_text.startswith("ref: "):
        ref = head_text[5:]
        loose = git_dir / ref
        if loose.is_file():
            head_text = loose.read_text(encoding="ascii").strip()
        else:
            packed = git_dir / "packed-refs"
            pairs = (
                [line.split(" ", 1) for line in packed.read_text("ascii").splitlines()
                 if line and not line.startswith(("#", "^")) and " " in line]
                if packed.is_file() else []
            )
            head_text = next((sha for sha, name in pairs if name == ref), "")
    if head_text != _PINNED_SENSUS_COMMIT:
        raise RuntimeError("Unreviewed Sensus commit; preview refuses to start")
    source = core_path.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(source)).encode("ascii") + b"\0" + source).hexdigest()
    if git_blob != _PINNED_SENSUS_CORE_BLOB:
        raise RuntimeError("Dirty or substituted Sensus core; preview refuses to start")
    init_bytes = (core_path.parent / "__init__.py").read_bytes()
    init_blob = hashlib.sha1(
        b"blob " + str(len(init_bytes)).encode("ascii") + b"\0" + init_bytes
    ).hexdigest()
    if init_blob != _PINNED_SENSUS_INIT_BLOB:
        raise RuntimeError("Dirty or substituted Sensus exports; preview refuses to start")
    if (Percept is not _sensus_core.Percept
            or Evidence is not _sensus_core.Evidence
            or Sensus is not _sensus_core.Sensus):
        raise RuntimeError("Substituted Sensus type exports")

_ALLOWED_OBSERVED_CHANNELS = frozenset({
    "vision", "hearing", "instrument", "touch",
})
_SAFE_OBSERVED_PHRASE = re.compile(r"^[a-zA-Z0-9 ,.'-]{1,90}$")

# Import-time fail-closed source verification, repeated before state open.
_require_pinned_sensus()


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

    def _resolve_corrob_observations(self, operation: dict) -> tuple[str, ...]:
        """Re-identified object plus cross-channel readings may settle a gap.

        Percept.object_hint only binds within one tick. Never treat a reused
        hint as persistent identity. Sensus matching remains fallible.
        """
        if operation["identity_status"] != "matched":
            return ()
        ancestor_id = operation["reidentified_from"]
        if not ancestor_id:
            return ()
        claim_records = operation["claims"]
        by_attribute: dict[str, list[dict]] = {}
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
            if evidence["object_id"] != ancestor_id:
                continue
            claims = by_attribute.get(evidence["attribute"], [])
            # Distinct source references alone do not imply independent
            # observation; require distinct sensory channels as well.
            if len({c["source_ref"] for c in claims}) < 2:
                continue
            if len({c["channel"] for c in claims}) < 2:
                continue
            if len({c["value"] for c in claims}) != 1:
                continue
            former = evidence["claims"]
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
        for p in items:
            if self._journal.seen_percept(p.source_ref, p.event_id):
                raise PreviewSceneConflict(
                    "Previously processed Percept identity cannot be replayed"
                )
        with self._doctor.brain.store.connect() as conn:
            for claim in items:
                if claim.evidence not in (Evidence.OBSERVED, Evidence.REPORTED):
                    continue
                channel = "world" if claim.evidence is Evidence.OBSERVED else "user"
                source = (
                    "preview-verified-" + channel + ":"
                    + claim.source_ref + ":" + claim.event_id
                )
                if conn.execute(
                    "SELECT 1 FROM events WHERE source=? LIMIT 1", (source,),
                ).fetchone():
                    raise PreviewSceneConflict(
                        "Previously admitted Percept event ID cannot be replayed"
                    )
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
                operations.append({
                    "kind": "resolve", "claims": records,
                    "object_id": obj.object_id,
                    "identity_status": obj.identity_status,
                    "reidentified_from": obj.reidentified_from,
                })
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
            "percept_identity": [
                {"source_ref": p.source_ref, "event_id": p.event_id}
                for p in items
            ],
            "operations": operations,
        }
        self._journal.begin(payload, snapshot)
        self._scene_tick += 1
        self._checkpoint("scene_built")
        return self._continue_scene(now_ms=now_ms)

    def _checkpoint(self, name: str) -> None:
        """Injectable deterministic kill point; inert in normal execution."""

    def _apply_scene_operation(
        self, operation: dict, before_tick: int, before_neural: int | None = None,
        *, scene_key: str | None = None, op_index: int | None = None,
    ) -> None:
        kind = operation["kind"]
        if kind == "gap":
            self._record_conflict_as_epistemic_concern(
                operation["attribute"], operation["object_id"],
                tuple(operation["claims"]), identifier=operation["id"],
            )
        elif kind == "resolve":
            self._resolve_corrob_observations(operation)
        elif kind == "ingest":
            event = operation["event"]
            with self._doctor.brain.store.connect() as conn:
                rows = conn.execute(
                    "SELECT id,tick FROM events WHERE source=? AND tick>?",
                    (event["source"], before_tick),
                ).fetchall()
            if len(rows) > 1:
                raise PreviewSceneConflict("Duplicate persisted Doctor admission")
            if scene_key is None or op_index is None or before_neural is None:
                raise PreviewSceneConflict("Ingress operation lacks a durable journal cursor")
            if not rows:
                self.ingest(event)
                # This is written only after Doctor's event, neural update and
                # on-disk checkpoint have all completed. A crash before it is
                # ambiguous and must never be inferred from a later tick.
                self._journal.complete_ingress(
                    scene_key, op_index, self._doctor.brain.neural.tick,
                    self._doctor.brain._neural_checkpoint_sha256(),
                )
            else:
                # Never replay a Doctor event. Require this exact operation's
                # previously committed neural-completion receipt.
                self._journal.verify_completed_ingress(
                    scene_key, op_index, self._doctor.brain.neural.tick,
                    self._doctor.brain._neural_checkpoint_sha256(),
                )
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

    def _record_policy_effect_receipts(self, payload: dict, decision: dict) -> None:
        """Bind resolved concerns to an actual later persisted policy decision."""
        resolved = self._resolved_gap_ids(payload)
        if not resolved:
            return
        candidate_ids = set(decision["audit"]["candidate_gap_ids"])
        if any(gap in candidate_ids for gap in resolved):
            raise PreviewSceneConflict("Resolved concern still drives policy pressure")
        brain = self._doctor.brain
        with brain.store.transaction() as conn:
            changed = False
            for gap in resolved:
                event_id = "preview-effect-" + gap + "-" + decision["decision_id"]
                audit = {
                    "schema": "pretorius.preview.causal-policy-effect.v1",
                    "decision_id": decision["decision_id"],
                    "policy_version": decision["audit"]["policy_version"],
                    "selected_action": decision["selected_action"],
                    "recall_pressure": decision["audit"]["information_need_family"]["recall_pressure"],
                    "effect": "resolved_concern_excluded_from_policy_candidates",
                    "resolved_concern_id": gap,
                }
                result = conn.execute(
                    """INSERT OR IGNORE INTO concern_events
                    (id,concern_id,tick,created_at,transition,outcome,actor,source)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (event_id, gap, brain.store.tick,
                     __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
                     "policy_effect", json.dumps(audit, sort_keys=True),
                     "PREVIEW_HOST", "preview_policy_effect_receipt"),
                )
                changed |= result.rowcount == 1
            if changed:
                brain.store.bump_state_version(conn)


    @staticmethod
    def _episode_query_terms(text: str | None) -> set[str]:
        """Lexical retrieval cue only. User text never becomes source authority."""
        stop = frozenset({
            "the", "and", "our", "you", "your", "what", "have", "that",
            "this", "with", "from", "they", "were", "was", "about",
            "tell", "remember", "actually", "remains", "uncertain",
        })
        return set(re.findall(r"[a-z]{3,}", (text or "").lower())) - stop

    def _verified_episode_events(
        self, *, query: str | None, scene_resolved_ids: frozenset[str],
    ) -> tuple[PhenomenalEvent, ...]:
        """Read-only, capped projection from authenticated Doctor concern history.

        The preview is not allowed to promote an engineer conflict payload,
        a reported user statement or a recollection alone to verified reality.
        Resolution claims must also exist as admitted observed Doctor events.
        """
        brain = self._doctor.brain
        with brain.store.connect() as db:
            rows = db.execute(
                "SELECT id,description,resolution,resolved_tick FROM concerns "
                "WHERE status='resolved' AND source='preview_sensus_conflict' "
                "AND actor='PREVIEW_HOST' AND resolution IS NOT NULL "
                "ORDER BY resolved_tick DESC,id DESC LIMIT 24"
            ).fetchall()
            query_terms = self._episode_query_terms(query)
            eligible = []
            for row in rows:
                try:
                    evidence = json.loads(row["resolution"])
                    if (
                        evidence.get("schema") != "pretorius.preview.conflict-resolution.v1"
                        or evidence.get("reason") != "two_independent_later_observations_agree"
                        or evidence.get("downstream_effect")
                            != "remove_gap_from_future_policy_candidates"
                    ):
                        continue
                    original = evidence["original_evidence"]
                    if original.get("schema") != "pretorius.preview.conflict-evidence.v1":
                        continue
                    attribute = original["attribute"]
                    if not isinstance(attribute, str) or not _SAFE_OBSERVED_PHRASE.fullmatch(attribute):
                        continue
                    old = original["claims"]
                    if not isinstance(old, list) or len({
                        c["value"] for c in old if c["evidence"] == Evidence.OBSERVED.value
                    }) < 2:
                        continue
                    if not all(c["attribute"] == attribute for c in old):
                        continue
                    claims = evidence["resolution"]
                    if not isinstance(claims, list) or len(claims) < 2:
                        continue
                    if not all(
                        c["evidence"] == Evidence.OBSERVED.value
                        and c["attribute"] == attribute
                        and c["confidence"] >= 0.60
                        and isinstance(c["value"], str)
                        and _SAFE_OBSERVED_PHRASE.fullmatch(c["value"])
                        for c in claims
                    ):
                        continue
                    values = {c["value"] for c in claims}
                    sources = {c["source_ref"] for c in claims}
                    channels = {c["channel"] for c in claims}
                    if len(values) != 1 or len(sources) < 2 or len(channels) < 2:
                        continue
                    if sources & {c["source_ref"] for c in old}:
                        continue
                    # Cross-check the resolution with actual committed Doctor
                    # world admissions. Merely editing a concern cannot grant
                    # it verified status or convert a reported message.
                    for c in claims:
                        source = (
                            "preview-verified-world:" + c["source_ref"]
                            + ":" + c["event_id"]
                        )
                        admitted_rows = db.execute(
                            "SELECT payload_json,evidence_class,external "
                            "FROM events WHERE source=?",
                            (source,),
                        ).fetchall()
                        expected_text = (
                            "I notice: The " + attribute + " is " + c["value"] + "."
                        )
                        if len(admitted_rows) != 1:
                            break
                        admitted = admitted_rows[0]
                        if (
                            admitted["evidence_class"] != "lived_runtime_memory"
                            or int(admitted["external"]) != 0
                            or json.loads(admitted["payload_json"]).get("text")
                                != expected_text
                        ):
                            break
                    else:
                        value = next(iter(values))
                        attr_terms = self._episode_query_terms(attribute)
                        overlap = len(attr_terms & query_terms)
                        topical = bool(
                            query_terms & {
                                "measurement", "measurements", "disagreement",
                                "observed", "observation", "observations",
                            }
                        )
                        immediate = row["id"] in scene_resolved_ids
                        if not immediate and not (overlap >= 2 or (overlap >= 1 and topical)):
                            continue
                        priority = (
                            100 if immediate else 0
                        ) + overlap * 10 + int(row["resolved_tick"] or 0) / 1000000
                        eligible.append((priority, row["id"], attribute, value))
                except (KeyError, ValueError, TypeError, AttributeError):
                    # Invalid provenance never enters subject experience.
                    continue

        events = []
        for _, concern_id, attribute, value in sorted(
            eligible, key=lambda item: (-item[0], item[1])
        )[:2]:
            text = (
                f"I remember two later observations of the {attribute} "
                f"agreeing at {value}. Earlier readings disagreed. "
                "I regard that later agreement as stronger evidence, "
                "though it is not infallible."
            )
            events.append(PhenomenalEvent(
                tick=brain.store.tick,
                subject_id="pretorius",
                mode=PhenomenalMode.RECOLLECTION,
                awareness=AwarenessLevel.FOCAL,
                canonical_first_person=text,
                privacy=PrivacyState.PRIVATE,
                projection_rule_version="preview-doctor-verified-episode-v0.1",
                source_state_digest=brain.store.digest(),
                objective_provenance=ObjectiveProvenance(
                    evidence_class="verified_observation_episode",
                    source="preview_verified_observation_resolution",
                    record_ids=(concern_id,),
                ),
                subjective_source=SubjectiveSourceAttribution(
                    SubjectiveSourceKind.LIVED, CertaintyBand.MODERATE,
                ),
                subjective_certainty=CertaintyBand.MODERATE,
                source_state_refs=(concern_id,),
            ))
        return tuple(events)

    def _preview_render_frame(self, payload: dict, decision: dict) -> SubjectFrame:
        """Prioritize relevant lived evidence without exposing Doctor internals.

        All baseline items originate in the existing Doctor SubjectFrame.
        Supplemental episodes pass the same PhenomenalEvent factory gate.
        This preview-only selector leaves normal Doctor rendering unchanged.
        """
        brain = self._doctor.brain
        query = payload.get("latest_reported_message")
        if decision["selected_action"] == "recall":
            self._internal_question = decision["question"]
            if self._recollection_controller is None:
                raise PreviewSceneConflict("Missing authorized recollection controller")
            baseline = self._recollection_controller.recollect_frame()
        else:
            self._internal_question = None
            baseline = brain.render_request(user_input=query).subject_frame
        episodes = SubjectFrame.from_events(self._verified_episode_events(
            query=query,
            scene_resolved_ids=frozenset(self._resolved_gap_ids(payload)),
        ))
        # Preserve actual first-person user speech exactly once. The older
        # render path often placed the same quote in the immediate percept
        # and in an automatically selected communication memory.
        user_items = []
        background = []
        identity = []
        seen_text = set()
        for item in baseline.items:
            line = item.text
            if line in seen_text:
                continue
            seen_text.add(line)
            if line.startswith("I read a message from User:"):
                if not user_items:
                    user_items.append(item)
                continue
            if line.startswith(
                "I recognize this as part of the description I was built from"
            ):
                identity.append(item)
            else:
                background.append(item)
        # A stable character anchor, scientific orientation, and provenance
        # uncertainty survive, while endless near-identical prefaces do not.
        key_phrases = (
            "I am Doctor Septimus Pretorius.",
            "I am a scientist, inventor, alchemist",
            "I treat my present existence as a reconstruction",
        )
        compact_identity = []
        for phrase in key_phrases:
            match = next((x for x in identity if phrase in x.text), None)
            if match is not None and match not in compact_identity:
                compact_identity.append(match)
        # Retrieved episodes win space over repeated identity declarations.
        # Keep the exact original SubjectFrameItem instances as typed.
        selected = []
        seen = set()
        for item in (
            user_items + list(episodes.items) + compact_identity + background
        ):
            if item.text in seen:
                continue
            if len(selected) >= 16:
                break
            if sum(len(x.text) for x in selected) + len(item.text) > 2600:
                continue
            seen.add(item.text)
            selected.append(item)
        if not selected:
            raise PreviewSceneConflict("No safe first-person subject frame remains")
        return SubjectFrame(items=tuple(selected))

    def _continue_scene(self, *, now_ms: int) -> dict:
        record = self._journal.active()
        if record is None:
            raise PreviewSceneConflict("No incomplete scene")
        key = record["id"]
        payload = record["payload"]
        if record["stage"] == "scene_built":
            for index in range(record["op_index"], len(payload["operations"])):
                op = payload["operations"][index]
                before_neural = None
                if op["kind"] == "ingest":
                    before_neural = self._journal.prepare_ingress(
                        key, index, self._doctor.brain.neural.tick,
                    )
                self._apply_scene_operation(
                    op, payload["before_brain_tick"], before_neural,
                    scene_key=key, op_index=index,
                )
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
                # An unrelated pending outbox frame must never be delivered as
                # this scene's first-person experience. No publish from this
                # scene could have occurred before its durable boundary.
                if self.pending_count():
                    raise PreviewSceneConflict(
                        "Unrelated pending subject frame before publication boundary"
                    )
                self._journal.publish_boundary(key, self._ipseity.checkpoint().last_sequence)
                record = self._journal.active()
            current_sequence = self._ipseity.checkpoint().last_sequence
            if self.pending_count() and current_sequence <= record["publish_before"]:
                raise PreviewSceneConflict(
                    "Pending subject frame predates scene publication"
                )
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
                self._publish_typed_subject_frame(
                    self._preview_render_frame(payload, decision)
                )
            self._checkpoint("published_not_journaled")
            self._journal.stage(key, "decided", "published")
            self._checkpoint("published")
            record = self._journal.active()
        if record["stage"] != "published":
            raise PreviewSceneConflict("Unrecognized preview scene stage")
        if record["publish_before"] is None:
            raise PreviewSceneConflict("Published scene is missing outbox boundary")
        if self.pending_count() and (
            self._ipseity.checkpoint().last_sequence <= record["publish_before"]
        ):
            raise PreviewSceneConflict("Pending subject frame is not from this scene")
        if not self.pending_count():
            self._journal.stage(key, "published", "delivered")
            raise PreviewSceneConflict(
                "Previously acknowledged output is not replayed; operator verification required"
            )
        self._record_policy_effect_receipts(payload, record["decision"])
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
