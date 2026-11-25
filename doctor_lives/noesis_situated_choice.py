"""Noesis-owned, opt-in situated action competition on the canonical brain.

This consumes the ORIGINAL recurrent probabilities and ORIGINAL autobiographical
first-person memories. It writes choices to the ORIGINAL BrainStore policy and
thought tables. A source-verified manual is evidence, never motor authority.

Narrow instruction-use research, NOT open-domain instruction understanding,
independent motor learning, or proof that the recurrent substrate learned the
manual. Host-verified physical offers remain an external environmental input.
"""
from __future__ import annotations

from contextlib import closing

import hashlib
import json
import re
from typing import Any

from .neural import ACTIONS
from .store import new_id, utc_now

VERSION = "noesis-situated-choice-v0.2"
OUTCOME_VERSION = "noesis-situated-choice-v0.3"
DAILY_BODY_VERSION = "noesis-situated-choice-v0.4-body"
# Grounded here in Noesis, not selected by the host. The existing neural motor
# vocabulary still has ten abstract tendencies, not physical work commands.
NEURAL_AFFORDANCE_MAP = {"experiment": "explore", "repair": "persist",
                         "clean": "persist", "light": "explore",
                         "extinguish": "avoid", "brew_tea": "persist",
                         "prepare_meal": "persist", "eat": "avoid",
                         "rest": "avoid", "sleep": "avoid",
                         "advance": "persist", "seek_kitchen": "persist",
                         "seek_bedroom": "avoid", "continue_commitment": "persist"}
if not set(NEURAL_AFFORDANCE_MAP.values()) <= set(ACTIONS):
    raise RuntimeError("Situated motor map references an absent neural tendency")
MEMORY_WEIGHT = 0.60
NEURAL_WEIGHT = 0.20
# Bounded, grammar-specific instruction comprehension, not unrestricted LLM text
# interpretation or generalized semantic learning.
INSTRUCTION = re.compile(
    r"\bwhen\s+(?P<cue>my [a-z ]{8,65}),\s*i should\s*"
    r"(?P<first>repair|experiment)\b.{0,95}?\bbefore i\s*"
    r"(?P<second>repair|experiment)\b",
    re.IGNORECASE,
)


def _cue_is_perceived(cue: str, first_person_observation: str) -> bool:
    # Match a current first-person *observation*, not remembered wishes or a
    # tool's hidden flags. Whitespace/punctuation differ across source texts.
    def normalize(value):
        return " ".join(re.findall(r"[a-z]+", value.lower()))
    return normalize(cue) in normalize(first_person_observation)


_ACTIVE_COMMITMENTS = {
    "six_organ_native_work_intention_v1": ("travel", "blocked"),
    "six_organ_endogenous_book_goal_v1": ("search", "open", "turn", "read"),
}
# Engineering prior for persistence, bounded below pressing bodily pressure.
COMMITMENT_WEIGHT = 0.10


