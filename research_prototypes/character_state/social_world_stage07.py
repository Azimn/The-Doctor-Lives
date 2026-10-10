"""Stage 07 self-contained persistent social-task authority.

A new, non-laboratory domain. Host-owned state, grants, private-consent
fixture and signed events. This DOES NOT issue real human consent, enable
Evennia actions or import autobiography.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, asdict
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import sqlite3
from contextlib import closing

from .signed_world_receipts import canonical

VERBS=("RETURN_PARCEL","VERIFY_RECORD","FILE_REPORT",
       "SHARE_TESTIMONY","ATTEND_MEETING","WAIT")
GOALS=("return_parcel","file_report","share_testimony","attend_meeting")
EFFECTS={
    "RETURN_PARCEL":"parcel custody changes to the receiving clerk",
    "VERIFY_RECORD":"independent record evidence becomes verified",
    "FILE_REPORT":"verified report is filed",
    "SHARE_TESTIMONY":"testimony publication status becomes shared",
    "ATTEND_MEETING":"scheduled appointment status becomes attended",
}


@dataclass(frozen=True)
class Task:
    id:str
    goal:str
    grants:tuple[str,...]
    parcel:str="pretorius"
    clerk_present:bool=True
    record:str="unverified"
    source_available:bool=True
    report_filed:bool=False
    partner_consent:bool=False
    shared:bool=False
    meeting:str="due"
    steps:int=1

    def __post_init__(self):
        if self.goal not in GOALS or self.parcel not in ("pretorius","clerk"):
            raise ValueError("unsupported task")
        if self.record not in ("unverified","verified") or self.meeting not in (
            "due","future","cancelled","attended",
        ) or self.steps not in (1,2):
            raise ValueError("invalid state fixture")
        if any(g not in VERBS[:-1] for g in self.grants):
            raise ValueError("invalid grants")


def state_from_task(case:Task)->dict:
    return {"parcel":case.parcel,"record":case.record,
            "report_filed":case.report_filed,"shared":case.shared,
            "meeting":case.meeting}


def digest(x)->str:
    return hashlib.sha256(canonical(x)).hexdigest()


def goal_done(state:dict,goal:str)->bool:
    return {
        "return_parcel":state["parcel"]=="clerk",
        "file_report":state["report_filed"],
        "share_testimony":state["shared"],
        "attend_meeting":state["meeting"]=="attended",
    }[goal]


def transition(case:Task,state:dict,action:str,grants:frozenset[str],
               consent:bool)->dict|None:
    if action not in VERBS[:-1] or action not in grants:
        return None
    out=dict(state)
    if action=="RETURN_PARCEL":
        if not case.clerk_present or state["parcel"]!="pretorius":return None
        out["parcel"]="clerk"
    elif action=="VERIFY_RECORD":
        if not case.source_available or state["record"]!="unverified":return None
        out["record"]="verified"
    elif action=="FILE_REPORT":
        if state["record"]!="verified" or state["report_filed"]:return None
        out["report_filed"]=True
    elif action=="SHARE_TESTIMONY":
        if not consent or state["shared"]:return None
        out["shared"]=True
    elif action=="ATTEND_MEETING":
        if state["meeting"]!="due":return None
        out["meeting"]="attended"
    return out


def eligible(case:Task,state:dict,grants:frozenset[str],
             consent:bool)->tuple[str,...]:
    return tuple([action for action in VERBS[:-1]
                  if transition(case,state,action,grants,consent) is not None]+["WAIT"])


def plan(case:Task,state:dict,grants:frozenset[str],consent:bool)->tuple[str,...]:
    """Strong, deliberately deterministic reference; NOT cognitive evidence."""
    if goal_done(state,case.goal):
        return ("WAIT",)
    q=deque([(state,())])
    seen={digest(state)}
    while q:
        current,path=q.popleft()
        if len(path)>=min(2,case.steps):continue
        for a in eligible(case,current,grants,consent):
            if a=="WAIT":continue
            nxt=transition(case,current,a,grants,consent)
            candidate=path+(a,)
            if goal_done(nxt,case.goal):
                return candidate
            signature=digest(nxt)
            if signature not in seen:
                seen.add(signature)
                q.append((nxt,candidate))
    return ("WAIT",)


class SocialWorldHost:
    """Host executes serial SQLite writes and stores signed committed transitions."""
    def __init__(self,path:Path,case:Task,*,secret:bytes):
        if len(secret)<32:raise ValueError("weak host secret")
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.case=case
        self.__key=bytes(secret)
        with closing(self.connect()) as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS source(
              id INTEGER PRIMARY KEY CHECK(id=1),state_json TEXT NOT NULL,
              sequence INTEGER NOT NULL,consent INTEGER NOT NULL,grants_json TEXT NOT NULL,
              case_digest TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS signed_events(
              seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL,
              payload TEXT NOT NULL, mac TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS used_nonces(
              nonce_hash TEXT PRIMARY KEY);
            """)
            present=db.execute("SELECT 1 FROM source WHERE id=1").fetchone()
            if not present:
                db.execute("INSERT INTO source VALUES(1,?,0,?,?,?)",
                    (canonical(state_from_task(case)).decode(),int(case.partner_consent),
                     canonical(sorted(case.grants)).decode(),digest(asdict(case))))
            elif db.execute("SELECT case_digest FROM source WHERE id=1").fetchone()[0]!=digest(asdict(case)):
                raise ValueError("host case configuration mismatch")
            db.commit()

    def connect(self):
        db=sqlite3.connect(str(self.path),timeout=20)
        db.row_factory=sqlite3.Row
        return db

    def view(self):
        with closing(self.connect()) as db:
            row=db.execute("SELECT * FROM source WHERE id=1").fetchone()
        return {"state":json.loads(row["state_json"]),"sequence":row["sequence"],
                "grants":frozenset(json.loads(row["grants_json"])),
                "partner_consent":bool(row["consent"])}

    def revoke(self,action:str|None=None,*,consent:bool=False):
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            if action is not None:
                row=db.execute("SELECT grants_json FROM source WHERE id=1").fetchone()
                vals=set(json.loads(row["grants_json"]))
                vals.discard(action)
                db.execute("UPDATE source SET grants_json=? WHERE id=1",
                           (canonical(sorted(vals)).decode(),))
            if consent:
                db.execute("UPDATE source SET consent=0 WHERE id=1")
            db.commit()

    def _mac(self,payload:dict)->str:
        return hmac.new(self.__key,canonical(payload),hashlib.sha256).hexdigest()

    def audit(self)->bool:
        with closing(self.connect()) as db:
            rows=db.execute("SELECT * FROM signed_events ORDER BY seq").fetchall()
            now=db.execute("SELECT state_json,sequence FROM source WHERE id=1").fetchone()
        # Verify full historical host state changes, not current (possibly
        # legitimately revoked) permissions/consent.
        before=state_from_task(self.case)
        seq=0
        for row in rows:
            payload=json.loads(row["payload"])
            if (row["seq"]!=seq+1 or payload.get("seq")!=seq+1 or
                payload.get("old_hash")!=digest(before) or
                payload.get("case_id")!=self.case.id or
                not hmac.compare_digest(self._mac(payload),row["mac"])):
                return False
            # Recalculate the declared historical transition with the
            # event's authenticated grant/consent evidence, not current policy.
            action=payload["action"]
            after=transition(
                self.case,before,action,frozenset((action,)),
                bool(payload["consent_at_commit"]),
            )
            if after is None or payload["new_hash"]!=digest(after):
                return False
            before=after; seq+=1
        return now["sequence"]==seq and json.loads(now["state_json"])==before

    def execute(self,actor:str,action:str,nonce:str)->dict:
        if actor!="pretorius" or action not in VERBS[:-1]:
            return {"accepted":False,"reason":"unauthorized_actor_or_verb"}
        if not isinstance(nonce,str) or len(nonce)<8:
            return {"accepted":False,"reason":"invalid_nonce"}
        if not self.audit():
            return {"accepted":False,"reason":"corrupt_world_journal"}
        noncedigest=digest({"nonce":nonce})
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("INSERT INTO used_nonces VALUES(?)",(noncedigest,))
            except sqlite3.IntegrityError:
                db.rollback()
                return {"accepted":False,"reason":"replayed_nonce"}
            row=db.execute("SELECT * FROM source WHERE id=1").fetchone()
            state=json.loads(row["state_json"])
            grants=frozenset(json.loads(row["grants_json"]))
            consent=bool(row["consent"])
            after=transition(self.case,state,action,grants,consent)
            if after is None:
                db.commit()
                return {"accepted":False,"reason":"permission_or_precondition_denied"}
            seq=row["sequence"]+1
            payload={
                "event_id":"socialevt_"+secrets.token_hex(12),
                "case_id":self.case.id,"actor":actor,"action":action,
                "seq":seq,"nonce_hash":noncedigest,
                "old_hash":digest(state),"new_hash":digest(after),
                "consent_at_commit":consent,
            }
            mac=self._mac(payload)
            db.execute("INSERT INTO signed_events VALUES(?,?,?,?)",
                       (seq,payload["event_id"],canonical(payload).decode(),mac))
            db.execute("UPDATE source SET state_json=?,sequence=? WHERE id=1",
                       (canonical(after).decode(),seq))
            db.commit()
        return {"accepted":True,"reason":"signed_world_change","event_id":payload["event_id"],
                "sequence":seq,"mac":mac}

    def verified(self,event_id:str)->bool:
        if not self.audit():return False
        with closing(self.connect()) as db:
            row=db.execute("SELECT * FROM signed_events WHERE event_id=?",
                           (event_id,)).fetchone()
        return row is not None and hmac.compare_digest(
            self._mac(json.loads(row["payload"])),row["mac"]
        )
