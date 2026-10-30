"""One-brain, two-way offline operator conversation through the original port.

No remote services, new planner, alternative memories or forged lived facts.
Both terminal and localhost handlers call OperatorConversation.submit().
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
import time
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from .chassis import PretoriusBrainPort
from .conversation_claims import admit_model_draft
from .engineer_time import engineer_time
from .lab_home_bridge import DoctorHomeBridge, _ACTION_DOMAINS, _row
from .local_ollama_transport import post_local_ollama
from .local_subject_gloss import valid_local_model
from .open_lab_bridge import OperatorWork
from .store import new_id, utc_now

class OperatorConversation:
    """No secondary state DB: durable utterances are in original BrainStore."""

    def __init__(self, state_dir: Path, world_file: Path):
        self.state_dir, self.world_file = Path(state_dir), Path(world_file)
        if not self.world_file.is_file() or not (self.state_dir / "brain.sqlite3").is_file() or not (self.state_dir / "pretorius_recurrent.npz").is_file():
            raise FileNotFoundError("Existing original Doctor and Laboratory required")
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.subject_port import SubjectPort
        self.doctor = PretoriusBrainPort(self.state_dir)
        self.bridge = DoctorHomeBridge(self.doctor,
                                       SubjectPort(SpatialHabitat(self.world_file)),
                                       authorized=True)
        self.work = OperatorWork(self.bridge)
        self._guard = threading.RLock()
        with self.doctor.brain.store.transaction() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS operator_conversation_turns (
                turn_id TEXT PRIMARY KEY, role TEXT NOT NULL CHECK(role IN ('operator','pretorius')),
                source_memory_id TEXT, text TEXT NOT NULL, claims_json TEXT NOT NULL,
                model_called INTEGER NOT NULL, model_tokens INTEGER NOT NULL,
                model_latency_ms REAL NOT NULL, beat TEXT NOT NULL, created_utc TEXT NOT NULL,
                simulation_day INTEGER NOT NULL DEFAULT 1
            )""")

    def history(self) -> list[dict]:
        with self.doctor.brain.store.connect() as db:
            rows = db.execute("SELECT * FROM operator_conversation_turns ORDER BY rowid").fetchall()
            result = [dict(row) for row in rows]
        for row in result:
            row["claims"] = json.loads(row.pop("claims_json"))
            row["model_called"] = bool(row["model_called"])
        return result

    def receive(self, text: str, *, turn_id: str | None = None,
                actor: str = "operator", day: int = 1) -> dict:
        """Label speech as operator testimony, never physical observation."""
        if not isinstance(text,str) or not 1 <= len(text.strip()) <= 800:
            raise ValueError("Operator message must contain 1 to 800 characters")
        if not isinstance(day,int) or day < 1:
            raise ValueError("Simulated day must be positive")
        turn_id = turn_id or "operator_" + uuid4().hex
        if not re.fullmatch(r"[a-zA-Z0-9_-]{3,100}",turn_id):
            raise ValueError("Invalid idempotency key")
        with self._guard:
            for row in self.history():
                if row["turn_id"] == turn_id:
                    if row["text"] != text or row["role"] != "operator":
                        raise ValueError("Reused operator key with different content")
                    return row
            # The canonical ingress firewall constructs a *reported utterance*.
            # The only firsthand experience is hearing/reading the message.
            receipt = self.doctor.ingest({
                "channel":"user", "source":"operator:conversation",
                "kind":"communication", "actor":actor, "text":text,
                "confidence":1.0,
            })
            clock = engineer_time()
            with self.doctor.brain.store.transaction() as db:
                db.execute("""INSERT INTO operator_conversation_turns
                    (turn_id,role,source_memory_id,text,claims_json,model_called,
                     model_tokens,model_latency_ms,beat,created_utc,simulation_day)
                    VALUES (?, 'operator', ?, ?, '[]', 0, 0, 0, ?, ?, ?)""",
                    (turn_id,receipt["memory_id"],text,clock.beat,clock.utc_iso,day))
                self.doctor.brain.store.bump_state_version(db)
            self.doctor.save()
            return self.history()[-1]

    def _receipt_verified(self, digest: str) -> bool:
        # Same actual operator-source receipt authority as OperatorWork.
        with self.work._connect() as db:
            matches = [r[0] for r in db.execute(
                "SELECT event_id FROM operator_events WHERE event_hash=?", (digest,))]
        for event_id in matches:
            checked = self.work.receipt(event_id)
            if checked and checked[1] == digest:
                return True
        # Validate original world ledgers using the ORIGINAL bridge's SHA
        # verifier, not merely the memory's claim to have lived an action.
        with sqlite3.connect(self.world_file) as db:
            for table in sorted(set(_ACTION_DOMAINS.values())):
                try:
                    row = db.execute("SELECT event_id FROM " + table +
                                     " WHERE event_hash=?", (digest,)).fetchone()
                except sqlite3.OperationalError:
                    continue
                if row is not None:
                    try:
                        _, real_hash = _row(db,table,row[0])
                    except Exception:
                        return False
                    return real_hash == digest
        return False

    def verified_claims(self) -> list[dict]:
        rows = list(reversed(self.doctor.brain.store.memories(False)))
        verified = []
        for mem in rows:
            if not mem["active"] or mem["evidence_class"] != "lived_runtime_memory":
                continue
            source = mem["source"]
            if source.startswith("laboratory-home:action:"):
                key = source.rsplit(":",1)[-1]
                if self._receipt_verified(key):
                    verified.append({"status":"verified","text":mem["text"],"source":"lived",
                                     "evidence_key":source,"memory_id":mem["id"],
                                     "tick":mem["created_tick"]})
        # A wish is explicitly hypothetical, sourced from its one BrainStore
        # proposal ledger. It is not an action, observation or completed goal.
        with self.doctor.brain.store.connect() as db:
            try:
                wishes=db.execute("""SELECT p.proposal_id,p.text,w.first_cycle
                  FROM open_wishes w JOIN open_proposals p
                  ON p.proposal_id=w.proposal_id ORDER BY w.first_cycle,p.rowid""").fetchall()
            except sqlite3.OperationalError:
                wishes=[]
        for wish in wishes:
            verified.append({"status":"verified","text":"I wished to " + str(wish[1]).removeprefix("I wish to ").rstrip(".") + ".",
                             "source":"wish","evidence_key":"wish:"+wish[0],
                             "tick":int(wish[2])})
        return verified

    def absence(self, days: int = 3) -> dict:
        if days < 1:
            raise ValueError("Days must be positive")
        events = [v for v in self.verified_claims() if v["source"]=="lived"]
        # Order is the original BrainStore admission order, not model prose.
        return {"days":days, "actual_receipt_keys":[e["evidence_key"] for e in events],
                "reported_receipt_keys":[e["evidence_key"] for e in events],
                "claims":events,
                "text":" ".join(e["text"] for e in events) if events
                else "I have no verified completed activities to report."}

    def _local_model(self, question: str, verified: list[dict], model: str | None):
        if model is None:
            return {"called":False,"tokens":0,"latency_ms":0.0,"draft":""}
        if not valid_local_model(model):
            raise ValueError("Invalid local Ollama model")
        prompt = ("Speak naturally to the operator about the conversation. "
                  "Do not invent Pretorius actions or memories. If describing "
                  "his past, ONLY repeat one of the exact first-person sentences "
                  "in verified_claims. Otherwise avoid first-person accounts. "
                  "Only source-qualified firsthand claims are allowed.\n"
                  +json.dumps({"operator_utterance":question,
                    "verified_claims":[v["text"] for v in verified[-8:]]},
                    ensure_ascii=False))
        payload=json.dumps({"model":model,"prompt":prompt,"stream":False,
                            "options":{"temperature":0,"num_predict":128}}).encode()
        start=time.monotonic()
        try:
            raw=post_local_ollama("127.0.0.1",11434,"/api/generate",payload,timeout=35)
            response=json.loads(raw.decode("utf-8"))
            draft=response.get("response","")
            tokens=int(response.get("eval_count",0))
            if not isinstance(draft,str) or tokens < 0:
                raise ValueError("Invalid model reply")
        except (OSError,ValueError,TimeoutError,UnicodeError):
            draft=""; tokens=0
        return {"called":True,"tokens":tokens,
                "latency_ms":round((time.monotonic()-start)*1000,2),
                "draft":draft}

    def respond(self, question: str, *, model: str | None = None,
                turn_id: str | None = None, day: int = 1,
                absence_days: int | None = None) -> dict:
        """Single source-backed reply with a separate unverified model gloss."""
        if not isinstance(question,str) or not question.strip():
            raise ValueError("Question must contain text")
        with self._guard:
            claim_pool=self.verified_claims()
            if absence_days is not None:
                recap=self.absence(absence_days)
                available=recap["claims"]
            else:
                # Bounded relevant autobiographical selection from the
                # actual source ledger. No claim generated from user text.
                terms=set(re.findall(r"[a-z]+",question.casefold()))
                matches=[v for v in claim_pool if
                         set(re.findall(r"[a-z]+",v["text"].casefold())) & terms]
                available=(matches or claim_pool)[-4:]
            use=available
            deterministic=" ".join(c["text"] for c in use)
            if not deterministic:
                deterministic="I have no verified firsthand actions to report."
            inference=self._local_model(question,available,model)
            filtered=admit_model_draft(inference["draft"],available)
            # Exactly sourced first-person facts are always the authoritative
            # output. Local prose is untrusted extra text, not replacing them.
            reply=deterministic
            if filtered.text:
                # Avoid repeating exact verified sentences in model draft.
                gloss=" ".join(s for s in filtered.text.split("\n") if s not in deterministic)
                if gloss.strip() and gloss not in deterministic:
                    reply += "\n" + gloss
            if filtered.blocked_drafts:
                reply += "\n(Unverified firsthand claims withheld.)"
            response_id=turn_id or "pretorius_" + uuid4().hex
            if not re.fullmatch(r"[a-zA-Z0-9_-]{3,100}",response_id):
                raise ValueError("Invalid response ID")
            existing=next((r for r in self.history() if r["turn_id"]==response_id),None)
            if existing:
                return existing
            clock=engineer_time()
            with self.doctor.brain.store.transaction() as db:
                # The reply is indexed as reported outgoing speech, never as
                # a verified physical experience or new historical event.
                mem_id=self.doctor.brain.store.add_memory(
                    db,self.doctor.brain.store.tick,
                    "My outgoing message to the operator: " + reply[:1200],
                    "pretorius:conversation-speech","communication",
                    "external_statement",True,1.0,True,0.35,
                    tags=("self-spoken","conversation-report"))
                db.execute("""INSERT INTO operator_conversation_turns
                    (turn_id,role,source_memory_id,text,claims_json,model_called,
                     model_tokens,model_latency_ms,beat,created_utc,simulation_day)
                    VALUES (?, 'pretorius', ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (response_id,mem_id,reply,json.dumps(use,sort_keys=True),
                     int(inference["called"]),inference["tokens"],inference["latency_ms"],
                     clock.beat,clock.utc_iso,day))
                self.doctor.brain.store.bump_state_version(db)
            self.doctor.save()
            return self.history()[-1] | {
                "blocked_model_firsthand":list(filtered.blocked_drafts),
                "unverified_model_text":list(filtered.model_unverified),
                "verified_memory_share":len(use) / max(1,len(use)+len(filtered.model_unverified))
            }

    def submit(self, text: str, *, request_id: str | None = None,
               model: str | None = None, day: int = 1) -> dict:
        if request_id is None:
            request_id="operator_"+uuid4().hex
        self.receive(text,turn_id=request_id,day=day)
        reply_key="pretorius_"+sha256(request_id.encode()).hexdigest()[:32]
        reply=self.respond(text,model=model,turn_id=reply_key,day=day,
                           absence_days=day if "what have you been doing" in text.casefold() else None)
        return reply

    def offer_initiative(self, cycle: int, *, day: int) -> dict:
        """Offer, do not command: Noesis may select any currently viable work."""
        from .open_inference import DeterministicFallback
        from .open_intentions import (
            propose_intentions, noesis_open_choice, authorized_open_action
        )
        if day < 1:
            raise ValueError("Simulation day required")
        existing=[t for t in self.history() if t["role"]=="pretorius"
                  and t["simulation_day"]==day
                  and t["turn_id"].startswith("initiative_")]
        if len(existing) >= 2:
            return {"initiated":False,"reason":"daily_initiative_limit"}
        proposals=propose_intentions(self.bridge,self.work,DeterministicFallback(),cycle)
        chosen=noesis_open_choice(self.bridge,self.work,proposals,cycle)
        if chosen["selected_affordance"]!="operator_message":
            return {"initiated":False,"reason":"original_noesis_chose_other",
                    "chosen":chosen["selected_affordance"]}
        event=authorized_open_action(self.bridge,self.work,chosen,cycle)
        source,receipt_hash=self.work.receipt(event["event_id"])
        assert receipt_hash == event["receipt_hash"]
        reply=" ".join(source["subject"]["inner"].split())
        clock=engineer_time()
        key="initiative_"+event["event_id"]
        with self.doctor.brain.store.transaction() as db:
            db.execute("""INSERT INTO operator_conversation_turns
                (turn_id,role,source_memory_id,text,claims_json,model_called,
                 model_tokens,model_latency_ms,beat,created_utc,simulation_day)
                VALUES (?, 'pretorius', ?, ?, ?, 0, 0, 0, ?, ?, ?)""",
                (key,event["memory_id"],reply,json.dumps([{
                    "status":"verified","text":reply,"source":"lived",
                    "evidence_key":"laboratory-home:action:"+receipt_hash,
                    "memory_id":event["memory_id"]}],sort_keys=True),
                 clock.beat,clock.utc_iso,day))
            self.doctor.brain.store.bump_state_version(db)
        self.doctor.save()
        return {"initiated":True,"turn_id":key,
                "noesis_decision_id":chosen["decision_id"],"event_id":event["event_id"],
                "reason":"original_noesis_selected_operator_message",
                "source":"laboratory-home:action:"+receipt_hash}
