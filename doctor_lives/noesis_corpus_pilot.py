"""Opt-in Noesis -> Corpus handoff through the REAL Laboratory receipt bridge.

Candidate source: PR #61 durable task/action reservation and verified source
outcomes. We reuse the production DoctorHomeBridge and its receipt idempotency,
rather than transplanting a CASCADE planner or creating a second policy/store.

An abstract neural tendency NEVER directly constitutes permission to move.
An independently approved host offer with an EXACT matching tendency is needed.
The original Laboratory remains the physical authority; all consequences enter
the one BrainStore through its first-person projection boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re

from .lab_home_bridge import DoctorHomeBridge, _ACTION_DOMAINS
from .neural import ACTIONS
from .organs import CognitiveProposal, SixOrganRuntime

_ID = re.compile(r"[a-z][a-z0-9_-]{1,63}\Z")
_STATION = re.compile(r"station:[a-z0-9:_-]{1,55}\Z")


@dataclass(frozen=True, slots=True)
class HostCorpusOffer:
    """Engineer-side physical offer; no neural or model action authorization."""

    tendency: str
    op: str
    station: str

    def __post_init__(self):
        if self.tendency not in ACTIONS:
            raise ValueError("Offer must match an original recurrent tendency")
        if self.op != "walk" or not _STATION.fullmatch(self.station):
            raise ValueError("Pilot offers ONLY bounded Laboratory walks")


@dataclass(frozen=True, slots=True)
class VerifiedBodyConsequence:
    """The only result admitted to feedback: an existing first-person memory."""

    proposal_id: str
    event_id: str
    status: str
    memory_id: str
    first_person: str
    spoken_aloud: str | None


@dataclass(frozen=True, slots=True)
class CognitiveFeedback:
    """Engineer-only policy receipt, not evidence of task improvement."""

    policy_decision_id: str
    selected_tendency: str
    is_replay: bool


class NoesisCorpusLaboratoryPilot:
    def __init__(self, runtime: SixOrganRuntime, subject_port, *,
                 authorized: bool = False):
        if not isinstance(runtime, SixOrganRuntime):
            raise TypeError("Pilot requires original six-organ brain")
        if authorized is not True:
            raise PermissionError("A trusted host must authorize the Lab adapter")
        self._runtime = runtime
        self._bridge = runtime.bind_laboratory(subject_port, authorized=True)
        if not isinstance(self._bridge, DoctorHomeBridge):
            raise TypeError("Only verified real Laboratory bridge is supported")
        if self._bridge.doctor is not runtime._port:
            raise RuntimeError("Corpus and Noesis must use the SAME brain port")

    @staticmethod
    def _event_id(decision_id: str) -> str:
        return "nc_" + sha256(decision_id.encode("utf-8")).hexdigest()[:32]

    @staticmethod
    def _feedback_trigger(event_id: str) -> str:
        return "nc_feedback_" + event_id[3:27]

    def _verified_policy(self, proposal: CognitiveProposal):
        if type(proposal) is not CognitiveProposal:
            raise TypeError("Requires an actual Noesis policy proposal")
        if proposal.initiated_by != "host" or proposal.selected_tendency not in ACTIONS:
            raise PermissionError("Unrecognized policy provenance")
        store = self._runtime._port.brain.store
        with store.connect() as db:
            policy = db.execute(
                "SELECT * FROM policy_decisions WHERE id=?",
                (proposal.policy_decision_id,),
            ).fetchone()
            thought = db.execute(
                "SELECT generated_by FROM thoughts WHERE id=?",
                (proposal.thought_id,),
            ).fetchone()
            latest = db.execute(
                "SELECT id FROM policy_decisions ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
        if (policy is None or thought is None or latest is None
                or policy["selected_action"] != proposal.selected_tendency
                or thought["generated_by"] != "neural_policy:"
                   + proposal.policy_decision_id):
            raise PermissionError("Policy proposal not sourced from the canonical brain")
        return policy, latest["id"]

    def act(self, proposal: CognitiveProposal, offer: HostCorpusOffer, *,
            authorized: bool = False) -> VerifiedBodyConsequence:
        """Execute only a host-offered action matching a genuine neural tendency."""
        if authorized is not True:
            raise PermissionError("Host must authorize this specific body action")
        if type(offer) is not HostCorpusOffer:
            raise TypeError("A typed host Corpus offer is required")
        policy, latest_id = self._verified_policy(proposal)
        if offer.tendency != proposal.selected_tendency:
            raise PermissionError("Selected Noesis tendency did not match the offer")
        eid = self._event_id(proposal.policy_decision_id)
        # An old proposal must NOT initiate an unreserved new action after
        # cognition has moved on. It MAY only replay an existing world receipt,
        # whose request is checked by DoctorHomeBridge._check_action_proof.
        with self._bridge.world._open() as db:
            existing = db.execute(
                "SELECT 1 FROM " + _ACTION_DOMAINS["walk"]
                + " WHERE event_id=?", (eid,),
            ).fetchone()
        if existing is None and latest_id != proposal.policy_decision_id:
            raise PermissionError("Stale Noesis decision cannot authorize new movement")
        receipt = self._bridge.act(
            "walk", event_id=eid, station=offer.station
        )
        text = receipt["subject"]["inner"]
        memory = self._runtime._port.brain.store.get_memory(receipt["memory_id"])
        if (not text.startswith(("I ", "My ", "Mine ", "Me "))
                or memory["text"] != text
                or memory["evidence_class"] != "lived_runtime_memory"
                or not memory["source"].startswith("laboratory-home:action:")):
            raise RuntimeError("Physical result was not a verified lived consequence")
        return VerifiedBodyConsequence(
            proposal_id=proposal.policy_decision_id, event_id=eid,
            status=receipt["status"], memory_id=receipt["memory_id"],
            first_person=text, spoken_aloud=receipt["subject"]["spoken_aloud"],
        )

    def reflect(self, consequence: VerifiedBodyConsequence, *,
                authorized: bool = False) -> CognitiveFeedback:
        """One original-neural-policy reflection on actually lived body feedback.

        This is a host-authorized cognitive opportunity. It neither invents
        physical initiative nor claims measured advantage over a simple host.
        A repeated request returns the original durable policy decision.
        """
        if authorized is not True:
            raise PermissionError("Separate host authorization for cognitive feedback")
        if type(consequence) is not VerifiedBodyConsequence:
            raise TypeError("Requires a typed verified Corpus consequence")
        eid = self._event_id(consequence.proposal_id)
        if consequence.event_id != eid:
            raise PermissionError("Consequence is not bound to the selected policy")
        brain = self._runtime._port.brain
        memory = brain.store.get_memory(consequence.memory_id)
        if (memory is None
                or not memory["active"]
                or memory["text"] != consequence.first_person
                or memory["evidence_class"] != "lived_runtime_memory"
                or not memory["source"].startswith("laboratory-home:action:")):
            raise PermissionError("Consequence does not match a lived Laboratory memory")
        # Reconcile with the SOURCE world receipt rather than trusting a host
        # dataclass. Replays are idempotent and verify the original request.
        with self._bridge.world._open() as db:
            world_row = db.execute(
                "SELECT envelope,event_hash FROM embodied_events WHERE event_id=?",
                (eid,),
            ).fetchone()
        if not world_row or memory["source"] != "laboratory-home:action:" + world_row[1]:
            raise PermissionError("Missing or mismatched authenticated world consequence")
        from .lab_home_bridge import _row
        with self._bridge.world._open() as db:
            _row(db, "embodied_events", eid)
        trigger = self._feedback_trigger(eid)
        with brain.store.connect() as db:
            previous = db.execute(
                "SELECT id,selected_action,state_pressure_json FROM policy_decisions "
                "WHERE trigger=? ORDER BY rowid DESC", (trigger,),
            ).fetchall()
        if previous:
            if len(previous) != 1:
                raise RuntimeError("Multiple feedback reflections for same world event")
            return CognitiveFeedback(previous[0]["id"], previous[0]["selected_action"], True)
        result = brain.think(trigger, decision_text=consequence.first_person)
        return CognitiveFeedback(result["policy_decision_id"], result["selected_action"], False)
