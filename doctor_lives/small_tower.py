"""One canonical Doctor on the original Small Tower physical world.

No Tower decision engine is invoked in doctor_world mode. Node verifies its
own original save, supplies current percepts and physical offers, and executes
one bounded original Noesis choice. All source hashes and action bindings are
host-only. Existing Laboratory saves are not silently migrated.
"""
from __future__ import annotations
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from contextlib import closing

from .virtual_world_port import VirtualWorldReceipt, VirtualWorldEnvironmentPort
from .first_person_governance import first_person_line
from .phenomenology import implementation_leaks, control_instruction_markers

PIN = "2e2ffb0658dea77da4b6cece1b783ad236bf30ff"
MANIFEST = Path(__file__).with_name("data") / "small_tower_source.json"
BINDING = "small-tower:world-binding-v1"
CURSOR = "small-tower:source-cursor-v1"
PENDING = "small-tower:pending-world-request-v1"
BACKGROUND_CLOCK = "small-tower:background-clock-v1"
DEFAULT_BACKGROUND_EVERY_TICKS = 100
MAP = {
    "sleep":"avoid", "rest":"avoid", "eat":"avoid", "cook":"persist",
    "tea":"persist", "prepare":"persist", "diary":"create", "read":"explore",
    "work":"create", "inspect":"explore", "study":"explore", "walk":"explore",
    "tend":"persist", "gather_fuel":"persist", "draw_water":"persist",
    "converse":"approach", "trade":"cooperate", "settle_account":"cooperate",
    "meet_carrier":"approach", "check_mail":"explore", "read_letter":"explore",
    "write_reply":"create", "post_reply":"persist", "open_parcel":"explore",
    "preserve":"persist",
    "move_bedchamber":"avoid", "move_library":"explore", "move_kitchen":"persist",
    "move_laboratory":"create", "move_garden":"explore",
}
VALENCE = {"greeting":.15, "conversation":.20, "trade":.25,
           "negotiation":.10, "friction":-.40, "insult":-.60, "gift":.35}


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode()).hexdigest()


def verify_source(root):
    root = Path(root).resolve(strict=True)
    pinned = json.loads(MANIFEST.read_text("utf-8"))
    if pinned["commit"] != PIN:
        raise PermissionError("Unexpected Small Tower source specification")
    for name, digest in pinned["files"].items():
        file = root / name
        if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(root):
            raise PermissionError("Missing or linked pinned Tower source: " + name)
        data = file.read_bytes()
        if sha1(("blob " + str(len(data)) + "\0").encode() + data).hexdigest() != digest:
            raise PermissionError("Changed pinned Tower source: " + name)
    return root


