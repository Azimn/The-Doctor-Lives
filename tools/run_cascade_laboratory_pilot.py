"""Exploratory real-world consequence probe with a simple explicit control.

Authored cases, simulated Laboratory world, deterministic renderer, tiny
neural configuration. No independent qualification or learned-policy claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from doctor_lives.cascade_laboratory import remember_look
from tools.run_cascade_articles_pilot import open_host
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.embodied_access import EmbodiedAccess
from pretorius_lab.book_library import BookLibrary

LABORATORY_PIN = "290ec97727c84728e61f69265949551e4ce911ec"
ARMS = ("doctor_memory", "memory_lesion", "memory_restoration", "simple_receipt_ledger")


def simple_read(port, witnessed_receipt, budget=4):
    """Independent explicit lookup controller, same observed information.

    Receives the same earlier local offer that entered Doctor, not a global
    world map. Selects the witnessed shelf if the requested book was there.
    """
    payload = witnessed_receipt["offered_payload"]
    found = any(x["object_id"] == "book:007" for x in payload["nearby_objects"])
    hint = payload["location"]["station"] if found else None
    order = ([hint] if hint else []) + [f"station:shelf:{n}" for n in (1, 2, 3)
                                          if f"station:shelf:{n}" != hint]
    actions = []
    result = {"success": False, "actions": actions, "policy": "simple-receipt-ledger"}
    def act(kind, arg=None):
        if len(actions) == budget:
            return None
        if kind == "move":
            receipt = port.move(arg)
        elif kind == "look":
            receipt = port.look()
        else:
            receipt = port.book("book:007", kind)
        actions.append({"kind": kind, "argument": arg, "receipt": receipt})
        return receipt
    for station in order:
        if port.verify()["station"] != station:
            if port.verify()["station"] != "station:center":
                if act("move", "station:center") is None:
                    break
            if act("move", station) is None:
                break
        view = act("look")
        if view is None:
            break
        if not any(x["object_id"] == "book:007" for x in view["offered_payload"]["nearby_objects"]):
            continue
        if act("open") is None:
            break
        page = act("read")
        if page:
            BookLibrary(port.habitat).verify()
            result.update(success=True, page_text=page["page_text"])
        break
    result["actions_used"] = len(actions)
    return result


def run_pilot():
    cases = []
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for shelf in (1, 2, 3):
            seed = root / f"seed-{shelf}"
            seed.mkdir()
            lab = SpatialHabitat.create(seed / "world.sqlite3")
            library = BookLibrary(lab)
            library.initialize()
            library.install("book:007", edition_id="pilot-v1", title="Task Reference",
                            author="Synthetic Fixture", pages=["Copper conducts electricity."],
                            source_class="original_fixture", source_reference="authored engineering case")
            if shelf != 3:
                lab.commit({"op": "place", "object_id": "book:007",
                            "anchor_id": f"shelf:{shelf}/slot:1"})
            port = EmbodiedAccess(lab)
            port.initialize(station="station:center")
            host, _ = open_host(seed / "three-organ-preview", "cascade")
            try:
                port.move(f"station:shelf:{shelf}")
                sighting = port.look()
                ids = remember_look(host, port, sighting)
                memory = next(i for i in ids if host._doctor.brain.store.get_memory(i)["source"].endswith("book:007"))
                port.move("station:center")
            finally:
                host.close()
            for arm in ARMS:
                case_dir = root / f"case-{shelf}-{arm}"
                case_dir.mkdir()
                lab.backup_to(case_dir / "world.sqlite3")
                world = SpatialHabitat(case_dir / "world.sqlite3")
                actor = EmbodiedAccess(world)
                if arm == "simple_receipt_ledger":
                    result = simple_read(actor, sighting)
                else:
                    shutil.copytree(seed / "three-organ-preview", case_dir / "three-organ-preview")
                    host, _ = open_host(case_dir / "three-organ-preview", "cascade")
                    try:
                        store = host._doctor.brain.store
                        if arm in ("memory_lesion", "memory_restoration"):
                            with store.transaction() as db:
                                store.archive_memory(db, memory, store.tick, "exploratory matched memory intervention")
                                store.bump_state_version(db)
                                if arm == "memory_restoration":
                                    db.execute("UPDATE memories SET active=1 WHERE id=?", (memory,))
                                    store.bump_state_version(db)
                        result = host.laboratory_read(actor, task_id="read-after-restart", book_id="book:007",
                                                      max_actions=4, authorized=True)
                    finally:
                        host.close()
                cases.append({"case": f"shelf-{shelf}", "arm": arm,
                              "history_receipt": sighting, "result": result,
                              "verified_body": actor.verify(), "verified_books": BookLibrary(world).verify()})
    source_root = Path(__file__).resolve().parents[1]
    sources = ("doctor_lives/cascade_laboratory.py", "doctor_lives/cascade_preview.py",
               "doctor_lives/cascade_background.py", "tools/run_cascade_laboratory_pilot.py")
    source_hashes = {p: hashlib.sha256((source_root / p).read_bytes()).hexdigest() for p in sources}
    wins = {arm: sum(x["result"]["success"] for x in cases if x["arm"] == arm) for arm in ARMS}
    return {"schema": "cascade.laboratory-pilot.v1", "laboratory_pin": LABORATORY_PIN,
            "evidence_class": "author_executed_exploratory_software_experiment",
            "full_article_qualification": False, "independent_cases": False,
            "protocol": {"case_locations": 3, "arms": list(ARMS), "action_budget": 4,
                         "restart": "host_close_then_new_host_on_copied_checkpoint",
                         "real_elapsed_delay": False, "renderer": "deterministic_governor_fixture"},
            "successes_of_three": wins,
            "interpretation": "Persistent source memory changes real route and bounded page delivery. Simple receipt ledger ties; no unique neural or CASCADE advantage established.",
            "source_sha256": source_hashes, "cases": cases}


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run_pilot()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"successes_of_three": report["successes_of_three"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
