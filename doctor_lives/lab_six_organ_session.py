"""Bounded experimental Laboratory cycle across all SIX canonical organ ports.

NOT a production entrypoint or a claim of globally enforced model sandbox.
The user-facing callback ONLY receives durable, first-person Ipseity output.
Physical world authority is exclusively the pinned Laboratory SubjectPort.
All weather continuation belongs to the same canonical BrainStore. This host
may propose a destination based on the original recurrent selected tendency,
but the Laboratory independently authorizes and verifies every movement.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from unittest.mock import patch

from .canonical_affectus_weather import CanonicalWeather
from .noesis_corpus_pilot import HostCorpusOffer
from .organs import SixOrganRuntime

_G = 0.05  # Preserved, PREDECLARED PR #90 experimental coupling. No tuning.
_VALID = {
    "station:threshold": "threshold", "station:hall": "hall",
    "station:center": "center", "station:kitchen": "kitchen",
    "station:bedroom": "bedroom", "station:parlor": "parlor",
    "station:shop:private": "private shop",
    "station:shop:public": "public shop",
    "station:shelf:1": "shelf one", "station:shelf:2": "shelf two",
    "station:shelf:3": "shelf three", "station:bench": "bench",
    "station:corner:nw": "northwest corner",
    "station:corner:se": "southeast corner",
    "station:chamber:entry": "chamber entrance",
    "station:chamber:table": "chamber table",
}


@dataclass(frozen=True)
class SixOrganCycleReceipt:
    tick: int
    ports_used: tuple[str, ...]
    scene_admitted: int
    scene_vetoed: tuple[str, ...]
    body_verified: bool
    canonical_weather_digest: str
    mnemonic_decision: str
    selected_tendency: str
    movement_status: str
    destination: str | None
    subjective_delivery_count: int
    host_provided_goal: bool
    self_selected_goal_proven: bool


@contextmanager
def original_noesis_weather(organ, modulation):
    """Apply ONE bounded experimental source to the existing native selector.

    The only decision authority remains PretoriusBrain.think. The patch lasts
    for a single synchronous cognition call, not installed on any entrypoint.
    Other donor modulation channels are NOT reported as used.
    """
    brain = organ._port.brain
    original = brain._state_policy_scores

    def adjusted(*args, **kwargs):
        base, scores, audit = original(*args, **kwargs)
        delta = _G * modulation.exploration_bias
        changed = dict(scores)
        changed["explore"] = max(1e-9, changed["explore"] + delta)
        changed["persist"] = max(1e-9, changed["persist"] - delta)
        norm = sum(changed.values())
        changed = {key: value / norm for key, value in changed.items()}
        audit = dict(audit)
        audit["lab_experiment_weather"] = {
            "modulation_consumed": "exploration_bias", "delta": delta,
            "not_subject_visible": True,
        }
        return base, changed, audit

    with patch.object(brain, "_state_policy_scores", side_effect=adjusted):
        yield


class SixOrganLaboratoryCycle:
    """Single-brain research host with all six ports invoked each cycle.

    No task text, action target or engineer diagnostic is sent to the
    renderer. The first-person gate is the ONLY callback destination.
    """

    def __init__(self, runtime: SixOrganRuntime, subject_port, *,
                 affectus_source: str | Path, renderer: Callable[[str], str],
                 authorized: bool = False, seed: int = 1842):
        if not isinstance(runtime, SixOrganRuntime) or authorized is not True:
            raise PermissionError("Explicit same-brain research host authorization")
        if not callable(renderer):
            raise TypeError("Renderer must be a callback accepting subject text")
        self.runtime = runtime
        self.subject = subject_port
        self.bridge = runtime.bind_laboratory(subject_port, authorized=True)
        self.corpus = runtime.bind_causal_laboratory(
            subject_port, authorized=True
        )
        self.affect = runtime.affectus.opt_in_laboratory_body_evidence(
            runtime, subject_port, authorized=True,
        )
        self.sensus = runtime.sensus.opt_in_multichannel_pilot()
        self.mnemosyne = runtime.mnemosyne.opt_in_endogenous_recollection()
        self.weather = CanonicalWeather(
            runtime._port, donor_root=affectus_source, seed=seed,
        )
        self.ipseity = runtime.synthetic_ipseity.open_durable_delivery(
            renderer=renderer,
        )
        if len({
            id(runtime.noesis._port), id(runtime.mnemosyne._port),
            id(runtime.affectus._port), id(runtime.sensus._port),
            id(runtime.corpus._port), id(runtime.synthetic_ipseity._port),
        }) != 1:
            raise RuntimeError("Six organs do not share one brain")

    def close(self) -> None:
        self.ipseity.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _canonical_recent_action(self):
        memories = [
            m for m in self.runtime._port.brain.store.memories()
            if m["source"].startswith("laboratory-home:action:")
        ]
        # BrainStore.memories() orders newest first by updated/created tick.
        return memories[0] if memories else None

    def _select_internal_affordance(self, tendency: str, station: str):
        """Only an internal explore tendency may originate locomotion.

        The verified world supplies *feasibility* (not goals). This is a
        bounded deterministic affordance allocator, NOT an extra neural
        selector, task controller or authored narrative intention.
        """
        if tendency != "explore":
            return None
        from pretorius_lab.embodied_access import STATIONS
        if station not in STATIONS:
            raise PermissionError("Outside source-reviewed Laboratory affordances")
        options = STATIONS[station][1]
        if not options:
            return None
        # Prefer the least-experienced admissible option using only the
        # canonical brain's LIVED memory text. No privileged destination
        # lookup or task-solution oracle enters the cognitive selector.
        prior = [
            m["text"].lower() for m in self.runtime._port.brain.store.memories()
            if m["source"].startswith("laboratory-home:action:")
        ]
        return min(
            options,
            key=lambda destination: (
                sum(_VALID[destination] in text for text in prior),
                destination,
            ),
        )

    def cycle(self, *, authorized_world_action: bool = False) -> SixOrganCycleReceipt:
        """One real cycle, fail-closed if either pinned donor is unavailable."""
        if type(authorized_world_action) is not bool:
            raise TypeError("A world permission is a typed host decision")
        tick = self.weather.tick + 1
        if tick == 0:
            tick = 1

        # SENSUS: authenticated Laboratory observation, then pinned
        # candidate scene fusion of that very same physical location.
        actual = self.bridge.observe()
        evidence = self.runtime._port.brain.store.get_memory(actual["memory_id"])
        if (evidence is None or not evidence["active"]
                or not evidence["source"].startswith("laboratory-home:observe:")):
            raise RuntimeError("No independently verified world observation")
        state = self.subject.embodied.verify()
        station = state["station"]
        if station not in _VALID:
            raise PermissionError("Unreviewed Laboratory station")
        donor = self.sensus._donor
        ref = evidence["source"]
        claim = donor.Percept(
            event_id="six_cycle_" + str(tick) + "_location",
            channel="vision",
            evidence=donor.Evidence.OBSERVED,
            source_ref=ref, tick=tick,
            attribute="room", value=_VALID[station],
            confidence=1.0, object_hint="room",
            features=(("type", "room"),),
        )
        scene = self.sensus.acquire(
            tick, (claim,), trusted_refs=frozenset({ref}),
            verified_world_refs=frozenset({ref}),
        )

        # CORPUS: read the real independently verified body before acting.
        self.subject.home.verify()
        body = self.subject.home.audit_state()["body"]
        if not isinstance(body, dict):
            raise RuntimeError("Missing source-verified physical body")

        # AFFECTUS: weather is durable in canonical BrainStore, and its
        # driver is a bounded trusted host opportunity. A realized world
        # consequence remains recorded independently, never forged.
        previous = self._canonical_recent_action()
        kind = "rest_density"
        magnitude = 0.0
        src = "host-opportunity:" + str(tick)
        if previous is not None:
            kind = "goal_impediment" if "foot" in previous["text"].lower() else "goal_progress"
            magnitude = 1.0
            src = previous["source"]
        self.weather.step(
            tick, (self.weather.driver(kind, magnitude, src),),
            authorized=True,
        )

        # MNEMOSYNE: policy selects own question from a canonical concern,
        # no host-authored question or privileged world fact.
        mnemonic = self.mnemosyne.deliberate()
        if mnemonic.action == "recall":
            self.mnemosyne.reflect_selected_recollection()

        # NOESIS: unchanged native neural selector, temporarily modulated.
        with original_noesis_weather(
            self.runtime.noesis, self.weather.modulation(),
        ):
            proposal = self.runtime.noesis.deliberate(
                host_trigger="six_organ_lab_cycle",
            )

        # CORPUS: no direct model/world actuation, only trusted-authorized
        # affordance and world verified source receipt.
        destination = self._select_internal_affordance(
            proposal.selected_tendency, station,
        )
        status = "not_executed"
        if destination is not None and authorized_world_action:
            receipt = self.corpus.act(
                proposal,
                HostCorpusOffer(
                    proposal.selected_tendency, "walk", destination,
                ),
                authorized=True,
            )
            status = receipt.status
            if receipt.spoken_aloud == "Ow! My foot!":
                self.affect.admit_impact(receipt, authorized=True)

        # IPSEITY: never call an LLM/renderer directly with audit/context.
        # In-process host conventions alone are not a universal D3 sandbox.
        if self.ipseity.pending_count():
            raise RuntimeError("Unacknowledged subject frame must reconcile")
        before = self.ipseity.pending_count()
        self.ipseity.publish_current()
        self.ipseity.deliver_next(now_ms=tick * 100_000)
        after = self.ipseity.pending_count()
        if after != 0 or before != 0:
            raise RuntimeError("Subject delivery failed to drain durable gate")

        return SixOrganCycleReceipt(
            tick=tick,
            ports_used=("Sensus", "Corpus", "Affectus", "Mnemosyne",
                        "Noesis", "Synthetic Ipseity"),
            scene_admitted=len(scene.admitted),
            scene_vetoed=scene.vetoed_attributes,
            body_verified=True,
            canonical_weather_digest=self.weather.snapshot_digest(),
            mnemonic_decision=mnemonic.action,
            selected_tendency=proposal.selected_tendency,
            movement_status=status,
            destination=destination if status != "not_executed" else None,
            subjective_delivery_count=1,
            host_provided_goal=False,
            # Selected abstract tendency + affordance is not by itself
            # proof of genuine independent intention or sustained goals.
            self_selected_goal_proven=False,
        )
