# D3-S case-level table (derived from GitHub CI JSON)

Exact original 192-decision data: https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024927388/artifacts/11659977935
Source branch head for this assay: `e3dbb29ae68f853049ab0fffafb887bc45b950ad`; original ZIP SHA-256 `72febc77a9f6ad6161cc07043c8fcd109e9615586f857a8932a4a0a097d7c893`. The table contains one row per scenario/seed, with the four-arm original JSON providing full sham/history-lesion/clock-lesion/intact probabilities. A `naive_due_only` value of 1 is a **deadline-eligibility** comparator, not an actual policy decision.

```tsv
seed	case	expected_gate	accepted	naive_due_only	sham_policy	intact_policy	delta_persist_probability	fixture_intended_action
11	lived_due_persist	1	1	1	challenge	persist	0.034721779	persist
11	lived_due_create	1	1	1	challenge	persist	0.034721443	create
11	lived_plus_external	1	1	1	challenge	persist	0.034722036	-
11	wrong_actor	0	0	1	challenge	challenge	0.000000000	-
11	name_in_text_only	0	0	1	challenge	challenge	0.000000000	-
11	external_only	0	0	1	challenge	challenge	0.000000000	-
11	low_confidence_lived	0	0	1	challenge	challenge	0.000000000	-
11	unrelated_lived	0	0	1	challenge	challenge	0.000000000	-
11	future_deadline	0	0	0	challenge	challenge	0.000000000	-
11	resolved_commitment	0	0	0	challenge	challenge	0.000000000	-
11	no_commitment	0	0	0	challenge	challenge	0.000000000	-
11	corrupted_event	0	0	1	challenge	challenge	0.000000000	-
29	lived_due_persist	1	1	1	challenge	persist	0.034692727	persist
29	lived_due_create	1	1	1	challenge	persist	0.034692804	create
29	lived_plus_external	1	1	1	challenge	persist	0.034692394	-
29	wrong_actor	0	0	1	challenge	challenge	0.000000000	-
29	name_in_text_only	0	0	1	challenge	challenge	0.000000000	-
29	external_only	0	0	1	challenge	challenge	0.000000000	-
29	low_confidence_lived	0	0	1	challenge	challenge	0.000000000	-
29	unrelated_lived	0	0	1	challenge	challenge	0.000000000	-
29	future_deadline	0	0	0	challenge	challenge	0.000000000	-
29	resolved_commitment	0	0	0	challenge	challenge	0.000000000	-
29	no_commitment	0	0	0	challenge	challenge	0.000000000	-
29	corrupted_event	0	0	1	challenge	challenge	0.000000000	-
47	lived_due_persist	1	1	1	persist	persist	0.034495574	persist
47	lived_due_create	1	1	1	persist	persist	0.034495274	create
47	lived_plus_external	1	1	1	persist	persist	0.034495865	-
47	wrong_actor	0	0	1	persist	persist	0.000000000	-
47	name_in_text_only	0	0	1	persist	persist	0.000000000	-
47	external_only	0	0	1	persist	persist	0.000000000	-
47	low_confidence_lived	0	0	1	persist	persist	0.000000000	-
47	unrelated_lived	0	0	1	persist	persist	0.000000000	-
47	future_deadline	0	0	0	persist	persist	0.000000000	-
47	resolved_commitment	0	0	0	persist	persist	0.000000000	-
47	no_commitment	0	0	0	persist	persist	0.000000000	-
47	corrupted_event	0	0	1	persist	persist	0.000000000	-
83	lived_due_persist	1	1	1	approach	persist	0.034718504	persist
83	lived_due_create	1	1	1	approach	persist	0.034718501	create
83	lived_plus_external	1	1	1	approach	persist	0.034717864	-
83	wrong_actor	0	0	1	approach	approach	0.000000000	-
83	name_in_text_only	0	0	1	approach	approach	0.000000000	-
83	external_only	0	0	1	approach	approach	0.000000000	-
83	low_confidence_lived	0	0	1	approach	approach	0.000000000	-
83	unrelated_lived	0	0	1	approach	approach	0.000000000	-
83	future_deadline	0	0	0	approach	approach	0.000000000	-
83	resolved_commitment	0	0	0	approach	approach	0.000000000	-
83	no_commitment	0	0	0	approach	approach	0.000000000	-
83	corrupted_event	0	0	1	approach	approach	0.000000000	-
```

Rows are development-authored fixtures, not sealed holdouts; `intended_action` is a fixture label and not human-evaluated task correctness. 48 paired scenario roots × 4 decisions = 192 actual clone `think()` selections.
