from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cognition import PretoriusBrain
from .models import Experience


def emit(value):
    print(json.dumps(value,indent=2,sort_keys=True,default=str))


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="doctor-lives")
    p.add_argument("--state",type=Path,default=Path("state"))
    sp=p.add_subparsers(dest="cmd",required=True)
    sp.add_parser("init")
    x=sp.add_parser("ingest"); x.add_argument("text"); x.add_argument("--source",default="world"); x.add_argument("--kind",default="observation"); x.add_argument("--actor"); x.add_argument("--external",action="store_true"); x.add_argument("--valence",type=float,default=0.0); x.add_argument("--arousal",type=float,default=0.0); x.add_argument("--threat",type=float,default=0.0); x.add_argument("--novelty",type=float,default=0.0); x.add_argument("--authority",type=float,default=0.0); x.add_argument("--autonomy",type=float,default=0.0)
    x=sp.add_parser("think"); x.add_argument("--trigger",default="voluntary")
    x=sp.add_parser("sleep"); x.add_argument("--ticks",type=int,default=12)
    x=sp.add_parser("commit"); x.add_argument("description"); x.add_argument("--actor"); x.add_argument("--due-tick",type=int); x.add_argument("--importance",type=float,default=.6)
    x=sp.add_parser("resolve"); x.add_argument("commitment_id"); x.add_argument("outcome"); x.add_argument("--release",action="store_true")
    x=sp.add_parser("outcome"); x.add_argument("action"); x.add_argument("--success",action="store_true"); x.add_argument("--reward",type=float,default=1.0)
    sp.add_parser("status"); sp.add_parser("view"); sp.add_parser("drift")
    x=sp.add_parser("render"); x.add_argument("--input",default=None)
    return p


def main(argv=None) -> int:
    a=parser().parse_args(argv)
    brain=PretoriusBrain(a.state)
    if a.cmd=="init": brain.save(); emit(brain.status())
    elif a.cmd=="ingest": emit(brain.ingest(Experience(a.text,source=a.source,kind=a.kind,actor=a.actor,external=a.external,valence=a.valence,arousal=a.arousal,threat=a.threat,novelty=a.novelty,authority=a.authority,autonomy=a.autonomy)))
    elif a.cmd=="think": emit(brain.think(a.trigger))
    elif a.cmd=="sleep": emit(brain.sleep(a.ticks))
    elif a.cmd=="commit": emit({"id":brain.add_commitment(a.description,a.actor,a.due_tick,a.importance)})
    elif a.cmd=="resolve": brain.resolve_commitment(a.commitment_id,a.outcome,not a.release); emit({"status":"ok"})
    elif a.cmd=="outcome": brain.record_action_outcome(a.action,a.success,a.reward); emit({"status":"ok"})
    elif a.cmd=="status": emit(brain.status())
    elif a.cmd=="view": emit(brain.cognitive_view().__dict__)
    elif a.cmd=="drift": emit(brain.drift_report())
    elif a.cmd=="render": emit(brain.render_request(a.input).to_dict())
    return 0

if __name__=="__main__":
    raise SystemExit(main())
