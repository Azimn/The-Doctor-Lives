from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .cognition import PretoriusBrain
from .chassis import PretoriusBrainPort


def emit(value):
    print(json.dumps(value,indent=2,sort_keys=True,default=str))


def emit_laboratory(value, *, human=False, local_model=None):
    """Render only authenticated first-person frames from a trusted host result.

    The JSON report remains the default machine interface. Human mode has no
    input file, provider override, model hook, or access to world/brain
    diagnostics. In particular, never serialize the rest of the host report.
    """
    if local_model is not None:
        from .local_subject_gloss import local_interpretation, valid_local_model
        # Validate the identifier before any host work or local socket use.
        if not human:
            raise ValueError("Local model interpretation requires --human")
        if not valid_local_model(local_model):
            raise ValueError("Invalid local model identifier")
    if not human:
        emit(value)
        return
    allowed = {
        "doctor-laboratory-offline-start.v1",
        "doctor-laboratory-offline-run.v1",
        "doctor-laboratory-offline-sleep.v1",
        "doctor-laboratory-offline-work.v1",
        "doctor-laboratory-offline-opportunity.v1",
    }
    if not isinstance(value, dict) or value.get("schema") not in allowed:
        raise RuntimeError("Unrecognized trusted Laboratory subject report")
    clock, frames = value.get("clock"), value.get("subject_frames")
    if (not isinstance(clock, dict) or not isinstance(clock.get("beat"), str)
            or len(clock["beat"]) != 4 or clock["beat"][0] != "@"
            or not clock["beat"][1:].isdigit() or not isinstance(frames, list)):
        raise RuntimeError("Malformed trusted Laboratory subject report")
    lines = [clock["beat"]]
    for frame in frames:
        if not isinstance(frame, dict) or not isinstance(frame.get("inner"), str):
            raise RuntimeError("Missing source-qualified first-person frame")
        if not frame["inner"].strip():
            raise RuntimeError("Empty source-qualified first-person frame")
        lines.append(frame["inner"])
    if not frames:
        lines.append("(No new first-person account.)")
    print("\n\n".join(lines))
    if local_model is not None and frames:
        note = local_interpretation(frames, local_model)
        if note:
            print("\n[Unverified local-model interpretation; not lived memory]\n" + note)
        else:
            print("\n[Local model unavailable; source-verified account unchanged.]")


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="doctor-lives")
    p.add_argument("--state",type=Path,default=Path("state"))
    sp=p.add_subparsers(dest="cmd",required=True)
    sp.add_parser("init")
    x=sp.add_parser("preview-init", help="Create one new experimental original-Laboratory workspace without overwriting an inhabited state"); x.add_argument("--workspace",type=Path,required=True)
    x=sp.add_parser("chat", help="Two-way source-verified local operator conversation"); x.add_argument("--world",type=Path,required=True); x.add_argument("--text",default=None); x.add_argument("--request-id",default=None); x.add_argument("--day",type=int,default=1); x.add_argument("--local-model",default=None)
    x=sp.add_parser("chat-serve", help="Loopback-only local HTML conversation client"); x.add_argument("--world",type=Path,required=True); x.add_argument("--port",type=int,default=8766); x.add_argument("--local-model",default=None)
    x=sp.add_parser("chat-opportunity", help="Offer Noesis a genuine opportunity to initiate a message"); x.add_argument("--world",type=Path,required=True); x.add_argument("--cycle",type=int,required=True); x.add_argument("--day",type=int,required=True)
    x=sp.add_parser("lab-start"); x.add_argument("--world", type=Path, required=True); x.add_argument("--human", action="store_true", help="Show only verified first-person Laboratory text and Swatch beats"); x.add_argument("--local-render-model", default=None, help="Optional localhost Ollama interpretation, labeled unverified; --human required")
    x=sp.add_parser("lab-run"); x.add_argument("--world", type=Path, required=True); x.add_argument("--seconds", type=float, default=60.0); x.add_argument("--interval-seconds", type=float, default=5.0); x.add_argument("--work-every-seconds", type=float, default=None, help="Optional real-elapsed bench opportunities; original Noesis chooses work, host never moves body"); x.add_argument("--human", action="store_true", help="Show only verified first-person Laboratory text and Swatch beats"); x.add_argument("--local-render-model", default=None, help="Optional localhost Ollama interpretation, labeled unverified; --human required")
    x=sp.add_parser("lab-opportunity", help="Offer original Noesis one source-feasible physical decision without choosing a goal"); x.add_argument("--world", type=Path, required=True); x.add_argument("--allow-world-actions", action="store_true", help="Explicitly authorize Noesis-selected original Laboratory action"); x.add_argument("--human", action="store_true", help="Render only source-verified first-person consequence")
    x=sp.add_parser("lab-native", help="Opt-in original six-organ book/rest goal opportunity, using local pinned donors"); x.add_argument("--world", type=Path, required=True); x.add_argument("--affectus-source", type=Path, required=True); x.add_argument("--steps", type=int, default=1); x.add_argument("--allow-world-actions", action="store_true", help="Explicitly permit original Laboratory movement/book/rest, not new goals")
    x=sp.add_parser("lab-soak"); x.add_argument("--world", type=Path, required=True); x.add_argument("--evidence-log", type=Path, required=True); x.add_argument("--seconds", type=float, default=86400.0); x.add_argument("--segment-seconds", type=float, default=900.0); x.add_argument("--interval-seconds", type=float, default=30.0); x.add_argument("--work-every-seconds", type=float, default=None, help="Offer Noesis real work only at a physically feasible bench")
    x=sp.add_parser("lab-soak-verify"); x.add_argument("--evidence-log", type=Path, required=True); x.add_argument("--world", type=Path, default=None, help="Verify every work receipt against the original Laboratory and canonical Doctor")
    x=sp.add_parser("lab-sleep"); x.add_argument("--world", type=Path, required=True); x.add_argument("--event-id", required=True, help="Stable operator-authorized physical sleep ID; repeat it to replay safely"); x.add_argument("--human", action="store_true", help="Show only verified first-person Laboratory text and Swatch beats"); x.add_argument("--local-render-model", default=None, help="Optional localhost Ollama interpretation, labeled unverified; --human required")
    x=sp.add_parser("lab-work"); x.add_argument("--world", type=Path, required=True); x.add_argument("--event-id", required=True, help="Stable work-opportunity ID; original Noesis chooses feasible physical action"); x.add_argument("--human", action="store_true", help="Show only verified first-person Laboratory text and Swatch beats"); x.add_argument("--local-render-model", default=None, help="Optional localhost Ollama interpretation, labeled unverified; --human required")
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
    # Validate optional model choice before opening world or canonical brain.
    if hasattr(a, "local_render_model") and a.local_render_model is not None:
        from .local_subject_gloss import valid_local_model
        if not a.human or not valid_local_model(a.local_render_model):
            raise ValueError("Local model requires --human and a valid identifier")
    if a.cmd == "preview-init":
        from .lab_preview import initialize_preview
        emit(initialize_preview(a.workspace))
        return 0
    if a.cmd in ("chat", "chat-serve", "chat-opportunity"):
        from .operator_conversation import OperatorConversation
        from .lab_runtime import _exclusive_host
        if getattr(a,"local_model",None) is not None:
            from .local_subject_gloss import valid_local_model
            if not valid_local_model(a.local_model):
                raise ValueError("Only a valid loopback Ollama model may be selected")
        if a.cmd=="chat-serve":
            from .operator_chat_web import serve
            return serve(a.state,a.world,port=a.port,model=a.local_model)
        with _exclusive_host(a.state,a.world):
            conversation=OperatorConversation(a.state,a.world)
            if a.cmd=="chat-opportunity":
                emit(conversation.offer_initiative(a.cycle,day=a.day))
                return 0
            if a.text is not None:
                emit(conversation.submit(a.text,request_id=a.request_id,
                                         day=a.day,model=a.local_model))
                return 0
            print("Pretorius operator chat. Type /quit to exit.")
            while True:
                try:
                    value=input("operator> ").strip()
                except (EOFError,KeyboardInterrupt):
                    break
                if value in ("/quit","/exit"):
                    break
                if value:
                    reply=conversation.submit(value,day=a.day,model=a.local_model)
                    print(reply["text"])
            return 0
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
        emit_laboratory(sleep_laboratory(a.state, a.world, event_id=a.event_id), human=a.human, local_model=a.local_render_model)
        return 0
    if a.cmd == "lab-work":
        from .lab_runtime import work_laboratory
        emit_laboratory(work_laboratory(a.state, a.world, event_id=a.event_id), human=a.human, local_model=a.local_render_model)
        return 0
    if a.cmd == "lab-opportunity":
        from .lab_runtime import offer_laboratory_day
        emit_laboratory(offer_laboratory_day(
            a.state, a.world, allow_world_actions=a.allow_world_actions,
        ), human=a.human)
        return 0
    if a.cmd == "lab-native":
        from .lab_runtime import run_native_laboratory
        emit(run_native_laboratory(
            a.state, a.world, affectus_source=a.affectus_source,
            steps=a.steps, allow_world_actions=a.allow_world_actions,
        ))
        return 0
    if a.cmd == "lab-soak-verify":
        from .lab_soak import read_soak_log, verify_soak_sources
        emit(verify_soak_sources(a.state, a.world, a.evidence_log)
             if a.world is not None else read_soak_log(a.evidence_log))
        return 0
    if a.cmd == "lab-soak":
        import signal
        from threading import Event
        from .lab_soak import soak_laboratory
        stop = Event()
        previous = {}
        def request_stop(signum, frame):
            stop.set()
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous[signum] = signal.getsignal(signum)
            signal.signal(signum, request_stop)
        try:
            emit(soak_laboratory(
                a.state, a.world, a.evidence_log,
                target_seconds=a.seconds, segment_seconds=a.segment_seconds,
                interval_seconds=a.interval_seconds,
                work_interval_seconds=a.work_every_seconds, stop=stop,
            ))
        finally:
            for signum, handler in previous.items():
                signal.signal(signum, handler)
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
            emit_laboratory(run_laboratory(
                a.state, a.world, duration_seconds=a.seconds,
                interval_seconds=a.interval_seconds, stop=stop,
                work_interval_seconds=a.work_every_seconds,
            ), human=a.human, local_model=a.local_render_model)
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
            emit_laboratory({
                "schema": "doctor-laboratory-offline-start.v1",
                "status": "ready",
                "recovered": len(recovered),
                "abandoned": len(abandoned),
                "subject_frames": [item["subject"] for item in recovered],
                "clock": {"utc": clock.utc_iso, "beat": clock.beat},
            }, human=a.human, local_model=a.local_render_model)
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
