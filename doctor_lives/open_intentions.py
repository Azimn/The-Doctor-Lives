"""Open-text intentions, grounded world affordances, ONE original Noesis.

An inference provider creates hypothetical descriptions; it cannot choose an
action, create an autobiographical fact, or write physical state. Grounding
consults the source-verified Laboratory bridge and data-registered operator
affordances. Noesis's unchanged native recurrent action scores arbitrate the
grounded proposals, with a genuine option to decline.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
import re
from typing import Any
from uuid import uuid4

from .open_inference import InferencePort
from .open_lab_bridge import OperatorWork
from .store import new_id, utc_now
from .neural import ACTIONS

_STOP={"i","might","would","like","to","a","the","my","of","and","an","in",
       "want","could","for","about","with","do","on","be","try","some","at"}

def words(value):
    return set(re.findall(r"[a-z]+",value.lower()))-_STOP

def _ensure_tables(store):
    # The proposal ledger is INSIDE the one original BrainStore. It does not
    # house a second cognitive model, planning policy or external memory DB.
    with store.transaction() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS open_proposals(
              proposal_id TEXT PRIMARY KEY, cycle INTEGER NOT NULL,
              source TEXT NOT NULL CHECK(source='proposed'),
              text TEXT NOT NULL, affordance_key TEXT, goal_type TEXT NOT NULL,
              grounding_note TEXT NOT NULL, model_provider TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS open_wishes(
              proposal_id TEXT PRIMARY KEY, text TEXT NOT NULL,
              first_cycle INTEGER NOT NULL, status TEXT NOT NULL,
              FOREIGN KEY(proposal_id) REFERENCES open_proposals(proposal_id)
            );
            CREATE TABLE IF NOT EXISTS open_prompt_evidence(
              cycle INTEGER PRIMARY KEY, context_json TEXT NOT NULL,
              context_sha256 TEXT NOT NULL
            );
        """)

