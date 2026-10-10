"""Strong transparent nonneural, source-bounded baseline for issue #53.

This is a planner CONTROL, not a second Pretorius or a consciousness claim.
It gets the same room view and allowed observation/action interface. It does not
receive the full world state or Doctor Lives' private cognitive state.
"""
import argparse
import json
from pathlib import Path

from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.observation_receipts import ObservationPort
from research_integrations.living_lab import _verify_observation


def run(world_path: Path) -> dict:
    world = SpatialHabitat(world_path)
    port = ObservationPort(world)
    room = port.expose("room", "room:sanctum")
    observed = _verify_observation(port, room)["offered_payload"]
    beaker = observed["objects"]["beaker:001"]
    decisions = []
    if beaker["condition"] != "broken":
        decisions.append("abstain: no broken-glass goal is indicated")
    elif not beaker["collected"]:
        event = world.commit({"op": "collect", "object_id": "beaker:001"},
                             actor="pretorius_research",
                             expected_revision=world.verify()["revision"])
        decisions.append({"collect_event": event["event_hash"]})
    elif beaker["anchor_id"] == "bench:main/position:left":
        floor = port.expose("shelf", "floor:sanctum")
        area = _verify_observation(port, floor)["offered_payload"]
        is_empty = any(x["anchor_id"] == "floor:corner:nw" and x["occupant"] is None
                       for x in area["positions"])
        decisions.append({"inspected_floor": floor["receipt_hash"], "vacant": is_empty})
        if is_empty:
            event = world.commit({
                "op": "place", "object_id": "beaker:001", "anchor_id": "floor:corner:nw"
            }, actor="pretorius_research",
               expected_revision=world.verify()["revision"])
            decisions.append({"place_event": event["event_hash"]})
    else:
        decisions.append("already secured: no change")
    location = world.locate("beaker:001")
    return {"controller": "strong_simple_non_neural_no_subject_memory",
            "decisions": decisions, "world_verified": world.verify(),
            "task_completed": location["condition"] == "broken"
            and location["location"]["anchor_id"] == "floor:corner:nw"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--world", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(run(a.world), sort_keys=True))


if __name__ == "__main__":
    main()
