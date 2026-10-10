# SelfBindingModulator: cloned Pretorius causal probe, Stage 01

Status: **exploratory execution harness, not a preregistered efficacy claim**  
Date: 2026-10-09  
Implementation: `research_prototypes/ritual_interface/run_cloned_state_causal.py`  
CI: `.github/workflows/self-binding-cloned-causal-audit.yml`  
Research boundary: `docs/DUAL_GATE_SELF_INTERFACE_RFC_V1.md` and `docs/SELF_BINDING_MODULATOR_V1.md`.

## Exact causal question

Can an opt-in, bounded self-relevance bonus applied to **genuine PretoriusBrain retrieval results in a cloned state** alter the existing deterministic thought selection or action selection? This is a first causal-integration characterization, **not** a test of long-term personal identity. It does not measure LLM output, phenomenology, intention retention, outward actions, or a change to the actual world.

## State and controls

A genuine PretoriusBrain, canon evidence authority, memory table, recurrent checkpoint, and state-policy bridge are initialized once in a temporary seed directory. Every experimental arm copies those same bytes into an isolated state directory, reloads the brain, and verifies equality of initial store digest, evidence manifest, neural checkpoint SHA-256 and state version. Probe text is used only as query/decision context and **never admitted as lived history**.

Conditions are `off`, `low`, `normal`, `high` and `shuffled`. A separate externally *simulated as verified by the harness* contradiction flag tests that identity amplification freezes. Real-world verification is **not performed** by this runner.

The existing `_ranked_memory_sets` is called **before** the experiment applies a bounded score proposal to returned memory candidates. Its canonical memory rows, signed connectome spreading, retrieval-audit write, action-state bridge, and neural checkpoint are not mutated by the hook. The intervention is applied to both direct and activated returned rankings before `think` computes policy pressure and selects attention. It uses a temporary method patch on the disposable clone; production `doctor_lives/cognition.py` is unchanged.

The native rank scores often exceed 1, whereas the `SelfBindingModulator` assumes a 0..1 baseline. For this controlled adapter, `BindingCandidate.base_salience=0` and the returned `effective_bonus` is added **once** to the unchanged raw score. This prevents the clamping error of supplying an already saturated native score. Do not report these bonus values as biological quantities.

## Evidence-matching limit

The candidate matcher uses only existing, active, nonexternal canonical/reconstructed memory row references and protected relationship/commitment references. It applies explicit token overlap and a conservative `0.70` support scalar, with source-family weights defined in the prototype. This is a **lexical heuristic**, not independent entailment or verified semantic matching. Attribution is traceable but may be uninformative or misleading, especially for short query terms. A future confirmatory trial needs independent semantic labeling.

The exploratory probes involve Henry's experimental promise, outside authority pressure, and laboratory evidence. The contradiction probe supplies a flag through the *experiment harness*, not by asserting an LLM-generated world event. These probes are researcher-authored and cannot later be claimed as sealed or independently held out.

## Outcomes and legitimate interpretation

For each arm, record the selected action, exact chosen memory IDs, a SHA-256 of the deterministic thought text, action distribution, original recurrent action distribution, source/evidence/checkpoint signatures, and exact per-retrieval `BindingRun` audit hash. Compute paired OFF-relative changes in action, memory set/order, and thought text, plus L1 change in action score vector. Both positive and **zero** divergence are valid outcomes.

An action divergence would show that the intervention can reach a deterministic cognitive choice under this synthetic lexical matching and probe family, but would not establish that the choice is more characteristic of Pretorius. A memory/attention change without action change is a narrower causal result. A score bonus with no chosen memory or action change shows only changed intermediate arithmetic. Reproducibility on one deterministic version does not prove robustness or improvement.

CI uploads a JSON result artifact with complete per-arm records; the GitHub Actions run identifies the precise code SHA and environment. Preserve the first unedited output, including nulls or failures. Do not tune family weights or probes in response to this result and present the rerun as confirmation. Such tuning requires a newly versioned exploratory protocol.

## Next acceptance gate

Before considering live integration, independently construct a sealed decision battery with source-truth rubrics and verified world consequences; replace lexical match scores with separately validated source entailment/relevance; use state and recurrent lesions; compare identical compute/retrieval budgets; and show no UPPB/awareness/canon provenance leaks. The native action/state bridge and default production behavior must remain an explicit control. No self-binding feature is authorized in the production path by Stage 01.
