"""Verified Laboratory body evidence into ORIGINAL Affectus/needs circuitry.

This is an opt-in causal research adapter, NOT adoption of the separately
proposed Spinoza affect-transition donor. The latter has not been source-pinned.
Neither first-person pain nor its appraisal may be generated from model text:
an actual verified Lab collision receipt and admitted autobiographical memory
are prerequisites. One original BrainStore, one neural policy and one subject
projector remain authoritative. Mapping a source-confirmed impact to a
bounded threat appraisal is a testable *hypothesis*, not certified realism.
"""
from __future__ import annotations

from dataclasses import dataclass

from .lab_home_bridge import _row
from .noesis_corpus_pilot import VerifiedBodyConsequence
from .organs import SixOrganRuntime


@dataclass(frozen=True, slots=True)
class VerifiedAffectReceipt:
    """Engineer audit only; never a renderer or subject-visible message."""

    body_memory_id: str
    source_action_memory_id: str
    source_domestic_event_hash: str
    status: str
    first_person: str
    threat_appraisal_applied: bool


class VerifiedLaboratoryAffectPilot:
    """Authenticated impact -> existing body channel -> existing needs.

    A true body-source transition is distinguished from the earlier
    world-event memory. Call only with a trusted Laboratory adapter
    and a host-approved verified physical collision.
    """

    def __init__(self, runtime: SixOrganRuntime, subject_port, *,
                 authorized: bool = False):
        if not isinstance(runtime, SixOrganRuntime):
            raise TypeError("One canonical six-organ runtime required")
        if authorized is not True:
            raise PermissionError("Host must authorize this source-bound pilot")
        if not hasattr(subject_port, "home") or not hasattr(subject_port, "habitat"):
            raise TypeError("Pinned real Laboratory home/physical source required")
        self._runtime = runtime
        self._subject = subject_port
        self._bridge = runtime.bind_laboratory(subject_port, authorized=True)
        if self._bridge.doctor is not runtime._port:
            raise RuntimeError("Affectus may not create another brain")

    def admit_impact(self, consequence: VerifiedBodyConsequence, *,
                     authorized: bool = False,
                     appraisal_enabled: bool = True) -> VerifiedAffectReceipt:
        """Admit once using world-signed collision + actual original memory.

        appraisal_enabled=False is a controlled lesion: the very same verified
        bodily sensation enters the same subject memory, but the speculative
        threat scalar is withheld. This is NOT an alternate neural selector.
        """
        if authorized is not True:
            raise PermissionError("Each bodily-affect admission needs host approval")
        if type(consequence) is not VerifiedBodyConsequence:
            raise TypeError("Expected the original verified Corpus result")
        if type(appraisal_enabled) is not bool:
            raise TypeError("Ablation choice must be explicit boolean")

        brain = self._runtime._port.brain
        memory = brain.store.get_memory(consequence.memory_id)
        if (memory is None or not memory["active"]
                or memory["text"] != consequence.first_person
                or memory["evidence_class"] != "lived_runtime_memory"):
            raise PermissionError("No matching lived source-action experience")
        self._subject.home.verify()  # validates the complete replayable body history
        with self._bridge.world._open() as db:
            physical, physical_hash = _row(
                db, "embodied_events", consequence.event_id
            )
            if (physical.get("kind") != "move"
                    or physical.get("after_station") != "station:shop:private"
                    or memory["source"] != "laboratory-home:action:" + physical_hash):
                raise PermissionError("Not a verified painful move")
            domestic, domestic_hash = _row(
                db, "domestic_events", "motion:" + physical_hash[:32]
            )
        subject = domestic.get("subject", {})
        checks = {
            "operation": domestic.get("op") == "walk",
            "movement_link": domestic.get("body_cursor") == physical_hash,
            "location": domestic.get("station") == "station:shop:private",
            "epoch": domestic.get("world_epoch") == physical.get("world_epoch"),
            "reflex": subject.get("spoken_aloud") == "Ow! My foot!",
            # The source-backed SubjectPort adds its separate rhythm
            # impression AFTER the domestic collision text. Requiring
            # complete equality would reject authentic first-person frames.
            "lived_text": (
                type(subject.get("inner")) is str
                and (consequence.first_person == subject["inner"]
                     or consequence.first_person.startswith(
                         subject["inner"] + " "
                     ))
            ),
            "reported_reflex": consequence.spoken_aloud == "Ow! My foot!",
        }
        invalid = tuple(k for k, valid in checks.items() if not valid)
        if invalid:
            # Expose only violated engineering predicates, not raw telemetry.
            raise PermissionError("Unverified impact source fields: "
                                  + ", ".join(invalid))

        # An event may only be admitted once, in ONE experimental arm.
        # Protect both the exact physical event and the intervention choice
        # against silent replays that alter the appraisal.
        base = "laboratory-body:impact:" + domestic_hash
        source = base + (":appraisal" if appraisal_enabled else ":lesion")
        other = base + (":lesion" if appraisal_enabled else ":appraisal")
        if any(m["source"] == other for m in brain.store.memories(False)):
            raise PermissionError("Cannot switch appraisal arm on a lived event")
        prior = [
            m for m in brain.store.memories(False) if m["source"] == source
        ]
        if prior:
            if len(prior) != 1 or not prior[0]["active"]:
                raise RuntimeError("Duplicate or archived body-event admission")
            return VerifiedAffectReceipt(
                body_memory_id=prior[0]["id"],
                source_action_memory_id=consequence.memory_id,
                source_domestic_event_hash=domestic_hash,
                status="already_admitted",
                first_person=prior[0]["text"],
                threat_appraisal_applied=appraisal_enabled,
            )

        # Both A/B arms enter IDENTICAL projected sensation. The only scalar
        # difference is the proposed threat-from-impact appraisal.
        # Neither numbers nor Laboratory records enter subject-visible text.
        ingested = self._runtime._port.ingest({
            "channel": "body",
            "signal": "pain",
            "level": 0.6,
            "source": source,
            "kind": "verified_bodily_collision",
            "arousal": 0.55,
            "threat": 0.65 if appraisal_enabled else 0.0,
            "valence": -0.3,
            "control": -0.2,
            "confidence": 1.0,
        })
        actual = brain.store.get_memory(ingested["memory_id"])
        if actual["text"] != ingested["ingress"]["subject_text"]:
            raise RuntimeError("Body experience was not canonically projected")
        return VerifiedAffectReceipt(
            body_memory_id=ingested["memory_id"],
            source_action_memory_id=consequence.memory_id,
            source_domestic_event_hash=domestic_hash,
            status="admitted",
            first_person=actual["text"],
            threat_appraisal_applied=appraisal_enabled,
        )
