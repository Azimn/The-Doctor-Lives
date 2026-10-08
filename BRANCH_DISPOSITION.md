# Pretorius Historical Branch Disposition

Status: B01 production-research inventory  
Authoritative production base: `271e87cf1f7c026594720d8ff8c9a58ce54da4fd`  
Inventory date: 2026-10-07

## Purpose

This inventory closes branch ambiguity before Neural Convergence characterization. Historical branches are evidence and donor material, not parallel production brains. Nothing in this document authorizes a mechanical merge of a historical line.

The disposition vocabulary is intentionally strict:

- **SUPERSEDED**: the production result or stronger successor is already represented on current `main`; do not merge the branch.
- **EVIDENCE-ONLY**: preserve the branch as historical validation, audit, or reproducibility evidence; it is not an implementation donor for current production.
- **DONOR-ONLY**: one or more ideas, contracts, tests, or mechanisms remain useful to later gates, but they must be semantically reimplemented against current production contracts rather than merged.
- **UNIQUE-TRANSPLANT-NEEDED**: a specific implementation is still required in production and has no accepted equivalent. Any such item must name the exact transplant before later work proceeds.

## Authoritative rule

Current `main` is the only production line. A branch being divergent or containing unique commits is not evidence that it should be merged. Donor use means inspect, preregister, reimplement minimally on a fresh production branch, test causally, and independently review.

The Subjective Perspective North Star and First-Person Subject Interface Contract remain global invariants. No donor mechanism may bypass the subject interface merely because its historical implementation predates that boundary.

## Exact branch inventory

| Branch | Exact head | Relationship to current main | Disposition | Production meaning |
| --- | --- | --- | --- | --- |
| `docs/reddit-derived-next-things` | `1c43d61eb945e4e1700679bc8f25240e9412de9d` | ancestor of main | **SUPERSEDED** | Planning documents and runbook were converged into production. Retain branch only as historical provenance. |
| `feature/pretorius-causal-audit-v0.3` | `32dfc46c08e238a6e38f75888ad0c68b1dbc8322` | divergent historical audit line | **EVIDENCE-ONLY** | Preserve causal-audit results, lesions, and negative findings. Current production has the accepted causal-audit lineage; do not merge this branch. |
| `feature/pretorius-deep-history-v1` | `717f42a162609a8884e8685ce46ea1cb73709ed6` | divergent historical implementation | **EVIDENCE-ONLY** | v1 is migration/evolution evidence. Deep-History v2 and later accepted production contracts supersede it. |
| `feature/pretorius-deep-history-v2` | `723ba07cecf5533cea343da088ab930a0d6d1adb` | divergent historical implementation | **EVIDENCE-ONLY** | Preserve schema/validator and migration history. Modern canonical-evidence and migration gates supersede it as a production line. |
| `feature/pretorius-neural-convergence-v05` | `cf009630f1c623b0bcac1eb9e5e7242fa3e8a0e7` | divergent; 2 commits unique versus current main | **DONOR-ONLY** | Scientifically important challenger. Its 4,096-unit recurrent configuration and felt-interoceptive-loop work feed B02-B07 characterization. Do not merge or call it identity continuity. |
| `feature/pretorius-state-policy-v0.4` | `3500d4c31fc8b5d0289ae8e6312dd8f868794aaa` | ancestor of main | **SUPERSEDED** | State-policy integration is already represented by stronger accepted production descendants. |
| `feature/universal-phenomenal-projection` | `06b8fec7cc2953defb384851f335f15ab8538375` | ancestor of main | **SUPERSEDED** | UPPB research is already represented in current production/planning and strengthened by the Subject Interface Firewall. |
| `integration/brain-v0.1` | `ad2c98c672316a6b6bb91e6354efae9e5583b2a3` | divergent early integration line | **DONOR-ONLY** | Preserve registry/persistence-boundary decisions as design evidence. Reuse semantics only through current host/runtime gates. |
| `integration/chassis-selection-v0.1` | `30b14df462a9785d4f0e69fc14dbe235c98da807` | divergent; 1 unique commit versus current main | **DONOR-ONLY** | Preserve the reversible chassis decision and brain/chassis ownership boundary. Gate 5/Bride integration must reimplement against current interfaces. |
| `integration/pretorius-brain-v0.1` | `6237bb99e6b036f7da45ce384964aa3b598a5237` | divergent early brain assembly | **DONOR-ONLY** | Preserve early chassis-save and assembly lessons. No wholesale transplant; current production brain/store contracts are authoritative. |
| `pretorius-v0.4-policy-bridge` | `02068362af6a969a3788a9fcbcd0b667644d25fd` | ancestor of main | **SUPERSEDED** | Policy bridge is already incorporated into later production history. |
| `prod/gate1-evidence-integrity` | `dfca40016bf29748fa38a23f43b47fc4a18e091b` | accepted ancestor of main | **SUPERSEDED** | Gate 1 was independently accepted and merged. Branch is closed production provenance, not an active line. |
| `prod/subject-interface-firewall` | `fe3dc237248200670457ad4cb6b3f04546c5f926` | accepted parent of current main | **SUPERSEDED** | A09-A13 were independently accepted and merged normally. The firewall now belongs to production main. |
| `release/pretorius-v0.5-rc1` | `d1567f3243b928b9086ba2b13ce59ee345fe1009` | ancestor of main | **SUPERSEDED** | Accepted RC1 is preserved in ancestry; later RC2/Gate 1/firewall production state supersedes it. |
| `validation/a07-media` | `0e2ae65b5e678ebf31cfc7c6c3f009fee03cf187` | divergent validation packaging line | **EVIDENCE-ONLY** | Preserve end-user-machine validation media/workflow provenance. Validation packaging is not production cognition. |
| `main` | `271e87cf1f7c026594720d8ff8c9a58ce54da4fd` | authoritative | **PRODUCTION** | Sole production line and base for Phase B. |

