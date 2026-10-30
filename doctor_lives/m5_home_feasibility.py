"""Pure physical-preflight transplant from Article 8 grounded-actions donor.

Source: experiment/doctor-household-care-20261019::
doctor_lives/home_grounded_actions.py::physically_available.
The host-side chooser and executable controller are deliberately excluded.
"""
from __future__ import annotations
from .home_motive_queue import TASKS, plan_steps

def physically_available(state:dict,station:str):
    from pretorius_lab.daily_rhythm import transition
    from pretorius_lab.physics import Conflict, LabError
    from .home_choice_probe import _shortest_route
    available,rejected={},{}
    for task in TASKS:
        try:
            steps=plan_steps(state,station,task)
            pos=station
            draft=state
            for step in steps:
                op,args=step["op"],step["args"]
                if op=="walk":
                    if _shortest_route(pos,args["station"])!=(args["station"],):
                        raise ValueError("Nonadjacent step in candidate household task")
                    pos=args["station"]
                else:
                    draft,_=transition(draft,op,args,pos)
            available[task]=steps
        except (Conflict,LabError,RuntimeError,ValueError) as exc:
            rejected[task]=type(exc).__name__+": "+str(exc)[:140]
    return {"available":available,"rejected":rejected}
