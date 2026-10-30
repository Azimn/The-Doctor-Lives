"""Installed-wheel operator lifecycle smoke, not an R4 autonomy acceptance."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


def invoke(console, *args):
    return subprocess.run([console, *args], capture_output=True, text=True, timeout=120)


def await_running(console, workspace, proc):
    deadline = time.monotonic() + 110
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            out, err = proc.communicate()
            raise AssertionError(f"Operator exited early {proc.returncode}: {out} {err}")
        check = invoke(console, "preview-status", "--workspace", str(workspace))
        if check.returncode == 0:
            value = json.loads(check.stdout)
            if value.get("status") == "running":
                assert value["current_activity"] == "original_laboratory_observation"
                assert value["uncoached_three_task_life_proven"] is False
                assert value["last_heartbeat"]
                assert value["uptime_seconds"] >= 0
                return
        time.sleep(0.4)
    raise AssertionError("Operator did not become ready")


def main():
    import doctor_lives
    import pretorius_lab
    assert not os.getenv("PYTHONPATH"), "Source import would mask a wheel failure"
    assert "site-packages" in str(Path(doctor_lives.__file__).resolve())
    assert "site-packages" in str(Path(pretorius_lab.__file__).resolve())
    console = shutil.which("doctor-lives")
    assert console and Path(console).parent == Path(sys.executable).parent

    with tempfile.TemporaryDirectory(prefix="wheel-preview-operator-") as tmp:
        workspace = Path(tmp) / "pretorius"
        absent = invoke(console, "preview-resume", "--workspace", str(workspace))
        assert absent.returncode == 2 and not workspace.exists()
        first = subprocess.Popen(
            [console, "preview-start", "--workspace", str(workspace)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            await_running(console, workspace, first)
            assert (workspace / "state" / "brain.sqlite3").is_file()
            assert (workspace / "laboratory.sqlite3").is_file()
            duplicate = invoke(console, "preview-resume", "--workspace", str(workspace))
            assert duplicate.returncode == 2, duplicate.stdout + duplicate.stderr
            stopping = invoke(console, "preview-stop", "--workspace", str(workspace))
            assert stopping.returncode == 0, stopping.stdout + stopping.stderr
            out, err = first.communicate(timeout=45)
            assert first.returncode == 0, (out, err)
            done = invoke(console, "preview-status", "--workspace", str(workspace))
            assert json.loads(done.stdout)["status"] == "stopped"
            resumed = subprocess.Popen(
                [console, "preview-resume", "--workspace", str(workspace)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            try:
                await_running(console, workspace, resumed)
                stopping = invoke(console, "preview-stop", "--workspace", str(workspace))
                assert stopping.returncode == 0, stopping.stdout + stopping.stderr
                out, err = resumed.communicate(timeout=45)
                assert resumed.returncode == 0, (out, err)
                assert json.loads(invoke(console, "preview-status", "--workspace", str(workspace)).stdout)["run_index"] == 2
            finally:
                if resumed.poll() is None:
                    resumed.kill()
                    resumed.communicate()
        finally:
            if first.poll() is None:
                first.kill()
                first.communicate()
        print(json.dumps({"installed_wheel": True, "operator_lifecycle": "PASS", "r4_autonomy_proven": False}))


if __name__ == "__main__":
    main()
