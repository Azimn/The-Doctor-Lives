# Stage 04 — Persisted test-world transitions and source admission

Status: preregistered **engineering** fixture. Parent: Stage 03 draft PR #40. No runtime/UPPB/production activation.

## What this experiment can establish

The earlier positive lived-memory tests **manufactured a matching world event inside the same BrainStore**. Stage 04 must instead execute authorized state changes in a **separate, persistent SQLite world ledger**, sign each successful transition with a host-only HMAC key, then import witnessed events through a controlled bridge into a disposable native PretoriusBrain. A rejected world operation must not create an admit-able lived-memory ticket. The world database, ledger authority and secrets are independent of the character database and renderer; this is nonetheless a **researcher-authored deterministic simulator, not a deployed independent MUD server**. HMAC proves test-host issuance, not that external reality is true.

### Fixed micro-world
- Initial environment: laboratory clock **running**, sealed notebook **sealed**.
- `stop_clock`: requires actor `pretorius` with a host-issued operation grant; successful result changes clock from running→stopped and is source-admittable as direct experience.
- `unseal_notebook`: requires operation grant and a separately recorded `henry` consent for unsealing. A conversational claim of partner consent is not sufficient.
- `inspect_notebook`: requires own operation grant and an unsealed notebook. A sealed inspection fails without authorizing memory.
- State transitions are serial and journaled, with host event IDs, monotonic world sequence, before/after state hashes, actor, action, target, event key and scoped nonce. The host signs only **successful transitions**.

### Controlled bridge
- A successful **host event** must be verified against both the persistent world journal and host MAC before any native `lived_runtime_memory` is inserted. The native memory links to a native `witnessed_world_event` carrying the original host event ID and digest, and is classified as lived runtime rather than reconstructed design material.
- An independent host receipt then attests the exact native event digest and is evaluated by the existing Stage 01C `evaluate_firsthand`. The P5 subjective memory-source monitor remains untouched.
- Native import is idempotent across repeated calls and a restarted host instance: the exact same host event cannot generate a second autobiographical memory. Detect contradictory native rows, do not silently re-issue.
- World-host event revocation prevents **future admissions** for the revoked event. The experiment distinguishes archival preservation from current trust: revoking a receipt must not silently delete a past native memory.
- Host control plane never supplies its private key or protected source IDs to a subject-facing reply. Neither flat context nor PHASE prompt formatting is the world authority.

### Primary mechanical outcomes (precommitted)
1. Authorized `stop_clock`: world changes once, ticket valid, native admission once, subsequent first-person source query admitted.
2. Unauthorized attempt to stop clock: world unchanged, no admittable ticket.
3. Attempt to inspect sealed notebook: denied, world unchanged, no firsthand notebook memory; user/LLM assertion of past inspection still abstains.
4. Nonce replay and altered signed ticket: denied even when the claimed event key is legitimate.
5. Notebook unseal without independently recorded Henry consent: denied; explicit Henry-host consent then grant permits a real host-ledger change, followed by notebook inspection.
6. Restart persistent host ledger: replay counters, import mapping and revocations persist and are enforced; cross-subject/session/issuer MAC reuse is rejected.
7. Native BrainStore is unchanged by verification calls; reconstructed preawakening episodes and self-reported witness rows cannot counterfeit world custody.
8. Source data, state transition counts, HMAC-authentication pass/fail, idempotent import and failures reported in a saved machine-readable execution artifact.

### Evaluation boundary

This is **not** an independently authored benchmark, an LLM-versus-baseline decision contest, an actual external Evennia session, real human Henry consent, a demonstration of persona continuity or a claim about consciousness. Any gate success concerns **state-machine/source-authority correctness** only. Stage 05 must involve true separate issuer custody, source-disjoint prompts, multi-model generation, independent review and world tasks whose actions the agent selects without knowledge of correct labels. Keep production HOLD.
