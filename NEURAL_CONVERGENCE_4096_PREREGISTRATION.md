# Neural Convergence 4,096-Unit Characterization Protocol

Status: **FROZEN PREREGISTRATION - B02**  
Production-research branch: `prod/neural-convergence-characterization`  
Frozen implementation parent: `cfa95da8fb970056f13e4a7dc568b994b990be85`  
Accepted production base: `271e87cf1f7c026594720d8ff8c9a58ce54da4fd`  
Historical donor reference: `feature/pretorius-neural-convergence-v05@cf009630f1c623b0bcac1eb9e5e7242fa3e8a0e7`  
Protocol version: `neural-convergence-characterization-b02-v1`

## 1. Purpose

This protocol freezes the experiment before production-size characterization results are generated.

The experiment asks a bounded engineering question:

> At the current 4,096-unit production scale, does the opt-in Neural Convergence profile provide stable, reproducible, causally load-bearing improvements over the accepted legacy v0.4 recurrent profile under matched developmental exposure?

It does **not** ask whether a 4,096-unit recurrent network is the maximum useful size, whether recurrent networks can or cannot scale beyond this point, whether a recurrent substrate is a person's identity, or whether increasing neural capacity is sufficient by itself to produce richer cognition.

The 4,096-unit point is the primary preregistered characterization point, not an assumed capacity ceiling.

## 2. Why the protocol is frozen

Control, challenger, seeds, exposure schedule, metrics, lesion families, decision rules, stop criteria, and capacity-adequacy rules are fixed before B04-B07 results exist.

Poor results must not cause the experiment to be retuned until it passes. Positive results must not cause favorable metrics to be selected after the fact. Any material protocol change after B02 invalidates direct comparison with the original preregistration and requires a versioned replacement protocol before new decisive runs.

Implementation defects in the B03 harness may be repaired without changing the scientific protocol. Any repair that changes stimuli, durations, seeds, measured endpoints, lesions, or decision thresholds requires a new preregistration.

## 3. Frozen control and challenger

Both conditions use the production implementation in `doctor_lives/neural.py` from the frozen implementation parent above.

### 3.1 Legacy control

The control is `DEFAULT_CONFIG` with no profile-changing override except the fixed seed for that matched run.

Shared production-scale parameters include:

- neurons: **4,096**
- sensory dimension: **512**
- average recurrent degree: **32**
- input degree: **10**
- excitatory fraction: **0.80**
- target rate: **0.08**
- recurrent scale: **0.34**
- input scale: **0.55**
- plasticity interval: **8**
- Hebbian learning rate: **0.00035**
- reward learning rate: **0.0012**
- eligibility decay: **0.92**
- maximum absolute recurrent weight: **0.75**
- action population size: **72**
- motor temperature: **0.30**

The accepted control-specific mechanisms remain:

- plasticity rule: `hebbian`
- neuromodulation: off
- synaptic tagging: off
- provisional update fraction: 0
- spectral homeostasis: off
- endogenous noise: 0
- intrinsic excitability homeostasis: off
- additional felt-state scalar channels: none

### 3.2 Neural Convergence challenger

The challenger is `NEURAL_CONVERGENCE_CONFIG` with no profile-changing override except the fixed seed for that matched run.

It preserves the shared 4,096-unit production parameters and changes only the already-defined convergence mechanisms:

- plasticity rule: `oja`
- neuromodulation: on
- synaptic tagging: on
- provisional update fraction: **0.08**
- tag decay: **0.90**
- capture scale: **1.0**
- spectral homeostasis: `banded`
- target recurrent gain: **0.88**
- allowed recurrent-gain band: **0.74 to 0.95**
- spectral check interval: **32**
- endogenous noise: **0.008**
- noise persistence: **0.92**
- intrinsic excitability homeostasis: on
- target state saturation: **0.18**
- state-gain bounds: **0.20 to 1.20**
- additional state channels:
  - `need_fatigue`
  - `need_affiliation`
  - `need_competence`
  - `need_autonomy`
  - `need_curiosity`
  - `need_continuity`

The experiment must not silently copy additional behavior from the historical donor branch.

## 4. Matched-run design

Each seed creates one matched pair:

1. legacy control;
2. Neural Convergence challenger.

The pair receives the same ordered text observations, ordinary scalar inputs, confidence, rewards, action-outcome schedule, and evaluation probes.

