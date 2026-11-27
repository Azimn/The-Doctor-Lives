"""Persistent original Phantasmagorium v0.5 on the one canonical Doctor.

The pinned original archive remains an external, owner-provided asset.
The exact donor facade runs in disposable scratch storage. Its continuity
snapshot and nonfactual recollections commit together in original BrainStore.
A dream is not a physical observation, autobiography, or motor grant.
"""
from __future__ import annotations

import base64
from contextlib import closing
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

from .phantasmagorium_bridge import verify_archive, DONOR_SHA256

ENV = "PRETORIUS_PHANTA_DONOR"
STATE = "phantasmagorium:canonical-v05"
SOURCE = "phantasmagorium:dream-recollection:"
LIMIT = 8_000_000

WORKER = r'''
import base64, hashlib, json, pathlib, sys, tempfile, zipfile
archive = pathlib.Path(sys.argv[1])
request = json.load(sys.stdin)
if hashlib.sha256(archive.read_bytes()).hexdigest() != request["pin"]:
    raise PermissionError("Donor changed after verification")
with tempfile.TemporaryDirectory(prefix="pretorius-phantasmagorium-") as tmp:
    root = pathlib.Path(tmp)
    with zipfile.ZipFile(archive) as pack:
        pack.extractall(root / "code")
    sys.path.insert(0, str(root / "code" / "Phantasmagorium_v0.5"))
    from phantasmagorium import Phantasmagorium
    scratch = root / "continuity"
    scratch.mkdir()
    for name, value in request["files"].items():
        rel = pathlib.PurePosixPath(name)
        if (rel.is_absolute() or "\\" in name or ":" in name
                or any(part in ("", ".", "..") for part in name.split("/"))
                or rel.suffix != ".json"):
            raise PermissionError("Unexpected donor continuity path")
        target = scratch.joinpath(*rel.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(value, validate=True))
    organ = Phantasmagorium(scratch, character_id="pretorius")
    for cue in request["cues"]:
        organ.observe(text=cue, day=request["day"], authorized=True,
                      provenance="firsthand")
    if request["op"] == "night":
        result = organ.night(day=request["day"], seed=request["seed"])
        recall = organ.recollect(seed=request["seed"])
        echo = organ.morning_echo(day=request["day"])
        # Restore donor's ordinary retention/expiry progression, never
        # force a dream to be remembered or insert a waking world fact.
        organ.tick(quiet=False)
    elif request["op"] == "fancy":
        result = organ.imagine(request["scene"], seed=request["seed"], mode="mixed")
        recall = None
        echo = None
        organ.tick(quiet=True)
    else:
        raise ValueError("Unknown original donor operation")
    files = {}
    total = 0
    for path in sorted(scratch.rglob("*")):
        if path.is_symlink():
            raise PermissionError("Unexpected donor symlink")
        if path.is_file():
            if path.suffix != ".json":
                raise PermissionError("Unexpected non-JSON continuity file")
            data = path.read_bytes()
            total += len(data)
            if total > 6000000 or len(files) >= 1000:
                raise ValueError("Donor continuity exceeds explicit bound")
            files[path.relative_to(scratch).as_posix()] = base64.b64encode(data).decode()
    print(json.dumps({"files": files, "result": result, "recall": recall,
                      "echo": echo}, ensure_ascii=False, allow_nan=False))
'''


def configured_archive(value=None):
    path = value if value is not None else os.environ.get(ENV)
    return verify_archive(path) if path else None


def _stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _digest(value):
    return sha256(_stable(value).encode()).hexdigest()


def _snapshot(raw, epoch):
    if raw is None:
        return {"epoch": epoch, "files": {}, "nights": 0,
                "last_sleep_revision": 0, "last_read_revision": 0}
    env = json.loads(raw)
    payload = env["payload"]
    if (env["sha256"] != _digest(payload) or payload["epoch"] != epoch
            or set(payload) != {"epoch", "files", "nights",
                                "last_sleep_revision", "last_read_revision"}
            or type(payload["files"]) is not dict
            or any(type(payload[k]) is not int or payload[k] < 0 for k in
                   ("nights", "last_sleep_revision", "last_read_revision"))):
        raise PermissionError("Invalid Phantasmagorium continuity envelope")
    return payload


