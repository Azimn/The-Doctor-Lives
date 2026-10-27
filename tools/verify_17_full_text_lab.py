#!/usr/bin/env python3
"""Build and audit all 17 source-backed physical volumes in ONE actual Lab.

Research-only, intentionally network-dependent corpus builder, invoked by
pinned GitHub Actions. Does not modify production world or character state.
Every Gutenberg source is independently checked by the reviewed Laboratory
importer against immutable Git byte length and Git blob before installation.

DO NOT pass the catalogue or engineering source bytes to the LLM. Subject
text must come from verified physical reading through DoctorHomeBridge.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from doctor_lives.lab_six_organ_session import SixOrganLaboratoryCycle
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime

from pretorius_lab.book_library import BookLibrary
from pretorius_lab.daily_rhythm import DailyRhythm
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.home_life import HomeLife
from pretorius_lab.period_bookshelf import (
    digital_leaves, genuine_text, import_collection, read_source,
)
from pretorius_lab.physics import LabError
from pretorius_lab.shelf_annex import physical_book_objects
from pretorius_lab.subject_port import SubjectPort


def save(path: Path, obj: object) -> None:
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    return cfg


def run(lab_root: Path, output_root: Path, affectus_root: Path) -> dict:
    source_root = lab_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    assert not (output_root / "laboratory.sqlite3").exists(), (
        "Never silently reinitialize an existing world"
    )
    manifest_files = (
        source_root / "corpus/victorian_bookshelf_v1.json",
        source_root / "corpus/esoteric_annex_1890.json",
    )
    manifests = [json.loads(p.read_text(encoding="utf-8")) for p in manifest_files]
    entries = [item for manifest in manifests for item in manifest["entries"]]
    required = {f"book:{n:03d}" for n in range(1, 18)}
    if len(entries) != 17 or {e["book_id"] for e in entries} != required:
        raise RuntimeError("Full text acceptance requires 17 distinct catalog identities")
    world = SpatialHabitat.create(output_root / "laboratory.sqlite3")
    source_payloads = {}
    expected_segments = {}
    original_bytes = {}
    def fetch_one(entry):
        ident = entry["book_id"]
        if ident in source_payloads:
            raise RuntimeError("Duplicate corpus download: " + ident)
        payload = read_source(entry)  # size + exact reviewed Git blob
        whole = genuine_text(payload)
        leaves = digital_leaves(whole)
        if "".join(leaves) != whole or len(leaves) <= 10:
            raise RuntimeError("Truncated book: " + ident)
        source_payloads[ident] = sha256(payload).hexdigest()
        expected_segments[ident] = leaves
        original_bytes[ident] = len(payload)
        return payload
    first = import_collection(
        world, manifests[0], setting_year=1890, fetcher=fetch_one,
    )
    second = import_collection(
        world, manifests[1], setting_year=1890,
        fetcher=fetch_one, register_annex=True,
    )
    if first["installed"] != 7 or second["installed"] != 10:
        raise RuntimeError("Not exactly 7+10 newly installed books")
    save(output_root / "seven-import.json", first)
    save(output_root / "ten-import.json", second)
    library = BookLibrary(world)
    library.verify()
    catalog = library.catalog()
    if set(catalog) != required:
        raise RuntimeError("Missing installed actual editions")
    physical = physical_book_objects(world)
    if set(required) - set(physical):
        raise RuntimeError("Some full-text books have no physical identity")
    record = {}
    with world._open() as db:  # engineer-only, NEVER model-facing
        ledger = json.loads(db.execute(
            "SELECT value FROM books_meta WHERE key='books'"
        ).fetchone()[0])
    for entry in entries:
        ident = entry["book_id"]
        volume = ledger[ident]["edition"]
        expected = expected_segments[ident]
        expected_slot = (
            f"shelf:3/slot:{int(ident[-3:])}"
            if int(ident[-3:]) <= 7
            else f"shelf:1/slot:{int(ident[-3:])-7}"
        )
        if physical[ident]["anchor_id"] != expected_slot:
            raise RuntimeError("Book is in an unexpected physical slot: " + ident)
        if (volume["pages"] != expected
                or volume["source_class"] != "public_domain_verified"
                or volume["title"] != entry["title"]
                or catalog[ident]["page_count"] != len(expected)
                or len(expected) < 11
                or not all(p.strip() for p in expected)):
            raise RuntimeError("Installed book text differs from verified bytes: " + ident)
        record[ident] = {
            "title": entry["title"], "author": entry["author"],
            "first_publication_year": entry["first_publication_year"],
            "source_git_blob_sha1": entry["source_git_blob_sha1"],
            "full_source_sha256": source_payloads[ident],
            "source_bytes": original_bytes[ident],
            "digital_segments": len(expected),
            "content_sha256": sha256("".join(expected).encode("utf-8")).hexdigest(),
            "physical_anchor": expected_slot,
            "first_segment_sha256": sha256(expected[0].encode("utf-8")).hexdigest(),
            "last_segment_sha256": sha256(expected[-1].encode("utf-8")).hexdigest(),
        }

    # Initialize the SAME embodied person in the already populated source world.
    HomeLife(world).initialize()
    DailyRhythm(world).initialize()
    subject = SubjectPort(world)
    doctor_path = output_root / "isolated-doctor-brain"
    doctor = SixOrganRuntime.open(doctor_path, neural_config=config())
    frames_seen = []

    def renderer(first_person):
        if not isinstance(first_person, str) or not first_person.startswith(
            ("I ", "My ", "Mine ", "Me ")
        ):
            raise PermissionError("Subject renderer was offered engineer data")
        frames_seen.append(sha256(first_person.encode("utf-8")).hexdigest())
        return "I am trying to understand what I have read."

    read_memories = {}
    with SixOrganLaboratoryCycle(
        doctor, subject, affectus_source=affectus_root,
        renderer=renderer, authorized=True, seed=1842,
    ) as host:
        # No remote reading. Even source-installed books require real reach.
        try:
            host.book_action(
                "book:008", "open", event_id="remote-book-open", authorized=True,
            )
        except LabError:
            pass
        else:
            raise RuntimeError("Unphysical remote reading was authorized")
        # Host-directed routes for availability ONLY, not autonomous initiative.
        host.bridge.act("walk", event_id="library-to-center", station="station:center")
        host.bridge.act("walk", event_id="library-to-first-shelf", station="station:shelf:1")
        order = [f"book:{n:03d}" for n in range(8, 18)]
        order += [f"book:{n:03d}" for n in range(1, 8)]
        for i, ident in enumerate(order):
            if ident == "book:001":
                host.bridge.act("walk", event_id="library-from-first-shelf",
                                station="station:center")
                host.bridge.act("walk", event_id="library-to-third-shelf",
                                station="station:shelf:3")
            event = ident.replace(":", "-")
            opened = host.book_action(
                ident, "open", event_id="fulltext-open-" + event,
                authorized=True,
            )
            reading = host.book_action(
                ident, "read", event_id="fulltext-read-" + event,
                authorized=True,
            )
            if opened["status"] != "admitted" or reading["status"] != "admitted":
                raise RuntimeError("Reading did not admit a new real-world receipt")
            if expected_segments[ident][0] not in reading["subject"]["inner"]:
                raise RuntimeError("Pretorius did not receive real text for " + ident)
            lived = doctor._port.brain.store.get_memory(reading["memory_id"])
            if (not lived or lived["text"] != reading["subject"]["inner"]
                    or lived["evidence_class"] != "lived_runtime_memory"
                    or not lived["source"].startswith("laboratory-home:action:")):
                raise RuntimeError("Unverified/incorrect first-person reading of " + ident)
            read_memories[ident] = reading["memory_id"]
            # Non-resetting canonical one-time world action, all books distinct.
        # Next actual page also exists, not just a title and one stored preview.
        ident = "book:007"
        host.book_action(
            ident, "turn", direction=1,
            event_id="fulltext-book007-turn-page2", authorized=True,
        )
        second_read = host.book_action(
            ident, "read", event_id="fulltext-book007-read-page2",
            authorized=True,
        )
        if expected_segments[ident][1] not in second_read["subject"]["inner"]:
            raise RuntimeError("Page two is not the pinned full source")
        # Publish once through the durable first-person gate. Never give
        # engineering catalog or hidden source bytes to a renderer.
        host.ipseity.publish_current()
        host.ipseity.deliver_next(now_ms=1_200_000)
        doctor.checkpoint()

    reopened = SixOrganRuntime.open(doctor_path)
    world_reopened = SpatialHabitat(output_root / "laboratory.sqlite3")
    subject_reopened = SubjectPort(world_reopened)
    before_replay_events = library.verify()
    with SixOrganLaboratoryCycle(
        reopened, subject_reopened, affectus_source=affectus_root,
        renderer=renderer, authorized=True, seed=1842,
    ) as host:
        identical = host.book_action(
            "book:007", "read",
            event_id="fulltext-book007-read-page2", authorized=True,
        )
        if (identical["status"] != "already_admitted"
                or identical["memory_id"] != second_read["memory_id"]):
            raise RuntimeError("World restart duplicated a read receipt")
        for ident, memory_id in read_memories.items():
            mem = reopened._port.brain.store.get_memory(memory_id)
            if not mem or expected_segments[ident][0] not in mem["text"]:
                raise RuntimeError("Restart lost source-attested personal reading")
    if before_replay_events != library.verify():
        raise RuntimeError("Replaying old page read mutated the world book ledger")
    if len(set(read_memories.values())) != 17:
        raise RuntimeError("Book reading memories are not 17 unique receipts")
    if set(BookLibrary(world_reopened).catalog()) != required:
        raise RuntimeError("World restart lost a physical full text")
    # Creates an independently replay-verified physical backup with ALL pages.
    backup_path = output_root / "verified-17-full-text-backup.sqlite3"
    world_reopened.backup(backup_path)
    backup_books = BookLibrary(SpatialHabitat(backup_path))
    if set(backup_books.catalog()) != required:
        raise RuntimeError("Backed-up full-text collection incomplete")
    report = {
        "schema": "pretorius.seventeen-full-text-lab-acceptance.v1",
        "pinned_lab": "6e49795752835d64fa6fd63d16359669a1ca2ba7",
        "setting_year": 1890,
        "total_full_text_books": len(record),
        "original_seven": 7, "esoteric_ten": 10,
        "full_source_bytes": sum(original_bytes.values()),
        "total_digital_segments": sum(len(p) for p in expected_segments.values()),
        "world_verified": True, "physical_shelves_verified": 17,
        "actual_host_authorized_book_reads": len(read_memories),
        "distinct_lived_read_memories": len(set(read_memories.values())),
        "actual_second_page_issued": 1, "duplicate_read_memory_count": 0,
        "brain_restart": True, "world_restart": True,
        "auto_initiated_book_goals_proven": 0,
        "default_production_world_changed": False,
        "books": record,
    }
    save(output_root / "acceptance.json", report)
    save(output_root / "physical-world-proof.json", world_reopened.verify())
    save(output_root / "catalog.json", backup_books.catalog())
    print("SIX_ORGAN_FULLTEXT_17_ACCEPTANCE=" + json.dumps({
        k: v for k, v in report.items() if k != "books"
    }, sort_keys=True))
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lab-source", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--affectus-source", required=True)
    a = p.parse_args()
    run(Path(a.lab_source), Path(a.output_dir), Path(a.affectus_source))


if __name__ == "__main__":
    main()
