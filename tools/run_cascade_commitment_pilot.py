"""Authored exploratory four-arm pilot for a durable commitment-to-action loop.

Three Laboratory locations, separate frozen checkpoints, real host restarts,
unrelated Doctor cognition, verified sightings, and an equal-information
receipt-ledger controller. Not independent or an Article qualification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile

from doctor_lives.cascade_laboratory import remember_look
from tools.run_cascade_articles_pilot import open_host
from tools.run_cascade_laboratory_pilot import simple_read
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.embodied_access import EmbodiedAccess
from pretorius_lab.book_library import BookLibrary

ARMS = ("doctor_memory", "memory_lesion",
        "memory_restoration", "simple_receipt_ledger")


def run_pilot():
    cases = []
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for shelf in (1, 2, 3):
            seed = root / ("seed-" + str(shelf))
            seed.mkdir()
            lab = SpatialHabitat.create(seed / "world.sqlite3")
            library = BookLibrary(lab)
            library.initialize()
            library.install("book:007", edition_id="commitment-pilot-v1",
                            title="Task Reference", author="Synthetic Fixture",
                            pages=["Copper conducts electricity."],
                            source_class="original_fixture",
                            source_reference="authored exploratory case")
            if shelf != 3:
                lab.commit({"op": "place", "object_id": "book:007",
                            "anchor_id": f"shelf:{shelf}/slot:1"})
            port = EmbodiedAccess(lab)
            port.initialize(station="station:center")
            seed_state = seed / "three-organ-preview"
            host, _ = open_host(seed_state, "cascade")
            try:
                host.accept_laboratory_commitment(
                    port, task_id="find-book", book_id="book:007",
                    expires_ms=100_000, max_actions=4, authorized=True)
            finally:
                host.close()
            for arm in ARMS:
                case_dir = root / f"case-{shelf}-{arm}"
                case_dir.mkdir()
                lab.backup_to(case_dir / "world.sqlite3")
                world = SpatialHabitat(case_dir / "world.sqlite3")
                actor = EmbodiedAccess(world)
                if arm == "simple_receipt_ledger":
                    # A separate simple durable intent and receipt are sufficient;
                    # do not give this baseline access to Doctor state.
                    contract = {"book_id": "book:007", "budget": 4,
                                "authorized": True, "expires_ms": 100_000}
                    contract_path = case_dir / "receipt-ledger.json"
                    contract_path.write_text(json.dumps(contract))
                    actor.move(f"station:shelf:{shelf}")
                    sighting = actor.look()
                    actor.move("station:center")
                    contract_path.write_text(json.dumps(
                        {"intent": contract, "sighting": sighting}))
                    after_restart = json.loads(contract_path.read_text())
                    before = {"status": "waiting_prerequisite", "actions": 0}
                    result = simple_read(actor, after_restart["sighting"],
                                         budget=after_restart["intent"]["budget"])
                    result["status"] = "completed" if result["success"] else "needs_review"
                    result["policy"] = "simple-persisted-receipt"
                else:
                    state = case_dir / "three-organ-preview"
                    shutil.copytree(seed_state, state)
                    host, _ = open_host(state, "cascade")
                    try:
                        before = host.service_laboratory_commitment(
                            actor, task_id="find-book", now_ms=10,
                            authorized=True)
                        actor.move(f"station:shelf:{shelf}")
                        sighting = actor.look()
                        ids = remember_look(host, actor, sighting)
                        actor.move("station:center")
                        host._doctor.brain.heartbeat(ticks=1)
                        host._doctor.brain.save()
                    finally:
                        host.close()
                    host, _ = open_host(state, "cascade")
                    try:
                        store = host._doctor.brain.store
                        target = next(i for i in ids if store.get_memory(i)["source"].endswith("book:007"))
                        if arm in ("memory_lesion", "memory_restoration"):
                            with store.transaction() as db:
                                store.archive_memory(db, target, store.tick,
                                                     "matched pilot memory intervention")
                                store.bump_state_version(db)
                                if arm == "memory_restoration":
                                    db.execute("UPDATE memories SET active=1 WHERE id=?",
                                               (target,))
                                    store.bump_state_version(db)
                        result = host.service_laboratory_commitment(
                            actor, task_id="find-book", now_ms=11,
                            authorized=True)
                        result["success"] = result["status"] == "completed"
                    finally:
                        host.close()
                cases.append({"shelf": shelf, "arm": arm, "before_sighting": before,
                              "after_restart": result,
                              "world_revision": actor.verify()["revision"]})
    counts = {arm: sum(int(c["after_restart"]["success"])
                       for c in cases if c["arm"] == arm) for arm in ARMS}
    return {"schema": "cascade.commitment-pilot.v0.1",
            "evidence_class": "authored_exploratory_software_experiment",
            "independent_cases": False, "real_elapsed_delay": False,
            "autonomous_scheduler_installed": False,
            "full_article_qualification": False,
            "actions_per_task": 4,
            "successes_of_three": counts,
            "cases": cases,
            "interpretation": "Tests a host-woken source-memory prerequisite and bounded real task completion; receipt-ledger control is equally informed."}


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = run_pilot()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"successes_of_three": report["successes_of_three"],
                      "output": str(args.output)}))


if __name__ == "__main__":
    main()