def _nonfactual(packet, status):
    return (type(packet) is dict and packet.get("epistemic_status") == status
            and packet.get("marked") is True
            and all(packet.get(k) is False for k in (
                "factual_memory_eligible", "world_fact_authority", "tool_authority")))


def _run(archive, request):
    raw = _stable(request)
    if len(raw) > LIMIT:
        raise ValueError("Phantasmagorium request exceeds continuity budget")
    archive = verify_archive(archive)
    if request.get("pin") != DONOR_SHA256:
        raise PermissionError("Exact original donor pin required")
    proc = subprocess.run([sys.executable, "-I", "-c", WORKER, str(archive)],
                          input=raw, capture_output=True, text=True,
                          encoding="utf-8", timeout=30, cwd=archive.parent)
    if proc.returncode or len(proc.stdout.encode()) > LIMIT:
        raise RuntimeError("Original Phantasmagorium worker failed: " + proc.stderr[-500:])
    result = json.loads(proc.stdout)
    if type(result.get("files")) is not dict:
        raise PermissionError("Missing original donor continuity")
    for name, encoded in result["files"].items():
        p = PurePosixPath(name)
        if (p.is_absolute() or "\\" in name or ":" in name
                or any(x in ("", ".", "..") for x in name.split("/"))
                or p.suffix != ".json" or type(encoded) is not str):
            raise PermissionError("Invalid donor snapshot member")
        json.loads(base64.b64decode(encoded, validate=True).decode("utf-8"))
    return result


def _next_event(bridge, table, cursor, op):
    """Actual physical ledger plus exact admitted memory, never operator text."""
    from .lab_home_bridge import _row
    store = bridge.doctor.brain.store
    epoch = bridge.subject.verify()["world_epoch"]
    with bridge.world._open() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                          (table,)).fetchone():
            return None
        rows = db.execute(
            "SELECT event_id,revision FROM " + table + " WHERE revision>? ORDER BY revision",
            (cursor,)).fetchall()
        for event_id, revision in rows:
            event, digest = _row(db, table, event_id)
            operation = event.get("op") if table == "rhythm_events" else event.get("action", {}).get("op")
            if operation != op or event.get("world_epoch") != epoch:
                continue
            if op == "sleep" and (event.get("station") != "station:bedroom" or event.get("args") != {}):
                raise PermissionError("Invalid original sleep receipt")
            if op == "read" and (not event.get("page_receipt") or not event.get("access_proof")):
                raise PermissionError("Invalid original reading receipt")
            source = "laboratory-home:action:" + digest
            with closing(store.connect()) as brain_db:
                matches = brain_db.execute(
                    "SELECT id FROM memories WHERE source=? AND active=1 AND external=0 "
                    "AND evidence_class='lived_runtime_memory'", (source,)).fetchall()
            if not matches:
                continue
            if len(matches) != 1:
                raise PermissionError("Ambiguous source memory for Phantasmagorium")
            memory = store.get_memory(matches[0]["id"])
            if op == "sleep" and memory["text"] != event["subject"]["inner"]:
                raise PermissionError("Sleep memory differs from original receipt")
            if op == "read" and not memory["text"].startswith("I read a page of "):
                raise PermissionError("Reading memory lacks first-person source")
            return revision, digest, memory
    return None