The only intended between-pair difference is the frozen neural profile. Convergence-only felt-state channels are supplied from the same externally generated latent/felt-state schedule; the control receives the same world sequence but, by design, its encoder does not admit those additional channels.

No renderer output participates in the characterization.

## 5. Frozen seeds

The decisive matched characterization uses exactly six seeds:

`1842, 1843, 1844, 1845, 1846, 1847`

Seed 1842 preserves the historical production default. The five adjacent seeds prevent the default seed from carrying the decision alone.

A failed or favorable seed may not be replaced because of its result. A seed may be rerun only when the artifact is invalid for a preregistered technical reason such as process interruption, corrupt output, or harness failure.

## 6. Frozen duration and phases

Each control/challenger seed uses the same **5,120 neural steps**.

### Phase 0 - initialization snapshot

Before exposure, record configuration identity, recurrent topology summary, weight-distribution summary, checkpoint identity, initial diagnostics, and fixed evaluation probes.

No learning occurs.

### Phase 1 - neutral stabilization: 512 steps

Use a deterministic balanced neutral stream with `learn=False`.

Purpose:

- characterize untrained dynamics;
- detect immediate instability or profile initialization bias;
- establish pre-development state/probe baselines.

### Phase 2 - developmental exposure: 3,584 steps

Use `learn=True`.

The stream contains seven fixed 512-step blocks. The B03 harness must generate these deterministically and identically for matched profiles:

1. novelty / exploration / creation;
2. authority / autonomy / coercion;
3. social approach / cooperation / distrust;
4. threat / avoidance / control;
5. persistence / competence / success and failure;
6. fatigue / affiliation / continuity-state variation;
7. mixed-conflict replay containing contradictory and near-neighbor contexts from blocks 1-6.

Within each block, positive, negative, neutral, and ambiguous outcomes must all occur. The outcome schedule is fixed by seed and must be written into the run artifact before the first learning step.

The harness may use the production `step()`, `reinforce_action()`, and `capture_outcome()` interfaces but may not add a challenger-only teaching signal.

### Phase 3 - frozen evaluation: 512 steps

Use `learn=False` and no reinforcement.

Present a balanced fixed probe battery containing seen, near-neighbor, opposite-context, and held-out combinations. Probe order is deterministic per seed and identical across the pair.

### Phase 4 - restart evaluation: 512 steps

Save, reload, and repeat the same probe battery with `learn=False`.

The pre-restart and post-restart conditions must begin from equivalent checkpointed state. This phase tests persistence and deterministic checkpoint recovery, not additional learning.

Total: **512 + 3,584 + 512 + 512 = 5,120 steps per profile per seed.**

## 7. Frozen primary measurements

The B03 harness must emit machine-readable values sufficient to calculate the following without rerunning the experiment.

### 7.1 Behavioral differentiation

For every evaluation probe record:

- complete ten-action probability vector;
- top action;
- action entropy;
- margin between the top two actions;
- paired control/challenger Jensen-Shannon divergence;
- pre-development versus post-development divergence within each profile;
- seen versus held-out and context-opposite response differences.

The point is not to reward difference for its own sake. A challenger that merely becomes noisier or more extreme has not improved.

### 7.2 Learning retention and interference

Record:

- response change immediately after each developmental block;
- retention of earlier block effects after later blocks;
- opposite-context interference;
- post-development retention during learning-disabled evaluation;
- persistence across save/reload.

The harness must preserve block-level measurements so catastrophic overwrite or context collapse cannot be hidden by an aggregate score.

### 7.3 Recurrent dynamics and stability

Record at fixed checkpoints:

- mean firing rate;
- `state_saturation`;
- state gain;
- recurrent gain estimate when available;
- homeostasis-event count;
- recurrent weight mean, standard deviation, absolute quantiles, minimum and maximum;
- fraction of recurrent weights at the configured clipping bound;
- excitatory/inhibitory sign violations;
- eligibility norm;
- synaptic-tag norm;
- non-finite values;
- action-distribution entropy.

A run with a finite but collapsed network remains a negative result; it is not automatically invalid.

### 7.4 Representational separation

For the fixed evaluation probes, preserve enough recurrent-state summaries to calculate:

- pairwise cosine similarity between probe states;
- within-context versus across-context state similarity;
- state-vector variance;
- covariance participation ratio/effective dimensionality using a deterministic numerical definition frozen in B03.

