# Sensus Communis Artificialis

**Canonical development repository for Sensus Artificialis**, a proposed synthetic cognitive organ for evidence-preserving, multisensory scene binding.

Sensus consumes typed, trust-bounded percepts from an upstream perception shell and emits immutable candidate scenes. It does not normalize sensors, authenticate percept sources, decide subjective admission, generate feelings, regulate gain, maintain an autobiography, or act as a decision-maker.

The architectural split is deliberate. An upstream perception shell, such as Witchglass, owns sensor normalization and trust adjudication. Sensus owns cross-channel binding, conflict/veto representation, short-lived object files, uncertain re-identification, and scene emission. Synthetic Ipseity determines what may be admitted to the subject. Daemonium handles gain regulation. Mnemosyne or the Archive owns longer-term mnemonic material. **No integration is currently authorized or implemented.**

The interoceptive channel is a first-class perceptual stream. Attribution uncertainty is preserved, including the valid state "uneasy, cause unknown." An affect attribution is a hypothesis, not an observation.

## Repository state

Version 0.1 is a **standalone computational scaffold**, not evidence of consciousness or demonstrated cognitive advantage. The repository includes a deterministic pure-Python implementation, standard-library unit tests, a proposed v0.1 scene contract, and experimental registration. No external models, sensors, memory systems, or APIs are required.

Run the contract tests from the repository root with:

    python -m unittest discover -s tests -v

Basic usage:

    from sensus_artificialis import Evidence, Percept, Sensus
    organ = Sensus()
    red = Percept("vision-1", "vision", Evidence.OBSERVED,
                  "shell:vision-1", 1, "color", "red", 0.9,
                  object_hint="item", features=(("shape", "round"),))
    scene = organ.step(1, [red])
    assert scene.objects[0].claims[0].evidence is Evidence.OBSERVED

Documentation: docs/SPEC_v0.1.md and docs/EXPERIMENTS_v0.1.md.

Design specification (2026-10-10): the hard invariant is **no evidential-class
amplification** — integration may bind, never upgrade; conflicting binds are
vetoed and surfaced, never silently resolved. See docs/SPEC_v0.1.md.

## Independent research and integration freeze

The standalone lab battery is documented in [docs/STANDALONE_BATTERY_v0.1.md](docs/STANDALONE_BATTERY_v0.1.md). Its known false merges are reported as negative cases. Run `python -m experiments.standalone_battery` for structured metrics; CI saves JSON artifacts. The [adoption gates](docs/ADOPTION_GATES.md) preserve the independent October 15 to 23 blinded ablation window; this repository does not adopt or modify external systems.