## Unique-transplant decision

**No historical The-Doctor-Lives branch currently qualifies as UNIQUE-TRANSPLANT-NEEDED.**

That is a substantive result. The divergent branches contain useful evidence, experimental mechanisms, or architectural lessons, but no branch contains a production implementation that should be transplanted verbatim before Phase B can continue.

The closest case is `feature/pretorius-neural-convergence-v05`. Its unique work must remain a challenger until B02-B07 establish whether the 4,096-unit configuration improves the accepted production substrate under matched causal tests. If it wins, production changes will be implemented deliberately on the Phase B branch rather than by merging the historical branch.

## Phase B donor map

B02-B07 may consult these branches without changing their disposition:

- Neural Convergence: `feature/pretorius-neural-convergence-v05@cf009630f1c623b0bcac1eb9e5e7242fa3e8a0e7`
- Causal-audit methodology/results: `feature/pretorius-causal-audit-v0.3@32dfc46c08e238a6e38f75888ad0c68b1dbc8322`
- historical state-policy baseline: `feature/pretorius-state-policy-v0.4@3500d4c31fc8b5d0289ae8e6312dd8f868794aaa`
- UPPB/first-person constraints: `feature/universal-phenomenal-projection@06b8fec7cc2953defb384851f335f15ab8538375`, with current `main` taking precedence wherever the historical line conflicts with the North Star or Subject Interface Firewall.

External donor repositories remain governed by `PRETORIUS_DONOR_BRANCH_AUDIT.md`; this B01 file classifies only branches in The-Doctor-Lives.

## Branch-convergence conclusion

Branch ambiguity is closed for the start of Phase B:

1. `main` is authoritative.
2. historical branches are not alternate products;
3. no historical branch is authorized for mechanical merge;
4. no unique transplant blocks B02;
5. Neural Convergence remains an evidence-gated challenger;
6. all later promoted behavior must be rebuilt against current production persistence, provenance, first-person subject-interface, and review contracts.

B02 may now freeze the 4,096-unit Neural Convergence characterization protocol without reopening historical branch convergence.
