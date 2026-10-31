"""Bounded experimental Laboratory cycle across all SIX canonical organ ports.

NOT a production entrypoint or a claim of globally enforced model sandbox.
The user-facing callback ONLY receives durable, first-person Ipseity output.
Physical world authority is exclusively the pinned Laboratory SubjectPort.
All weather continuation belongs to the same canonical BrainStore. This host
may propose a destination based on the original recurrent selected tendency,
but the Laboratory independently authorizes and verifies every movement.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Callable
from unittest.mock import patch

from .canonical_affectus_weather import CanonicalWeather
from .noesis_corpus_pilot import HostCorpusOffer
from .organs import CognitiveProposal
from .organs import SixOrganRuntime

_G = 0.05  # Preserved, PREDECLARED PR #90 experimental coupling. No tuning.
_VALID = {
    "station:threshold": "threshold", "station:hall": "hall",
    "station:center": "center", "station:kitchen": "kitchen",
    "station:bedroom": "bedroom", "station:parlor": "parlor",
    "station:shop:private": "private shop",
    "station:shop:public": "public shop",
    "station:shelf:1": "shelf one", "station:shelf:2": "shelf two",
    "station:shelf:3": "shelf three", "station:bench": "bench",
    "station:corner:nw": "northwest corner",
    "station:corner:se": "southeast corner",
    "station:chamber:entry": "chamber entrance",
    "station:chamber:table": "chamber table",
}


@dataclass(frozen=True)
class SixOrganCycleReceipt:
    tick: int
    ports_used: tuple[str, ...]
    scene_admitted: int
    scene_vetoed: tuple[str, ...]
    body_verified: bool
    canonical_weather_digest: str
    mnemonic_decision: str
    selected_tendency: str
    movement_status: str
    destination: str | None
    subjective_delivery_count: int
    host_provided_goal: bool
    self_selected_goal_proven: bool


@contextmanager
def original_noesis_weather(organ, modulation):
    """Apply bounded exploration and memory-retention weather to original Noesis.

    The only decision authority remains PretoriusBrain.think. Neither this
    temporary read-time weighting nor the caller can author a goal or source.
    """
    brain = organ._port.brain
    original = brain._state_policy_scores
    original_salience = brain._salience

    def weather_salience(row, now_tick, terms):
        # Retention affects only READ-TIME relative memory relevance.
        # Never erase, rewrite or promote an unverified experience.
        age = max(0, now_tick - int(row["updated_tick"]))
        age_weight = min(1.0, age / 12.0)
        multiplier = 1.0 + _G * (1.0 - modulation.decay_multiplier) * age_weight
        return max(0.0, original_salience(row, now_tick, terms) * multiplier)

    def adjusted(*args, **kwargs):
        base, scores, audit = original(*args, **kwargs)
        delta = _G * modulation.exploration_bias
        changed = dict(scores)
        changed["explore"] = max(1e-9, changed["explore"] + delta)
        changed["persist"] = max(1e-9, changed["persist"] - delta)
        norm = sum(changed.values())
        changed = {key: value / norm for key, value in changed.items()}
        audit = dict(audit)
        audit["lab_experiment_weather"] = {
            "modulation_consumed": ("exploration_bias", "decay_multiplier"),
            "exploration_delta": delta,
            "relative_memory_retention": modulation.decay_multiplier,
            "not_subject_visible": True,
        }
        return base, changed, audit

    with patch.object(brain, "_salience", side_effect=weather_salience):
        with patch.object(brain, "_state_policy_scores", side_effect=adjusted):
            yield


class SixOrganLaboratoryCycle:
    """Single-brain research host with all six ports invoked each cycle.

    No task text, action target or engineer diagnostic is sent to the
    renderer. The first-person gate is the ONLY callback destination.
    """

    def __init__(self, runtime: SixOrganRuntime, subject_port, *,
                 affectus_source: str | Path, renderer: Callable[[str], str],
                 authorized: bool = False, seed: int = 1842):
        if not isinstance(runtime, SixOrganRuntime) or authorized is not True:
            raise PermissionError("Explicit same-brain research host authorization")
        if not callable(renderer):
            raise TypeError("Renderer must be a callback accepting subject text")
        self.runtime = runtime
        self.subject = subject_port
        self.bridge = runtime.bind_laboratory(subject_port, authorized=True)
        self.corpus = runtime.bind_causal_laboratory(
            subject_port, authorized=True
        )
        self.affect = runtime.affectus.opt_in_laboratory_body_evidence(
            runtime, subject_port, authorized=True,
        )
        self.sensus = runtime.sensus.opt_in_multichannel_pilot()
        self.mnemosyne = runtime.mnemosyne.opt_in_endogenous_recollection()
        self.weather = CanonicalWeather(
            runtime._port, donor_root=affectus_source, seed=seed,
        )
        self.ipseity = runtime.synthetic_ipseity.open_durable_delivery(
            renderer=renderer,
        )
        # Recover a world action that committed before brain admission,
        # once the SAME original brain/weather is reopened from its store.
        self._reconcile_pending()
        if len({
            id(runtime.noesis._port), id(runtime.mnemosyne._port),
            id(runtime.affectus._port), id(runtime.sensus._port),
            id(runtime.corpus._port), id(runtime.synthetic_ipseity._port),
        }) != 1:
            raise RuntimeError("Six organs do not share one brain")

    def close(self) -> None:
        self.ipseity.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def book_action(self, book_id: str, operation: str, *,
                    event_id: str, authorized: bool = False,
                    direction: int | None = None):
        """Operate a REAL installed, reachable book via source-backed receipt.

        This is a host-authorized research capability. A caller choosing
        a title does NOT establish endogenous goal selection. Pretorius
        receives only verified first-person page text as lived memory,
        never engineer catalog state, hidden pages or bare Gutenberg URLs.
        World and book ledgers own location, edition and physical access.
        """
        import re
        if authorized is not True:
            raise PermissionError("Separate host authorization required for book act")
        if (type(book_id) is not str
                or re.fullmatch(r"book:[0-9]{3}", book_id) is None):
            raise ValueError("Expected stable physical Laboratory book ID")
        if operation not in ("open", "read", "turn", "close"):
            raise PermissionError("Unsupported bounded research book operation")
        if self._pending() is not None:
            raise RuntimeError("Reconcile pending body motion before reading")
        kwargs = {"book_id": book_id, "operation": operation}
        if operation == "turn":
            if direction not in (-1, 1) or type(direction) is not int:
                raise ValueError("Page turn must be exactly one leaf")
            kwargs["direction"] = direction
        elif direction is not None:
            raise ValueError("Direction is valid only for page turns")
        # Bridge validates the actual book-event hash AND original world
        # physical custody/pose; replay gets the one original memory.
        outcome = self.bridge.act("book", event_id=event_id, **kwargs)
        admitted = self.runtime._port.brain.store.get_memory(
            outcome["memory_id"],
        )
        if (admitted is None or admitted["text"] != outcome["subject"]["inner"]
                or not admitted["source"].startswith("laboratory-home:action:")
                or admitted["evidence_class"] != "lived_runtime_memory"):
            raise RuntimeError("Book action was not admitted as lived source evidence")
        return outcome

    _PENDING = "six_organ_lab_pending_world_action_v1"

    def _pending(self):
        raw = self.runtime._port.brain.store.meta(self._PENDING)
        if raw is None:
            return None
        try:
            result = json.loads(raw)
        except ValueError as exc:
            raise RuntimeError("Corrupt pending physical authorization") from exc
        if (type(result) is not dict or
            set(result) != {"policy_decision_id", "thought_id",
                            "selected_tendency", "destination"}):
            raise RuntimeError("Invalid pending Laboratory action reservation")
        return result

    def _reserve_movement(self, proposal: CognitiveProposal, destination: str):
        from pretorius_lab.embodied_access import STATIONS
        if destination not in STATIONS:
            raise PermissionError("Unreviewed physical destination")
        if self._pending() is not None:
            raise RuntimeError("Pending Laboratory action must first reconcile")
        # Neural checkpoint first; then the canonical SQLite reservation.
        # A crash cannot turn a verified physical action into a forgotten
        # host decision solely because the process lost in-memory weights.
        self.runtime.checkpoint()
        data = {
            "policy_decision_id": proposal.policy_decision_id,
            "thought_id": proposal.thought_id,
            "selected_tendency": proposal.selected_tendency,
            "destination": destination,
        }
        with self.runtime._port.brain.store.transaction() as db:
            self.runtime._port.brain.store.set_meta(
                self._PENDING, json.dumps(data, sort_keys=True), db,
            )
            self.runtime._port.brain.store.bump_state_version(db)

    def _clear_movement(self):
        with self.runtime._port.brain.store.transaction() as db:
            db.execute("DELETE FROM meta WHERE key=?", (self._PENDING,))
            self.runtime._port.brain.store.bump_state_version(db)

    def _reconcile_pending(self):
        pending = self._pending()
        if pending is None:
            return None
        proposal = CognitiveProposal(
            policy_decision_id=pending["policy_decision_id"],
            thought_id=pending["thought_id"],
            selected_tendency=pending["selected_tendency"],
        )
        offer = HostCorpusOffer(
            proposal.selected_tendency, "walk", pending["destination"],
        )
        # The existing Corpus pilot checks the ORIGINAL policy receipt
        # and the actual world action, admitting at most one lived memory.
        consequence = self.corpus.act(proposal, offer, authorized=True)
        self.corpus.reflect(consequence, authorized=True)
        if consequence.spoken_aloud == "Ow! My foot!":
            self.affect.admit_impact(consequence, authorized=True)
        self._clear_movement()
        return consequence

    def _execute_movement(self, proposal: CognitiveProposal, destination: str):
        self._reserve_movement(proposal, destination)
        # If the host dies between world commit and Doctor admission,
        # the reservation remains. Next host restart reconciles it.
        return self._reconcile_pending()

    def _canonical_recent_action(self):
        memories = [
            m for m in self.runtime._port.brain.store.memories()
            if m["source"].startswith("laboratory-home:action:")
        ]
        # BrainStore.memories() orders newest first by updated/created tick.
        return memories[0] if memories else None

    def _select_internal_affordance(self, tendency: str, station: str):
        """Only an internal explore tendency may originate locomotion.

        The verified world supplies *feasibility* (not goals). This is a
        bounded deterministic affordance allocator, NOT an extra neural
        selector, task controller or authored narrative intention.
        """
        from collections import Counter, deque
        from pretorius_lab.embodied_access import STATIONS
        from .lab_home_bridge import _row

        if station not in STATIONS:
            raise PermissionError("Outside source-reviewed Laboratory affordances")
        options = STATIONS[station][1]
        if not options:
            return None
        if tendency == "avoid":
            # Feasible physical retreat toward the REAL bedroom; no
            # geometric shortcuts and no host-authored task destination.
            queue = deque([(station, ())])
            seen = {station}
            while queue:
                at, steps = queue.popleft()
                if at == "station:bedroom":
                    return steps[0] if steps else None
                for neighbor in STATIONS[at][1]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        queue.append((neighbor, steps + (neighbor,)))
            return None
        if tendency != "explore":
            return None

        # Only source-verified movements that the SAME canonical brain
        # actually lived may affect exploration priorities.
        counts = Counter()
        lived = [
            m for m in self.runtime._port.brain.store.memories()
            if m["source"].startswith("laboratory-home:action:")
        ]
        with self.bridge.world._open() as db:
            for memory in lived:
                digest = memory["source"].split(":")[-1]
                row = db.execute(
                    "SELECT event_id FROM embodied_events WHERE event_hash=?",
                    (digest,),
                ).fetchone()
                if row is None:
                    continue
                event, verified = _row(db, "embodied_events", row[0])
                if verified != digest:
                    raise RuntimeError("Autobiography/world movement source mismatch")
                destination = event["after_station"]
                if destination in STATIONS:
                    counts[destination] += 1
        return min(options, key=lambda dest: (counts[dest], dest))

    def cycle(self, *, authorized_world_action: bool = False) -> SixOrganCycleReceipt:
        """One real cycle, fail-closed if either pinned donor is unavailable."""
        if type(authorized_world_action) is not bool:
            raise TypeError("A world permission is a typed host decision")
        tick = self.weather.tick + 1
        if tick == 0:
            tick = 1

        # SENSUS: authenticated Laboratory observation, then pinned
        # candidate scene fusion of that very same physical location.
        actual = self.bridge.observe()
        evidence = self.runtime._port.brain.store.get_memory(actual["memory_id"])
        if (evidence is None or not evidence["active"]
                or not evidence["source"].startswith("laboratory-home:observe:")):
            raise RuntimeError("No independently verified world observation")
        state = self.subject.embodied.verify()
        station = state["station"]
        if station not in _VALID:
            raise PermissionError("Unreviewed Laboratory station")
        # AFFECTUS: weather is durable in canonical BrainStore, and its
        # driver is a bounded trusted host opportunity. A realized world
        # consequence remains recorded independently, never forged.
        previous = self._canonical_recent_action()
        kind = "rest_density"
        magnitude = 0.0
        src = "host-opportunity:" + str(tick)
        consumed = None
        if (previous is not None
                and previous["source"] != self.weather.last_consumed_world_source()):
            kind = "goal_impediment" if "foot" in previous["text"].lower() else "goal_progress"
            magnitude = 1.0
            src = previous["source"]
            consumed = src
        self.weather.step(
            tick, (self.weather.driver(kind, magnitude, src),),
            authorized=True, consumed_world_source=consumed,
        )

        modulation = self.weather.modulation()
        # The OBSERVED source remains immutable; only prominence of the
        # verified scene claim changes within bounded percept confidence.
        claim_confidence = max(0.5, min(1.0, 0.8 * modulation.salience_gain))
        donor = self.sensus._donor
        ref = evidence["source"]
        claim = donor.Percept(
            event_id="six_cycle_" + str(tick) + "_location",
            channel="vision",
            evidence=donor.Evidence.OBSERVED,
            source_ref=ref, tick=tick,
            attribute="room", value=_VALID[station],
            confidence=claim_confidence, object_hint="room",
            features=(("type", "room"),),
        )
        scene = self.sensus.acquire(
            tick, (claim,), trusted_refs=frozenset({ref}),
            verified_world_refs=frozenset({ref}),
        )

        # CORPUS: read the real independently verified body before acting.
        self.subject.home.verify()
        body = self.subject.home.audit_state()["body"]
        if not isinstance(body, dict):
            raise RuntimeError("Missing source-verified physical body")

        # MNEMOSYNE: same original concern/recall policy. Weather changes
        # its recall cost, not question text or source authority.
        recall_cost = max(0.0, min(1.0,
            0.12 - _G * modulation.rehearsal_bias))
        mnemonic = self.mnemosyne.deliberate(recall_cost=recall_cost)
        if mnemonic.action == "recall":
            self.mnemosyne.reflect_selected_recollection()

        # NOESIS: unchanged native neural selector, temporarily modulated.
        with original_noesis_weather(
            self.runtime.noesis, modulation,
        ):
            proposal = self.runtime.noesis.deliberate(
                host_trigger="six_organ_lab_cycle",
            )

        # CORPUS: no direct model/world actuation, only trusted-authorized
        # affordance and world verified source receipt.
        destination = self._select_internal_affordance(
            proposal.selected_tendency, station,
        )
        status = "not_executed"
        if destination is not None and authorized_world_action:
            receipt = self._execute_movement(proposal, destination)
            status = receipt.status
        elif (proposal.selected_tendency == "avoid"
              and station == "station:bedroom" and authorized_world_action):
            self.corpus._verified_policy(proposal)
            from hashlib import sha256
            event_id = "six_rest_" + sha256(
                proposal.policy_decision_id.encode()
            ).hexdigest()[:32]
            rest = self.bridge.act("rest", event_id=event_id)
            if rest["status"] not in ("admitted", "already_admitted"):
                raise RuntimeError("Laboratory rest lacked verified admission")
            status = "rested"
            destination = station

        # IPSEITY: never call an LLM/renderer directly with audit/context.
        # In-process host conventions alone are not a universal D3 sandbox.
        if self.ipseity.pending_count():
            raise RuntimeError("Unacknowledged subject frame must reconcile")
        before = self.ipseity.pending_count()
        self.ipseity.publish_current()
        self.ipseity.deliver_next(now_ms=tick * 100_000)
        after = self.ipseity.pending_count()
        if after != 0 or before != 0:
            raise RuntimeError("Subject delivery failed to drain durable gate")

        return SixOrganCycleReceipt(
            tick=tick,
            ports_used=("Sensus", "Corpus", "Affectus", "Mnemosyne",
                        "Noesis", "Synthetic Ipseity"),
            scene_admitted=len(scene.admitted),
            scene_vetoed=scene.vetoed_attributes,
            body_verified=True,
            canonical_weather_digest=self.weather.snapshot_digest(),
            mnemonic_decision=mnemonic.action,
            selected_tendency=proposal.selected_tendency,
            movement_status=status,
            destination=destination if status != "not_executed" else None,
            subjective_delivery_count=1,
            host_provided_goal=False,
            # Selected abstract tendency + affordance is not by itself
            # proof of genuine independent intention or sustained goals.
            self_selected_goal_proven=False,
        )
