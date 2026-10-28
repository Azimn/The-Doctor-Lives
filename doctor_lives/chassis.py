from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Mapping

from .cognition import PretoriusBrain
from .ingress import IngressProjectionError, project_raw_ingress
from .models import SubjectFrame
from .projection import ProjectionContext
from .subject_inquiry import (
    SubjectInquiryAuthorizationError,
    validate_subject_inquiry,
)


class HostRecollectionController:
    """Host-owned invocation capability, never a model-facing tool.

    The host must provide a trusted zero-argument callback that selects an
    internal recollection question. The callback's actual authorship is not
    certified here, so using a forced question is only a positive control.
    """

    def __init__(self, port: "PretoriusBrainPort", choose_question: Callable[[], str]):
        self._port = port
        self._choose_question = choose_question

    def recollect_frame(self):
        """Return the Doctor-created typed SubjectFrame, with a one-use permit."""
        # This trusted in-process capability supplies the typed frame directly
        # to Synthetic Ipseity without rebuilding a subject frame from strings.
        question = validate_subject_inquiry(self._choose_question())
        permit = self._port._issue_subject_inquiry(self, question)
        return self._port._subject_recollection_frame(question, _authorization=permit)

    def recollect(self) -> dict[str, Any]:
        """Return subject-only text for renderer-neutral chassis consumers."""
        frame = self.recollect_frame()
        return {
            "schema": "the-doctor-lives.subject-recollection.v1",
            "subject_frame": list(frame.renderer_context()),
        }


