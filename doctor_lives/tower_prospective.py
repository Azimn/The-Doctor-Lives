"""Prospective intentions on the same original Noesis/Telos/BrainStore.

Goals originate from a selected journey and a remembered, previously
completed activity in its destination. The known spatial graph is reconstructed
from admitted perceptions, not the hidden world map. Immediate affordances
remain independently available and compete with bounded goal pressure.
"""
from collections import deque
from contextlib import closing
import json
from .lab_telos import SOURCE_PREFIX

PREFIX = SOURCE_PREFIX + "tower-prospective:"
ROOMS = {"bedchamber": "bedchamber", "library": "library",
         "kitchen and hearth": "kitchen", "laboratory": "laboratory",
         "garden path": "garden"}
ACTIONS = frozenset(("read", "work", "study", "inspect", "diary", "tea",
                     "cook", "eat", "rest", "sleep", "tend", "prepare",
                     "gather_fuel", "draw_water", "preserve"))
MAX_ACTIVE = 3
PRESSURE = .065


def _room(text):
    for label, key in ROOMS.items():
        if text.startswith("I am in my " + label + "."):
            return key
    return None


def _edges(text):
    return {key for label, key in ROOMS.items()
            if "I can make my way to my " + label + "." in text}


def first_step(graph, start, target):
    if start == target or not start or not target:
        return None
    queue = deque([(start, None)])
    seen = {start}
    while queue:
        node, step = queue.popleft()
        for nxt in sorted(graph.get(node, ())):
            if nxt in seen:
                continue
            first = step or nxt
            if nxt == target:
                return "move_" + first
            seen.add(nxt)
            queue.append((nxt, first))
    return None


def _active(store):
    with closing(store.connect()) as db:
        rows = db.execute(
            "SELECT * FROM commitments WHERE source LIKE ? AND status='open' ORDER BY created_tick,id",
            (PREFIX + "%",)).fetchall()
    result = []
    for row in rows:
        raw = store.meta("telos:tower-prospective:" + row["id"])
        if raw is None:
            raise PermissionError("Prospective commitment has no sealed origin")
        goal = json.loads(raw)
        if (goal["id"] != row["id"] or row["source"] != PREFIX + goal["origin_policy_id"]
                or row["description"] != goal["description"]
                or row["outcome"] is not None or goal["target"] not in ACTIONS
                or goal["room"] not in ROOMS.values()):
            raise PermissionError("Prospective commitment origin mismatch")
        result.append(goal)
    if len(result) > MAX_ACTIVE:
        raise PermissionError("Prospective commitment budget exceeded")
    return result


def deferred_need(action, narrative, latest_store, last_garden, room, feasible):
    """Keep ownership but suspend pressure for a currently irrelevant need."""
    if action in ("eat", "cook") and not any(cue in narrative for cue in
            ("I am painfully hungry.", "I could do with something to eat.")):
        return "appetite_satisfied"
    cues = {"gather_fuel":"fuel is running low", "draw_water":"water is running low",
            "tend":"edible provisions are running low"}
    if action in cues:
        if latest_store and cues[action] not in latest_store:
            return "last_observed_supply_not_low"
        if (room != "garden" and last_garden and action not in last_garden["offers"]
                and last_garden["elapsed"] < 100):
            return "recently_observed_unavailable"
    return None


def unavailable_activity(action, destination, room, feasible, known):
    """A remembered intention need not cause repeated travel to a blocked task."""
    if destination == room:
        return None if action in feasible else "currently_unavailable"
    prior = known.get(destination)
    if prior and action == "tea" and action not in prior["offers"]:
        perception = prior.get("observed_text", "")
        if ("I can see Stores shelf." in perception
                and "I can see Kettle." in perception
                and "I can see that my tea is running low." in perception
                and not prior.get("replenishment_memory_ids")):
            # A finite missing ingredient is not restored by elapsed time.
            # A relevant witnessed replenishment can justify a fresh check,
            # but does not itself establish that tea is now available.
            return "awaiting_observed_replenishment"
    if prior and action not in prior["offers"] and prior["elapsed"] < 100:
        return "recently_observed_unavailable"
    return None


