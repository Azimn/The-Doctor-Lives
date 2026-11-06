"""Explicit six-organ FUNCTIONAL PORTS around the one canonical Pretorius brain.

This is a D2 interface milestone, not six independent agents, new minds, or
proof that all proposed mechanisms have been adopted. Every port delegates to
the EXISTING brain, ingress, and host boundaries. No new databases, clocks,
world authority or selectors are created.

Most importantly:
* Sensus is an existing single-stream percept adapter here. It is NOT the
  standalone multichannel Sensus donor.
* Synthetic Ipseity provides typed Doctor projection here. Durable admission
  belongs to the separately reviewed optional Synthetic Ipseity session.
* Corpus observes body-supplied signals; it cannot command a body or assert
  physical effects.
* Affectus reads existing affective/needs influences. It is not a second
  emotion engine or neural/action policy.

This is an in-process developer/host interface, NOT a security sandbox.
An authorized host must still enforce real source attestation and no-bypass
access at its model/tool edges before D3 can be called complete.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Any, Callable, Mapping

from .chassis import HostRecollectionController, PretoriusBrainPort
from .models import SubjectFrame


@dataclass(frozen=True, slots=True)
class OrganDescriptor:
    name: str
    state: str
    implementation: str
    limitation: str


# A truthful state inventory, not six auto-promoted "implemented" labels.
ORGAN_REGISTRY: tuple[OrganDescriptor, ...] = (
    OrganDescriptor(
        "Noesis", "adapter-backed", "PretoriusBrainPort.cognition + recurrent selector",
        "Host invocation is not autonomous planning or world action.",
    ),
    OrganDescriptor(
        "Mnemosyne", "adapter-backed",
        "BrainStore memory + host-granted first-person recollection",
        "Experimental P4-P6D recollection is not the default.",
    ),
    OrganDescriptor(
        "Affectus", "mapped", "Existing needs and state-to-policy pressure",
        "No separate qualified affect engine or distinct state writer.",
    ),
    OrganDescriptor(
        "Sensus", "mapped", "Existing first-person world/tool ingress",
        "No standalone Sensus multichannel binding donor has been adopted.",
    ),
    OrganDescriptor(
        "Synthetic Ipseity", "adapter-backed",
        "Doctor SubjectFrame projection; optional durable donor adapter",
        "Typed projection alone is not universal durable admission.",
    ),
    OrganDescriptor(
        "Corpus", "mapped", "Existing bodily ingress and interoception",
        "Environment owns physical state; there is no motor authority here.",
    ),
)


@dataclass(frozen=True, slots=True)
class AcquisitionReceipt:
    """Host-only confirmation of a single admitted first-person acquisition."""

    tick: int
    event_id: str
    memory_id: str
    first_person: str

    @classmethod
    def from_brain(cls, result: Mapping[str, Any]) -> "AcquisitionReceipt":
        # Never accidentally expose the brain's neural/action diagnostics.
        return cls(
            tick=int(result["tick"]),
            event_id=str(result["event_id"]),
            memory_id=str(result["memory_id"]),
            first_person=str(result["ingress"]["subject_text"]),
        )


@dataclass(frozen=True, slots=True)
class CognitiveProposal:
    """An existing Noesis tendency, NOT physical-world action authorization."""

    policy_decision_id: str
    thought_id: str
    selected_tendency: str
    initiated_by: str = "host"


@dataclass(frozen=True, slots=True)
class CognitivePulse:
    """Engineer-only record of a HOST-SCHEDULED existing brain heartbeat."""

    ticks: int
    store_tick: int
    thought_count: int
    selected_tendencies: tuple[str, ...]
    initiated_by: str = "host"


@dataclass(frozen=True, slots=True)
class SleepReplayReport:
    """Engineer-only record of existing mnemonic replay without waking time."""

    requested_ticks: int
    fragments: int
    store_tick: int
    neural_tick_after: int
    initiated_by: str = "host"


@dataclass(frozen=True, slots=True)
class AffectiveInfluence:
    """Engineer-only read of EXISTING need-mediated selection influence."""

    state_version: int
    felt_bands: tuple[tuple[str, str], ...]
    need_policy_deltas: tuple[tuple[str, float], ...]


class NoesisOrgan:
    def __init__(self, port: PretoriusBrainPort):
        self._port = port

    def deliberate(self, *, host_trigger: str = "six-organ-host") -> CognitiveProposal:
        """Advance the one existing neural selection path, never execute action."""
        if (
            type(host_trigger) is not str
            or not re.fullmatch(r"[a-z][a-z0-9_-]{1,63}", host_trigger)
        ):
            raise ValueError("Noesis needs a bounded, host-authored trigger label")
        decision = self._port.cognition(host_trigger)
        return CognitiveProposal(
            policy_decision_id=str(decision["policy_decision_id"]),
            thought_id=str(decision["id"]),
            selected_tendency=str(decision["selected_action"]),
        )


    def deliberate_feasible_actions(
        self, *, observation_memory_id: str,
        eligible_read_memory_ids: tuple[str, ...],
        feasible_actions: tuple[str, ...],
        learning_enabled: bool = True, neural_prior_enabled: bool = True,
        outcome_learning_enabled: bool = False,
        eligible_outcome_memory_ids: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        """Noesis, not the host, ranks concrete offers using lived evidence.

        The world still supplies physical feasibility and separately authorizes
        any execution. The same original brain/store own decision and thought.
        """
        return self._port.brain.choose_feasible_action(
            observation_memory_id=observation_memory_id,
            eligible_read_memory_ids=eligible_read_memory_ids,
            feasible_actions=feasible_actions,
            learning_enabled=learning_enabled,
            neural_prior_enabled=neural_prior_enabled,
            outcome_learning_enabled=outcome_learning_enabled,
            eligible_outcome_memory_ids=eligible_outcome_memory_ids,
        )

    def pulse(self, ticks: int = 1) -> CognitivePulse:
        """Advance existing homeostatic time and conditional neural cognition.

        A heartbeat may produce ZERO thoughts; the host's pulse is an
        opportunity, not fabricated evidence of autonomous initiative.
        Never returns raw need state, source IDs, policy scores or thoughts
        to a subject renderer. No world action is attempted.
        """
        if type(ticks) is not int or not 1 <= ticks <= 24:
            raise ValueError("Noesis pulse must be 1 to 24 bounded host ticks")
        report = self._port.heartbeat(ticks)
        thoughts = report["thoughts"]
        return CognitivePulse(
            ticks=int(report["ticks"]),
            store_tick=int(report["tick"]),
            thought_count=len(thoughts),
            selected_tendencies=tuple(
                str(thought["selected_action"]) for thought in thoughts
            ),
        )


class MnemosyneOrgan:
    def __init__(self, port: PretoriusBrainPort):
        self._port = port

    def opt_in_endogenous_recollection(self):
        """Opt-in PR #59 mechanism, one policy/store and host capability.

        An internal concern, not a caller-supplied question, is required.
        This does not declare production autonomy or renderer admission.
        """
        from .mnemosyne_pilot import MnemosyneEndogenousPilot
        return MnemosyneEndogenousPilot(self._port, enabled=True)

    def bind_host_recollection(
        self, choose_internal_question: Callable[[], str]
    ) -> HostRecollectionController:
        """The host verifies authorship; this does NOT assert autonomous recall."""
        return self._port.bind_recollection_controller(choose_internal_question)

    def recollect(self, controller: HostRecollectionController) -> SubjectFrame:
        """Use the original one-use question/state-bound grant and typed frame."""
        if (
            not isinstance(controller, HostRecollectionController)
            or controller._port is not self._port
        ):
            raise PermissionError("Recollection controller belongs to another brain")
        return controller.recollect_frame()


    def replay_sleep(self, ticks: int = 12) -> SleepReplayReport:
        """Run the existing neural/memory sleep path without world-time advance.

        No extra dreaming system, state store, or subjective memory admission.
        Generated fragments remain engineering records unless separately
        acquired by the canonical first-person boundary.
        """
        if type(ticks) is not int or not 1 <= ticks <= 24:
            raise ValueError("Mnemosyne replay must be 1 to 24 bounded ticks")
        report = self._port.sleep(ticks)
        return SleepReplayReport(
            requested_ticks=int(report["ticks"]),
            fragments=int(report["fragments"]),
            store_tick=int(report["store_tick"]),
            neural_tick_after=int(self._port.brain.neural.tick),
        )


class AffectusOrgan:
    def __init__(self, port: PretoriusBrainPort):
        self._port = port

    def opt_in_laboratory_body_evidence(self, runtime, subject_port, *,
                                        authorized: bool = False):
        """Prototype from verified world impact through ORIGINAL needs circuit.

        This does not adopt the unpinned Spinoza transition prototype or
        authorize a second selector. It is never active by default.
        """
        if runtime._port is not self._port:
            raise PermissionError("Affectus must use its own canonical brain")
        from .affectus_lab_pilot import VerifiedLaboratoryAffectPilot
        return VerifiedLaboratoryAffectPilot(
            runtime, subject_port, authorized=authorized
        )

    def read_motivational_influence(self) -> AffectiveInfluence:
        """Read existing need influence; do not introduce a second decision rule.

        This result is for developer-side causal inspection, never the model
        or first-person renderer. Felt words require Ipseity projection.
        """
        brain = self._port.brain
        _, _, audit = brain._state_policy_scores([])
        needs = audit["families"]["needs"]
        return AffectiveInfluence(
            state_version=brain.store.state_version,
            felt_bands=tuple(sorted(brain._felt_state().items())),
            need_policy_deltas=tuple(sorted((k, float(v)) for k, v in needs.items())),
        )


class SensusOrgan:
    def __init__(self, port: PretoriusBrainPort):
        self._port = port

    def acquire_existing_percept(
        self, raw: Mapping[str, Any], *, host_authorized: bool = False
    ) -> AcquisitionReceipt:
        """Use approved world/tool single-stream projection, NOT donor fusion.

        The opt-in indicates the caller has checked provider authority. It
        is not itself an attestation token or proof of world facts.
        """
        if host_authorized is not True:
            raise PermissionError("Host must explicitly authorize percept ingress")
        if not isinstance(raw, Mapping) or raw.get("channel") not in ("world", "tool"):
            raise ValueError("Sensus receives only world/tool percepts")
        return AcquisitionReceipt.from_brain(
            self._port._ingest_authorized_sensus(raw, organ=self)
        )

    def opt_in_multichannel_pilot(self):
        """Use the reviewed Sensus binder only in an explicitly tested host.

        Import and donor integrity verification occur on demand; the default
        single-stream Sensus path and canonical brain remain unchanged.
        """
        from .sensus_pilot import SensusCandidatePilot
        return SensusCandidatePilot(self)


class SyntheticIpseityOrgan:
    def __init__(self, port: PretoriusBrainPort):
        self._port = port

    def project_subject_frame(self, user_input: str | None = None) -> SubjectFrame:
        """Typed, subject-only frame, prior to an authorized admission/outbox."""
        return self._port.subject_frame(user_input)

    def open_durable_delivery(self, *, renderer: Callable[[str], str],
                              epoch_id: str = "pretorius-lifetime-v1"):
        """Opt-in authoritative output route using this SAME brain port.

        Reuse the reviewed Synthetic Ipseity v0.9.11 host. Its durable outbox
        tracks delivery only, never autobiographical state or identity. This
        path does NOT install a global no-bypass production sandbox.
        """
        from .ipseity_integration import DoctorSyntheticIpseitySession

        return DoctorSyntheticIpseitySession(
            self._port.brain.state_dir,
            renderer=renderer,
            epoch_id=epoch_id,
            brain_port=self._port,
        )


class CorpusOrgan:
    def __init__(self, port: PretoriusBrainPort):
        self._port = port

    def acquire_body_signal(
        self, raw: Mapping[str, Any], *, host_authorized: bool = False
    ) -> AcquisitionReceipt:
        """Project a provider's bounded bodily reading, never act on hardware."""
        if host_authorized is not True:
            raise PermissionError("Host must explicitly authorize body ingress")
        if not isinstance(raw, Mapping) or raw.get("channel") != "body":
            raise ValueError("Corpus requires an explicit body-channel reading")
        return AcquisitionReceipt.from_brain(self._port.ingest(raw))