class PretoriusBrainPort:
    """Stable, renderer-neutral boundary for an arbitrary agent chassis.

    The chassis may deliver observations and ask for cognition or a render
    request. It does not receive direct authority to rewrite identity evidence,
    provenance, memory classification, or the recurrent substrate.
    """

    SCHEMA = "the-doctor-lives.brain-port.v1"

    def __init__(self, state_dir: str | Path, *, neural_config: dict[str, Any] | None = None):
        self.brain = PretoriusBrain(state_dir, neural_config=neural_config)
        self._recollection_controller: HostRecollectionController | None = None
        self._pending_subject_inquiry: tuple[object, str, str, int] | None = None
        # Host-only physical admission capabilities. This is intentionally
        # NOT a public model API or an alternative memory store.
        self._verified_laboratory_bridges: set[object] = set()

    def ingest(self, event: Mapping[str, Any]) -> dict[str, Any]:
        """Untrusted chassis input may NOT assert firsthand physical truth.

        WORLD text becomes explicitly attributed external report evidence;
        WORLD percept fields cannot be admitted through this public entrypoint.
        Only a separately authorized, source-backed Laboratory bridge can
        admit actual physical lived observations.
        """
        return self._project_and_ingest(event, laboratory_verified=False)

    def _register_laboratory_bridge(self, bridge: object) -> None:
        """Trusted in-process host registration; NOT a security sandbox."""
        from .lab_home_bridge import DoctorHomeBridge

        if type(bridge) is not DoctorHomeBridge or bridge.doctor is not self:
            raise PermissionError("Only a bound original Laboratory host can register")
        if bridge.subject.habitat is not bridge.world:
            raise PermissionError("Laboratory subject and physical world do not match")
        bridge.subject.verify()
        self._verified_laboratory_bridges.add(bridge)

    def _ingest_verified_laboratory(self, event: Mapping[str, Any], *,
                                    bridge: object) -> dict[str, Any]:
        """Accept a one-use verified host handoff, never an asserted source key.

        The original DoctorHomeBridge verifies actual world/percept or action
        receipts before issuing this in-process handoff. An arbitrary caller
        supplying a syntactically valid Laboratory source string is denied.
        """
        from .lab_home_bridge import DoctorHomeBridge

        if (type(bridge) is not DoctorHomeBridge
                or bridge not in self._verified_laboratory_bridges
                or bridge.doctor is not self
                or not isinstance(event, Mapping)
                or event.get("channel") != "world"
                or not isinstance(event.get("percept"), str)
                or bridge._active_verified_admission != (
                    event.get("source"), event.get("percept")
                )):
            raise PermissionError("No active, source-verified Laboratory handoff")
        return self._project_and_ingest(event, laboratory_verified=True)

    def _ingest_authorized_sensus(self, event: Mapping[str, Any], *,
                                   organ: object) -> dict[str, Any]:
        """Trusted host-to-Sensus boundary; not an untrusted model API.

        One existing SensusOrgan tied to THIS original brain must explicitly
        offer an already-verified percept. Host authority is a research
        assumption here, not a cryptographic attestation.
        """
        from .organs import SensusOrgan
        if (type(organ) is not SensusOrgan
                or organ._port is not self
                or event.get("channel") not in ("world", "tool")):
            raise PermissionError("Percept is not from the bound Sensus host")
        return self._project_and_ingest(
            event, laboratory_verified=(event["channel"] == "world"),
        )

    def _ingest_verified_virtual_world(self, event: Mapping[str, Any], *,
                                       environment: object,
                                       receipt: object) -> dict[str, Any]:
        """Require the bound world provider to independently verify receipt."""
        from .virtual_world_port import (
            VirtualWorldEnvironmentPort, VirtualWorldReceipt,
        )
        if (type(environment) is not VirtualWorldEnvironmentPort
                or type(receipt) is not VirtualWorldReceipt
                or environment._runtime._port is not self
                or not environment._provider.verify_receipt(receipt)
                or receipt.world_id != environment._world_id
                or receipt.world_epoch != environment._epoch
                or event.get("channel") != "world"
                or event.get("percept") != receipt.first_person
                or event.get("source") != (
                    "virtual-world:" + receipt.world_id + ":"
                    + receipt.world_epoch + ":" + receipt.kind + ":"
                    + receipt.event_id
                )):
            raise PermissionError("Unverified virtual-world source")
        return self._project_and_ingest(event, laboratory_verified=True)

    def _ingest_mock_fixture(self, event: Mapping[str, Any], *,
                             provider: object, observation: object) -> dict[str, Any]:
        """Admit one explicitly synthetic sensor fixture as a REPORTED event.

        This is neither a real-world attestation nor permission to actuate.
        The typed test provider owns its finite schedule; no caller may
        manufacture synthetic observation authority via source labels alone.
        """
        from .environment_port import MockRobotEnvironmentPort, MockSensorObservation

        if (type(provider) is not MockRobotEnvironmentPort
                or type(observation) is not MockSensorObservation
                or provider._port is not self
                or observation not in provider._observations
                or not provider._authorized
                or event.get("channel") != "world"
                or event.get("percept") != observation.first_person
                or event.get("source") != (
                    "mock-robot-fixture:" + provider._session + ":"
                    + observation.event_id
                )):
            raise PermissionError("No authenticated synthetic fixture")
        return self._project_and_ingest(
            event, laboratory_verified=False, mock_fixture=True,
        )

    def _project_and_ingest(self, event: Mapping[str, Any], *,
                            laboratory_verified: bool,
                            mock_fixture: bool = False) -> dict[str, Any]:
        projected = project_raw_ingress(
            event,
            context=ProjectionContext(
                subject_id="pretorius",
                tick=self.brain.store.tick + 1,
                source_state_digest=self.brain.store.digest(),
                projection_rule_version="subject-interface-a12-port",
            ),
            _laboratory_verified=laboratory_verified,
            _mock_fixture=mock_fixture,
        )
        result = self.brain.ingest(projected.experience)
        result["ingress"] = {
            "channel": projected.channel.value,
            "raw_sha256": projected.raw_sha256,
            "control_like": projected.control_like,
            "subject_text": projected.event.subject_text,
        }
        return result

    def cognition(self, trigger: str = "chassis") -> dict[str, Any]:
        return self.brain.think(trigger)

    def view(self) -> dict[str, Any]:
        return asdict(self.brain.cognitive_view())

    def subject_frame(self, user_input: str | None = None) -> SubjectFrame:
        """Host-only typed subject projection for the single Ipseity admission seam.

        The returned SubjectFrame is factory-produced by the existing Doctor
        projector. This method does NOT hand out an engineer audit or certify
        durable awareness admission. A conforming production host must still
        route the result through its chosen one authoritative access gate.
        """
        return self.brain.render_request(user_input).subject_frame

    def render_request(self, user_input: str | None = None) -> dict[str, Any]:
        return self.brain.render_request(user_input).to_dict()

    def bind_recollection_controller(
        self, choose_question: Callable[[], str]
    ) -> HostRecollectionController:
        """Bind exactly one in-process host-owned source of self-questions.

        The host MUST verify the callable's controller provenance before
        binding; no origin string supplied by a user, tool or renderer is
        sufficient. An actual autonomous decision mechanism is not supplied
        by this interface.
        """
        if self._recollection_controller is not None:
            raise SubjectInquiryAuthorizationError(
                "Recollection controller is already bound for this brain port"
            )
        if not callable(choose_question):
            raise TypeError("A trusted question-selector callback is required")
        controller = HostRecollectionController(self, choose_question)
        self._recollection_controller = controller
        return controller

    def _issue_subject_inquiry(
        self, controller: HostRecollectionController, question: str
    ) -> object:
        if controller is not self._recollection_controller:
            raise SubjectInquiryAuthorizationError(
                "Unrecognized host recollection controller"
            )
        if self._pending_subject_inquiry is not None:
            raise SubjectInquiryAuthorizationError(
                "Another internal recollection authorization is pending"
            )
        query = validate_subject_inquiry(question)
        nonce = object()
        self._pending_subject_inquiry = (
            nonce, query, self.brain.store.digest(), self.brain.neural.tick,
        )
        return nonce

    def _subject_recollection_frame(
        self, question: str, *, _authorization: object = None
    ) -> dict[str, Any]:
        """Return a typed frame only after consuming a one-use host grant.

        A valid authorization is private to a single bound host controller,
        question and brain state, and is consumed BEFORE retrieval. Internal
        caller authority is distinct from first-person wording validation.
        """
        pending = self._pending_subject_inquiry
        if (
            pending is None
            or _authorization is not pending[0]
            or type(question) is not str
            or question != pending[1]
        ):
            raise SubjectInquiryAuthorizationError(
                "Subject recollection requires a one-use host controller grant"
            )
        # Consume before invoking any retrieval, even on a downstream error.
        self._pending_subject_inquiry = None
        if (
            self.brain.store.digest() != pending[2]
            or self.brain.neural.tick != pending[3]
        ):
            raise SubjectInquiryAuthorizationError(
                "Subject recollection authorization refers to stale brain state"
            )
        return self.brain.subject_recollection(question)

    def subject_recollection(
        self, question: str, *, _authorization: object = None
    ) -> dict[str, Any]:
        """Return only first-person strings after host authorization."""
        frame = self._subject_recollection_frame(
            question, _authorization=_authorization
        )
        return {
            "schema": "the-doctor-lives.subject-recollection.v1",
            "subject_frame": list(frame.renderer_context()),
        }

    def heartbeat(self, ticks: int = 1) -> dict[str, Any]:
        """Host-scheduled aging and endogenous thought via the existing brain."""
        return self.brain.heartbeat(ticks)

    def sleep(self, ticks: int = 12) -> dict[str, Any]:
        return self.brain.sleep(ticks)

    def save(self) -> dict[str, Any]:
        self.brain.save()
        return {
            "schema": self.SCHEMA,
            "port_schema": self.SCHEMA,
            "tick": self.brain.store.tick,
            "state_version": self.brain.store.state_version,
            "state_digest": self.brain.store.digest(),
        }

    def status(self) -> dict[str, Any]:
        out = self.brain.status()
        out["port_schema"] = self.SCHEMA
        return out
