"""Opt-in, isolated THREE-COMPONENT Pretorius preview host.

Sensus is the evidence-preserving scene binder, Doctor's EXISTING policy owns
endogenous-recall selection, and Synthetic Ipseity is the ONLY renderer path.
This is a preview, not a production promotion or an authorized rewrite of
the Sensus donor's separately blinded experiments.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import time
from typing import Callable, Iterable
from uuid import uuid4

from .ipseity_integration import DoctorSyntheticIpseitySession
from .ipseity_local import build_local_renderer
from .subject_inquiry import validate_subject_inquiry

try:
    from sensus_artificialis import Evidence, Percept, Sensus, SCHEMA_VERSION
except ImportError as exc:
    raise ImportError(
        "Three-organ preview requires the exact reviewed Sensus donor on PYTHONPATH"
    ) from exc


_EXPECTED_SENSUS_SCHEMA = "sensus.scene.v0.1"
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
        super().__init__(
            path, renderer=renderer,
            epoch_id="pretorius-three-organ-preview-v1",
            neural_config=neural_config,
        )
        self._sensus = Sensus()
        self._scene_tick = self._doctor.brain.store.tick + 1
        self._internal_question: str | None = None
        self.bind_recollection_controller(self._choose_internal_question)

    def _choose_internal_question(self) -> str:
        if self._internal_question is None:
            raise RuntimeError("No policy-selected internal recollection pending")
        return self._internal_question

    def _record_conflict_as_epistemic_concern(self, attribute: str) -> str:
        if not _SAFE_OBSERVED_PHRASE.fullmatch(attribute):
            raise ValueError("Untrusted conflict attribute cannot form a subject cue")
        description = "the " + attribute.strip()
        validate_subject_inquiry(f"What do I remember of {description}?")
        identifier = "preview-gap-" + uuid4().hex
        brain = self._doctor.brain
        with brain.store.transaction() as conn:
            conn.execute(
                """INSERT INTO concerns
                (id,created_tick,updated_tick,description,status,importance,
                 uncertainty,actor,source)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (identifier, brain.store.tick, brain.store.tick, description,
                 "open", 0.95, 0.95, "PREVIEW_HOST", "preview_sensus_conflict"),
            )
            brain.store.bump_state_version(conn)
        return identifier

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

        scene = self._sensus.step(self._scene_tick, items)
        self._scene_tick += 1
        admitted = 0
        gap_ids = []
        latest_reported_message: str | None = None
        for obj in scene.objects:
            if obj.contested_attributes:
                # Conservative: withhold ALL claims about a contested object,
                # including non-contested fields, rather than laundering them.
                for conflict in scene.conflicts:
                    if conflict.object_id == obj.object_id and conflict.status == "vetoed":
                        observed_sources = [
                            claim for claim in obj.claims
                            if claim.attribute == conflict.attribute
                            and claim.evidence is Evidence.OBSERVED
                        ]
                        if len(observed_sources) >= 2:
                            gap_ids.append(
                                self._record_conflict_as_epistemic_concern(
                                    conflict.attribute
                                )
                            )
                continue
            for claim in obj.claims:
                if claim.evidence is Evidence.OBSERVED:
                    self.ingest({
                        "channel": "world",
                        "text": f"The {claim.attribute} is {claim.value}.",
                        "source": "preview-verified-world:" + claim.source_ref,
                        "novelty": 0.35,
                    })
                    admitted += 1
                elif claim.evidence is Evidence.REPORTED:
                    self.ingest({
                        "channel": "user",
                        "actor": "User",
                        "source": "preview-verified-user:" + claim.source_ref,
                        "text": claim.value,
                    })
                    latest_reported_message = claim.value
                    admitted += 1
                # Inferred, remembered and interoceptive claims are NOT
                # rewritten as world observations or autobiographical memory.

        decision = self._doctor.brain.research_endogenous_recall(
            enabled=True, persist=True, preview_live=True
        )
        if decision["selected_action"] == "recall":
            self._internal_question = decision["question"]
            self.publish_recollection()
        else:
            self._internal_question = None
            # A general memory rank can bury a fresh User statement under
            # inherited identity roots. Use Doctor's existing FIRST-PERSON
            # user-input projector for the already-attested communication.
            # This creates no second memory or direct model-input bypass.
            self.publish_current(user_input=latest_reported_message)
        delivery = self.deliver_next(now_ms=now_ms)
        if delivery is None:
            raise RuntimeError("First-person frame leased; delivery not acknowledged")
        return {
            "schema": "pretorius.three-organ-preview.v1",
            "answer": delivery.response,
            "scene_schema": scene.schema_version,
            "scene_conflicts": len(scene.conflicts),
            "admitted_percepts": admitted,
            "new_epistemic_gap_ids": gap_ids,
            "endogenous_decision_id": decision["decision_id"],
            "endogenous_action": decision["selected_action"],
            "recollection_selected": decision["selected_action"] == "recall",
            "ipseity_pending": self.pending_count(),
            "engineer_only": True,
            "not_production_approved": True,
        }

    def resume_preview(self, *, now_ms: int) -> str:
        """Retry pending renderer delivery; NEVER replay any Percept or decision."""
        if not self.pending_count():
            raise RuntimeError("No pending first-person delivery")
        delivery = self.deliver_next(now_ms=now_ms)
        if delivery is None:
            raise RuntimeError("A prior worker holds the subject-frame lease")
        return delivery.response


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
