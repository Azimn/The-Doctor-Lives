# Endogenous recall as a deliberative action, research v0.1

Status: **synthetic-replica-only exploratory implementation**. No adoption into
live Pretorius, no change to production action policy or neural checkpoint.
This research branch begins at `9df827b66e5d743ee1d08e6b48c5050ff124800f`
and does not alter Doctor PRs #55/#56 or the Synthetic Ipseity donor.

## Rationale

The ten neural `ACTIONS` represent broad tendencies, not memory/tool verbs.
Adding a motor action directly would change encoder dimensions, motor weights
and checkpoint shape. Instead, `PretoriusBrain.research_endogenous_recall`
adds a versioned **deliberative** choice among `recall`, `continue`,
`ask`, and `defer`, leaving the recurrent output set unchanged.

The v0.4 bridge contributes `explore` and `persist` tendencies. A bounded
`information_need_family` uses importance × uncertainty from the
existing **concern ledger**, plus felt curiosity/fatigue, cost and cooldown.
Candidate questions derive from internal *synthetic fixture* concerns, never
from the API caller. The scorer is deterministic and has no memory-answer
oracle. At present its weights are engineering hypotheses, not tuned findings.

## Hard boundary

The method requires `enabled=True` AND exact synthetic replica identity
`("SYNTHETIC_REPLICA_RESEARCH_ONLY",)`. Tests construct a disposable
`BrainStore` and stub neural action scores, without creating or manipulating
the canonical Pretorius instance. Candidates must have
`source="synthetic_epistemic_probe"` and
`actor="SYNTHETIC_REPLICA"`. The existing strict internal-question
validator rejects malformed or implementation-control-like cues.

`persist=False` defaults to side-effect-free counterfactual selection.
`persist=True` appends a **distinctly versioned** row to the existing
`policy_decisions` table, including candidate gap IDs, bridge state,
raw and normalized deliberative scores, the selected action, neural tick
and a hash of a proposed self-question, if any. Audit and decision outputs
are **engineer-only**, never a SubjectFrame. The record does **not** claim
that recall was executed, surfaced, or helpful. Deliberative probabilities
must not be conflated with the neural action distribution.

## What this explicitly does not demonstrate

This is a runnable synthetic action-selection seam, not an autonomous LLM
retrieval success, blind task study, or finished episodic-memory policy.
`recall` selection produces an *unexecuted intention* and a candidate cue,
NOT a memory lookup or host action grant. There is no integration into the
released `doctor-lives-local` launcher or Synthetic Ipseity path. An
authorized host still must enforce question provenance. The older 0/8
model-selected recall result remains unmodified.

DUCK v0.10 donates a **motivation concept**, not its executive, personality,
or memory. No separate organ, imported DUCK runtime, or competing identity
store is created.

## Acceptance and falsification before transplant

The included synthetic fixture tests cover opt-in isolation, source rejection,
unknown gaps, competing fatigue/cost, deterministic intentions, cooldown,
audit-to-cue lineage, and intact neural action dimensions. They establish
mechanical correctness only.

Next evaluate sealed, independently authored multi-turn tasks under matched
budgets and identical evidence across:
(1) no recollection,
(2) random timed recollection,
(3) forced targeted recollection,
(4) a strong explicit gap-trigger rule, and
(5) this policy-selected recollection.
Blindly score correct task completion, unnecessary lookups, bad source claims,
proper abstention, latency and restart trace coherence. Only promote if the
policy beats the strong simple controller in downstream utility, without an
increase in false memory claims. This is not a release blocker for Synthetic
Ipseity's existing integration.
