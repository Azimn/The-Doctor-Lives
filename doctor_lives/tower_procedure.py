"""Source-authenticated contextual procedural sequence memory.

Preserves the original Article 8 minimum-practice and bounded preference
principle. Repeated successful adjacent steps in the same perceived room
form a revisable preference, not a script, a motor grant, or a claim of
material skill gain. The original source still owns physical competence.
"""
from contextlib import closing
import json
from .home_habit_trace import MIN_PRACTICE
from .tower_development import _room

CAP = .025
VERSION = "tower-contextual-procedure-v1"


def appraise(episodes, room, feasible):
    """Episodes are chronological verified action outcomes, including failures."""
    scores = dict.fromkeys(feasible,0.)
    ids = {a: [] for a in feasible}
    if not episodes or not episodes[-1]["success"] or episodes[-1]["room"] != room:
        return scores, ids
    cue = episodes[-1]["action"]
    seen = set()
    histories = {a: [] for a in feasible}
    for first, second in zip(episodes, episodes[1:]):
        if (not first["success"] or first["action"] != cue
                or first["room"] != room or second["room"] != room
                or second["action"] not in feasible
                or second["source"] in seen):
            continue
        seen.add(second["source"])
        histories[second["action"]].append((first,second))
    for action, history in histories.items():
        recent = history[-4:]
        wins = [pair for pair in recent if pair[1]["success"]]
        losses = len(recent)-len(wins)
        if len(wins) >= MIN_PRACTICE and len(wins)>losses and recent[-1][1]["success"]:
            scores[action] = CAP * (len(wins)-losses)/len(recent)
            ids[action] = list(dict.fromkeys(m["memory_id"] for pair in recent for m in pair))
    return scores,ids


def verified_sequences(brain, provider, observation, feasible):
    from .small_tower import SmallTowerSource
    if type(provider) is not SmallTowerSource:
        raise PermissionError("Original Tower required")
    store = brain.store
    current = provider.snapshot()
    receipt = provider._observation(current)
    prefix = "virtual-world:small-tower:" + receipt.world_epoch + ":"
    if (not observation["active"] or observation["external"]
            or observation["evidence_class"] != "lived_runtime_memory"
            or observation["source"] != prefix+"observation:"+receipt.event_id
            or observation["text"] != receipt.first_person):
        raise PermissionError("Procedural appraisal needs current perception")
    events = [r for r in current["events"] if r["kind"] in ("completed","action_failed")
              and r.get("policyRef")][-64:]
    episodes=[]
    for event in events:
        pid=event["policyRef"]
        outcome_raw=store.meta("telos:tower-outcome:"+pid)
        if not outcome_raw:
            # Do not join across missing or pre-integration history.
            episodes=[]
            continue
        outcome=json.loads(outcome_raw)
        with closing(store.connect()) as db:
            policy=db.execute("SELECT selected_action,state_pressure_json FROM policy_decisions "
                              "WHERE id=? AND trigger='noesis_world_affordance'",(pid,)).fetchone()
            commitment=db.execute("SELECT status,outcome,source FROM commitments WHERE id=?",
                                  (outcome["commitment_id"],)).fetchone()
        memory=store.get_memory(outcome["source_memory_id"])
        if not memory or not memory["active"]:
            episodes=[]
            continue
        r=provider.event_receipt(event)
        expected=prefix+r.kind+":"+r.event_id
        success=event["kind"]=="completed"
        status="kept" if success else "broken"
        if (not policy or not commitment or commitment["status"]!=status
                or commitment["source"]!="telos:native:tower:"+pid
                or outcome["origin_policy_id"]!=pid or outcome["status"]!=status
                or memory["source"]!=expected or memory["text"]!=r.first_person
                or memory["text"]!=commitment["outcome"] or memory["external"]
                or memory["evidence_class"]!="lived_runtime_memory"
                or memory["source_event_id"]!=outcome["source_event_id"]):
            raise PermissionError("Unverified procedural consequence")
        action=policy["selected_action"]
        if action.startswith("move_"):
            # A journey is a genuine boundary, not a household procedure.
            episodes.append({"action":action,"room":None,"success":success,
                             "memory_id":memory["id"],"source":expected})
            continue
        if action!=event["operation"]:
            raise PermissionError("Procedural action differs from physical outcome")
        origin=json.loads(policy["state_pressure_json"])
        perceived=store.get_memory(origin["observation_memory_id"])
        if (not perceived or not perceived["active"] or perceived["external"]
                or perceived["evidence_class"]!="lived_runtime_memory"
                or not perceived["source"].startswith(prefix+"observation:")):
            episodes=[]
            continue
        episodes.append({"action":action,"room":_room(perceived["text"]),
                         "success":success,"memory_id":memory["id"],"source":expected})
    return appraise(episodes,_room(observation["text"]),feasible)
