# Pretorius x Synthetic Ipseity: real brain-to-renderer integration

Status: implementation candidate on a review-only stacked branch. Do not
promote or announce universal enforcement until the standalone host is wired
exclusively to this port and all review gates are satisfied.

## Authoritative components and pins

Doctor production baseline:
`Azimn/The-Doctor-Lives@56aab5493ef48cdb560881a138b2277ca6ebcce0`.
Doctor subject-recollection interface proposal: PR #55, commit
`97b2c9ad1e0d765ab07cd6c62541f3ee9c4896cc`.
Synthetic Ipseity core baseline:
`Azimn/synthetic-ipseity@d55e2a7fecda1760df1d21590ce3bdcfc7f0a729`.
Cross-repository additive trusted-projector donor:
`Azimn/synthetic-ipseity@e2d1dc3978c952e59d270a29e84704c8a1fe264a`
(PR #31, v0.9.11 candidate). Exact donor commit is checked out in the
specialized GitHub Actions workflow. It is not an unrestricted branch pin.

## Execution path

```text
Lab / person / scheduler / body / tool
    |  existing Doctor authorized projection and state admission
    v
PretoriusBrainPort + persistent Doctor BrainStore and recurrent state
    |  real cognitive_view -> protected Doctor SubjectFrame
    v
DoctorSyntheticIpseitySession (trusted in-process host)
    |  typed Doctor SubjectFrame only
    |  host attested acquisition, subject/epoch, monotonic cursor
    v
SyntheticIpseityOrgan 0.9.11 (real imported package)
    |  preserved projected wording, bounded access
    v
DurableIpseityHost (separate atomic cursor + subject-only outbox)
    |  leased first-person text ONLY
    v
SubjectOnlyRendererPort -> local model/callback
```

All world authorization, physical receipts, actual cognition, personal
identity, memory classification and neural adaptation remain in the Doctor
and Laboratory authorities. This adapter cannot rewrite autobiographical
memory or execute laboratory commands. Model replies are **not** automatically
accepted as memories, first-person experiences, physical outcomes or actions.

The canonical Doctor projection already protects provenance and converts
felt state, memories, impulses, relationships and incoming communication into
first-person experience. The imported standalone Synthetic Ipseity organ
enforces another *active* independent admission and restartable render gate.
The new `PROJECTED_SUBJECT_EVENT` donor kind preserves that verified
projection verbatim. Re-projecting as a new recollection or external tool
result would generate false epistemic/source attribution.

## Usage from trusted Python host

Install a reviewed Synthetic Ipseity source commit with v0.9.11 capabilities;
the specialized workflow documents and validates the exact donor revision.
The main Doctor install intentionally does NOT require an optional experimental
package or automatically alter existing production behavior.

```python
from doctor_lives.ipseity_integration import DoctorSyntheticIpseitySession

with DoctorSyntheticIpseitySession(
    "my-disposable-pretorius-state",
    renderer=lambda first_person_text: local_renderer(first_person_text),
) as runtime:
    runtime.ingest({
        "channel": "world",
        "text": "The laboratory balance reads 325 grams for the beaker.",
        "source": "approved-world-perception",
    })
    runtime.think()
    runtime.publish_current()
    receipt = runtime.deliver_next(now_ms=1000)

    # PR #55's Doctor-owned first-person retrieval:
    runtime.publish_recollection(
        "What do I remember of the balance reading for the beaker?"
    )
    recall_receipt = runtime.deliver_next(now_ms=2000)
```

The lambda is illustrative, not a real model installation or an endorsement
of accepting generated text as truth. A genuine host must use a trusted
renderer adapter, validate communication and assign action permission separately.

## Restart, trust, and scope limitations

The Synthetic Ipseity SQLite checkpoint and outbox persist under the canonical
Doctor state directory in a separate `synthetic_ipseity.sqlite3` file. It
does not replace `brain.sqlite3` or `pretorius_recurrent.npz`.

Renderer failure leaves a subject-only outbox frame pending; a later process
can lease and retry that original text. Delivery is at-least-once, not
exactly-once. Host authorization, external action acknowledgements and
cross-database Doctor/store atomicity must be handled by a future standalone
runtime transaction/receipt protocol. Caller controls when a new
`publish_current` or `publish_recollection` opportunity is created; this
interface does not authenticate autonomous intention by itself.

The trusted host must *not* hand arbitrary text to this organ as a supposedly
preprojected event. `_publish_typed_subject_frame` only accepts the
factory-controlled Doctor `SubjectFrame` type and all output is routed through
the source-attested SyntheticIpseityOrgan. The library is not a security
sandbox for malicious Python code. It cannot stop other code from directly
invoking `PretoriusBrainPort.render_request` or a model API. The deployed
standalone chassis MUST remove all such bypasses before claiming an enforced
end-to-end subject-access boundary. No interface here establishes consciousness.

## Required gate

The independent linked CI suite runs the real 0.9.11 donor on the actual
PretoriusBrainPort, uses genuine Doctor SQLite and neural checkpoint state,
admits a real world observation, retrieves it after a fresh process restart,
and confirms a subject-only callback rather than raw engineering telemetry.
It tests malformed query rejection, renderer error lease recovery and
factory-controlled subject-frame enforcement. These are engineering
integration tests only.

Before production promotion: review source-authentication, timing/clock and
cursor authorization, duplicate publish behavior across interruptions,
world/brain/outbox transaction ordering, bypass inventory, malicious source
prompt handling, model-response admission discipline, and source-truth
semantics. Run the actual laboratory across restart and one real local renderer
with opt-in and baseline arms. Preserve the known negative model-action results
under Issue #53 rather than retroactively claiming improved autonomy.

## Concrete local entry point

The optional `doctor-lives-local` command is the approved first integration
chassis for a human-initiated dialogue turn. It does not use the previous raw
brain CLI as a model entrypoint. The runtime requires the reviewed
`synthetic-ipseity==0.9.11` package. It fails closed when the integration
capability is unavailable or an earlier subject frame is outstanding.

Use a **new disposable directory** until the release gate is reviewed. On
Windows with Python 3.11+, a Git client, and Ollama installed:

```powershell
py -m pip install "git+https://github.com/Azimn/synthetic-ipseity.git@e2d1dc3978c952e59d270a29e84704c8a1fe264a"
py -m pip install "git+https://github.com/Azimn/The-Doctor-Lives.git@integration/synthetic-ipseity-subject-path"
ollama pull qwen3:1.5b
doctor-lives-local --state .\pretorius-test-state --model qwen3:1.5b --say "Good evening, Doctor."
```

For a temporary local inference failure, repeat **without** re-entering the
human message:

```powershell
doctor-lives-local --state .\pretorius-test-state --model qwen3:1.5b --resume
```

A pending frame, including one already leased for delivery, must be
acknowledged or reconciled before the host publishes another frame.
`require_drained=True` is checked atomically within the donor's durable
outbox transaction. It does not promise exactly-once model execution,
consistent speech across model swaps, or atomic transactions between
Pretorius's brain DB and the organ DB.

The initial CLI presents **human-initiated dialogue only**. The user message
is projected and stored as a received communication; only the authorized
`SubjectFrame` goes to Ollama. The model reply is deliberately **not**
re-ingested as lived memory, speech, action or world truth. There is not yet
an autonomous wake schedule or tool executor in this CLI. The first
lineage source remains PretoriusBrain, never the renderer.

The donor remains an optional source package rather than a required global
dependency because research and existing approved v0.5 brain runs must remain
stable. The exact donor commit is tested in the dedicated cross-repository
workflow. The version check rejects unreviewed package versions, while commit
pinning during deployment is still the installer/operator's responsibility.

## Bypass inventory and safe claims

The ordinary `doctor-lives` CLI can print diagnostic/render data without
Synthetic Ipseity, but does not invoke a language model. It must remain an
engineer CLI, not become the renderer used by the local hosted experience.
`PretoriusBrainPort.render_request` also remains callable by trusted Python
for research and existing tests. The `doctor-lives-local` path invokes a
model **only through** `SubjectOnlyRendererPort` after durable admission.
Other standalone research scripts may call models directly; they are not
authorized local-host entry points.

The implementation has not proven global no-bypass across hostile Python
code sharing process authority, an alternate host, or a future MMO adapter.
Before moving these PRs into production main, an independent review must
verify the actual deployed launcher, package/dependency lock, host action
capabilities, conflict recovery and all future model-context assembly.

## Crash-window local input journal (engineer-only)

The local CLI additionally maintains `local_turn_journal.sqlite3` and
`local_turn_mutex.sqlite3` in the caller-selected disposable state directory.
The journal records the exact human communication, a SHA-256 checksum,
an independent unique turn key, prior Doctor state digest, prior Doctor
waking and neural ticks, and the lifecycle of admission/publication/delivery.
The full message is restricted engineer-side data; it is NOT passed as raw
journal content to the renderer or treated as Pretorius's internal thought.
The SHA-256 checksum is an accidental-integrity check, NOT a signature,
provenance credential or privacy-preserving encryption.

A separate SQLite `BEGIN IMMEDIATE` lease serializes the entire local
turn across trusted host processes without holding locks over the actual
Doctor memory database, organ state or renderer outbox. Each journal stage
commits independently, so a process crash releases the mutex while leaving
a durable recovery cue.

The source of a newly ingested user message has a unique
`local-conversation:<turn-key>` engineer identifier. On `--resume`, the
runtime searches the **actual Doctor BrainStore** for that exact source:
zero matching events may be retried only when the Doctor state digest has
not changed; one matching event cannot be re-ingested; more than one
fails closed. A recovered event must have the expected next waking tick and
an advanced persisted recurrent tick. This extra check detects a crash
after the Doctor SQLite event write but before its neural checkpoint is
saved. In that situation the runtime refuses to claim a complete turn.
Do not resolve it by blindly re-running the ingress.

The session then either publishes through the reviewed Ipseity organ or
reuses its existing durable outbox. If the outbox has already acknowledged
the response but journal completion was interrupted, `--resume` clears the
intent **without repeating model inference**, and reports that the old
text cannot be replayed from this interface. If the model call failed,
`--resume` can retry a leased frame only after its lease expires.
Inference delivery remains at-least-once, not exactly-once.

The tests deliberately interrupt before Doctor admission, between
admission and publication, after outbox commit, after renderer
acknowledgement, and after SQL admission but **before neural stepping**.
They assert no new invented lived memory, no duplicate incoming message,
and no silent success attribution from a half-saved brain.

Limitations: caller authority remains trusted in-process Python. The
unique turn key prevents accidental replay but is not an authenticated
external request token. Separate SQLite files still cannot be committed
as one cross-database distributed transaction. Recovery of a partially
written canonical Doctor brain/neural checkpoint requires an explicit
separate engineering repair, not this interface.

## Real Ollama smoke: bounded-generation gate, 2026-10-12

The first **actual** CPU Ollama invocation reached the local HTTP endpoint
through the complete PretoriusBrain -> SubjectFrame -> SyntheticIpseityOrgan
-> durable outbox -> SubjectOnlyRendererPort -> LocalOllamaRenderer chain. Its
first response completed (1,777 characters), but the second inference
timed out after 180 seconds. The control was NOT a subject-access failure;
the old adapter omitted an output-token limit. The previous failing run is
https://github.com/Azimn/The-Doctor-Lives/actions/runs/38210025588 .

The reviewed v0.9.11 donor candidate now requires `num_predict` (64-token
default, user-settable 1..512) without changing the subject-only input.
This was retested with the genuine Ollama v0.40.3 binary (official-release
SHA-256 checked), locally downloaded `smollm2:135m` (270MB), and a
temporary standalone Pretorius brain plus actual SQLite stores. No mocked
responses were used.

**Observed passing run:**
https://github.com/Azimn/The-Doctor-Lives/actions/runs/38210400785
at Doctor commit `977d50795fb6559ccda290c7d122edcd5a81d806`
and donor commit `e2d1dc3978c952e59d270a29e84704c8a1fe264a`.

- Two of two actual HTTP generation calls returned nonempty model text.
- Turn 1: 3,200 subject-input characters, 307 model-output characters.
- Turn 2: 2,937 subject-input characters, 311 model-output characters.
- Both recorded real HTTP requests used only `model`, `prompt`,
  `stream` and `options`, with the prompt unchanged by hidden state.
- The tests excluded specifically enumerated engineer-only fields, original
  event identifiers, journal names, and neural checkpoint diagnostics.
- Two incoming human statements were separately persisted as external
  experiences. The recurrent substrate advanced. Generated model speech
  was not unilaterally admitted into lived autobiographical memory.

These are real execution facts, not human-quality dialogue evidence. The
model was chosen solely to keep smoke inference affordable on an ordinary
CPU GitHub Actions runner. No subjective awareness, protected autonomy,
independent action or superior character fidelity is claimed.

The test is deliberately a one-shot push workflow that runs again only if
the dedicated workflow YAML is modified. It is also available for manual
dispatch. Keeping inference separate from ordinary test CI avoids burning
computing resources on each research commit.

## Static entrypoint and model-ingress inventory

`python tools/ipseity_entrypoint_gate.py` fails when an *unreviewed
provider/process import* is introduced into the shipping Python package,
and verifies the declared CLI / subject-only renderer contract. Its
reviewed, explicitly exempt research-only paths are:

- `doctor_lives/vector_fly_eval.py`: urllib-based external inference
  benchmarking, including a direct `/api/generate` call. **Research only**.
- `doctor_lives/neural_characterization.py`: subprocess instrumentation.
  **Research only**.
- `doctor_lives/neural_lesions.py`: subprocess instrumentation.
  **Research only**.
- `doctor_lives/neural_robustness.py`: subprocess instrumentation.
  **Research only**.

`doctor_lives/cli.py` can serialize an engineer-oriented render request
through `brain.render_request(...).to_dict()` but does not itself invoke
an inference provider. `doctor_lives/chassis.py` exposes the same
renderer-neutral API for trusted third-party consumers. **Neither is
authorized as a model-ingress route for the released character.**
The protected `doctor-lives-local` entrypoint currently invokes an actual
model only through Synthetic Ipseity's subject-text outbox.

This scanner is a *change-control guard*, NOT a sandbox or proof of global
non-bypass. Dynamic imports, a malicious package, direct Python access to
brain internals, research scripts intentionally using standalone providers,
and future Village hosts remain outside its authorization guarantee.
Promotion requires a separate independent reviewer of host authority,
model transport and action/receipt boundaries.

## Upstream v0.9.11 action-cycle adoption, 2026-10-12

The canonical independent Synthetic Ipseity `main` changed to
`b02d50c5b63f5402bc8306481decae6f43e641b2`, with
`src/synthetic_ipseity/laboratory_action.py` and its
`AUTHORIZED_LABORATORY_ACTION_V0_9_11.md` reference action gateway.
Upstream release does NOT yet contain the trusted Doctor preprojected
subject-event adapter, drained-outbox publication or the bounded
`num_predict` real Ollama fix. Both branches initially declared version
0.9.11, so choosing package by version number alone would lose mandatory
Doctor behavior.

The dedicated donor PR #31 now merges the upstream main as a second
parent, with no conflicting changed paths and without modifying canonical
main. Combined donor revision:
`e2d1dc3978c952e59d270a29e84704c8a1fe264a`. It contains
upstream action-gateway source and tests, all upstream documentation,
the annotation-audit fix, and all previously tested Doctor-required
first-person and inference/transaction controls. GitHub Actions
https://github.com/Azimn/synthetic-ipseity/actions/runs/38211446442
passed all three tested Python versions on that exact combined revision.
Both Doctor CI workflows now install that commit, not an unreviewed floating
version or previous donor candidate.

**Causal boundary:** Upstream reference action gateway recognizes exactly
`inspect_lamp`, `open_drawer`, and `inspect_drawer` in its own tiny
SQLite demonstration world. It cannot be assumed to own or manipulate the
actual Pretorius-Laboratory. In a controlled interoperability test,
`tests/test_ipseity_action_reference.py` admits a genuine Doctor
`SubjectFrame` to that reference gateway, proposes an allowlisted drawer
open, verifies a real donor SQLite effect and new host-attested first-person
feedback, and separately denies an invalid multi-field model proposal.
The test **also verifies** that neither effect nor model output silently
writes autobiographical memory to Pretorius's real brain.

This is an interface compatibility gate only. The real Pretorius Laboratory
still owns its action catalog, environmental receipts, world mutation and
authoritative feedback. A later integration must map the Doctor-authorized
concrete action and object to *that* existing world interface, persist the
actual world effect with a replay-safe action key, then admit only the
world's genuine receipt as a new protected perception. Do not point the
model at toy reference tables and claim the permanent lab is alive.

The upstream `AuthorizedLaboratoryTurn` is a reusable proof of
transaction ordering and action/feedback admission, not proof of a
character-appropriate model policy. Preserve the already observed
negative comparisons in the lab: donor compatibility tests cannot
establish autonomous choice or neural superiority.

## Standalone RC1: host-confirmed text emission and self-speech, 2026-10-12

`doctor-lives-local` is now a **text-output host**, not an unverified
renderer that merely prints after its conversation has been marked delivered.
With `--say` (or `--resume` when safe), the CLI holds its existing
single-writer local-turn lock and performs this sequence:

1. Doctor ingests a real human message through his existing first-person
   ingress projection and commits the actual recurrent step.
2. Synthetic Ipseity admits Doctor's own `SubjectFrame` to its outbox.
3. Before acknowledging the organ's delivery lease, the trusted renderer
   records the model response and SHA-256 digest in the **engineer-only**
   `speech_emission.sqlite3`. An interrupted lease can reuse that exact
   response rather than rerunning the model.
4. The CLI hands text to an explicitly trusted output sink. The default
   terminal sink reports ACK **only after a successful stdout write + flush**.
   The journal records `prepared -> emitting -> acknowledged`. It never
   treats the model's own report of having spoken as proof.
5. Only after this ACK does Doctor commit a first-person record of his own
   *actual written utterance*: `I see my words appear in the conversation:
   “…”.` This is first-person attribution of a **written** text effect,
   not an assertion of acoustic hearing, remote receipt, intent, factual
   accuracy or anything physically uttered. Malformed or hostile model
   wording is not copied verbatim into autobiographical memory; the host
   uses a safe generic description of the confirmed emission instead.
6. The local-turn journal closes the turn. After an interrupted post-ACK
   memory write, `--resume` checks the canonical Doctor source and neural
   tick and never emits or records the speech twice.

This changes the **CLI path only**. Existing `local_turn(..., emit=None)`
remains a deliberately non-emitting research API and does not certify
speech or create self-speech memory. Other renderers never gain implicit
authority to turn generated text into observed events.

**Crash semantics and nonclaims.** If an output sink raises an error or dies
after the journal records `emitting`, the terminal output MAY have appeared.
Because stdout has no idempotent remote receipt or rollback operation,
automatic replay is forbidden and manual reconciliation is required. A
completed ACK is a successful **local stream flush**, not evidence that a
human saw the output, and not a network-delivery guarantee. Database
journals still are not one atomic transaction; explicit source checks
prevent duplicate canonical memories after most ordinary local restarts,
while irreconcilable neural checkpoint faults halt the session. This
provides safe at-most-once *automatic emission attempt* per local turn
and a source-grounded memory of confirmed writes, **not** exactly-once
end-to-end delivery. Tests inject failures before organ ACK, after output
attempt, after output ACK, and after canonical self-speech memory commit.

The permanent physical laboratory remains out of scope for Standalone
RC1. The independent donor's tiny drawer/lamp reference world is not
an authoritative Pretorius laboratory and is not used by this launcher.

### Standalone-release acceptance gates still open

- Independent review and safe merge order for Doctor PRs #55, #56
  and donor PR #31, with exact source pins after merge.
- Fresh Windows local-install and startup on a disposable state
  directory, offline/failed Ollama restart, and documented repair for
  deliberately unresolved emission attempts.
- Restore test verifying **all** Doctor neural/SQLite, Ipseity,
  turn-intent and speech-receipt databases survive as one consistent
  bundle; no unsupported cross-DB exactly-once claim.
- A suitable local model, stable character prompt policy without
  unearned background data, and an acceptance corpus testing
  dialogue continuity and self-attribution across sessions.

These are deployability gates, not a mandate to introduce a new
cognitive architecture, move the laboratory, or train a new neural model.