class SixOrganRuntime:
    """One brain with six in-process typed functional seams.

    Does not replace the default host until separate D3-D11 acceptance gates.
    No organ owns independent state or has direct world/robot authorization.
    """

    def __init__(self, port: PretoriusBrainPort):
        if not isinstance(port, PretoriusBrainPort):
            raise TypeError("SixOrganRuntime requires the canonical Pretorius brain port")
        self._port = port
        self.noesis = NoesisOrgan(port)
        self.mnemosyne = MnemosyneOrgan(port)
        self.affectus = AffectusOrgan(port)
        self.sensus = SensusOrgan(port)
        self.synthetic_ipseity = SyntheticIpseityOrgan(port)
        self.corpus = CorpusOrgan(port)

    @classmethod
    def open(
        cls, state_dir: str | Path, *, neural_config: dict[str, Any] | None = None
    ) -> "SixOrganRuntime":
        return cls(PretoriusBrainPort(state_dir, neural_config=neural_config))

    @property
    def organ_registry(self) -> tuple[OrganDescriptor, ...]:
        return ORGAN_REGISTRY

    def bind_laboratory(self, subject_port, *, authorized: bool = False):
        """Attach the existing source-verified Laboratory bridge to this brain.

        No second Laboratory, simulated world, or action planner is created.
        The world retains receipt authority; the brain retains memory authority.
        A host must separately authorize each world action.
        """
        from .lab_home_bridge import DoctorHomeBridge

        return DoctorHomeBridge(
            self._port, subject_port, authorized=authorized
        )

    def bind_source_verified_book_search(self, embodied_port, *,
                                         authorized: bool = False):
        """Opt-in PR #61 source-memory/physical-task experiment.

        The verified Laboratory owns its book/world receipts, this same
        PretoriusBrainPort owns all first-person memory and policy. The task
        reservation journal is engineering execution state, not another brain.
        Host authors the task: no autonomous initiative or superiority claim.
        """
        from .six_organ_book_task import VerifiedBookSearch
        return VerifiedBookSearch(self, embodied_port, authorized=authorized)

    def bind_causal_laboratory(self, subject_port, *, authorized: bool = False):
        """Experimental Noesis-choice / host-authorized Corpus action handoff.

        Reuses the same verified DoctorHomeBridge, original neural selector,
        source-attested world consequences and original BrainStore.
        A selected abstract tendency alone NEVER permits physical action.
        """
        from .noesis_corpus_pilot import NoesisCorpusLaboratoryPilot
        return NoesisCorpusLaboratoryPilot(
            self, subject_port, authorized=authorized
        )

    def bind_conclave(self, *, enabled: bool = False):
        """Opt-in bounded esoteric interpretation sharing this BrainStore.

        No extra mind, selector, autobiographical write path, renderer ingress,
        or physical authority. Host admission checks remain mandatory.
        """
        from .conclave import Conclave
        return Conclave(self._port.brain.store, enabled=enabled)

    def checkpoint(self) -> dict[str, Any]:
        """Persist the SAME canonical neural checkpoint and brain state.

        Existing PretoriusBrainPort.save controls format and persistence.
        This does not create a six-organ checkpoint or migration format.
        """
        return self._port.save()

    def status(self) -> dict[str, Any]:
        """Engineer-only inventory, deliberately separate from subject access."""
        return {
            "architecture": "pretorius-six-organ-target.v1",
            "qualification": "D2 opt-in adapter prototype; NOT six-organ production",
            "brain_schema": self._port.SCHEMA,
            "organs": [
                {
                    "name": organ.name,
                    "state": organ.state,
                    "implementation": organ.implementation,
                    "limitation": organ.limitation,
                }
                for organ in ORGAN_REGISTRY
            ],
            "canonical_state_digest": self._port.brain.store.digest(),
        }
