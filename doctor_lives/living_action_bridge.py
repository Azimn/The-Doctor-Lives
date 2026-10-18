"""Opt-in living-world bridge: one Doctor memory for each verified action.

PretoriusBrainPort remains the sole cognition/identity/memory authority.
The Laboratory LivingActionPort owns *only* verified physical opportunities
and source receipts. No second planner, neural tuning or imposed daily agenda.
"""
from __future__ import annotations

from .lab_home_bridge import DoctorHomeBridge, _hash, _SAFE_ID


class DoctorLivingActionBridge(DoctorHomeBridge):
    """Connect the existing real Doctor to the Laboratory's unified action port.

    The returned machine-readable offers are HOST ONLY. The Doctor receives
    exclusively the verified natural-language first-person text through
    the existing DoctorHomeBridge ingress firewall.
    """

    def __init__(self, doctor, subject_port, *, authorized=False):
        super().__init__(doctor, subject_port, authorized=authorized)
        from pretorius_lab.living_action_port import LivingActionPort
        self.actions = LivingActionPort(self.world)

    def discover(self):
        original = self.actions.discover()
        frame = original["subject_frame"]
        source = "laboratory-home:discover:" + _hash({
            "stamp": original["world_stamp"],
            "subject": frame,
        })
        admitted = self._admit(frame, source, kind="observation")
        return {
            "subject": admitted, "world_stamp": original["world_stamp"],
            "offers_for_trusted_host": original["offers"],
            "not_independent_action_selection": True,
        }

    def act_offered(self, offer_id, *, event_id, text=None, bookmark_id=None):
        if type(event_id) is not str or not _SAFE_ID.fullmatch(event_id):
            raise ValueError("Doctor action requires an allowed stable event ID")
        result = self.actions.act(
            offer_id, event_id=event_id, text=text,
            bookmark_id=bookmark_id)
        receipt = result["source"]
        if (not receipt["verified"] or receipt["source_event_id"] != event_id
                or type(receipt["source_event_hash"]) is not str
                or len(receipt["source_event_hash"]) != 64):
            raise RuntimeError("Unverified physical outcome cannot enter Doctor memory")
        admitted = self._admit(
            result["subject"],
            "laboratory-home:action:" + receipt["source_event_hash"],
            kind="observation")
        return {
            "subject": admitted,
            "physical_source": receipt,
            "command": result["command"],
            "host_selected_offer_not_neural_choice": True,
        }
