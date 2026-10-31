"""Fail-closed, read-only validation for one pristine 17-book original Laboratory.

This verifies a world supplied by the pinned, full-text corpus builder.
Verification NEVER imports a book, moves the Doctor, or invents experience.
"""
from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path


REQUIRED = frozenset(f"book:{i:03d}" for i in range(1, 18))


def verify_unread_seventeen(path: str | Path) -> dict:
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.book_library import BookLibrary
    from pretorius_lab.shelf_annex import physical_book_objects
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm

    source = Path(path).expanduser().resolve(strict=True)
    if source.is_symlink() or not source.is_file():
        raise ValueError("The template must be one existing, regular world file")
    world = SpatialHabitat(source)
    world_report = world.verify()
    HomeLife(world).verify()
    DailyRhythm(world).verify()
    library = BookLibrary(world)
    library.verify()
    catalog = library.catalog()
    if set(catalog) != REQUIRED:
        raise ValueError("Expected exactly 17 fully installed books")
    physically_present = physical_book_objects(world)
    if set(REQUIRED) - set(physically_present):
        raise ValueError("Every volume needs a physical shelf location")
    with closing(world._open()) as db:
        books = json.loads(db.execute(
            "SELECT value FROM books_meta WHERE key='books'"
        ).fetchone()[0])
        movement = db.execute("SELECT count(*) FROM embodied_events").fetchone()[0]
        completed_readings = db.execute(
            "SELECT count(*) FROM books_events WHERE json_extract(payload,'$.action.op')='read'"
        ).fetchone()[0]
    if set(books) != REQUIRED or movement != 0 or completed_readings != 0:
        raise ValueError("Not a pristine and unread physical Laboratory")
    for ident, item in books.items():
        edition = item["edition"]
        if (edition.get("source_class") != "public_domain_verified"
                or not edition.get("source_reference")
                or not isinstance(edition.get("pages"), list)
                or len(edition["pages"]) <= 10
                or any(type(page) is not str or not page.strip()
                       for page in edition["pages"])
                or item["opened"] is not False
                or item["current_page"] != 1
                or item["bookmarks"]):
            raise ValueError("Book missing full source or already experienced: " + ident)
    return {
        "status": "pristine",
        "books_installed": 17,
        "full_text_verified_with_original_laboratory": True,
        "source_bytes_manifest_independently_attested": False,
        "world_epoch": world_report["world_epoch"],
        "world_moves": movement,
        "prior_reads": completed_readings,
    }
