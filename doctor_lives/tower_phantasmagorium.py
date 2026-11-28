"""Original Phantasmagorium v0.5 on authenticated Tower activity boundaries.

The donor snapshot and nonfactual recollection share the canonical BrainStore
transaction. No imagined scene can become a verified physical outcome.
"""
from contextlib import closing
from hashlib import sha256
import json

from .lab_phantasmagorium import (
    STATE, SOURCE, _snapshot, _stable, _digest, _run, _nonfactual,
)
from .phantasmagorium_bridge import DONOR_SHA256, verify_archive

CURSOR = "phantasmagorium:tower-cursor:v1"
LATEST_FANCY = "phantasmagorium:tower-latest-fancy:v1"
ELIGIBLE = ("read", "rest", "sleep")


def _require_subject(store, subject):
    from .tower_ipseity import TowerIpseity
    if type(subject) is not TowerIpseity or subject.store is not store:
        raise PermissionError("Imagination requires its owning Synthetic Ipseity organ")
    return subject


def sync_tower_phantasmagorium(store, provider, receipt, memory_id, archive, *, subject=None):
    """Consume an actual completed read or sleep once, including source replay."""
    from .small_tower import SmallTowerSource
    from .virtual_world_port import VirtualWorldReceipt
    if (type(provider) is not SmallTowerSource
            or type(receipt) is not VirtualWorldReceipt
            or receipt.kind != "action"
            or receipt.operation not in ELIGIBLE
            or not receipt.successful
            or not provider.verify_receipt(receipt)):
        raise PermissionError("Authentic completed Tower reading, rest or sleep required")
    memory = store.get_memory(memory_id)
    source = ("virtual-world:small-tower:" + receipt.world_epoch
              + ":action:" + receipt.event_id)
    if (not memory or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or memory["source"] != source or memory["text"] != receipt.first_person
            or not memory.get("source_event_id")):
        raise PermissionError("Exact admitted Tower source memory required")
    _require_subject(store, subject)
    subject_digest = store.digest()
    archive = verify_archive(archive)
    digest = sha256(source.encode()).hexdigest()
    key = "phantasmagorium:tower-event:" + digest
    previous = store.meta(key)
    if previous:
        report = json.loads(previous)
        if report["source_memory_id"] != memory_id:
            raise PermissionError("Conflicting imagination source replay")
        return report
    raw = store.meta(STATE)
    state = _snapshot(raw, receipt.world_epoch)
    sleeping = receipt.operation == "sleep"
    day = state["nights"] + 1
    request = {"pin": DONOR_SHA256, "files": state["files"], "day": day,
               "seed": int(digest[:15], 16), "cues": [memory["text"]],
               "op": "night" if sleeping else "fancy"}
    if sleeping:
        with closing(store.connect()) as db:
            cues = db.execute(
                "SELECT text FROM memories WHERE active=1 AND external=0 "
                "AND evidence_class='lived_runtime_memory' AND source LIKE ? "
                "AND created_tick<? ORDER BY created_tick DESC LIMIT 5",
                ("virtual-world:small-tower:" + receipt.world_epoch + ":%",
                 memory["created_tick"])).fetchall()
        request["cues"] = [r["text"][:1000] for r in reversed(cues)] + request["cues"]
    elif receipt.operation == "read":
        # The Tower currently supplies a witnessed consultation, not full page
        # text. Do not invent the book's contents or a second lived event.
        request["scene"] = {"initial_scene": {"entities": [
            {"id": "folio", "kind": "book", "properties": {"form": "historical folio"}},
            {"id": "page", "kind": "page", "properties": {"context": memory["text"]}},
        ], "relations": []}, "max_fragments": 4}
    else:
        # Waking reverie during a genuinely completed quiet rest. The only
        # ingredients are the lived rest and a preceding admitted perception.
        with closing(store.connect()) as db:
            previous = db.execute(
                "SELECT text FROM memories WHERE active=1 AND external=0 "
                "AND evidence_class='lived_runtime_memory' AND source LIKE ? "
                "AND created_tick<? ORDER BY created_tick DESC,id DESC LIMIT 1",
                ("virtual-world:small-tower:" + receipt.world_epoch + ":observation:%",
                 memory["created_tick"])).fetchone()
        impression = previous["text"][:160] if previous else memory["text"][:160]
        request["cues"].insert(0, impression)
        request["scene"] = {"initial_scene": {"entities": [
            {"id": "rest", "kind": "activity", "properties": {"context": memory["text"][:160]}},
            {"id": "impression", "kind": "memory", "properties": {"context": impression}},
        ], "relations": []}, "max_fragments": 4}
    output = _run(archive, request)
    result, recall = output["result"], output["recall"]
    expected = "dreamed_not_lived" if sleeping else "hypothetical_only"
    if not _nonfactual(result, expected):
        raise PermissionError("Original donor omitted fictional provenance")
    text = None
    motifs = ()
    if sleeping:
        if not _nonfactual(recall, "dreamed_not_lived") or type(recall.get("has_recollection")) is not bool:
            raise PermissionError("Unmarked dream recollection")
        if recall["has_recollection"]:
            text = recall["text"]
            from .phenomenology import implementation_leaks, control_instruction_markers
            if (type(text) is not str or not text.startswith("I recall a dream: ")
                    or len(text) > 800 or implementation_leaks(text)
                    or control_instruction_markers(text)):
                raise PermissionError("Unmarked or unsafe dream text")
    else:
        motifs = verified_fancy_motifs(result)
    updated = dict(state, files=output["files"])
    if sleeping:
        updated["nights"] = day
    envelope = {"payload": updated, "sha256": _digest(updated)}
    report = {"source_sha256": digest, "source_memory_id": memory_id,
              "source_event_id": memory["source_event_id"],
              "donor_sha256": DONOR_SHA256, "operation": request["op"],
              "sleep_index": updated["nights"], "fictional_result_sha256": _digest(result),
              "recollection_memory_id": None, "world_authority": False,
              "factual_memory_eligible": False, "motor_authority": False,
              "fragment_count": len(result.get("fragments", [])),
              "source_operation": receipt.operation, "fictional_motifs": list(motifs)}
    with store.transaction() as db:
        existing = db.execute("SELECT value FROM meta WHERE key=?", (STATE,)).fetchone()
        if (existing["value"] if existing else None) != raw:
            raise RuntimeError("Concurrent original Phantasmagorium update")
        if db.execute("SELECT 1 FROM meta WHERE key=?", (key,)).fetchone():
            raise RuntimeError("Duplicate donor source event")
        if text:
            report["recollection_memory_id"] = store.add_memory(
                db, store.tick, text, SOURCE + digest, "dream_recollection",
                "dreamed_not_lived", True, 1.0, False, .35,
                tags=("dream", "fictional", "nonfactual"))
        from .phenomenology import PhenomenalMode, SubjectiveSourceKind
        events = []
        if text:
            events.append(subject.event("Phantasmagorium", text, PhenomenalMode.RECOLLECTION,
                (memory_id, report["recollection_memory_id"]), attribution=SubjectiveSourceKind.DREAMED,
                external=True, digest=subject_digest))
        for motif in motifs:
            events.append(subject.event("Phantasmagorium", fancy_line(motif), PhenomenalMode.INTERNAL_THOUGHT,
                (memory_id,), attribution=SubjectiveSourceKind.IMAGINED, external=True, digest=subject_digest))
        if events:
            admission = subject.record(db, "imagination:" + digest, events, phase="imagination")
            report["ipseity_admission_sha256"] = admission["sha256"]
        store.set_meta(STATE, _stable(envelope), db)
        store.set_meta(key, _stable(report), db)
        if motifs:
            pointer = {"key": key, "source": source, "report_sha256": _digest(report)}
            store.set_meta(LATEST_FANCY, _stable(pointer), db)
        store.bump_state_version(db)
    return report