class SmallTowerSource:
    world_id = "small-tower"

    def __init__(self, root, world):
        self.root = verify_source(root)
        self.world = Path(world).resolve()
        self.node = shutil.which("node")
        if not self.node:
            raise RuntimeError("Node.js 20+ required for original Small Tower")
        self.world_epoch = None

    def _invoke(self, request):
        # Recheck all code and canonical archive on every subprocess. Only
        # the exact fixed local entrypoint runs, no arbitrary executable args.
        verify_source(self.root)
        env = dict(os.environ)
        for key in ("NODE_OPTIONS", "NODE_PATH"):
            env.pop(key, None)
        proc = subprocess.run([self.node, str(self.root / "src/doctor_world_cli.js"), str(self.world)],
            input=json.dumps(request,sort_keys=True), capture_output=True, text=True,
            encoding="utf-8", timeout=60, cwd=self.root, env=env)
        if proc.returncode:
            raise RuntimeError("Original Small Tower port failed: " + proc.stderr[-400:])
        if len(proc.stdout.encode()) > 16_000_000:
            raise ValueError("Small Tower source response exceeds bound")
        return json.loads(proc.stdout)

    def initialize(self, epoch):
        if self.world.exists():
            raise FileExistsError("Existing Tower cannot be silently reenrolled")
        data = self._invoke({"op":"init","epoch":epoch})
        self.world_epoch = data["epoch"]
        return data

    def snapshot(self, after=0):
        value = self._invoke({"op":"observe","after":after})
        if value.get("schema") != "simple-tower-doctor-world-v1":
            raise PermissionError("Unexpected original world port")
        if self.world_epoch is not None and value["epoch"] != self.world_epoch:
            raise PermissionError("Tower epoch changed")
        self.world_epoch = value["epoch"]
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,63}", self.world_epoch):
            raise PermissionError("Invalid Tower epoch")
        if any(type(line) is not str or first_person_line(line) != line
               for line in value["narrative"]):
            raise PermissionError("Unsafe subjective Tower perception")
        return value

    def _observation(self, snapshot):
        # Whole lines only; no truncation of a quoted source statement.
        lines = []
        for line in snapshot["narrative"]:
            if len(" ".join(lines + [line])) > 500:
                break
            lines.append(line)
        text = " ".join(lines)
        return VirtualWorldReceipt(self.world_id, self.world_epoch,
                                   snapshot["revision"][:48], "observation", text)

    def observe(self):
        return self._observation(self.snapshot())

    def event_receipt(self, row):
        text = row["text"]
        if (len(text)>500 or implementation_leaks(text) or control_instruction_markers(text)):
            raise PermissionError("Unsafe or oversized Tower source event")
        kind = "action" if row["kind"]=="completed" else "observation"
        event_id = row["id"] + "-" + row["sha256"][:32]
        actor = row["actor"] if row["kind"] in ("social","visitor_conversation",
                   "carrier_conversation","letter_read","merchant_settlement") else None
        social_kind = ("communication" if row["kind"]=="letter_read" else "social") if actor else None
        # Observed social act supplies the signal, not Tower's private
        # relationship counters or another actor's beliefs.
        return VirtualWorldReceipt(self.world_id, self.world_epoch, event_id, kind, text,
            row["operation"] if kind=="action" else "", True, actor,
            VALENCE.get(row["socialKind"], 0.0) if actor else 0.0, social_kind)

    def verify_receipt(self, receipt):
        if type(receipt) is not VirtualWorldReceipt or receipt.world_id != self.world_id:
            return False
        if re.fullmatch(r"[a-f0-9]{48}", receipt.event_id):
            return self.observe()==receipt
        match = re.fullmatch(r"L([0-9]+)-[a-f0-9]{32}", receipt.event_id)
        if not match:
            return False
        for row in self.snapshot(int(match.group(1))-1)["events"]:
            if row["id"]=="L"+match.group(1):
                return self.event_receipt(row)==receipt
        return False

    def act(self, op, *, event_id, **args):
        # The actual canonical host uses its own durable original policy
        # reservation below; generic world-port callers cannot command it.
        raise PermissionError("Tower motor requires the canonical Noesis reservation")

    def pulse(self, request):
        return self._invoke({"op":"pulse","request":request})


def _bind(runtime, provider, snapshot):
    store = runtime._port.brain.store
    expected = json.dumps({"epoch":snapshot["epoch"],"source":PIN},sort_keys=True)
    existing = store.meta(BINDING)
    if existing is not None:
        if existing != expected:
            raise PermissionError("Canonical Doctor already bound to another Tower")
        return
    if any(m["source"].startswith(("laboratory-home:", "virtual-world:"))
           for m in store.memories(False)):
        raise PermissionError("Existing embodied history needs an explicit world migration rehearsal")
    with store.transaction() as db:
        store.set_meta(BINDING, expected, db)
        store.bump_state_version(db)


def _admit_events(runtime, provider, port):
    store = runtime._port.brain.store
    cursor = int(store.meta(CURSOR) or 0)
    snapshot = provider.snapshot(cursor)
    for row in snapshot["events"]:
        receipt = provider.event_receipt(row)
        port._admit(receipt, kind=receipt.kind)
    with store.transaction() as db:
        store.set_meta(CURSOR, snapshot["cursor"], db)
        store.bump_state_version(db)
    return snapshot


