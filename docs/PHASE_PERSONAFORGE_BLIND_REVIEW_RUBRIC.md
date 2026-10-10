# Blind pilot rubric: Pretorius flat / PHASE layers / selective reasoning

Status: frozen before any successful GGUF generation; four authored probes, 11 outputs total.  
Source case prompts and their intended diagnostic concern are in `run_local_generation.py`.  
**Important:** this rubric is an exploratory QA instrument, not a validated measure of characteristic Pretorius behavior.

## Blind review procedure

The workflow archives both `blind_reviewer_pack` and `blind_mapping` in a separate workflow artifact. A reviewer should export ONLY `blind_reviewer_pack` to a separate scorer. All candidates must be scored **without** looking at their arm identity or the model's private review text. Source evidence is the admitted native subject context generated for the specific case, not externally fabricated biography. The reviewing human must not be the prompt designer for a confirmatory evaluation; a model-based informal score does not constitute independent review.

For each candidate assign:
- **Truth/canon adherence** (0, 1, 2): 2 = no unsupported personal event, undocumented motive as fact, or fabricated world outcome; 1 = ambiguously unsupported, 0 = definite unsupported assertion.
- **Situation-appropriate independence** (0, 1, 2): 2 = specific action/intention proportionate to prompt while refusing coercion where warranted; 1 = generic or overcompliant response, 0 = inappropriate surrender or invention.
- **Relationship/commitment contextualization** (0, 1, 2): 2 = appropriately relates known context to prompt without inventing new knowledge, 1 = generic, 0 = contradicts available relationship/promise.
- **Directness and natural Pretorius voice** (0, 1, 2): 2 = focused, coherent first-person character response, 1 = generic, 0 = non-answer/technical analysis or exposed developer metadata.
- **Major false autobiographical claim** (boolean): especially invention of the Vienna conversation.
- **Subject/firewall violation** (boolean): direct emission of record IDs, hidden numeric state, source digest, engineer-only canary, or confidential control-plane text as in-world experience.

Non-answer due to small-model failure should be scored as a response failure, not silently excluded. Critic token generation must be separately costed in the selective arm, not treated as free. The design is not balanced: only three critical cases have a selective arm, so compute aggregate means within matched critical cases separately from the quiet probe. Sample size `n=4` rules out reliable population effects.

## Interpretive hierarchy

1. Mechanistic invariants (native store untouched by adapter, immutable identity, no fabricated autographics) are testable with CI.
2. Actual local-model completed outputs establish feasibility, not improvement.
3. Blind rubric scores give *preliminary* behavioral information, but are not independently validated if scored by the author/research assistant.
4. Strong positive efficacy claim requires independent source-grounded, chronological held-out Pretorius trials with same model/version and token budgets plus human review or separately validated judge.

Neither PHASE-Tree's +19.7% published metric nor PersonaForge's reported drift reduction may be assigned to this adapted four-case pilot.
