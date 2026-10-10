# Eidolon D2: Mnemosyne Loom and Chronos Coil, source-bound prospective attention

**Status:** preregistered *engineering construction* contract. Not independent evidence of character-continuity improvement, learned neural persistence, semantic recollection, or a trained future predictor. **Date:** October 9, 2026 (US Central).

## Why this increment

The successful Eidolon E2 no-cue construction isolated a carried-state channel, but its four action targets were hand-assigned and its decaying trace was independent from verified memory and the commitments actually held by Pretorius. D2 now adds an *entirely read-only* bridge from the existing authoritative `BrainStore` to an engineer-only prospective-goal prioritizer. It must not start a second autobiographical database, invent memories from prompt text or mutate the live brain.

The original v0.1 and E2 source/results remain unaltered; this is an additional experimental donor, not a rewrite of historical evaluation.

## Declared representation and narrow algorithms

**Mnemosyne Loom** is a verified evidence view: it reads active memories that carry exact `lived_runtime_memory` autobiography classification and a referentially matching lived-runtime event, source, text, actor, confidence and timestamp. The source of actor attribution is the original event payload, not a substring in the memory. External statements, reconstructed/canonical/synthesized preawakening material, records with missing provenance, suppressed canon-conflict losers, mismatched records, and inactive records cannot become a lived witness. No guessed missing actor or source is permitted. The exact source event and memory identifiers appear only in the engineer audit plane.

**Chronos Coil** reads only the subject's existing open/overdue commitments. It estimates bounded prospective *attention priority* using goal importance, due tick, token overlap with validated lived-event text, and actor agreement. Explicit clock/tick ordering and actor identity are separate ablation dimensions. A candidate's evidence must be older than or equal to the decision tick; it may be older or newer than a commitment's creation depending on the actual sequence. If the goal requires an actor, a remembered event with a different actor cannot support it. The system does not infer a neural action label from a goal and does not write an intention back to `BrainStore`.

This is **a transparent deterministic rule-based baseline**. It provides provenance and temporal contracts to an eventual learned Noetic Crucible, but it is not claimed as that trained system.

### Candidate scoring (fixed engineering demonstration)

For each live commitment `c` at clock tick `t`:

```text
urgency(c,t) = 1 / (1 + max(0, due_tick(c) - t))
               if due_tick exists, else 0.25
baseline(c,t) = importance(c) * (0.20 + 0.80 * urgency(c,t))
overlap(e,c) = |content_tokens(e) intersect content_tokens(c)|
               / max(1, |content_tokens(c)|)
support(e,c) = overlap(e,c) * confidence(e)
               only for verified lived, source-matched, actor-valid evidence
priority(c,t) = min(1, baseline(c,t) + 0.45 * max_e support(e,c))
```

Stopwords, actor-name tokens and all numeric caps are fixed in code and documented. A matched no-history arm sets `support=0`; a no-temporal arm sets urgency to 0.25. These controls receive the same underlying store state. They differ only by an explicit lesion of one scoring family. This is a mechanical demonstration of information flow, not a discovery that history or time improves decisions.

## Assertions

1. A valid lived event and a commitment sharing actor and content produce a *source-cited* prospective priority change, while the same text attributed to a different actor does not.
2. An external person's claim that Pretorius previously did something is not valid lived evidence.
3. Reconstructed/canonical historical material cannot be promoted to lived evidence by being semantically similar. Inactive, provenance-corrupted and canon-suppressed records are excluded.
4. Moving the current clock toward a due tick can change urgency, and the no-temporal ablation eliminates that part of the difference.
5. Resolved commitments disappear from forecasts, not merely fall below a threshold.
6. Running the adaptor leaves database digest, neural tick, neural action distribution and renderer-facing Subject Frame unchanged.
7. Repeated calls on identical state produce identical content; actor/event/tick changes are recorded in the audit envelope, and no protected identifiers are projected to Pretorius.

## Prototype comparison battery and limitations

The synthetic development fixture uses a temporary real Pretorius brain with a 128-neuron fast test profile, two open commitments with different actors and deadlines, relevant lived and external testimony, actor substitution, due-date advancement, and matched no-history/no-time controls. Hand-authored fixtures provide *construction tests* only. No independent evaluation, semantic paraphrase holdout, recurrent synaptic lesion, E4 fresh decoder, learned planning, actual action selection or adaptive prediction is attempted here.

An honest outcome might be a priority change exactly matching the scoring rule. That is useful contract validation but **not** evidence that the full Eidolon architecture is better than the production policy or a graph retrieval baseline. The final report must include both positive and negative checks, actual CI run URLs, and any integration block.

## Production governance

Implement separately as `doctor_lives/eidolon_temporal.py` and export nothing from the public `doctor_lives` package by default. Use `PretoriusBrain.store` read-only; never alter `doctor_lives/cognition.py`, history files, source authorities, checkpoint formats, production policy or the renderer. No port or network actions. No new metadata gets access to the protected Subject Frame. Failure to verify the source event means exclusion, never guessing. Regression testing and shadow tests precede any downstream-action bridge proposal.

If this stage passes, the next credible step is a matched-clone *choice outcome* experiment comparing a learned recurrent agent against the deterministic temporal baseline on independently authored actor- and episode-disjoint future-intention cases. This D2 implementation alone cannot satisfy that gate.