def last_room_offers(store, prefix):
    """Read original choice receipts and their associated admitted observations."""
    known = {}
    with closing(store.connect()) as db:
        elapsed = 0
        for row in db.execute("SELECT key,value FROM meta WHERE key LIKE 'small-tower:choice:%' OR key LIKE 'small-tower:receipt:%' ORDER BY rowid DESC"):
            payload = json.loads(row["value"])
            if row["key"].startswith("small-tower:receipt:"):
                elapsed += payload["elapsed"]
                continue
            memory = db.execute("SELECT id,text,source,active,external,evidence_class,created_tick FROM memories WHERE id=?", (payload["observation_id"],)).fetchone()
            if (not memory or not memory["active"] or memory["external"]
                    or memory["evidence_class"] != "lived_runtime_memory"
                    or not memory["source"].startswith(prefix + "observation:")):
                continue
            room = _room(memory["text"])
            if room and room not in known:
                known[room] = {"memory_id":memory["id"],"offers":payload["offers"],
                               "elapsed":elapsed,"observed_text":memory["text"]}
                if room == "kitchen":
                    # Relevant actions are actual admitted physical outcomes,
                    # not hidden inventory or a timer. These may warrant
                    # rechecking a previously unavailable tea offer.
                    relevant = ("I traded provisions with the caller on terms I chose.",
                                "I opened a package delivered through the post.",
                                "I gathered fallen wood for the hearth.",
                                "I drew a measured supply of water.")
                    known[room]["replenishment_memory_ids"] = [r["id"] for r in db.execute(
                        "SELECT id,text FROM memories WHERE active=1 AND external=0 "
                        "AND evidence_class='lived_runtime_memory' AND source LIKE ? "
                        "AND created_tick>? ORDER BY created_tick,id",
                        (prefix+"action:%",memory["created_tick"])) if r["text"] in relevant]
            if len(known) == len(ROOMS):
                break
    return known


