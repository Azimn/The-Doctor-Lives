# The Doctor Lives

The Doctor Lives is the production assembly repository for Doctor Septimus Pretorius as a persistent, renderer-neutral cognitive system.

The brain owns identity evidence, autobiographical continuity, relationships, concerns, prospective commitments, interoception, salience, endogenous cognition, offline replay, consolidation, recurrent state, and provenance. A language model is a renderer and cognitive organ, not the identity database. Shell, browser, scheduler, messaging, and other capabilities remain outside the brain until a chassis is attached through the stable port.

Calibos is used as a structural donor only. No Calibos memories, private thought stream, relationships, preferences, values, or persona cartridge are imported. The enforced transplant surface is mechanism: salience, interoceptive lag, unresolved loops, sleep and replay, consolidation discipline, drift accounting, and provenance boundaries. Pretorius identity comes from pinned Pretorius evidence under `evidence/` and `doctor_lives/data/bootstrap.json`.

The recurrent Pretorius network is causally load-bearing. Its action distribution selects the cognitive policy used to choose which otherwise-salient non-root memories enter endogenous attention. Every such decision is written to `policy_decisions` with action scores, candidate and selected memory IDs, recurrent tick, checkpoint SHA-256, trigger, and policy version. Outcome reinforcement and sleep replay can therefore change later cognition through the network, and those changes are auditable.

The architectural mutation boundary is defined in `ARCHITECTURE_CONTRACT.md` and `doctor_lives/data/evolution_policy.json`. Frozen invariants require explicit migration. Lived memory, relationships, self-model hypotheses, felt state, salience, recurrent weights, and other developmental state are allowed to evolve.

The current public Jelly-Psiduck repository does not contain the frozen v0.2 engine implementation used by Calibos. This repository therefore reproduces the required first-person workspace and endogenous-cognition semantics behind local interfaces rather than claiming to vendor unavailable code. An exact engine snapshot can later replace that compatibility layer only if it passes the same contract tests.

Install with `python -m pip install -e .`. The command-line entry point is `doctor-lives`. The stable chassis API is `doctor_lives.PretoriusBrainPort`.

Run the regression suite with `python -m unittest discover -s tests -v`.

## Deep-history migration

On first boot, `pretorius-deep-history-v1` installs a dense Pretorius-only prehistory in addition to the minimal identity bootstrap. The migration preserves the full 70-node, 243-edge Persona Connectome, imports the archived research agenda, and adds curated multi-source records for Ingolstadt, the homunculi, institutional rejection, digital continuation, Henry Frankenstein, the Creature, creator responsibility, epistemic independence, artificial life, and continuity concerns.

These are inherited records, not retroactively fabricated lived events. Each imported memory has a stable history key, evidence class, and machine-readable provenance pointing to the pinned Agent-Pretorius commit and source locator. Post-awakening events continue to use `lived_experience`, so the system can always distinguish what Pretorius inherited from what this runtime actually experienced.

The migration also records what was deliberately excluded. LoRA training examples remain training-lineage evidence rather than autobiography, legacy prompt-control text is not treated as personal history, architecture references remain mechanism evidence, and missing biography remains an explicit gap instead of being invented.

