"""Optional Candidate B one-brain Laboratory life-cycle research host.

One six-organ cycle, then one original Noesis-owned situated physical choice,
if the original world currently permits it. Never supplies an action name or
invented task, changes Laboratory rules, respawns supplies, or grants autonomy
credit for a host-offered opportunity. The host retains movement routing.
"""
from __future__ import annotations

from pathlib import Path

from .lab_runtime import _exclusive_host
from .noesis_day import real_affordances, offer_daily_opportunity, act_on_noesis_choice
from .store import new_id


def run_daily_life_cycle(
    state: str | Path, world: str | Path, *, affectus_source: str | Path,
    authorize_world: bool = False,
) -> dict:
    if type(authorize_world) is not bool:
        raise TypeError("World authorization must be explicit")
    state, world = Path(state), Path(world)
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.subject_port import SubjectPort
    from .lab_six_organ_session import SixOrganLaboratoryCycle
    from .organs import SixOrganRuntime

    def renderer(text):
        if type(text) is not str or not text.startswith(("I ", "My ", "Mine ", "Me ")):
            raise PermissionError("One first-person Ipseity gate required")
        return text

    with _exclusive_host(state, world):
        runtime = SixOrganRuntime.open(state)
        subject = SubjectPort(SpatialHabitat(world))
        epoch = subject.verify()["world_epoch"]
        with SixOrganLaboratoryCycle(
            runtime, subject, affectus_source=Path(affectus_source),
            renderer=renderer, authorized=True,
        ) as session:
            try:
                # All SIX canonical organs actually participate in this cycle.
                cycle = session.cycle(authorized_world_action=authorize_world)
                if len(cycle.ports_used) != 6 or cycle.subjective_delivery_count != 1:
                    raise RuntimeError("An incomplete six-organ cycle cannot act")
                offered = real_affordances(session.bridge)
                selected = None
                action = None
                if offered:
                    selected = offer_daily_opportunity(session.bridge)
                    if authorize_world:
                        action = act_on_noesis_choice(
                            session.bridge, selected,
                            event_id=new_id("candidate_b_life"), authorized=True,
                        )
                # This contract is not R4 three-goal autonomy, only a single
                # Noesis selection among authenticated local Lab affordances.
                outcome = {
                    "schema": "pretorius.candidate-b.one-brain-daily-cycle.v1",
                    "world_epoch": epoch,
                    "all_six_ports_invoked": list(cycle.ports_used),
                    "one_subject_delivery": cycle.subjective_delivery_count == 1,
                    "weather_state_digest": cycle.canonical_weather_digest,
                    "selected_tendency": cycle.selected_tendency,
                    "movement_status": cycle.movement_status,
                    "world_feasible_actions": list(offered),
                    "daily_noesis_policy_id": selected.policy_id if selected else None,
                    "daily_noesis_selected": selected.action if selected else None,
                    "world_effect": action,
                    "host_offered_opportunity": True,
                    "world_action_authorized": authorize_world,
                    "self_selected_sustained_goal_proven": False,
                    "independent_three_activity_r4_proven": False,
                    "four_affectus_output_causality_proven": False,
                }
            finally:
                runtime.checkpoint()
        if subject.verify()["world_epoch"] != epoch:
            raise RuntimeError("Original Laboratory epoch changed")
        return outcome
