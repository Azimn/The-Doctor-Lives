"""Opt-in Sensus candidate acquisition for the existing six-organ Pretorius.

Mechanism source: PR #59 at 2b0bb21425558cb24906309075b3d919850b10e8,
using the standalone Sensus donor at 802e459ee68950414347d5fa324484c034f57b81.
This is NOT production Sensus adoption, universal sensor authentication, or a
replacement for the Doctor's authoritative world/lived-memory ingress.

The donor binds typed evidence and vetoes contested attributes. This adapter
admits only separately host-verified, uncontested, direct observations through
the EXISTING Doctor Sensus/ingress port. Its scene files are ephemeral and
never a competing autobiographical database.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Iterable

from .organs import AcquisitionReceipt, SensusOrgan
from .store import new_id, utc_now
from .subject_inquiry import validate_subject_inquiry

_PINNED_COMMIT = "802e459ee68950414347d5fa324484c034f57b81"
_PINNED_CORE_BLOB = "507cd9f75af04353b5e42d67fb60c147acff5ffb"
_PINNED_INIT_BLOB = "ac434e8d41119ca11a91948e3c0dd7aca3fa3660"
_SCHEMA = "sensus.scene.v0.1"
_REF = re.compile(r"^[a-zA-Z0-9._:/-]{1,100}$")
_PHRASE = re.compile(r"^[a-zA-Z0-9 ,.'-]{1,90}$")
_CHANNEL_PREFIX = {
    "vision": "I see that",
    "hearing": "I hear that",
    "touch": "I feel that",
    "instrument": "I read on the instrument that",
}


def _git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def _load_verified_donor():
    try:
        import sensus_artificialis as donor
        from sensus_artificialis import core
    except ImportError as exc:
        raise RuntimeError("Install the pinned Sensus donor to use this opt-in pilot") from exc
    source = Path(core.__file__).resolve()
    root = source.parent.parent
    git = root / ".git"
    # As in the reviewed #59 preview: require a real detached pinned checkout.
    # Refuse editable working copies or unreviewed packaged substitutes.
    if not git.is_dir():
        raise RuntimeError("Sensus donor must be a reviewed Git checkout")
    head = (git / "HEAD").read_text(encoding="ascii").strip()
    if head != _PINNED_COMMIT:
        raise RuntimeError("Sensus donor must be detached at reviewed commit")
    if (_git_blob(source) != _PINNED_CORE_BLOB
            or _git_blob(source.parent / "__init__.py") != _PINNED_INIT_BLOB):
        raise RuntimeError("Sensus source has been modified since review")
    if (core.SCHEMA_VERSION != _SCHEMA
            or donor.Sensus is not core.Sensus
            or donor.Percept is not core.Percept
            or donor.Evidence is not core.Evidence):
        raise RuntimeError("Sensus donor interface identity mismatch")
    return donor


@dataclass(frozen=True, slots=True)
class SensusCandidateOutcome:
    """Engineer-only receipt: never forward this record into subject context."""

    scene_tick: int
    admitted: tuple[AcquisitionReceipt, ...]
    vetoed_attributes: tuple[str, ...]
    withheld_claim_ids: tuple[str, ...]
    candidate_count: int
    epistemic_gap_ids: tuple[str, ...] = ()
    # No world-state promotion and no false claim of organ qualification.


class SensusCandidatePilot:
    """Single-brain, host-invoked multichannel test on a pinned donor.

    trusted_refs must be authenticated externally by the caller's trusted
    observer. verified_world_refs must be a separately verified SUBSET: a
    well-typed Percept, or a caller-provided boolean, is not authentication.
    This class is an in-process experimental host boundary, not a sandbox.
    """

    def __init__(self, organ: SensusOrgan):
        if not isinstance(organ, SensusOrgan):
            raise TypeError("Requires the existing six-organ Sensus interface")
        self._organ = organ
        self._donor = _load_verified_donor()
        self._binder = self._donor.Sensus()

    def _persist_verified_conflict(self, scene_tick, conflict, claims) -> str | None:
        """Materialize a verified sensory disagreement as an epistemic concern.

        Adapted from the reviewed PR #59 _record_conflict_as_epistemic_concern.
        No disputed value is admitted as lived observation, and the concern is
        not evidence that a disputed physical fact is true.
        """
        if (conflict.status != "vetoed"
                or not _PHRASE.fullmatch(conflict.attribute)):
            return None
        question = "What do I remember of the " + conflict.attribute + "?"
        validate_subject_inquiry(question)
        evidence = {
            "schema": "pretorius.sensus.conflict-evidence.v1",
            "scene_tick": scene_tick,
            "attribute": conflict.attribute,
            "object_id": conflict.object_id,
            "claims": sorted(
                (
                    {
                        "event_id": p.event_id,
                        "source_ref": p.source_ref,
                        "channel": p.channel,
                        "value": p.value,
                        "evidence": p.evidence.value,
                    }
                    for p in claims
                ),
                key=lambda p: (p["source_ref"], p["event_id"]),
            ),
            "resolution": None,
            "downstream_effect": "open_epistemic_pressure",
        }
        digest = hashlib.sha256(
            json.dumps(evidence["claims"], sort_keys=True).encode("utf-8")
        ).hexdigest()[:32]
        identifier = "sensus-gap-" + digest
        # Single canonical BrainStore: atomic conflict receipt + concern.
        brain = self._organ._port.brain
        with brain.store.transaction() as conn:
            existing = conn.execute(
                "SELECT source,actor,description FROM concerns WHERE id=?",
                (identifier,),
            ).fetchone()
            if existing:
                receipt = conn.execute(
                    """SELECT outcome FROM concern_events
                    WHERE concern_id=? AND source='preview_sensus_conflict'
                    AND transition='opened'""",
                    (identifier,),
                ).fetchone()
                if (existing["source"] != "preview_sensus_conflict"
                        or existing["actor"] != "PREVIEW_HOST"
                        or not receipt
                        or json.loads(receipt["outcome"])["claims"] != evidence["claims"]):
                    raise RuntimeError("Conflicting epistemic concern replay")
                return identifier
            conn.execute(
                """INSERT INTO concerns
                (id,created_tick,updated_tick,description,status,importance,
                 uncertainty,actor,source)
                VALUES(?,?,?,?,'open',?,?,?,?)""",
                (
                    identifier, brain.store.tick, brain.store.tick,
                    "the " + conflict.attribute, 0.95, 0.95,
                    "PREVIEW_HOST", "preview_sensus_conflict",
                ),
            )
            conn.execute(
                """INSERT INTO concern_events
                (id,concern_id,tick,created_at,transition,outcome,actor,source)
                VALUES(?,?,?,?,?,?,?,?)""",
                (
                    new_id("concern_event"), identifier, brain.store.tick,
                    utc_now(), "opened", json.dumps(evidence, sort_keys=True),
                    "PREVIEW_HOST", "preview_sensus_conflict",
                ),
            )
            brain.store.bump_state_version(conn)
        return identifier

    def acquire(
        self,
        tick: int,
        percepts: Iterable[object],
        *,
        trusted_refs: frozenset[str],
        verified_world_refs: frozenset[str],
    ) -> SensusCandidateOutcome:
        """Bind first; only unconflicted, verified OBSERVED cues can be lived."""
        if type(trusted_refs) is not frozenset or type(verified_world_refs) is not frozenset:
            raise TypeError("Trusted host must supply two explicit frozen source sets")
        if not verified_world_refs.issubset(trusted_refs):
            raise PermissionError("Verified world sources must be trusted sources")
        if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
            raise ValueError("Scene tick must be nonnegative integer")
        items = tuple(percepts)
        if not items or any(type(x) is not self._donor.Percept for x in items):
            raise TypeError("Only nonempty typed donor Percepts are supported")
        if len({x.event_id for x in items}) != len(items):
            raise ValueError("Duplicate event IDs in scene")
        for claim in items:
            if claim.tick != tick:
                raise ValueError("Percept/scene clock mismatch")
            if claim.source_ref not in trusted_refs:
                raise PermissionError("Unattested percept source")
            if not _REF.fullmatch(claim.source_ref) or not _REF.fullmatch(claim.event_id):
                raise ValueError("Unsafe source reference or event identifier")
            if (claim.evidence is self._donor.Evidence.OBSERVED
                    and (claim.channel not in _CHANNEL_PREFIX
                         or not _PHRASE.fullmatch(claim.attribute)
                         or not _PHRASE.fullmatch(claim.value))):
                raise ValueError("Unbounded observed claim must not enter lived memory")

        # Preflight already-ingested identities to avoid known replay before
        # mutating the donor's ephemeral object-file state.
        with self._organ._port.brain.store.connect() as conn:
            for p in items:
                if p.evidence is not self._donor.Evidence.OBSERVED:
                    continue
                source = "sensus-pilot-verified:" + p.source_ref + ":" + p.event_id
                if conn.execute(
                    "SELECT 1 FROM events WHERE source=? LIMIT 1", (source,)
                ).fetchone():
                    raise RuntimeError("Repeated sensory event cannot be admitted twice")

        scene = self._binder.step(tick, items)
        vetoed = []
        gaps = []
        admitted = []
        withheld = []
        for object_view in scene.objects:
            contested = set(object_view.contested_attributes)
            # Treat only two separately source-verified OBSERVED channels as
            # eligible evidence for an internally relevant epistemic gap.
            for conflict in scene.conflicts:
                if (conflict.object_id != object_view.object_id
                        or conflict.status != "vetoed"):
                    continue
                observed = [
                    p for p in object_view.claims
                    if p.attribute == conflict.attribute
                    and p.evidence is self._donor.Evidence.OBSERVED
                    and p.source_ref in verified_world_refs
                ]
                if (len({p.value for p in observed}) < 2
                        or len({p.source_ref for p in observed}) < 2
                        or len({p.channel for p in observed}) < 2):
                    continue
                gap = self._persist_verified_conflict(tick, conflict, observed)
                if gap:
                    gaps.append(gap)
            for claim in object_view.claims:
                if (claim.evidence is not self._donor.Evidence.OBSERVED
                        or claim.attribute in contested
                        or claim.source_ref not in verified_world_refs):
                    withheld.append(claim.event_id)
                    continue
                prefix = _CHANNEL_PREFIX[claim.channel]
                first_person = f"{prefix} the {claim.attribute} is {claim.value}."
                receipt = self._organ.acquire_existing_percept(
                    {
                        "channel": "world", "kind": "sensory_observation",
                        "source": "sensus-pilot-verified:" + claim.source_ref
                                  + ":" + claim.event_id,
                        "percept": first_person,
                        "confidence": float(claim.confidence),
                    },
                    host_authorized=True,
                )
                admitted.append(receipt)
        for conflict in scene.conflicts:
            vetoed.append(conflict.attribute)
        return SensusCandidateOutcome(
            scene_tick=tick,
            admitted=tuple(admitted),
            vetoed_attributes=tuple(sorted(set(vetoed))),
            withheld_claim_ids=tuple(sorted(withheld)),
            candidate_count=len(items),
            epistemic_gap_ids=tuple(sorted(set(gaps))),
        )
