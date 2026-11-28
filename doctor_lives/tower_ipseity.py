"""The owning first-person subject in ordinary canonical Tower cognition.

Uses the original PhenomenalEvent / SubjectFrame capabilities, one BrainStore
and one existing recurrent selector. The history is an ordered admission
record in the canonical store, not another biography or independent mind.
Only natural-language SubjectFrame contents cross the conscious boundary;
lineage, proof and latent appraisals remain engineer-only.
"""
from contextlib import closing, contextmanager
from hashlib import sha256
import json
import re
from .models import SubjectFrame, SubjectRendererCapability
from .phenomenology import (PhenomenalEvent, PhenomenalMode, AwarenessLevel,
    PrivacyState, ObjectiveProvenance, SubjectiveSourceAttribution,
    SubjectiveSourceKind, CertaintyBand, assert_subject_text_safe)
from .first_person_governance import first_person_line
from .store import new_id

HEAD = "ipseity:tower-history-head:v1"
RECORD = "ipseity:tower-history:"
VERSION = "tower-owning-subject-v1"
_FIRST = re.compile(r"^(I\b|My\b|Me\b|Mine\b)",re.I)


def _stable(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))


def _digest(value):
    return sha256(_stable(value).encode()).hexdigest()


def _read(db,key):
    row=db.execute("SELECT value FROM meta WHERE key=?",(key,)).fetchone()
    return row["value"] if row else None


