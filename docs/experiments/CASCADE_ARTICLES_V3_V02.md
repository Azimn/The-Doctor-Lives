# Pretorius CASCADE experimental build v0.2

The target is one real Pretorius runtime that can earn support for each of the 34 Articles under specified deployment conditions. This update continues PR #61's existing brain, Sensus, endogenous recollection, Synthetic Ipseity and pinned governor. It binds development to the revised manuscript supplied by Jay, adds actual budgeted background cognition, and executes a matched restart pilot. It does not declare all-Article qualification.

## Canonical source and assessment

The source is `Articles_of_ArtificialityV.3_REVISED.docx`, supplied October 14 America/Chicago. Its exact SHA-256 is `0a8d52c58c404e602c78abb492fbdb92b337733624346e3318f2e4ca4fcffc60`. The implementation inspected all 34 Article passages, the methods and stopping rules, and both tables. The manuscript is a conceptual framework, not a validated scoring instrument or a report of new model experiments. Its external bibliography was not audited in this task.

`doctor_lives/data/articles_v3_contract.json` retains the source hash, exact headings, individual Article-passage hashes, normalized capacity claims, deployment prerequisites and relevant controls. No unpublished full manuscript or author contact information is republished. Identity markers remain part of Article 11; convergent profundity remains part of Article 23. The [readiness map](CASCADE_ARTICLES_V3_READINESS.md) records implemented, partial and absent functions without treating component names as passed Articles.

`cascade_articles.py` keeps exactly the manuscript's three evidential outcomes. Supported requires the registered numerical consequences and relevant controls to hold for the declared claim. Unsupported requires a genuine discriminating opportunity and informative alternatives with an adverse observed result. Unassessable names missing prerequisites, absent opportunities or inadequate assessment access and stops the probe. An engineering fixture cannot become a deployed longitudinal pass. Tampered artifacts, wrong rubric hashes, changed predictions, unknown Article IDs and paths escaping the study directory are rejected.

The program currently adopts three separated history sessions, two delayed opportunities and one held-out transfer context as its initial study convention. The manuscript explicitly calls that a pragmatic starting convention, not a validated universal threshold. Counts do not establish that opportunities were actually informative. The scorer remains a trusted-evaluator bookkeeping tool: artifact hashes bind supplied records, not truth, reviewer identity, proper randomization or independence. It cannot turn fabricated measurements into valid evidence. Its unit tests exercise the procedure with synthetic numerical records, not passing Pretorius Article results.

## Real background work

`cascade_background.py` adds a host-scheduled worker that calls the existing Doctor heartbeat. Open concerns and overdue commitments determine whether the existing cognition policy produces a thought. A worker does not inject a fictional stimulus, invent a resolution, force a recollection, call a renderer, or send a notification. The heartbeat records actual Doctor policy decisions and thoughts in the canonical preview store.

A host-issued lease specifies a finite total tick quota, a per-wake bound, a minimum interval and an expiry. Issuing the same lease again cannot refill or alter it. It can be revoked. A durable reservation consumes quota before cognition starts. Completed wake IDs return their existing engineer receipt without re-execution. Failed or indeterminate work never receives a refund or an automatic retry. The receipts record actual start/end timestamps, monotonic duration, pre/post Doctor digests, brain ticks and persisted policy IDs. Tick units are operational allowances, not measured tokens, energy or subjective effort.

The CASCADE host now holds a lifetime directory lock, preventing another process from loading an obsolete neural checkpoint while a host is active. Foreground cycles, scene recovery and background work also share an operation lock. A killed process leaves a lock requiring explicit operator reconciliation. A partial failed wake blocks later work until reconciled. This deliberately gives up unattended crash recovery rather than risk duplicate or inconsistent cognition. Cross-database atomicity and exactly-once external effects are not claimed. The separate-process test shows an authorized wake actually executing and persisting cognition; it does not install a service on Jay's machine or prove ongoing scheduling over days.

The actual-host test with an overdue commitment produced a heartbeat policy decision. After explicit commitment completion, the next wake produced no new thought in that fixture. An additional correction makes `CausalSnapshot.open_commitments` count overdue commitments as well as open ones; overdue obligations were previously omitted from that audit count.

## Actual matched pilot

