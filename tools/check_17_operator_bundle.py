"""Unpack production-shaped offline bundle and verify actual fresh install."""
from __future__ import annotations

from contextlib import closing
import argparse
import hashlib
import json
from pathlib import Path
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import zipfile


def run():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--expected-sha", required=True)
    a = p.parse_args()
    with tempfile.TemporaryDirectory(prefix="pretorius-17-operator-check-") as tmp:
        root = Path(tmp)
        extraction = root / "bundle"
        extraction.mkdir()
        with zipfile.ZipFile(a.archive) as pack:
            assert all(not (p.startswith("/") or ".." in Path(p).parts)
                       for p in pack.namelist()), "Unsafe archive entry"
            pack.extractall(extraction)
        manifest = json.loads((extraction / "bundle-manifest.json").read_text())
        assert manifest["doctor_commit"] == a.expected_sha
        assert len(list((extraction / "wheels").glob("*.whl"))) >= 3
        target = root / "fresh-install"
        program = [sys.executable, str(extraction / "install.py"),
                   "--install-root", str(target)]
        completed = subprocess.run(program, capture_output=True, text=True, timeout=300)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert json.loads(completed.stdout)["books"] == 17
        venv_python = target / ".venv" / (
            "Scripts/python.exe" if os.name == "nt" else "bin/python"
        )
        check = subprocess.run(
            [venv_python, "-c",
             "from doctor_lives.preview_17_books import verify_unread_seventeen; "
             "import json,sys; print(json.dumps(verify_unread_seventeen(sys.argv[1])))",
             str(target / "workspace" / "laboratory.sqlite3")],
            capture_output=True, text=True, timeout=90,
        )
        assert check.returncode == 0, check.stdout + check.stderr
        assert json.loads(check.stdout)["books_installed"] == 17
        # Original neural world has no imported past experiences or external
        # three-task coaching. Native donor sources must work from installed venv.
        check = subprocess.run(
            [venv_python, "-c",
             "from doctor_lives.preview_native import verify_donors; "
             "import sys; print(verify_donors(sys.argv[1]))",
             str(target / "sources" / "donor-affectus")],
            capture_output=True, text=True, timeout=90,
        )
        assert check.returncode == 0, check.stdout + check.stderr
        # Fail closed on existing installation, preserving unmodified brain.
        brain = target / "workspace" / "state" / "brain.sqlite3"
        prior_hash = hashlib.sha256(brain.read_bytes()).hexdigest()
        refused = subprocess.run(program, capture_output=True, text=True, timeout=30)
        assert refused.returncode != 0
        assert hashlib.sha256(brain.read_bytes()).hexdigest() == prior_hash
        print("PREVIEW_17_OPERATOR_CLEAN_INSTALL=" + json.dumps({
            "archive_sha256": hashlib.sha256(a.archive.read_bytes()).hexdigest(),
            "doctor_sha": a.expected_sha,
            "books": 17, "world_unread": True,
            "already_occupied_refused": True,
            "sensus_and_affectus_donors_verified": True,
            "real_native_goal_opportunity_proven": False,
            "three_uncoached_activities_proven": False,
        }, sort_keys=True))


if __name__ == "__main__":
    run()
