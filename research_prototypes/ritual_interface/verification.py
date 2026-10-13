"""External sealed-probe aggregation. Reports do not authorize identity edits."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProbeObservation:
    probe_id: str
    domain: str
    passed: bool
    source_grounded: bool

    def __post_init__(self) -> None:
        if not self.probe_id or not self.domain:
            raise ValueError("probe id and domain required")
        if type(self.passed) is not bool or type(self.source_grounded) is not bool:
            raise TypeError("probe values must be booleans")


@dataclass(frozen=True, slots=True)
class VerificationReport:
    status: str
    failed_probe_ids: tuple[str, ...]
    covered_domains: tuple[str, ...]


def verify(observations: tuple[ProbeObservation, ...], *, required_domains: tuple[str, ...]) -> VerificationReport:
    if not isinstance(observations, tuple) or any(not isinstance(x, ProbeObservation) for x in observations):
        raise TypeError("observations must be a tuple of ProbeObservation")
    if not isinstance(required_domains, tuple) or not required_domains or any(not isinstance(x, str) or not x for x in required_domains):
        raise ValueError("required_domains must be a nonempty tuple")
    if len(set(required_domains)) != len(required_domains):
        raise ValueError("duplicate required domains")
    ids = [x.probe_id for x in observations]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate probe id")
    covered = tuple(sorted({x.domain for x in observations}))
    if not set(required_domains).issubset(covered):
        return VerificationReport("insufficient_evidence", (), covered)
    failed = tuple(x.probe_id for x in observations if not x.passed or not x.source_grounded)
    return VerificationReport("drift" if failed else "pass", failed, covered)
