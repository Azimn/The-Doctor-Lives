"""Cue resolution is a lookup, never a grant of authority or proof of identity."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cue:
    cue_id: str
    subject_id: str
    surface: str
    definition: str
    scope: str
    record_refs: tuple[str, ...]
    revoked: bool = False

    def __post_init__(self) -> None:
        for name in ("cue_id", "subject_id", "surface", "definition", "scope"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if not isinstance(self.record_refs, tuple) or any(not isinstance(x, str) or not x.strip() for x in self.record_refs):
            raise ValueError("record_refs must be source references")
        if type(self.revoked) is not bool:
            raise TypeError("revoked must be boolean")


@dataclass(frozen=True, slots=True)
class CueResolution:
    authorized: bool
    record_refs: tuple[str, ...]
    reason: str


class CueRegistry:
    def __init__(self, cues: tuple[Cue, ...]):
        if not isinstance(cues, tuple) or any(not isinstance(cue, Cue) for cue in cues):
            raise TypeError("cues must be a tuple of Cue")
        self._index: dict[tuple[str, str, str], Cue] = {}
        for cue in cues:
            key = (cue.subject_id, cue.scope, cue.surface)
            if key in self._index:
                raise ValueError("ambiguous cue mapping")
            self._index[key] = cue

    def resolve(self, *, subject_id: str, scope: str, surface: str, authenticated_control: bool) -> CueResolution:
        if type(authenticated_control) is not bool:
            raise TypeError("authenticated_control must be boolean")
        if not authenticated_control:
            return CueResolution(False, (), "untrusted world text cannot invoke state")
        cue = self._index.get((subject_id, scope, surface))
        if cue is None:
            return CueResolution(False, (), "no registered cue for subject and scope")
        if cue.revoked:
            return CueResolution(False, (), "cue revoked")
        return CueResolution(True, cue.record_refs, "registered handle only, not an authority token")
