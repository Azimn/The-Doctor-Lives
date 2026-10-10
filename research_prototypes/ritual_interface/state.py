"""Read-only, content-addressed projection of upstream authoritative identity refs."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
import re

_DIGEST = re.compile(r"^[a-f0-9]{64}$")


@dataclass(frozen=True, slots=True)
class IdentitySnapshot:
    subject_id: str
    state_version: int
    manifest_digest: str
    invariants: tuple[str, ...]
    relationships: tuple[str, ...]
    commitments: tuple[str, ...]
    memories: tuple[str, ...]
    self_model_hypotheses: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.subject_id, str) or not self.subject_id.strip():
            raise ValueError("subject_id is required")
        if type(self.state_version) is not int or self.state_version < 0:
            raise ValueError("state_version must be nonnegative integer")
        if not isinstance(self.manifest_digest, str) or not _DIGEST.fullmatch(self.manifest_digest):
            raise ValueError("manifest_digest must be lowercase SHA-256 hex")
        for name in ("invariants", "relationships", "commitments", "memories", "self_model_hypotheses"):
            values = getattr(self, name)
            if not isinstance(values, tuple) or any(not isinstance(v, str) or not v.strip() for v in values):
                raise ValueError(f"{name} must be a tuple of nonempty source refs")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} has duplicate source refs")

    @property
    def digest(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