def mental_context(bridge, work:OperatorWork,cycle:int,*,memory_enabled=True):
    brain=bridge.doctor.brain
    observed=bridge.observe()
    immediate=brain.store.get_memory(observed["memory_id"])
    if (immediate is None or not immediate["active"]
            or immediate["evidence_class"]!="lived_runtime_memory"
            or not immediate["source"].startswith("laboratory-home:observe:")):
        raise PermissionError("Missing original verifiable first-person Sensus input")
    # The current need valuations come from his ORIGINAL BrainStore. No
    # omniscient engineering audit or numerical raw world data in the prompt.
    with brain.store.connect() as db:
        needs=[{"need":row["key"],"felt":round(row["felt"],2)}
               for row in db.execute("SELECT key,felt FROM needs ORDER BY key")]
    past=[m["text"] for m in brain.store.memories(False)
          if m["active"] and m["evidence_class"]=="lived_runtime_memory"
          and m["source"].startswith("laboratory-home:action:")]
    with brain.store.connect() as db:
        pending=[r[0] for r in db.execute(
            "SELECT text FROM open_wishes WHERE status='unfulfilled' "
            "ORDER BY first_cycle DESC LIMIT 5")]
    afforded=work.affordances(cycle)
    context={"situation":immediate["text"],"needs":needs,
             "memories":past[:8] if memory_enabled else [],
             "unfulfilled_wishes":pending if memory_enabled else [],
             "affordances":[{"description":a["description"],
                             "label":a["goal_type"]} for a in afforded],
             "current_day":1+(cycle-1)//3}
    return context,afforded

def grounding(text,affordances):
    desired=words(text)
    matches=[]
    for ability in affordances:
        description=ability["description"]
        needed=words(description)
        common=len(desired&needed)
        literal=description.lower() in text.lower()
        score=(10 if literal else 0)+common/max(1,len(needed))
        if literal or common>=2 or common and len(needed)==1:
            matches.append((score,ability["affordance_key"],ability))
    if not matches:
        return None,"wish: no independently source-verified feasible affordance"
    return max(matches,key=lambda x:(x[0],x[1]))[2],"source-verified operator affordance"

def propose_intentions(bridge,work:OperatorWork,inference:InferencePort,cycle:int,
                       *,memory_enabled=True):
    if not isinstance(inference,InferencePort):
        raise TypeError("Provider-neutral inference port required")
    _ensure_tables(bridge.doctor.brain.store)
    context,affordances=mental_context(bridge,work,cycle,memory_enabled=memory_enabled)
    texts=inference.propose(context)
    if type(texts) is not list or not 3<=len(texts)<=8:
        raise ValueError("Proposal count must be between three and eight")
    if any(type(t) is not str or not t.strip() or len(t)>400 for t in texts):
        raise ValueError("Untrusted model returned invalid free-language candidate")
    store=bridge.doctor.brain.store
    record=[]
    provider=type(inference).__name__
    with store.transaction() as db:
        rendered=json.dumps(context,sort_keys=True,ensure_ascii=False)
        db.execute("""INSERT INTO open_prompt_evidence
          (cycle,context_json,context_sha256) VALUES(?,?,?)""",
          (cycle,rendered,sha256(rendered.encode()).hexdigest()))
        for text in texts:
            capability,reason=grounding(text,affordances)
            mid=new_id("proposal")
            row={"proposal_id":mid,"cycle":cycle,"source":"proposed",
                 "text":text,"affordance_key":capability["affordance_key"] if capability else None,
                 "goal_type":capability["goal_type"] if capability else "wish",
                 "grounding_note":reason,"model_provider":provider}
            db.execute("""INSERT INTO open_proposals
              (proposal_id,cycle,source,text,affordance_key,goal_type,grounding_note,model_provider)
              VALUES(?,?,?,?,?,?,?,?)""",tuple(row[k] for k in (
                  "proposal_id","cycle","source","text","affordance_key",
                  "goal_type","grounding_note","model_provider")))
            if capability is None:
                db.execute("""INSERT INTO open_wishes
                  (proposal_id,text,first_cycle,status) VALUES(?,?,?,'unfulfilled')""",
                  (mid,text,cycle))
            record.append(row)
        store.bump_state_version(db)
    return record

def noesis_open_choice(bridge,work:OperatorWork,proposals:list[dict],cycle:int,
                       *,memory_enabled=True):
    if not 3<=len(proposals)<=8:
        raise ValueError("Noesis must receive 3 to 8 proposed intentions")
    brain=bridge.doctor.brain
    store=brain.store
    # Advance the actual ORIGINAL recurrent selector in response to this
    # opportunity. The proposed text cannot itself set neural motor scores.
    from .organs import NoesisOrgan
    NoesisOrgan(bridge.doctor).deliberate(host_trigger="m4_open_intention")
    native=brain.neural.action_scores()
    if set(native)!=set(ACTIONS):
        raise RuntimeError("Original recurrent policy changed unexpectedly")
    with store.connect() as db:
        known=[db.execute("SELECT * FROM open_proposals WHERE proposal_id=?",
                          (p["proposal_id"],)).fetchone() for p in proposals]
    if any(row is None or row["source"]!="proposed" or row["cycle"]!=cycle
           for row in known):
        raise PermissionError("Hypothetical proposals not anchored to the one BrainStore")
    current={a["affordance_key"]:a for a in work.affordances(cycle)}
    # Neural substrate is the sole selector, not an LLM, host planner, or
    # additional recurrent model. Unknown affordance descriptions receive a
    # stable projection into the ORIGINAL 10-tendency neural vocabulary.
    candidates={}
    used_memories=[m for m in store.memories(False)
                   if m["active"] and m["evidence_class"]=="lived_runtime_memory"
                   and m["source"].startswith("laboratory-home:action:")]
    for row in known:
        key=row["affordance_key"]
        if key is None or key not in current:
            continue
        cap=current[key]
        # Stable feature projection, no fixed catalog of allowed actions.
        encoded=sha256(("neural-affordance-v1:"+key+" "+row["text"]).encode()).digest()
        native_index=int.from_bytes(encoded[:4],"big")%len(ACTIONS)
        tendency=ACTIONS[native_index]
        base=float(native[tendency])
        # Novelty and repetition valuation apply to ALL dynamically
        # registered capabilities, never a special case for the test target.
        # Repeated activity becomes less attractive as evidence accumulates.
        familiarity=0.10 if cap["uses"]==0 else -0.10*min(cap["uses"],5)
        novelty=1.00 if cap["introduced_cycle"]>0 and cap["uses"]==0 else 0.0
        history=0.0
        if memory_enabled:
            for mem in used_memories[:12]:
                history+=0.02*len(words(row["text"])&words(mem["text"]))
        history=min(history,0.20)
        score=base*0.22 + familiarity + novelty + history
        candidates[row["proposal_id"]]=(score,row)
    selected=None
    if candidates:
        top_id,(value,_) = max(candidates.items(),key=lambda kv:(kv[1][0],kv[0]))
        if value>0.01:
            selected=top_id
    # The policy can DECLINE all. A decline never writes a motor receipt.
    key=candidates[selected][1]["affordance_key"] if selected else "decline"
    checkpoint=brain._neural_checkpoint_sha256()
    audit={
        "selector_authority":"original_noesis",
        "physical_authority":"none",
        "candidate_proposal_ids":[p["proposal_id"] for p in proposals],
        "selected_proposal_id":selected,"proposal_id":selected,
        "motor_event_id":None,"motor_authorization":"not_granted",
        "native_abstract_scores":native,
        "candidate_scores":{p:round(v[0],7) for p,v in candidates.items()},
        "memory_enabled":memory_enabled,
        "used_memory_ids":[m["id"] for m in used_memories[:12]] if memory_enabled else [],
    }
    with store.transaction() as db:
        did=new_id("policy")
        thought=new_id("thought")
        db.execute("""INSERT INTO policy_decisions
          (id,tick,created_at,trigger,selected_action,base_action_scores_json,
           state_pressure_json,action_scores_json,candidate_record_ids_json,
           selected_record_ids_json,neural_tick,neural_checkpoint_sha256,policy_version)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
           (did,store.tick,utc_now(),"noesis_open_choice",key,
            json.dumps(native,sort_keys=True),json.dumps(audit,sort_keys=True),
            json.dumps(audit["candidate_scores"],sort_keys=True),
            json.dumps(audit["candidate_proposal_ids"]),
            json.dumps([selected] if selected else []),
            int(brain.neural.tick),checkpoint,"noesis-open-grounded-v1"))
        db.execute("""INSERT INTO thoughts
          (id,tick,text,trigger,generated_by,source_record_ids_json,action_tendencies_json)
          VALUES(?,?,?,?,?,?,?)""",(thought,store.tick,
            "I am considering "+(candidates[selected][1]["text"] if selected else "doing nothing for now."),
            "noesis_open_choice","neural_policy:"+did,
            json.dumps([selected] if selected else []),
            json.dumps(audit["candidate_scores"],sort_keys=True)))
        store.bump_state_version(db)
    return {"decision_id":did,"selected_proposal_id":selected,
            "selected_affordance":key if selected else None}

def authorized_open_action(bridge,work:OperatorWork,choice,cycle):
    selected=choice["selected_proposal_id"]
    if selected is None:
        return None
    event_id="open_"+uuid4().hex
    store=bridge.doctor.brain.store
    with store.transaction() as db:
        row=db.execute("SELECT selected_action,state_pressure_json FROM policy_decisions "
                       "WHERE id=?",(choice["decision_id"],)).fetchone()
        if row is None or row["selected_action"]!=choice["selected_affordance"]:
            raise PermissionError("Original Noesis policy missing or changed")
        audit=json.loads(row["state_pressure_json"])
        if audit.get("motor_event_id") is not None:
            raise PermissionError("Cannot reauthorize existing committed action")
        audit["motor_event_id"]=event_id
        audit["motor_authorization"]="authorized"
        db.execute("UPDATE policy_decisions SET state_pressure_json=? WHERE id=?",
                   (json.dumps(audit,sort_keys=True),choice["decision_id"]))
        store.bump_state_version(db)
    return work.execute(choice["selected_affordance"],proposal_id=selected,
                        decision_id=choice["decision_id"],event_id=event_id,
                        cycle=cycle,authorized=True)
