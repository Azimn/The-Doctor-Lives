# Ritual-interface reference prototype

Status: **isolated, offline, unvalidated, not integrated with Pretorius production**.

This is a minimal, standard-library-only interface-prototype for the architecture in `docs/DUAL_GATE_SELF_INTERFACE_RFC_V1.md`. It is deliberately outside the installed `doctor_lives` package and is not imported by `PretoriusBrain`, the UPPB, P3 `AwarenessRouter`, or the renderer.

The modules are independent: `state.py` provides an immutable digest-bearing source-reference projection, `cues.py` provides scope- and subject-bound lookup that requires an externally authenticated invocation, `reconstruction.py` creates deterministic version-checked non-truncating hydration plans, `verification.py` aggregates observations from a hypothetical external sealed behavioral evaluator, `governance.py` performs a capability-based change preflight without mutating identity, `world.py` tests world-event authority and consent before hypothetical ledger acceptance, and `binding.py` retains the preliminary scalar bounded-relevance helper. The concrete `SelfBindingModulator` is now implemented independently in `self_binding_modulator.py` with version-pinned input validation, source-linked event signals, controlled OFF/LOW/NORMAL/HIGH/SHUFFLED lesions, global freeze on verified world contradictions, and SHA-256 audit traces. `run_self_binding_demo.py` emits a reproducible synthetic comparison without any model inference.

These are **contract prototypes**, not full implementations. In particular, they do not read the live BrainStore, implement an authorizing capability service, perform any actual retrieval, evaluate model responses, execute world actions, write identity history, change neural state, implement a psychedelic simulation, or guarantee safety if the surrounding chassis supplies false authentication. Digest fields check shape/content linkage, not cryptographic signature authenticity. The included tests are synthetic and cannot establish persona efficacy. Host-provided semantic relevance, world-conflict verification and authentication must be enforced independently; source membership alone does not verify those inputs.

Run offline from repository root:

```sh
python -m unittest discover -s tests -p 'test_ritual_interface_prototype.py' -v
python -m unittest discover -s tests -p 'test_self_binding_modulator.py' -v
python -m research_prototypes.ritual_interface.run_self_binding_demo
```

This does not promote a ritual mechanism. Promotion requires source-independent held-out evidence from Attractomancy, full provenance/firewall regression, performance against simple baselines, migration gates and explicit approval.

See [SelfBindingModulator v1](../../docs/SELF_BINDING_MODULATOR_V1.md) for exact state, gain, audit, and world-contradiction semantics. Neither the component nor the demonstration is attached to the production brain or P3 awareness path.
