from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from .cognition import PretoriusBrain
from .models import Experience


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
        allowed = {
            "text", "source", "kind", "valence", "arousal", "social", "authority",
            "autonomy", "novelty", "achievement", "isolation", "threat", "intimacy",
            "control", "creation", "actor", "external", "confidence", "tags",
        }
        unknown = set(event) - allowed
        if unknown:
            raise ValueError(f"unsupported experience fields: {sorted(unknown)}")
        if not str(event.get("text", "")).strip():
            raise ValueError("experience text is required")
        payload = dict(event)
        if "tags" in payload:
            payload["tags"] = tuple(str(x) for x in payload["tags"])
        return self.brain.ingest(Experience(**payload))

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