class TowerIpseity:
    def __init__(self, brain):
        self.brain=brain
        self.store=brain.store

    def event(self, organ, text, mode, refs=(), *, attribution=SubjectiveSourceKind.UNKNOWN,
              external=False, digest=None, tick=None):
        if not isinstance(text,str) or not _FIRST.match(text.strip()):
            raise PermissionError("Conscious Tower experience must be natural first-person text")
        assert_subject_text_safe(text)
        if first_person_line(text)!=text:
            raise PermissionError("Unsafe or altered first-person experience")
        return (organ, PhenomenalEvent(
            tick=self.store.tick if tick is None else tick,subject_id="pretorius",mode=mode,
            awareness=AwarenessLevel.CONSCIOUS,canonical_first_person=text,
            privacy=PrivacyState.PRIVATE,projection_rule_version=VERSION,
            source_state_digest=digest or self.store.digest(),
            objective_provenance=ObjectiveProvenance(
                evidence_class="owned_subject_projection",source=organ,external=external,
                record_ids=tuple(refs)),
            subjective_source=SubjectiveSourceAttribution(attribution,CertaintyBand.MODERATE),
            source_state_refs=tuple(refs)))

    @staticmethod
    def frame(events):
        if any(e.subject_id!="pretorius" for _,e in events):
            raise PermissionError("Only the one Pretorius subject may enter awareness")
        return SubjectFrame.from_events(e for _,e in events)

    def record(self, db, key, events, *, phase, tick=None):
        """Atomic ordered admission. Replayed source keys never add experience twice."""
        events=tuple(events)
        frame=self.frame(events)
        lines=SubjectRendererCapability.read(frame)
        content=[{"organ":organ,"text":text,"mode":e.mode.value,
                  "attribution":e.subjective_source.kind.value,
                  "source_refs":list(e.source_state_refs),"external":e.objective_provenance.external}
                 for (organ,e),text in zip(events,lines)]
        if key.startswith("recollection:"):
            # Only the active Mnemosyne reflection may admit its selected cue.
            # Raw record/admit_private calls and read-only retrieval cannot mint
            # this handoff. Consume it even if validation or recording fails.
            grant=getattr(self.brain,"_pending_recollection_admission",None)
            self.brain._pending_recollection_admission=None
            expected=(key,phase,content,self.store.tick,self.store.digest(),self.brain.neural.tick)
            if (grant is None or grant!=expected or (tick is not None and tick!=self.store.tick)
                    or _read(db,RECORD+key) is not None):
                raise PermissionError("No fresh one-use selected recollection admission")
        key=RECORD+key
        prior=_read(db,key)
        if prior:
            old=json.loads(prior)
            if old["content"]!=content or old["phase"]!=phase:
                raise PermissionError("Conflicting first-person history replay")
            return old
        previous=json.loads(_read(db,HEAD) or '{"sequence":0,"sha256":null}')
        payload={"subject":"pretorius","sequence":previous["sequence"]+1,
                 "previous_sha256":previous["sha256"],"key":key,
                 "phase":phase,"tick":self.store.tick if tick is None else tick,"content":content}
        entry=dict(payload,sha256=_digest(payload))
        self.store.set_meta(key,_stable(entry),db)
        self.store.set_meta(HEAD,_stable({"sequence":entry["sequence"],"sha256":entry["sha256"]}),db)
        self.store.bump_state_version(db)
        return entry

    def validate_ingress(self, exp, projected):
        """Require the existing typed ingress projection, not a new raw gateway."""
        if first_person_line(exp.text)!=exp.text or not _FIRST.match(exp.text):
            raise PermissionError("Tower input must be natural first-person experience")
        if projected is None:
            if (exp.source.startswith("local-emission:")
                    and exp.kind in ("confirmed_written_utterance","perceived_utterance")):
                return
            raise PermissionError("Tower input requires the canonical ingress projector")
        if (type(projected) is not PhenomenalEvent or projected.subject_id!="pretorius"
                or projected.subject_text!=exp.text
                or SubjectRendererCapability.read(SubjectFrame.from_events((projected,)))!=(exp.text,)):
            raise PermissionError("Projected experience differs from admitted subject")

    def record_ingress(self,db,*,source,kind,text,memory_id,event_id,external,tick,digest,projected=None):
        """Commit all supported ingress channels before recurrent thought."""
        communication=source.startswith("local-conversation:")
        if (source.startswith(("virtual-world:small-tower:", "laboratory-home:"))
                or communication or source.startswith("local-emission:")):
            # Preserve existing source-bound replay format byte for byte.
            organ=("Expression" if kind=="confirmed_written_utterance" else
                   "Corpus" if ":action:" in source else "Sensus")
            attribution=(SubjectiveSourceKind.TOLD if communication else
                         SubjectiveSourceKind.SELF_OBSERVED if organ=="Expression" else SubjectiveSourceKind.LIVED)
            mode=PhenomenalMode.SELF_PERCEPTION if organ=="Expression" else PhenomenalMode.PERCEPT
            refs=(memory_id,) if communication else (memory_id,event_id)
            reported=communication or external
        else:
            if projected is None:
                raise PermissionError("Non-world input lacks typed provenance")
            mode=projected.mode
            attribution=projected.subjective_source.kind
            organ=("Corpus" if mode==PhenomenalMode.BODILY_SENSATION else
                   "Mnemosyne" if mode==PhenomenalMode.RECOLLECTION else "Sensus")
            refs=(memory_id,event_id,*projected.source_state_refs)
            reported=external or projected.objective_provenance.external
        event=self.event(organ,text,mode,refs,attribution=attribution,external=reported,
                         digest=digest,tick=tick)
        return self.record(db,("communication:" if communication else "acquisition:")+memory_id,
                           (event,),phase="communication" if communication else "acquisition",tick=tick)

    def acquisition(self, memory_id):
        memory=self.store.get_memory(memory_id)
        if (not memory or not memory["active"] or memory["external"]
                or memory["evidence_class"]!="lived_runtime_memory"
                or not memory.get("source_event_id")):
            raise PermissionError("Owned acquisition requires an actual admitted experience")
        organ=("Expression" if memory["kind"]=="confirmed_written_utterance" else
               "Corpus" if ":action:" in memory["source"] else "Sensus")
        kind=(SubjectiveSourceKind.SELF_OBSERVED if organ=="Expression" else SubjectiveSourceKind.LIVED)
        event=self.event(organ,memory["text"],PhenomenalMode.SELF_PERCEPTION if organ=="Expression"
                         else PhenomenalMode.PERCEPT,(memory_id,memory["source_event_id"]),attribution=kind)
        with self.store.transaction() as db:
            return self.record(db,"acquisition:"+memory_id,(event,),phase="acquisition")

    def commitment_event(self, item, digest):
        """Reacquire my own earlier native decision; do not assume every row is mine."""
        source=item["source"]
        prefix="telos:native:"
        if not source.startswith(prefix+"tower:") and not source.startswith(prefix+"tower-prospective:"):
            return None
        pid=source.rsplit(":",1)[-1]
        with closing(self.store.connect()) as db:
            policy=db.execute("SELECT selected_action,state_pressure_json FROM policy_decisions "
                              "WHERE id=? AND trigger='noesis_world_affordance'",(pid,)).fetchone()
            thought=db.execute("SELECT id,text FROM thoughts WHERE generated_by=?",
                               ("noesis_world_affordance:"+pid,)).fetchone()
            if not policy or not thought or not thought["text"].startswith("I intend to "):
                return None
            if source.startswith(prefix+"tower-prospective:"):
                raw=_read(db,"telos:tower-prospective:"+item["id"])
                if not raw:
                    raise PermissionError("Own prospective commitment lacks origin")
                goal=json.loads(raw)
                candidate=json.loads(policy["state_pressure_json"]).get("prospective_goals",{}).get("candidates",{}).get(policy["selected_action"])
                if (not candidate or goal["origin_policy_id"]!=pid
                        or goal["description"]!=item["description"]
                        or any(goal[k]!=candidate[k] for k in ("target","room","prior_policy_id","prior_memory_id"))):
                    raise PermissionError("Own prospective commitment differs from prior decision")
                origin=db.execute("SELECT id,text FROM thoughts WHERE generated_by=?",
                                  ("ipseity_prospective:"+pid,)).fetchone()
                if origin and origin["text"]!="I intend to "+item["description"]+".":
                    raise PermissionError("First-person intention differs from protected goal")
                refs=(item["id"],pid,thought["id"])+( (origin["id"],) if origin else ())
            else:
                if thought["text"].removeprefix("I intend to ").rstrip(".")!=item["description"]:
                    raise PermissionError("Own motor intention differs from prior thought")
                refs=(item["id"],pid,thought["id"])
        return self.event("Telos","I still intend to "+item["description"]+".",
                          PhenomenalMode.INTENTION,refs,
                          attribution=SubjectiveSourceKind.SELF_OBSERVED,digest=digest)

    def owned_events(self, digest=None):
        digest=digest or self.store.digest()
        result=[]
        for item in self.store.open_commitments():
            event=self.commitment_event(item,digest)
            if event is not None:
                result.append((item["id"],event))
        return result

    def admit_private(self, key, organ, text, refs=(), *, mode=PhenomenalMode.INTERNAL_THOUGHT,
                      attribution=SubjectiveSourceKind.SELF_OBSERVED):
        line=first_person_line(text)
        if line.startswith("I cannot make sense of"):
            raise PermissionError("Private experience is not subject-safe")
        event=self.event(organ,line,mode,refs,attribution=attribution)
        with self.store.transaction() as db:
            return self.record(db,key,(event,),phase="private_experience")

    def communication(self, memory_id):
        memory=self.store.get_memory(memory_id)
        if (not memory or not memory["active"]
                or memory["evidence_class"] not in ("external_statement","lived_runtime_memory")
                or not memory["source"].startswith("local-conversation:")):
            raise PermissionError("Actual received conversation required")
        event=self.event("Sensus",memory["text"],PhenomenalMode.PERCEPT,(memory_id,),
                         attribution=SubjectiveSourceKind.TOLD,external=True)
        with self.store.transaction() as db:
            return self.record(db,"communication:"+memory_id,(event,),phase="communication")

    def expression_frame(self, frame):
        """Use the same owned first-person history in actual local expression."""
        lines=SubjectRendererCapability.read(frame)
        digest=self.store.digest()
        events=[]
        history=self.verify_history()
        recent=[(entry,item) for entry in history[-24:] for item in entry["content"]
                if entry["phase"] in ("decision","private_thought") and item["organ"]=="Noesis"][-4:]
        for entry,item in recent:
            line="I recall having thought: "+item["text"]
            if first_person_line(line)==line:
                events.append(self.event("Mnemosyne",line,PhenomenalMode.RECOLLECTION,
                                         (entry["key"],),attribution=SubjectiveSourceKind.SELF_OBSERVED,digest=digest))
        for line in lines[:64-len(events)]:
            owned_line=first_person_line(line)
            events.append(self.event("Expression",owned_line,PhenomenalMode.INTERNAL_THOUGHT,digest=digest))
        subject_frame=self.frame(events)
        with self.store.transaction() as db:
            self.record(db,new_id("expression-context"),events,phase="expression_context")
        return subject_frame

    def verify_history(self):
        """Read-only verification of the single ordered subject history."""
        with closing(self.store.connect()) as db:
            rows=db.execute("SELECT value FROM meta WHERE key LIKE ?",(RECORD+"%",)).fetchall()
            head=json.loads(_read(db,HEAD) or '{"sequence":0,"sha256":null}')
        entries=sorted((json.loads(row["value"]) for row in rows),key=lambda x:x["sequence"])
        previous=None
        for sequence,entry in enumerate(entries,1):
            payload={k:v for k,v in entry.items() if k!="sha256"}
            if (entry["subject"]!="pretorius" or entry["sequence"]!=sequence
                    or entry["previous_sha256"]!=previous or entry["sha256"]!=_digest(payload)):
                raise PermissionError("Broken first-person history continuity")
            for item in entry["content"]:
                if not _FIRST.match(item["text"]) or first_person_line(item["text"])!=item["text"]:
                    raise PermissionError("Non-subject content in history")
            previous=entry["sha256"]
        if head!={"sequence":len(entries),"sha256":previous}:
            raise PermissionError("First-person history head mismatch")
        return entries

    def capture(self, observation, narrative, offers, interpretation_cues, imaginative_cues, affective_lines=()):
        """Conscious working experience before deliberation, not after rendering."""
        if (not observation["active"] or observation["external"]
                or observation["evidence_class"]!="lived_runtime_memory"
                or not observation["source"].startswith("virtual-world:small-tower:")
                or any(line not in observation["text"] for line in narrative)):
            raise PermissionError("Ipseity requires the admitted present perception")
        state_digest=self.store.digest()
        events=[]
        def add(organ,text,mode,refs=(),attribution=SubjectiveSourceKind.UNKNOWN,external=False):
            # A malformed optional projection is withheld rather than made into
            # an invented subjective event. Source-bound perception is strict.
            events.append(self.event(organ,text,mode,refs,attribution=attribution,
                                     external=external,digest=state_digest))
        for line in narrative:
            add("Sensus",line,PhenomenalMode.PERCEPT,(observation["id"],),
                SubjectiveSourceKind.LIVED)
        for offer in offers:
            add("Corpus",offer["text"],PhenomenalMode.EXPECTATION,(observation["id"],))
        for key,value in self.brain._felt_state().items():
            line=self.brain._felt_subject_text(key,value)
            if line:
                add("Corpus" if key=="fatigue" else "Affectus",line,
                    PhenomenalMode.BODILY_SENSATION if key=="fatigue" else PhenomenalMode.FEELING,
                    ("need:"+key,))
        for line in affective_lines:
            add("Affectus",line,PhenomenalMode.FEELING,(observation["id"],))
        owned_events=self.owned_events(state_digest)
        owned={rid:event[1].subject_text for rid,event in owned_events}
        with self.cognitive_access(owned):
            _, ranked=self.brain._ranked_memory_sets(8,query=" ".join(narrative),audit=False)
        for score,memory in ranked:
            item=self.brain._view_item(score,memory)
            line=first_person_line(item.first_person)
            if line.startswith("I cannot make sense of"):
                continue
            organ=("Phantasmagorium" if memory["evidence_class"]=="dreamed_not_lived" else
                   "Expression" if memory["kind"]=="confirmed_written_utterance" else "Mnemosyne")
            attribution=(SubjectiveSourceKind.DREAMED if organ=="Phantasmagorium" else
                         SubjectiveSourceKind.SELF_OBSERVED if organ=="Expression" else SubjectiveSourceKind.UNKNOWN)
            add(organ,line,PhenomenalMode.RECOLLECTION,(memory["id"],),attribution,bool(memory["external"]))
        for thought in self.store.thoughts(3):
            if thought["text"].startswith(("I ","My ")):
                line=first_person_line(thought["text"])
                if not line.startswith("I cannot make sense of"):
                    add("Noesis",line,PhenomenalMode.INTERNAL_THOUGHT,(thought["id"],),
                        SubjectiveSourceKind.SELF_OBSERVED)
        for cue in interpretation_cues:
            line="I associate this impression with "+cue.rstrip(".")+"."
            if first_person_line(line)==line:
                add("Conclave",line,PhenomenalMode.BELIEF,(observation["id"],),SubjectiveSourceKind.INFERRED)
        for motif in imaginative_cues:
            line="I imagine "+motif.rstrip(".")+", without taking it for something I witnessed."
            if first_person_line(line)==line:
                add("Phantasmagorium",line,PhenomenalMode.INTERNAL_THOUGHT,(observation["id"],),SubjectiveSourceKind.IMAGINED)
        events.extend(event for _,event in owned_events)
        frame=self.frame(events)
        with self.store.transaction() as db:
            entry=self.record(db,new_id("opportunity"),events,phase="deliberation")
        return frame,owned,entry

    @contextmanager
    def cognitive_access(self,owned):
        """Noesis consumes first-person owned commitments, not raw SQL goals."""
        previous=getattr(self.brain,"_ipseity_owned_commitments",None)
        self.brain._ipseity_owned_commitments=dict(owned)
        try:
            yield
        finally:
            self.brain._ipseity_owned_commitments=previous