def sync_phantasmagorium(bridge, archive):
    """Consume one genuine read or sleep event after original world admission.

    Host schedules only opportunities. No new world event or goal is made.
    Donor day is the successive physical sleep index, not wall-clock time.
    A prior actual event may be reconciled after a crash or late activation.
    """
    from .lab_home_bridge import DoctorHomeBridge
    if type(bridge) is not DoctorHomeBridge:
        raise PermissionError("Actual original Laboratory bridge required")
    archive = verify_archive(archive)
    brain = bridge.doctor.brain
    store = brain.store
    epoch = bridge.subject.verify()["world_epoch"]
    raw = store.meta(STATE)
    state = _snapshot(raw, epoch)
    candidates = []
    for table, op, cursor in (("books_events", "read", "last_read_revision"),
                              ("rhythm_events", "sleep", "last_sleep_revision")):
        found = _next_event(bridge, table, state[cursor], op)
        if found is not None:
            candidates.append((found[2]["created_tick"], op, cursor, found))
    if not candidates:
        return None
    _, op, cursor, (revision, digest, memory) = min(candidates, key=lambda item: item[0])
    seed = int(digest[:15], 16)
    day = state["nights"] + 1
    request = {"pin": DONOR_SHA256, "files": state["files"], "day": day,
               "seed": seed, "cues": [memory["text"][:2000]],
               "op": "night" if op == "sleep" else "fancy"}
    if op == "sleep":
        # Only actual preceding source-acquired waking experiences, never
        # hidden world state, fantasy, operator testimony or another mind.
        before = memory["created_tick"]
        with closing(store.connect()) as db:
            cues = db.execute(
                "SELECT text FROM memories WHERE active=1 AND external=0 "
                "AND evidence_class='lived_runtime_memory' "
                "AND source LIKE 'laboratory-home:action:%' AND created_tick<? "
                "ORDER BY created_tick DESC LIMIT 5", (before,)).fetchall()
        request["cues"] = [r["text"][:1000] for r in reversed(cues)] + request["cues"]
    else:
        # Explicit creative ingredients, not an assertion about reality.
        # The two entities derive from the actually experienced page.
        excerpt = memory["text"].split("The words before me read: ", 1)[-1][:120]
        request["scene"] = {"initial_scene": {"entities": [
            {"id": "book", "kind": "book", "properties": {"form": "bound volume"}},
            {"id": "page", "kind": "page", "properties": {"words": excerpt}},
        ], "relations": []}, "max_fragments": 4}
    output = _run(archive, request)
    result, recall = output["result"], output["recall"]
    if not _nonfactual(result, "dreamed_not_lived" if op == "sleep" else "hypothetical_only"):
        raise PermissionError("Original donor omitted fictional provenance")
    text = None
    motifs = ()
    if op == "sleep":
        if not _nonfactual(recall, "dreamed_not_lived") or type(recall.get("has_recollection")) is not bool:
            raise PermissionError("Unmarked dream recollection")
        if recall["has_recollection"]:
            text = recall["text"]
            if (type(text) is not str or not text.startswith("I recall a dream: ")
                    or len(text) > 800):
                raise PermissionError("Unmarked or unbounded dream text")
            from .phenomenology import implementation_leaks, control_instruction_markers
            if implementation_leaks(text) or control_instruction_markers(text):
                raise PermissionError("Dream text cannot cross subject boundary")
    else:
        from .tower_phantasmagorium import verified_fancy_motifs
        motifs = verified_fancy_motifs(result)
    updated = dict(state, files=output["files"])
    updated[cursor] = revision
    if op == "sleep":
        updated["nights"] = day
    envelope = {"payload": updated, "sha256": _digest(updated)}
    key = "phantasmagorium:event:" + digest
    report = {"source_sha256": digest, "source_memory_id": memory["id"],
              "donor_sha256": DONOR_SHA256, "operation": request["op"],
              "sleep_index": updated["nights"], "fictional_result_sha256": _digest(result),
              "recollection_memory_id": None, "world_authority": False,
              "factual_memory_eligible": False, "motor_authority": False,
              "fragment_count": len(result.get("fragments", [])),
              "fictional_motifs": list(motifs)}
    if text or motifs:
        from .tower_ipseity import TowerIpseity
        from .phenomenology import PhenomenalMode, SubjectiveSourceKind
        subject = TowerIpseity(brain)
        subject_digest = store.digest()
    with store.transaction() as db:
        existing = db.execute("SELECT value FROM meta WHERE key=?", (STATE,)).fetchone()
        if (existing["value"] if existing else None) != raw:
            raise RuntimeError("Concurrent original Phantasmagorium update")
        if db.execute("SELECT 1 FROM meta WHERE key=?", (key,)).fetchone():
            raise RuntimeError("Duplicate donor source event")
        if text:
            # Nonfactual experience, external=True conservatively excludes
            # it from all existing verified-lived authority checks.
            mid = store.add_memory(
                db, store.tick, text, SOURCE + digest, "dream_recollection",
                "dreamed_not_lived", True, 1.0, False, .35,
                tags=("dream", "fictional", "nonfactual"),
            )
            report["recollection_memory_id"] = mid
            # Match the existing Tower donor ownership boundary: the memory,
            # original source lineage and admission commit atomically, before
            # any later policy/recurrent consumer can access the dream text.
        if text or motifs:
            events = []
            if text:
                events.append(subject.event("Phantasmagorium", text, PhenomenalMode.RECOLLECTION,
                                            (memory["id"], mid),
                                            attribution=SubjectiveSourceKind.DREAMED,
                                            external=True, digest=subject_digest))
            for motif in motifs:
                events.append(subject.event("Phantasmagorium", fancy_line(motif),
                                            PhenomenalMode.INTERNAL_THOUGHT, (memory["id"],),
                                            attribution=SubjectiveSourceKind.IMAGINED,
                                            external=True, digest=subject_digest))
            admission = subject.record(db, "imagination:" + digest, events,
                                       phase="imagination")
            report["ipseity_admission_sha256"] = admission["sha256"]
        store.set_meta(STATE, _stable(envelope), db)
        store.set_meta(key, _stable(report), db)
        store.bump_state_version(db)
    return report


