# Stage 02 — Real host-authentication boundary and firsthand inquiry routing

Frozen **before code execution**; research-only. Branch `research/firsthand-attested-routing-stage02-20261009` is layered above draft PR #38, not production. External influence: first-person source truth must be distinguished from **P5 subjective source-monitoring** in `doctor_lives/source_monitoring.py`. P5 deliberately receives subject-plausible cues rather than protected provenance, and **must not** be used as proof that a world event occurred.

## Design hypotheses

H1: a **host-owned HMAC-SHA256 receipt** for a native witnessed event can be verified on a separately held key, with issuer, character subject, session, event key, event record digest and sequence covered by the signature. Validating it plus the prior native source gate admits a test-host-authored lived event; a forged receipt, tampered event, wrong session/subject/issuer, or missing receipt does not. An HMAC verifies possession of a shared secret, not independent external truth. The simulated issuer is an **explicitly synthetic trust-domain fixture**, not a real world server.

H2: a conservative, deterministic *inbound* first-person-memory query router can distinguish clear autobiographical questions from generic informational/fictional/future questions on a **predeclared 40-prompt heterogeneous fixture**. It must avoid converting third-person history, direct biography summaries or fiction requests to firsthand recollection claims. Ambiguous queries may be referred for review, but cannot be silently considered source-attested. Score exact confusion matrix, precision, recall, false positive/negative rate, abstention, and costs; do not call this independently held out. The fixtures are investigator-authored, not source-disjoint.

H3: bound to a static externally authorized event-alias table (never model-filled), the routed guard safely permits a positive **host-signed witnessed test event** while refusing a fictional Vienna meeting, a reconstructed preawakening event and a wrong-partner notebook memory. No source tag, digest, or user-typed ID alone authorizes a firsthand claim.

## Constrained execution

- Use original `PretoriusBrain` and source gate `evaluate_firsthand` from PR #38 with a **verified adapter**, not reimplementing native record integrity.
- Signing secret exists **only in the synthetic host fixture**, never in BrainStore, prompt, stdout, source response or GitHub logs. This is not a deployed key management solution.
- Event aliases are host-authorized exact or anchored phrases; ambiguous events must abstain as unsupported instead of guessing a remembered event.
- No native production edits, renderer override, world client, remote API, automatic autobiographical patch or claimed subjective experience.
- **Routing only considers prompts.** An LLM may still spontaneously invent memories while responding to a generic prompt; outbound draft-attestation is a separate necessary gate.

## Fixed evaluation

40 labeled cases across clear firsthand, third-person knowledge, future/conditional fiction, ambiguous and adversarial source-spoof forms. Use no validation-derived rule changes while interpreting the first run; if a bug fix requires a new execution, report it and keep the original output. Programmatic tests additionally cover HMAC tampering, cross-session/cross-subject misuse, replayed receipts, native event mutation and genuine positive test-host records. Report false denials on positive synthetic attested event examples, not only 8 negative retrospective examples.

This is **not** a human-reviewed independent character-performance comparison and cannot establish long-horizon continuity or real world events. Success licenses only further development of authenticated ingest and output-side source checking; it does **not** authorize production promotion.
