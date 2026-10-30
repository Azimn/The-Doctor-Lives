from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .cognition import PretoriusBrain
from .chassis import PretoriusBrainPort


def emit(value):
    print(json.dumps(value,indent=2,sort_keys=True,default=str))


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="doctor-lives")
    p.add_argument("--state",type=Path,default=Path("state"))
    sp=p.add_subparsers(dest="cmd",required=True)
    sp.add_parser("init")
    x=sp.add_parser("lab-start"); x.add_argument("--world", type=Path, required=True)
    x=sp.add_parser("lab-run"); x.add_argument("--world", type=Path, required=True); x.add_argument("--seconds", type=float, default=60.0); x.add_argument("--interval-seconds", type=float, default=5.0)
    x=sp.add_parser("lab-sleep"); x.add_argument("--world", type=Path, required=True); x.add_argument("--event-id", required=True, help="Stable operator-authorized physical sleep ID; repeat it to replay safely")
    x=sp.add_parser("lab-work"); x.add_argument("--world", type=Path, required=True); x.add_argument("--event-id", required=True, help="Stable work-opportunity ID; original Noesis chooses feasible physical action")
    x=sp.add_parser("lab-backup"); x.add_argument("--world", type=Path, required=True); x.add_argument("--output", type=Path, required=True)
    x=sp.add_parser("lab-restore"); x.add_argument("--world", type=Path, required=True); x.add_argument("--archive", type=Path, required=True)
    x=sp.add_parser("ingest"); x.add_argument("text"); x.add_argument("--source",default="world"); x.add_argument("--kind",default="observation"); x.add_argument("--actor"); x.add_argument("--external",action="store_true"); x.add_argument("--valence",type=float,default=0.0); x.add_argument("--arousal",type=float,default=0.0); x.add_argument("--threat",type=float,default=0.0); x.add_argument("--novelty",type=float,default=0.0); x.add_argument("--authority",type=float,default=0.0); x.add_argument("--autonomy",type=float,default=0.0)
    x=sp.add_parser("think"); x.add_argument("--trigger",default="voluntary")
    x=sp.add_parser("heartbeat"); x.add_argument("--ticks",type=int,default=1)
    x=sp.add_parser("sleep"); x.add_argument("--ticks",type=int,default=12)
    x=sp.add_parser("commit"); x.add_argument("description"); x.add_argument("--actor"); x.add_argument("--due-tick",type=int); x.add_argument("--importance",type=float,default=.6)
    x=sp.add_parser("resolve"); x.add_argument("commitment_id"); x.add_argument("outcome"); x.add_argument("--release",action="store_true")
    x=sp.add_parser("outcome"); x.add_argument("action"); x.add_argument("--success",action="store_true"); x.add_argument("--reward",type=float,default=1.0)
    sp.add_parser("status"); sp.add_parser("view"); sp.add_parser("drift")
    x=sp.add_parser("consolidate"); x.add_argument("--apply",action="store_true")
    x=sp.add_parser("render"); x.add_argument("--input",default=None)
    return p


