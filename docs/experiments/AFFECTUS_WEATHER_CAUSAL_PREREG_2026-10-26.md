# Preregistered restricted Affectus weather modulation ablation

**Status:** design locked before any experimental execution. Standalone draft PR based on six-organ draft PR #89; no production entrypoint changes, no main merge, and no writes to #89.

**Baseline:** PR #89 at `e8c770a0140991dc308e194a79adcee148ab2248`, default `main` at `784cff39d58a7fe46bb5e4ffc16e0284e6663c78`. Governance: `docs/architecture/SIX_ORGAN_MECHANISM_ADOPTION_DECISION.md` and `docs/experiments/AFFECTUS_SPINOZA_PROSPECTIVE_AUDIT_2026-10-26.md`.

The donor is `Azimn/Sensus-Communis-Artificialis`, exact reviewed `904bf11861700739ccc03d4b0d4340ff3422a7d3`, module `sensus_artificialis/affectus.py`. Its transition direction tokens report **recent** change in state; this experiment neither interprets them as another capability nor alters their configuration. The historical 48/57 overlapping result and 144/294 independent holdout stay unchanged and are **not** acceptance data for this mechanism.

## Previous code and its limitations

- Existing `VerifiedLaboratoryAffectPilot`, first added at `08bf7822dda3d2fdcdb240807ff03ed353dabba1`, verified at `557a36c9630c9770de006bad1dd35dc17eac48b9`, and controls through `958bdf2ad03a225e8421daa83caf5d790ee024a0`, does genuinely attest Lab injury, admit its first-person bodily frame to the canonical brain, and test no duplicate admission, restart and lesion.
- It changes **threat appraisal** between arms, so need state is **not matched**; reports need-policy score difference but **no counted downstream selected-policy change** relative to a needs-only baseline. That effect does not qualify the weather donor, and this experiment neither duplicates nor alters its trusted injury path.
- The earlier Sensus conflict veto, Mnemosyne recollection, durable Ipseity, and real-world Noesis–Corpus causal work remain separate and unchanged. Here no external percept is admitted, no world action is issued, and no private renderer receives engineer diagnostics.

## Two-arm causal experiment (locked before results)

**Independent matched episodes:** 40 seed pairs, seeds 2000–2039. Fixed canonical Doctor neural configuration: `neurons=128`, `sensory_dim=64`, `avg_recurrent_degree=8`, `input_degree=4`, `action_population_size=8`, same seed in both arms. Identical initial single-brain needs, recurrent scores, all observed memories (none externally injected), and world context (neither arm instantiates a world). Each arm consists of its *own short-lived experimental copy of the same canonical Pretorius*, evaluated sequentially; these are separate controlled-run alternatives, never concurrently deployed beings or persistent identities.

**Weather ON:** the **unchanged pinned donor**, default configuration, evolves for 80 ticks under the same predeclared host-fixture driver program. All eight abstract driver kinds cycle in their canonical declared order in contiguous blocks of four ticks, with a fixed eight-magnitude sequence `[1.0,-0.75,0.8,0.9,0.6,0.5,0.65,-0.4]`. The reference reflects the donor's full habituation, opponent processes, slow decay, RNG and modulation outputs. These are **engineering-only experimental drivers**, not claims of sourced lived observations.

**Weather OFF:** same donor dynamics, driver sequence and seed *still computed* (ensures exactly the same underlying weather), but its modulation is **lesioned** at the original cognitive-policy entry point. The original needs-only `PretoriusBrain._state_policy_scores` stays unchanged.

**Fixed coupling rule:** use only `Modulation.exploration_bias` as a bounded *score delta* in the existing (single) cognitive score map: `delta=0.05*exploration_bias`; add to `explore`, subtract from `persist`, positivity floor `1e-9`, then renormalize. `0.05` is the existing original family cap, fixed here before running. Selection and durable thought/policy record remain owned by the original `PretoriusBrain.think`; no new action selector or task planner. `salience_gain`, `rehearsal_bias`, and `decay_multiplier` are explicitly **unconsumed** by all decisions in this test; their presence is NOT credited as a causal effect.

**Primary endpoint (no post-hoc changes):** number of matched pairs with different *selected policy tendency*, over 40; report numerator, denominator, rate, action-score differences separately, original neural and needs parity. If 0/40 differ, the weather modulation is **decoration on this battery** and this round STOPS without tuning the coupling or seed/drivers.

**Secondary task-proxy endpoint IF decisions differ:** predeclared host task is either seek new evidence (`explore`, even seed), or continue an unfinished obligation (`persist`, odd seed), so the measurable **tendency-to-task match** is `selected_tendency == target`. Compare correct/40 for weather ON, weather OFF needs-only, and a trivial exact-label controller (40/40 by construction). This is *not* world task completion, bodily safety or autonomous goal selection, and can show no advantage. No world effects may be claimed without separate Laboratory receipts.

**Lesion control:** OFF is identical except no consumed weather modulation. **Restart control:** prove donor `snapshot/restore` maintains weather and dynamics; separately reopen the normal canonical Pretorius checkpoint and assert this isolated, ephemeral experimental weather is **not durably attached**. Failure of durable integration must be recorded as a blocker, not hidden as success.

**Adoption gate:** only a counted downstream change provides a causal signal; task-proxy gains against needs-only and simple controller require objective further tasks before any graduation. A zero count requires stopping with decoration. No holdout metric alterations, no extra persistent stores, no output of raw affect telemetry to subject-facing text.
