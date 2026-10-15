"""One real Pretorius experimental host with CASCADE conformance controls.

Inherits the existing Sensus -> Doctor endogenous recall -> Synthetic Ipseity
preview; the existing host-bound Self-Reference Governor remains the optional
speech renderer. Nothing in this wrapper changes the production entrypoint.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
import sys
import time
from typing import Iterable
from uuid import uuid4

from .cascade_governance import (
    CycleGrant, counterfactual_permission_test, preflight_cycle,
    propose_chronos_wake, read_bounded_memory_paths, snapshot_doctor,
    verify_host_cycle,
)
from .three_organ_preview import Evidence, Percept, ThreeOrganPretoriusPreview


class CascadePretoriusPreview(ThreeOrganPretoriusPreview):
    """Opt-in integrated test host, NOT a parallel Pretorius identity system."""

    def __init__(
        self, state_dir: str | Path, *, renderer, enabled: bool = False,
        neural_config: dict | None = None,
        require_governor: bool = True,
    ):
        if not enabled:
            raise PermissionError("Explicit CASCADE experimental opt-in required")
        if type(require_governor) is not bool:
            raise TypeError("Governor requirement must be explicitly boolean")
        if require_governor:
            from .self_reference_adapter import HostBoundGovernorRenderer
            if (not isinstance(renderer, HostBoundGovernorRenderer)
                    or not renderer.enabled):
                raise PermissionError(
                    "CASCADE governed profile needs the pinned host-bound governor"
                )
        self._cascade_require_governor = require_governor
        super().__init__(
            state_dir, renderer=renderer, enabled=True,
            neural_config=neural_config,
        )

    def make_host_grant(
        self, *, permissions: frozenset[str], max_percepts: int,
        max_claim_chars: int = 2400,
    ) -> CycleGrant:
        """Trusted in-process issuer. Never accepts an identity in a message."""
        state = snapshot_doctor(self)
        return CycleGrant(
            expected_state_digest=state.state_digest,
            expected_scene_tick=self._scene_tick,
            permissions=permissions,
            max_percepts=max_percepts,
            max_claim_chars=max_claim_chars,
        )

    def cycle(
        self, percepts: Iterable[Percept], *,
        trusted_source_refs: frozenset[str],
        now_ms: int,
        cascade_grant: CycleGrant | None = None,
    ) -> dict:
        if type(cascade_grant) is not CycleGrant:
            raise PermissionError("An explicit host-issued CASCADE grant is required")
        state_before = snapshot_doctor(self)
        items = tuple(percepts)
        receipt = preflight_cycle(
            state_before, cascade_grant, items, trusted_source_refs,
        )
        if not receipt.allowed:
            raise PermissionError("CASCADE arbiter veto: " + receipt.reason)
        # The inherited host still independently authenticates every source,
        # guards scene replay, persists policy, and admits typed first-person
        # experience through durable Synthetic Ipseity.
        outcome = super().cycle(
            items, trusted_source_refs=trusted_source_refs, now_ms=now_ms,
        )
        trace = verify_host_cycle(self, state_before, outcome)
        return {
            **outcome,
            "cascade_schema": trace.schema,
            "cascade_arbiter": asdict(receipt),
            "cascade_causal_trace": asdict(trace),
            "cascade_engineer_only": True,
            "cascade_conformance_only": True,
        }

    def counterfactual_gate(
        self, items: Iterable[Percept], *,
        trusted_source_refs: frozenset[str],
        cascade_grant: CycleGrant,
        remove_permission: str,
    ) -> tuple:
        """Side-effect-free, same-state intervention on action eligibility."""
        before = snapshot_doctor(self)
        return counterfactual_permission_test(
            before, cascade_grant, items, trusted_source_refs,
            removed_permission=remove_permission,
        )

    def graph_probe(self, memory_id: str, *, max_hops: int = 2):
        return read_bounded_memory_paths(self, memory_id, max_hops=max_hops)

    def chronos_proposal(
        self, *, current_tick: int, last_wake_tick: int,
        min_interval: int, host_authorized: bool,
    ):
        return propose_chronos_wake(
            current_tick=current_tick, last_wake_tick=last_wake_tick,
            min_interval=min_interval, permission=host_authorized,
            pending_delivery=self.pending_count() != 0 or self._journal.active() is not None,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="doctor-lives-cascade-preview",
        description="Isolated CASCADE + three-organ + governor Pretorius experiment",
    )
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--model", default="qwen3:1.5b")
    parser.add_argument("--enable-experimental-preview", action="store_true")
    parser.add_argument("--renderer-control", choices=("governed", "plain"),
                        default="governed")
    parser.add_argument("--max-percepts", type=int, default=4)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--say", help="Host-reported User speech")
    mode.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    if not args.enable_experimental_preview:
        parser.error("Explicit --enable-experimental-preview required")
    if args.state.name != "three-organ-preview":
        parser.error("--state must end in a dedicated three-organ-preview directory")
    if not 1 <= args.max_percepts <= 128:
        parser.error("--max-percepts must be 1..128")

    from .ipseity_local import build_local_renderer
    governed = None
    if args.renderer_control == "governed":
        from .self_reference_adapter import HostBoundGovernorRenderer
        from synthetic_ipseity.local_ollama import LocalOllamaConfiguredRenderer
        governed = HostBoundGovernorRenderer(
            enabled=True, recovery_enabled=True,
            trusted_instruction="Express the current experience as your own speech.",
            render=LocalOllamaConfiguredRenderer(args.model),
            fallback_text="I must consider my words more carefully.",
            max_model_attempts=2,
        )
    renderer = governed if governed is not None else build_local_renderer(args.model)
    with CascadePretoriusPreview(
        args.state, enabled=True, renderer=renderer,
        require_governor=governed is not None,
    ) as host:
        if governed is not None:
            governed.bind_doctor_host(host, addressee_subject_id="visitor")
        now = int(time.time() * 1000)
        if args.resume:
            print(host.resume_preview(now_ms=now))
        else:
            grant = host.make_host_grant(
                permissions=frozenset({"communicate"}),
                max_percepts=args.max_percepts,
            )
            source = "cascade-preview:local-user"
            claim = Percept(
                event_id="cascade-report-" + uuid4().hex,
                channel="conversation", evidence=Evidence.REPORTED,
                source_ref=source, tick=host._scene_tick,
                attribute="message", value=args.say, confidence=0.8,
            )
            outcome = host.cycle(
                (claim,), trusted_source_refs=frozenset({source}),
                now_ms=now, cascade_grant=grant,
            )
            print(outcome["answer"])
            print(
                "CASCADE engineer receipt: decision="
                + outcome["cascade_causal_trace"]["policy_decision_id"]
                + " state_changed=true; research only",
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
