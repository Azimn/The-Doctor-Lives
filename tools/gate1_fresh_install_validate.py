from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import shutil
import sys
import traceback
from pathlib import Path
from typing import Any


NETWORK_EVENTS: list[str] = []


def _network_guard(event: str, args: tuple[Any, ...]) -> None:
    if event.startswith("socket."):
        NETWORK_EVENTS.append(event)
        raise RuntimeError(f"network access is forbidden during Gate 1 validation: {event}")


sys.addaudithook(_network_guard)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _retrieval_signature(brain, query: str) -> list[dict[str, Any]]:
    _, activated = brain._ranked_memory_sets(14, query=query, audit=False)
    return [
        {
            "record_id": str(row["id"]),
            "score": round(float(score), 12),
        }
        for score, row in activated
    ]


def validate(state_dir: Path, source_root: Path | None) -> dict[str, Any]:
    from doctor_lives import Experience, PretoriusBrain
    import doctor_lives

    package_path = Path(doctor_lives.__file__).resolve()
    if source_root is not None and _inside(package_path, source_root):
        raise RuntimeError(
            f"validation imported doctor_lives from the source checkout: {package_path}"
        )
    if state_dir.exists() and any(state_dir.iterdir()):
        raise RuntimeError(f"validation state directory is not empty: {state_dir}")
    if state_dir.exists():
        shutil.rmtree(state_dir)

    brain = PretoriusBrain(state_dir)
    initial = brain.status()
    ingest = brain.ingest(Experience(
        "Morgan returned the calibration notes and kept the agreed procedure.",
        source="gate1-world",
        kind="interaction",
        actor="Morgan",
        valence=0.65,
        arousal=0.05,
        social=0.8,
        novelty=0.1,
        confidence=0.95,
        tags=("gate1", "continuity", "calibration"),
    ))
    commitment_id = brain.add_commitment(
        "Recheck the calibration record after restart.",
        actor="Morgan",
        importance=0.8,
    )

    before_render_digest = brain.store.digest()
    render = brain.render_request("homunculi calibration continuity")
    after_render_digest = brain.store.digest()
    if before_render_digest != after_render_digest:
        raise AssertionError("render_request mutated canonical durable state")

    retrieval_a = _retrieval_signature(brain, "homunculi continuity")
    retrieval_b = _retrieval_signature(brain, "homunculi continuity")
    if retrieval_a != retrieval_b:
        raise AssertionError("historical retrieval was not deterministic")

    with brain.store.connect() as conn:
        classification = conn.execute(
            """SELECT autobiographical_class,wording
            FROM memory_classifications WHERE memory_id=?""",
            (ingest["memory_id"],),
        ).fetchone()
        relationship = conn.execute(
            "SELECT peer_id,display_name,trust,reliability "
            "FROM relationships WHERE peer_id='morgan'"
        ).fetchone()

    if classification is None:
        raise AssertionError("lived memory classification was not persisted")
    if str(classification["autobiographical_class"]) != "lived_runtime_memory":
        raise AssertionError("lived memory autobiographical class changed")
    if str(classification["wording"]) != "quoted":
        raise AssertionError("lived memory wording provenance changed")
    if relationship is None:
        raise AssertionError("relationship update was not persisted")

    brain.save()
    before_restart = brain.status()
    del brain

    restored = PretoriusBrain(state_dir)
    after_restart = restored.status()
    commitments = {str(x["id"]): x for x in restored.store.open_commitments()}
    relationships = {str(x["peer_id"]): x for x in restored.store.relationships()}

    checks = {
        "renderer_read_only_digest_preserved": before_render_digest == after_render_digest,
        "deterministic_retrieval_preserved": retrieval_a == retrieval_b,
        "restart_state_digest_preserved": (
            before_restart["state_digest"] == after_restart["state_digest"]
        ),
        "restart_tick_preserved": before_restart["tick"] == after_restart["tick"],
        "bootstrap_version_preserved": (
            before_restart["bootstrap_version"] == after_restart["bootstrap_version"]
        ),
        "deep_history_version_preserved": (
            before_restart["deep_history_version"] == after_restart["deep_history_version"]
        ),
        "canonical_evidence_fingerprint_preserved": (
            before_restart["canonical_evidence"]["manifest_fingerprint"]
            == after_restart["canonical_evidence"]["manifest_fingerprint"]
        ),
        "canonical_evidence_snapshot_preserved": (
            before_restart["canonical_evidence"]["snapshot_id"]
            == after_restart["canonical_evidence"]["snapshot_id"]
        ),
        "commitment_recovered": commitment_id in commitments,
        "relationship_recovered": "morgan" in relationships,
        "lived_autobiographical_class_preserved": (
            str(classification["autobiographical_class"]) == "lived_runtime_memory"
        ),
        "lived_wording_provenance_preserved": (
            str(classification["wording"]) == "quoted"
        ),
        "network_attempts": len(NETWORK_EVENTS),
    }
    failed = [
        key for key, value in checks.items()
        if key != "network_attempts" and value is not True
    ]
    if NETWORK_EVENTS:
        failed.append("network_attempts")
    if failed:
        raise AssertionError(f"Gate 1 validation failed checks: {failed}")

    return {
        "schema": "the-doctor-lives.gate1-fresh-install-validation.v1",
        "status": "pass",
        "package_version": importlib.metadata.version("the-doctor-lives"),
        "package_path": str(package_path),
        "python": sys.version,
        "platform": platform.platform(),
        "network_guard": "python audit hook rejects all socket.* events",
        "network_events": list(NETWORK_EVENTS),
        "state_dir": str(state_dir.resolve()),
        "initial": {
            "schema_version": restored.store.meta("schema_version"),
            "bootstrap_version": initial["bootstrap_version"],
            "deep_history_version": initial["deep_history_version"],
            "canonical_evidence_manifest_version": (
                initial["canonical_evidence"]["manifest_version"]
            ),
        },
        "checks": checks,
        "retrieval_signature": retrieval_a,
        "memory_id": ingest["memory_id"],
        "commitment_id": commitment_id,
        "render_schema": render.schema,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()

    try:
        report = validate(args.state, args.source_root)
    except Exception as exc:
        report = {
            "schema": "the-doctor-lives.gate1-fresh-install-validation.v1",
            "status": "fail",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "python": sys.version,
            "platform": platform.platform(),
            "network_events": list(NETWORK_EVENTS),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        raise

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
