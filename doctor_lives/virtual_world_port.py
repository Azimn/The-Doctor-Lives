"""Portable virtual-world observation and action boundary for ONE Pretorius.

The character's brain, memory, neural state, and first-person admission stay
in the Doctor. Virtual worlds own geometry, items, physics and action receipts.
The host explicitly binds one trusted environment at a time. This contract
is for game/simulation worlds, NOT robotic hardware or a general trust sandbox.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol, runtime_checkable

from .environment_port import EnvironmentFeedback
from .ingress import control_instruction_markers, implementation_leaks
from .organs import SixOrganRuntime

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_FIRST_PERSON = ("I ", "My ", "Mine ", "Me ")


@dataclass(frozen=True, slots=True)
class VirtualWorldReceipt:
    """World-issued evidence; never give the engineering envelope to Pretorius."""

    world_id: str
    world_epoch: str
    event_id: str
    kind: str  # observation or action
    first_person: str
    operation: str = ""
    successful: bool = True

    def __post_init__(self):
        for item in (self.world_id, self.world_epoch, self.event_id):
            if type(item) is not str or not _SAFE_ID.fullmatch(item):
                raise ValueError("World receipt requires safe stable identifiers")
        if self.kind not in ("observation", "action"):
            raise ValueError("Unknown world receipt kind")
        if type(self.successful) is not bool:
            raise ValueError("World receipt success must be explicit")
        if self.kind == "action" and not _SAFE_ID.fullmatch(self.operation):
            raise ValueError("Action receipt requires bounded operation")
        if self.kind == "observation" and self.operation:
            raise ValueError("Observation must not carry action authority")
        if (type(self.first_person) is not str
                or not self.first_person.startswith(_FIRST_PERSON)
                or not 1 <= len(self.first_person) <= 500
                or control_instruction_markers(self.first_person)
                or implementation_leaks(self.first_person)):
            raise ValueError("Only bounded situated first-person percepts may enter")


@runtime_checkable
class VirtualWorldSource(Protocol):
    """An independently authoritative, host-trusted simulated-world adapter."""

    world_id: str
    world_epoch: str

    def observe(self) -> VirtualWorldReceipt: ...
    def act(self, op: str, *, event_id: str, **args) -> VirtualWorldReceipt: ...
    def verify_receipt(self, receipt: VirtualWorldReceipt) -> bool: ...


class VirtualWorldEnvironmentPort:
    """Bind a trusted simulated world to one existing PretoriusBrainPort.

    Unlike the fixture-only mock robot, this provider can perform real
    WORLD-AUTHORIZED virtual actions with replayable source receipts.
    Verification is delegated to the pinned/trusted world service; Python
    interface conformance and authorized=True do not authenticate a provider.
    Do not provide this interface directly to an untrusted model.
    """

    def __init__(
        self, runtime: SixOrganRuntime, provider: VirtualWorldSource, *,
        authorized: bool = False,
    ):
        if not isinstance(runtime, SixOrganRuntime):
            raise TypeError("Must use the one canonical six-organ runtime")
        if authorized is not True:
            raise PermissionError("Trusted host must explicitly bind a virtual world")
        if not isinstance(provider, VirtualWorldSource):
            raise TypeError("World must implement receipt verification")
        if (type(provider.world_id) is not str
                or not _SAFE_ID.fullmatch(provider.world_id)
                or type(provider.world_epoch) is not str
                or not _SAFE_ID.fullmatch(provider.world_epoch)):
            raise ValueError("World identity and epoch must be bounded")
        self._runtime = runtime
        self._provider = provider
        self._world_id = provider.world_id
        self._epoch = provider.world_epoch

    def _admit(self, receipt: VirtualWorldReceipt, *, kind: str,
               expected_event_id: str | None = None,
               expected_op: str | None = None) -> EnvironmentFeedback:
        if type(receipt) is not VirtualWorldReceipt:
            raise TypeError("Unrecognized virtual-world receipt")
        if (receipt.world_id != self._world_id
                or receipt.world_epoch != self._epoch
                or receipt.kind != kind
                or not self._provider.verify_receipt(receipt)):
            raise PermissionError("Provider receipt was not source-verified")
        if expected_event_id is not None and receipt.event_id != expected_event_id:
            raise RuntimeError("Action receipt does not match the requested event")
        if expected_op is not None and receipt.operation != expected_op:
            raise RuntimeError("Action receipt does not match the requested operation")
        if not receipt.successful:
            raise PermissionError("Rejected world action cannot become completed experience")

        source = ("virtual-world:" + self._world_id + ":" + self._epoch
                  + ":" + receipt.kind + ":" + receipt.event_id)
        port = self._runtime._port
        # Reconcile after a crash between world effect and brain memory: the
        # provider owns the durable effect/receipt, BrainStore owns acquisition.
        with port.brain.store.connect() as conn:
            saved = conn.execute(
                "SELECT id,text,evidence_class FROM memories WHERE source=?",
                (source,),
            ).fetchall()
        if saved:
            if (len(saved) != 1
                    or saved[0]["text"] != receipt.first_person
                    or saved[0]["evidence_class"] != "lived_runtime_memory"):
                raise RuntimeError("Conflicting virtual-world receipt replay")
            return EnvironmentFeedback(
                status="already_admitted", memory_id=saved[0]["id"],
                first_person=saved[0]["text"], source_kind=self._world_id,
            )
        ingested = port.ingest({
            "channel": "world", "kind": "virtual_world_observation",
            "source": source, "percept": receipt.first_person,
        })
        return EnvironmentFeedback(
            status="admitted", memory_id=ingested["memory_id"],
            first_person=ingested["ingress"]["subject_text"],
            source_kind=self._world_id,
        )

    def observe(self) -> EnvironmentFeedback:
        return self._admit(self._provider.observe(), kind="observation")

    def act(self, op: str, *, event_id: str, **args) -> EnvironmentFeedback:
        if type(op) is not str or not _SAFE_ID.fullmatch(op):
            raise ValueError("Unsafe world operation")
        if type(event_id) is not str or not _SAFE_ID.fullmatch(event_id):
            raise ValueError("World action needs a stable event identity")
        receipt = self._provider.act(op, event_id=event_id, **args)
        return self._admit(
            receipt, kind="action", expected_event_id=event_id, expected_op=op
        )