def assess(brain, provider, observation, offers, abstract, affordance_map, *, owned_commitments=None):
    from .small_tower import SmallTowerSource
    if type(provider) is not SmallTowerSource:
        raise PermissionError("Original Tower required")
    current = provider.observe()
    store = brain.store
    prefix = "virtual-world:small-tower:" + current.world_epoch + ":"
    if (not observation["active"] or observation["external"]
            or observation["evidence_class"] != "lived_runtime_memory"
            or observation["source"] != prefix + "observation:" + current.event_id
            or observation["text"] != current.first_person):
        raise PermissionError("Prospective appraisal needs current admitted observation")
    room = _room(observation["text"])
    graph = {}
    with closing(store.connect()) as db:
        memories = db.execute(
            "SELECT text FROM memories WHERE active=1 AND external=0 "
            "AND evidence_class='lived_runtime_memory' AND source LIKE ? "
            "ORDER BY created_tick DESC LIMIT 128", (prefix + "observation:%",)).fetchall()
        past = db.execute(
            "SELECT p.id,p.selected_action,p.state_pressure_json FROM policy_decisions p "
            "JOIN commitments c ON c.source='telos:native:tower:'||p.id "
            "WHERE c.status='kept' AND p.trigger='noesis_world_affordance' "
            "ORDER BY c.updated_tick DESC LIMIT 32").fetchall()
    for text in [observation["text"]] + [m["text"] for m in memories]:
        loc = _room(text)
        if loc:
            graph.setdefault(loc, set()).update(_edges(text))
    keys = {o["key"] for o in offers}
    graph[room] = {k.removeprefix("move_") for k in keys if k.startswith("move_")}
    active = _active(store)
    scores = dict.fromkeys(keys, 0.)
    links = {k: [] for k in keys}
    candidates = {}
    deferred = {}
    from .tower_regulation import remembered_supply
    supplies = remembered_supply(store, observation, offers)
    latest_store = next((t for t in [observation["text"]] + [m["text"] for m in memories]
                         if "I can see Stores shelf." in t), None)
    known = last_room_offers(store, prefix)
    def defer(action, destination):
        return (deferred_need(action, observation["text"], latest_store,
                              supplies.get("last_garden"), room, keys)
                or unavailable_activity(action, destination, room, keys, known))
    for goal in active:
        if goal["epoch"] != current.world_epoch:
            raise PermissionError("Foreign prospective commitment")
        if owned_commitments is not None and owned_commitments.get(goal["id"]) != "I still intend to "+goal["description"]+".":
            continue
        reason = defer(goal["target"], goal["room"])
        if reason:
            deferred[goal["id"]] = reason
            continue
        key = goal["target"] if goal["room"] == room else first_step(graph, room, goal["room"])
        if key in keys:
            scores[key] = min(PRESSURE, scores[key] + PRESSURE * goal["importance"])
            links[key].append(goal["id"])
    if len(active) < MAX_ACTIVE:
        # Independently check the source history once before using any old
        # task as a prospective ingredient. A protected database row alone
        # does not authenticate a historical physical accomplishment.
        history = provider.snapshot()
        if provider._observation(history) != current:
            raise PermissionError("Tower changed during prospective appraisal")
        verified_events = {}
        for event in history["events"]:
            if event["kind"] == "completed" and event.get("policyRef"):
                receipt = provider.event_receipt(event)
                verified_events[event["policyRef"]] = (event, prefix + "action:" + receipt.event_id, receipt.first_person)
        seen = {(g["room"], g["target"]) for g in active}
        # A fresh goal is possible only on an actual current journey to a
        # location where a prior self-selected task physically succeeded.
        for row in past:
            action = row["selected_action"]
            if action not in ACTIONS:
                continue
            evidence = json.loads(row["state_pressure_json"])
            prior = store.get_memory(evidence["observation_memory_id"])
            if (not prior or not prior["active"] or prior["external"]
                    or prior["evidence_class"] != "lived_runtime_memory"
                    or not prior["source"].startswith(prefix + "observation:")):
                continue
            dest = _room(prior["text"])
            move = "move_" + dest if dest else None
            if move not in keys or (dest, action) in seen or dest == room or defer(action, dest):
                continue
            raw = store.meta("telos:tower-outcome:" + row["id"])
            if not raw:
                raise PermissionError("Past task lacks authenticated outcome")
            outcome = json.loads(raw)
            memory = store.get_memory(outcome["source_memory_id"])
            if (not memory or not memory["active"] or memory["external"]
                    or memory["evidence_class"] != "lived_runtime_memory"
                    or not memory["source"].startswith(prefix + "action:")
                    or memory.get("source_event_id") != outcome["source_event_id"]
                    or outcome["status"] != "kept"
                    or outcome["origin_policy_id"] != row["id"]):
                continue
            proof = verified_events.get(row["id"])
            if (not proof or proof[0]["operation"] != action
                    or proof[1] != memory["source"] or proof[2] != memory["text"]):
                raise PermissionError("Prospective source lacks original physical completion")
            # Use the original abstract tendency as a prospective appraisal.
            # No new target is fabricated and a journey is never forced.
            strength = float(abstract["action_scores"][affordance_map[action]])
            if strength <= 0.0:
                continue
            candidate = {"target": action, "room": dest, "epoch": current.world_epoch,
                         "prior_policy_id": row["id"], "prior_memory_id": memory["id"],
                         "description": evidence["offer_appraisals"][action]["cue"].split(" ", 1)[1].rstrip("."),
                         "importance": min(.85, .45 + strength),
                         "appraisal": strength}
            if move not in candidates or candidate["appraisal"] > candidates[move]["appraisal"]:
                candidates[move] = candidate
    return {"scores": scores, "links": links, "candidates": candidates,
            "room": room, "active_ids": [g["id"] for g in active],
            "deferred_owned_goals": deferred, "recent_room_offers": known}


