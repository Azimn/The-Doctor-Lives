# Three-component Pretorius preview (research integration; no production promotion)

**Branch:** `integration/three-organ-pretorius-preview`, deliberately
stacked on draft Doctor [PR #57](https://github.com/Azimn/The-Doctor-Lives/pull/57).
The upstream standalone Sensus and Synthetic Ipseity repositories remain
unchanged. This is a real `PretoriusBrainPort` / actual Pretorius identity
running in a **separate state directory named `three-organ-preview`**,
not a synthetic pretend brain. The render transport is still the proven
`DoctorSyntheticIpseitySession` durable organ.

### One coherent path

```text
Authenticated typed shell Percepts
  -> Sensus v0.1 candidate scene (source/evidence preserved, conflicting bind veto)
  -> Doctor's approved ingress (only uncontested observed facts or reported User speech)
  -> Doctor's existing concern ledger (verified observed conflicts become UNCERTAINTY only)
  -> existing Doctor state-to-policy bridge (opt-in recall/continue/ask/defer deliberation)
  -> Doctor host-bound recollection controller (only on selected recall)
  -> Doctor factory-controlled typed SubjectFrame
  -> durable Synthetic Ipseity v0.9.11
  -> subject-only local Ollama renderer
```

**No actor is granted credibility by Sensus type-checking alone.** The host
must supply a separately authenticated `trusted_source_refs` allowlist.
This is a trusted Python boundary, not cryptographic authentication or a
sandbox. The standalone CLI can authenticate local User speech only:
`--say` is `Evidence.REPORTED` and does *not* become visual or
physical proof. Direct observed Percepts require a real upstream trusted
sensor/simulation host using `ThreeOrganPretoriusPreview.cycle()`.
Inferred, remembered, and interoceptive raw streams are never laundered
into world observations or autobiographical fact. Any contested object
is withheld altogether. Two contradictory, confirmed observed claims
may open a **source-marked epistemic concern** (not a memory) and the
Doctor's deliberative policy may elect to recall, without host-forcing
a question.

Every `publish_*` still passes a genuine Doctor typed frame through the
actual durable Ipseity host. The model sees only first-person text, not
Sensus scene IDs, raw evidence class, hidden policy scores, source hashes,
authorization tokens, or protected action data. The engineer receives a
separate receipt (never feed it to the renderer).

### Exact development dependencies

Doctor and Ipseity integration are available on Doctor main, but
Ipseity's 0.9.11 package is **optional**, not installed by plain
`pip install -e .`. Sensus has no pip packaging definition, so its
pinned repository root must be exposed to Python without copying its
implementation into Doctor. On the preview host:

```bash
git clone https://github.com/Azimn/synthetic-ipseity.git ../synthetic-ipseity
git -C ../synthetic-ipseity checkout --detach e2d1dc3978c952e59d270a29e84704c8a1fe264a
python -m pip install -e ../synthetic-ipseity
git clone https://github.com/Azimn/Sensus-Communis-Artificialis.git ../Sensus-Communis-Artificialis
git -C ../Sensus-Communis-Artificialis checkout --detach 802e459ee68950414347d5fa324484c034f57b81
python -m pip install -e .
PYTHONPATH="../Sensus-Communis-Artificialis:." doctor-lives-three-organ-preview \
  --state ./three-organ-preview --enable-experimental-preview --say "Good evening."
```

In Windows PowerShell, instead set `$env:PYTHONPATH` to the
Sensus checkout's absolute path (and run `python -m doctor_lives.three_organ_preview`
with the same `--state`, `--enable-experimental-preview`, and `--say`
arguments). This uses local Ollama default `qwen3:1.5b`; no paid API.

For a verified multi-channel test, run the pinned-donor CI job in
`.github/workflows/three-organ-pretorius-preview.yml`. It uses
small disposable neural configurations and tests conflict-to-recall,
model input isolation, source class preservation, missing permission
rejection, and pending-outbox recovery.

### Scientific and operational constraints

- **Live policy is opt-in preview only.** Synthetic research v0.1 still
  refuses Pretorius by default. The live preview uses a different
  `policy_version` and only consumes independently verified Sensus
  conflicts; it never sees hypothetical gold answers.
- The prior independent policy benchmark **lost 13/18 vs 14/18** against
  the strong simple gap rule. Successful plumbing does not reverse that
  negative result or prove model-selected autonomy.
