"""Opt-in, source-pinned access to the user's Phantasmagorium v0.5 donor.

No world, action, canonical memory or executive authority is delegated here.
The donor ZIP is supplied externally and hash-checked. The adapter never
installs a second durable subject store. Night() is a single-night research
probe, NOT the longitudinal Nocturnal Theatre integration.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
import zipfile

from .store import BrainStore

DONOR_SHA256 = "31e31c0a87e155c072227b086cf012a5f1dcb5aa2de51f676b909ae8255454a8"
PREFIX = "Phantasmagorium_v0.5/"
WORKER = r'''
import json, pathlib, sys, tempfile, zipfile
archive = pathlib.Path(sys.argv[1])
method = sys.argv[2]
request = json.load(sys.stdin)
with tempfile.TemporaryDirectory(prefix="pretorius-phanta-donor-") as temp:
    with zipfile.ZipFile(archive) as pack:
        pack.extractall(temp)
    sys.path.insert(0, str(pathlib.Path(temp) / "Phantasmagorium_v0.5"))
    if method == "fancy":
        from phantasmagorium.fancy import free_fancy
        output = free_fancy(request)
    elif method == "night":
        from undertow import UndertowV2
        engine = UndertowV2(pathlib.Path(temp) / "scratch-dreams")
        output = engine.run_night(day=request["day"], seed=request["seed"],
                                  experience=request.get("experience", {}),
                                  rupture_palette=True)
    else:
        raise ValueError("Unsupported organoid method")
    print(json.dumps(output, sort_keys=True, ensure_ascii=False, allow_nan=False))
'''


def verify_archive(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_symlink() or not candidate.is_file():
        raise FileNotFoundError("An existing non-symlinked Phantasmagorium donor ZIP is required")
    candidate = candidate.resolve(strict=True)
    if candidate.stat().st_size > 2_000_000:
        raise ValueError("Oversized organoid donor")
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != DONOR_SHA256:
        raise PermissionError("Unreviewed Phantasmagorium source digest")
    with zipfile.ZipFile(candidate) as archive:
        members = archive.infolist()
        if not members or len(members) > 200:
            raise ValueError("Unreviewed archive membership")
        for item in members:
            name = item.filename
            if (not name.startswith(PREFIX)
                    or name.startswith("/")
                    or "\\" in name
                    or any(part in ("", ".", "..") for part in name.split("/")[:-1])
                    or (item.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError("Unsafe donor archive path")
    return candidate


class PhantasmagoriumBridge:
    """Non-authoritative donor probe; only opaque unadmitted hashes persist."""

    def __init__(self, store: BrainStore, archive: str | Path, *, enabled: bool = False):
        if type(store) is not BrainStore or enabled is not True:
            raise PermissionError("An explicitly enabled canonical BrainStore is required")
        self.store = store
        self.archive = verify_archive(archive)

    def _invoke(self, method: str, request: dict[str, Any]) -> dict:
        if method not in ("fancy", "night") or type(request) is not dict:
            raise ValueError("Unsupported organoid request")
        encoded = json.dumps(request, sort_keys=True, allow_nan=False)
        if len(encoded) > 8192:
            raise ValueError("Oversized organoid request")
        proc = subprocess.run(
            [sys.executable, "-I", "-c", WORKER, str(self.archive), method],
            input=encoded, capture_output=True, text=True, timeout=25,
            cwd=self.archive.parent,
        )
        if proc.returncode != 0:
            raise RuntimeError("Source-pinned organoid worker refused operation: " +
                               proc.stderr[-400:])
        value = json.loads(proc.stdout)
        if type(value) is not dict:
            raise RuntimeError("Unexpected organoid response")
        report = {
            "schema": "pretorius.phantasmagorium.donor-probe.v1",
            "donor_sha256": DONOR_SHA256,
            "method": method,
            "evidence_class": "imagined" if method == "fancy" else "dreamed_not_lived",
            "lived_fact": False,
            "action_authority": False,
            "independent_world_observation": False,
            "longitudinal_dream_continuity_proven": False,
            "result": value,
        }
        serialized = json.dumps(report, sort_keys=True, ensure_ascii=False, allow_nan=False)
        if len(serialized) > 65536:
            raise ValueError("Oversized organoid output")
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        # Keep only opaque provenance in the canonical engineering ledger.
        # Raw imagined/dreamed text CANNOT enter the Doctor's durable memory
        # until a separately proven Ipseity/Mnemosyne admission path exists.
        # This is not a substitute for such a path.
        pending = json.dumps({
            "schema": "pretorius.phantasmagorium.unadmitted-digest.v1",
            "content_sha256": digest,
            "source_sha256": DONOR_SHA256,
            "evidence_class": report["evidence_class"],
            "subject_admitted": False,
            "no_autobiographical_content": True,
        }, sort_keys=True)
        with self.store.transaction() as db:
            self.store.set_meta("phantasmagorium:probe:" + digest, pending, db)
            self.store.bump_state_version(db)
        return {"record_id": digest, "subject_admitted": False, **report}

    def fancy(self, scene: dict, *, seed: int, max_fragments: int = 4) -> dict:
        if type(seed) is not int or not 0 <= seed < 2**63:
            raise ValueError("Invalid fancy seed")
        return self._invoke("fancy", {
            "initial_scene": scene, "seed": seed, "max_fragments": max_fragments
        })

    def single_night_probe(self, *, day: int, seed: int, experience: dict | None = None) -> dict:
        if type(day) is not int or day < 0 or type(seed) is not int or not 0 <= seed < 2**63:
            raise ValueError("Invalid dream parameters")
        # Does not claim prior-night continuity, autonomous scheduling or lived memories.
        return self._invoke("night", {
            "day": day, "seed": seed, "experience": experience or {}
        })
