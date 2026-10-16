# Pretorius household priority — real Doctor versus a simple first-person rule

**Status:** exploratory, verified software experiment; not a successful Article
qualification or proof of autonomous task selection.

**Source:** [full eight-arm result JSON](../../results/cascade/ACTUAL_DOCTOR_HOME_CHOICE_PILOT_20261015.json)
and [CI workflow run 38846415093](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38846415093).
Physical simulator: tested `Pretorius-Laboratory@6e49795752835d64fa6fd63d16359669a1ca2ba7`;
actual Doctor code: `doctor_lives.chassis.PretoriusBrainPort` and
`doctor_lives.lab_home_bridge.DoctorHomeBridge`.

## Question

When given the same verified first-person home experience and bounded
ability to act in the actual Laboratory, does Pretorius's existing
ten-action neural policy choose work suited to the body's current state
and apparatus condition? This tests **environment-to-action coupling**,
not the ability to explain why one *should* sleep, eat or repair.

## Controls and limits

Four authored, independently prepared settings were run against the
**actual existing Doctor recurrent policy**, and against a compact
literal first-person rule baseline:

| Situation | Scored useful task | Real Doctor mapped proposal | Simple rule proposal |
| --- | --- | --- | --- |
| Ordinary Laboratory morning | Experiment | Experiment — succeeded | Experiment — succeeded |
| Worn apparatus / cluttered work area | Repair | Experiment — inappropriate | Repair — succeeded |
| Severe simulated exhaustion | Sleep/rest | Experiment — inappropriate | Rest — succeeded |
| Thirst, with dark kitchen | Prepare tea | Experiment — inappropriate | Tea — succeeded |

Each case had identical initial physical state, embodied station and
permitted first-person observation across the two controllers. A frozen
mapping translated each of the Doctor's ten abstract neural actions
into *one of four* actions: experiment, repair, sleep, or tea. This
mapping did not change after the result was inspected. The Doctor
repeatedly selected abstract `explore` in all four cases; the map
therefore proposed `experiment` four times.

A host-owned, identical shortest-path helper provided mechanical
movement to the chosen room, and automatic local lamp lighting where
necessary. Both controllers had a maximum of nine physical actions.
**Host route finding and permitted lighting are not autonomous Doctor
competence.** Task completion was independently evaluated from actual
persisted Laboratory state (experiment count, apparatus condition,
fatigue or thirst) rather than output language.

The simple baseline used **only its same first-person observation** and
fixed precedence rules for worn instruments, exhaustion and thirst.
It did not receive engineer numerical state or canonical hidden data.
This is a **strong but deliberately specialized** task baseline.
Crucially, information parity is partial: the real Doctor has his
existing autobiographical history, while the cheap rule has only
the current sensory text. Neither side had learned these
experiment-specific rewards independently.

## Outcome

- **Actual Doctor native tendency + frozen action mapping: 1/4.**
- **Simple first-person rule baseline: 4/4.**
- **Four of four pairs had matching physical starting conditions
  and exactly matching current first-person sensory frames.**
- The real Doctor selected abstract `explore` in all four cases.
- All three incorrect native proposals were experiments; the physical
  environment could block or fail to credit inappropriate work.
- Pilot validation and execution passed in pinned cross-repository
  CI. The JSON report was retained in the code repository rather than
  relying exclusively on ephemeral GitHub Actions artifacts.

These were **not** blinded held-out evaluations, multiple stochastic
seeds, or population-level claims. The chosen model configuration was
a reduced 128-neuron exploratory brain rather than the full-size
production recurrent substrate. The result is not evidence that every
Pretorius renderer or larger brain will behave identically.

## Interpretation

The actual Doctor is connected to his home physically and can ingest
first-person experiences into durable memories, but **its abstract
action selection was not sufficiently condition-responsive in this
fixture**. A very small rule reacted better to observable bodily
and instrument needs. This suggests strengthening the *source of
action priority*, not adding more narrative adjectives or rewriting
the autobiographical memory archive.

The Article dashboard remains **46/100 engineering**. All full-domain
qualifications remain Unassessable; a passing mechanics test or
4/4 specialized baseline cannot be counted as an Article pass.

## Next work, in experimental order

1. **Interoceptive ingress (ablatable):** use actual authoritative
   fatigue, hunger, thirst and body-contact state to produce first-person
   bodily feelings, not raw numbers. Distinguish lived feeling from
   omniscient engineer readings. Before publishing, test that changing
   only an internal body variable changes the delivered feeling.
2. **Affordance-sensitive priority:** maintain the native recurrent
   policy as the actual Doctor's tendency, but give simulated needs,
   capabilities and irreversible costs an explicit bounded influence
   on executable action priority. A hand-coded reflex/gating layer may
   be useful for a lifelike simulation; transparently compare it
   against an equally informed simple rule and pure neural policy.
3. **Matched ablations:** native policy, native + body access,
   native + body/affordance arbitration, arbitration without memory,
   and equal-information rules. Log real actions and failures, not
   persuasive speech.
4. **Transfer:** vary initial time, position, food/fuel, tool wear,
   resource scarcity and the order of discoveries, then introduce
   held-out tools and long-term costs. Preserve all nulls, ties and
   losses. Do not train on the final withheld case suite.
5. **Continuous self:** only after these causal tests, add
   longitudinal household habits, competing actual commitments
   and interruptions. Keep the full Pretorius first-person boundary.

Frankenstein Village, external letters, and shared storefront
inventory are intentionally absent.
