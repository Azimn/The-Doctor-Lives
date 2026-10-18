"""Matched real Doctor + Laboratory remediation for the avoid→tea failure.

Four physically initialized household cases. Each arm owns its own source
world, but shared case/seed preparations create identical pre-decision material
conditions. Six decisions are made with real neural policy on every arm.
No promised long-term autonomy and no rigged baseline outcome claims.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import tempfile

from .home_grounded_actions import ARMS, choose, execute
from .home_native_practice import _agent, _act, SEEDS
from .home_choice_probe import _shortest_route
from .lab_home_bridge import _hash

SCHEMA = "article08-grounded-action-remediation.v0.1"
LAB_PIN = "6e49795752835d64fa6fd63d16359669a1ca2ba7"
CASES = ("ordinary_home", "empty_tea", "worn_workbench", "evening_dark")
OFFERS = 6


def _move(bridge, target, prefix):
    current = bridge.subject.embodied.verify()["station"]
    for i, station in enumerate(_shortest_route(current, target), 1):
        _act(bridge, "walk", f"{prefix}w{i}", station=station)
    if bridge.subject.embodied.verify()["station"] != target:
        raise AssertionError("World route failed")


def _prepare(bridge, case):
    _move(bridge, "station:kitchen", "setupKitchen")
    if case == "empty_tea":
        for i in range(3):
            _act(bridge, "brew_tea", f"setupTea{i}")
        if bridge.subject.rhythm.audit_state()["supplies"]["tea"] != 0:
            raise AssertionError("This world's real tea should be exhausted")
    elif case == "worn_workbench":
        _move(bridge, "station:bench", "setupBench")
        for i in range(2):
            _act(bridge, "experiment", f"setupExperiment{i}")
        if bridge.subject.rhythm.audit_state()["apparatus"] != 0:
            raise AssertionError("Two actual experiments must wear the apparatus")
        _move(bridge, "station:kitchen", "setupReturn")
    elif case == "evening_dark":
        for i in range(3):
            _act(bridge, "advance", f"setupEvening{i}", minutes=240)
        if bridge.subject.rhythm.audit_state()["minute"] % 1440 != 19 * 60:
            raise AssertionError("Evening was not reached through real time")
    elif case != "ordinary_home":
        raise ValueError("Unregistered case")


def _single(root, case, seed, arm):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm

    path = root / case / str(seed) / arm
    path.mkdir(parents=True, exist_ok=True)
    world = SpatialHabitat.create(path / "lab.sqlite3")
    HomeLife(world).initialize()
    DailyRhythm(world).initialize()
    bridge, _ = _agent(path, seed)
    _prepare(bridge, case)
    start = bridge.subject.rhythm.audit_state()
    start_station = bridge.subject.embodied.verify()["station"]
    attempts = []
    for n in range(OFFERS):
        decision = choose(bridge, arm=arm)
        result = execute(bridge, decision, prefix=f"g{n}{case[:3]}{arm[:2]}")
        verified = bridge.subject.verify()["verified"]
        if not verified:
            raise AssertionError("Every attempt must fully replay")
        if arm != "legacy_mapped" and decision["selected_task"] is not None:
            if decision["selected_task"] not in decision["available_tasks"]:
                raise AssertionError("Grounded controller attempted an unavailable task")
        attempts.append({
            "offer": n, "policy_id": decision["neural_policy_receipt"],
            "native_generic_action": decision["native_generic_action"],
            "first_person_sha256": decision["first_person_sha256"],
            "chosen": decision["selected_task"],
            "preflight_available": list(decision["available_tasks"]),
            "preflight_denied": decision["unavailable_tasks"],
            "accepted": result["completed"],
            "material_benefit": result.get("actual_effect"),
            "denied_reason": result["denied_reason"],
            "physical_source_receipts": result["receipts"],
            "world_verified": verified,
        })
    chosen = [a["chosen"] for a in attempts if a["chosen"]]
    completed = [a for a in attempts if a["accepted"]]
    return {
        "case": case, "seed": seed, "arm": arm,
        "initial_material_sha256": _hash(start), "initial_station": start_station,
        "initial_first_person_sha256": attempts[0]["first_person_sha256"],
        "accepted_activity_count": len(completed),
        "material_benefit_count": sum(bool(x["material_benefit"])
                                      for x in completed),
        "denied_activity_count": sum(not x["accepted"] for x in attempts),
        "diverse_completed_activities": len({x["chosen"] for x in completed}),
        "attempted_tea_while_unavailable": sum(
            x["chosen"] == "tea" and "tea" not in x["preflight_available"]
            for x in attempts),
        "selected_categories": dict(Counter(chosen)),
        "attempts": attempts,
        "world_replay": bridge.subject.verify()["verified"],
        "doctor_lived_observation_count": sum(
            m["source"].startswith("laboratory-home:")
            for m in bridge.doctor.brain.store.memories(False)),
    }


def run_grounded_screen(*, cases=CASES, seeds=SEEDS, arms=ARMS):
    if (not cases or not seeds or not arms
            or set(cases) - set(CASES) or set(seeds) - set(SEEDS)
            or set(arms) - set(ARMS)):
        raise ValueError("Only frozen case/seed/controller subsets are allowed")
    with tempfile.TemporaryDirectory() as folder:
        results = [_single(Path(folder), case, seed, arm)
                   for case in cases for seed in seeds for arm in arms]
    parity = []
    for case in cases:
        for seed in seeds:
            cohort = [x for x in results if x["case"] == case and x["seed"] == seed]
            same = (
                len({x["initial_material_sha256"] for x in cohort}) == 1
                and len({x["initial_station"] for x in cohort}) == 1
                and len({x["initial_first_person_sha256"] for x in cohort}) == 1)
            parity.append({"case": case, "seed": seed, "matched": same})
            if not same:
                raise AssertionError("Unfair beginning source states or observations")
    totals = {
        arm: {
            "accepted": sum(x["accepted_activity_count"]
                            for x in results if x["arm"] == arm),
            "material_benefits": sum(x["material_benefit_count"]
                                     for x in results if x["arm"] == arm),
            "denied": sum(x["denied_activity_count"]
                          for x in results if x["arm"] == arm),
            "unavailable_tea_attempts": sum(x["attempted_tea_while_unavailable"]
                                            for x in results if x["arm"] == arm),
        } for arm in arms
    }
    full = (len(cases) == len(CASES) and len(seeds) == len(SEEDS)
            and len(arms) == len(ARMS))
    checks = {
        "all_worlds_replay": all(x["world_replay"] for x in results),
        "matched_source_conditions": all(x["matched"] for x in parity),
        "all_grounded_attempts_preflight_legal": all(
            x["chosen"] in x["preflight_available"]
            for trial in results if trial["arm"] != "legacy_mapped"
            for x in trial["attempts"] if x["chosen"] is not None),
        "no_grounded_tea_when_unavailable": all(
            x["attempted_tea_while_unavailable"] == 0
            for x in results if x["arm"] != "legacy_mapped"),
    }
    if full:
        checks["material_remediation_vs_legacy"] = bool(
            all(totals[arm]["accepted"] > totals["legacy_mapped"]["accepted"]
                for arm in ("grounded_doctor", "grounded_simple")))
        checks["neural_increment_over_simple"] = (
            totals["grounded_doctor"]["material_benefits"] >
            totals["grounded_simple"]["material_benefits"])
    return {
        "schema": SCHEMA, "pre_registration":
            "docs/experiments/ARTICLE08_GROUNDED_HOME_ACTION_PREREG_20261018.md",
        "lab_pin": LAB_PIN, "cases": list(cases), "seeds": list(seeds),
        "arms": list(arms), "offers_per_trial": OFFERS,
        "article8_score_before_after": 10, "qualification": "UNASSESSABLE",
        "doctor_identity_unchanged": True,
        "host_scheduled_not_spontaneous": True,
        "checks": checks, "totals": totals,
        "matched_cohorts": parity, "trials": results,
    }