- The Sensus donor explicitly says cross-project implementation should
  wait until after its Oct 15–23 blinded ablation period. This branch
  runs a **parallel experimental preview** with no donor mutations,
  reclassification of existing results, or production adoption. It
  must not contaminate independent blinded evaluation.
- The preview now uses a separate, engineer-only SQLite scene journal
  with a durable scene snapshot, operation cursor, neural-ingress baseline,
  recovered policy decision, and protected outbox cursor. Restart resumes
  the stored scene without running Sensus or the decision policy again.
  An interrupted neural checkpoint, already acknowledged output, or a
  mismatched ledger still fails closed for operator reconciliation.
  Do not deploy as an unattended production host.
- The pinned Sensus short-lived object files, tick and ID counter are
  snapshotted in the preview scene journal and restored across CLI launches.
  Their donor-defined short retention window and false-merge limitations
  remain unchanged. The adapter touches the pinned donor's private in-memory
  structure and must not be generalized to new donor versions.
- The repo's existing production `doctor-lives-local` CLI and
  canonical state remain unmodified. Do not merge this branch into
  `main` until explicit independent security review, adoption gates,
  crash/replay transaction design and blinded downstream comparison.


### Preview validation round: source, outcome and crash boundaries

The review changes remain opt-in and only on draft PR #59. The original
13/18 policy versus 14/18 simpler gap-rule benchmark remains a **negative
result** and has not been rerun or reinterpreted as a positive finding. This
round does not change the policy's score weights or ten recurrent outputs.

**Causal loop, narrow claim:** a vetoed high-confidence observed conflict opens
a source-marked epistemic concern whose opening event contains the full
constituent assertions: event IDs, original source references, channel and
evidence class, tick, attribute, value, confidence, object hints and features.
Recollection may occur, but does not settle which world assertion is true.
Only a later uncontested scene with at least two distinct, separately
allowlisted observed sources agreeing about the same attribute and object hint
may resolve the concern. The resolution carries both the original complete
evidence and the later observations. Resolution removes that concern from the
next endogenous-recall candidate set. An idempotent, durable policy-effect
receipt links that closure to the subsequent decision ID and recall pressure.
A disposable matched-state intervention
temporarily reopens the same concern, preserving other state, and compares
the policy scores with the resolved version. A changed score vector is a
causal policy test, not a claim that the character's conversational decisions
or performance improved.

**Durability contract:** scene binding occurs in Sensus and is then sealed into
a separate SQLite journal before any Doctor state is mutated. The journal
stores each approved Doctor operation and progresses a monotonic cursor.
Re-opening an interrupted scene consults its source-addressed Doctor events,
source-bearing concern history and existing policy decision receipts.
Already committed admissions and decisions are not repeated. The donor's
bounded short-lived object files are restored from the journal. All scene
payloads, state keys, stage names, policy scores and source references remain
engineer-only. None enter Synthetic Ipseity's subject payload.

**Crash testing bars:** the preview suite covers deterministic injected
exceptions at intermediate points, plus real child-process hard exits at
scene-build persistence, operation admission, decision write, outbox
publication, and delivery acknowledgement. The tests check one Doctor
admission and one preview policy decision after recovery. If a renderer
acknowledged output before the scene journal advanced, recovery records the
delivered stage and refuses to replay that output. A human operator must
confirm what was actually seen. Inference is still at-least-once until host
output acknowledgements are reconciled. This test is an engineering durability
bar, **not** a real-model sustained dialogue bar or a guarantee of exactly-once
observable speech.

**Donor guard:** at module import and before state initialization, the preview
requires Git HEAD at the exact reviewed Sensus commit
802e459ee68950414347d5fa324484c034f57b81, exact imported core Git blob
507cd9f75af04353b5e42d67fb60c147acff5ffb, and exact package export
blob ac434e8d41119ca11a91948e3c0dd7aca3fa3660. The donor must be a Git
checkout and it must not contain source modifications to those files.
The separate production-entrypoint import audit remains unweakened.
The preview suite also statically refuses any production package call that
passes literal preview_live=True.

**Remaining limits:** source allowlisting and distinct source refs do not prove
that two sensors have independent real-world custody. The Sensus 80/160
re-identification result, and known false merges, remain in force. A crash
inside a Doctor neural save can leave a mismatch requiring operator action;
the journal refuses unsafe admission replay rather than falsely completing
it. There has been no sustained local Ollama multi-turn trial, no blind
improvement over the 14/18 gap-rule baseline, and no released Windows
installer. All three organs are still research preview dependencies, not
a three-organ production launch. Donor blinded ablations through October
23, 2026 remain sealed, and Calibos must audit this draft before promotion.


