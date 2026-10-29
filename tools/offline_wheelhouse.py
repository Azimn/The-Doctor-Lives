"""Seal and verify a source-pinned, offline-installable Pretorius wheelhouse.

This manifest detects missing, added or modified wheels and binds an installation
bundle to recorded source commits. It is not a signature or a reproducible-build
attestation. Build wheels online first, then verify and install with --no-index.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "pretorius-offline-wheelhouse.v1"
MANIFEST = "pretorius-wheelhouse-manifest.json"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _files(directory: Path) -> list[Path]:
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError("Wheelhouse must be an existing real directory")
    entries = sorted(directory.iterdir(), key=lambda p: p.name)
    for path in entries:
        if path.is_symlink() or not path.is_file():
            raise ValueError("Wheelhouse contains a symlink or non-file entry")
        if path.name != MANIFEST and not path.name.endswith(".whl"):
            raise ValueError(f"Unexpected wheelhouse member: {path.name}")
    wheels = [p for p in entries if p.suffix == ".whl"]
    names = [p.name.lower().replace("-", "_") for p in wheels]
    for required in ("the_doctor_lives_", "pretorius_laboratory_"):
        if not any(name.startswith(required) for name in names):
            raise ValueError(f"Required distribution missing: {required}")
    return wheels


def _pin(value: str) -> str:
    if not SHA40.fullmatch(value):
        raise ValueError("Source commit must be an exact 40-character lowercase SHA")
    return value


def seal(directory: Path, doctor_sha: str, lab_sha: str) -> dict:
    _pin(doctor_sha)
    _pin(lab_sha)
    manifest_path = directory / MANIFEST
    if manifest_path.exists() or manifest_path.is_symlink():
        raise FileExistsError("Wheelhouse already sealed; do not overwrite manifest")
    wheels = _files(directory)
    result = {
        "schema": SCHEMA,
        "doctor_source_sha": doctor_sha,
        "laboratory_source_sha": lab_sha,
        "wheels": {p.name: {"bytes": p.stat().st_size, "sha256": _sha256(p)} for p in wheels},
    }
    manifest_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def verify(directory: Path, doctor_sha: str, lab_sha: str) -> dict:
    _pin(doctor_sha)
    _pin(lab_sha)
    wheels = _files(directory)
    manifest_path = directory / MANIFEST
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ValueError("Missing or untrusted wheelhouse manifest")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {
        "schema", "doctor_source_sha", "laboratory_source_sha", "wheels"
    }:
        raise ValueError("Unexpected wheelhouse manifest schema")
    if data["schema"] != SCHEMA or data["doctor_source_sha"] != doctor_sha or data["laboratory_source_sha"] != lab_sha:
        raise ValueError("Wheelhouse source commit mismatch")
    records = data["wheels"]
    if not isinstance(records, dict) or set(records) != {p.name for p in wheels}:
        raise ValueError("Wheelhouse member set mismatch")
    for path in wheels:
        record = records[path.name]
        if not isinstance(record, dict) or set(record) != {"bytes", "sha256"}:
            raise ValueError(f"Invalid wheel manifest entry: {path.name}")
        if type(record["bytes"]) is not int or record["bytes"] < 0 or not isinstance(record["sha256"], str) or not SHA256.fullmatch(record["sha256"]):
            raise ValueError(f"Invalid wheel metadata: {path.name}")
        if path.stat().st_size != record["bytes"] or _sha256(path) != record["sha256"]:
            raise ValueError(f"Wheelhouse integrity mismatch: {path.name}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    parser.add_argument("--wheelhouse", required=True, type=Path)
    parser.add_argument("--doctor-sha", required=True)
    parser.add_argument("--lab-sha", required=True)
    args = parser.parse_args()
    action = seal if args.command == "seal" else verify
    result = action(args.wheelhouse, args.doctor_sha, args.lab_sha)
    print(json.dumps({"status": args.command + "ed", "schema": result["schema"],
                      "wheel_count": len(result["wheels"]),
                      "doctor_source_sha": result["doctor_source_sha"],
                      "laboratory_source_sha": result["laboratory_source_sha"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
