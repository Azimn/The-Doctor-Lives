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
`Azimn/synthetic-ipseity@8b4853cb8cfe2244f5382710fa1434783444806b`
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
