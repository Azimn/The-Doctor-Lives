"""Bounded bodily and intellectual demand from actually perceived Tower cues.

This is a regulatory appraisal, never an action selector. Route knowledge
comes from the same individual's admitted current and historical perceptions,
not the simulator's private map or its unused decision engine.
"""
from contextlib import closing
from .tower_prospective import _room, _edges, first_step


def appraisal(narrative, offers, remembered):
    text = " ".join(narrative)
    room = _room(text)
    if room is None:
        raise PermissionError("Current subject-native room perception required")
    graph = {}
    for prior in remembered:
        loc = _room(prior)
        if loc:
            graph.setdefault(loc, set()).update(_edges(prior))
    keys = {offer["key"] for offer in offers}
    # Current physical offers, not remembered exits, authorize the first step.
    graph[room] = {key.removeprefix("move_") for key in keys if key.startswith("move_")}
    scores = {}

    def add(key, amount):
        if key in keys:
            scores[key] = max(scores.get(key, 0.0), amount)

    severe = "I feel worn out" in text
    tired = severe or "I am getting tired." in text
    if tired:
        # Both actions use the same abstract avoid tendency. Equal pressure
        # for a tired body lets the shorter, repeatedly successful rest
        # dominate restorative sleep. Distinguish their physical purposes
        # using the source's observed fatigue bands, not hidden energy.
        add("rest", .08 if severe else .045)
        add("sleep", .20 if severe else .16)
        if not keys.intersection(("rest", "sleep")):
            add(first_step(graph, room, "bedchamber"), .20 if severe else .16)
    # Consumption is not intrinsically rewarding when its need is absent.
    # Keep all legal actions available, but stop reinforcing wasteful meals.
    hungry = "I am painfully hungry." in text or "I could do with something to eat." in text
    if hungry:
        urgent = "I am painfully hungry." in text
        add("eat", .20 if urgent else .16)
        add("cook", .10 if urgent else .075)
        if not keys.intersection(("eat", "cook")):
            add(first_step(graph, room, "kitchen"), .20 if urgent else .14)
    else:
        for key in ("eat", "cook"):
            if key in keys:
                scores[key] = -.16
    if "I long for something to occupy my mind." in text:
        intellectual = keys.intersection(("read", "study", "inspect", "work"))
        if intellectual:
            for key in intellectual:
                add(key, .09)
        else:
            for target in ("library", "laboratory"):
                add(first_step(graph, room, target), .09)
    return scores


def verified_appraisal(store, observation, offers, narrative):
    if (not observation or not observation["active"] or observation["external"]
            or observation["evidence_class"] != "lived_runtime_memory"
            or not observation["source"].startswith("virtual-world:small-tower:")
            or ":observation:" not in observation["source"]
            or observation["text"] != " ".join(narrative)):
        raise PermissionError("Bodily regulation requires the exact admitted perception")
    prefix = observation["source"].rsplit(":observation:", 1)[0] + ":observation:"
    with closing(store.connect()) as db:
        rows = db.execute(
            "SELECT text FROM memories WHERE active=1 AND external=0 "
            "AND evidence_class='lived_runtime_memory' AND source LIKE ? "
            "AND created_tick<=? ORDER BY created_tick DESC LIMIT 128",
            (prefix + "%", observation["created_tick"])).fetchall()
    return appraisal(narrative, offers, [row["text"] for row in rows])


# A remembered shortage must remain actionable after leaving the stores.
# One actual completed relevant attempt triggers re-observation, not a claim
# that an unseen inventory quantity is now adequate.
SUPPLY_CUES = (
    ("fuel is running low", "gather_fuel", "I gathered fallen wood for the hearth.", .16),
    ("water is running low", "draw_water", "I drew a measured supply of water.", .16),
    ("edible provisions are running low", "tend", "I tended the patch beside the tower.", .18),
)


