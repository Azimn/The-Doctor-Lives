#!/usr/bin/env python3
"""Produce a self-contained wheel-based installer from exact pinned sources.

Called only after the existing full-text source/authentic-Laboratory builder
produces an independently verified unread 17-book snapshot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


PINS = {
    "laboratory_commit": "6e49795752835d64fa6fd63d16359669a1ca2ba7",
    "sensus_commit": "802e459ee68950414347d5fa324484c034f57b81",
    "affectus_commit": "904bf11861700739ccc03d4b0d4340ff3422a7d3",
    "ipseity_commit": "e2d1dc3978c952e59d270a29e84704c8a1fe264a",
}


def run():
    p = argparse.ArgumentParser()
    for option in ("wheels", "source-report", "sensus", "affectus", "laboratory", "ipseity", "output"):
        p.add_argument("--" + option, type=Path, required=True)
    p.add_argument("--doctor-commit", required=True)
    p.add_argument("--platform", choices=("windows", "linux"), required=True)
    a = p.parse_args()
    report = json.loads(a.source_report.read_text(encoding="utf-8"))
    if (report["total_full_text_books"] != 17
            or report["pristine_book_count"] != 17
            or report["pristine_prior_world_moves"] != 0
            or report["physical_shelves_verified"] != 17
            or not report["pristine_unread_world_available"]
            or set(report["books"]) != {f"book:{i:03d}" for i in range(1, 18)}):
        raise RuntimeError("17-book builder failed independent source/physics review")
    for key, folder in (
        ("laboratory_commit", a.laboratory),
        ("sensus_commit", a.sensus),
        ("affectus_commit", a.affectus),
        ("ipseity_commit", a.ipseity),
    ):
        actual = subprocess.check_output(["git", "-C", str(folder), "rev-parse", "HEAD"],
                                         text=True).strip()
        if actual != PINS[key]:
            raise RuntimeError("Unreviewed donor checkout: " + key)
    out = a.output.absolute()
    if out.exists():
        raise FileExistsError("Refuse to overwrite a generated bundle")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pretorius-pack-") as root:
        staging = Path(root)
        shutil.copytree(a.wheels, staging / "wheels")
        src = staging / "sources"
        src.mkdir()
        shutil.copytree(a.sensus, src / "donor-sensus")
        shutil.copytree(a.affectus, src / "donor-affectus")
        shutil.copy2(a.source_report.parent / "unread-17-full-text-lab.sqlite3",
                     staging / "unread-17-full-text-lab.sqlite3")
        shutil.copy2(Path(__file__).with_name("install_17_operator_bundle.py"),
                     staging / "install.py")
        files = {}
        for f in sorted(staging.rglob("*")):
            if f.is_symlink():
                raise RuntimeError("Symlink in offline bundle: " + str(f))
            if f.is_file():
                files[f.relative_to(staging).as_posix()] = hashlib.sha256(
                    f.read_bytes()).hexdigest()
        manifest = {
            "schema": "pretorius.17-book.offline-operator.v1",
            "python": "3.12", "platform": a.platform,
            "doctor_commit": a.doctor_commit,
            **PINS, "books": 17,
            "verified_source_report_sha256": hashlib.sha256(
                a.source_report.read_bytes()).hexdigest(),
            "wheels": sorted((staging / "wheels").iterdir(), key=lambda x: x.name)
                and sorted(f.name for f in (staging / "wheels").iterdir()),
            "files": files,
            "clean_install_and_3task_accepted": False,
        }
        (staging / "bundle-manifest.json").write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        with zipfile.ZipFile(out, "x", zipfile.ZIP_DEFLATED,
                             compresslevel=6, allowZip64=True) as zipfile_out:
            for f in sorted(staging.rglob("*")):
                if f.is_file():
                    zipfile_out.write(f, arcname=f.relative_to(staging).as_posix())
    print(json.dumps({"status": "bundled", "archive": str(out),
                      "doctor_commit": a.doctor_commit, "books": 17,
                      "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                      "ready_for_release": False}, sort_keys=True))


if __name__ == "__main__":
    run()
