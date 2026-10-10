"""Experimental signed source custody bridge, separate from Pretorius cognition.

The host/test world owns a ≥32 byte secret. The character does not. This
authenticates a host-issued RECEIPT (integrity and issuer within a controlled
test trust domain) but does not prove that the external world truly changed.
Never expose signatures or receipts as experienced first-person content.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import hmac
import json

from .firsthand_gate import WorldReceipt


def canonical(value: object) -> bytes:
    return json.dumps(value,sort_keys=True,ensure_ascii=False,
                      separators=(",",":")).encode("utf-8")


@dataclass(frozen=True)
class SignedWorldReceipt:
    issuer: str
    subject_id: str
    session_id: str
    event_id: str
    event_key: str
    event_digest: str
    sequence: int
    mac_sha256: str

    def __post_init__(self):
        for key in ("issuer","subject_id","session_id","event_id","event_key"):
            if not getattr(self,key) or not getattr(self,key).strip():
                raise ValueError("receipt has empty scope")
        if self.sequence < 0 or type(self.sequence) is not int:
            raise ValueError("receipt requires a nonnegative sequence")
        if len(self.event_digest)!=64 or len(self.mac_sha256)!=64:
            raise ValueError("malformed hash or MAC")

    @property
    def signed_fields(self) -> dict:
        return {name:getattr(self,name) for name in (
            "issuer","subject_id","session_id","event_id","event_key",
            "event_digest","sequence",
        )}


@dataclass(frozen=True)
class WorldHostVerifier:
    """Research dependency passed in by host. The secret cannot be serialized.

    Exact session/issuer/subject scopes, an explicit active event allowlist,
    and optional revocation are checked before source eligibility.
    """

    issuer: str
    subject_id: str
    session_id: str
    secret: bytes
    allowed_event_ids: frozenset[str]
    revoked_event_ids: frozenset[str] = frozenset()

    def __post_init__(self):
        if len(self.secret)<32:
            raise ValueError("insufficient host key entropy/length")
        if not all((self.issuer,self.subject_id,self.session_id)):
            raise ValueError("host identity scope required")

    def verify(self, receipt: SignedWorldReceipt) -> WorldReceipt | None:
        if not isinstance(receipt,SignedWorldReceipt):
            raise TypeError("typed signed receipt required")
        if (receipt.issuer != self.issuer or
            receipt.subject_id != self.subject_id or
            receipt.session_id != self.session_id or
            receipt.event_id not in self.allowed_event_ids or
            receipt.event_id in self.revoked_event_ids):
            return None
        expected=hmac.new(self.secret,canonical(receipt.signed_fields),
                          hashlib.sha256).hexdigest()
        if not hmac.compare_digest(receipt.mac_sha256,expected):
            return None
        return WorldReceipt(
            receipt.event_id,receipt.event_key,receipt.event_digest,
        )

    def verify_batch(
        self, receipts: tuple[SignedWorldReceipt, ...],
    ) -> tuple[WorldReceipt,...]:
        if not isinstance(receipts,tuple):
            raise TypeError("receipts must be a tuple")
        verified=[]
        seen=set()
        for ticket in receipts:
            ref=self.verify(ticket)
            if ref is None:
                continue
            if ref.event_id in seen:
                raise ValueError("duplicated event receipt")
            seen.add(ref.event_id)
            verified.append(ref)
        return tuple(verified)


def issue_receipt(
    verifier: WorldHostVerifier, *,
    event_id: str, event_key: str, event_digest: str, sequence: int,
) -> SignedWorldReceipt:
    """Controlled host/test-world signing only; NEVER call from model context."""
    if event_id not in verifier.allowed_event_ids:
        raise ValueError("event not admitted to active world-host ledger")
    data={
        "issuer":verifier.issuer,"subject_id":verifier.subject_id,
        "session_id":verifier.session_id,"event_id":event_id,
        "event_key":event_key,"event_digest":event_digest,
        "sequence":sequence,
    }
    mac=hmac.new(verifier.secret,canonical(data),hashlib.sha256).hexdigest()
    return SignedWorldReceipt(**data,mac_sha256=mac)
