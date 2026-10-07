from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from .cognition import PretoriusBrain
from .ingress import project_raw_ingress
from .projection import ProjectionContext


class PretoriusBrainPort:
    """Stable, renderer-neutral boundary for an arbitrary agent chassis.

    The chassis may deliver observations and ask for cognition or a render
    request. It does not receive direct authority to rewrite identity evidence,
    provenance, memory classification, or the recurrent substrate.
    """

    SCHEMA = "the-doctor-lives.brain-port.v1"

    def __init__(self, state_dir: str | Path, *, neural_config: dict[str, Any] | None = None):
        self.brain = PretoriusBrain(state_dir, neural_config=neural_config)

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
