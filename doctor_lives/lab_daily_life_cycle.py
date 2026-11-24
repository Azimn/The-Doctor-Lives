"""Optional Candidate B one-brain Laboratory life-cycle research host.

One six-organ cycle, then one original Noesis-owned situated physical choice,
if the original world currently permits it. Never supplies an action name or
invented task, changes Laboratory rules, respawns supplies, or grants autonomy
credit for a host-offered opportunity. The host retains movement routing.
"""
from __future__ import annotations

from pathlib import Path

from .lab_runtime import _exclusive_host
from .noesis_day import (real_affordances, offer_daily_opportunity,
                         act_on_noesis_choice, reconcile_pending_daily_action,
                         pending_daily_action_ids)
from .store import new_id


def run_daily_life_cycle(
    state: str | Path, world: str | Path, *, affectus_source: str | Path,
    authorize_world: bool = False,
    phantasmagorium_source=None,
) -> dict:
    if type(authorize_world) is not bool:
        raise TypeError("World authorization must be explicit")
    state, world = Path(state), Path(world)
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.subject_port import SubjectPort
    from .lab_six_organ_session import SixOrganLaboratoryCycle
    from .organs import SixOrganRuntime
    from .lab_phantasmagorium import configured_archive, sync_phantasmagorium
    phanta = configured_archive(phantasmagorium_source)

    def renderer(text):
        if type(text) is not str or not text.startswith(("I ", "My ", "Mine ", "Me ")):
            raise PermissionError("One first-person Ipseity gate required")
        return text

    with _exclusive_host(state, world):
        runtime = SixOrganRuntime.open(state)
        subject = SubjectPort(SpatialHabitat(world))
        epoch = subject.verify()["world_epoch"]
        preflight_bridge = runtime.bind_laboratory(subject, authorized=True)
        preflight_pending = pending_daily_action_ids(preflight_bridge)
        if len(preflight_pending) > 1 or (preflight_pending and (
            runtime._port.brain.store.meta(SixOrganLaboratoryCycle._PENDING) is not None
            or runtime._port.brain.store.meta(SixOrganLaboratoryCycle._PENDING_REST) is not None
        )):
            raise RuntimeError("Conflicting canonical motor reservations")
        with SixOrganLaboratoryCycle(
            runtime, subject, affectus_source=Path(affectus_source),
            renderer=renderer, authorized=True,
            recover_world_actions=authorize_world,
            couple_physical_fatigue=True,
        ) as session:
            try:
                # Reconcile a previously authorized Noesis motor BEFORE making
                # another decision. The original world receipt is idempotent;
                # no new operator goal or physical action is inferred.
                recovered_six = session.recovered_world_action is not None
                pending = pending_daily_action_ids(session.bridge)
                if recovered_six and pending:
                    raise RuntimeError("Conflicting six-organ and daily motor reservations")
                # A read-only opportunity must NEVER replay a reserved motor.
                # When permission exists, recover its single original world
                # effect first. Recovery consumes this host opportunity: a
                # second movement or fresh daily action would be a ghost act.
                recovered = (
                    reconcile_pending_daily_action(session.bridge)
                    if authorize_world and pending else ()
                )
                deferred = pending if not authorize_world else ()
                # All SIX canonical organs still participate, without a
                # second physical effect in the same recovery opportunity.
                # The daily host has one motor authority: its situated
                # Noesis decision. The six-organ cycle remains a complete
                # non-actuating cognition/perception opportunity, not a
                # competing abstract motor that can preempt a bodily need.
                cycle = session.cycle(authorized_world_action=False)
                if len(cycle.ports_used) != 6 or cycle.subjective_delivery_count != 1:
                    raise RuntimeError("An incomplete six-organ cycle cannot act")
                offered = real_affordances(session.bridge)
                selected = None
                action = None
                if (offered and not recovered and not deferred
                        and not recovered_six
                        and cycle.movement_status == "not_executed"):
                    selected = offer_daily_opportunity(session.bridge)
                    if authorize_world:
                        action = act_on_noesis_choice(
                            session.bridge, selected,
                            event_id=new_id("candidate_b_life"), authorized=True,
                        )
                # This contract is not R4 three-goal autonomy, only a single
                # Noesis selection among authenticated local Lab affordances.
                phanta_report = (sync_phantasmagorium(session.bridge, phanta)
                                 if phanta and authorize_world else None)
                outcome = {
                    "schema": "pretorius.candidate-b.one-brain-daily-cycle.v1",
                    "phantasmagorium": phanta_report,
                    "world_epoch": epoch,
                    "all_six_ports_invoked": list(cycle.ports_used),
                    "one_subject_delivery": cycle.subjective_delivery_count == 1,
                    "weather_state_digest": cycle.canonical_weather_digest,
                    "selected_tendency": cycle.selected_tendency,
                    "movement_status": cycle.movement_status,
                    "world_feasible_actions": list(selected.options if selected else offered),
                    "daily_noesis_policy_id": selected.policy_id if selected else None,
                    "daily_noesis_selected": selected.action if selected else None,
                    "world_effect": action,
                    "reconciled_prior_noesis_actions": list(recovered),
                    "pending_prior_noesis_actions": list(deferred),
                    "reconciled_prior_six_organ_action": recovered_six,
                    "new_motor_suppressed_for_recovery": bool(
                        recovered or deferred or recovered_six
                    ),
                    "daily_motor_suppressed_for_six_organ_effect":
                        cycle.movement_status != "not_executed",
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
