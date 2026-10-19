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


## Research v0.2: source-backed, matched-arm outcome harness

Run `python tools/run_endogenous_recall_benchmark.py --seed 1842
--output /tmp/endogenous-recall-outcomes.json` (or omit `--output`).
The runner in `tools/run_endogenous_recall_benchmark.py` now creates
**separate disposable synthetic BrainStore replicas** for five arms and
18 frozen fixture tasks: no recall, seeded random recall, forced targeted
recall (upper bound), an explicit and nontrivial uncertainty/fatigue
gap-trigger baseline, and opt-in policy-selected recall.

All arms receive the **same per-task recorded first-person source facts**,
uncertainty, curiosity and fatigue, with at most **one** authorized lookup.
The existing `subject_recollection()` projects retrieved content into a
typed first-person SubjectFrame. A fixed, deliberately simple non-LLM
answer reader receives only the first-person text; it cannot inspect the
gold answer, decision audit, memory IDs, source metadata or arm label.
The evaluator scores a correct source-backed answer, appropriate abstention
on withheld information, false claims, unnecessary lookups, and recovery
of the experimental receipt after SQLite reopening.

Research controller authorization is **strictly confined** to the disposable
synthetic harness. For a policy-selected lookup it checks the persisted
`policy_decisions` row and internal-question SHA before executing.
The existing `events` table receives an engineer-only experiment receipt,
with decision reference and subject-frame digest. Duplicate attempts with
the same attempt key are refused. Such receipts **never** become autobiographical
subject memories. The live Doctor chassis host authorization and Synthetic
Ipseity donor are neither bypassed nor altered by this research harness.

### Interpretation and promotion bar

These are **frozen teaching fixtures**, not independently constructed
holdouts, and the fixed text reader is not a role-playing language model.
Results measure narrow factual continuity from a subject-safe retrieval,
not general conversational quality, autonomous neural authorship, emergent
mind, or an LLM's creative decision. Forced targeted recall has privileged
timing by design and is an *upper-bound control*. No production merge is
authorized on the strength of this benchmark alone.

The exact falsification comparison is **policy-selected vs strong gap rule**
under identical evidence, recall budget and evaluator. The policy must beat
that baseline on externally authored tasks with unseen variations before
claims of policy benefit or promotion. If parity or worse persists, shelve
the policy addition rather than rebranding forced lookup as autonomy.


### Verified preliminary benchmark, 2026-10-12

Exact code head `990e0ec1bfda10db41e9013429c664dad9711427`,
seed `1842`, 18 synthetic episodes x 5 arms = **90 scored trials**.
The test-runner and separate CLI both passed in GitHub Actions
[38329691716](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38329691716).
The paired fixture checks passed 17/17 unit tests; general brain,
fresh-install and causal-audit workflows also passed on that head.

| Condition | Success/18 | Correct sourced facts | Appropriate withheld-fact abstentions | Lookups | Unnecessary lookups | False claims |
|---|---:|---:|---:|---:|---:|---:|
| No recall | 6 | 0 | 6 | 0 | 0 | 0 |
| Random recall | 12 | 6 | 6 | 8 | 2 | 0 |
| Forced targeted recall (upper bound) | 18 | 12 | 6 | 18 | 6 | 0 |
| Strong gap-trigger rule | **14** | **8** | 6 | 11 | 3 | 0 |
| Policy-selected recall | 13 | 7 | 6 | 10 | 3 | 0 |

**Outcome: provisional negative for policy advantage.** The new policy
executed authorized synthetic recall and recovered real source-backed
first-person facts, but scored **one fewer correct task** than the
strong simple rule. None of the policy benefit hypotheses have been
confirmed. Counts are illustrative, not significance tests or power
analysis. These deterministic author-designed cases, the simple
fixed renderer, and a short no-model horizon do not establish real
autonomous model-initiated recall or transferable character cognition.

**Disposition:** keep draft PR #57 as a research artifact. Do not
promote the deliberative policy to production or expand the recurrent
action set on this evidence. A new preregistered, independently authored
blind holdout with matched budgets and real downstream action outcomes
is needed before reconsideration. The historical Gate 4 0/8 outcome
remains unchanged.

The CI workflow also uploads the entire JSON trial ledger as a
downloadable Actions artifact (separate from live Pretorius state)
so the 90 individual trial outcomes can be independently inspected.
