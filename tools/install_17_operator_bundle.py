#!/usr/bin/env python3
"""Install a complete source-pinned 17-book Pretorius preview, offline.

The archive is prepared in CI from reviewed immutable donors. It contains an
unread original Laboratory, actual Doctor/Ipseity/Laboratory wheels, and pinned
Affectus/Sensus sources. Never touch an existing installation or brain.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


def check_bundle(home: Path) -> dict:
    manifest = json.loads((home / "bundle-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "pretorius.17-book.offline-operator.v1":
        raise RuntimeError("Unrecognized bundle")
    for name, digest in manifest["files"].items():
        path = home / name
        if (path.is_symlink() or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != digest):
            raise RuntimeError("Missing or modified bundle byte content: " + name)
    return manifest


def exec_check(cmd, *, cwd=None):
    subprocess.run([str(v) for v in cmd], cwd=cwd, check=True)


def run():
    parser = argparse.ArgumentParser(description="Install the 17-book Laboratory offline in one new location")
    parser.add_argument("--install-root", type=Path, required=True,
                        help="New empty installation path; existing destinations are refused")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        parser.error("Python 3.12 is required for this reviewed wheel archive")
    home = Path(__file__).resolve().parent
    manifest = check_bundle(home)
    target = args.install_root.expanduser().absolute()
    if target.exists() or target.is_symlink():
        raise FileExistsError("Never overwrite an existing Pretorius: " + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the directory exclusively, then roll it back on any failure.
    target.mkdir()
    completed = False
    try:
        source = target / "sources"
        source.mkdir()
        shutil.copytree(home / "sources" / "donor-sensus", source / "donor-sensus")
        shutil.copytree(home / "sources" / "donor-affectus", source / "donor-affectus")
        template = target / "templates"
        template.mkdir()
        shutil.copy2(home / "unread-17-full-text-lab.sqlite3",
                     template / "unread-17-full-text-lab.sqlite3")
        environment = target / ".venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        executable = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        exec_check([executable, "-m", "pip", "install", "--no-index",
                    "--find-links", home / "wheels",
                    "the-doctor-lives[laboratory]==0.5.0rc2",
                    "synthetic-ipseity==0.9.11"])
        site = subprocess.check_output([
            str(executable), "-c",
            "import sysconfig; print(sysconfig.get_paths()['purelib'])"
        ], text=True).strip()
        # Import the reviewed Sensus checkout as demanded by its source gate,
        # instead of disguising it as an unsigned PyPI wheel.
        (Path(site) / "pretorius_reviewed_sensus.pth").write_text(
            str(source / "donor-sensus") + "\n", encoding="utf-8")
        exec_check([executable, "-c",
                    "from doctor_lives.preview_native import verify_donors; "
                    "import sys; verify_donors(sys.argv[1])",
                    source / "donor-affectus"])
        workspace = target / "workspace"
        exec_check([executable, "-m", "doctor_lives.cli", "preview-init",
                    "--workspace", workspace, "--world-template",
                    template / "unread-17-full-text-lab.sqlite3"])
        result = subprocess.check_output([
            str(executable), "-c",
            "from doctor_lives.preview_17_books import verify_unread_seventeen; "
            "import json,sys; print(json.dumps(verify_unread_seventeen(sys.argv[1])))",
            str(workspace / "laboratory.sqlite3")
        ], text=True)
        assert json.loads(result)["books_installed"] == 17
        launchers = {
            "start": ["preview-start", "--native-affectus-source",
                      str(source / "donor-affectus")],
            "resume": ["preview-resume"],
            "status": ["preview-status"],
            "stop": ["preview-stop"],
        }
        for label, args2 in launchers.items():
            if os.name == "nt":
                command = (f'@echo off\r\n"%~dp0.venv\\Scripts\\python.exe" '
                           f'-m doctor_lives.cli {args2[0]} --workspace "%~dp0workspace"')
                if len(args2) > 1:
                    command += f' --native-affectus-source "%~dp0sources\\donor-affectus"'
                (target / (label + "-preview.cmd")).write_text(command + "\r\n")
            else:
                script = ('#!/bin/sh\nset -eu\n'
                          'DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\n'
                          'exec "$DIR/.venv/bin/python" -m doctor_lives.cli '
                          + args2[0] + ' --workspace "$DIR/workspace"')
                if len(args2) > 1:
                    script += ' --native-affectus-source "$DIR/sources/donor-affectus"'
                path = target / (label + "-preview.sh")
                path.write_text(script + "\n", encoding="utf-8")
                path.chmod(0o755)
        (target / "installed-bundle-receipt.json").write_text(
            json.dumps({
                "schema": "pretorius.17-book.operator-install.v1",
                "doctor_commit": manifest["doctor_commit"],
                "original_laboratory_commit": manifest["laboratory_commit"],
                "sensus_commit": manifest["sensus_commit"],
                "affectus_commit": manifest["affectus_commit"],
                "ipseity_commit": manifest["ipseity_commit"],
                "books": 17, "unread_before_start": True,
                "operator_supplied_goal": None,
                "three_uncoached_activities_verified": False,
                "release_accepted": False,
            }, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        completed = True
        print(json.dumps({"status": "installed", "install_root": str(target),
                          "workspace": str(workspace), "books": 17,
                          "native_mode_available": True,
                          "release_accepted": False}, sort_keys=True))
    finally:
        if not completed:
            shutil.rmtree(target, ignore_errors=False)


if __name__ == "__main__":
    run()
