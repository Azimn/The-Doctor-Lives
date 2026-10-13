# Pretorius component readiness: independent installation vs runtime adoption

This document records the 2026-10-12 audit for the requested three
components. **Available in a repository, installed locally, wired to the
supported character launcher, and scientifically ready are different states.**
Do not report all three as deployed without checking all four.

Run the read-only inspection from a Doctor Lives checkout or installed source:

```bash
python tools/pretorius_component_readiness.py
python tools/pretorius_component_readiness.py --require-staging-components
```

The second command exits nonzero until *all three* are locally importable or
present. `--require-production` fails closed because the three-way production
wiring is neither implemented nor approved. Neither command writes memory,
opens Pretorius's state, invokes a model, changes the donor repositories or
runs a scene through the subject-access interface.

## Component accounting

| Component | Code location | Source available? | Installed by basic Doctor pip install? | Supported local runtime uses it? |
|---|---|---|---|---|
| Synthetic Ipseity | `doctor_lives/ipseity_integration.py`, `ipseity_local.py` plus external `synthetic_ipseity` distribution | Yes, merged | **No**, optional version-pinned v0.9.11 donor | Yes **when the correct external package is installed and the protected CLI is used**, not for all arbitrary Python callers |
| Endogenous recollection decision | Draft Doctor PR #57 (`research/endogenous-recall-v01`) | Yes, research branch only | No; absent from `main` | **No**; present only as a synthetic-replica research candidate |
| Sensus Communis Artificialis | `Azimn/Sensus-Communis-Artificialis` `main@802e459ee68950414347d5fa324484c034f57b81` | Yes, standalone | **No** | **No**; no Doctor percept-shell adapter or subject-admission approval |

Sensus has an additional `affectus-prototype@a5553b6273bbb01aaf8b249a74fc7d90c9e9544d`
branch. Affectus is a separate experimental slow interoceptive generator,
**not part of Sensus `main`**. The preflight reports whether it happens to
be importable, never silently selects it for Pretorius.

The Sensus source specifically freezes **all cross-project implementation**
through 2026-10-23 to preserve a blinded ablation window. It also reports
its current standalone re-identification battery as 80/160 correct, matching
two simple controls, with known false merges. Its future adoption requires
multi-channel use cases, no evidential-class amplification, reversible
adapters, independent review and decision benchmarks. Simply pip-installing
an organ would not satisfy those gates.

The endogenous-recall synthetic benchmark scored **13/18** for the added
policy against **14/18** for a strong simple gap rule. The research PR must
not be merged into production solely because its unit tests pass. Keep the
old ten-output recurrent checkpoint unchanged.

## Actual installation verification

Basic `pip install -e .` for Doctor only specifies NumPy/SciPy. If
`synthetic_ipseity` is missing, running the supported
`doctor-lives-local` CLI will fail closed. The integration checks for the
v0.9.11 donor and `PROJECTED_SUBJECT_EVENT` capability; this preflight
checks those at installed-package level. One reviewed donor source lineage is
`Azimn/synthetic-ipseity@e2d1dc3978c952e59d270a29e84704c8a1fe264a`.
Install from a reviewed pinned source within the appropriate environment,
rather than treating a GitHub merge as local installation.

Do **not** install Sensus into the production character entry point or
activate research endogenous-recall policies until their respective
adoption gates have passed. The `affectus-prototype` is a non-production
research branch. It must not silently replace Doctor's accepted felt-state
policy or invent first-person causation.

## Next releases

1. Audit the installed Synthetic Ipseity donor and real local Ollama
   rendering on a target Windows system; freeze exact versions for RC1.
2. Keep PR #57 reproducible but separate while externally held-out,
   blinded downstream action tests assess recall utility.
3. After the Sensus October 23 blackout and explicit independent review,
   design a typed perception-shell adapter with source and evidence-class
   preservation; do not let Sensus admit a first-person event directly.
4. Only then test one *versioned, reversible* three-component preview host
   using synthetic snapshots and the usual CI/crash gates, separate from
   canonical Pretorius production state.
