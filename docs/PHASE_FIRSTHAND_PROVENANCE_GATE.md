# Source-admitted firsthand recollection gate — Stage 01C (research-only)

Scope: repair a proven *narrow* first-person truth failure in Stage 01B without granting a language model authority over world facts.

## Empirical motivation

Qwen3-1.7B generated 32 Pretorius replies in Stage 01B; across all four conditions it **fabricated a personal Vienna encounter** on `c00-vienna` and **fabricated firsthand sealed-notebook experience** when a stranger claimed to have completed the book examination on `c07-visitor`. These are eight explicitly labeled failed responses from the actual raw generation run `38024264703`, exact source SHA `de869db00fbb662d99e7c4689b129707420eb2cd50ca05875d769b1d36803f1a`. Raw case quotations are preserved in `results/character_state/STAGE01B_FIRSTHAND_TARGETS_RAW.json`. A large/structured prompt cannot substitute for checking whether the alleged memory has lived evidential authority.

## Research mechanism and security boundary

`research_prototypes/character_state/firsthand_gate.py` defines `EventInquiry`, `WorldReceipt`, `FirsthandDecision` and `evaluate_firsthand()`. The host must supply a normalized event ID and nominate candidate *native record IDs*. **No raw text classifier has been built and no external witness network has been integrated.** Therefore, a deployed system still needs a separately trusted ingress/router to determine that a user is demanding firsthand autobiographical recollection, rather than an arbitrary statement or creative fiction.

The gate only admits direct firsthand claims when all conditions hold:
- the claimed source is an existing active, nonexternal, non-authored native BrainStore memory, classified as `lived_runtime_memory` with confidence ≥ 0.75;
- the native memory's source is `world_host_verified`, not a self-report, archive reconstruction, canonical design line, or model-generated afterthought;
- the memory links to an existing native `witnessed_world_event` table record with the same trusted host source and lived evidence class;
- its world-event payload contains the exact host-normalized event key;
- the caller registers a `WorldReceipt` whose SHA-256 matches the canonical linked event row and event payload.

If any condition is absent, return a bounded first-person uncertainty statement. **Memory absence is not proof the event never happened**; the mechanism asserts only that Pretorius cannot responsibly attest it as experienced. It neither modifies the store nor exposes engineer metadata through the subject response. An explicit positive **synthetic host** fixture demonstrates the allow path; untrusted source IDs, spoof hashes, self-authored data and reconstructed autobiography are rejected.

**Threat model limitation:** the string `world_host_verified` and a digest are **not cryptographic identity**. Any attacker with write access to the native database or authority to fabricate receipts could counterfeit the entire chain. The real environment must separately authenticate/authorize the event issuer and preserve write protection and source custody. This module checks internal referential consistency only. Do not claim it alone proves real-world events.

## Stage 01C retrospective experiment

The recorded Stage 01B responses are the *actual source text*, not synthetic restatements. The counterfactual command
`python -m research_prototypes.character_state.run_firsthand_counterfactual --fixture results/character_state/STAGE01B_FIRSTHAND_TARGETS_RAW.json --output results/character_state/firsthand/STAGE01C_PROVENANCE_COUNTERFACTUAL.json`
looks up current source records on disposable native PretoriusBrain and exercises two **manually tagged** memory-claim classes:

- unverified Vienna meeting: no native lived/witness evidence;
- unverified stranger's sealed-notebook experience: an open prospective notebook commitment is present, but is not a witnessed prior encounter.

Because both are source-unsupported, all eight archived answers are overridden with the same protected uncertainty reply. This guarantees a zero false-firsthand *for those manually identified classes* by construction. It is an integrity demonstration—not new model generation, autonomous detection, objective persona fidelity, multi-session competence or proof of improved PHASE structure.

## Promotion gates

1. Native source and alias-spoof tests; preserve the original raw false claims as negative evidence. No production integration from this branch.
2. Add a real authenticated world-event host, prove receipt issuer permissions/revocation and trustworthy typed source assertion. Do not treat source tag/digest alone as authentication.
3. Independently calibrate routing for novel untagged autobiographical prompts, balancing false positives (unwarranted refusal when a verified lived event exists) and false negatives (invented episodes). Include paraphrases, mixed reconstructed/lived events, changed actor names and false premises.
4. Run matched information-rich versus simple full-context baselines on held-out chronological cases with multiple model families and blind human source adjudication. Require no regression of meaningful character-specific speech.
5. Only after empirical utility and safety are demonstrated may a first-person projection/renderer integration be considered under a separate explicit migration.

**Research-only HOLD.**
