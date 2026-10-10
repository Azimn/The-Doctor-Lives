# Predictive Self Loop v0.1: executable research implementation

Status: **implemented in isolated shadow research, not enabled in Pretorius production**.  
Related source: Hirsh (2026), [The Game of Self](https://doi.org/10.1177/10888683261422344).  
Governing full analysis: [Game of Self PSL RFC v1](GAME_OF_SELF_PREDICTIVE_SELF_LOOP_RFC_V1.md).  
Architecture target: The Doctor Lives; production baseline remains `legacy_v04`.

## What was added

`research_prototypes/predictive_self/loop.py` implements a model-independent, inspectable, standard-library-only **forecast -> observe -> update** loop. `adapter.py` reads source-pinned PretoriusBrain state and can verify *only* native stored policy decisions, not external world outcomes. `run_shadow_demo.py` exercises both a labeled synthetic world-witness case and a genuine PretoriusBrain policy decision on a disposable state. The underlying `doctor_lives/` package and default brain code were not modified.

Five mechanisms have separate observable inputs and outputs:

| Mechanism | Executable hook | Epistemic boundary |
| --- | --- | --- |
| Semantic -> episodic | Fallible source-linked `SemanticClaim` indicators weakly tilt a source neural action distribution | Proxy, not evidence that the design self accurately predicts traits |
| Episodic -> semantic | High-precision `WORLD_VERIFIED` episodes change slow hypotheses only after >=3 witnessed episodes in >=3 distinct contexts | Internal selected policy *never* rewrites semantic self; source canon untouched |
| Contextual expression | Context-specific action counts update immediately, shrunk to the semantic distribution; repeated partner-specific action counts add relational context | Context categories are supplied by caller; identical labels must mean equivalent situations |
| Relationship model | Verified observable cooperative/not-cooperative partner behavior informs a bounded Beta-style probability | No guesses about hidden thoughts promoted to facts; no reward for sycophancy |
| Epistemic proposal | High action entropy suggests evidence inspection; ambiguous partner response suggests clarification | Typed `InquiryProposal` has **no execution, tool access or consent authority** |

Each `Forecast` is sealed before observing a later event and includes a snapshot digest, action probabilities, semantic estimates, relationship response estimate, optional per-action success estimate and a deterministic audit fingerprint. An admitted `ObservedEpisode` must identify that preexisting unconsumed forecast, match its situation, occur after its source cutoff, use a valid action and have a unique event ID and witness reference. The model calculates multiclass Brier and action log-loss; world-success and partner-behavior Brier scores are computed only when independently asserted by the host.

`RUNTIME_POLICY` episodes may update the fast contextual distribution of what the actual neural brain **selected** but cannot assert external consequences, verify a partner, or revise slow semantic self hypotheses. `WORLD_VERIFIED` events are caller-attested placeholders in the research prototype, not cryptographically authenticated. Any real adapter must verify the real world ledger and witness before construction.

Long-term semantic revisions are deliberately conservative: credible observed action indicators from multiple distinct contexts form a smoothed posterior, capped at ±0.15 relative to its prior. These are heuristics chosen for falsifiable research, **not derived numeric parameters from Hirsh**. A single observation may adjust contextual expectation, but cannot rewrite global identity. Designed backstory, reconstructed memory and provenance-ranked canon never change.

## Persistence and reboot

`export_checkpoint()` creates a deterministic JSON payload containing source snapshot digest, version, hypotheses digest, configuration, sealed forecasts, admitted evidence records, per-observation scores and a SHA-256 replay seal. Export requires no outstanding forecasts and sequential forecast/observation pairs (v0.1 restriction).

`restore_checkpoint(snapshot, claims, checkpoint_json)` replays all predictions and observations from the exact same source fingerprint, checking the per-forecast digest, scores, resulting audit digest and source/claim compatibility. A different snapshot, changed hypothesis or tampered record fails closed. It does not change BrainStore or authorize the recovered data as canon.

**Important:** SHA-256 integrity is *not* a cryptographic signature or proof that witnesses are genuine. Checkpoint authentication, user consent, privacy and source custody remain responsibilities of a separate host. The JSON is portable across processes and model renderers, but **actual cross-model persona continuity has not been measured**.

## Real Pretorius adapter

`snapshot_from_brain(brain)` reads the existing canonical manifest, BrainStore content/version/tick, recurrent action probability distribution, currently admitted memory IDs, relationship IDs, commitments and self-model source IDs. It verifies that the source BrainStore digest does not change while reading. It does **not** map identity prose into psychological trait claims or fabricate a new self autobiography.

`witnessed_policy_decision(brain, loop, forecast, decision_id)` queries the actual `policy_decisions` table for a real later action and creates an action-only `RUNTIME_POLICY` observation. It cannot certify whether that action occurred in the world, what another person experienced or whether any commitment was fulfilled. The situation label is currently caller-supplied and unverified.

Example commands from repository root:

```sh
python -m unittest discover -s tests -p 'test_predictive_self_loop.py' -v
python -m research_prototypes.predictive_self.run_shadow_demo
```

The demo explicitly labels all world outcomes `mock` and uses a disposable native brain state. No linked real-world outcome or independent cognitive-inference data was collected.

## What is *not* included

No second recurrent policy, changed production action or retrieval scoring, new active agent in Pretorius, extra BrainStore schema tables, LLM introspection, changed UPPB/P3 gating, a live planner, autonomous inquiry, causal world feedback integration or renderer instruction path. No hidden state is revealed through first-person subjective access.

This is **not** a full active inference implementation or variational free-energy optimizer. Action and partner probability estimates use simple smoothed counts and bounded semantic biases, not fitted deep generative dynamics. The subjective "I" and semantic "Me" are conceptual analogies, not consciousness claims.

## Experimental gates

1. Run the mechanics and read-only-native adapter tests under GitHub CI. Failure blocks any further validation.
2. Audit whether meaningful, independent world-action/outcome witness records actually exist. Without those records, only *mechanics* are tested.
3. Freeze source-disjoint and chronological holdouts. Compare PSL against the identical neural baseline, flat conditional frequencies, and one-way history models; include shuffled identity/context references and simple zero-trait baselines.
4. Evaluate predictive Brier/log loss, calibration, abstention/coverage, contexts/relationships, source truth, and prospective commitment followthrough. A change of forecast is not proof of improved persona.
5. Only after the read-only forecast gate succeeds can a separate optional, bounded *policy proposal* be considered under a new production gate. The original experiment's SelfBindingModulator mixed/null results remain preserved.

**Current ruling: research available, production HOLD.**