def main(argv=None) -> int:
    a=parser().parse_args(argv)
    # The CLI is a human report, NOT a trusted physical-world provider.
    # Never hand it raw Experience construction or caller-chosen world proof.
    if a.cmd == "ingest":
        if a.source != "world" or a.external:
            raise PermissionError(
                "CLI cannot certify source identity or external/world truth; "
                "use an authorized provider instead"
            )
        port = PretoriusBrainPort(a.state)
        emit(port.ingest({
            "channel": "user", "text": a.text,
            "actor": a.actor or "CLI operator",
            "source": "cli:user-communication",
            "kind": "communication",
            "valence": a.valence, "arousal": a.arousal,
            "threat": a.threat, "novelty": a.novelty,
            "authority": a.authority, "autonomy": a.autonomy,
        }))
        return 0
    if a.cmd in ("lab-backup", "lab-restore"):
        from .lab_backup import backup, restore
        if a.cmd == "lab-backup":
            emit(backup(a.state, a.world, a.output))
        else:
            emit(restore(a.archive, a.state, a.world))
        return 0
    if a.cmd == "lab-sleep":
        from .lab_runtime import sleep_laboratory
        emit(sleep_laboratory(a.state, a.world, event_id=a.event_id))
        return 0
    if a.cmd == "lab-work":
        from .lab_runtime import work_laboratory
        emit(work_laboratory(a.state, a.world, event_id=a.event_id))
        return 0
    if a.cmd == "lab-run":
        import signal
        from threading import Event
        from .lab_runtime import run_laboratory

        stop = Event()
        previous = {}
        def request_stop(signum, frame):
            stop.set()
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous[signum] = signal.getsignal(signum)
            signal.signal(signum, request_stop)
        try:
            emit(run_laboratory(
                a.state, a.world, duration_seconds=a.seconds,
                interval_seconds=a.interval_seconds, stop=stop,
            ))
        finally:
            for signum, handler in previous.items():
                signal.signal(signum, handler)
        return 0
    if a.cmd == "lab-start":
        from .lab_runtime import _exclusive_host
        # The start/recovery entrypoint must hold BOTH host leases, just like
        # lab-run and lab-sleep. Never open a shared authority first.
        with _exclusive_host(a.state, a.world):
            # Explicit local operator entrypoint. The world and the original
            # neural checkpoint must already exist; never invent either on typo.
            if not a.world.is_file():
                raise FileNotFoundError("Existing authoritative Laboratory world required")
            if not (a.state / "brain.sqlite3").is_file() or not (
                a.state / "pretorius_recurrent.npz"
            ).is_file():
                raise FileNotFoundError("Existing canonical Doctor BrainStore and neural checkpoint required")
            from pretorius_lab.habitat_v2 import SpatialHabitat
            from pretorius_lab.subject_port import SubjectPort
            from .engineer_time import engineer_time
            from .organs import SixOrganRuntime
    
            # All six functional ports wrap the SAME original brain. This host
            # only resumes actions previously authorized and durably reserved.
            # It never chooses a new goal or physical action on behalf of Noesis.
            runtime = SixOrganRuntime.open(a.state)
            bridge = runtime.bind_laboratory(
                SubjectPort(SpatialHabitat(a.world)), authorized=True,
            )
            from .lab_runtime import _recover_shipping_actions
            _, recovered, abandoned = _recover_shipping_actions(bridge)
            clock = engineer_time()
            emit({
                "schema": "doctor-laboratory-offline-start.v1",
                "status": "ready",
                "recovered": len(recovered),
                "abandoned": len(abandoned),
                "subject_frames": [item["subject"] for item in recovered],
                "clock": {"utc": clock.utc_iso, "beat": clock.beat},
            })
            return 0
    brain=PretoriusBrain(a.state)
    if a.cmd=="init": brain.save(); emit(brain.status())
    elif a.cmd=="think": emit(brain.think(a.trigger))
    elif a.cmd=="heartbeat": emit(brain.heartbeat(a.ticks))
    elif a.cmd=="sleep": emit(brain.sleep(a.ticks))
    elif a.cmd=="commit": emit({"id":brain.add_commitment(a.description,a.actor,a.due_tick,a.importance)})
    elif a.cmd=="resolve": brain.resolve_commitment(a.commitment_id,a.outcome,not a.release); emit({"status":"ok"})
    elif a.cmd=="outcome": brain.record_action_outcome(a.action,a.success,a.reward); emit({"status":"ok"})
    elif a.cmd=="status": emit(brain.status())
    elif a.cmd=="view": emit(asdict(brain.cognitive_view()))
    elif a.cmd=="drift": emit(brain.drift_report())
    elif a.cmd=="consolidate": emit(brain.consolidate(apply=a.apply))
    elif a.cmd=="render": emit(brain.render_request(a.input).to_dict())
    return 0

if __name__=="__main__":
    raise SystemExit(main())