def verified_fancy_motifs(result):
    """Only marked, bounded and non-control creative motifs can affect retrieval."""
    from .phenomenology import implementation_leaks, control_instruction_markers
    if not _nonfactual(result, "hypothetical_only"):
        raise PermissionError("Unmarked waking imagination")
    fragments = result.get("fragments")
    if type(fragments) is not list or len(fragments) > 4:
        raise PermissionError("Unbounded fancy fragments")
    motifs = []
    for fragment in fragments:
        if not _nonfactual(fragment, "dreamed_not_lived"):
            raise PermissionError("Unmarked fancy fragment")
        motif = fragment.get("motif")
        if (type(motif) is str and 0 < len(motif) <= 160
                and not implementation_leaks(motif)
                and not control_instruction_markers(motif)
                and motif not in motifs):
            motifs.append(motif)
    return tuple(motifs)


def fancy_line(motif):
    return "I imagine " + motif.rstrip(".") + ", without taking it for something I witnessed."


def retrieval_motifs(store, observation_source, *, subject=None):
    """Private nonfactual associations, never direct action or lived evidence."""
    raw = store.meta(LATEST_FANCY)
    if raw is None:
        return ()
    _require_subject(store, subject)
    pointer = json.loads(raw)
    if (type(pointer) is not dict
            or set(pointer) != {"key", "source", "report_sha256"}
            or not pointer["key"].startswith("phantasmagorium:tower-event:")
            or pointer["key"] != "phantasmagorium:tower-event:" + sha256(pointer["source"].encode()).hexdigest()
            or pointer["source"].rsplit(":", 2)[0] != observation_source.rsplit(":", 2)[0]):
        raise PermissionError("Foreign or malformed imaginative continuity")
    report = json.loads(store.meta(pointer["key"]))
    if (_digest(report) != pointer["report_sha256"]
            or report["operation"] != "fancy" or report["donor_sha256"] != DONOR_SHA256
            or any(report[k] is not False for k in
                   ("world_authority", "factual_memory_eligible", "motor_authority"))):
        raise PermissionError("Unverified imaginative continuity")
    memory = store.get_memory(report["source_memory_id"])
    if (not memory or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or memory["source"] != pointer["source"]
            or memory.get("source_event_id") != report["source_event_id"]):
        raise PermissionError("Missing original imaginative source")
    motifs = report["fictional_motifs"]
    if type(motifs) is not list or len(motifs) > 4 or any(type(m) is not str or not 0 < len(m) <= 160 for m in motifs):
        raise PermissionError("Malformed imaginative cues")
    from .phenomenology import implementation_leaks, control_instruction_markers
    if any(implementation_leaks(m) or control_instruction_markers(m) for m in motifs):
        raise PermissionError("Unsafe imaginative cues")
    # Preserve pre-repair reports as engineering evidence, never fabricate a
    # historical admission or expose their unowned motifs to current cognition.
    if "ipseity_admission_sha256" not in report:
        return ()
    from .tower_ipseity import RECORD
    digest = sha256(pointer["source"].encode()).hexdigest()
    if report.get("source_sha256") != digest:
        raise PermissionError("Imaginative report source digest mismatch")
    key = RECORD + "imagination:" + digest
    entry = next((e for e in subject.verify_history() if e["key"] == key), None)
    expected = [{"organ": "Phantasmagorium", "text": fancy_line(motif),
                 "mode": "internal_thought", "attribution": "imagined",
                 "source_refs": [memory["id"]], "external": True} for motif in motifs]
    if (entry is None or entry["phase"] != "imagination"
            or entry["sha256"] != report["ipseity_admission_sha256"]
            or entry["content"] != expected):
        raise PermissionError("Imaginative cues differ from owned admission")
    return tuple(motifs)