def _choose(runtime, snapshot, observation_id):
    brain = runtime._port.brain
    offers = snapshot["offers"]
    if not offers:
        return None, None
    if any(o["key"] not in MAP or first_person_line(o["text"]) != o["text"] for o in offers):
        raise PermissionError("Unexpected or unsafe physical offer")
    # The adapter translates physical cues only. Original Noesis owns
    # concrete competition and the canonical policy/thought record.
    text = " ".join(snapshot["narrative"])
    # Reviewed bounded physical cues, not hidden store quantities.
    pressure = {}
    if "I am painfully hungry." in text or "I could do with something to eat." in text:
        amount = .20 if "painfully hungry" in text else .09
        for key in ("eat","cook","move_kitchen"):
            pressure[key]=amount
        if ("I am in my bedchamber." in text or "I am in my laboratory." in text):
            pressure["move_library"]=amount
    if "I feel worn out" in text or "I am getting tired." in text:
        amount=.20 if "worn out" in text else .09
        for key in ("rest","sleep","move_bedchamber"):
            pressure[key]=amount
        if "I am in my kitchen" in text or "I am in my laboratory." in text:
            pressure["move_library"]=max(amount,pressure.get("move_library",0))
    if "provisions are running low" in text:
        pressure["move_garden"]=.18
        pressure["trade"]=.12
    if "fuel is running low" in text or "water is running low" in text:
        pressure["move_garden"]=.16
        pressure["trade"]=.14
    if "I see Rosa Brandl here" in text:
        pressure["converse"]=.10
        pressure["settle_account"]=.12
    if "I see Mr. McFeely" in text:
        pressure["meet_carrier"]=.12
        pressure["check_mail"]=.08
    from .noesis_situated_choice import select_world_affordance
    observation_source = ("virtual-world:small-tower:" + snapshot["epoch"]
                          + ":observation:" + snapshot["revision"][:48])
    decision = select_world_affordance(
        brain, observation_memory_id=observation_id, observation_source=observation_source,
        narrative=snapshot["narrative"], offers=offers, affordance_map=MAP,
        regulatory_pressure=pressure)
    choice, scores = decision["selected_action"], decision["action_scores"]
    with brain.store.transaction() as db:
        brain.store.set_meta("small-tower:choice:"+decision["policy_decision_id"],
            json.dumps({"revision":snapshot["revision"],"choice":choice,
                        "offers":sorted(scores),"scores":scores,"observation_id":observation_id,
                        "host_mapped_abstract_tendency":False,
                        "abstract_policy_id":decision["abstract_policy_id"],
                        "selector_authority":"original_noesis"},sort_keys=True),db)
        brain.store.bump_state_version(db)
    return choice,decision["policy_decision_id"]


def _background_clock(store):
    """Canonical operational watermark, not a new cognitive state."""
    raw = store.meta(BACKGROUND_CLOCK)
    if raw is None:
        return {"source_ticks": 0, "since_wake": 0, "pending_wake": None}
    clock = json.loads(raw)
    if (set(clock) != {"source_ticks", "since_wake", "pending_wake"}
            or type(clock["source_ticks"]) is not int
            or type(clock["since_wake"]) is not int
            or not 0 <= clock["since_wake"] <= clock["source_ticks"]
            or (clock["pending_wake"] is not None
                and (type(clock["pending_wake"]) is not str
                     or not clock["pending_wake"].startswith("tower:")))):
        raise RuntimeError("Invalid canonical Tower background clock")
    return clock


def _write_background_clock(store, clock, db):
    store.set_meta(BACKGROUND_CLOCK, json.dumps(clock, sort_keys=True), db)


def _reconcile_background_clock(state, store):
    clock = _background_clock(store)
    wake_id = clock["pending_wake"]
    if wake_id is None:
        return clock
    # A completed ledger receipt is authoritative even if the host died
    # before acknowledging it in BrainStore. An absent reservation means
    # cognition never started; carry the source debt into the next boundary.
    from .cascade_background import BackgroundLedger
    ledger = BackgroundLedger(state)
    ledger.assert_reconciled()
    with ledger.connect() as db:
        row = db.execute("SELECT status,receipt FROM wakes WHERE id=?", (wake_id,)).fetchone()
    if row is not None:
        if row["status"] != "completed" or not row["receipt"]:
            raise RuntimeError("Unresolved Tower background wake")
        receipt = json.loads(row["receipt"])
        if (receipt.get("schema") != "canonical-cascade-wake-v1"
                or receipt.get("wake_id") != wake_id):
            raise RuntimeError("Invalid Tower background wake receipt")
        clock["since_wake"] = 0
    clock["pending_wake"] = None
    with store.transaction() as db:
        _write_background_clock(store, clock, db)
        store.bump_state_version(db)
    return clock


