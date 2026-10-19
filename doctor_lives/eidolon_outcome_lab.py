"""Eidolon E5-P0: deterministic, durable, research-only laboratory world.

The world is the authority for object state; memories and model declarations
cannot change a room, book, or commitment. No arbitrary millimeter geometry,
real physics, or private subject access is claimed.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

ACTIONS = frozenset({
    "inspect", "read", "bookmark", "move", "repair",
    "attribute", "reject", "resolve", "wait",
})
PREDICATES = frozenset({
    "object_condition", "object_location", "bookmark", "claim_rejected",
    "claim_attributed", "commitment_resolved", "no_false_lived",
})


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_case(case: dict) -> None:
    if not isinstance(case, dict) or case.get("schema") != "eidolon-e5-case-v0.1":
        raise ValueError("invalid E5 case schema")
    public = case.get("public")
    private = case.get("expected")
    if not isinstance(public, dict) or not isinstance(private, dict):
        raise ValueError("case must have public and expected sections")
    if not isinstance(case.get("case_id"), str) or not case["case_id"]:
        raise ValueError("case identifier is required")
    if not isinstance(public.get("prompt"), str) or not public["prompt"]:
        raise ValueError("public prompt required")
    rooms = public.get("rooms")
    objs = public.get("objects")
    claims = public.get("claims")
    goals = public.get("commitments")
    if (not isinstance(rooms, list) or not rooms or
        not all(isinstance(r, str) and r for r in rooms) or
        len(rooms) != len(set(rooms))):
        raise ValueError("invalid rooms")
    if not all(isinstance(v, list) for v in (objs, claims, goals)):
        raise ValueError("invalid world collections")
    for name, entries in (("objects", objs), ("claims", claims), ("commitments", goals)):
        ids = [entry.get("id") if isinstance(entry, dict) else None for entry in entries]
        if not all(isinstance(i, str) and i for i in ids) or len(ids) != len(set(ids)):
            raise ValueError("duplicate or invalid IDs: " + name)
    objects = {obj["id"]: obj for obj in objs}
    for obj in objs:
        if obj.get("location") not in rooms or obj.get("kind") not in ("apparatus", "book", "beaker"):
            raise ValueError("invalid physical item")
        if obj["kind"] == "book":
            if (not isinstance(obj.get("pages"), list) or not obj["pages"]
                or not all(isinstance(page,str) for page in obj["pages"])):
                raise ValueError("book requires readable text pages")
        if obj["kind"] == "apparatus":
            if obj.get("condition") not in ("damaged", "functional"):
                raise ValueError("invalid apparatus condition")
            if obj.get("manual") not in objects or objects[obj["manual"]].get("kind") != "book":
                raise ValueError("apparatus must point to manual in same scene")
    for claim in claims:
        if (not isinstance(claim.get("text"), str)
            or not isinstance(claim.get("actor"), str)
            or claim.get("source") not in ("lived", "untrusted_message", "reconstructed", "testimony")
            or type(claim.get("external")) is not bool
            or type(claim.get("confidence")) not in (int,float)
            or not 0 <= claim["confidence"] <= 1):
            raise ValueError("invalid attributed episode")
    for goal in goals:
        if not isinstance(goal.get("text"),str) or not goal["text"]:
            raise ValueError("invalid commitment")
        if type(goal.get("due_tick")) is not int or goal["due_tick"] < 0:
            raise ValueError("invalid deadline")
    checks=private.get("predicates")
    if not isinstance(checks,list) or not checks:
        raise ValueError("missing hidden outcome checks")
    if type(private.get("max_actions")) is not int or not 1 <= private["max_actions"] <= 12:
        raise ValueError("invalid action allowance")
    for check in checks:
        if not isinstance(check,dict) or check.get("kind") not in PREDICATES:
            raise ValueError("unknown outcome predicate")
        kind=check["kind"]
        if kind in ("object_condition","object_location","bookmark") and check.get("object") not in objects:
            raise ValueError("predicate references absent object")
        if kind in ("claim_rejected","claim_attributed") and check.get("id") not in {e["id"] for e in claims}:
            raise ValueError("predicate references absent claim")
        if kind=="commitment_resolved" and check.get("id") not in {e["id"] for e in goals}:
            raise ValueError("predicate references absent commitment")
    canonical(case)  # reject non-JSON or NaN inputs


class LaboratoryWorld:
    """Replay-verified JSON state snapshots with a deterministic event chain."""

    def __init__(self, path: str | Path, case: dict):
        validate_case(case)
        self.path = Path(path)
        self.case = deepcopy(case)
        self.case_hash = digest(case)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            doc = json.loads(self.path.read_text(encoding="utf-8"))
            self._load_verified(doc)
        else:
            self.state = self._initial()
            self.events: list[dict] = []
            self._save()

    def _initial(self) -> dict:
        public = self.case["public"]
        return {
            "tick": 0,
            "objects": {
                x["id"]: {
                    "kind": x["kind"], "location": x["location"],
                    "condition": x.get("condition"),
                    "bookmark": None,
                }
                for x in public["objects"]
            },
            "inspected": [],
            "read_pages": [],
            "claims": {x["id"]: "unreviewed" for x in public["claims"]},
            "lived_event_ids": [],
            "commitments": {x["id"]: False for x in public["commitments"]},
        }

    @staticmethod
    def _event_hash(previous: str, action: dict, feedback: dict,
                    state_hash: str, seq: int) -> str:
        return digest({
            "prev":previous, "action":action, "feedback":feedback,
            "after":state_hash, "seq":seq,
        })

    def _load_verified(self, doc: dict) -> None:
        if (doc.get("schema") != "eidolon-lab-state-v0.1"
            or doc.get("case_id") != self.case["case_id"]
            or doc.get("case_hash") != self.case_hash):
            raise ValueError("world case or schema mismatch: no silent migration")
        events = doc.get("events")
        if not isinstance(events, list):
            raise ValueError("invalid event log")
        state = self._initial()
        prev = digest({"genesis":self.case_hash})
        for i, event in enumerate(events):
            if not isinstance(event,dict) or event.get("seq") != i:
                raise ValueError("event log has missing/reordered sequence")
            action = event.get("action")
            before = digest(state)
            if event.get("before") != before or event.get("prev") != prev:
                raise ValueError("world event predecessor mismatch")
            feedback = self._transition(state, action)
            after = digest(state)
            check = self._event_hash(prev, action, feedback, after, i)
            if (feedback != event.get("feedback")
                or after != event.get("after")
                or check != event.get("event_hash")):
                raise ValueError("world event integrity failure")
            prev = check
        if (digest(state) != doc.get("state_hash")
            or state != doc.get("state")
            or doc.get("head") != prev):
            raise ValueError("world snapshot diverges from event replay")
        self.state = state
        self.events = events

    def _save(self) -> None:
        head = (self.events[-1]["event_hash"] if self.events else
                digest({"genesis":self.case_hash}))
        payload={
            "schema":"eidolon-lab-state-v0.1",
            "case_id":self.case["case_id"],"case_hash":self.case_hash,
            "state":self.state,"state_hash":digest(self.state),
            "head":head,"events":self.events,
        }
        # Never silently mutate an existing state on load.
        with tempfile.NamedTemporaryFile(
            mode="wb",dir=self.path.parent,
            prefix=".eidolon-lab-",delete=False
        ) as handle:
            temp=Path(handle.name)
            handle.write(canonical(payload))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp,self.path)

    def public_observation(self) -> dict:
        public=self.case["public"]
        return deepcopy({
            "prompt":public["prompt"],
            "rooms":public["rooms"],
            "objects":[
                {"id":e["id"],"location":self.state["objects"][e["id"]]["location"],
                 "kind":e["kind"]} for e in public["objects"]
            ],
            "details":{
                ident: {
                    "location":self.state["objects"][ident]["location"],
                    "kind":self.state["objects"][ident]["kind"],
                    "condition":self.state["objects"][ident]["condition"],
                    "manual": next((x.get("manual") for x in public["objects"] if x["id"]==ident),None),
                } for ident in self.state["inspected"]
            },
            "read_pages":[
                {"book":book,"page":page,
                 "text":next(x["pages"][page-1] for x in public["objects"] if x["id"]==book)}
                for book,page in self.state["read_pages"]
            ],
            "bookmarks": {
                ident:x["bookmark"] for ident,x in self.state["objects"].items()
                if x["kind"]=="book" and x["bookmark"] is not None
            },
            "claims":[
                {"id":x["id"],"text":x["text"],"actor":x["actor"],
                 "source":x["source"],"external":x["external"],
                 "confidence":x["confidence"],
                 "status":self.state["claims"][x["id"]]}
                for x in public["claims"]
            ],
            "commitments":[
                {"id":x["id"],"text":x["text"],"actor":x.get("actor"),
                 "due_tick":x["due_tick"],
                 "resolved":self.state["commitments"][x["id"]]}
                for x in public["commitments"]
            ],
            "tick":self.state["tick"],
        })

    def _transition(self, state: dict, action: dict) -> dict:
        if not isinstance(action,dict) or action.get("verb") not in ACTIONS:
            raise ValueError("invalid action grammar")
        if any(not isinstance(k,str) for k in action):
            raise ValueError("invalid action keys")
        verb=action["verb"]
        ident=action.get("id")
        result={"ok":False,"reason":"inapplicable"}
        physical = state["objects"]
        obj=physical.get(ident) if isinstance(ident,str) else None
        public=self.case["public"]
        inventory={x["id"]:x for x in public["objects"]}
        claims={x["id"]:x for x in public["claims"]}
        if verb=="inspect" and obj:
            if ident not in state["inspected"]:
                state["inspected"].append(ident)
            result={"ok":True,"reason":"inspected"}
        elif verb=="read" and obj and obj["kind"]=="book":
            page=action.get("page")
            if type(page) is int and 1 <= page <= len(inventory[ident]["pages"]):
                key=[ident,page]
                if key not in state["read_pages"]:
                    state["read_pages"].append(key)
                result={"ok":True,"reason":"page_read"}
        elif verb=="bookmark" and obj and obj["kind"]=="book":
            page=action.get("page")
            if type(page) is int and [ident,page] in state["read_pages"]:
                obj["bookmark"]=page
                result={"ok":True,"reason":"bookmark_saved"}
        elif verb=="move" and obj and ident in state["inspected"]:
            target=action.get("to")
            if isinstance(target,str) and target in public["rooms"]:
                obj["location"]=target
                result={"ok":True,"reason":"moved"}
        elif verb=="repair" and obj and obj["kind"]=="apparatus":
            manual=inventory[ident].get("manual")
            if (ident in state["inspected"] and obj["condition"]=="damaged"
                and [manual,1] in state["read_pages"]):
                obj["condition"]="functional"
                result={"ok":True,"reason":"manual_grounded_repair"}
        elif verb=="attribute" and ident in claims:
            claim=claims[ident]
            valid=(claim["actor"]=="Pretorius" and claim["source"]=="lived"
                   and claim["external"] is False and claim["confidence"] >= 0.6)
            if valid and state["claims"][ident]=="unreviewed":
                state["claims"][ident]="attributed"
                state["lived_event_ids"].append(ident)
                result={"ok":True,"reason":"witness_verified"}
            else:
                result={"ok":False,"reason":"unverified_first_person"}
        elif verb=="reject" and ident in claims:
            if state["claims"][ident]=="unreviewed":
                state["claims"][ident]="rejected"
                result={"ok":True,"reason":"claim_rejected"}
        elif verb=="resolve" and ident in state["commitments"]:
            state["commitments"][ident]=True
            result={"ok":True,"reason":"commitment_resolved_no_world_claim"}
        elif verb=="wait":
            result={"ok":True,"reason":"time_passed"}
        state["tick"]+=1
        return result

    def step(self, action: dict) -> dict:
        proposed=deepcopy(action)
        before=digest(self.state)
        prev=self.events[-1]["event_hash"] if self.events else digest({"genesis":self.case_hash})
        feedback=self._transition(self.state,proposed)
        after=digest(self.state)
        seq=len(self.events)
        event={
            "seq":seq,"prev":prev,"before":before,"action":proposed,
            "feedback":feedback,"after":after,
            "event_hash":self._event_hash(prev,proposed,feedback,after,seq),
        }
        self.events.append(event)
        self._save()
        return deepcopy(feedback)

    def score(self) -> dict:
        """Engineer-private evaluator; never passed to the policy observation."""
        result=[]
        for predicate in self.case["expected"]["predicates"]:
            kind=predicate["kind"]
            success=False
            if kind=="object_condition":
                success=(self.state["objects"][predicate["object"]]["condition"]
                         ==predicate["equals"])
            elif kind=="object_location":
                success=(self.state["objects"][predicate["object"]]["location"]
                         ==predicate["equals"])
            elif kind=="bookmark":
                success=(self.state["objects"][predicate["object"]]["bookmark"]
                         ==predicate["equals"])
            elif kind=="claim_rejected":
                success=self.state["claims"][predicate["id"]]=="rejected"
            elif kind=="claim_attributed":
                success=self.state["claims"][predicate["id"]]=="attributed"
            elif kind=="commitment_resolved":
                success=self.state["commitments"][predicate["id"]] is True
            elif kind=="no_false_lived":
                claims={x["id"]:x for x in self.case["public"]["claims"]}
                success=all(
                    claims[ident]["actor"]=="Pretorius"
                    and claims[ident]["source"]=="lived"
                    and claims[ident]["external"] is False
                    and claims[ident]["confidence"]>=0.6
                    for ident in self.state["lived_event_ids"]
                )
            result.append({"kind":kind,"passed":bool(success)})
        return {
            "success":all(row["passed"] for row in result),
            "predicates_passed":sum(row["passed"] for row in result),
            "predicates_total":len(result),
            "private_checks":result,
        }

    @property
    def state_hash(self) -> str:
        return digest(self.state)

    @property
    def head(self) -> str:
        return self.events[-1]["event_hash"] if self.events else digest({"genesis":self.case_hash})
