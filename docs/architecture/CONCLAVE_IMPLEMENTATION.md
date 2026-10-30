# Pretorius' Conclave: opt-in kernel, experimental implementation

**Branch:** feature/pretorius-conclave-20261029, derived from integration/m5 commit ac0e2edea0e73c16c4064f70de14f00d558dc045.  
**Contract:** docs/architecture/PRETORIUS_COMPLETE_ESOTERIC_COGNITIVE_ARCHITECTURE.md on the separate research RFC branch / PR #100.  
**Tracking:** issue #101.  
**Status:** Executable kernel + persistence + tests; not the fully integrated esoteric cognitive candidate.

## What is running code

doctor_lives/conclave.py registers five bounded local methods. Agrippan Wheel uses typed elemental/celestial registers with explicitly UNKNOWN intellectual/causal edges. Llullian Ars supplies constrained relations/questions. Brunian Memory constructs a stable unusual locus/image cue, not a memory rewrite. Ficinian Temperament asks testable questions about sensory and bodily context rather than imposing astrological mood. Geomantic Shield computes four mothers, four daughters, nieces, witnesses, and judge with a reproducible source-derived seed; its output is divinatory, not a prediction or a Laboratory observation.

The methods are independently addressable. They may return no reading; caller can select zero or a subset. Each historical work is identified in the registry, but primary passage/edition pinning and outside specialist assessment are still required before source-fidelity claims. The generated correspondences and relational grids are labeled *research reconstructions*. An edition-unpinned geomantic source remains explicitly unpinned.

## One BrainStore, one mind

Only SixOrganRuntime.bind_conclave(enabled=True) opens the opt-in kernel. It binds to the same original BrainStore instance as Pretorius. An additive, versioned Conclave namespace is initialized transactionally inside the existing brain.sqlite3, with no new store file, neural model, or scheduler. Existing core schema version and production release gate are unchanged.

The namespace stores readings, evidence *for* and *against* (independent dimensions), typed conflict links, and an append-only transition log. Readings may be generated, noticed, considered, adopted, doubted, contested, ignored, revised, withdrawn, or dormant. Retrieval preserves all of them. A reading's four-valued status is *neither*, *supported*, *rejected*, or *both*. These are statuses of entered evidence, NOT probabilities of world truth. No automatic synthesis, belief deletion, or majority vote takes place.

Each reading retains source event, provenance class, tradition, source work, context, method trace, questions, optional observational controls, optional no-authority action suggestions and mnemonic cues. Swatch beats and UTC originate in the existing host clock. Replays use stable identifiers and do not overwrite a reading's subsequent state.

## Minimal host usage

    from doctor_lives.organs import SixOrganRuntime
    from doctor_lives.conclave import Stimulus

    runtime = SixOrganRuntime.open(existing_state_directory)
    conclave = runtime.bind_conclave(enabled=True)
    readings = conclave.interpret(Stimulus(
        source_event_id="operator_report:001",
        source_kind="reported",
        context_key="garden",
        text="I was told a raven circled the moonlit garden.",
    ))
    # Optional cue requests; never privileged recall or a direct memory write:
    optional_cues = conclave.cues("garden")

Calls MUST originate in an authorized host after source admission. A user-facing renderer or untrusted language model must never receive an unrestricted Conclave object or database handle. world_verified inputs and support references require a matching externally flagged event in the canonical BrainStore, but this record check alone is NOT a substitute for the existing Laboratory's independent attestation and first-person ingress boundary.

Do NOT pass interpretations directly as lived events into PretoriusBrain.ingest, or treat dreamed or divined readings as verified. Do NOT turn action_suggestions into physical commands. Noesis remains the sole selector and the existing Laboratory receipt bridge must still authorize and execute any action.

## Reproducibility and acceptance

Run:

    python -m pip install -e .
    python -m unittest tests/test_conclave.py -v
    python -m unittest discover -s tests -p "test_six_organ_runtime.py" -v

Dedicated GitHub Actions workflow: .github/workflows/conclave-checks.yml.

Tests cover method diversity, deterministic geomantic operations, no-source/no-reading, explicit gating, idempotent replay, four-valued contradictory support, multi-reading conflict, dormant and withdrawn persistence across a new BrainStore instance, host event record admission, dream source non-promotion, no first-person memory writes, and no policy-decision creation.

**Not yet claimed:** full scholarly passage pinning and fidelity; live Phantasmagorium/Nocturnal Theatre coupling; all six organs exercised causally via this kernel; Noesis learning of Conclave cues; situated physical rites and authoritative world outcomes; whole-system A/B/ablation and cold-crash soak; production qualification or consciousness/occult efficacy. These remain within issue #101. Draft PR #100 remains a design reference, not evidence of runtime completion.

**Independent boundary:** The Conclave can maintain a beautiful, odd, or contradictory reading for years without compelling a decision or corrupting empirical evidence. No model call or paid API is required.
