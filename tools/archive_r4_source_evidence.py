#!/usr/bin/env python3
"""Preserve read-only original R4 evidence for independent replay.

SQLite backup includes committed WAL rows without changing the Laboratory or
canonical BrainStore. This is source retention, never autonomy certification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3


SOURCES = (
    ("laboratory.sqlite3", "original-laboratory.sqlite3"),
    ("state/brain.sqlite3", "canonical-brain.sqlite3"),
    ("preview-activity.jsonl", "preview-activity.jsonl"),
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def capture(workspace: Path, output_dir: Path) -> dict:
    """Fail closed if any original source is absent; never synthesize it."""
    workspace = Path(workspace).resolve(strict=True)
    output_dir = Path(output_dir).resolve()
    if output_dir == workspace or workspace in output_dir.parents:
        raise ValueError("Evidence destination must be outside the live workspace")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError("Evidence destination must be empty")
    for source_name, _ in SOURCES:
        source = workspace / source_name
        if not source.is_file() or source.is_symlink():
            raise FileNotFoundError("Missing original R4 source: " + source_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    captured = {}
    for source_name, archive_name in SOURCES:
        source = workspace / source_name
        destination = output_dir / archive_name
        if source.suffix == ".sqlite3":
            with sqlite3.connect(source.absolute().as_uri() + "?mode=ro", uri=True) as reader:
                with sqlite3.connect(destination) as writer:
                    reader.backup(writer)
            with sqlite3.connect(destination.absolute().as_uri() + "?mode=ro", uri=True) as check:
                if check.execute("PRAGMA quick_check").fetchone() != ("ok",):
                    raise RuntimeError("Invalid archived SQLite source: " + archive_name)
        else:
            with source.open("rb") as reader, destination.open("xb") as writer:
                shutil.copyfileobj(reader, writer)
        captured[archive_name] = {
            "original_relative_path": source_name,
            "sha256": _sha256(destination),
            "bytes": destination.stat().st_size,
        }
    manifest = {
        "schema": "pretorius.r4.original-source-evidence.v1",
        "files": captured,
        "sqlite_backup_includes_committed_wal": True,
        "source_files_modified_by_archiver": False,
        "source_authentication_performed": False,
        "autonomy_credit": False,
        "independent_qa_review_performed": False,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print("R4_ORIGINAL_SOURCE_ARCHIVE=" + json.dumps(
        capture(args.workspace, args.output_dir), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
