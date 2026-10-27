# Pretorius: six-organ mechanism adoption decision

Status: **Architecture decision, not an implementation or certification**. Date: 2026-10-26. Integration home: draft PR #89. Existing three-organ and CASCADE previews remain intact.

## Decision

PR #89 is the **single-brain integration skeleton**, not the finished organ implementation. PRs #57/#59/#60/#61 are **reviewed candidate mechanism sources**; they are not a second brain and must not be blindly merged or used as competing production entrypoints. Original main and its frozen backup remain untouched. The canonical PretoriusBrainPort, SQLite evidence store, recurrent substrate, and source-authority rules remain sole owners of identity, memory, cognition and persistence.

An organ graduates from `mapped` / `adapter-backed` to `implemented` only after a real, load-bearing mechanism is wired to a restricted host boundary, survives relevant restart/interruptions, and passes a matched causal ablation with measured outcomes. A method forwarding to a pre-existing brain method is **not** evidence of a new organ.

## Donor-to-organ integration order

| Organ | Current #89 seam | Candidate source | Required causal test | Graduation blocker |
| --- | --- | --- | --- | --- |
| Sensus | existing world/tool single stream | #59 `three_organ_preview.py`, `preview_scene_journal.py`, pinned Sensus scene binder | matched conflicting versus uncontested multi-modal percepts; no false autobiographical admission; measurable downstream recall/decision change | donor version audit, veto provenance, first-person ingress and no-bypass |
| Mnemosyne | canonical memory and one-use host recall | #57/#59 endogenous recollection; #61 memory-conditioned Laboratory task | lesion, restoration, no-recall matched checkpoints; durable recall permits and restart | no extra memory authority; independence from host-authored question |
| Synthetic Ipseity | typed SubjectFrame only | #59 durable v0.9.11 admission/outbox, #60 optional governor | bypass rejection, replay/ack crash tests, model sees only admitted first-person frame | production host routing all renderer calls through one gate |
| Noesis | original recurrent decision and host pulse | #59 epistemic decision policy, #61 bounded action reservations | intervention changes selected proposal or verified action with same world state | distinguish endogenous selection from host-authored task controller |
| Affectus | existing needs-mediated readout | separate Spinoza transition prototype, **not yet adopted** | affect transition ablation changes downstream policy on matched percept/need states | versioned donor review, no second selector or false feelings |
| Corpus | existing body ingress; no actuation | verified Laboratory `DoctorHomeBridge`, #61 world action receipts | controlled bodily perturbation changes motivation/choice, consequence memory survives replay/restart | physical authority remains Laboratory; no fabricated motor initiative |

## Integration acceptance sequence

1. **D2 Laboratory parity:** retain #89's bridge to the actual Laboratory; run source-verified observe, move, bodily consequence, replay, restart and no-double-admission tests with pinned donor. CI green must include non-skipped Laboratory tests.
2. **Sensus causal acquisition:** port #59's pinned donor adapter into the #89 host without changing the canonical brain or accepting conflicted observations as facts. Add matched conflicting/uncontested fixtures and receipt-linked evidence audits.
3. **Mnemosyne endogenous access:** port host-authoritative, genuinely self-selected recall from #59; preserve one-use state-bound grants. Compare memory lesion, restoration and no-recall.
4. **Ipseity enforcement:** route all production model-facing reads through one durable admission/outbox; reject direct engineer telemetry, renderer self-authority and replay after interruption. A Python `_port` convention alone is not isolation.
5. **Noesis and Corpus closed loop:** connect a selected tendency to a separately authorized Laboratory action, durable world receipt, admitted first-person consequence, and subsequent memory-conditioned decision. Distinguish actual internal selection from host-supplied task policy.
6. **Affectus transition mechanism:** evaluate the independent donor in isolation, then introduce only if it changes behavior beyond baseline needs readout without taking over the neural selector.
7. **D11 superiority gate:** paired preserved checkpoints; equal model, seed, schedule, sensory inputs and world state; independent holdouts; failure, safety and continuity metrics; ablations per organ. Preserve a negative result rather than relabeling it success.

## Evidence and unresolved claims

- PR #59 implements a Sensus conflict veto, endogenous cue selection and durable Ipseity rendering on an opt-in experimental host. It is not automatically present in #89.
- PR #60 adds an optional self-reference governor after the Ipseity boundary; it is not a seventh organ.
- PR #61 adds a bounded, **host-authorized** Laboratory task controller with durable action receipts. Its 3/3 memory, 1/3 lesion, 3/3 restoration result does not establish superiority to its 3/3 simple receipt-ledger controller baseline.
- #89's `SixOrganRuntime.bind_laboratory` is a real bridge into the existing Laboratory, not yet a full autonomous closed loop. CI success is necessary, not sufficient, and skipped optional-dependency tests do not count as executed Laboratory evidence.
- No claim that Sensus donor, Affectus transition donor, global D3 no-bypass or D4–D11 are implemented in #89 is authorized by this decision.

## Stop conditions

Do not merge to main, switch production entrypoints, or mark any organ integrated if the donor source hash is unreviewed, an external observation is promoted to lived memory without verified provenance, a model can access engineer-only diagnostics, world actions lack receipts, or a parity regression appears. Do not create a second persistent brain, competing policy authority, or per-organ identity database.