def fancy_line(motif):
    return "I imagine " + motif.rstrip(".") + ", without taking it for something I witnessed."


def owned_imagination_report(store, digest, report, expected_content):
    """Match the committed original admission, never mint history on retrieval.

    Historical unowned reports stay available for engineering inspection.
    The existing full history verifier remains the continuity audit; this
    bounded lookup avoids replaying the entire history on every retrieval.
    """
    from .tower_ipseity import RECORD, _digest as history_digest
    key = RECORD + "imagination:" + digest
    raw = store.meta(key)
    if not raw or not report.get("ipseity_admission_sha256"):
        return False
    try:
        entry = json.loads(raw)
        payload = {k: v for k, v in entry.items() if k != "sha256"}
        return (entry["key"] == key and entry["subject"] == "pretorius"
                and entry["phase"] == "imagination"
                and entry["sha256"] == report["ipseity_admission_sha256"]
                and entry["sha256"] == history_digest(payload)
                and entry["content"] == expected_content)
    except (ValueError, TypeError, KeyError, AttributeError):
        return False


def owned_dream_memory(store, row):
    """A donor dream may be recalled only with its original owned source."""
    if (row.get("kind") != "dream_recollection"
            and row.get("evidence_class") != "dreamed_not_lived"
            and not row.get("source", "").startswith(SOURCE)):
        return True
    if (row.get("kind") != "dream_recollection"
            or row.get("evidence_class") != "dreamed_not_lived"
            or not row.get("active") or not row.get("external")
            or not row.get("source", "").startswith(SOURCE)):
        return False
    digest = row["source"][len(SOURCE):]
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        return False
    for prefix in ("phantasmagorium:event:", "phantasmagorium:tower-event:"):
        raw = store.meta(prefix + digest)
        if not raw:
            continue
        try:
            report = json.loads(raw)
            if (report["source_sha256"] != digest or report["operation"] != "night"
                    or report["donor_sha256"] != DONOR_SHA256
                    or report["recollection_memory_id"] != row["id"]
                    or any(report[k] is not False for k in
                           ("world_authority", "factual_memory_eligible", "motor_authority"))):
                continue
            source = store.get_memory(report["source_memory_id"])
            if (not source or not source["active"] or source["external"]
                    or source["evidence_class"] != "lived_runtime_memory"):
                continue
            if prefix == "phantasmagorium:event:":
                if source["source"] != "laboratory-home:action:" + digest:
                    continue
            elif (not source["source"].startswith("virtual-world:small-tower:")
                    or ":action:" not in source["source"]
                    or sha256(source["source"].encode()).hexdigest() != digest
                    or not source.get("source_event_id")
                    or source["source_event_id"] != report.get("source_event_id")):
                continue
            expected = [{"organ": "Phantasmagorium", "text": row["text"],
                         "mode": "recollection", "attribution": "dreamed",
                         "source_refs": [source["id"], row["id"]], "external": True}]
            if owned_imagination_report(store, digest, report, expected):
                return True
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
    return False