def supply_appraisal(remembered_store, completed_texts, feasible):
    scores = {}
    if not remembered_store or "I can see Stores shelf." not in remembered_store:
        return scores
    for cue, action, completed, pressure in SUPPLY_CUES:
        if cue in remembered_store and completed not in completed_texts and action in feasible:
            scores[action] = pressure
    return scores


def supply_route(remembered_store, completed_texts, feasible, last_garden_offers=None, elapsed=0):
    """Recheck a recently unavailable replenishment only at ordinary cadence.

    The shortage remains remembered; no attempt or absence proves adequacy.
    A fresh feasible offer immediately supersedes a prior unavailable offer.
    """
    if not remembered_store or "I can see Stores shelf." not in remembered_store:
        return {}
    if "move_garden" not in feasible:
        return {}
    pressure = 0.0
    for cue, action, completed, amount in SUPPLY_CUES:
        if cue not in remembered_store or completed in completed_texts:
            continue
        if (last_garden_offers is not None and action not in last_garden_offers
                and elapsed < 100):
            continue
        pressure = max(pressure, amount)
    return {"move_garden":pressure} if pressure else {}


def remembered_supply(store, observation, offers):
    """Use the latest same-epoch stores perception and later lived outcomes."""
    if (not observation or observation["external"] or not observation["active"]
            or observation["evidence_class"] != "lived_runtime_memory"
            or not observation["source"].startswith("virtual-world:small-tower:")
            or ":observation:" not in observation["source"]):
        raise PermissionError("Supply appraisal requires an admitted Tower perception")
    prefix = observation["source"].rsplit(":observation:", 1)[0] + ":"
    with closing(store.connect()) as db:
        remembered = db.execute(
            "SELECT id,text,created_tick FROM memories WHERE active=1 AND external=0 "
            "AND evidence_class='lived_runtime_memory' AND source LIKE ? "
            "AND created_tick<=? AND text LIKE '%I can see Stores shelf.%' "
            "ORDER BY created_tick DESC,id DESC LIMIT 1",
            (prefix + "observation:%", observation["created_tick"])).fetchone()
        if remembered is None:
            return {"source_memory_id":None,"completed_memory_ids":[],"scores":{}}
        outcomes = db.execute(
            "SELECT id,text FROM memories WHERE active=1 AND external=0 "
            "AND evidence_class='lived_runtime_memory' AND source LIKE ? "
            "AND created_tick>? AND created_tick<=?",
            (prefix + "action:%", remembered["created_tick"], observation["created_tick"])).fetchall()
        # Choice receipts bind the known legal offers to their admitted scene.
        # Only same-epoch authenticated garden observations are eligible.
        import json
        garden = None
        for row in db.execute("SELECT rowid,value FROM meta WHERE key LIKE 'small-tower:choice:%' ORDER BY rowid DESC"):
            choice = json.loads(row["value"])
            memory = db.execute("SELECT id,text,source,external,evidence_class,active FROM memories WHERE id=?", (choice["observation_id"],)).fetchone()
            if (memory and memory["active"] and not memory["external"]
                    and memory["evidence_class"] == "lived_runtime_memory"
                    and memory["source"].startswith(prefix + "observation:")
                    and _room(memory["text"]) == "garden"):
                elapsed = sum(json.loads(r["value"])["elapsed"] for r in db.execute(
                    "SELECT value FROM meta WHERE key LIKE 'small-tower:receipt:%' AND rowid>?", (row["rowid"],)))
                garden = {"memory_id":memory["id"], "offers":choice["offers"], "elapsed":elapsed}
                break
    completed = {row["text"] for row in outcomes}
    feasible = {offer["key"] for offer in offers}
    scores = supply_appraisal(remembered["text"], completed, feasible)
    scores.update(supply_route(remembered["text"], completed, feasible,
                               None if garden is None else set(garden["offers"]),
                               0 if garden is None else garden["elapsed"]))
    return {"source_memory_id":remembered["id"],
            "completed_memory_ids":[row["id"] for row in outcomes
                                    if row["text"] in {item[2] for item in SUPPLY_CUES}],
            "last_garden":garden, "scores":scores}