Raw 4,096-dimensional state snapshots may be stored in compressed artifacts if practical; if not, B03 must preregister a lossless-enough deterministic summary before B04 runs.

### 7.5 Computational cost

Record:

- wall-clock runtime;
- peak resident memory if available in the runner;
- checkpoint size;
- recurrent nonzero count;
- steps per second;
- time attributable to recurrent-gain checks when measurable.

Efficiency is secondary to causal value but is part of the production decision.

## 8. B06 causal lesions frozen in advance

B06 must use the B04/B05 artifacts and exact matched seeds. At minimum it must include:

### 8.1 Necessity lesion

Remove or neutralize the learned recurrent change responsible for the candidate effect while preserving topology and non-neural inputs as closely as the implementation allows.

Question: does a previously observed developmental effect degrade?

### 8.2 Sufficiency transplant/projection

Apply the isolated learned recurrent component or its preregistered functional equivalent to a matched baseline state without importing unrelated state.

Question: is the component sufficient to recover a measurable portion of the effect?

### 8.3 Causal-core lesion

Rank recurrent changes using a metric frozen before lesion outcomes are inspected. Compare targeted high-change removal against size-matched random removal.

Question: is the concentrated learned core disproportionately necessary?

### 8.4 Relearning after lesion

After a validated lesion, re-expose the system to the original developmental evidence under the same learning rule.

Question: does the system recover the lost function, and at what rate?

### 8.5 Sham and fixed-seed controls

Every lesion family requires a no-op/sham manipulation and a size-matched or distribution-matched control where applicable.

A lesion result without an appropriate control is descriptive, not causal evidence.

## 9. B07 topology, distribution, and clipping probes frozen in advance

B07 must preserve null results and include:

- topology-matched transfer;
- independent-topology functional-homology comparison;
- learned-delta distribution preservation with assignment permutation;
- high-change versus ordinary-edge comparison;
- recurrent-weight clipping sensitivity;
- delta clipping sensitivity;
- sign-contract verification;
- brittleness under modest perturbation;
- fixed-seed rerun controls.

No successful transfer may be described as transfer of identity. The object under study is a recurrent developmental mechanism.

## 10. Capacity adequacy: 4,096 is not assumed sufficient

This section is a binding part of the preregistration.

A negative or weak result at 4,096 units does **not** by itself establish that Neural Convergence is mechanistically unhelpful at larger capacity.

The B02-B07 program can establish that the 4,096-unit implementation is useful, harmful, stable, unstable, causally load-bearing, causally weak, or **capacity-adequacy unresolved**. It cannot infer a universal scaling ceiling from one network size.

### 10.1 Capacity-warning indicators

Before B08 may reject the challenger as a default, the evidence must be checked for the following predeclared warning signs:

1. **Representational crowding**: distinct probe families remain unusually similar in recurrent-state space while behavioral differentiation is weak.
2. **Cross-context interference**: learning later blocks reproducibly erases earlier context-specific effects across a majority of seeds.
3. **Persistent saturation or gain-bound pressure**: the network spends substantial evaluation/development time near saturation or repeatedly requires homeostatic correction in a way consistent with insufficient representational headroom.
4. **Capacity-like causal concentration**: a very small fraction of recurrent changes carries a disproportionate share of learned behavior while surrounding capacity contributes little and lesions produce severe bottleneck behavior.
5. **No observed plateau evidence**: the B02-B07 results provide no basis for claiming that increased units would fail to improve representational separation or reduce interference.

Items 1-4 are positive capacity-pressure signals. Item 5 is an epistemic constraint: absence of a scaling study is not evidence of a scaling plateau.

### 10.2 Capacity-unresolved trigger

If the 4,096 challenger is weak enough that B08 would otherwise reject it **and** either:

- at least two of indicators 1-4 are reproducibly present across at least four of six seeds; or
- B06/B07 reveal a clear bottleneck whose plausible mechanism is representational capacity rather than the convergence rule itself,

then **architectural rejection is prohibited**.

B08 must instead record:

`RETAIN OPTIONAL - CAPACITY ADEQUACY UNRESOLVED; SCALING STUDY REQUIRED BEFORE REJECTION`

A new versioned preregistration must then be written before larger networks are run.

### 10.3 Reserved scaling ladder

The reserved follow-up ladder is:

`1,024 -> 4,096 -> 16,384 -> 65,536`