`tools/run_cascade_articles_pilot.py` executes three arms from a common small-neural-state checkpoint: the existing governed preview, the CASCADE governed preview, and a no-task-history control with the same number of observations. It runs three history-building sessions, two delayed questions and a transfer question, closing and reopening the actual host between each session. All arms receive one tick of the same Doctor heartbeat after the third session. CASCADE arms use the new lease-bound worker; the existing preview invokes its existing heartbeat directly. The no-history arm intentionally removes relevant evidence and is an information control, not an equal-information efficacy comparator.

All real organ imports, canonical Pretorius identity, source projection, Sensus scene construction, Doctor policy, subject recollection, Ipseity durability and governor checks execute. The renderer is a disclosed deterministic safe-output fixture. There are no real LLM calls, blinded questions, independently authored holdouts, real multi-day intervals or human ratings. Host clock positions are simulated and actual execution durations are reported separately. The transfer question is an author-designed development case, not an independent heldout confirmation.

The executed case-level record is [ARTICLES_V3_ENGINEERING_PILOT.json](../../results/cascade/ARTICLES_V3_ENGINEERING_PILOT.json). It contains 18 sessions across the three arms. CASCADE and the existing preview chose identical policy actions in **6/6 paired sessions**, exposed the same relevant fact in the same sessions and supplied equal-length subject inputs. This is a local null for action or recall-access improvement from the governance wrapper, not a claim of general architectural equivalence.

The prior observed `325 grams` reading was available to subject-safe recall during the conflict, first delayed question and transfer question in the two history-equipped arms. It never appeared in the no-task-history control. The disputed `451 grams` and `919 grams` readings were not emitted into any subject frame as settled observations. The second delayed paraphrase selected continue and did not surface the earlier reading in either main arm. That miss is preserved; no fixture or policy was changed to remove it. This exact-phrase accessibility measurement is not semantic answer correctness, good conversation or an independent action consequence.

Each arm's background interval produced one existing Doctor policy decision. CASCADE adds permission, quota, expiry, replay and operational-failure constraints around that computation; it does not demonstrate a superior cognitive algorithm. The full Article assessment remains Unassessable because no registered deployed longitudinal Article studies were supplied. This is not a finding that the system fails every capacity, and no all-Article pass is reported.

## Reproduction

Use the pinned donors and isolated state directory already required by PR #61. Run from this repository with reviewed Sensus on `PYTHONPATH`:

```bash
python -m unittest discover -s tests -p 'test_cascade*.py' -v
python -m tools.run_cascade_articles_pilot --output results/cascade/LOCAL_ARTICLES_V3_PILOT.json
python tools/ipseity_entrypoint_gate.py
```

For an authorized one-shot scheduled worker, the existing CASCADE CLI accepts `--background-wake`, `--authorize-background`, `--lease-id`, `--wake-id`, `--lease-expires-ms`, `--background-total-ticks`, `--background-ticks` and `--background-interval-ms`. Supply a new wake ID and the unchanged lease specification on each due invocation. Expiry is an actual Unix epoch in milliseconds. A local scheduler may invoke this command, but this project does not install one or authorize unsolicited external actions. The default governed profile still requires the pinned governor. It constructs a local renderer configuration but a background wake never calls it.

On a crash, preserve the whole preview state, neural checkpoint, operational ledger and lock files before inspection. A started/failed wake is an ambiguous partially completed operation. Inspect its pre/post receipts and Doctor policy history, then recover from a verified backup or perform a separately reviewed reconciliation. Do not blindly delete locks, refill the lease or rerun a wake. No automatic reconciliation API is supplied.

## Work required for all 34 claims

The readiness map exposes substantial functional gaps, especially differentiated social belief tracking, learned procedural habits, empirical affordance learning, prospective preparation rather than only overdue response, consequential external agency, history-conditioned humor, local pragmatic norms and operative future stakes. Existing state and learning mechanisms also need new causal and transfer evidence. Semantic grounding and history-specific reflection remain separate from the syntactic governor.

The next development work should follow a missing function through the actual Doctor policy and subject interface into an independently observed consequence, then test it against a simpler equal-information controller. Fresh blinded cases and real renderer substitution are required before generality claims. Add only mechanisms with named owners and predicted outcomes, retain nulls, and keep the experimental stack unmerged until its production authority and release gates are separately satisfied. Neither theatrical dysfunction nor simulated suffering is a requirement in the manuscript.
