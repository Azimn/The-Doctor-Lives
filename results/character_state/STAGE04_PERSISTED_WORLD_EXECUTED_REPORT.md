# Stage 04 — Executed persistent test-world transitions and Pretorius lived-source drill

**Disposition: PASS for isolated world mechanics; no demonstrated autonomous decision or long-term persona improvement. Production HOLD.**

## Executed provenance

- [GitHub Actions run 38028153848](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028153848), source SHA `c9e388a410e73ebad32789efcbb0b838c1734000`. All **9 native/source/ledger adversarial tests passed** and the drill's machine assertions passed.
- Complete machine result: Actions artifact `stage04-persisted-world-witness-drill`, ID `11660908436`; `MEASURED_WORLD_HOST_DRILL.json` (2369 bytes), SHA256 `a6b1a935fc1feef5b87b90009b5b439017ec165a17bb5c5cb75c3d983b0cb3e4`. Artifact retained for 90 days.
- [Frozen protocol](../../docs/STAGE04_PERSISTENT_WORLD_HOST_PROTOCOL.md). Research sources: `world_host_ledger.py`, `world_native_bridge.py`, `run_world_host_stage04.py` and `tests/test_world_host_stage04.py`.
- No cloud LLM inference, no production brain modification, no P5 subjective source-monitor change.

## Separate deterministic world-state experiment

The host SQLite ledger began with a running laboratory clock and a sealed notebook, plus **no operation grants or Henry consent**. This time a separate persistent world database performed real scripted actions before generating a signed source event. The source was *not* simply fabricated inside Pretorius's memory table.

| Operation | Outcome | Grounded reason |
| --- | --- | --- |
| Stop clock without grant | DENIED | Actor lacks host permission |
| Stop clock with grant | SUCCESS | Clock changed running → stopped |
| Retry same stop-clock nonce | DENIED | Persisted nonce replay |
| Stop already stopped clock | DENIED | World state precondition |
| Inspect sealed notebook | DENIED | Sealed world-state object |
| Unseal without Henry consent | DENIED | Separate consent missing |
| Unseal after synthetic host Henry consent | SUCCESS | Notebook changed sealed → open |
| Inspect now-open notebook | SUCCESS | Host journal attests inspection without further state mutation |

Measured: **8 attempts; 3 signed successes; 5 denied; 2 actual state mutations**. The third success is an observed inspection action without a new changed world-state value; it must not be counted as a third changed object.

Two actual native Pretorius lived-memory records were admitted *after* signed host verification: the observed stopped clock and the open-notebook inspection. A refused sealed inspection admitted no first-person record. The host source and native memory link remained stable across repeated imports; revocation prevented future clock-memory *attestation* while leaving the already admitted historical memory intact.

A restarted host retained the serial world ledger, nonce replay registry, event-to-memory import binding and revocation. The final state was **clock stopped / notebook open**, world sequence 3, ledger integrity check PASS. Forged signatures, wrong actors, subjects/sessions, changed world/native rows and native import duplications were rejected in tests.

## Why the result is bounded

- This is a **researcher-authored deterministic simulator**, not an independently operated Evennia service or genuinely autonomous AI gameplay. The test controller selected the actions.
- The registered Henry consent is **scripted host test data**, not permission from a real external partner. Host administration/grant functions do not yet authenticate real human operators.
- HMAC attests possession of the fixture key within its trust domain, not independent external-world truth; the key is known in the research runner and host-control writes remain privileged.
- P5's subjective recollection source estimation is still separated from engineer-only objective source provenance. No raw MAC/ledger fields cross the subject renderer.
- Check-then-write sequencing has not been hardened for arbitrary concurrent multi-process world actors. A crash between native memory commit and host import-marker commit is detected as a conflict and fails closed, rather than silently reconciled.
- No LLM selected an action; no evidence yet that PHASE outperforms flat evidence organization in independent world tasks. No long-term identity, cross-model persistence, real external partner behavior or consciousness claim.

**Next gate:** Source-matched flat versus PHASE versus chronological-context model-selected world actions against the same permissions and costs, then source-disjoint independently authored tasks, actual external world authority, and blind human adjudication. Production HOLD.
