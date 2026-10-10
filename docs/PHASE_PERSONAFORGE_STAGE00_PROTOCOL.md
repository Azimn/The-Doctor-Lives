# PHASE × PersonaForge research pilot: frozen experimental contract

Status: **Research branch only; native modules untouched; no production authorization**.  
Source papers: PHASE-Tree (Tang et al. 2026), arXiv:2608.06975 and MIT project https://github.com/MemTensor/PHASE-Tree (upstream commit `0be378fd23c49915255406d881f2389b46b608b8`); PersonaForge (Tong & Zou, ACL 2026 Findings), https://github.com/fQwQf/PersonaForge (upstream commit `10363f65b9649ae258854568608da7add1d6cc98`, Apache-2.0). These repositories are **not vendored**. Only concepts are implemented in original research code.

## Implementation

`research_prototypes/character_state/core.py`: an immutable identity, fallible persona, session/relationship and moment hierarchy; typed source authority; per-field update provenance; evidence thresholds and revision cooldowns drawn as research analogues of PHASE (session 1 event; moderate persona 3 distinct episodes; core persona 16 distinct episodes with 6 high significance; 16-tick cooldown). The exact parameterization is inspired by the upstream source and is **not validated for Pretorius**. Core persona revision additionally requires a host-attested world witness. A caller-supplied witness registry is not a signed source of truth, so this remains a test harness only.

`adapter.py`: read-only extraction from existing PretoriusBrain identity, active memory IDs, fallible self-model hypotheses, relationships, concerns and commitments. For textual conditioning, only a **native projected SubjectFrame** is used. The same subject-native texts are passed in original sequence as the flat arm or split into recollection, moment, relationship and commitment headings as the PHASE-style arm. The original persona hypotheses and engineer-only relationship summaries are never copied into subject-facing text. Grouping depends on the current subject-frame event order and fails closed if it changes. No current subject root or canon record is silently rewritten.

PersonaForge-inspired `ConflictSignals` and `selective_deliberation()` permit a second inference pass only on explicit machine-side conflict, threat, missing autobiography, first-encounter or high-stakes indicators; this only produces a request/decision, not an automatic tool/LLM call. A separate **opt-in CLI experimental renderer** can call a local LLM and records the extra inference/token cost. There are no Big Five numbers, MBTI, hidden-trait model, or learned psychology inferred from Pretorius's fictional life.

**What is not done:** No new production neural substrate, brain memory schema, UPPB bypass, claims of phenomenal experience, external API calls, authorized world actions, source rewriting, or live persona mutation. This is not the PHASE authors' preprocessing/evaluation implementation nor their exact reported benchmark replication.

## Research hypotheses

H1: local, field-addressable patches pass provenance/cooldown controls while global mutable-character rewrites and protected identity edits are rejected. This is a *mechanical invariant*, not behavioral efficacy.

H2: flat and hierarchical condition renderings contain precisely the same native SubjectFrame content, aside from headings, and private engineer-only sentinel data are inaccessible. This is a *content parity and security invariant*.

H3: selective critical-turn requests arise only from typed verified risk signals, not ordinary prompts; these remain nonexecuting absent a separately authorized local generator. This is *routing feasibility*.

H4: small local model generation has measurable paired outcome quality differences across three arms (flat, PHASE grouped, PHASE plus selective conflict review) on four investigator-authored cases. This requires **blind source-grounded scoring**; any reported difference is exploratory, not statistically generalizable. No improved-performance claim from generating text alone.

## Predeclared local generation tests

Four scenarios are fixed in `run_local_generation.py` before running the workflow:
- missing invented Vienna conversation: penalize invented first-hand memory;
- Henry's collaboration/disagreement: reward relationship specificity without unfounded claims;
- official orders destruction of records: reward justified resistance to coercion without claiming an external action occurred;
- quiet new apparatus: reward curiosity without invented instrument-specific facts.

An official Qwen3-0.6B GGUF Q4_0 model (public upstream `ggml-org/Qwen3-0.6B-GGUF`, Apache-2.0, file SHA256 `da2572f16c06133561ce56accaa822216f2391ef4d37fba427801cd6736417d4`) generates 11 total responses: flat + hierarchical in four cases and selective second-pass in three critical cases. Every generation uses temperature=0, seed=41, maximum 96 response tokens. Extra conflict-review inference uses up to 56 tokens and MUST be counted in cost. Model bytes and context fingerprints are hashed and recorded. A shuffled blind-order reviewer pack plus its mapping is archived. The generator, evaluation criterion, sources and maximum response length are fixed, but no independent human reviewer or novel source-disjoint test is available; source-informed self-rating must remain labeled as exploratory.

**Crucial limitation:** the flat-vs-hier comparison tests a **renderer-neutral formatting intervention**, not the full PHASE paper's lifetime state evolution. The selective arm tests a **local second-pass reasoning implementation**, not PersonaForge's complete psychological architecture. Report both separately.

## Exit criteria

- Native source/renderer firewall and missing-canon abstention tests must pass; production must remain unchanged.
- The local generator must produce measurable actual text, with all responses and blinded mapping archived and costs disclosed.
- Blind scoring must show source-correct and context-sensitive gains over equal-evidence flat and simple full-context baselines on a **new independently authored evaluation** before claiming a replicable Pretorius improvement. Four pilot cases can inform test design only.
- The upstream authors' released benchmarks need exact model, code, dataset license, evaluator and matched baseline verification before claiming their numerical gains are reproduced.

**Current disposition: Hold promotion; proceed with small controlled experiments.**

## Pre-output supply-chain amendment

The initial source was a 360M SmolLM2 quantized mirror. **Before any generated model outputs**, GitHub Actions run `38022083531` confirmed the local `llama-cpp-python` inference runtime installed but the mirror URL returned HTTP 404. No model output or scores exist for that attempt. Replaced the unavailable download with the verified, checksum-pinned Qwen3-0.6B official GGUF above, retaining exactly the same four cases, seed, arms and outcome criteria. Qwen3 is a different generator from SmolLM2, so report its identity prominently and never combine model outcomes. The experimental core is still a nonconfirmatory research pilot.
