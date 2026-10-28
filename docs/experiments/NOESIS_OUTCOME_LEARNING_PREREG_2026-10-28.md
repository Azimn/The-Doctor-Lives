# Noesis consequence-of-action learning, v0.3: preregistration
Date: 2026-10-28. Status: preregistered before v0.3 implementation. Parent tested head: `5b9d7e816e9244121ba6c1130c9b97c5d34bc644`; branch PR #98, production main untouched.

## Goal
Make the **existing canonical Noesis**, rather than the Laboratory host, use a real **consequence of a previously executed action** to alter a later choice among feasible actions. No prescriptive book is required. The previous v0.2 instruction-conditioning remains unchanged by default and v0.3 is opt-in. No seventh organ, secondary database, second policy selector, autonomous scheduler or LLM-generated reward.

## Mechanism fixed before tests
The original brain's recurring ten-tendency scores are mapped with the existing fixed `explore -> experiment`, `persist -> repair` grounding, unchanged weight 0.20. During a verified situated choice with `outcome_learning_enabled=True`, the trusted Laboratory host supplies **only IDs** of original lived work outcomes whose authentic independent `rhythm_events` have `op in {experiment, repair}`, `station=station:bench`, `args={}`, a checked hash and matching first-person experience. The host supplies no reward, desired action, privileged state or next step.

Noesis itself examines its **own first-person action memories** and the current first-person observation, not a separate outcome controller. If the current observation says "My instruments look worn and will need attention." and Noesis recalls one verified experiment consequence "I complete a careful experiment at my workbench. The apparatus shows wear.", apply a bounded **-0.60** to `experiment`. A verified first-person `repair` memory "I replace the worn component in my apparatus." yields a bounded **+0.30** to `repair` under that same current cue. At most one latest genuine outcome per action is counted, preventing repetition amplification. Neither rule fires without current matching perception. These are **researcher-authored appraisal heuristics** over directly experienced effects, not self-discovered causal semantics, general reinforcement learning or neural synaptic plasticity.

One policy decision and thought are committed transactionally to the existing canonical BrainStore with selected concrete action, neural contribution, witnessed evidence IDs and outcome contributions. No reward is projected as a number into subjective experience. Version and opt-in evidence flags are auditable. Previous v0.2 decisions remain accepted by the existing motor-authorizing port.

## Fixed arms and expected outcomes
1. **No book, real wear caused by performed experiment.** Start from canonical Laboratory, physically move to bench, perform one real experiment which wears apparatus from 2 to 1 and creates one lived first-person outcome. With both work actions currently feasible, no manual learning, v0.3 ON, Noesis selects **repair** due to its actual remembered consequence; host authorizes only the selected action; Laboratory records one physically effective repair and one lived repair experience.
2. **Outcome learning OFF:** same world and original brain, same feasible actions; score contribution must be zero. With recurrent priors explicitly held at zero, baseline tie resolves **experiment**.
3. **Outcome memory archived and restored:** with identical real world and prior, `repair -> experiment -> repair`, no world actions during comparisons; after restart the same source-linked consequence remains usable.
4. **Unverified fake experiment story:** no sourced outcome influence. Repeated action ID cannot produce a second learned episode.
5. **Sound apparatus despite an earlier real experiment:** no worn cue, no recalled-consequence adjustment. One counterfactual world has no rehearsal memory and one world records actual repair (which physically restores apparatus).
6. **Unauthorized motor proposal and stale decision:** neither creates a world action; authenticated replay/restart executes at most once.
7. **Negative causal controls:** same remembered consequence but no current cue, disable outcome-learning, or archive the lived memory; all yield zero outcome score adjustment. The native recurrent prior should change baseline scores when enabled, but a memory-dominant final choice is *not* proof that recurrent weights learned.
8. Original v0.1/v0.2 and pinned donor regressions must remain passing, and no Lab test may be reported as passing if it was skipped.

## Scoring and caveats
Primary result is *actual physically receipted action selection*, plus source-verified side effect and reversible decision lesion. One authored experiment, under a declared heuristic, does not establish general world-model learning, causal inference, transfer to new apparatus or human realism. An equal-information literal outcome-memory rule can make the same choice, so superiority is NOT claimed. Do not relabel D3-D11 or Article 15 complete on this result.

## Release-readiness decision context
After the experiment, assess separately: (i) isolated scientific capability evidence; (ii) integrated/merged single-brain production runtime; (iii) install, continual autonomous life, user interaction, restart/backup, full no-bypass and acceptance tests. Do not conflate green opt-in PR CI with a shipped Pretorius v1.0. Provide a finite minimum shipping bar and explicitly defer unbounded general-human-simulation work.
