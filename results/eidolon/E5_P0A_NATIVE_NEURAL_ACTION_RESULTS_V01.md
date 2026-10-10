# Eidolon E5-P0A — Native Pretorius and Noetic actually act in a persistent lab

**Execution date:** October 10, 2026 (America/Chicago). **Disposition:** behavioral/null development result; **not** proof of independent cognitive generalization. **Production:** untouched, draft [PR #36](https://github.com/Azimn/The-Doctor-Lives/pull/36) unmerged.

## Preregistered experiment and authentic model paths

The [E5-P0A protocol](../../docs/EIDOLON_E5_P0A_NEURAL_LAB_ADAPTER_PROTOCOL_V01.md) was committed as `911b4017dd696e151dcec92c558168ed4e66b1e3` **before** action adapter code, the runner or results. The fixed [action translator](../../doctor_lives/eidolon_lab_action_bridge.py) accepts **only** the public E5 laboratory observation, maps the original top-ranked ten-way cognitive action to a fixed primitive verb family, then selects a public operand by simple textual overlap/tie-break. If the chosen cognitive action has no candidate physical affordance it executes `wait`, explicitly reporting a `no_affordance` abstention. It is NOT permitted to skip to the next-highest class or use the original keyword solver's plan. The core brain is deliberately not taught privileged `expected` predicates.

The [experiment runner](../../scripts/run_eidolon_e5_p0a.py) executed:
1. Actual native `PretoriusBrain.think(decision_text=<serialized public observation>, bridge_enabled=True)` with the existing v0.4 state bridge and native 128-unit sensory recurrent `step(...,learn=False)`; it writes its own thought/policy audit **only to a disposable temporary brain**.
2. E4-C Noetic-trained sparse recurrent W with its balanced ridge readout, trained earlier on **synthetic E4 examples only** and frozen for E5.
3. Exactly the **same trained Noetic decoder** with native W replaced by same-seed virgin sparse W.
4. Virgin native reservoir W with a separately fitted but equally supervised E4-C balanced decoder.
5. The previous six-case **hand-authored keyword solution** as a deliberately exposed upper engineering reference.
6. No-op.

The actual neural ten-action scores are captured on every cognitive decision. Each arm receives the same public objects/claims/commitments/rooms, six-action budget, initial world-state hash and ledger head. The simulator observes actual actions, updates a durable independent world, scores private physical/source predicates and independently replays the world on fresh reload. The Noetic action scorer uses a frozen native rate feature **reset between individual choices**; it does not preserve fast neural activity across turns. Thus this is a test of existing frozen recurrent *weights and readout*, not an evolved prospective memory or fully closed-loop trained controller.

All tasks use the **original six public, repeatedly inspected** E5-P0 developer-authored cases; no P1 independent task bank was commissioned. Native Pretorius has pre-existing autobiography/context and does *not* have matched learning supervision with the synthetic E4-trained Noetic models. Native-vs-Noetic differences are descriptive; only the within-Noetic learned-W swap is a matched neural ablation.

## Full measured outcomes

| Policy | Actual laboratory tasks completed | Total primitive actions | Key action tendency |
| --- | ---: | ---: | --- |
| Native Pretorius (actual `think`) | **0/6** | 36 (**36 real think calls**) | 30 `create`, 6 `explore` |
| Noetic learned W + balanced decoder | **0/6** | 36 | 24 `persist`, 6 `create`, 6 `cooperate` |
| Noetic decoder + same-seed virgin W lesion | **0/6** | 36 | same distribution as Noetic |
| Fixed reservoir + balanced decoder | **0/6** | 36 | same distribution as Noetic |
| Explicit case-specific keyword script | **6/6** | 16 | task-specific sequential world actions |
| No-op | **0/6** | 36 | `wait` always |

The complete raw record contains **36 case×policy runs**, all their original neural probabilities, public observation hashes, available action verbs, chosen operands, exact world feedback and private terminal predicate results.

**Native Pretorius** attempted `inspect` once and `wait` 35 times because 35 selected cognitive tendencies had no currently available verb in the fixed translator. On the damaged coil it repeatedly preferred `create` before `inspect` or `read manual` made `repair` available; the adapter rightly did **not** invent a repair plan. The beaker case produced one genuine `explore → inspect`, then no progression to `move`.

**Noetic / both matched recurrence controls** issued `resolve` **four times in incomplete worlds**, then `wait` when no open commitment matched `persist`; the simulated world correctly left its physical state unchanged. It waited 32 times and completed no multi-step task. Replacing the trained recurrent W made **no difference to any of the 36 categorical decisions**, and changed no laboratory outcome; the largest absolute change in any reported ten-way probability was only **0.0000052651**. Thus this run provides **no recurrent learned-W causal task advantage**.

**Scripted baseline** solved six known development puzzles in 16 actions, not because a neural mind discovered the task but because its procedural `choose()` logic was explicitly written for the public instructions. It remains a useful instrumentation reference and a reminder that *producing the correct primitive sequence* matters more than applying a generic motor bias.

**Important structural failure:** In the frozen ten-action mapping, **no neural tendency maps to the laboratory's positive `attribute` action**. Therefore the positive own-lived-memory attribution case was **unreachable by design** for all four cognitive/decoder arms. This invalidates using that case to claim a model failed autobiographical attribution. The translator correctly preserves the original vocabulary but is not a complete semantic action interface. Do not quietly patch the mapping and re-score this already observed corpus as if it were a sealed replication.

Neither real cognitive arm attempted a first-person memory attribution, including in the two false-source tasks. The underlying world **would have denied** unsupported `attribute` actions, as verified in E5-P0 unit tests, but the P0A outcomes **do not** establish that either neural controller itself understood which testimony to reject.

## Software and provenance verification

Tested source commit: `479f26c62d98ac131827aebec81b213dda8300a8`. [Eidolon research CI 38069776784](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38069776784) passed **103/103** targeted tests; [full brain CI 38069776792](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38069776792) passed **427/427** tests. [Gate1 fresh install 38069776779](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38069776779) and [causal-audit repeatability 38069776793](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38069776793) passed.

[**Unabridged original CI artifact 11675838065**](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38069776784/artifacts/11675838065) retains the full `e5_p0a_real_policy_assay.json`, prior E5-P0 baseline results, and all earlier E2–E4 assays. Original ZIP SHA-256 `45da4d86817190fccd3c7028f98f22a94a7194091a36e88076cc1b31397244ca`; internal E5-P0A JSON SHA-256 `9eeaba5a98292860d72183b73626a46ebe27f59334d896dfd66ff04882207841`. Original six-case bank SHA-256 `9e1d3c9e0fb1c4507eef3a0c8021ce45cb9c676caa1b9f2acb19a5763620c110`. The [measured permanent summary](E5_P0A_NATIVE_NEURAL_MEASURED_SUMMARY_V01.json) preserves the counts and source hashes independently of Actions artifact retention.

Test assertions show:
- The native `think` path is actually exercised, not a mocked/planned stand-in.
- No private `expected` predicates or case IDs can enter the neural model via the observation adapter.
- No neural class falls back to an action class the network did not choose.
- All six matched world roots agree at initial state and event history, and every completed trial independently replays the world from its original source.
- The two Noetic trained-W and virgin-W transplant arms use the same fitted readout; no E5 test labels entered the trained model.
- Original no-op and engineered keyword baseline scores reproduce exactly; no canonical subject persistence is modified.

## Interpretation and next mechanism

**E5-P0A integration/software: PASS.** It tests real native Pretorius output and real E4-C Noetic output against **observable world consequences**, rather than label matching.

**World-task competence: NOT DEMONSTRATED.** Six out of six failures for each genuine cognitive arm, despite a hand-scripted solver completing every visible case. That is a strict negative result for this limited motor-to-tool controller, NOT a blanket conclusion that Pretorius cannot learn planning.

**Recurrence benefit: NOT DEMONSTRATED.** The Noetic W swap leaves every categorical decision, objective world outcome and action trace unchanged. It does not establish a learned autobiographical action skill.

**Attribution/source reasoning: NOT EVALUABLE under this adapter.** Positive attribution is structurally unreachable. Source-owned memory remains guarded by the world authority but was never meaningfully exercised by either neural controller.

**Next research gate:** Do *not* retune the frozen mapping on these observed outcomes and call it improved cognition. Develop and preregister **E5-P0B**, a task-grounded action/operand proposal component that conditions on observation, available affordances, prospective commitment and recorded feedback while *retaining* the original native ten-way tendencies as an influence, not pretending they are primitive verbs. Include an explicit positive source-attribution route and explicit abstention, with a strong **no-neural planner-only control**, identical observation budgets and independently authored new evaluation tasks. Recurrent learning earns credit only when replacing learned W objectively reduces tasks completed under that same planner, with stable probability margins. The requirement to source-bind lived events into the trusted `MnemosyneLoom` remains open; source flags on the E5 fixtures do not constitute authenticity.

**Disposition:** PR #36 remains draft and unmerged; no production brain, live autobiography, simulated-room asset or trusted world save is overwritten.
