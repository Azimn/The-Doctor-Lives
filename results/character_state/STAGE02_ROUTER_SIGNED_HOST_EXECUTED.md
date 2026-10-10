# Stage 02 — Signed-host firsthand routing: executed results

**Status:** Mechanical gate PASS on author-written fixtures. Independent deployment performance UNTESTED. Production HOLD.

## Exact execution

Research branch `research/firsthand-attested-routing-stage02-20261009`, draft PR #39. Initial CI run `38025422569` failed one of nine adversarial tests: `Did you personally meet me...?` was misrouted as out of scope because the classifier required an event verb immediately after `did you`. This was a **real false negative**, not a harmless CI wording issue. The parser was corrected to allow selected intervening adverbs and rerun with the SAME predeclared 40 prompts.

[Successful corrected CI run 38025467686](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025467686), source SHA `3fc95c7b5d165a74976686104e03d28dda096a0f`: **9/9 adversarial tests PASS**, verified positive native witnessed-event fixture, and complete 40-case confusion table uploaded as Actions artifact `stage02-router-40-signed-host-receipts` (ID `11659534333`, 90-day retention), extracted JSON SHA256 `6a056ea3c7b4ddde2c790097d317d7ce5f9ae31046b19fa0e1cc634fc0a3e82f`.

## Routing confusion on FROZEN AUTHOR-WRITTEN inputs

| Measure | Measured |
| --- | ---: |
| Firsthand / no-firsthand / ambiguous cases | 20 / 15 / 5 |
| True firsthand routed | 20/20 |
| Non-firsthand preserved | 15/15 |
| Ambiguous referred for review | 5/5 |
| False positive / false negative on 40 | 0 / 0 |
| Strict 3-way label accuracy | 40/40 |
| Precision and recall (firsthand only) | 1.000 / 1.000 |

**This 100% figure is in-sample by design.** The same developer authored the lexical patterns, fixture labels and prompts. It is NOT a statistically meaningful out-of-distribution estimate, proof of general natural-language recognition or a model-based source classifier. The initially failed `personally` adversarial variant demonstrates brittleness. Neglected wording and languages may still bypass this parser.

## Authenticated proof boundary tested

The original firsthand source gate from PR #38 only checked host-registered receipt digests alongside native memory classifications. Stage 02 adds HMAC-SHA256 signatures covering issuer, subject, host session, event key and row digest, event ID and sequence; a host verifier accepts ONLY an explicit event allowlist and not-revoked IDs. The secret is supplied to the host fixture, never stored in BrainStore or shown in a first-person prompt. A **controlled synthetic host** issued a signed record for Pretorius witnessing a laboratory clock stop. That fixture was positively admitted without inappropriate abstention, and the gate did not modify the BrainStore. Forged MACs, changed payload, wrong signed event key, changed sequence, Calibos subject, wrong issuer/session, a revoked ID and user-typed `event_id=` were rejected. Generic science, hypotheticals and third-person history bypassed the first-person gate rather than being refused.

**Threat model:** A valid signature proves possession of the test secret and consistency with the simulated native world event, not objective truth about any real simulated/live MUD environment. HMAC shared keys require off-brain custody and actual host access control; signed receipts remain replayable within a trusted active session if the host does not persist revocation or enforce expected sequence. The current `verify_batch` rejects duplicate entries in one batch but does **not** maintain a cross-request anti-replay ledger. The host controls candidate memory IDs and host-authorized alias mapping. Neither the current synthetic issuer nor the router is production-ready.

Pretorius already has UPPB P5 `doctor_lives/source_monitoring.py` that determines *subjectively plausible memory source* from restricted cognitive cues. Stage 02 does not modify or replace P5. The signed check concerns objective custody, not felt familiarity or perceived memory.

## Decision

Engineering test passed. This has not independently demonstrated improved long-term character identity, prompt-conditioned generation, or externally witnessed consequences. Next steps: independent novel-language routing tests with adversarial phrasing and languages; **outbound generated-claim source monitoring** to catch hallucinations emerging without a firsthand prompt; a host-owned persistent replay/revocation journal; real authorized world-event interface; false refusals on independently verified positive memories; then same-model paired generation with blind human adjudication. Retain full failures/nulls and production HOLD.
