from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Mapping

from .cognition import PretoriusBrain
from .ingress import project_raw_ingress
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

    def recollect(self) -> dict[str, Any]:
        # The external user/tool/renderer never supplies a question to this
        # method. The registered host callback is the only query producer.
        question = validate_subject_inquiry(self._choose_question())
        permit = self._port._issue_subject_inquiry(self, question)
        return self._port.subject_recollection(question, _authorization=permit)


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

    def ingest(self, event: Mapping[str, Any]) -> dict[str, Any]:
        """Project raw chassis input before it can become Pretorius's experience."""
        projected = project_raw_ingress(
            event,
            context=ProjectionContext(
                subject_id="pretorius",
                tick=self.brain.store.tick + 1,
                source_state_digest=self.brain.store.digest(),
                projection_rule_version="subject-interface-a12-port",
            ),
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

    def subject_recollection(
        self, question: str, *, _authorization: object = None
    ) -> dict[str, Any]:
        """Fail closed for unsolicited user/tool/model internal queries.

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
        frame = self.brain.subject_recollection(question)
        return {
            "schema": "the-doctor-lives.subject-recollection.v1",
            "subject_frame": list(frame.renderer_context()),
        }

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
