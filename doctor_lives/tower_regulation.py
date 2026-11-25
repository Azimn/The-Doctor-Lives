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
        add("rest", .14 if severe else .09)
        add("sleep", .20 if severe else .09)
        if not keys.intersection(("rest", "sleep")):
            add(first_step(graph, room, "bedchamber"), .20 if severe else .09)
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
