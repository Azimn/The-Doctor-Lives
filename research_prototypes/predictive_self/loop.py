"""Predictive Self Loop (PSL v0.1), isolated shadow-mode cognitive research.

Five mechanisms: semantic-to-episodic priors, episodic-to-semantic revision,
contextual action distributions, observable partner-response estimates, and
non-executing epistemic inquiry proposals.

This implementation is not active inference's expected-free-energy solver,
does not implement a second action policy, and must not be imported into
the live Pretorius brain without an independent promotion gate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import StrEnum
import hashlib
import json
import math


PROTOCOL = "pretorius-predictive-self-loop-v0.1"
MIN_SLOW_CONTEXTS = 3
MIN_SLOW_EPISODES = 3


def _unit(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{name} cannot be boolean")
    try:
        result = float(value)
    except (ValueError, TypeError) as exc:
        raise TypeError(f"{name} must be numeric") from exc
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise ValueError(f"{name} must be finite between zero and one")
    return result


def _required(text: str, name: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"{name} must be nonempty text")
    return text


def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()


def _distribution(values: tuple[float, ...], name: str) -> tuple[float, ...]:
    if not isinstance(values, tuple) or not values:
        raise TypeError(f"{name} must be a nonempty tuple")
    normalized = tuple(_unit(x, name) for x in values)
    if not math.isclose(sum(normalized), 1.0, abs_tol=1e-8):
        raise ValueError(f"{name} must sum to one")
    return normalized


def _normalized(values: tuple[float, ...]) -> tuple[float, ...]:
    total = sum(values)
    if not total or not math.isfinite(total):
        raise ValueError("distribution has no finite positive mass")
    return tuple(v / total for v in values)


class EvidenceKind(StrEnum):
    RUNTIME_POLICY = "runtime_policy"
    WORLD_VERIFIED = "world_verified"


@dataclass(frozen=True, slots=True)
class SelfSnapshot:
    subject_id: str
    state_digest: str
    state_version: int
    manifest_digest: str
    cutoff_tick: int
    actions: tuple[str, ...]
    base_probabilities: tuple[float, ...]
    admitted_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _required(self.subject_id, "subject_id")
        for field in ("state_digest", "manifest_digest"):
            digest = getattr(self, field)
            if not isinstance(digest, str) or len(digest) != 64 or any(
                x not in "0123456789abcdef" for x in digest
            ):
                raise ValueError(f"{field} must be SHA-256 hex")
        for field in ("state_version", "cutoff_tick"):
            x = getattr(self, field)
            if type(x) is not int or x < 0:
                raise ValueError(f"{field} must be a nonnegative integer")
        if not isinstance(self.actions, tuple) or len(self.actions) < 2:
            raise ValueError("at least two possible actions are required")
        if any(not isinstance(a, str) or not a.strip() for a in self.actions):
            raise ValueError("action labels must be text")
        if len(set(self.actions)) != len(self.actions):
            raise ValueError("action labels must be distinct")
        if len(self.base_probabilities) != len(self.actions):
            raise ValueError("one baseline probability required per action")
        _distribution(self.base_probabilities, "base_probabilities")
        if not isinstance(self.admitted_refs, tuple) or any(
            not isinstance(x, str) or not x.strip() for x in self.admitted_refs
        ) or len(set(self.admitted_refs)) != len(self.admitted_refs):
            raise ValueError("admitted_refs must be distinct, nonempty source IDs")

    @property
    def digest(self) -> str:
        return _hash(asdict(self))


@dataclass(frozen=True, slots=True)
class Situation:
    """Context and social partner, never an inferred statement of world truth."""

    context_id: str
    role: str
    partner_id: str | None = None

    def __post_init__(self) -> None:
        _required(self.context_id, "context_id")
        _required(self.role, "role")
        if self.partner_id is not None:
            _required(self.partner_id, "partner_id")

    @property
    def key(self) -> str:
        return _hash(asdict(self))


@dataclass(frozen=True, slots=True)
class SemanticClaim:
    """Fallible prediction proxy, not authoritative autobiography or a value rule."""

    key: str
    indicator_actions: tuple[str, ...]
    prior_mean: float
    source_refs: tuple[str, ...]
    prior_strength: float = 6.0

    def __post_init__(self) -> None:
        _required(self.key, "claim key")
        if not isinstance(self.indicator_actions, tuple) or not self.indicator_actions:
            raise ValueError("indicator_actions must be a nonempty tuple")
        if len(set(self.indicator_actions)) != len(self.indicator_actions):
            raise ValueError("indicator_actions must be distinct")
        if not isinstance(self.source_refs, tuple) or not self.source_refs:
            raise ValueError("semantic hypotheses require provenance references")
        if len(set(self.source_refs)) != len(self.source_refs) or any(
            not isinstance(x, str) or not x.strip() for x in self.source_refs
        ):
            raise ValueError("source references must be distinct, nonempty")
        _unit(self.prior_mean, "prior_mean")
        if isinstance(self.prior_strength, bool) or not isinstance(
            self.prior_strength, (int, float)
        ) or not math.isfinite(self.prior_strength) or self.prior_strength <= 0:
            raise ValueError("prior_strength must be finite positive")


@dataclass(frozen=True, slots=True)
class InquiryProposal:
    """Machine-side suggestion only; cannot call an external tool."""

    kind: str
    reason: str
    requires_authorization: bool = True


@dataclass(frozen=True, slots=True)
class Forecast:
    forecast_id: str
    sequence: int
    source_snapshot: str
    cutoff_tick: int
    situation: Situation
    action_probabilities: tuple[float, ...]
    semantic_probability: tuple[tuple[str, float], ...]
    partner_cooperation_probability: float | None
    success_probability_by_action: tuple[float, ...]
    inquiry: InquiryProposal | None
    digest: str


@dataclass(frozen=True, slots=True)
class ObservedEpisode:
    """Must come from a trusted host witness, not user/renderer/model prose."""

    event_id: str
    forecast_id: str
    tick: int
    situation: Situation
    action: str
    evidence_kind: EvidenceKind
    witness_ref: str
    evidence_precision: float = 1.0
    world_success: bool | None = None
    partner_cooperated: bool | None = None

    def __post_init__(self) -> None:
        for name in ("event_id", "forecast_id", "witness_ref"):
            _required(getattr(self, name), name)
        _required(self.action, "action")
        if type(self.tick) is not int or self.tick < 0:
            raise ValueError("episode tick must be nonnegative")
        if not isinstance(self.evidence_kind, EvidenceKind):
            raise TypeError("evidence_kind must be EvidenceKind")
        _unit(self.evidence_precision, "evidence_precision")
        for field in ("world_success", "partner_cooperated"):
            v = getattr(self, field)
            if v is not None and type(v) is not bool:
                raise TypeError(f"{field} must be boolean or None")
        if self.evidence_kind is EvidenceKind.RUNTIME_POLICY and (
            self.world_success is not None or self.partner_cooperated is not None
        ):
            raise ValueError("runtime policy record cannot attest world/partner outcomes")
        if self.partner_cooperated is not None and self.situation.partner_id is None:
            raise ValueError("partner response needs a named partner")


@dataclass(frozen=True, slots=True)
class PredictionError:
    forecast_id: str
    event_id: str
    multiclass_brier: float
    action_log_loss: float
    success_brier: float | None
    partner_brier: float | None
    semantic_shift: tuple[tuple[str, float, float], ...]


class PredictiveSelfLoop:
    """Read-only forecast then append-only *in-memory* episode admission.

    A caller must verify the witness. Merely supplying the evidence_kind enum
    does not constitute authentication. No BrainStore records are ever written.
    """

    def __init__(
        self,
        snapshot: SelfSnapshot,
        *,
        claims: tuple[SemanticClaim, ...] = (),
        context_strength: float = 5.0,
        partner_strength: float = 5.0,
    ):
        if not isinstance(snapshot, SelfSnapshot):
            raise TypeError("snapshot must be SelfSnapshot")
        if not isinstance(claims, tuple) or any(
            not isinstance(c, SemanticClaim) for c in claims
        ):
            raise TypeError("claims must be tuple of SemanticClaim")
        keys = [c.key for c in claims]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate semantic claim key")
        for c in claims:
            if not set(c.indicator_actions).issubset(snapshot.actions):
                raise ValueError("semantic indicators must be in the action space")
            if not set(c.source_refs).issubset(snapshot.admitted_refs):
                raise ValueError("unadmitted identity source reference")
        for name, v in (("context_strength", context_strength),
                        ("partner_strength", partner_strength)):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or (
                not math.isfinite(v) or v <= 0
            ):
                raise ValueError(f"{name} must be finite positive")
        self.snapshot = snapshot
        self.claims = claims
        self.context_strength = float(context_strength)
        self.partner_strength = float(partner_strength)
        self._open: dict[str, Forecast] = {}
        self._history: list[tuple[Forecast, ObservedEpisode, PredictionError]] = []
        self._sequence = 0
        self._last_observed_tick = snapshot.cutoff_tick

    @property
    def history(self) -> tuple[tuple[Forecast, ObservedEpisode, PredictionError], ...]:
        return tuple(self._history)

    def _claim_means(self) -> tuple[tuple[str, float], ...]:
        # Global changes require multiple *independent situation keys* and
        # high-precision, post-forecast evidence. Lower-quality episodes can
        # still inform context counts but never rewrite global self hypotheses.
        quality = [
            event for _, event, _ in self._history
            if event.evidence_precision >= .75
            and event.evidence_kind is EvidenceKind.WORLD_VERIFIED
        ]
        distinct_contexts = {event.situation.key for event in quality}
        result = []
        for claim in self.claims:
            p = claim.prior_mean
            if len(quality) >= MIN_SLOW_EPISODES and len(distinct_contexts) >= MIN_SLOW_CONTEXTS:
                positive = sum(
                    e.evidence_precision for e in quality if e.action in claim.indicator_actions
                )
                total = sum(e.evidence_precision for e in quality)
                estimate = (claim.prior_strength * p + positive) / (
                    claim.prior_strength + total
                )
                # Hard research bound; this is not a learned biological rule.
                p = max(0.0, min(1.0, max(
                    claim.prior_mean - .15,
                    min(claim.prior_mean + .15, estimate),
                )))
            result.append((claim.key, p))
        return tuple(result)

    def _semantic_prior(self, claim_probs: tuple[tuple[str, float], ...]) -> tuple[float, ...]:
        # Small bounded tilt based on source-grounded *testable indicators*.
        # All unindicated actions retain nonzero support from the recurrent base.
        probs = dict(claim_probs)
        action_weights = list(self.snapshot.base_probabilities)
        for claim in self.claims:
            direction = (probs[claim.key] - .5) * .5
            for idx, action in enumerate(self.snapshot.actions):
                if action in claim.indicator_actions:
                    action_weights[idx] *= 1.0 + direction
        return _normalized(tuple(action_weights))

    def _counts(self, situation: Situation) -> tuple[list[float], list[float]]:
        local = [0.0] * len(self.snapshot.actions)
        partner = [0.0] * len(self.snapshot.actions)
        for _, e, _ in self._history:
            idx = self.snapshot.actions.index(e.action)
            if e.situation.key == situation.key:
                local[idx] += e.evidence_precision
            if situation.partner_id is not None and e.situation.partner_id == situation.partner_id:
                partner[idx] += e.evidence_precision
        return local, partner

    def _partner_cooperation(self, partner_id: str | None) -> float | None:
        if partner_id is None:
            return None
        episodes = [
            e for _, e, _ in self._history
            if e.situation.partner_id == partner_id
            and e.partner_cooperated is not None
        ]
        positives = sum(e.evidence_precision for e in episodes if e.partner_cooperated)
        total = sum(e.evidence_precision for e in episodes)
        return (1.0 + positives) / (2.0 + total)

    def _world_success(self, situation: Situation) -> tuple[float, ...]:
        successes = [1.0] * len(self.snapshot.actions)
        totals = [2.0] * len(self.snapshot.actions)
        for _, e, _ in self._history:
            if e.world_success is not None and e.situation.key == situation.key:
                i = self.snapshot.actions.index(e.action)
                totals[i] += e.evidence_precision
                successes[i] += e.evidence_precision * float(e.world_success)
        return tuple(s / t for s, t in zip(successes, totals))

    def forecast(self, situation: Situation) -> Forecast:
        if not isinstance(situation, Situation):
            raise TypeError("situation must be Situation")
        beliefs = self._claim_means()
        prior = self._semantic_prior(beliefs)
        local, partner = self._counts(situation)
        context = _normalized(tuple(
            self.context_strength * p + c for p, c in zip(prior, local)
        ))
        probabilities = context
        if situation.partner_id is not None:
            probabilities = _normalized(tuple(
                self.partner_strength * p + c
                for p, c in zip(context, partner)
            ))
        n = len(probabilities)
        entropy = -sum(p * math.log(p) for p in probabilities if p > 0) / math.log(n)
        cooperation = self._partner_cooperation(situation.partner_id)
        inquiry = None
        if cooperation is not None and .35 <= cooperation <= .65:
            inquiry = InquiryProposal("ask_partner", "unresolved_observable_partner_response")
        elif entropy >= .80:
            inquiry = InquiryProposal("inspect_evidence", "high_predicted_action_uncertainty")
        self._sequence += 1
        fid = f"psl-{self._sequence:06d}"
        data = {
            "id": fid, "source": self.snapshot.digest, "situation": asdict(situation),
            "cutoff": self._last_observed_tick, "actions": self.snapshot.actions,
            "probabilities": probabilities, "beliefs": beliefs,
            "cooperation": cooperation,
            "success_probabilities": self._world_success(situation),
            "inquiry": asdict(inquiry) if inquiry else None,
        }
        result = Forecast(
            forecast_id=fid, sequence=self._sequence,
            source_snapshot=self.snapshot.digest,
            cutoff_tick=self._last_observed_tick,
            situation=situation,
            action_probabilities=probabilities,
            semantic_probability=beliefs,
            partner_cooperation_probability=cooperation,
            success_probability_by_action=self._world_success(situation),
            inquiry=inquiry, digest=_hash(data),
        )
        self._open[fid] = result
        return result

    def observe(self, episode: ObservedEpisode) -> PredictionError:
        if not isinstance(episode, ObservedEpisode):
            raise TypeError("episode must be ObservedEpisode")
        prior = self._open.get(episode.forecast_id)
        if prior is None:
            raise ValueError("unknown, consumed or unsealed forecast")
        if prior.situation != episode.situation:
            raise ValueError("situation changed between forecast and observation")
        if episode.action not in self.snapshot.actions:
            raise ValueError("observed action outside the declared action space")
        if episode.event_id in {e.event_id for _, e, _ in self._history}:
            raise ValueError("duplicated witnessed event")
        if episode.witness_ref in {e.witness_ref for _, e, _ in self._history}:
            raise ValueError("duplicated witness reference")
        if episode.tick <= max(prior.cutoff_tick, self._last_observed_tick):
            raise ValueError("observation is not later than the sealed forecast and previous event")
        i = self.snapshot.actions.index(episode.action)
        probs = prior.action_probabilities
        brier = sum((p - (1.0 if j == i else 0.0)) ** 2
                    for j, p in enumerate(probs))
        log_loss = -math.log(max(probs[i], 1e-15))
        success_brier = (
            (prior.success_probability_by_action[i] - float(episode.world_success)) ** 2
            if episode.world_success is not None else None
        )
        partner_brier = (
            (prior.partner_cooperation_probability - float(episode.partner_cooperated)) ** 2
            if episode.partner_cooperated is not None
            and prior.partner_cooperation_probability is not None else None
        )
        self._history.append((
            prior, episode, PredictionError(
                prior.forecast_id, episode.event_id, brier, log_loss,
                success_brier, partner_brier, (),
            )
        ))
        shifts = tuple(
            (key, dict(prior.semantic_probability)[key], dict(self._claim_means())[key])
            for key in (c.key for c in self.claims)
        )
        record = replace(self._history[-1][2], semantic_shift=shifts)
        self._history[-1] = (prior, episode, record)
        del self._open[episode.forecast_id]
        self._last_observed_tick = episode.tick
        return record

    def export_checkpoint(self) -> str:
        """Portable audit checkpoint after completed serial forecast/outcome pairs.

        The checkpoint is content-addressed for replay/integrity, not signed or
        authenticated. The caller must protect the actual source and witness
        records. Concurrent forecasts require a future versioned protocol.
        """
        if self._open:
            raise ValueError("all outstanding forecasts must be resolved before checkpoint")
        if any(f.sequence != index + 1
               for index, (f, _, _) in enumerate(self._history)):
            raise ValueError("v0.1 checkpoints require sequential forecast/observation")
        payload = {
            "protocol": PROTOCOL,
            "snapshot_digest": self.snapshot.digest,
            "claims_sha256": _hash([asdict(c) for c in self.claims]),
            "context_strength": self.context_strength,
            "partner_strength": self.partner_strength,
            "episodes": [
                {
                    "situation": asdict(f.situation),
                    "forecast_digest": f.digest,
                    "observation": asdict(e),
                    "error": asdict(error),
                }
                for f, e, error in self._history
            ],
            "audit_sha256": self.audit()["audit_sha256"],
        }
        return json.dumps({
            "payload": payload, "sha256": _hash(payload),
        }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @classmethod
    def restore_checkpoint(
        cls,
        snapshot: SelfSnapshot,
        *,
        claims: tuple[SemanticClaim, ...],
        checkpoint_json: str,
    ) -> "PredictiveSelfLoop":
        """Replay-and-verify portable records against an unchanged source state."""
        if not isinstance(checkpoint_json, str):
            raise TypeError("checkpoint_json must be a string")
        record = json.loads(checkpoint_json)
        if not isinstance(record, dict) or not isinstance(record.get("payload"), dict):
            raise ValueError("invalid checkpoint envelope")
        payload = record["payload"]
        if record.get("sha256") != _hash(payload):
            raise ValueError("checkpoint integrity mismatch")
        if payload.get("protocol") != PROTOCOL or payload.get("snapshot_digest") != snapshot.digest:
            raise ValueError("source state or protocol mismatch")
        if payload.get("claims_sha256") != _hash([asdict(c) for c in claims]):
            raise ValueError("semantic hypotheses do not match checkpoint")
        rebuilt = cls(
            snapshot, claims=claims,
            context_strength=payload["context_strength"],
            partner_strength=payload["partner_strength"],
        )
        for item in payload["episodes"]:
            forecast = rebuilt.forecast(Situation(**item["situation"]))
            if forecast.digest != item["forecast_digest"]:
                raise ValueError("replayed forecast diverged")
            details = dict(item["observation"])
            details["situation"] = Situation(**details["situation"])
            details["evidence_kind"] = EvidenceKind(details["evidence_kind"])
            error = rebuilt.observe(ObservedEpisode(**details))
            if _hash(asdict(error)) != _hash(item["error"]):
                raise ValueError("replayed scoring or posterior diverged")
        if rebuilt.audit()["audit_sha256"] != payload["audit_sha256"]:
            raise ValueError("replayed ledger digest diverged")
        return rebuilt

    def audit(self) -> dict[str, object]:
        """Structured engineer-only audit. Not safe to project as subject text."""
        records = [
            {
                "forecast": asdict(f), "observation": asdict(e),
                "scored_error": asdict(error),
            }
            for f, e, error in self._history
        ]
        return {
            "protocol": PROTOCOL,
            "snapshot_digest": self.snapshot.digest,
            "n_forecasts": self._sequence,
            "n_scored": len(self._history),
            "n_open": len(self._open),
            "semantic_posterior": dict(self._claim_means()),
            "scored": records,
            "audit_sha256": _hash(records),
        }