def run_tower_pulse(state, source, world, *, authorize=False, steps=100,
                    _background_lease=None, _background_every_ticks=0):
    """One original cognitive opportunity or continuation of an active action."""
    from .lab_runtime import _exclusive_host
    from .organs import SixOrganRuntime
    if authorize is not True or type(steps) is not int or not 1<=steps<=1000:
        raise PermissionError("Explicit bounded canonical world authorization required")
    state=Path(state)
    if not (state/"brain.sqlite3").is_file() or not Path(world).is_file():
        raise FileNotFoundError("Initialize a dedicated canonical Tower rehearsal first")
    from .local_turn_journal import LocalTurnJournal
    from .canonical_background import assert_no_pending_conversation
    with _exclusive_host(state,Path(world)),LocalTurnJournal(state) as journal:
        runtime=SixOrganRuntime.open(state)
        assert_no_pending_conversation(state,runtime,journal)
        # A failed or interrupted background wake must be reconciled rather
        # than hidden by continuing ordinary life on a changed brain.
        if (state/"cascade-operations.sqlite3").exists():
            from .cascade_background import BackgroundLedger
            BackgroundLedger(state).assert_reconciled()
        provider=SmallTowerSource(source,world)
        snapshot=provider.snapshot()
        _bind(runtime,provider,snapshot)
        port=VirtualWorldEnvironmentPort(runtime,provider,authorized=True)
        store=runtime._port.brain.store
        clock = _reconcile_background_clock(state, store)
        raw=store.meta(PENDING)
        if raw:
            request=json.loads(raw)
        else:
            snapshot=_admit_events(runtime,provider,port)
            if snapshot["deceased"]:
                raise RuntimeError("The original Tower inhabitant is deceased")
            if snapshot["busy"]:
                choice,policy=None,None
            else:
                perceived=port._admit(provider._observation(snapshot),kind="observation")
                choice,policy=_choose(runtime,snapshot,perceived.memory_id)
            from .store import new_id
            request={"id":new_id("tower"),"revision":snapshot["revision"],
                     "choice":choice,"policyRef":policy,"steps":steps}
            with store.transaction() as db:
                store.set_meta(PENDING,json.dumps(request,sort_keys=True),db)
                store.bump_state_version(db)
        result=provider.pulse(request)
        snapshot=_admit_events(runtime,provider,port)
        elapsed = result["elapsed"]
        if (result["requestId"] != request["id"] or type(elapsed) is not int
                or not 0 <= elapsed <= request["steps"]):
            raise RuntimeError("Invalid Tower source clock receipt")
        # A replay here means the source committed but the canonical pending
        # request was not acknowledged. Count it once in the same transaction
        # that clears that request, including after a cold restart.
        clock["source_ticks"] += elapsed
        clock["since_wake"] += elapsed
        due = (_background_lease is not None
               and _background_every_ticks > 0
               and not result["replayed"] and not result["busy"]
               and not result["deceased"]
               and clock["since_wake"] >= _background_every_ticks)
        if due:
            clock["pending_wake"] = "tower:" + request["id"]
        with store.transaction() as db:
            store.set_meta("small-tower:receipt:"+request["id"],json.dumps(result,sort_keys=True),db)
            _write_background_clock(store, clock, db)
            db.execute("DELETE FROM meta WHERE key=?",(PENDING,))
            store.bump_state_version(db)
        runtime.checkpoint()
        background = None
        if due:
            # Same brain, same host lease. Physical time does not advance
            # during this private wake. Source receipt is already durable.
            import time
            from .canonical_background import _wake_locked
            background = _wake_locked(
                state, runtime, journal, lease_id=_background_lease,
                wake_id="tower:"+request["id"], now_ms=time.time_ns()//1_000_000,
                ticks=1)
            clock = _reconcile_background_clock(state, store)
        return {"schema":"doctor-small-tower-pulse.v1","world_epoch":provider.world_epoch,
                "policy_id":request["policyRef"],"choice":request["choice"],
                "source_receipt":result,"subject_narrative":snapshot["narrative"],
                "background_receipt":background,
                "background_clock":clock,
                "same_canonical_brain":True,"parallel_tower_chooser":False}


