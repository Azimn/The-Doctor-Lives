"""Operator-work affordances for the original source-verified Laboratory bridge.

Real, local file and inbox changes live BESIDE the pinned Laboratory's own
physical ledger, with an independently hashed operator receipt ledger. The
original DoctorHomeBridge retains the one durable action-intent lock and the
original BrainStore retains the one lived-memory ingress. No file system action
is authorized by model prose alone.
"""
from __future__ import annotations
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
from typing import Any

from .lab_home_bridge import DoctorHomeBridge, _ACTION_DOMAINS, _stable

_SAFE = re.compile(r"[a-z][a-z0-9_]{2,63}\Z")
_TARGET = re.compile(r"[a-z][a-z0-9_.-]{2,63}\Z")
VERBS = frozenset({"read_document","write_notes","append_journal",
                   "send_operator_message","read_operator_reply"})
DEFAULTS = (
    ("document_read","read the research document", "read_document","research.txt","study"),
    ("document_notes","write notes about the research document","write_notes","notes.txt","reflect"),
    ("daily_journal","append an observation to my daily journal","append_journal","journal.txt","journal"),
    ("operator_message","send a message to my operator's inbox","send_operator_message","inbox.txt","correspond"),
    ("operator_reply","read a reply from my operator's inbox","read_operator_reply","replies.txt","read"),
)
def digest(value):
    return sha256(_stable(value).encode("utf-8")).hexdigest()

