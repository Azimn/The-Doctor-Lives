"""M5 experimental donor influences. All OFF by default.

Donor mechanisms do not authorize or execute actions. They only expose
source-linked, bounded proposal pressures to the ORIGINAL Noesis selector.
All relevant memories/commitments remain in the canonical BrainStore.
"""
from __future__ import annotations
import json
import re

DONORS=("cascade_commitments","household_grounded","household_habit")
CAP_PER_FAMILY=0.03

def _words(text):
    return set(re.findall(r"[a-z]+",str(text).lower()))-{
        "i","would","like","might","to","the","a","an","of","my","with","for",
        "could","should","and","in","on","will","about","this","that"}

def contributions(bridge,work,proposal,affordance,cycle,enabled=()):
    if not set(enabled)<=set(DONORS):
        raise ValueError("Unknown donor, no silent plugin adoption")
    values={name:0.0 for name in DONORS}
    store=bridge.doctor.brain.store
    text=str(proposal["text"])
    if "cascade_commitments" in enabled:
        for commitment in store.open_commitments():
            if len(_words(commitment.get("description",""))&_words(text))>=2:
                values["cascade_commitments"]=CAP_PER_FAMILY
                break
    if "household_grounded" in enabled:
        # Import only the original donor's PURE world preflight, not its
        # host-side task selector or executor. M4 operator capabilities already
        # have independent source-grounded availability, so receive ZERO
        # extra credit. A future physical home task requires the real-world
        # preflight before this donor can provide an eligible candidate.
        from .m5_home_feasibility import physically_available
        if affordance.get("goal_type")=="household":
            state=bridge.subject.rhythm.audit_state()
            station=bridge.subject.embodied.verify()["station"]
            choices=physically_available(state,station)["available"]
            if affordance.get("affordance_key") not in choices:
                raise PermissionError("Household donor cannot authorize impossible task")
    if "household_habit" in enabled:
        # Original source-only first-person action memories and independently
        # verifiable operator receipts, never a duplicate habit SQLite store.
        count=0
        key=affordance["affordance_key"]
        with work._connect() as db:
            ids=[(r["event_id"],r["event_hash"]) for r in db.execute(
                "SELECT event_id,event_hash FROM operator_events WHERE op=?",(key,))]
        sources={m["source"] for m in store.memories(False)
                 if m["active"] and m["evidence_class"]=="lived_runtime_memory"}
        for event_id,h in ids:
            verified=work.receipt(event_id)
            if verified is None or verified[1]!=h:
                raise PermissionError("Habit donor encountered unverified receipt")
            if "laboratory-home:action:"+h in sources:
                count+=1
        if count>=2:
            values["household_habit"]=min(CAP_PER_FAMILY,0.01*count)
    return values
