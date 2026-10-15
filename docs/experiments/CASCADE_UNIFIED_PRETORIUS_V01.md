# CASCADE plus Pretorius, unified experimental host v0.1

**Research status: isolated, unmerged, not production-approved.**
This v0.1 record is preserved historically. The [v0.2 canonical Articles update](CASCADE_ARTICLES_V3_V02.md)
adds an actual budgeted heartbeat worker, source-bound evidence contract and paired restart pilot.
Branch: `experiment/cascade-unified-pretorius-20261014`, stacked on
`integration/self-reference-governor-pinned-preview` (Doctor PR #60),
which in turn stacks on three-organ preview PR #59 and endogenous recall
research PR #57. This hierarchy preserves all established integration
decisions. None of those experimental branches is silently promoted to main.

## What actually runs

`CascadePretoriusPreview` subclasses the existing *real*
`ThreeOrganPretoriusPreview`. Ingest remains:

```
trusted typed Sensus Percepts + host source allowlist
  -> CASCADE host grant: state digest, action permissions, resource budget
  -> unchanged Sensus cross-modal conflict binding
  -> actual Doctor brain / v0.4-derived endogenous recall / durable policy ledger
  -> actual first-person SubjectFrame / Synthetic Ipseity outbox
  -> pinned Self-Reference Governor and controlled renderer, when enabled
  -> Doctor policy receipt + read-only CASCADE causal-state comparison
```

Only the last trusted speech callback receives subject text. It does not
receive `CausalSnapshot`, CASCADE arbitration receipts, source claims,
Sensus objects, memory IDs, posterior scalars or policy telemetry.

The actual Doctor brain owns Pretorius's identity, neural substrate, needs,
memories, concerns and commitments. **CASCADE does not create a second brain,
copy the governor donor, replace the memory store, or infer an identity from
dialogue.** The optional governor and Sensus donors remain pinned to existing
reviewed revisions. This branch edits neither donor or their experiment data.

## Six CASCADE subsystem dispositions

| CASCADE subsystem | This integration | Limits |
|---|---|---|
| Causal State Kernel | Read-only `CausalSnapshot` of actual Doctor state/version/hash, needs, commitments, concerns, memory count and recurrent checkpoint | Does not establish that all state variables causally influence action |
| Bayesian Memory & Path Graph | Diagnostic calibrated-posterior function and bounded association-graph traversal over *existing active Doctor memory IDs* | No Bayesian weights are written into Doctor; association strength is not source reliability; global/vector retrieval comparison still needed |
| Autonomous Chronos Daemon | Deterministic, permission-bound due-wake proposal that refuses pending deliveries | **No autonomous background daemon, persisted wake schedule, or restart-safe exactly-once wake actuator implemented** |
| Policy & Action Arbiter | Host-created, digest-pinned permissions, perception/character budgets, source authentication, fail-closed preflight before the unchanged Doctor cycle | Does not replace Doctor's internal deliberation; only ingress eligibility is newly arbitrated |
| Zero-Leakage Renderer | Reuses factory-created typed SubjectFrame, real durable Ipseity and canonical pinned Self-Reference Governor on the full profile | No unrestricted semantic truth checker, no guarantee a model cannot paraphrase an unsupported claim; text-only heuristics remain incomplete |
| Intervention & Audit Harness | Matched permission ablation without host mutation, plus persisted Doctor decision verification, neural/state digests and rejection-path tests | Not yet causal cross-domain lesion, autonomous-wake longitudinal, or blind real-model superiority evidence |

These are six *integrated subsystem seams*, not a claim of six experimentally
validated complete CASCADE organs. The CASCADE thirty-four-article specification
remains an external conformance target. Article-by-article passing status has
not been established, and no article is claimed fully satisfied here.

## Basic run, separated from production

On a checkout of the branch with the exact donor installations already used
by PR #60 and #59:

```bash
python -m pip install -e ".[self-reference-governor-preview]"
export PYTHONPATH=/path/to/reviewed/Sensus-Communis-Artificialis:.
doctor-lives-cascade-preview \
  --enable-experimental-preview \
  --state /tmp/cascade-a/three-organ-preview \
  --model qwen3:1.5b \
  --renderer-control governed \
  --say "What do you remember of the laboratory balance?"
```

The alternate `--renderer-control plain` is an **explicit ungoverned
control**, not a production recommendation. Isolate it under a different
state root, e.g. `/tmp/cascade-b/three-organ-preview`. Keep
`doctor-lives-local` unchanged. A failed renderer may leave durable
Ipseity output pending; use `--resume` only according to the existing
three-organ crash-recovery constraints. Any already acknowledged but
unrecorded delivery requires operator reconciliation, not blind replay.

## Reproducible software acceptance gates

`tests/test_cascade_preview.py` checks probability math and impossible
evidence, trusted typed grants, denied permissions, insufficient resource
budgets, unauthenticated sources, simulation-only Chronos permissions,
counterfactual gate ablation without state mutation, actual Sensus-to-Doctor
policy-to-Ipseity delivery, policy receipt reconstruction from authoritative
SQLite, restart persistence, bounded memory-graph provenance and refusal to
launch a full-profile session without the pinned governor.

GitHub Actions workflow `cascade-unified-pretorius.yml` installs exact donor
revisions, runs these tests on Python 3.11, 3.12 and 3.13, repeats the original
three-organ and governor regression suites and reruns the production subject
boundary inventory. **An added test file or workflow is not evidence of a green
run until the workflow result is checked.**

## Research design and preregistration for next gate

Compare the accepted four-organ preview without CASCADE gates against the
same preview with CASCADE gates. Freeze evidence, observation order,
first-person subject frame, renderer instruction and model/seed/compute
budget whenever the targeted intervention is renderer-only. For causal
state-policy tests, use cloned disposable Doctor stores, manipulate exactly
one eligible relationship, concern, commitment, resource or source-reliability
state variable, then record downstream decision-score differences and
verified task effects. Distinguish interventions that merely change permission
from interventions that alter the *subject's* chosen action.

For autonomous-wake comparison, implement a durable independently authorized
scheduler and transactional wake receipts first. A proposed wake is **not**
autonomous thought. Measure spontaneous authorized work, missed and duplicate
wakes, conflicting commitments, crash recovery and cost. No live scheduler,
external account capability or unsolicited tool action should be activated
by this preview.

For retrieval, pit the same source-linked memories against flat search,
bounded graph-routed search, and rewired-graph controls at matched evidence
and inference budget. Treat posterior belief and memory association as
different variables. On renderer tests, include first-person, second-person
self-address and third-person self-reference displacements, unsupported
autobiographical claims, speaker uncertainty and refusal/repair rate with blind
human scoring. The current syntactic governor cannot stand in for semantic
grounding.

**Existing negative evidence is retained:** the experimental endogenous
recall controller scored 13/18 versus 14/18 for a simple gap-trigger
control. Standalone Sensus object re-identification matched simple controls
at 80/160. Earlier governor experiments observed zero vetoes for certain
second/third-person failures until the rules were expanded. None of these
results is erased by the integration being operational.

## Release criteria

Keep this branch draft while source-authenticated live-world authority,
cross-database crash atomicity, governed semantic claim safety, autonomous
wake idempotence, benchmark superiority, and an independently reviewed
article-by-article CASCADE register remain open. Sensus's Oct 15-23 blinded
ablation schedule is independent and must not be modified or prematurely
unblinded.