class OperatorWork:
    def __init__(self, bridge: DoctorHomeBridge):
        if not isinstance(bridge,DoctorHomeBridge):
            raise TypeError("Must share original DoctorHomeBridge")
        self.bridge=bridge
        self.root=Path(bridge.world.path).resolve().parent
        self.path=Path(str(bridge.world.path)+".operator-work.sqlite3")
        self.workspace=self.root/"operator-workspace"
        self.workspace.mkdir(parents=True,exist_ok=True)
        for name, initial in (("research.txt","A field report on notes, artifacts, and memory.\n"),
                              ("replies.txt","I have received a reply: Continue your observations.\n")):
            p=self.workspace/name
            if not p.exists():
                with p.open("x",encoding="utf-8") as out:
                    out.write(initial)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS operator_affordances(
                    affordance_key TEXT PRIMARY KEY, description TEXT NOT NULL,
                    verb TEXT NOT NULL, target TEXT NOT NULL, goal_type TEXT NOT NULL,
                    introduced_cycle INTEGER NOT NULL, uses INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS operator_events(
                    event_id TEXT PRIMARY KEY, op TEXT NOT NULL,
                    payload_json TEXT NOT NULL, event_hash TEXT NOT NULL UNIQUE
                );
            """)
            for key,description,verb,target,goal in DEFAULTS:
                db.execute("""INSERT OR IGNORE INTO operator_affordances
                    (affordance_key,description,verb,target,goal_type,introduced_cycle)
                    VALUES(?,?,?,?,?,0)""",(key,description,verb,target,goal))

    @contextmanager
    def _connect(self):
        with sqlite3.connect(self.path,timeout=30) as db:
            db.row_factory=sqlite3.Row
            db.execute("PRAGMA busy_timeout=30000")
            db.execute("PRAGMA synchronous=FULL")
            yield db

    def _target(self,name):
        if not isinstance(name,str) or not _TARGET.fullmatch(name):
            raise ValueError("Operator target must be a safe local filename")
        path=self.workspace/name
        if path.is_symlink():
            raise PermissionError("Operator workspace symlink rejected")
        return path

    def register(self,key:str,description:str,verb:str,target:str,goal_type:str,
                 *,introduced_cycle:int):
        """Data-only new capability: no Python changes, no operator action."""
        if (not isinstance(key,str) or not _SAFE.fullmatch(key)
                or verb not in VERBS or not isinstance(description,str)
                or not 4<=len(description)<=160
                or not isinstance(goal_type,str) or not _SAFE.fullmatch(goal_type)
                or type(introduced_cycle) is not int or introduced_cycle<1):
            raise ValueError("Invalid data-described local capability")
        self._target(target)
        with self._connect() as db:
            db.execute("""INSERT INTO operator_affordances
                (affordance_key,description,verb,target,goal_type,introduced_cycle)
                VALUES(?,?,?,?,?,?)""",(key,description,verb,target,goal_type,introduced_cycle))

    def affordances(self,cycle:int)->list[dict[str,Any]]:
        with self._connect() as db:
            rows=[dict(row) for row in db.execute(
                """SELECT affordance_key,description,verb,target,goal_type,
                          introduced_cycle,uses FROM operator_affordances
                          WHERE introduced_cycle<=? ORDER BY affordance_key""",(cycle,))]
        valid=[]
        for row in rows:
            self._target(row["target"])
            # Reading replies is not possible until there is an actual reply,
            # never generate a reply from the model or the host as an outcome.
            if row["verb"]=="read_operator_reply" and not (self.workspace/row["target"]).exists():
                continue
            valid.append(row)
        return valid

    def receipt(self,eid):
        with self._connect() as db:
            row=db.execute("SELECT * FROM operator_events WHERE event_id=?",(eid,)).fetchone()
        if row is None:return None
        event=json.loads(row["payload_json"])
        if (event.get("event_id")!=eid
                or event.get("op")!=row["op"]
                or digest(event)!=row["event_hash"]):
            raise RuntimeError("Source operator receipt hash mismatch")
        return event,row["event_hash"]

    def execute(self, key, *, proposal_id, decision_id, event_id,
                cycle, authorized=False) -> dict:
        """Only a policy-linked, authorized proposal may alter local files."""
        if authorized is not True:
            raise PermissionError("Host permission required; model text is not authority")
        with self.bridge.doctor.brain.store.connect() as db:
            policy=db.execute("SELECT selected_action,trigger,state_pressure_json "
                              "FROM policy_decisions WHERE id=?",(decision_id,)).fetchone()
            proposal=db.execute("SELECT * FROM open_proposals WHERE proposal_id=?",
                                (proposal_id,)).fetchone()
        if policy is None or proposal is None:
            raise PermissionError("No original Noesis policy and proposed intention")
        audit=json.loads(policy["state_pressure_json"])
        if (policy["trigger"]!="noesis_open_choice" or policy["selected_action"]!=key
                or proposal["source"]!="proposed" or proposal["affordance_key"]!=key
                or audit.get("proposal_id")!=proposal_id
                or audit.get("motor_event_id")!=event_id
                or audit.get("motor_authorization")!="authorized"
                or audit.get("selector_authority")!="original_noesis"):
            raise PermissionError("Unbound proposal or non-original motor authorization")
        if not isinstance(event_id,str) or not _SAFE.fullmatch(event_id):
            raise ValueError("Bounded physical action ID required")
        with self._connect() as db:
            cap=db.execute("SELECT * FROM operator_affordances WHERE affordance_key=? "
                           "AND introduced_cycle<=?",(key,cycle)).fetchone()
        if cap is None:
            raise PermissionError("No real currently enabled physical affordance")
        target=self._target(cap["target"])
        # Claim an original Doctor action-intent reservation, not a separate
        # host planner. A failed uncertain post-world operation stays pending.
        _ACTION_DOMAINS.setdefault(key,"operator_events")
        args={"proposal_id":proposal_id,"decision_id":decision_id,
              "cycle":cycle}
        with self.bridge._locked_action_intent(key,event_id,args):
            evidence=self.receipt(event_id)
            if evidence is None:
                text=target.read_text(encoding="utf-8") if target.exists() else ""
                state=self._state(target,int(cap["uses"]))
                source_text=proposal["text"].strip().replace("\n"," ")[:240]
                if cap["verb"] in ("write_notes","append_journal","send_operator_message"):
                    addition=source_text+"\n"
                    next_text=text+addition
                    perceived="I wrote: "+source_text
                else:
                    next_text=text
                    perceived="I read: "+(text[-900:] if text else "There is no reply.")
                new_state=self._state_data(next_text,int(cap["uses"])+1)
                event={
                    "event_id":event_id,"op":key,"verb":cap["verb"],
                    "proposal_id":proposal_id,"decision_id":decision_id,
                    "state_before":state,"state_after":new_state,
                    "file_before_sha":sha256(text.encode()).hexdigest(),
                    "file_after_sha":sha256(next_text.encode()).hexdigest(),
                    "file_append":next_text[len(text):],
                    "target":cap["target"],"subject":{"inner":perceived,
                    "spoken_aloud":None},
                }
                h=digest(event)
                with self._connect() as db:
                    # Durable future-replay receipt BEFORE the file mutation.
                    db.execute("""INSERT INTO operator_events
                        (event_id,op,payload_json,event_hash) VALUES(?,?,?,?)""",
                        (event_id,key,_stable(event),h))
                    db.execute("UPDATE operator_affordances SET uses=uses+1 "
                               "WHERE affordance_key=?",(key,))
                evidence=(event,h)
            event,h=evidence
            current=target.read_text(encoding="utf-8") if target.exists() else ""
            current_hash=sha256(current.encode()).hexdigest()
            if current_hash==event["file_before_sha"]:
                with target.open("w",encoding="utf-8",newline="") as out:
                    out.write(current+event["file_append"])
                    out.flush();os.fsync(out.fileno())
            elif current_hash!=event["file_after_sha"]:
                raise RuntimeError("Operator file changed between receipt and replay")
            final=target.read_text(encoding="utf-8") if target.exists() else ""
            if sha256(final.encode()).hexdigest()!=event["file_after_sha"]:
                raise RuntimeError("Operator receipt not physically fulfilled")
            original=self.bridge._admit_verified(
                event["subject"],"laboratory-home:action:"+h,kind="observation")
            return {"event_id":event_id,"op":key,"receipt_hash":h,
                    "memory_id":original["memory_id"],"status":original["status"]}

    @staticmethod
    def _state_data(text,uses):
        return digest({"content_sha":sha256(text.encode()).hexdigest(),"uses":uses})
    def _state(self,target,uses):
        text=target.read_text(encoding="utf-8") if target.exists() else ""
        return self._state_data(text,uses)
