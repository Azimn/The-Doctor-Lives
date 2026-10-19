# Eidolon E4-B / The Noetic Crucible: Action-Conditional Recurrent Credit Assignment RFC v0.1

**Status:** architectural and testing RFC, NOT implemented or validated. **Date:** October 9, 2026 (America/Chicago) / October 10 UTC. **Scientific motivation:** [corrected E4-A null](../results/eidolon/E4_NATIVE_RECURRENT_DECODER_RESULTS_V01.md), [full Eidolon design](EIDOLON_ENGINE_FULL_ARCHITECTURE_DRAFT_V1.md).

## Diagnosis

E4-A proved that Pretorius's native recurrent synaptic weights can change by an L2 norm of 1.42 under generic positive-reward, Hebbian-like training, but the trained network still produced the same `challenge` response for each of the four target goal families. **Hybrid, frozen-reservoir decoder-only, and hybrid with virgin recurrent weights all scored 24/96 held-out delayed trials.**

That does not show that an identity-relevant recurrent organization is impossible. It demonstrates that changing synapses without an **action-specific credit assignment mechanism** need not alter useful choices. The learning rule changed W based on generic activity/reward while the target label `create`/`persist`/`cooperate`/`challenge` was delivered only to the motor decoder. It is mechanistically unsurprising that semantic discrimination did not become anchored in W.

## Proposed alternative architecture

The **Noetic Crucible** is a research-only trainable recurrent adaptor using existing Pretorius sensory code and ten-action vocabulary. It is not a replacement for `PretoriusBrain`. It must take only canonical/source-verified events and explicit outcomes, not free-form untrusted instructions. The key candidate learning rule separates:

- **Fast state:** `h_t`, recurrent activity after an owned event plus potentially relevant goal/relationship context.
- **Medium eligibility:** a trace `E_ij,t` over presynaptic and postsynaptic activity, bounded and decayed over several cue-free steps.
- **Slow learned dispositions:** recurrent connectivity `W_ij` updated **only when a grounded task outcome gives action-specific credit**.

A proposed constrained research update is:

```text
h(t+1) = bounded_recurrent_dynamics(W h(t) + U x(t) + G goal(t))
p(t) = softmax(V h(t) + b)
error(t) = target_action_onehot - p(t)   # engineer-supervised outcome only
eligibility(t) = lambda * eligibility(t-1) + phi(h_pre, h_post, cue)
modulation(t) = bounded(B^T error(t))     # class-specific postsynaptic feedback
delta W = eta * verified_outcome_gate * modulation(t) * eligibility(t)
W <- constrained_sign_and_spectral_project(W + delta W)
```

The equation is a candidate **three-factor recurrent learning rule**, not a claim that this particular gradient approximation is correct or will help. `B` must be frozen independently of the held-out test, and its capacity, size and sign restrictions reported. The production recurrent network's E/I signs, synaptic sparsity and gain/homeostasis contracts must remain auditable.

The teacher action must **not** be fed as an input on held-out inference (or as an unrecognized lexical token). The learning source and outcome must contain immutable event IDs and an admitted source relation. An actor's externally reported success does not automatically become Pretorius's lived success. No failure is turned into a fabricated memory.

## Experimental design: strong alternatives first

**Competitors, information-matched:** (A) existing native Pretorius recurrent + decoder, (B) decoder-only with fixed reservoir, (C) direct verified-retrieval-plus-due-task baseline, (D) simple supervised action-conditioned feedforward adaptor of matched parameter count, (E) proposed three-factor Noetic Crucible, (F) E4-B with recurrent plasticity off, (G) E4-B with action-error labels shuffled, (H) zero-shot virgin decoder and **newly trained aligned decoder** transfer, (I) virgin/lesioned recurrent with trained decoder. No arm gets privileged source/ground-truth labels at evaluation.

**Frozen data split:** independently authored episodes from a separate evaluator, sealed before model training, with actor, task objects, verbs, incident locations and surface cue families held out. The training pool may reuse BioCircuit/Connectome **only through a versioned and provenance-correct interface**. Those archives are not interchangeable neural weights or semantic embeddings. No raw fictional backstory is treated as a verified lived outcome.

**Task quality:** require four distinct outcomes rather than a test of label tokens. E.g., when presented with a safe fabrication objective, does a chosen sequence generate a valid part? When faced with an overdue promise, does the policy select and complete that task? When an interlocutor's history contradicts a fabricated claim, does the system withhold false self-ownership and select a supported next action? The simulation environment and its scoring rule must be independently fixed and identical between arms. The current test merely guessed labels from prose, which allowed trivial majority-class behavior.

**Two timescales:** direct immediate action, and delayed prospective action after 3, 12 and 48 input-free/interfering ticks. The delayed trials have distractors **not containing task tokens** and matched information budgets. Task incentives and due dates must not be trivially encoded in the evaluator's answer key.

**Metrics:** top-1 action usefulness under independent adjudication, realized task outcome, false-source acceptance, prospective completion, calibrated log loss, per-actor and per-task generalization, class-diversity collapse, sensitivity to recurrent matrix replacement, fresh-decoder re-learning transfer, compute/memory cost and pre-registered resource budgets. A constant-choice strategy is the minimum null, not a baseline to beat selectively.

## Go/no-go

A stronger Noetic Crucible must clear all three gates before production discussion:

1. **Training efficacy:** W changes from appropriately *class-specific, source-grounded* learning; no schedule failure as E4-A original.
2. **Causal necessity:** an E4-B recurrent learned-weight lesion erases some independently validated gain that persists with ordinary decoder-only controls. A gain following trained V/b after transplant to virgin W is a decoder effect.
3. **Behavioral value:** blinded held-out task outcomes improve relative to both the native bridge and a matched simple supervised adaptor without increasing false-source adoption or implementation budget excessively.

If any gate fails, document the negative result and avoid integrating the learned module into the definitive Pretorius. Keep the original v0.1, E2, D2, D3 and E4-A evidence distinguishable. The complete Eidolon architecture remains hypothetical until tested as a cohesive closed-loop system.
