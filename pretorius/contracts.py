"""Stable boundaries between Pretorius, renderers, and agent bodies."""

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class CognitiveView:
    """Renderer-neutral snapshot of what is currently cognitively available."""

    identity_roots: Sequence[str]
    salient_memories: Sequence[str]
    concerns: Sequence[str]
    commitments: Sequence[str]
    relationships: Mapping[str, Mapping[str, Any]]
    interoception: Mapping[str, float]
    neural_state_ref: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Experience:
    """An event offered to the mind. Acceptance into autobiography is separate."""

    content: str
    source: str
    observed: bool
    provenance: Mapping[str, Any] = field(default_factory=dict)


class RendererBoundary:
    """Interface contract only. Renderers express state; they do not own it."""

    def render(self, view: CognitiveView, prompt: str) -> str:
        raise NotImplementedError


class AgentBodyBoundary:
    """Capabilities supplied by an eventual agent chassis."""

    def capabilities(self) -> Sequence[str]:
        raise NotImplementedError
