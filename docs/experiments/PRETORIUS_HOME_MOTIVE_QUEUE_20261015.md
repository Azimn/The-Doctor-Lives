# Pretorius at home: motives, object affordances and interruptible activities

**Date:** 2026-10-15 · **Status:** experimental, opt-in, isolated real-Doctor pilot.  
**Inspired by:** The Sims' pragmatic combination of domestic motives, object affordances, action selection and interrupted routines—not by reimplementing The Sims, its artwork, or any proprietary system.

## Architecture and boundary

Use the actual, unchanged `PretoriusBrainPort` for identity, persistent memory,
neural tendencies and future autobiographical retrieval. The existing
`DoctorHomeBridge` delivers material, source-verified physical observations
from the standalone Pretorius Laboratory's `SubjectPort` as **natural-language
first-person experience only**. A newly bounded host-level
`home_motive_queue.HomeActivityQueue` provides:

1. **Motive scores**, deliberately simple engineering rules over authorized
   fatigue, thirst, hunger, laboratory equipment condition and surrounding
   clutter. Existing native ten-action recurrent scores add a small frozen
   preference to these externally defined needs. Nothing changes the neural
   checkpoint or forges a Doctor thought.
2. **Actual object affordances** gating household actions against finite
   fuel, food, water, tea, reagents, repair parts, location, illumination,
   exhaustion and previously prepared meals. The physical Laboratory must
   still accept every action independently.
3. **Interruptible physical activity plans**: nearest reachable station,
   possible illumination, then the genuine local house or laboratory action.
   The ledger stores only host permissions, plan steps, receipts and current
   progress; it is *not* a second personal memory store.
4. **Persistent start/pause/resume/cancel** with a material-state fingerprint.
   Restart does not erase work. External world changes cause the pending
   plan to pause rather than performing previously arranged actions against
   a changed environment. A second active plan cannot supersede the first
   without explicit cancellation/completion.
5. **Exactly-one-action-per-host-step**. Every activity is bounded to a
   declared twelve-step construction maximum, with experiment comparisons
   enforcing at most nine actions for every arm. No background daemon,
   autonomous real-time scheduler or implied free movement.

The planning and verification APIs return **engineer-only** details such as
scores and event hashes. Those never enter the Doctor's actual subject frame.
The only subjective output of a performed step is the inherited
`{"inner": first-person natural-language text, "spoken_aloud": optional speech}`.
A spontaneous foot collision/utterance can occur during travel without a
deliberative neural action.

## Initial actions

`experiment` consumes reagents, wears apparatus and increases fatigue/
clutter; `repair` consumes scarce parts; `rest` uses the real bedroom and
advances simulated time; `tea` uses water, fuel and tea in the kitchen;
`meal` prepares and eats an available ration; `clean` clears work-area
condition using time. A task's mere selection never awards success.
The physics ledger must record genuine material changes.

These six verbs are an **initial household action vocabulary**, not a
psychological definition of his wishes. Keep his contrary preferences,
long-term projects and sense of self in the original brain. Do not make
"fatigue is high" automatically mean he wants to sleep; it means an actual
competing motive can interfere with ongoing research. Do not pretend
numerical utility directly appears in his subjective consciousness.

## Causal comparison

Existing negative control: [actual Doctor home task pilot](../../results/cascade/ACTUAL_DOCTOR_HOME_CHOICE_PILOT_20261015.json)
obtained native-Doctor **1/4** useful household actions versus a strong
current-frame simple rule **4/4** in four authored scenarios.

The new opt-in four-arm comparison includes:
- **Native only**: same unmodified ten-action neural policy and previously
  declared fixed abstract-to-household mapping.
- **Native plus bounded motive arbitration**: actual recurrent scores
  contribute to household motives; bodily needs and material affordances
  influence priority; a physical activity queue executes a finite plan.
- **Body-priority lesion**: same recurrent scores and physical affordance
  gates, but no bodily utility pressure. Invalid or impossible actions
  remain physically vetoed.
- **Simple first-person rule**: deliberately strong cheap controller using
  the identical current first-person frame; the real Doctor brain still
  receives the same cognitive opportunity, without contributing to choice.

All arms start from independently constructed but materially identical
physical world conditions and exactly the same first-person sensory text
for each case, use the same physical Laboratories, and have at most nine
physical actions. The action routing helper is a **host-supplied advantage**
common to the arms, not a cognitive success. Body priority receives
privileged simulated physiology **in the trusted environment controller**
only; the native Doctor itself never reads numeric state, and this
information advantage is an important qualification on outcome claims.
The comparison measures whether a simple ecological scaffolding improves
task completion, *not* whether a learned neural action policy became good
at household work.

**Results must come from actual CI; never predeclare victory**. Record
mechanical success and failure, bad or infeasible proposals, the bodily
lesion, matched perception and physical action budget. No hidden
post-hoc adjustment of coefficients to make all outcomes look good.

## Reliability boundaries

Normal interruption and program restart are restart-safe. The queue refuses
to resume if the Laboratory world changes during its pause. The queue
does not yet **automatically reconcile** a rare crash between a committed
physical action and a later queue cursor update: it fails closed and
requires an explicit engineering reconciliation, to prevent duplicating
movement, consumed stock or bodily reactions. The full authorized
physical world remains the source of truth. A later change can add
proven safe post-crash recovery, with a high-quality paired test.

None of this authorizes irreversible external correspondence, Village
travel, changes to the small storefront or public sales, sentience
claims, scored 34-Article qualification, or adding a new authoritative
pretend autobiographical memory record.

## How to verify

Use the dedicated `.github/workflows/home-motive-queue.yml` workflow.
It pins the previously tested independent Pretorius-Laboratory commit
`6e49795752835d64fa6fd63d16359669a1ca2ba7`, runs the home motive
and queue unit tests, then an isolated physical action comparison, and
archives the complete JSON experiment report.

Next: withheld start times and room states, multi-object priority conflicts,
supply scarcity, sleep interrupting planned experiments, unavailable lamp
oil, prospective commitments and longitudinal learned routines. Each
mechanism will be compared against a cost- and information-matched simple
controller. Keep a strict distinction between code correctness and
behavioral evidence.

The overall Article tracker remains **46/100 engineering** until
independent causal and transfer requirements are satisfied.
