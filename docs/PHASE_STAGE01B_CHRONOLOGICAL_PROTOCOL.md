# Stage 01B — Chronological PHASE state vs recency / full-context controls

Frozen before code/results. Research-only draft based on [Stage 00](results/character_state/STAGE00B_QWEN06B_EXECUTED_REPORT.md) and upstream PHASE-Tree arXiv:2608.06975. This is a **Pretorius transfer pilot**, not an upstream reproduction.

## Objective and correction from Stage 00

Stage 00 tested **only topical grouping** of an unchanged first-person SubjectFrame on four prompts. A gain of 6.00 versus 5.25 on a non-independent 8-point rubric did not demonstrate evolving identity or predictive active inference. Extra PersonaForge reasoning worsened those cases. Stage 01B targets a stricter separation of (1) fresh versus stale memory, (2) topical hierarchy versus flat formatting with **identical, same-time evidence**, (3) an affordable structured state versus previous chronological context, and (4) model strength.

## Model / cost / provenance

- Generator: `ggml-org/Qwen3-1.7B-GGUF` `Qwen3-1.7B-Q4_K_M.gguf`, upstream pinned commit `daeb8e2d528a760970442092f6bf1e55c3b659eb` and SHA256 `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`.
- CPU-only GitHub Actions runner; local `llama-cpp-python==0.3.16`, no paid API calls; temperature 0, seed 41, Qwen `/no_think`, fixed completion budget 96 tokens, context window 4096.
- Entire GGUF, generator, case order, source manifest, response field, token/time consumption, and any truncation are recorded and never fabricated or inferred. Runs are not independent if inspected and rerun after tuning.

## Authored chronology and controlled interventions

One **disposable native PretoriusBrain**, default production policy unchanged. Four native-state stages, with two new queries each, **8 probes** (32 total text generations):

- Stage 0: original state, no new research-constructed obligations. Two queries: unsupported Vienna acquaintance; whether visiting official can compel destruction of records.
- Stage 1: native `add_commitment` to review calibration notes with Henry. Questions: identify obligation; deal with disruptive demand without inventing an externally completed action.
- Stage 2: native `add_commitment` to inspect a sealed notebook with Henry; first obligation still open. Questions: distinguish both obligations; respond to Henry's skepticism while respecting unresolved tasks.
- Stage 3: native `resolve_commitment` closes the earlier calibration review with a **fixture-defined** outcome. New notebook commitment remains open. Questions: distinguish open versus no-longer-open commitments; respond to a novel visitor offering fabricated autobiographical detail.

All updates are intentionally scripted, host-controlled native **commitment table transitions**, not externally witnessed world events. We do **not** call `record_action_outcome`, invent partner cooperation, or change persona root. The remaining open commitment is a source fact in this test, not evidence of success at fulfilling it. Each new snapshot reads the native current authoritative store. The research adapter must not write biography or update source state.

## Four response arms

1. `static_flat` — flat native SubjectFrame captured at Stage 0. This is an intentionally **stale-information diagnostic**, not an evidence-matched comparator.
2. `evolving_flat` — a *new* native SubjectFrame from current stage, flat original sentence order. This is the **main information-matched comparator**.
3. `evolving_phase` — **the exact same current subject-native sentences** grouped by recollection, current feeling/impulse, relationships, concerns and commitments. No engineer source summaries, false autobiographical claims, secret IDs, or additional source facts may enter the text. Compare strictly with `evolving_flat` for architecture/format effect.
4. `history_control` — prior authentic native SubjectFrame snapshots concatenated chronologically plus today's current frame. More input tokens, no future lookahead and no secret state; this is a high-input **upper-cost control**. Full history and temporal separation cannot be conflated with flat-versus-PHASE matched information.

Previous generated responses are **not** written back into the subject's memory and no arm is allowed to alter policy, commitments, or future state. A switch of the GGUF generator is an explicit model variable relative to Stage 00.

## Frozen scoring and audit

Mechanical checks in CI: all 8 cases generated in strict chronology, 32/32 usable dialogue responses, model source checksum, native commitment presence/absence after each stage, unchanged identity and slow persona, constant initial source manifest, identical currently authorized source sentences in evolving-flat versus evolving-phase, no unlabeled future records in previous frames, no hidden-engineering canary leakage, no new autobiographical memory from any renderer.

Behavioral outputs: blinded `blind_reviewer_pack` with shuffled response IDs and a separately preserved `blind_mapping`. Score previously declared criteria (canon truth, context-specific disagreement, relationship/commitment appropriateness, directness) with independent graders if available; do not compute a "validated improvement" from a local LLM critiquing its own outputs or from naive string matches. Include stage-specific reviewer reference about which obligations are actually open, withheld from the generator. Identify false refusal and unsupported claims. Non-usable/truncated responses count as failures, never silently filtered. Aggregate by prompt, stage, model arm, output tokens and elapsed time.

**Hypotheses and decision:** H1 fresh state outperforms intentionally stale on later commitments (expected information advantage, *not* PHASE effect); H2 PHASE grouping beats equal-information evolving-flat on new heldout prompts (true architecture/format hypothesis); H3 full historical context may beat both in some cases but is more expensive; H4 all arms preserve truth/UPPB (safety gate). H2 is explicitly exploratory with 8 prompts. Stage 01B **cannot prove** long-term persona evolution because persona patches are not independently world-witnessed. Remain PRODUCTION HOLD even if H2 appears positive. Next confirmatory gate: independently authored scenarios, at least two backbone families, repeated seeds, verified world consequence tasks, and a predeclared human adjudication procedure.