This ladder is **not executed by B02-B07** and does not authorize automatic promotion of larger networks. It exists so a capacity-triggered follow-up cannot choose convenient sizes after seeing the result.

A future scaling protocol may omit a rung only for documented hardware/runtime infeasibility, and must preserve sparse-connectivity comparisons or explicitly state how connectivity scaling changes.

### 10.4 What scaling may reveal

A later study must distinguish:

- smooth benefit from increased capacity;
- a qualitative capacity threshold;
- saturation/plateau;
- worsening stability or cost;
- a bottleneck that shifts from capacity to plasticity, topology, curriculum, sensing, or another mechanism.

More neurons are not presumed better.

## 11. Decision rules for B08

B08 must use the complete B04-B07 evidence. No single aggregate score decides promotion.

### 11.1 Hard integrity gate

The challenger cannot become the production default if any unresolved issue remains in:

- deterministic fixed-seed replay where determinism is expected;
- checkpoint save/reload;
- E/I sign contract;
- non-finite state;
- unbounded/clipping failure;
- Subject Interface Firewall compatibility;
- production migration compatibility.

### 11.2 Causal gate

Promotion requires evidence that at least one claimed Neural Convergence mechanism is load-bearing under controlled lesion rather than merely correlated with a favorable output.

### 11.3 Behavioral/developmental value gate

For promotion, improvement must be reproducible across seeds and must not consist solely of larger action-vector divergence, higher noise, or stronger extremity.

At minimum:

- at least **4 of 6** matched seeds must show the same favorable direction on the claimed primary effect;
- the median paired effect must be non-trivial under the metric's B03-defined normalization;
- no primary stability or retention endpoint may show a severe unexplained regression;
- B06 must support causal attribution;
- B07 must not reveal unacceptable brittleness.

Because B03 will define the exact normalized statistics before outcome data exist, B03 may specify numerical reporting transforms but may not weaken these directional requirements.

### 11.4 Allowed B08 dispositions

1. **PROMOTE**: challenger earns production-default consideration.
2. **RETAIN OPTIONAL**: mechanism is interesting/useful but evidence is insufficient or tradeoffs do not justify a default change.
3. **RETAIN OPTIONAL - CAPACITY ADEQUACY UNRESOLVED**: 4,096 cannot fairly support rejection; scaling study required.
4. **REJECT AS DEFAULT**: evidence supports keeping legacy v0.4 as default and no preregistered capacity-unresolved trigger blocks rejection.

No result permits silent deletion of the challenger or its negative evidence.

## 12. Invalid-run and stop criteria

A run is invalid, rather than a negative scientific result, only for a predeclared technical failure:

- wrong commit/config/seed;
- mismatched input or outcome sequence within a pair;
- harness exception before the required artifact is finalized;
- corrupt or unreadable checkpoint/artifact;
- non-deterministic generation of the supposedly fixed curriculum itself;
- missing required measurements;
- runner termination or resource failure that prevents completion.

The following are **valid negative results and must be preserved**:

- poor behavioral performance;
- lack of divergence from control;
- excessive interference;
- saturation;
- recurrent collapse that remains numerically well-defined;
- inability to demonstrate lesion causality;
- failed transfer;
- poor scaling of runtime;
- greater seed variance;
- brittleness.

Do not stop the experiment merely because the challenger is losing.

## 13. Evidence and provenance requirements

Every B04-B07 artifact must contain:

- protocol version;
- repository commit SHA;
- profile;
- exact configuration;
- seed;
- phase lengths;
- curriculum hash;
- outcome-schedule hash;
- software/runtime version where available;
- timestamps;
- result payload;
- artifact SHA-256.

Human-readable summaries must point to the machine-readable artifact and may not silently replace it.

## 14. Prohibited interpretations

This program does not establish:

- consciousness;
- biological equivalence;
- a neuron-count correspondence to a human nervous system;
- that recurrent weights are Pretorius's identity;
- that larger networks are necessarily better;
- that 4,096 is sufficient;
- that failure at 4,096 proves failure at all scales;
- that success at 4,096 proves indefinite scaling;
- that a transferred recurrent core transfers a person.

The scientific claim is limited to measured causal contributions under the frozen protocol.

## 15. B02 completion condition

B02 is complete when this preregistration is committed before any B04-B07 decisive artifact is generated.

B03 may now implement only the harness and configuration machinery needed to execute this frozen protocol. It must not inspect future outcome data to redefine the experiment.