### Follow-up adversarial integrity review (draft-only)

This round corrects a transaction defect: `isolation_level=None` disables
implicit SQLite transactions, so an ordinary `with connection` block did not
atomically bind the scene intent to its Sensus snapshot. The preview journal
now explicitly uses `BEGIN IMMEDIATE` and `COMMIT` with rollback on failure.
The no-donor journal test deliberately throws while serializing the second
record, and confirms that neither record remains before a clean retry.

The stored scene payload, Sensus object-file snapshot and selected policy
decision now include SHA-256 integrity checks. Missing checksums from older
unverified preview state are rejected, not silently backfilled. Recovery from
this condition requires operator review of the isolated research state.
These checks detect unintentional changes and naive row tampering. They are
**not signatures or proof of hostile-host resistance**: an actor with SQLite
write access can also replace the hash. Genuine source custody requires a
separate trusted host boundary.

A pending Synthetic Ipseity frame that precedes the scene's publication
boundary is rejected instead of being consumed as the current scene's
first-person output. This test remains a trusted-in-process integration
test, not a cryptographic binding of every outbox frame to a scene.

The donor expressly defines `Percept.object_hint` as a **same-tick binding
hint only**. It is no longer used to establish persistent object identity
across scenes. Evidence-based concern resolution now additionally requires
Sensus to report a matched cross-tick object identifier equal to the
original disputed object, and requires at least two later agreeing observed
claims from different sensory channels and source references. Negative tests
hold the concern open when another object reuses the same hint or when only
one sensory channel confirms it. This does **not** overturn Sensus's
80/160 re-identification result or prove two channels have independently
authenticated physical origin. A future real sensor host must establish that
custody separately.

This is still a preview engineering and causal-state test. The 13/18 vs
14/18 recall-policy negative result remains untouched. Neither independent
real-model cognitive improvement nor production eligibility is claimed.


### Scene-input replay protection

The preview scene journal now records a unique pair of
`(source_ref, event_id)` for **every authenticated input in a bound scene**.
That includes claims withheld because their object was contested, so a
disputed Percept cannot be reintroduced at the next scene tick to create
another concern. These records commit atomically with scene intent and the
Sensus state snapshot. If snapshot serialization fails, the percept receipts
also roll back. A distinct source reference is a separate namespace: host
authentication, not this database index, must prevent forged source identity.

Receipt enforcement is prospective for scenes processed under this journal
version. Earlier research states are not retroactively attributed unseen
event IDs. Any absent integrity evidence remains fail-closed rather than
fabricated. The receipt index is engineer-only and intentionally retained
for durable replay prevention; retention/privacy policy is still a
deployment design requirement.

### Policy-selected recall recovery and neural completion receipts

Recovery tests now exercise actual policy-selected recollection from a
contradictory visual/instrument scene with an existing first-person memory.
Interrupted scenes are resumed at eight checkpoints. The checks require exactly
one persisted preview policy decision, exactly one durable conflict concern,
and only the earlier memory in the subject renderer context. Vetoed conflicting
measurement values must remain exclusively in engineer-side evidence.

The neural recovery proof has also been strengthened. A higher saved neural
tick was previously accepted as sufficient evidence that an earlier Doctor
admission had completed. It is not: unrelated neural activity may increase
the tick even if the original event's checkpoint save failed. The preview scene
journal now records `op_completed_tick` and `op_completed_sha` **per
admission**, only after `Doctor.ingest` returns and its neural checkpoint
exists. On restart, an already-persisted Doctor event is never re-ingested.
It may be skipped only if the operation-specific receipt matches both the
neural tick and on-disk checkpoint SHA-256. A committed event with a missing or
mismatched completion receipt fails closed for operator reconciliation, even
when neural time has advanced through other activity.

This closes a tick-only false-positive path, not the underlying cross-database
atomicity problem. A crash after Doctor commits its event but before the neural
completion receipt will intentionally block automatic recovery. Existing
interrupted preview states without the newly introduced receipts cannot be
retrospectively certified. The test deliberately advances neural state without
the original receipt and separately changes a completed operation's receipt;
both must fail without duplicate ingestion or model delivery.

The deterministic renderer and SQLite crash gates do not establish
a sustained real-Ollama dialogue bar, objectively better character behavior,
or reliable exactly-once delivery to the outside world. The 13/18 versus
14/18 endogenous-recall loss remains unchanged. Promotion is still gated by
independent review and real-model evaluation.
