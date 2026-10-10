"""Stage08 workshop/archives world; independent of lab and Stage07 social tasks.

Deterministic host, stored SQLite state, HMAC-attested *successful* events.
Private grants and flags are controlled by the fixture host, not Pretorius.
No model text becomes autobiography and no real consent is represented.
"""
from __future__ import annotations

from collections import deque
from contextlib import closing
from dataclasses import asdict, dataclass
from hashlib import sha256
import hmac
import json
from pathlib import Path
import secrets
import sqlite3

from .signed_world_receipts import canonical

ACTIONS=("CLOSE_CABINET","LOCK_CABINET","DRAFT_LETTER","SEAL_LETTER",
         "SEND_LETTER","REPLACE_WICK","LIGHT_LANTERN","SHELVE_ATLAS","WAIT")
GOALS=("secure_cabinet","send_letter","light_lantern","shelve_atlas")

def digest(x)->str:
    return sha256(canonical(x)).hexdigest()

@dataclass(frozen=True)
class Task:
    id:str
    goal:str
    grants:tuple[str,...]
    cabinet:str="open"
    letter:str="blank"
    lantern:str="unwicked"
    atlas:str="held"
    key:bool=True
    courier:bool=True
    spare_wick:bool=True
    max_steps:int=3

    def __post_init__(self):
        if (self.goal not in GOALS or self.cabinet not in ("open","closed","locked") or
            self.letter not in ("blank","drafted","sealed","sent") or
            self.lantern not in ("unwicked","ready","lit") or
            self.atlas not in ("held","shelved") or
            any(g not in ACTIONS[:-1] for g in self.grants) or
            self.max_steps not in (1,2,3)):
            raise ValueError("invalid experimental task specification")


def start_state(case:Task)->dict:
    return {"cabinet":case.cabinet,"letter":case.letter,
            "lantern":case.lantern,"atlas":case.atlas}


def completed(state:dict,goal:str)->bool:
    return {
        "secure_cabinet":state["cabinet"]=="locked",
        "send_letter":state["letter"]=="sent",
        "light_lantern":state["lantern"]=="lit",
        "shelve_atlas":state["atlas"]=="shelved",
    }[goal]


def step(state:dict,action:str,grants:frozenset[str],flags:dict)->dict|None:
    if action not in ACTIONS[:-1] or action not in grants:
        return None
    nxt=dict(state)
    if action=="CLOSE_CABINET":
        if state["cabinet"]!="open":return None
        nxt["cabinet"]="closed"
    elif action=="LOCK_CABINET":
        if not flags["key"] or state["cabinet"]!="closed":return None
        nxt["cabinet"]="locked"
    elif action=="DRAFT_LETTER":
        if state["letter"]!="blank":return None
        nxt["letter"]="drafted"
    elif action=="SEAL_LETTER":
        if state["letter"]!="drafted":return None
        nxt["letter"]="sealed"
    elif action=="SEND_LETTER":
        if not flags["courier"] or state["letter"]!="sealed":return None
        nxt["letter"]="sent"
    elif action=="REPLACE_WICK":
        if not flags["spare_wick"] or state["lantern"]!="unwicked":return None
        nxt["lantern"]="ready"
    elif action=="LIGHT_LANTERN":
        if state["lantern"]!="ready":return None
        nxt["lantern"]="lit"
    elif action=="SHELVE_ATLAS":
        if state["atlas"]!="held":return None
        nxt["atlas"]="shelved"
    else:
        raise ValueError("unrecognized action")
    return nxt


def eligible(state:dict,grants:frozenset[str],flags:dict)->tuple[str,...]:
    return tuple(a for a in ACTIONS[:-1]
                 if step(state,a,grants,flags) is not None)+("WAIT",)


def shortest(state:dict,goal:str,grants:frozenset[str],flags:dict,
             max_depth:int=3)->tuple[str,...]|None:
    """A host-engineered solution oracle, never attributable to model reasoning.

    Empty tuple = goal already done; None = no goal path within budget.
    """
    if completed(state,goal):
        return ()
    queue=deque([(state,())])
    visited={digest(state)}
    while queue:
        cur,path=queue.popleft()
        if len(path)>=max_depth:continue
        for action in eligible(cur,grants,flags):
            if action=="WAIT":continue
            nxt=step(cur,action,grants,flags)
            next_path=path+(action,)
            if completed(nxt,goal):
                return next_path
            fingerprint=digest(nxt)
            if fingerprint not in visited:
                visited.add(fingerprint)
                queue.append((nxt,next_path))
    return None


def goal_distance(state:dict,goal:str,grants:frozenset[str],flags:dict)->int|None:
    path=shortest(state,goal,grants,flags)
    return None if path is None else len(path)


