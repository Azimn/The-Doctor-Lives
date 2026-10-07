from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).with_name("data")
MANIFEST_NAME = "canonical_evidence_manifest_v1.json"
ACTIVE_SCHEMA = "pretorius-canonical-evidence-active-v1"
SNAPSHOT_SCHEMA = "pretorius-canonical-evidence-snapshot-v1"
AUDIT_SCHEMA = "pretorius-canonical-evidence-audit-v1"


class EvidenceIntegrityError(RuntimeError):
    """Raised when canonical evidence cannot be verified safely."""


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class CanonicalEvidenceAuthority:
    """Versioned authority for Pretorius canonical package evidence."""

    def __init__(
        self,
        state_dir: str | Path,
        *,
        distribution_root: str | Path | None = None,
        manifest_path: str | Path | None = None,
    ):
        self.state_dir = Path(state_dir)
        self.distribution_root = (
            Path(distribution_root) if distribution_root is not None else DATA_DIR
        )
        self.manifest_path = (
            Path(manifest_path)
            if manifest_path is not None
            else self.distribution_root / MANIFEST_NAME
        )
        self.root = self.state_dir / "evidence_authority"
        self.snapshots_dir = self.root / "snapshots"
        self.audit_dir = self.root / "audit"
        self.active_pointer_path = self.root / "active.json"
        self.manifest = self._load_manifest()
        self.manifest_version = int(self.manifest["version"])
        self.manifest_fingerprint = hashlib.sha256(
            _canonical_json_bytes(self.manifest)
        ).hexdigest()
        self._artifacts = {
            str(item["id"]): dict(item) for item in self.manifest["artifacts"]
        }
        self._prepared = False
        self._active_snapshot_id: str | None = None

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.is_file():
            raise EvidenceIntegrityError(
                f"canonical evidence manifest is missing: {self.manifest_path}"
            )
        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise EvidenceIntegrityError(
                f"canonical evidence manifest is unreadable: {self.manifest_path}"
            ) from exc
        if manifest.get("schema") != "pretorius-canonical-evidence-manifest-v1":
            raise EvidenceIntegrityError(
                f"unsupported canonical evidence manifest schema: {manifest.get('schema')!r}"
            )
        if int(manifest.get("version", 0)) < 1:
            raise EvidenceIntegrityError("canonical evidence manifest version must be positive")
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise EvidenceIntegrityError("canonical evidence manifest has no artifacts")
        seen_ids: set[str] = set()
        seen_paths: set[str] = set()
        for item in artifacts:
            if not isinstance(item, dict):
                raise EvidenceIntegrityError("canonical evidence artifact entry is malformed")
            artifact_id = str(item.get("id", ""))
            relative_path = str(item.get("path", ""))
            expected = str(item.get("git_blob_sha1", "")).lower()
            path = Path(relative_path)
            if (
                not artifact_id
                or artifact_id in seen_ids
                or not relative_path
                or relative_path in seen_paths
                or path.is_absolute()
                or ".." in path.parts
                or len(expected) != 40
                or any(ch not in "0123456789abcdef" for ch in expected)
            ):
                raise EvidenceIntegrityError(
                    f"invalid canonical evidence artifact declaration: {item!r}"
                )
            seen_ids.add(artifact_id)
            seen_paths.add(relative_path)
        return manifest

    @property
    def active_snapshot_id(self) -> str:
        if not self._prepared or self._active_snapshot_id is None:
            raise EvidenceIntegrityError("canonical evidence authority is not prepared")
        return self._active_snapshot_id

    @property
    def active_root(self) -> Path:
        return self.snapshots_dir / self.active_snapshot_id

    def _artifact_digest(self, path: Path) -> str:
        if not path.is_file():
            raise EvidenceIntegrityError(f"canonical evidence artifact is missing: {path}")
        return git_blob_sha1(path.read_bytes())

    def _verify_root(self, root: Path, *, label: str) -> None:
        for artifact_id, item in self._artifacts.items():
            path = root / str(item["path"])
            expected = str(item["git_blob_sha1"]).lower()
            if not path.is_file():
                raise EvidenceIntegrityError(
                    f"{label} canonical evidence artifact {artifact_id!r} is missing: {path}"
                )
            actual = self._artifact_digest(path)
            if actual != expected:
                raise EvidenceIntegrityError(
                    f"{label} canonical evidence artifact {artifact_id!r} failed digest verification: "
                    f"expected {expected}, got {actual}"
                )

    def verify_distribution_snapshot(self) -> None:
        self._verify_root(self.distribution_root, label="distribution")

    def _discard_staging(self) -> None:
        if not self.snapshots_dir.exists():
            return
        for path in self.snapshots_dir.iterdir():
            if path.is_dir() and path.name.startswith(".staging-"):
                shutil.rmtree(path)

    def _read_active_pointer(self) -> dict[str, Any]:
        if not self.active_pointer_path.is_file():
            raise EvidenceIntegrityError("canonical evidence active pointer is missing")
        try:
            pointer = json.loads(self.active_pointer_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise EvidenceIntegrityError("canonical evidence active pointer is unreadable") from exc
        if pointer.get("schema") != ACTIVE_SCHEMA:
            raise EvidenceIntegrityError("canonical evidence active pointer schema is invalid")
        return pointer

    def _validate_active_pointer(self, pointer: dict[str, Any]) -> str:
        version = int(pointer.get("manifest_version", -1))
        fingerprint = str(pointer.get("manifest_fingerprint", ""))
        snapshot_id = str(pointer.get("snapshot_id", ""))
        if version != self.manifest_version or fingerprint != self.manifest_fingerprint:
            raise EvidenceIntegrityError(
                "canonical evidence manifest rollback or incompatible manifest detected: "
                f"state has version={version} fingerprint={fingerprint!r}, "
                f"runtime requires version={self.manifest_version} "
                f"fingerprint={self.manifest_fingerprint!r}"
            )
        candidate = Path(snapshot_id)
        if (
            not snapshot_id
            or candidate.is_absolute()
            or candidate.name != snapshot_id
            or snapshot_id in {".", ".."}
        ):
            raise EvidenceIntegrityError("canonical evidence active snapshot id is invalid")
        return snapshot_id

    def _verify_snapshot(self, snapshot_id: str) -> None:
        root = self.snapshots_dir / snapshot_id
        meta_path = root / "snapshot.json"
        if not meta_path.is_file():
            raise EvidenceIntegrityError(
                f"canonical evidence snapshot metadata is missing: {snapshot_id}"
            )
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise EvidenceIntegrityError(
                f"canonical evidence snapshot metadata is unreadable: {snapshot_id}"
            ) from exc
        if (
            meta.get("schema") != SNAPSHOT_SCHEMA
            or int(meta.get("manifest_version", -1)) != self.manifest_version
            or str(meta.get("manifest_fingerprint", "")) != self.manifest_fingerprint
            or str(meta.get("snapshot_id", "")) != snapshot_id
        ):
            raise EvidenceIntegrityError(
                f"canonical evidence snapshot metadata does not match the active manifest: {snapshot_id}"
            )
        self._verify_root(root, label=f"snapshot {snapshot_id!r}")

    def _next_snapshot_id(self, kind: str) -> str:
        stem = f"manifest-v{self.manifest_version}-{self.manifest_fingerprint[:12]}"
        if kind == "initial":
            return stem
        index = 1
        while True:
            candidate = f"{stem}-{kind}-{index:04d}"
            if not (self.snapshots_dir / candidate).exists():
                return candidate
            index += 1

    def _write_json_atomic(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(f".{path.name}.tmp")
        temp.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temp, path)

    def _next_audit_sequence(self) -> int:
        if not self.audit_dir.exists():
            return 1
        values = []
        for path in self.audit_dir.glob("*.json"):
            try:
                values.append(int(path.stem))
            except ValueError:
                continue
        return max(values, default=0) + 1

    def _write_audit_event(
        self,
        *,
        kind: str,
        snapshot_id: str,
        parent_snapshot_id: str | None,
        reason: str,
    ) -> None:
        sequence = self._next_audit_sequence()
        self._write_json_atomic(
            self.audit_dir / f"{sequence:06d}.json",
            {
                "schema": AUDIT_SCHEMA,
                "sequence": sequence,
                "kind": kind,
                "manifest_version": self.manifest_version,
                "manifest_fingerprint": self.manifest_fingerprint,
                "snapshot_id": snapshot_id,
                "parent_snapshot_id": parent_snapshot_id,
                "reason": reason,
            },
        )

    def _copy_distribution_snapshot(
        self,
        *,
        kind: str,
        parent_snapshot_id: str | None,
        reason: str,
    ) -> str:
        snapshot_id = self._next_snapshot_id(kind)
        destination = self.snapshots_dir / snapshot_id
        if destination.exists():
            self._verify_snapshot(snapshot_id)
            return snapshot_id

        staging = self.snapshots_dir / f".staging-{snapshot_id}"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True, exist_ok=False)
        try:
            for item in self._artifacts.values():
                relative = Path(str(item["path"]))
                target = staging / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.distribution_root / relative, target)
            self._write_json_atomic(
                staging / "snapshot.json",
                {
                    "schema": SNAPSHOT_SCHEMA,
                    "snapshot_id": snapshot_id,
                    "manifest_version": self.manifest_version,
                    "manifest_fingerprint": self.manifest_fingerprint,
                    "source": "installed_distribution_snapshot",
                    "kind": kind,
                    "parent_snapshot_id": parent_snapshot_id,
                    "reason": reason,
                },
            )
            self._verify_root(staging, label=f"staging snapshot {snapshot_id!r}")
            os.replace(staging, destination)
        except Exception:
            if staging.exists():
                shutil.rmtree(staging)
            raise
        self._verify_snapshot(snapshot_id)
        return snapshot_id

    def _activate(
        self,
        *,
        snapshot_id: str,
        kind: str,
        parent_snapshot_id: str | None,
        reason: str,
    ) -> None:
        self._write_audit_event(
            kind=kind,
            snapshot_id=snapshot_id,
            parent_snapshot_id=parent_snapshot_id,
            reason=reason,
        )
        self._write_json_atomic(
            self.active_pointer_path,
            {
                "schema": ACTIVE_SCHEMA,
                "manifest_version": self.manifest_version,
                "manifest_fingerprint": self.manifest_fingerprint,
                "snapshot_id": snapshot_id,
            },
        )
        self._active_snapshot_id = snapshot_id
        self._prepared = True

    def prepare(self) -> "CanonicalEvidenceAuthority":
        self.verify_distribution_snapshot()
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self._discard_staging()

        if self.active_pointer_path.exists():
            pointer = self._read_active_pointer()
            snapshot_id = self._validate_active_pointer(pointer)
            self._verify_snapshot(snapshot_id)
            self._active_snapshot_id = snapshot_id
            self._prepared = True
            return self

        snapshot_id = self._copy_distribution_snapshot(
            kind="initial",
            parent_snapshot_id=None,
            reason="Initial adoption of the versioned canonical evidence authority.",
        )
        self._activate(
            snapshot_id=snapshot_id,
            kind="initial_adoption",
            parent_snapshot_id=None,
            reason="Initial adoption of the versioned canonical evidence authority.",
        )
        return self

    def _persisted_manifest_binding(self) -> tuple[str | None, str | None]:
        database = self.state_dir / "brain.sqlite3"
        if not database.is_file():
            return None, None
        try:
            uri = f"file:{database.resolve().as_posix()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True)
            try:
                rows = dict(conn.execute(
                    """SELECT key,value FROM meta
                    WHERE key IN (
                        'canonical_evidence_manifest_version',
                        'canonical_evidence_manifest_fingerprint'
                    )"""
                ).fetchall())
            finally:
                conn.close()
        except sqlite3.DatabaseError as exc:
            raise EvidenceIntegrityError(
                "cannot verify canonical evidence recovery against persisted state binding"
            ) from exc

        version = str(rows.get("canonical_evidence_manifest_version") or "") or None
        fingerprint = (
            str(rows.get("canonical_evidence_manifest_fingerprint") or "") or None
        )
        if (version is None) != (fingerprint is None):
            raise EvidenceIntegrityError(
                "canonical evidence persisted state binding is partial; "
                "explicit repair or migration is required"
            )
        return version, fingerprint

    def recover_from_distribution(self, *, reason: str) -> dict[str, Any]:
        if not reason.strip():
            raise ValueError("canonical evidence recovery requires a non-empty reason")
        self.verify_distribution_snapshot()

        stored_version, stored_fingerprint = self._persisted_manifest_binding()
        if stored_version is not None and (
            stored_version != str(self.manifest_version)
            or stored_fingerprint != self.manifest_fingerprint
        ):
            raise EvidenceIntegrityError(
                "explicit canonical evidence migration required: persisted state is bound to "
                f"version={stored_version} fingerprint={stored_fingerprint!r}, "
                f"runtime recovery offers version={self.manifest_version} "
                f"fingerprint={self.manifest_fingerprint!r}"
            )

        parent_snapshot_id: str | None = None
        if self.active_pointer_path.exists():
            try:
                pointer = self._read_active_pointer()
            except EvidenceIntegrityError:
                pointer = None
            if pointer is not None:
                pointer_version = int(pointer.get("manifest_version", -1))
                pointer_fingerprint = str(pointer.get("manifest_fingerprint", ""))
                if (
                    pointer_version != self.manifest_version
                    or pointer_fingerprint != self.manifest_fingerprint
                ):
                    raise EvidenceIntegrityError(
                        "explicit canonical evidence migration required: active pointer is "
                        "bound to an incompatible manifest; recovery cannot rewrite "
                        "manifest identity"
                    )
                parent_snapshot_id = self._validate_active_pointer(pointer)

        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self._discard_staging()

        snapshot_id = self._copy_distribution_snapshot(
            kind="recovery",
            parent_snapshot_id=parent_snapshot_id,
            reason=reason,
        )
        self._activate(
            snapshot_id=snapshot_id,
            kind="recovery",
            parent_snapshot_id=parent_snapshot_id,
            reason=reason,
        )
        self._verify_snapshot(snapshot_id)
        return {
            "manifest_version": self.manifest_version,
            "manifest_fingerprint": self.manifest_fingerprint,
            "snapshot_id": snapshot_id,
            "parent_snapshot_id": parent_snapshot_id,
            "recovered_from": "installed_distribution_snapshot",
        }

    def artifact_path(self, artifact_id: str) -> Path:
        if not self._prepared:
            self.prepare()
        item = self._artifacts.get(artifact_id)
        if item is None:
            raise KeyError(f"unknown canonical evidence artifact {artifact_id!r}")
        path = self.active_root / str(item["path"])
        expected = str(item["git_blob_sha1"]).lower()
        actual = self._artifact_digest(path)
        if actual != expected:
            raise EvidenceIntegrityError(
                f"active canonical evidence artifact {artifact_id!r} changed after verification: "
                f"expected {expected}, got {actual}"
            )
        return path

    def verify_reference(self, artifact_id: str, git_blob_digest: str) -> bool:
        item = self._artifacts.get(artifact_id)
        if item is None:
            raise EvidenceIntegrityError(
                f"protected evidence reference names unknown artifact {artifact_id!r}"
            )
        expected = str(item["git_blob_sha1"]).lower()
        if git_blob_digest.lower() != expected:
            raise EvidenceIntegrityError(
                f"protected evidence reference digest mismatch for {artifact_id!r}: "
                f"expected {expected}, got {git_blob_digest}"
            )
        self.artifact_path(artifact_id)
        return True

    def status(self) -> dict[str, Any]:
        if not self._prepared:
            self.prepare()
        return {
            "schema": ACTIVE_SCHEMA,
            "manifest_version": self.manifest_version,
            "manifest_fingerprint": self.manifest_fingerprint,
            "snapshot_id": self.active_snapshot_id,
            "artifact_ids": sorted(self._artifacts),
            "distribution_snapshot_verified": True,
            "recovery_policy": "append_only_snapshot_then_atomic_pointer",
        }