def sync_history(store, provider, snapshot, archive, *, subject=None):
    """Replay missed eligible events in source order, independently of world ingress."""
    from .small_tower import SmallTowerSource
    if type(provider) is not SmallTowerSource or provider.world_epoch != snapshot["epoch"]:
        raise PermissionError("Actual same-epoch Tower history required")
    _require_subject(store, subject)
    archive = verify_archive(archive)
    raw = store.meta(CURSOR)
    after = 0
    if raw is not None:
        saved = json.loads(raw)
        if saved["epoch"] != snapshot["epoch"]:
            raise PermissionError("Foreign Phantasmagorium cursor")
        after = saved["cursor"]
    if type(after) is not int or not 0 <= after <= snapshot["cursor"]:
        raise PermissionError("Invalid Phantasmagorium source cursor")
    if after == snapshot["cursor"] and raw is not None:
        return ()
    history = provider.snapshot(after)
    if history["cursor"] != snapshot["cursor"] or history["revision"] != snapshot["revision"]:
        raise PermissionError("World changed during imagination reconciliation")
    rows = [r for r in history["events"]
            if r["kind"] == "completed" and r["operation"] in ELIGIBLE]
    def source_for(receipt):
        return "virtual-world:small-tower:" + receipt.world_epoch + ":action:" + receipt.event_id
    def event_key(receipt):
        return "phantasmagorium:tower-event:" + sha256(source_for(receipt).encode()).hexdigest()
    # Earlier versions had no separate cursor. Preserve their committed
    # chronology, never insert a new dream behind an already stored night.
    last_existing = max((r["sequence"] for r in rows
                         if store.meta(event_key(provider.event_receipt(r))) is not None),
                        default=after)
    if raw is None and store.meta(STATE) is not None:
        if any(r["sequence"] < last_existing and r["operation"] in ("read", "sleep")
               and store.meta(event_key(provider.event_receipt(r))) is None for r in rows):
            raise PermissionError("Historical donor gap requires explicit chronological migration")
    reports = []
    for row in rows:
        receipt = provider.event_receipt(row)
        if row["sequence"] < last_existing and row["operation"] == "rest" and store.meta(event_key(receipt)) is None:
            # Quiet rest became eligible in this release; no retroactive
            # insertion into an already advanced dream journal.
            continue
        with closing(store.connect()) as db:
            matches = db.execute("SELECT id FROM memories WHERE source=? AND active=1",
                                 (source_for(receipt),)).fetchall()
        if len(matches) != 1:
            raise PermissionError("Imagination history lacks unique admitted source memory")
        reports.append(sync_tower_phantasmagorium(store, provider, receipt,
                                                  matches[0]["id"], archive,subject=subject))
    with store.transaction() as db:
        prior = db.execute("SELECT value FROM meta WHERE key=?", (CURSOR,)).fetchone()
        if (prior["value"] if prior else None) != raw:
            raise RuntimeError("Concurrent Phantasmagorium cursor writer")
        store.set_meta(CURSOR, _stable({"epoch": snapshot["epoch"], "cursor": snapshot["cursor"]}), db)
        store.bump_state_version(db)
    return tuple(reports)


def require_archive(store, *, required=False):
    """A configured donor cannot silently disappear from a continuing life."""
    from .lab_phantasmagorium import configured_archive
    archive = configured_archive()
    if archive is None and (required or store.meta(STATE) is not None
                            or store.meta(CURSOR) is not None):
        raise FileNotFoundError("Original Phantasmagorium v0.5 archive required; set PRETORIUS_PHANTA_DONOR")
    return archive
