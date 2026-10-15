# Diagnosing the exposed delayed paraphrase miss

## Question and scope

The v0.2 pilot recorded a delayed paraphrase selecting continue without surfacing the prior 325-gram reading. The original report preserved the miss without assigning a unique cause. A later review proposed lexical rather than semantic retrieval as the explanation. This diagnostic distinguishes the recall policy's cooldown gate from the preview's cue-sensitive episode projection. It is a post-hoc investigation of an already exposed developer fixture, not a fresh confirmatory semantic benchmark.

The source baseline is `09df2169b6d9359336d9dbec93888f56af0613c9`. No cognitive module, source memory, default policy, standalone organ or production state is changed. The diagnostic runs only on disposable copies of actual CASCADE Pretorius state, using the existing four-organ host and deterministic governed renderer.

## Intervention

The first four original sessions and the one authorized intervening heartbeat construct the same predecessor state as the original pilot. After closing the host, its state directory is copied into four conditions. A two-by-two design varies the later User wording (the earlier original question versus the exposed paraphrase) and the policy parameter `cooldown_ticks` (the existing default 2 versus a diagnostic clamp to 1). The copied pre-session Doctor digests are identical in all four conditions.

The experiment instruments the existing policy call. It first calls the same policy without persistence and verifies that this leaves Doctor state unchanged. It then commits the actual call with the declared cooldown parameter and verifies agreement with the forecast. Every result is cross-checked against the persisted policy-decision row. Policy audit data remain engineer-only, outside the Ipseity and governor input. No model receives the scores or an externally supplied question as an internal recollection.

## Measured outcome

| User wording | Cooldown parameter | Cooldown active | Committed action | Stored 325-gram fact accessible |
| --- | ---: | --- | --- | --- |
| Earlier original wording | 2 | Yes | continue | Yes |
| Earlier original wording | 1 | No | recall | Yes |
| Exposed paraphrase | 2 | Yes | continue | No |
| Exposed paraphrase | 1 | No | recall | Yes |

The active cooldown sets the recall score to exactly zero in both default conditions, despite information need of 0.9025. The diagnostic parameter change re-enables recall and reverses the committed action for both wordings. The paraphrase then receives the previously stored reading. None of the four subject frames contains the disputed 451/919-gram readings as settled observations; the governor accepts all four fixture responses.

The original wording can also surface the episode through the existing cue-sensitive preview projection while the policy selects continue. The paraphrase does not access that route at the default gate. Thus **policy selection and memory accessibility are distinct measurements**. The particular miss is explained by an interaction between a cooldown gate and cue-sensitive projection, not an isolated demonstration that the underlying memory cannot be retrieved from this wording.

This does not establish semantic generalization. The internally selected recollection question still comes from the existing concern rather than being derived semantically from arbitrary User language. It also does not establish improved external task outcomes, natural conversation, usefulness of more frequent recall, or a production-appropriate cooldown value. Reducing a gate on an exposed fixture can increase recall cost or unwanted repetition elsewhere. The default remains 2, and the original 18-session record remains unchanged.

## Reproduction and disposition

Run `python -m tools.run_cascade_cooldown_diagnostic --output results/cascade/LOCAL_COOLDOWN_DIAGNOSTIC.json` with the same pinned donor setup as PR #61. The committed [case-level result](../../results/cascade/COOLDOWN_WORDING_DIAGNOSTIC.json) includes common-checkpoint verification, raw scores, authoritative decision IDs, subject-input hashes and exact code hashes. `tests/test_cascade_cooldown_diagnostic.py` preserves both the cooldown action effect and the residual wording-dependent projection difference.

The next efficacy gate must use fresh scenarios, equal opportunity and real resource budgets, a simpler controller, a prespecified externally observable task outcome, and the same declared counterfactual intervention. This diagnostic is evidence of a narrow causal gate, not another all-Article passing claim or a justification for adding a new architecture.
