"""CASCADE budget and replay semantics on the existing canonical Doctor.

Retains the original operational ledger, not a second mind. Background work
never grants motor authority or creates a conversation without a real input.
"""
from pathlib import Path
from .cascade_background import BackgroundLease, BackgroundLedger, checked_id, integer
from .lab_runtime import _exclusive_host
from .local_turn_journal import LocalTurnJournal
from .organs import SixOrganRuntime

def assert_no_pending_conversation(state,runtime,journal):
    if journal.open_turn() is not None:
        raise RuntimeError("Recover unfinished conversation first")
    if (state/"synthetic_ipseity.sqlite3").exists():
        from .ipseity_integration import DoctorSyntheticIpseitySession
        def denied(_):
            raise PermissionError("Background cognition cannot render")
        with DoctorSyntheticIpseitySession(state,renderer=denied,brain_port=runtime._port) as session:
            if session.pending_count():
                raise RuntimeError("Recover undelivered subject experience first")

def _ready(state,runtime,journal):
    assert_no_pending_conversation(state,runtime,journal)
    store=runtime._port.brain.store
    if any(store.meta(k) is not None for k in (
        "small-tower:pending-world-request-v1",
        "six_organ_lab_pending_world_action_v1",
        "six_organ_lab_pending_verified_rest_v1")):
        raise RuntimeError("Recover unfinished world action first")

def issue(state, lease, *, authorized=False):
    if authorized is not True:
        raise PermissionError("Explicit background authorization required")
    state=Path(state)
    if not (state/"brain.sqlite3").is_file():
        raise FileNotFoundError("Existing canonical state required")
    with _exclusive_host(state):
        ledger=BackgroundLedger(state)
        ledger.assert_reconciled()
        ledger.issue(lease)

def revoke(state, lease_id, *, authorized=False):
    if authorized is not True:
        raise PermissionError("Explicit background authorization required")
    state=Path(state)
    with _exclusive_host(state):
        BackgroundLedger(state).revoke(lease_id)

def wake(state, *, lease_id,wake_id,now_ms,ticks=1,authorized=False):
    if authorized is not True:
        raise PermissionError("Explicit background authorization required")
    checked_id(lease_id);checked_id(wake_id);integer(now_ms);integer(ticks,1,100)
    state=Path(state)
    if not (state/"brain.sqlite3").is_file():
        raise FileNotFoundError("Existing canonical state required")
    with _exclusive_host(state),LocalTurnJournal(state) as journal:
        runtime=SixOrganRuntime.open(state)
        return _wake_locked(state,runtime,journal,lease_id=lease_id,wake_id=wake_id,
                            now_ms=now_ms,ticks=ticks)


def _wake_locked(state,runtime,journal,*,lease_id,wake_id,now_ms,ticks=1):
    """Trusted host already holds the canonical exclusive lock."""
    _ready(state,runtime,journal)
    ledger=BackgroundLedger(state)
    ledger.assert_reconciled()
    prior=ledger.reserve(lease_id,wake_id,now_ms,ticks)
    if prior is not None:
        return {**prior,"replayed_receipt":True}
    brain=runtime._port.brain
    before=brain.store.tick
    try:
        result=brain.heartbeat(ticks=ticks)
        # Use actual existing internal uncertainty, never a supplied
        # question or invented external stimulus.
        pilot=runtime.mnemosyne.opt_in_endogenous_recollection()
        decision=pilot.deliberate()
        # The original Mnemosyne policy now owns its intention atomically
        # for both production bindings, not just this background caller.
        reflection=None
        if decision.action=="recall":
            reflection=pilot.reflect_selected_recollection(reconstruct=True)
        runtime.checkpoint()
        receipt={"schema":"canonical-cascade-wake-v1","wake_id":wake_id,
                 "before_tick":before,"after_tick":brain.store.tick,
                 "heartbeat_policy_ids":[t["policy_decision_id"] for t in result["thoughts"]],
                 "mnemosyne_policy_id":decision.decision_id,
                 "reflection_policy_id":reflection.next_policy_decision_id if reflection else None,
                 "renderer_calls":0,"external_actions":0,"engineer_only":True,
                 "replayed_receipt":False}
        ledger.complete(wake_id,receipt)
        return receipt
    except BaseException as exc:
        ledger.complete(wake_id,{"error_type":type(exc).__name__,
                        "operator_reconciliation_required":True},status="failed")
        raise
