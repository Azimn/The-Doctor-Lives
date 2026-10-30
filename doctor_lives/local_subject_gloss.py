"""Optional localhost-only interpretive gloss for authenticated subject frames.

The original first-person frame is the only source-backed account. A model
may paraphrase it for an operator, but cannot write lived memory, authorize
world actions, or replace the subject renderer. No remote endpoint is accepted.
"""
from __future__ import annotations

import http.client
import json
import re

_MODEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,95}\Z")
_MAX_INPUT = 2048
_MAX_OUTPUT = 500


def local_interpretation(frames: list[dict], model: str) -> str | None:
    """Best-effort optional Ollama gloss, never authoritative first-person text.

    Only already source-qualified inner strings are sent. No world receipts,
    engineer telemetry, neural state, memory IDs, or arbitrary host URLs cross
    the loopback boundary. A missing/failed local server leaves the verified
    transcript untouched.
    """
    if not isinstance(model, str) or not _MODEL.fullmatch(model):
        raise ValueError("Invalid local model identifier")
    if not isinstance(frames, list):
        raise ValueError("Trusted subject frames required")
    texts = []
    for frame in frames:
        if not isinstance(frame, dict) or not isinstance(frame.get("inner"), str):
            raise ValueError("Source-qualified subject frame required")
        texts.append(frame["inner"])
    if not texts:
        return None
    source = "\n".join(texts)[:_MAX_INPUT]
    request = {
        "model": model,
        "stream": False,
        "prompt": (
            "Interpret this first-person account in one short, third-person "
            "operator note. Do not assert new events, observations or memories. "
            "Your response is unverified commentary, never the subject's voice.\n"
            + source
        ),
        "options": {"temperature": 0, "num_predict": 128},
    }
    payload = json.dumps(request, ensure_ascii=False).encode("utf-8")
    connection = http.client.HTTPConnection("127.0.0.1", 11434, timeout=1.5)
    try:
        connection.request(
            "POST", "/api/generate", body=payload,
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        if response.status != 200:
            return None
        raw = response.read(4097)
        if len(raw) > 4096:
            return None
        value = json.loads(raw.decode("utf-8"))
        note = value.get("response") if isinstance(value, dict) else None
        if not isinstance(note, str) or not note.strip():
            return None
        return note.strip()[:_MAX_OUTPUT]
    except (OSError, TimeoutError, ValueError, UnicodeError, http.client.HTTPException):
        return None
    finally:
        connection.close()