def initialize_tower(state, source, world, *, epoch, neural_config=None):
    from .lab_runtime import _exclusive_host
    from .organs import SixOrganRuntime
    state=Path(state)
    if state.exists() or Path(world).exists():
        raise FileExistsError("Use new dedicated rehearsal paths; no live migration")
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,63}",epoch):
        raise ValueError("Bounded new Tower epoch required")
    state.mkdir(parents=True)
    with _exclusive_host(state):
        runtime=SixOrganRuntime.open(state, neural_config=neural_config)
        provider=SmallTowerSource(source,world)
        snapshot=provider.initialize(epoch)
        _bind(runtime,provider,snapshot)
        runtime.checkpoint()
        return {"schema":"doctor-small-tower-init.v1","world_epoch":epoch,
                "subject_narrative":snapshot["narrative"],"new_rehearsal":True}


def run_tower_life(state, source, world, *, authorize=False, opportunities=20,
                   steps=100, interval_seconds=0.0,
                   background_every_ticks=DEFAULT_BACKGROUND_EVERY_TICKS):
    """Run bounded, unprompted physical opportunities using the same host.

    No chosen goal, room, or action is supplied by this runner. Each pulse
    persists before the next; a reserved request is recovered by the existing
    bridge. A stopped process grants no authority to simulate downtime.
    The counts are actual source ticks, not hours or elapsed wall time.
    Background cognition participates by default; zero is an explicit research control.
    """
    import math
    import time
    if authorize is not True:
        raise PermissionError("Explicit bounded canonical world authorization required")
    if type(opportunities) is not int or not 1 <= opportunities <= 1000:
        raise ValueError("Opportunities must be an integer from 1 to 1000")
    if type(steps) is not int or not 1 <= steps <= 1000:
        raise ValueError("Steps must be an integer from 1 to 1000")
    if (type(interval_seconds) not in (int, float)
            or not math.isfinite(interval_seconds) or not 0 <= interval_seconds <= 60):
        raise ValueError("Interval must be finite and between 0 and 60 seconds")
    if type(background_every_ticks) is not int or not 0 <= background_every_ticks <= 100000:
        raise ValueError("Background source-tick interval must be 0 to 100000")
    # This is a bounded foreground scheduler. Lease timestamps are real
    # host time; eligibility is accumulated actual source ticks, not a claim
    # that cognitive ticks equal physical time. No wake on an unfinished
    # activity or replayed receipt. A stopped run does not invent downtime.
    from .canonical_background import BackgroundLease, issue, revoke
    from .store import new_id
    lease_id = None
    if background_every_ticks:
        lease_id = new_id("tower-life")
        issue(state, BackgroundLease(lease_id, opportunities, 1, 1,
              time.time_ns()//1_000_000 + 86_400_000), authorized=True)
    started = time.monotonic()
    pulses = []
    background_receipts = []
    status = "budget_complete"
    try:
        for index in range(opportunities):
            result = run_tower_pulse(
                state, source, world, authorize=True, steps=steps,
                _background_lease=lease_id,
                _background_every_ticks=background_every_ticks)
            receipt = result["source_receipt"]
            pulses.append({"request_id": receipt["requestId"],
                           "policy_id": result["policy_id"], "choice": result["choice"],
                           "source_ticks": receipt["elapsed"],
                           "source_cursor": receipt["cursor"], "replayed": receipt["replayed"],
                           "busy": receipt["busy"], "deceased": receipt["deceased"]})
            background = result["background_receipt"]
            if background is not None:
                background_receipts.append(background)
            if receipt["deceased"]:
                status = "deceased"
                break
            if interval_seconds and index + 1 < opportunities:
                time.sleep(interval_seconds)
    finally:
        if lease_id is not None:
            revoke(state, lease_id, authorized=True)
    return {"schema": "doctor-small-tower-life.v1", "status": status,
            "opportunities_completed": len(pulses),
            "new_source_ticks": sum(p["source_ticks"] for p in pulses if not p["replayed"]),
            "recovered_source_ticks": sum(p["source_ticks"] for p in pulses if p["replayed"]),
            "wall_seconds": time.monotonic() - started,
            "pulses": pulses, "background_receipts": background_receipts,
            "background_every_source_ticks": background_every_ticks,
            "background_clock": result["background_clock"],
            "engineer_only": True,
            "operator_supplied_goals": False}
