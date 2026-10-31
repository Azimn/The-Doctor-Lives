"""Independent-process, offline runner-health witness for an existing Laboratory soak.

This records machine/process continuity. It does not certify Laboratory action,
Noesis initiative, lived memory, or independently anchored 86,400-second time.
Run on persistent local/self-hosted hardware, never as a GitHub-hosted soak.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import time

SCHEMA = "pretorius.runner-health-observer.v1"
MIN_QUALIFY_SECONDS = 86400.0


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _boot_identity() -> str:
    if sys.platform.startswith("linux"):
        return Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    if os.name == "nt":
        import subprocess
        command = ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                   "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString('o')"]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if completed.returncode != 0 or not completed.stdout.strip():
            raise RuntimeError("Windows OS boot identity unavailable")
        return completed.stdout.strip()
    raise RuntimeError("Unsupported observer OS: boot identity unavailable")


def _uptime_seconds() -> float:
    if sys.platform.startswith("linux"):
        return float(Path("/proc/uptime").read_text().split()[0])
    if os.name == "nt":
        import ctypes
        kernel = ctypes.windll.kernel32
        kernel.GetTickCount64.restype = ctypes.c_ulonglong
        return kernel.GetTickCount64() / 1000.0
    raise RuntimeError("Unsupported observer OS: uptime unavailable")


def _memory_bytes() -> tuple[int, int]:
    if sys.platform.startswith("linux"):
        values = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, _, raw = line.partition(":")
            if key in ("MemTotal", "MemAvailable"):
                values[key] = int(raw.split()[0]) * 1024
        return values["MemTotal"], values["MemAvailable"]
    if os.name == "nt":
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise RuntimeError("Windows memory telemetry unavailable")
        return status.ullTotalPhys, status.ullAvailPhys
    raise RuntimeError("Unsupported observer OS: memory unavailable")


def _cpu_ticks() -> tuple[int, int]:
    if sys.platform.startswith("linux"):
        parts = Path("/proc/stat").read_text().splitlines()[0].split()
        if parts[0] != "cpu":
            raise RuntimeError("Linux CPU telemetry unavailable")
        values = [int(x) for x in parts[1:]]
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        return sum(values), idle
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        class FILETIME(ctypes.Structure):
            _fields_ = [("low", wintypes.DWORD), ("high", wintypes.DWORD)]
        idle, kernel, user = FILETIME(), FILETIME(), FILETIME()
        if not ctypes.windll.kernel32.GetSystemTimes(
                ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
            raise RuntimeError("Windows CPU telemetry unavailable")
        value = lambda ft: (ft.high << 32) | ft.low
        return value(kernel) + value(user), value(idle)
    raise RuntimeError("Unsupported observer OS: CPU unavailable")


def _process_identity(pid: int) -> str | None:
    if sys.platform.startswith("linux"):
        try:
            raw = Path(f"/proc/{pid}/stat").read_text()
            fields = raw.rsplit(")", 1)[1].split()
            if fields[0] == "Z":
                return None
            return fields[19]  # Kernel process start ticks, field 22.
        except (FileNotFoundError, ProcessLookupError):
            return None
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.windll.kernel32
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = ctypes.c_void_p
        handle = kernel.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFORMATION
        if not handle:
            return None
        try:
            class FILETIME(ctypes.Structure):
                _fields_ = [("low", wintypes.DWORD), ("high", wintypes.DWORD)]
            created, exited, kernel_time, user_time = (FILETIME() for _ in range(4))
            kernel.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(FILETIME)] * 4
            kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD)]
            if not kernel.GetProcessTimes(handle, ctypes.byref(created),
                                          ctypes.byref(exited), ctypes.byref(kernel_time),
                                          ctypes.byref(user_time)):
                raise RuntimeError("Cannot read observed process creation time")
            exit_code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                raise RuntimeError("Cannot read observed process state")
            if exit_code.value != 259:  # STILL_ACTIVE
                return None
            return str((created.high << 32) | created.low)
        finally:
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            kernel.CloseHandle(handle)
    raise RuntimeError("Unsupported observer OS: process identity unavailable")


def _sample(pid: int, disk_path: Path, soak_log: Path | None,
            boot_id: str, process_id: str, previous_cpu: tuple[int, int] | None,
            previous_uptime: float | None) -> tuple[dict, tuple[int, int]]:
    current_id = _process_identity(pid)
    if current_id != process_id:
        raise RuntimeError("Observed Pretorius process exited or PID was reused")
    uptime = _uptime_seconds()
    if (sys.platform.startswith("linux") and _boot_identity() != boot_id) or (
            previous_uptime is not None and uptime + 1 < previous_uptime):
        raise RuntimeError("Observed runner rebooted")
    total, available = _memory_bytes()
    disk = shutil.disk_usage(disk_path)
    cpu = _cpu_ticks()
    busy = None
    if previous_cpu is not None:
        elapsed_ticks = cpu[0] - previous_cpu[0]
        idle_ticks = cpu[1] - previous_cpu[1]
        if elapsed_ticks > 0 and 0 <= idle_ticks <= elapsed_ticks:
            busy = round(100.0 * (elapsed_ticks - idle_ticks) / elapsed_ticks, 2)
    stat = soak_log.stat() if soak_log is not None and soak_log.is_file() else None
    return ({"schema": SCHEMA, "utc": _utc(), "monotonic_ns": time.monotonic_ns(),
             "boot_identity": boot_id, "uptime_seconds": uptime,
             "observed_pid": pid, "process_start_identity": process_id,
             "cpu_busy_percent": busy, "memory_total_bytes": total,
             "memory_available_bytes": available, "disk_total_bytes": disk.total,
             "disk_free_bytes": disk.free, "soak_log_size_bytes": stat.st_size if stat else None,
             "soak_log_mtime_ns": stat.st_mtime_ns if stat else None,
             "runner_health_only": True, "independent_source_attestation": False}, cpu)


def observe(*, pid: int, evidence_log: Path, disk_path: Path, seconds: float,
            interval: float, soak_log: Path | None = None) -> dict:
    if type(pid) is not int or pid <= 0 or not (0 < seconds <= 604800):
        raise ValueError("Valid process PID and positive bounded elapsed duration required")
    if not (0.01 <= interval <= 30.0):
        raise ValueError("Observer interval must be between 0.01 and 30 seconds")
    evidence_log = Path(evidence_log).absolute()
    disk_path = Path(disk_path).resolve(strict=True)
    if not disk_path.exists() or evidence_log.is_symlink():
        raise ValueError("Observer disk path must exist; evidence log cannot be a symlink")
    if soak_log is not None:
        soak_log = Path(soak_log)
        if soak_log.is_symlink():
            raise ValueError("Soak log cannot be a symlink")
    boot_id = _boot_identity()
    process_id = _process_identity(pid)
    if process_id is None:
        raise RuntimeError("Observed Pretorius process is not alive")
    # Never overwrite a previous observer record or share the producer's log.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(evidence_log, flags, 0o600)
    start = time.monotonic_ns()
    last = None
    count = 0
    previous_cpu = None
    previous_uptime = None
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            while True:
                record, previous_cpu = _sample(pid, disk_path, soak_log, boot_id,
                                               process_id, previous_cpu, previous_uptime)
                previous_uptime = record["uptime_seconds"]
                if last is not None and (record["monotonic_ns"] - last) > 60_000_000_000:
                    raise RuntimeError("Unaccounted observer gap exceeds 60 seconds")
                last = record["monotonic_ns"]
                record["sequence"] = count + 1
                stream.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
                count += 1
                elapsed = (last - start) / 1e9
                if elapsed >= seconds:
                    break
                time.sleep(min(interval, max(0, seconds - elapsed)))
    except BaseException:
        # Keep the partial append-only evidence for independent investigation.
        raise
    return {"status": "observer_completed", "observed_pid": pid,
            "boot_identity": boot_id, "samples": count,
            "monotonic_elapsed_seconds": round((last - start) / 1e9, 3),
            "runner_health_only": True, "independent_source_attestation": False,
            "r5_qualified": False, "reason": "World/Noesis/BrainStore and independent clock review required"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--evidence-log", type=Path, required=True)
    parser.add_argument("--disk-path", type=Path, required=True)
    parser.add_argument("--soak-log", type=Path)
    parser.add_argument("--seconds", type=float, default=MIN_QUALIFY_SECONDS)
    parser.add_argument("--interval", type=float, default=30.0)
    args = parser.parse_args()
    result = observe(pid=args.pid, evidence_log=args.evidence_log,
                     disk_path=args.disk_path, seconds=args.seconds,
                     interval=args.interval, soak_log=args.soak_log)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
