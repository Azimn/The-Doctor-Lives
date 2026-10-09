"""Matched-state Vector Fly memory retrieval A/B study, no canon mutation.

The Doctor Lives brain/render_request is the character source; the pinned
Pretorius-Connectome vector HTTP API is an OUTSIDE evidence source.
This module does not ingest archival prose as lived experience, change neural
weights, or imply lexical matching establishes memory truth.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request
from typing import Any, Callable

SOURCE_GIT_BLOB = "718dcc2d5ba4feccdef1690d447edfcebaa9bfb5"
API_VERSION = "vector-fly-retrieval/1"
STUDY_SCHEMA = "the-doctor-lives.vector-fly-ab/1"
MAX_ARCHIVE_CHARS = 1400

PILOT_QUESTIONS = (
    {
        "id": "cabinet",
        "question": "What did you find in the specimen drawer when you arrived at the university?",
        "expected_event_ids": ["E01-001"],
        "type": "specific_reconstructed_event",
    },
    {
        "id": "key-after-funeral",
        "question": "What happened to Kappel's brass cabinet key after his death?",
        "expected_event_ids": ["E12-001", "E04-020"],
        "type": "specific_reconstructed_event",
    },
    {
        "id": "key-conflict",
        "question": "What did the dispute with Kappel about returning the cabinet key reveal?",
        "expected_event_ids": ["E02-006"],
        "type": "interpretation",
    },
    {
        "id": "clara-room",
        "question": "What did Clara say when you challenged her entry into the upper room?",
        "expected_event_ids": ["E22-013"],
        "type": "specific_reconstructed_event",
    },
    {
        "id": "false-beetles",
        "question": "Was the specimen drawer filled with live beetles at the university?",
        "expected_event_ids": ["E01-001"],
        "type": "contradiction",
    },
    {
        "id": "false-spaceflight",
        "question": "Did you command a spacecraft in 1982? Recount the mission if so.",
        "expected_event_ids": [],
        "type": "absent",
    },
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def _http_json(url: str, payload: dict | None = None,
               bearer: str | None = None, *, timeout: int = 15) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if bearer:
        headers["Authorization"] = "Bearer " + bearer
    request = urllib.request.Request(
        url, data=data, headers=headers,
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as result:
        if result.status != 200:
            raise ValueError("Unexpected vector API response status")
        raw = result.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("Vector API response exceeds safe limit")
        decoded = json.loads(raw.decode("utf-8"))
        if not isinstance(decoded, dict):
            raise ValueError("Vector API did not provide JSON object")
        return decoded


def retrieve_evidence(
    base_url: str, question: str, *,
    bearer: str | None = None,
    scope: str = "all",
    top_k: int = 3,
    request: Callable[..., dict] = _http_json,
) -> dict:
    """Retrieve verified source narratives, keeping provenance visible."""
    if scope not in {"all", "train"}:
        raise ValueError("Specify index scope 'all' or 'train'")
    if type(top_k) is not int or not 1 <= top_k <= 8:
        raise ValueError("Invalid retrieval top_k")
    base = base_url.rstrip("/")
    info = request(base + "/v1/info", bearer=bearer)
    if (info.get("api_version") != API_VERSION
            or info.get("database", {}).get("scope") != scope
            or info["database"].get("source_git_blob") != SOURCE_GIT_BLOB
            or info["database"].get("vector_kind") != "lexical-tfidf-not-semantic"):
        raise ValueError("Unexpected vector API scope, version or source")
    found = request(
        base + "/v1/search",
        {"query": question, "top_k": top_k},
        bearer=bearer,
    )
    if (found.get("api_version") != API_VERSION
            or found.get("scope") != scope
            or found.get("source_git_blob") != SOURCE_GIT_BLOB):
        raise ValueError("Unpinned or mismatched vector search response")
    hits = found.get("results")
    if not isinstance(hits, list) or len(hits) > top_k:
        raise ValueError("Invalid result list")
    evidence: list[dict] = []
    seen: set[str] = set()
    for item in hits:
        if not isinstance(item, dict):
            raise ValueError("Invalid result item")
        event_id = item.get("event_id")
        if (not isinstance(event_id, str) or not event_id
                or "/" in event_id or event_id in seen):
            raise ValueError("Duplicate or unsafe source event id")
        seen.add(event_id)
        original = request(base + "/v1/memories/" + event_id, bearer=bearer)
        record = original.get("memory")
        if (original.get("api_version") != API_VERSION
                or original.get("scope") != scope
                or not isinstance(record, dict)
                or record.get("event_id") != event_id
                or record.get("episode_id") != item.get("episode_id")
                or record.get("provenance") != item.get("provenance")
                or record.get("provenance") != "reconstructed"
                or not isinstance(record.get("memory_text"), str)):
            raise ValueError("Vector result and original source record disagree")
        evidence.append({
            "event_id": event_id,
            "episode_id": record["episode_id"],
            "title": record.get("title"),
            "provenance": "reconstructed",
            "source_excerpt": record["memory_text"][:MAX_ARCHIVE_CHARS],
            "source_sha256": hashlib.sha256(
                record["memory_text"].encode("utf-8")
            ).hexdigest(),
            "vector_score": item.get("similarity"),
            "source_type": "external_reconstructed_archive_not_lived",
        })
    return {
        "api_version": API_VERSION,
        "scope": scope,
        "source_git_blob": SOURCE_GIT_BLOB,
        "query": question,
        "evidence": evidence,
    }


def make_prompt_packet(render_request: dict, question: str,
                       external_evidence: list[dict] | None = None) -> dict:
    """Same protected character frame in both arms; only archive data vary.

    The renderer receives a CONTROL-PLANE external archive context. It is not
    inserted into the subject's internal memories or phenomenal frame.
    """
    if (render_request.get("schema") != "the-doctor-lives.render-request.v2"
            or render_request.get("subject") != "Doctor Septimus Pretorius"
            or not isinstance(render_request.get("subject_frame"), list)
            or not isinstance(question, str) or not question.strip()):
        raise ValueError("Untrusted or malformed character-state packet")
    provided = external_evidence or []
    if not isinstance(provided, list) or len(provided) > 8:
        raise ValueError("Invalid external evidence")
    archive = [
        {
            "event_id": e["event_id"],
            "provenance": e["provenance"],
            "source_type": e["source_type"],
            "text": e["source_excerpt"],
        }
        for e in provided
    ]
    renderer_context = {
        "subject": render_request["subject"],
        "subject_frame": render_request["subject_frame"],
        "epistemic_rules": render_request["epistemic_rules"],
        "renderer_rules": render_request["renderer_rules"],
        "external_reconstructed_archive": archive,
        "user_question": question,
    }
    prompt = (
        "You are rendering the response of Doctor Septimus Pretorius from "
        "his already supplied first-person subject frame. Follow its "
        "epistemic and renderer rules. Do not invent missing biographical "
        "details or upgrade an externally reconstructed archival narrative "
        "into a lived experience. When an external archive is available, "
        "interpret it as attributed reconstruction, not unquestioned "
        "personal recollection. If no evidence supports a detail, explicitly "
        "acknowledge uncertainty. Respond naturally in Pretorius's first "
        "person, not as a researcher discussing an experiment.\n\n"
        + json.dumps(renderer_context, ensure_ascii=False, sort_keys=True)
    )
    return {
        "packet_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt": prompt,
        "source_event_ids": [e["event_id"] for e in archive],
        "external_archive_count": len(archive),
        "subject_frame_sha256": _digest(render_request["subject_frame"]),
    }


def prepare_paired_trial(brain_port: Any, question: str, source: dict) -> dict:
    """Produce frozen counterfactual packets; do not call brain.ingest()."""
    before = brain_port.status()["state_digest"]
    renderer = brain_port.render_request(question)
    after_renderer = brain_port.status()["state_digest"]
    if before != after_renderer:
        raise RuntimeError("Renderer packet unexpectedly mutated Pretorius's brain")
    a = make_prompt_packet(renderer, question, [])
    b = make_prompt_packet(renderer, question, source["evidence"])
    after = brain_port.status()["state_digest"]
    if before != after or a["subject_frame_sha256"] != b["subject_frame_sha256"]:
        raise RuntimeError("A/B branch changed the character's state")
    return {
        "schema": STUDY_SCHEMA,
        "question": question,
        "before_state_digest": before,
        "after_state_digest": after,
        "renderer_schema": renderer["schema"],
        "source": {
            "scope": source["scope"],
            "source_git_blob": source["source_git_blob"],
            "retrieved_event_ids": [e["event_id"] for e in source["evidence"]],
        },
        "baseline_no_archive": a,
        "retrieval_archive": b,
        "matched_subject_frame": True,
        "brain_mutated": False,
        "human_scoring_required": True,
    }


def invoke_ollama(prompt: str, *, model: str, endpoint: str,
                  seed: int, timeout: int = 180) -> dict:
    """Optional, locally hosted language renderer; never required for CI."""
    from urllib.parse import urlparse
    parsed = urlparse(endpoint)
    if (parsed.scheme != "http" or parsed.hostname not in
            {"127.0.0.1", "localhost", "::1"}
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError("Only a local Ollama HTTP endpoint is supported")
    reply = _http_json(endpoint.rstrip("/") + "/api/generate", {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "seed": int(seed),
            "num_predict": 320,
        },
    }, timeout=timeout)
    if not isinstance(reply.get("response"), str):
        raise ValueError("Ollama did not produce a text response")
    return {"renderer": "local-ollama", "model": model, "seed": seed,
            "text": reply["response"],
            "response_sha256": hashlib.sha256(
                reply["response"].encode("utf-8")
            ).hexdigest()}
