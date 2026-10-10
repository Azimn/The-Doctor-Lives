"""Stage 06: inspectable host-observed action eligibility and goal regression.

This layer never grants permissions, asserts consent or writes the world.
Only an authenticated host operation can change environment state. Eligibility
is a prediction over a frozen observation, never an execution authorization.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .world_host_ledger import WorldHostLedger

ACTIONS=("STOP_CLOCK","UNSEAL_NOTEBOOK","INSPECT_NOTEBOOK","WAIT")
HOST_VERBS={
    "STOP_CLOCK":"stop_clock",
    "UNSEAL_NOTEBOOK":"unseal_notebook",
    "INSPECT_NOTEBOOK":"inspect_notebook",
}
GOALS=("stop_clock","inspect_notebook")


@dataclass(frozen=True)
class HostObservation:
    clock: str
    notebook: str
    grants: frozenset[str]
    henry_consent: bool
    sequence: int

    @classmethod
    def from_world(cls, host:WorldHostLedger, actor:str="pretorius"):
        state=host.world()
        authority=host.visible_authority(actor)
        return cls(
            clock=state["state"]["clock"],
            notebook=state["state"]["notebook"],
            grants=frozenset(authority["grants"]),
            henry_consent=bool(authority["henry_unseal_consent"]),
            sequence=state["sequence"],
        )


def feasible(observation:HostObservation, action:str)->bool:
    """Only PRECHECK feasibility; world.execute must reauthorize atomically."""
    if action=="WAIT":
        return True
    if action not in HOST_VERBS:
        return False
    if HOST_VERBS[action] not in observation.grants:
        return False
    if action=="STOP_CLOCK":
        return observation.clock=="running"
    if action=="UNSEAL_NOTEBOOK":
        return observation.notebook=="sealed" and observation.henry_consent
    if action=="INSPECT_NOTEBOOK":
        return observation.notebook=="open"
    return False


def eligible_actions(observation:HostObservation)->tuple[str,...]:
    return tuple(action for action in ACTIONS if feasible(observation,action))


def _step(state:tuple[str,str,bool], action:str)->tuple[str,str,bool]:
    clock,notebook,inspected=state
    if action=="STOP_CLOCK":
        return ("stopped",notebook,inspected)
    if action=="UNSEAL_NOTEBOOK":
        return (clock,"open",inspected)
    if action=="INSPECT_NOTEBOOK":
        return (clock,notebook,True)
    raise ValueError("unrecognized state action")


def regress_goal(
    observation:HostObservation,goal:str,*,max_depth:int=3,
)->tuple[str,...]:
    """Find the shortest authorized plan over typed world preconditions.

    WAIT is returned for already-satisfied stop-clock goals and for
    currently impossible goals. A witnessed inspection is an action goal:
    a notebook being open alone does not mean it was inspected.
    """
    if goal not in GOALS or max_depth<1 or max_depth>3:
        raise ValueError("unsupported action goal or planning horizon")
    start=(observation.clock,observation.notebook,False)
    def complete(state:tuple[str,str,bool])->bool:
        return (state[0]=="stopped" if goal=="stop_clock" else state[2])
    if complete(start):
        return ("WAIT",)
    queue=deque([(start,())])
    explored={start}
    while queue:
        state,path=queue.popleft()
        if len(path)>=max_depth:
            continue
        frame=HostObservation(
            clock=state[0],notebook=state[1],
            grants=observation.grants,henry_consent=observation.henry_consent,
            sequence=observation.sequence,
        )
        for action in eligible_actions(frame):
            if action=="WAIT":
                continue
            nxt=_step(state,action)
            if nxt==state or nxt in explored:
                continue
            plan=path+(action,)
            if complete(nxt):
                return plan
            explored.add(nxt)
            queue.append((nxt,plan))
    return ("WAIT",)


def describe_menu(observation:HostObservation)->str:
    allowed=eligible_actions(observation)
    return "Host-eligible actions NOW: "+", ".join(allowed)+"."


def recheck_before_execution(host:WorldHostLedger,action:str)->tuple[bool,str]:
    """Fresh-state safety check, never proof that the later host call succeeds."""
    if action not in ACTIONS:
        return False,"invalid_action"
    current=HostObservation.from_world(host)
    if feasible(current,action):
        return True,"currently_eligible"
    return False,"stale_or_denied_affordance"
