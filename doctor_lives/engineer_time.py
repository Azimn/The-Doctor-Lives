"""Swatch .beat display time for engineer-only metadata, NEVER subject input.

Swatch Biel Mean Time (BMT) is fixed UTC+01:00 without DST. A 24-hour
reference day has 1,000 beats, each 86.4 seconds. .beats are a clock display,
NOT a chronological key or replacement for UTC/monotonic counters.

Reference: https://github.com/swatchtime/sample-code
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

_BMT = timezone(timedelta(hours=1), "BMT")
_MICROSECONDS_PER_DAY = 86_400_000_000


@dataclass(frozen=True)
class EngineerTimeCode:
    """Audit-only paired clock; UTC is authoritative, .beat is presentation."""

    utc_iso: str
    bmt_date: str
    beat: str

    @property
    def display(self) -> str:
        return f"{self.bmt_date} {self.beat} BMT"


def engineer_time(at: datetime | None = None) -> EngineerTimeCode:
    if at is None:
        at = datetime.now(timezone.utc)
    if not isinstance(at, datetime) or at.tzinfo is None or at.utcoffset() is None:
        raise ValueError("engineer time requires timezone-aware datetime")
    utc = at.astimezone(timezone.utc)
    bmt = utc.astimezone(_BMT)
    micros = (
        ((bmt.hour * 60 + bmt.minute) * 60 + bmt.second) * 1_000_000
        + bmt.microsecond
    )
    number = micros * 1000 // _MICROSECONDS_PER_DAY
    return EngineerTimeCode(
        utc_iso=utc.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        bmt_date=bmt.date().isoformat(),
        beat=f"@{number:03d}",
    )