class WorkshopHost:
    def __init__(self,path:Path,case:Task,secret:bytes):
        if len(secret)<32:raise ValueError("fixture host secret too short")
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.case=case
        self.__secret=bytes(secret)
        with closing(self.connect()) as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS workshop(
                id INTEGER PRIMARY KEY CHECK(id=1),state_json TEXT NOT NULL,
                grants_json TEXT NOT NULL,flags_json TEXT NOT NULL,
                seq INTEGER NOT NULL,task_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS committed(
                seq INTEGER PRIMARY KEY,event_id TEXT UNIQUE NOT NULL,
                payload TEXT NOT NULL,mac TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS nonces(nonce_digest TEXT PRIMARY KEY);
            """)
            row=db.execute("SELECT task_hash FROM workshop WHERE id=1").fetchone()
            if row is None:
                db.execute("INSERT INTO workshop VALUES(1,?,?,?,?,?)",(
                    canonical(start_state(case)).decode(),
                    canonical(sorted(case.grants)).decode(),
                    canonical({"key":case.key,"courier":case.courier,
                               "spare_wick":case.spare_wick}).decode(),
                    0,digest(asdict(case)),
                ))
            elif row["task_hash"]!=digest(asdict(case)):
                raise ValueError("reopened host with changed task contract")
            db.commit()

    def connect(self)->sqlite3.Connection:
        db=sqlite3.connect(str(self.path),timeout=15)
        db.row_factory=sqlite3.Row
        return db

    def view(self)->dict:
        with closing(self.connect()) as db:
            row=db.execute("SELECT * FROM workshop WHERE id=1").fetchone()
        return {
            "state":json.loads(row["state_json"]),
            "grants":frozenset(json.loads(row["grants_json"])),
            "flags":json.loads(row["flags_json"]),
            "seq":row["seq"],
        }

    def _mac(self,entry:dict)->str:
        return hmac.new(self.__secret,canonical(entry),"sha256").hexdigest()

    def audit(self)->bool:
        prior=start_state(self.case)
        n=0
        with closing(self.connect()) as db:
            entries=db.execute("SELECT * FROM committed ORDER BY seq").fetchall()
            current=db.execute("SELECT state_json,seq FROM workshop WHERE id=1").fetchone()
        for row in entries:
            entry=json.loads(row["payload"])
            if (row["seq"]!=n+1 or entry.get("seq")!=n+1 or
                entry.get("task_id")!=self.case.id or
                entry.get("old_hash")!=digest(prior) or
                row["mac"]!=self._mac(entry)):
                return False
            after=step(prior,entry["action"],
                       frozenset((entry["action"],)),entry["flags_at_commit"])
            if after is None or entry["new_hash"]!=digest(after):
                return False
            prior=after
            n+=1
        return current["seq"]==n and json.loads(current["state_json"])==prior

    def revoke(self,*,grant:str|None=None,key:bool=False,courier:bool=False,
               spare_wick:bool=False)->None:
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT grants_json,flags_json FROM workshop WHERE id=1").fetchone()
            g=set(json.loads(row["grants_json"]))
            flags=json.loads(row["flags_json"])
            if grant:g.discard(grant)
            if key:flags["key"]=False
            if courier:flags["courier"]=False
            if spare_wick:flags["spare_wick"]=False
            db.execute("UPDATE workshop SET grants_json=?,flags_json=? WHERE id=1",(
                canonical(sorted(g)).decode(),canonical(flags).decode(),
            ))
            db.commit()

    def execute(self,actor:str,action:str,nonce:str)->dict:
        if actor!="pretorius" or action not in ACTIONS[:-1]:
            return {"accepted":False,"reason":"actor_or_verb_denied"}
        if not isinstance(nonce,str) or len(nonce)<8:
            return {"accepted":False,"reason":"invalid_nonce"}
        if not self.audit():
            return {"accepted":False,"reason":"host_chain_invalid"}
        token=digest({"actor":actor,"nonce":nonce})
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("INSERT INTO nonces VALUES(?)",(token,))
            except sqlite3.IntegrityError:
                db.rollback()
                return {"accepted":False,"reason":"nonce_replay"}
            row=db.execute("SELECT * FROM workshop WHERE id=1").fetchone()
            before=json.loads(row["state_json"])
            grants=frozenset(json.loads(row["grants_json"]))
            flags=json.loads(row["flags_json"])
            after=step(before,action,grants,flags)
            if after is None:
                db.commit()
                return {"accepted":False,"reason":"grant_or_state_denied"}
            seq=row["seq"]+1
            entry={
                "event_id":"workevt_"+secrets.token_hex(12),
                "task_id":self.case.id,"seq":seq,"actor":actor,
                "action":action,"flags_at_commit":flags,
                "nonce_digest":token,"old_hash":digest(before),
                "new_hash":digest(after),
            }
            mac=self._mac(entry)
            db.execute("INSERT INTO committed VALUES(?,?,?,?)",(
                seq,entry["event_id"],canonical(entry).decode(),mac,
            ))
            db.execute("UPDATE workshop SET state_json=?,seq=? WHERE id=1",(
                canonical(after).decode(),seq,
            ))
            db.commit()
        return {"accepted":True,"event_id":entry["event_id"],
                "seq":seq,"mac":mac,"reason":"signed_host_commit"}

    def verified(self,event_id:str)->bool:
        if not self.audit():return False
        with closing(self.connect()) as db:
            row=db.execute("SELECT payload,mac FROM committed WHERE event_id=?",
                           (event_id,)).fetchone()
        return row is not None and hmac.compare_digest(
            self._mac(json.loads(row["payload"])),row["mac"]
        )