def _verified_active_commitment(brain, ref):
    if (type(ref) is not tuple or len(ref) != 2
            or ref[0] not in _ACTIVE_COMMITMENTS or type(ref[1]) is not str):
        raise PermissionError("Canonical active commitment reference required")
    key, goal_id = ref
    raw = brain.store.meta(key)
    if raw is None:
        raise PermissionError("Missing canonical commitment")
    envelope = json.loads(raw)
    goal = envelope["payload"]
    digest = hashlib.sha256(json.dumps(
        goal, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()).hexdigest()
    if (digest != envelope.get("sha256") or goal["id"] != goal_id
            or goal["phase"] not in _ACTIVE_COMMITMENTS[key]):
        raise PermissionError("Commitment is not active and source-bound")
    with closing(brain.store.connect()) as db:
        origin = db.execute(
            "SELECT selected_action,trigger FROM policy_decisions WHERE id=?",
            (goal["origin_policy_id"],),
        ).fetchone()
        thought = db.execute(
            "SELECT generated_by FROM thoughts WHERE id=?",
            (goal["origin_thought_id"],),
        ).fetchone()
    tendencies = (("explore", "persist") if key.startswith("six_organ_native_work")
                  else ("explore",))
    if (origin is None or origin["trigger"] != "six_organ_lab_cycle"
            or origin["selected_action"] not in tendencies or thought is None
            or thought["generated_by"] != "neural_policy:" + goal["origin_policy_id"]):
        raise PermissionError("Commitment lacks its canonical neural origin")
    return goal


def select_with_original_noesis(
    brain, *, observation_memory_id: str,
    eligible_read_memory_ids: tuple[str, ...],
    feasible_actions: tuple[str, ...],
    learning_enabled: bool = True, neural_prior_enabled: bool = True,
    outcome_learning_enabled: bool = False,
    eligible_outcome_memory_ids: tuple[str, ...] = (),
    author_day_goal: bool = False,
    interoception_enabled: bool = False,
    active_commitment: tuple[str, str] | None = None,
    habit_bridge=None,
    developmental_history_enabled: bool = False,
) -> dict[str, Any]:
    """Commit one original-brain choice and detailed engineer-only audit.

    Only authenticated original-Doctor lived Laboratory memories can serve as
    candidate evidence. An authorized host has separately checked each read
    against its world receipt; Noesis independently reads its lived text and
    selects the action itself. Callers must not supply suggested choice, raw
    page text, numeric body data or a fabricated percept.
    """
    if (type(learning_enabled) is not bool or type(neural_prior_enabled) is not bool
            or type(outcome_learning_enabled) is not bool or type(author_day_goal) is not bool
            or type(interoception_enabled) is not bool
            or type(developmental_history_enabled) is not bool):
        raise TypeError("Research lesion switches must be explicit booleans")
    if developmental_history_enabled and not outcome_learning_enabled:
        raise ValueError("Developmental history requires outcome learning")
    if type(observation_memory_id) is not str:
        raise TypeError("An original brain observation memory ID is required")
    if type(eligible_read_memory_ids) is not tuple or any(
        type(rid) is not str for rid in eligible_read_memory_ids
    ) or len(eligible_read_memory_ids) > 32 or len(set(eligible_read_memory_ids)) != len(eligible_read_memory_ids):
        raise ValueError("Bounded unique source-verified memory IDs required")
    if type(feasible_actions) is not tuple or not feasible_actions or len(feasible_actions) > len(NEURAL_AFFORDANCE_MAP) or any(
        type(a) is not str or a not in NEURAL_AFFORDANCE_MAP
        for a in feasible_actions
    ) or len(set(feasible_actions)) != len(feasible_actions):
        raise ValueError("Unrecognized or duplicate physical offers")
    if not interoception_enabled and any(
            a in ("seek_kitchen", "seek_bedroom") for a in feasible_actions):
        raise PermissionError("Household route requires the admitted body-cue policy")
    if ("continue_commitment" in feasible_actions) != (active_commitment is not None):
        raise PermissionError("Continuation must reference an actual active commitment")
    commitment = None
    if active_commitment is not None:
        if not interoception_enabled or author_day_goal:
            raise PermissionError("Commitment competition requires bodily perception")
        commitment = _verified_active_commitment(brain, active_commitment)
    observation = brain.store.get_memory(observation_memory_id)
    if (observation is None or not observation["active"]
            or observation["evidence_class"] != "lived_runtime_memory"
            or not observation["source"].startswith("laboratory-home:observe:")
            or not observation["text"].startswith(("I ", "My "))):
        raise PermissionError("No newly admitted original-brain first-person perception")

    native = brain.neural.action_scores()
    if set(native) != set(ACTIONS):
        raise RuntimeError("Existing canonical neural action vocabulary changed")
    base = {action: NEURAL_WEIGHT * float(native[NEURAL_AFFORDANCE_MAP[action]])
            if neural_prior_enabled else 0.0 for action in feasible_actions}
    final = dict(base)
    considered = []
    eligible = []
    for memory_id in eligible_read_memory_ids:
        memory = brain.store.get_memory(memory_id)
        if (memory is None or not memory["active"]
                or memory["evidence_class"] != "lived_runtime_memory"
                or not memory["source"].startswith("laboratory-home:action:")
                or not memory["text"].startswith("I read a page of ")
                or "The words before me read: " not in memory["text"]):
            continue
        eligible.append(memory_id)
        if not learning_enabled:
            continue
        page = memory["text"].split("The words before me read: ", 1)[1]
        matched = INSTRUCTION.search(" ".join(page.split()))
        if not matched:
            continue
        a, b = matched.group("first").lower(), matched.group("second").lower()
        if (a == b or a not in feasible_actions or b not in feasible_actions
                or not _cue_is_perceived(matched.group("cue"), observation["text"])):
            continue
        considered.append((int(memory["created_tick"]), memory_id, a, b))

    # Latest matching actually lived instruction breaks contradictory advice.
    # This is a fixed recency heuristic, not evidence of human-like judgment.
    considered.sort(key=lambda row: (row[0], row[1]), reverse=True)
    chosen_evidence = [considered[0][1]] if considered else []
    if chosen_evidence:
        final[considered[0][2]] += MEMORY_WEIGHT
    outcome_scores = {action: 0.0 for action in feasible_actions}
    eligible_outcomes = []
    used_outcomes = []
    if outcome_learning_enabled:
        from .noesis_consequences import (consequence_pressure,
                                           developmental_consequence_pressure)
        appraisal = (developmental_consequence_pressure if developmental_history_enabled
                     else consequence_pressure)
        outcome_scores, eligible_outcomes, used_outcomes = appraisal(
            brain, observation=observation["text"],
            verified_outcome_memory_ids=eligible_outcome_memory_ids,
            feasible_actions=feasible_actions,
        )
        for action in feasible_actions:
            final[action] += outcome_scores[action]
    elif eligible_outcome_memory_ids:
        # In opt-out controls, do not inspect or implicitly use outcome IDs.
        if type(eligible_outcome_memory_ids) is not tuple:
            raise TypeError("Outcome evidence IDs must be a tuple")
    body_scores = {action: 0.0 for action in feasible_actions}
    body_cues = ()
    if interoception_enabled:
        from .noesis_interoception import perceived_regulatory_pressure
        body_scores, body_cues = perceived_regulatory_pressure(
            observation["text"], feasible_actions,
        )
        for action in feasible_actions:
            final[action] += body_scores[action]
    commitment_scores = {action: 0.0 for action in feasible_actions}
    telos_id = None
    if commitment is not None:
        from .lab_telos import DEFAULT_IMPORTANCE, active_persistence
        telos_id, importance = active_persistence(brain, commitment)
        # Preserve the reviewed baseline persistence prior while attaching
        # its contribution to the actual existing canonical commitment.
        weight = min(0.15, COMMITMENT_WEIGHT * importance / DEFAULT_IMPORTANCE)
        commitment_scores["continue_commitment"] = weight
        final["continue_commitment"] += weight
    habit_scores = {action: 0.0 for action in feasible_actions}
    habit_ids = []
    habit_counts = {}
    if habit_bridge is not None:
        if not interoception_enabled:
            raise PermissionError("Household habits require situated perception")
        from .lab_habits import verified_habit_pressure
        habit_scores, habit_ids, habit_counts = verified_habit_pressure(
            brain, habit_bridge, observation_memory_id, feasible_actions)
        for action in feasible_actions:
            final[action] += habit_scores[action]
    selected_action = max(sorted(feasible_actions), key=lambda a: final[a])
    active_version = (DAILY_BODY_VERSION if interoception_enabled else
                      OUTCOME_VERSION if outcome_learning_enabled else VERSION)

    evidence = {
        "version": active_version,
        "outcome_learning_enabled": outcome_learning_enabled,
        "developmental_history_enabled": developmental_history_enabled,
        "developmental_history_version": ("work-history-appraisal-v2"
                                          if developmental_history_enabled else None),
        "eligible_verified_outcome_ids": eligible_outcomes,
        "used_outcome_memory_ids": used_outcomes,
        "outcome_contributions": outcome_scores,
        "interoception_enabled": interoception_enabled,
        "perceived_body_cues": list(body_cues),
        "interoceptive_contributions": body_scores,
        "habit_enabled": habit_bridge is not None,
        "habit_contributions": habit_scores,
        "habit_practice_counts": habit_counts,
        "habit_source_memory_ids": habit_ids,
        "commitment_contributions": commitment_scores,
        "active_commitment_id": commitment["id"] if commitment else None,
        "telos_commitment_id": telos_id,
        "active_commitment_origin": commitment["origin_policy_id"] if commitment else None,
        "neural_affordance_map": {a: NEURAL_AFFORDANCE_MAP[a] for a in feasible_actions},
        "neural_prior_weight": NEURAL_WEIGHT,
        "learning_weight": MEMORY_WEIGHT,
        "learning_enabled": learning_enabled,
        "neural_prior_enabled": neural_prior_enabled,
        "observation_memory_id": observation_memory_id,
        "eligible_verified_memory_ids": eligible,
        "matched_memory_ids": [x[1] for x in considered],
        "used_memory_ids": chosen_evidence,
        "native_abstract_scores": native,
        "candidate_base_scores": base,
        "candidate_final_scores": final,
        "selector_authority": "original_noesis",
        "physical_authority": "none",
        "note": "host validates receipt/feasibility; Noesis chooses; host authorizes physical execution",
    }
    checkpoint = brain._neural_checkpoint_sha256()
    # Both the decision and its first-person cognitive intention share the
    # original canonical DB transaction. No independent policy table/store.
    with brain.store.transaction() as db:
        pid = new_id("policy")
        tid = new_id("thought")
        db.execute(
            """INSERT INTO policy_decisions
            (id,tick,created_at,trigger,selected_action,base_action_scores_json,
             state_pressure_json,action_scores_json,candidate_record_ids_json,
             selected_record_ids_json,neural_tick,neural_checkpoint_sha256,policy_version)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (pid, brain.store.tick, utc_now(), "noesis_situated_choice",
             selected_action, json.dumps(native, sort_keys=True),
             json.dumps(evidence, sort_keys=True),
             json.dumps(final, sort_keys=True),
             json.dumps(list(dict.fromkeys([observation_memory_id] + eligible + eligible_outcomes + habit_ids))),
             json.dumps(list(dict.fromkeys([observation_memory_id] + chosen_evidence + used_outcomes + habit_ids))),
             int(brain.neural.tick), checkpoint, active_version),
        )
        if selected_action == "continue_commitment":
            subject_thought = "I intend to continue what I was doing."
        elif selected_action in ("seek_kitchen", "seek_bedroom"):
            subject_thought = (
                "I intend to make my way to the kitchen."
                if selected_action == "seek_kitchen"
                else "I intend to make my way to the bedroom."
            )
        else:
            subject_thought = (
                "I judge that " + selected_action
                + (" is the action I should try next." if interoception_enabled or author_day_goal
                   else " is the action I should try next at the workbench.")
            )
        db.execute(
            """INSERT INTO thoughts
            (id,tick,text,trigger,generated_by,source_record_ids_json,action_tendencies_json)
            VALUES(?,?,?,?,?,?,?)""",
            (tid, brain.store.tick, subject_thought, "noesis_situated_choice",
             "noesis_situated_choice:" + pid,
             json.dumps(list(dict.fromkeys([observation_memory_id] + chosen_evidence + used_outcomes + habit_ids))),
             json.dumps(final, sort_keys=True)),
        )
        # Construct a bounded intention from Noesis's own selected cognitive
        # thought, in the ORIGINAL BrainStore and original policy transaction.
        if author_day_goal:
            key = "pretorius_day_noesis_goal_v1"
            existing = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
            if existing is None:
                goal = {
                    "schema": "pretorius.native-day-goal.v1",
                    "id": hashlib.sha256(pid.encode()).hexdigest()[:24],
                    "origin_policy_id": pid, "origin_thought_id": tid,
                    "observation_memory_id": observation_memory_id,
                    "selected_action": selected_action,
                    "intention": subject_thought, "phase": "active",
                }
                envelope = {
                    "payload": goal,
                    "sha256": hashlib.sha256(json.dumps(
                        goal, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False,
                    ).encode()).hexdigest(),
                }
                brain.store.set_meta(key, json.dumps(envelope, sort_keys=True), db)
        brain.store.bump_state_version(db)
    return {
        "policy_decision_id": pid,
        "thought_id": tid,
        "selected_action": selected_action,
        "action_scores": final,
        "base_action_scores": base,
        "source_memory_ids": chosen_evidence,
        "used_outcome_memory_ids": used_outcomes,
        "outcome_contributions": outcome_scores,
        "observation_memory_id": observation_memory_id,
        "policy_version": active_version,
    }



def select_world_affordance(brain, *, observation_memory_id, observation_source,
                            narrative, offers, affordance_map, regulatory_pressure,
                            tower_provider=None):
    """Original Noesis concrete choice on a trusted world's admitted perception.

    The adapter supplies feasible offers and bounded physical cue pressure,
    not the selected action. Canonical abstract deliberation supplies the
    common prior. Reapply its existing state families to each offer's own
    semantic cues so distinct actions sharing a neural tendency can compete
    on relevant history, commitments, concerns and relationships. This is a
    bounded engineering projection, not a new learned competence mechanism.
    """
    observation = brain.store.get_memory(observation_memory_id)
    if (observation is None or not observation["active"]
            or observation["evidence_class"] != "lived_runtime_memory"
            or observation["source"] != observation_source
            or not observation_source.startswith("virtual-world:small-tower:")
            or not observation["text"].startswith("I ")):
        raise PermissionError("Current authenticated Tower observation required")
    if (not offers or len(offers) > 32 or len({o["key"] for o in offers}) != len(offers)
            or any(o["key"] not in affordance_map
                   or affordance_map[o["key"]] not in ACTIONS
                   or not o["text"].startswith("I could ") for o in offers)):
        raise ValueError("Bounded unique feasible offers required")
    if any(type(v) not in (int, float) or not 0 <= v <= .20
           for v in regulatory_pressure.values()):
        raise ValueError("Invalid bounded physical cue pressure")
    context = " ".join([*narrative, *(o["text"] for o in offers)])
    # Conclave is a normal participant in this embodied opportunity, not a
    # second chooser. Only the exact authenticated perception can seed it.
    from .conclave import Conclave, Stimulus
    conclave = Conclave(brain.store, enabled=True)
    source_event = observation.get("source_event_id")
    if not source_event:
        raise PermissionError("Tower observation lacks canonical event provenance")
    interpretation_context = "tower:" + hashlib.sha256(source_event.encode()).hexdigest()[:32]
    readings = conclave.interpret(Stimulus(
        source_event, "world_verified", interpretation_context,
        observation["text"][:2000].strip()))
    # Use the existing kernel's associations as retrieval cues, not as
    # propositions about reality, physical offers, or instructions.
    interpretation_cues = conclave.cues(interpretation_context)
    from .tower_phantasmagorium import retrieval_motifs
    imaginative_cues = retrieval_motifs(brain.store, observation_source)
    retrieval_context = " ".join((context, *interpretation_cues, *imaginative_cues))
    abstract = brain.think("small_tower_native_opportunity", decision_text=context)
    direct, ranked = brain._ranked_memory_sets(48, query=retrieval_context, audit=True)
    base, scores, local, candidate_ids = {}, {}, {}, [observation_memory_id]
    by_key = {o["key"]: o for o in offers}
    outcome_scores = dict.fromkeys(by_key, 0.0)
    outcome_ids = {key: [] for key in by_key}
    if tower_provider is not None:
        from .tower_development import verified_consequence_pressure
        outcome_scores, outcome_ids = verified_consequence_pressure(
            brain, tower_provider, observation, tuple(by_key))
    procedure_scores = dict.fromkeys(by_key, 0.0)
    procedure_ids = {key: [] for key in by_key}
    if tower_provider is not None:
        from .tower_procedure import verified_sequences
        procedure_scores, procedure_ids = verified_sequences(
            brain, tower_provider, observation, tuple(by_key))
    prospective = None
    if tower_provider is not None:
        from .tower_prospective import assess
        prospective = assess(brain, tower_provider, observation, offers, abstract, affordance_map)
    for key in sorted(by_key):
        offer = by_key[key]
        tendency = affordance_map[key]
        # Common words such as "could" must not activate the same commitment
        # for every alternative. Offer labels remain actual perceived options.
        cue = key.replace("_", " ") + " " + offer["text"][8:]
        _, _, appraisal = brain._state_policy_scores(
            ranked, decision_text=cue, direct_history_ranked=direct)
        families = appraisal["families"]
        # A relevant commitment is an action-specific persistence pressure,
        # even if its concrete continuation happens to map to explore/create.
        commitment = max(families["commitments"][tendency],
                         families["commitments"]["persist"])
        specific = (commitment + families["history"][tendency]
                    + families["relationships"][tendency]
                    + families["concerns"][tendency])
        specific = max(-.05, min(.05, specific))
        base[key] = NEURAL_WEIGHT * abstract["action_scores"][tendency]
        goal_pressure = prospective["scores"][key] if prospective else 0.0
        scores[key] = (base[key] + regulatory_pressure.get(key, 0.0) + specific
                       + outcome_scores[key] + goal_pressure + procedure_scores[key])
        local[key] = {"tendency": tendency, "cue": cue,
                      "commitment": commitment, "specific_pressure": specific,
                      "prospective_pressure": goal_pressure,
                      "procedural_pressure": procedure_scores[key],
                      "procedural_memory_ids": procedure_ids[key],
                      "developmental_pressure": outcome_scores[key],
                      "developmental_memory_ids": outcome_ids[key],
                      "source_ids": appraisal["source_ids"],
                      "families": families}
        candidate_ids.extend(appraisal["source_ids"]["history"])
        candidate_ids.extend(outcome_ids[key])
        candidate_ids.extend(procedure_ids[key])
    selected = max(sorted(scores), key=scores.get)
    selected_ids = list(dict.fromkeys([observation_memory_id]
                        + local[selected]["source_ids"]["history"] + outcome_ids[selected]
                        + procedure_ids[selected]))
    evidence = {"version": "noesis-world-affordance-v1",
                "abstract_policy_id": abstract["policy_decision_id"],
                "observation_memory_id": observation_memory_id,
                "selector_authority": "original_noesis",
                "physical_authority": "none",
                "offer_appraisals": local,
                "conclave": {
                    "context_key": interpretation_context,
                    "source_event_id": source_event,
                    "reading_ids": [r.id for r in readings],
                    "retrieval_cues": list(interpretation_cues),
                    "retrieval_query_sha256": hashlib.sha256(retrieval_context.encode()).hexdigest(),
                    "motor_authority": False,
                    "lived_fact_authority": False,
                },
                "phantasmagorium": {"retrieval_cues": list(imaginative_cues),
                                    "world_authority": False, "motor_authority": False,
                                    "lived_fact_authority": False},
                "prospective_goals": prospective,
                "procedural_memory": {"enabled": tower_provider is not None,
                                      "version": "tower-contextual-procedure-v1",
                                      "contributions": procedure_scores,
                                      "source_memory_ids": procedure_ids},
                "developmental_history": {"enabled": tower_provider is not None,
                                          "version": "tower-contextual-consequence-v1",
                                          "contributions": outcome_scores,
                                          "source_memory_ids": outcome_ids},
                "physical_cue_pressure": {k: regulatory_pressure.get(k, 0.0)
                                          for k in scores},
                "candidate_base_scores": base,
                "candidate_final_scores": scores}
    pid, tid = new_id("policy"), new_id("thought")
    with brain.store.transaction() as db:
        db.execute(
            """INSERT INTO policy_decisions
            (id,tick,created_at,trigger,selected_action,base_action_scores_json,
             state_pressure_json,action_scores_json,candidate_record_ids_json,
             selected_record_ids_json,neural_tick,neural_checkpoint_sha256,policy_version)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (pid, brain.store.tick, utc_now(), "noesis_world_affordance",
             selected, json.dumps(base, sort_keys=True), json.dumps(evidence, sort_keys=True),
             json.dumps(scores, sort_keys=True), json.dumps(list(dict.fromkeys(candidate_ids))),
             json.dumps(selected_ids), int(brain.neural.tick),
             brain._neural_checkpoint_sha256(), "noesis-world-affordance-v1"))
        db.execute(
            """INSERT INTO thoughts
            (id,tick,text,trigger,generated_by,source_record_ids_json,action_tendencies_json)
            VALUES(?,?,?,?,?,?,?)""",
            (tid, brain.store.tick, "I intend to " + by_key[selected]["text"][8:],
             "noesis_world_affordance", "noesis_world_affordance:" + pid,
             json.dumps(selected_ids), json.dumps(scores, sort_keys=True)))
        brain.store.bump_state_version(db)
    return {"policy_decision_id": pid, "abstract_policy_id": abstract["policy_decision_id"],
            "selected_action": selected, "action_scores": scores, "appraisals": local}