def reserve(store, db, request, *, subject=None):
    pid = request["policyRef"]
    if not pid:
        return
    row = db.execute("SELECT tick,selected_action,state_pressure_json FROM policy_decisions WHERE id=?",
                     (pid,)).fetchone()
    audit = json.loads(row["state_pressure_json"]).get("prospective_goals")
    if not audit:
        return
    selected = request["choice"]
    if selected != row["selected_action"]:
        raise PermissionError("Prospective origin differs from Noesis decision")
    candidate = audit["candidates"].get(selected)
    if candidate is not None and not audit["links"].get(selected):
        rid = "telos_prospective_" + pid
        goal = dict(candidate, id=rid, origin_policy_id=pid)
        # Use the exact original offer-derived task text, not external goal prose.
        goal["description"] = "return to " + candidate["room"] + " to " + candidate["target"].replace("_", " ")
        raw = json.dumps(goal, sort_keys=True)
        key = "telos:tower-prospective:" + rid
        count = db.execute("SELECT COUNT(*) FROM commitments WHERE source LIKE ? AND status='open'",
                           (PREFIX + "%",)).fetchone()[0]
        if count >= MAX_ACTIVE:
            raise PermissionError("Prospective commitment budget exceeded")
        db.execute("INSERT INTO commitments "
                   "(id,created_tick,updated_tick,description,status,due_tick,importance,actor,source,outcome) "
                   "VALUES(?,?,?,?,'open',NULL,?,NULL,?,NULL)",
                   (rid, row["tick"], store.tick, goal["description"], goal["importance"], PREFIX + pid))
        store.set_meta(key, raw, db)
        from .store import new_id
        thought_id=new_id("thought")
        db.execute("INSERT INTO thoughts (id,tick,text,trigger,generated_by,source_record_ids_json,action_tendencies_json) "
                   "VALUES(?,?,?,?,?,?,?)",
                   (thought_id,store.tick,"I intend to "+goal["description"]+".",
                    "ipseity_prospective_intention","ipseity_prospective:"+pid,
                    json.dumps([goal["prior_memory_id"]]),"{}"))
        if subject is not None:
            from .phenomenology import PhenomenalMode, SubjectiveSourceKind
            owned=subject.event("Telos","I intend to "+goal["description"]+".",PhenomenalMode.INTENTION,
                                (rid,pid,thought_id,goal["prior_memory_id"]),
                                attribution=SubjectiveSourceKind.SELF_OBSERVED)
            subject.record(db,"prospective:"+rid,(owned,),phase="intention")
    # No timeout or unrelated action can claim fulfillment. The protected
    # prospective commitment remains open through interruptions and restart.


def complete(store, db, policy_id, outcome):
    """Called inside the physical intention completion transaction."""
    if outcome["status"] != "kept":
        return
    row = db.execute("SELECT selected_action,state_pressure_json FROM policy_decisions WHERE id=?",
                     (policy_id,)).fetchone()
    action = row["selected_action"]
    audit = json.loads(row["state_pressure_json"]).get("prospective_goals")
    if not audit or action.startswith("move_"):
        return
    memory = db.execute("SELECT text FROM memories WHERE id=?",
                        (outcome["source_memory_id"],)).fetchone()
    for rid in audit["links"].get(action, []):
        saved = db.execute("SELECT value FROM meta WHERE key=?",
                           ("telos:tower-prospective:" + rid,)).fetchone()
        if saved is None:
            raise PermissionError("Missing prospective goal")
        goal = json.loads(saved["value"])
        if goal["target"] != action or goal["room"] != audit["room"]:
            continue
        current = db.execute("SELECT status,source FROM commitments WHERE id=?", (rid,)).fetchone()
        if current is None or current["source"] != PREFIX + goal["origin_policy_id"]:
            raise PermissionError("Unverified prospective goal")
        if current["status"] != "open":
            raise PermissionError("Prospective goal already closed")
        db.execute("UPDATE commitments SET status='kept',updated_tick=?,outcome=? WHERE id=?",
                   (store.tick, memory["text"], rid))
        store.set_meta("telos:tower-prospective-completion:" + rid,
                       json.dumps(dict(outcome, prospective_id=rid), sort_keys=True), db)
