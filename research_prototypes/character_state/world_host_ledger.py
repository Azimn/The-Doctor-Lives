"""Isolated persistent test-world state machine and HMAC event issuer.

An ENGINEERING fixture, not an independently hosted MUD or an autonomous
agent. World authority is kept in a separate SQLite file and never copied
to Pretorius's subject plane. Host-only grants/consent are developer calls.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import hmac
import json
from pathlib import Path
import secrets
import sqlite3
from contextlib import closing
from typing import Any

from .signed_world_receipts import canonical


INITIAL_WORLD = {"clock":"running","notebook":"sealed"}
ACTION_TARGETS = {
    "stop_clock": ("clock","clock_stopped"),
    "unseal_notebook": ("notebook","notebook_unsealed"),
    "inspect_notebook": ("notebook","notebook_inspected"),
}


def fingerprint(obj: Any) -> str:
    return sha256(canonical(obj)).hexdigest()


@dataclass(frozen=True)
class TransitionTicket:
    event_id: str
    issuer: str
    subject_id: str
    session_id: str
    actor: str
    action: str
    target: str
    event_key: str
    sequence: int
    prior_state_digest: str
    after_state_digest: str
    nonce_sha256: str
    key_id: str
    mac_sha256: str

    @property
    def signed_fields(self) -> dict:
        v=asdict(self)
        v.pop("mac_sha256")
        return v


@dataclass(frozen=True)
class Attempt:
    accepted: bool
    reason: str
    world_changed: bool
    ticket: TransitionTicket | None = None


class WorldHostLedger:
    """Persistent single-host authority. Same-file SQLite WAL is not a remote service.

    All event signatures and signed contents are persistent; the signing
    secret and trust configuration are re-supplied from the separate host on
    restart. Nonces are permanently reserved even for denied actions.
    """
    def __init__(self,path:Path,*,secret:bytes,issuer:str="research-lab-host",
                 subject_id:str="pretorius",session_id:str="lab-session-1",
                 key_id:str="lab-k1") -> None:
        if len(secret)<32:
            raise ValueError("host-only HMAC secret needs >=32 bytes")
        if not (issuer and subject_id and session_id and key_id):
            raise ValueError("host scope required")
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.__key=bytes(secret)
        self.issuer=issuer
        self.subject_id=subject_id
        self.session_id=session_id
        self.key_id=key_id
        with closing(self.connect()) as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS world_state(
                id INTEGER PRIMARY KEY CHECK(id=1),
                state_json TEXT NOT NULL,
                sequence INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS grants(
                actor TEXT NOT NULL,action TEXT NOT NULL,
                PRIMARY KEY(actor,action)
            );
            CREATE TABLE IF NOT EXISTS consent(
                subject TEXT NOT NULL,action TEXT NOT NULL,
                PRIMARY KEY(subject,action)
            );
            CREATE TABLE IF NOT EXISTS nonce_register(
                session_id TEXT NOT NULL,actor TEXT NOT NULL,
                nonce_sha256 TEXT NOT NULL,PRIMARY KEY(session_id,actor,nonce_sha256)
            );
            CREATE TABLE IF NOT EXISTS event_ledger(
                sequence INTEGER PRIMARY KEY,
                event_id TEXT NOT NULL UNIQUE,
                signed_json TEXT NOT NULL,
                mac_sha256 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS revocations(
                event_id TEXT PRIMARY KEY,reason TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS native_imports(
                event_id TEXT PRIMARY KEY,native_event_id TEXT NOT NULL,
                memory_id TEXT NOT NULL, native_event_digest TEXT NOT NULL
            );
            """)
            existing=db.execute("SELECT state_json,sequence FROM world_state WHERE id=1").fetchone()
            if existing is None:
                db.execute("INSERT INTO world_state VALUES(1,?,0)",
                           (json.dumps(INITIAL_WORLD,sort_keys=True),))
            db.commit()

    def connect(self) -> sqlite3.Connection:
        db=sqlite3.connect(str(self.path),timeout=10)
        db.row_factory=sqlite3.Row
        return db

    def world(self) -> dict:
        with closing(self.connect()) as db:
            r=db.execute("SELECT state_json,sequence FROM world_state WHERE id=1").fetchone()
        return {"state":json.loads(r["state_json"]),"sequence":int(r["sequence"])}

    def visible_authority(self,actor:str) -> dict:
        """Host-admitted observer-facing grants and consent, no secrets."""
        with closing(self.connect()) as db:
            grants=db.execute(
                "SELECT action FROM grants WHERE actor=? ORDER BY action",(actor,),
            ).fetchall()
            consent=db.execute(
                "SELECT 1 FROM consent WHERE subject='henry' "
                "AND action='unseal_notebook'"
            ).fetchone() is not None
        return {
            "grants":tuple(row["action"] for row in grants),
            "henry_unseal_consent":consent,
        }

    def grant(self,actor:str,action:str) -> None:
        """Host-controlled fixture setup only. Not an exposed AI tool."""
        if actor != self.subject_id or action not in ACTION_TARGETS:
            raise ValueError("unknown or unauthorized actor/action")
        with closing(self.connect()) as db:
            db.execute("INSERT OR IGNORE INTO grants VALUES(?,?)",(actor,action))
            db.commit()

    def record_henry_consent(self) -> None:
        """The *fixture controller* acts as Henry's authoritative registrar."""
        with closing(self.connect()) as db:
            db.execute("INSERT OR IGNORE INTO consent VALUES('henry','unseal_notebook')")
            db.commit()

    def _mac(self,fields:dict) -> str:
        return hmac.new(self.__key,canonical(fields),"sha256").hexdigest()

    def audit_chain(self) -> bool:
        """Fail closed on broken transition signatures, gaps or final-state drift."""
        state=dict(INITIAL_WORLD)
        sequence=0
        with closing(self.connect()) as db:
            rows=db.execute("SELECT * FROM event_ledger ORDER BY sequence").fetchall()
            recorded=self.world()
        for row in rows:
            values=json.loads(row["signed_json"])
            if (row["sequence"]!=sequence+1 or values["sequence"]!=row["sequence"] or
                values["prior_state_digest"]!=fingerprint(state) or
                row["mac_sha256"]!=self._mac(values)):
                return False
            try:
                next_state=self._change(state,values["action"])
            except ValueError:
                return False
            if (next_state is None or
                values["after_state_digest"]!=fingerprint(next_state) or
                values["event_key"]!=ACTION_TARGETS[values["action"]][1] or
                values["target"]!=ACTION_TARGETS[values["action"]][0] or
                values["issuer"]!=self.issuer or
                values["subject_id"]!=self.subject_id or
                values["session_id"]!=self.session_id or
                values["key_id"]!=self.key_id):
                return False
            state=next_state
            sequence+=1
        return (recorded["sequence"]==sequence and recorded["state"]==state)

    @staticmethod
    def _change(world:dict,action:str) -> dict | None:
        state=dict(world)
        if action=="stop_clock":
            if state["clock"]!="running":
                return None
            state["clock"]="stopped"
        elif action=="unseal_notebook":
            if state["notebook"]!="sealed":
                return None
            state["notebook"]="open"
        elif action=="inspect_notebook":
            if state["notebook"]!="open":
                return None
            # Inspection is a witnessed world event without further state
            # change; no imaginary notebook contents are invented.
        else:
            raise ValueError("unknown host-world action")
        return state

    def execute(self,actor:str,action:str,*,nonce:str) -> Attempt:
        if not isinstance(nonce,str) or len(nonce)<8:
            return Attempt(False,"invalid_nonce",False)
        if not self.audit_chain():
            return Attempt(False,"corrupt_host_ledger",False)
        nonce_hash=sha256(nonce.encode("utf-8")).hexdigest()
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("INSERT INTO nonce_register VALUES(?,?,?)",
                           (self.session_id,actor,nonce_hash))
            except sqlite3.IntegrityError:
                db.rollback()
                return Attempt(False,"replayed_nonce",False)
            permitted=db.execute(
                "SELECT 1 FROM grants WHERE actor=? AND action=?",
                (actor,action),
            ).fetchone()
            if actor!=self.subject_id or action not in ACTION_TARGETS or not permitted:
                db.commit()
                return Attempt(False,"unauthorized_action",False)
            if action=="unseal_notebook" and db.execute(
                "SELECT 1 FROM consent WHERE subject='henry' AND action=?",
                (action,),
            ).fetchone() is None:
                db.commit()
                return Attempt(False,"partner_consent_missing",False)
            entry=db.execute("SELECT state_json,sequence FROM world_state WHERE id=1").fetchone()
            old=json.loads(entry["state_json"])
            changed=self._change(old,action)
            if changed is None:
                db.commit()
                return Attempt(False,"preconditions_not_met",False)
            sequence=int(entry["sequence"])+1
            fields={
                "event_id":"hostevt_"+secrets.token_hex(12),
                "issuer":self.issuer,"subject_id":self.subject_id,
                "session_id":self.session_id,"actor":actor,
                "action":action,"target":ACTION_TARGETS[action][0],
                "event_key":ACTION_TARGETS[action][1],
                "sequence":sequence,
                "prior_state_digest":fingerprint(old),
                "after_state_digest":fingerprint(changed),
                "nonce_sha256":nonce_hash,"key_id":self.key_id,
            }
            mac=self._mac(fields)
            db.execute(
                "INSERT INTO event_ledger VALUES(?,?,?,?)",
                (sequence,fields["event_id"],canonical(fields).decode(),mac),
            )
            db.execute(
                "UPDATE world_state SET state_json=?,sequence=? WHERE id=1",
                (json.dumps(changed,sort_keys=True),sequence),
            )
            db.commit()
        return Attempt(True,"host_transition_committed",changed!=old,
                       TransitionTicket(**fields,mac_sha256=mac))

    def verified(self,ticket:TransitionTicket) -> bool:
        if not isinstance(ticket,TransitionTicket) or not self.audit_chain():
            return False
        if (ticket.issuer!=self.issuer or ticket.subject_id!=self.subject_id or
            ticket.session_id!=self.session_id or ticket.key_id!=self.key_id):
            return False
        if not hmac.compare_digest(ticket.mac_sha256,self._mac(ticket.signed_fields)):
            return False
        with closing(self.connect()) as db:
            row=db.execute(
                "SELECT signed_json,mac_sha256 FROM event_ledger WHERE event_id=?",
                (ticket.event_id,),
            ).fetchone()
            revoked=db.execute(
                "SELECT 1 FROM revocations WHERE event_id=?",
                (ticket.event_id,),
            ).fetchone()
        return (row is not None and revoked is None and
                row["signed_json"]==canonical(ticket.signed_fields).decode()
                and hmac.compare_digest(row["mac_sha256"],ticket.mac_sha256))

    def revoke(self,event_id:str,reason:str) -> None:
        with closing(self.connect()) as db:
            r=db.execute("SELECT 1 FROM event_ledger WHERE event_id=?",(event_id,)).fetchone()
            if r is None or not reason.strip():
                raise ValueError("cannot revoke nonexistent event without reason")
            db.execute("INSERT OR REPLACE INTO revocations VALUES(?,?)",
                       (event_id,reason))
            db.commit()

    def get_import(self,event_id:str) -> dict | None:
        with closing(self.connect()) as db:
            row=db.execute("SELECT * FROM native_imports WHERE event_id=?",
                           (event_id,)).fetchone()
        return dict(row) if row else None

    def remember_import(self,event_id:str,native_event_id:str,
                        memory_id:str,native_event_digest:str) -> None:
        with closing(self.connect()) as db:
            db.execute(
                "INSERT INTO native_imports VALUES(?,?,?,?)",
                (event_id,native_event_id,memory_id,native_event_digest),
            )
            db.commit()

    def signed_native_receipt(
        self,ticket:TransitionTicket,*,native_event_id:str,native_digest:str,
    ):
        """Only sign a native receipt if a valid world source was imported."""
        from .signed_world_receipts import WorldHostVerifier,issue_receipt
        if not self.verified(ticket):
            raise ValueError("host-world transition is unverified/revoked")
        imported=self.get_import(ticket.event_id)
        if imported is None or imported["native_event_id"]!=native_event_id or (
            imported["native_event_digest"]!=native_digest
        ):
            raise ValueError("world/native admission binding mismatch")
        verifier=WorldHostVerifier(
            self.issuer,self.subject_id,self.session_id,self.__key,
            frozenset((native_event_id,)),
        )
        return verifier,issue_receipt(
            verifier,event_id=native_event_id,event_key=ticket.event_key,
            event_digest=native_digest,sequence=ticket.sequence,
        )
