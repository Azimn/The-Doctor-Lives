"""Pinned Sensus binding of the actual Tower's admitted semantic perception.

Only source-admitted lines enter the original binder. Working object files
and the exact scene receipt persist inside BrainStore. A missing channel is
not fabricated; this is semantic perception, not camera or microphone input.
"""
from dataclasses import asdict
from hashlib import sha256
from importlib import import_module
import json

from .canonical_affectus_weather import load_reviewed_weather
from .tower_affectus import DONOR

STATE = "sensus:tower-working-files:v1"
CHANNELS = ("vision", "interoception", "spatial", "hearing")


def _stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return sha256(_stable(value).encode()).hexdigest()


def _core():
    load_reviewed_weather(DONOR)
    return import_module("pretorius_reviewed_weather_donor.core")


def _line_spec(line):
    bodily = (
        ("I am painfully hungry.", "hunger"),
        ("I could do with something to eat.", "hunger"),
        ("I feel worn out and find it hard to concentrate.", "fatigue"),
        ("I am getting tired.", "fatigue"),
        ("I feel uncomfortable.", "comfort"),
        ("I find the solitude wearing.", "affiliation"),
        ("I long for something to occupy my mind.", "stimulation"),
    )
    for phrase, attribute in bodily:
        if line == phrase:
            return "interoception", attribute, "body", (("type", "body"),)
    if line.startswith("I am in my "):
        return "spatial", "location", "room", (("type", "room"), ("label", line))
    if line.startswith("I can make my way to my "):
        return "spatial", "adjacent_route", line, (("type", "route"), ("label", line))
    if line.startswith(("I can see ", "I see ")):
        return "vision", "appearance", line, (("type", "visible"), ("label", line))
    if line.startswith("I heard "):
        return "hearing", "sound", line, (("type", "sound"), ("label", line))
    return "spatial", "situated_context", line, (("type", "context"), ("label", line))


def bind_scene(runtime, provider, snapshot, receipt, memory_id, weather):
    """Return bound, uncontested source lines for the original Noesis decision."""
    from .small_tower import SmallTowerSource
    from .virtual_world_port import VirtualWorldReceipt
    if (type(provider) is not SmallTowerSource or type(receipt) is not VirtualWorldReceipt
            or receipt.kind != "observation" or provider._observation(snapshot) != receipt
            or not provider.verify_receipt(receipt)):
        raise PermissionError("Original current Tower perception required for Sensus")
    store = runtime._port.brain.store
    memory = store.get_memory(memory_id)
    source = ("virtual-world:small-tower:" + receipt.world_epoch
              + ":observation:" + receipt.event_id)
    if (not memory or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or memory["source"] != source or memory["text"] != receipt.first_person
            or not memory.get("source_event_id")):
        raise PermissionError("Sensus requires exact canonical admitted experience")
    lines = []
    for line in snapshot["narrative"]:
        if len(" ".join(lines + [line])) > len(receipt.first_person):
            break
        lines.append(line)
    if " ".join(lines) != receipt.first_person or not lines:
        raise PermissionError("Unadmitted Tower scene text")
    key = "sensus:tower-scene:" + sha256(source.encode()).hexdigest()
    existing = store.meta(key)
    if existing is not None:
        prior = json.loads(existing)
        if prior["source_memory_id"] != memory_id or prior["source"] != source:
            raise PermissionError("Conflicting Tower scene replay")
        return prior
    core = _core()
    binder = core.Sensus(core.SensusConfig(expected_channels=CHANNELS))
    raw = store.meta(STATE)
    if raw is not None:
        envelope = json.loads(raw)
        state = envelope["payload"]
        if envelope["sha256"] != _digest(state) or state["epoch"] != receipt.world_epoch:
            raise PermissionError("Corrupt or foreign Sensus working state")
        binder._last_tick = state["last_tick"]
        binder._next_id = state["next_id"]
        binder._files = {r["object_id"]: core.ObjectFile(
            r["object_id"], tuple(tuple(pair) for pair in r["features"]),
            r["last_seen_tick"]) for r in state["files"]}
    tick = binder._last_tick + 1
    confidence = max(.5, min(1., .8 * weather.modulation().salience_gain))
    items = []
    for i, line in enumerate(lines):
        channel, attr, hint, features = _line_spec(line)
        evidence = core.Evidence.INTEROCEPTIVE if channel == "interoception" else core.Evidence.OBSERVED
        items.append(core.Percept(
            event_id="tower-scene-" + str(tick) + "-" + str(i),
            channel=channel, evidence=evidence, source_ref=source, tick=tick,
            attribute=attr, value=line, confidence=confidence, object_hint=hint,
            features=features))
    scene = binder.step(tick, tuple(items))
    withheld = {claim.event_id for obj in scene.objects for claim in obj.claims
                if claim.attribute in obj.contested_attributes}
    admitted = [item.value for item in items if item.event_id not in withheld]
    state = {"epoch": receipt.world_epoch, "last_tick": binder._last_tick,
             "next_id": binder._next_id,
             "files": [asdict(item) for item in binder.recent_object_files]}
    report = {"schema": scene.schema_version, "tick": tick, "source": source,
              "source_memory_id": memory_id, "source_event_id": memory["source_event_id"],
              "channels": sorted({p.channel for p in items}),
              "absent_channels": list(scene.absent_channels),
              "conflicts": [asdict(conflict) for conflict in scene.conflicts],
              "admitted_lines": admitted, "withheld_claim_ids": sorted(withheld),
              "object_count": len(scene.objects), "confidence": confidence,
              "working_state_sha256": _digest(state), "world_authority": False}
    with store.transaction() as db:
        before = db.execute("SELECT value FROM meta WHERE key=?", (STATE,)).fetchone()
        if (before["value"] if before else None) != raw:
            raise RuntimeError("Concurrent Sensus scene writer")
        if db.execute("SELECT 1 FROM meta WHERE key=?", (key,)).fetchone():
            raise RuntimeError("Duplicate Sensus scene")
        store.set_meta(STATE, _stable({"payload": state, "sha256": _digest(state)}), db)
        store.set_meta(key, _stable(report), db)
        store.bump_state_version(db)
    return report
