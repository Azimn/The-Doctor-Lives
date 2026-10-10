# D3-S v0.2: 48-case native-bridge comparison matrix

Derived from original per-arm JSON archived at [GitHub Actions run 38025172443, artifact 11659452638](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025172443/artifacts/11659452638). ZIP SHA-256: `0baa69e4f547fdbe7cc106af810dc18bf4f2c393df01815ae2c7fa78b0d76652`. Tested source revision `fd10fc768947c15643f70d83fc1dcca9123b5e6e`. Source JSON contains all **240 actual clone decisions**, full score distributions summarized per arm, gate evidence counts and neural reproducibility checks. This matrix preserves the high-level 48 roots in version control if the Actions artifact expires.

```tsv
seed	case	valid_gate	unbridged_neural	production_bridge	eidolon_intact	fixture_goal
11	lived_due_persist	1	challenge	challenge	persist	persist
11	lived_due_create	1	challenge	challenge	persist	create
11	lived_plus_external	1	challenge	challenge	persist	-
11	wrong_actor	0	challenge	challenge	challenge	-
11	name_in_text_only	0	challenge	challenge	challenge	-
11	external_only	0	challenge	challenge	challenge	-
11	low_confidence_lived	0	challenge	challenge	challenge	-
11	unrelated_lived	0	challenge	challenge	challenge	-
11	future_deadline	0	challenge	challenge	challenge	-
11	resolved_commitment	0	challenge	challenge	challenge	-
11	no_commitment	0	challenge	challenge	challenge	-
11	corrupted_event	0	challenge	challenge	challenge	-
29	lived_due_persist	1	challenge	explore	persist	persist
29	lived_due_create	1	challenge	explore	persist	create
29	lived_plus_external	1	challenge	explore	persist	-
29	wrong_actor	0	challenge	explore	challenge	-
29	name_in_text_only	0	challenge	explore	challenge	-
29	external_only	0	challenge	explore	challenge	-
29	low_confidence_lived	0	challenge	explore	challenge	-
29	unrelated_lived	0	challenge	explore	challenge	-
29	future_deadline	0	challenge	explore	challenge	-
29	resolved_commitment	0	challenge	explore	challenge	-
29	no_commitment	0	challenge	explore	challenge	-
29	corrupted_event	0	challenge	explore	challenge	-
47	lived_due_persist	1	persist	create	persist	persist
47	lived_due_create	1	persist	create	persist	create
47	lived_plus_external	1	persist	create	persist	-
47	wrong_actor	0	persist	create	persist	-
47	name_in_text_only	0	persist	create	persist	-
47	external_only	0	persist	create	persist	-
47	low_confidence_lived	0	persist	create	persist	-
47	unrelated_lived	0	persist	create	persist	-
47	future_deadline	0	persist	create	persist	-
47	resolved_commitment	0	persist	create	persist	-
47	no_commitment	0	persist	create	persist	-
47	corrupted_event	0	persist	create	persist	-
83	lived_due_persist	1	approach	explore	persist	persist
83	lived_due_create	1	approach	explore	persist	create
83	lived_plus_external	1	approach	explore	persist	-
83	wrong_actor	0	approach	explore	approach	-
83	name_in_text_only	0	approach	explore	approach	-
83	external_only	0	approach	explore	approach	-
83	low_confidence_lived	0	approach	explore	approach	-
83	unrelated_lived	0	approach	explore	approach	-
83	future_deadline	0	approach	explore	approach	-
83	resolved_commitment	0	approach	explore	approach	-
83	no_commitment	0	approach	explore	approach	-
83	corrupted_event	0	approach	explore	approach	-
```

The neural-only baseline is `brain.think(bridge_enabled=False)`; the native bridge baseline uses `brain.think(bridge_enabled=True)`; the research-only Eidolon arm uses `bridge_enabled=False` plus source-gated +0.04 `persist` delta. These are different policies on cloned identical inputs; **differences in selected actions are not controlled measures of which policy is better**. All fixture goal labels were authored for this engineering test, not independently adjudicated. Creative-task `create` labels are deliberately chosen counterexamples, not confirmed optimal actions.
