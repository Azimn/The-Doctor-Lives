"""Environment-neutral observation/action host boundary for one Pretorius.

Current authoritative provider: pinned Pretorius-Laboratory through the
existing DoctorHomeBridge. Optional mock-robot provider: immutable scripted
sensor observations, NO hardware or movement authority, no shadow brain/world.
This is a D5 provider interface milestone, not robotic deployment.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Protocol, runtime_checkable

from .chassis import PretoriusBrainPort
from .ingress import control_instruction_markers, implementation_leaks
from .organs import SixOrganRuntime

_ID = re.compile(r"^[a-zA-Z0-9._:-]{1,72}$")


@dataclass(frozen=True, slots=True)
class EnvironmentFeedback:
    """Host/audit output; this envelope is NOT a subject renderer context."""

    status: str
    memory_id: str
    first_person: str
    source_kind: str


@runtime_checkable
class EnvironmentPort(Protocol):
    """Same observational and authorization signatures across environments."""

    def observe(self) -> EnvironmentFeedback: ...

    def act(self, op: str, *, event_id: str, **args) -> EnvironmentFeedback: ...


@dataclass(frozen=True, slots=True)
class MockSensorObservation:
    """Host-provided test fixture, not a real device attestation or world truth."""

    event_id: str
    first_person: str

    def __post_init__(self):
        if type(self.event_id) is not str or not _ID.fullmatch(self.event_id):
            raise ValueError("Mock observation needs bounded event identity")
        if (type(self.first_person) is not str
                or not self.first_person.startswith(("I ", "My ", "Mine ", "Me "))
                or len(self.first_person) > 500
                or implementation_leaks(self.first_person)
                or control_instruction_markers(self.first_person)):
            raise ValueError("Mock input must be situated, bounded, non-control first person")


class LaboratoryEnvironmentPort:
    """Thin facade over the SAME world and same tested receipt bridge."""

    def __init__(
        self, runtime: SixOrganRuntime, laboratory_subject_port, *,
        authorized: bool = False,
    ):
        if not isinstance(runtime, SixOrganRuntime):
            raise TypeError("Requires existing canonical six-organ runtime")
        self._bridge = runtime.bind_laboratory(
            laboratory_subject_port, authorized=authorized
        )

    @staticmethod
    def _result(report) -> EnvironmentFeedback:
        return EnvironmentFeedback(
            status=report["status"],
            memory_id=report["memory_id"],
            first_person=report["subject"]["inner"],
            source_kind="laboratory",
        )

    def observe(self) -> EnvironmentFeedback:
        return self._result(self._bridge.observe())

    def act(self, op: str, *, event_id: str, **args) -> EnvironmentFeedback:
        # The existing real Laboratory bridge still owns verification, physical
        # authorization and replay. This facade DOES NOT grant initiative.
        return self._result(self._bridge.act(op, event_id=event_id, **args))


class MockRobotEnvironmentPort:
    """Observation-only substitute. Never connects to robot hardware.

    The caller supplies a fixed finite sequence of synthetic sensor observations
    from an authenticated test harness. Memory is the ONE canonical BrainStore,
    with event/source identity guaranteeing replay idempotence across restart.
    """

    def __init__(
        self, runtime: SixOrganRuntime, observations: tuple[MockSensorObservation, ...],
        *, session_id: str, authorized: bool = False,
    ):
        if not isinstance(runtime, SixOrganRuntime):
            raise TypeError("Requires existing canonical six-organ runtime")
        if authorized is not True:
            raise PermissionError("Explicit mock-only environment authorization required")
        if type(session_id) is not str or not _ID.fullmatch(session_id):
            raise ValueError("Mock session requires bounded ID")
        if type(observations) is not tuple or any(
            type(item) is not MockSensorObservation for item in observations
        ):
            raise TypeError("Mock provider accepts only frozen typed observations")
        if len({x.event_id for x in observations}) != len(observations):
            raise ValueError("Duplicate mock observation IDs")
        self._port: PretoriusBrainPort = runtime._port
        self._session = session_id
        self._observations = observations
        self._cursor = 0

    def observe(self) -> EnvironmentFeedback:
        if self._cursor >= len(self._observations):
            raise StopIteration("Mock sensor fixture exhausted; no invented observation")
        item = self._observations[self._cursor]
        self._cursor += 1
        source = "mock-robot-fixture:" + self._session + ":" + item.event_id
        # Existing canonical evidence ledger is the durable idempotency source.
        # Do not create per-environment or per-organ persistent memories.
        with self._port.brain.store.connect() as db:
            saved = db.execute(
                "SELECT id,text FROM memories WHERE source=?",
                (source,),
            ).fetchall()
        if saved:
            if len(saved) != 1 or saved[0]["text"] != item.first_person:
                raise RuntimeError("Mock observation replay conflicts with canonical memory")
            return EnvironmentFeedback(
                status="already_admitted", memory_id=saved[0]["id"],
                first_person=saved[0]["text"], source_kind="mock_robot",
            )
        received = self._port.ingest({
            "channel": "world", "source": source,
            "kind": "mock_sensor_observation", "percept": item.first_person,
        })
        return EnvironmentFeedback(
            status="admitted", memory_id=received["memory_id"],
            first_person=received["ingress"]["subject_text"],
            source_kind="mock_robot",
        )

    def act(self, op: str, *, event_id: str, **args) -> EnvironmentFeedback:
        raise PermissionError("Mock robot cannot actuate; no hardware executor installed")
