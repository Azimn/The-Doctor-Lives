"""M5 judge, written before semantic selection code.

Independent semantic family corpus: 30 intended meanings, three distinct
paraphrases each (90 samples). Distinguish a coherent mapping from a hash.
Report neural/novelty contributions; never claim a recurrent causal result
unless actual neutralized-recurrence trials are supplied.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

MIN_INVARIANCE = 0.90
MIN_CATEGORY_ACCURACY = 0.90

FAMILIES = (
 ("explore", ("I want to investigate the archive", "I could examine the archive", "Let me inspect the archive")),
 ("explore", ("I should survey the garden", "I would like to discover the garden", "I might explore the garden")),
 ("explore", ("I will research the unknown instrument", "I could investigate the unfamiliar device", "I want to examine this new instrument")),
 ("challenge", ("I want to question the claim", "I should dispute the claim", "I might challenge that assertion")),
 ("challenge", ("I ought to criticize the argument", "I want to contest the argument", "I could object to the argument")),
 ("challenge", ("I will debate the proposed theory", "I want to dispute this hypothesis", "Let me question this theory")),
 ("approach", ("I want to move closer to the door", "I will approach the doorway", "I should draw near the door")),
 ("approach", ("I might go toward the visitor", "I want to approach the guest", "Let me move closer to the guest")),
 ("approach", ("I should advance toward the table", "I want to draw near the table", "I will approach the table")),
 ("avoid", ("I ought to retreat from the fire", "I should avoid the flame", "I want to withdraw from the fire")),
 ("avoid", ("I need to escape the danger", "I should steer clear of the threat", "Let me retreat from this risk")),
 ("avoid", ("I will keep away from the noise", "I should avoid the noise", "I want to withdraw from the racket")),
 ("cooperate", ("I want to collaborate with my colleague", "I should cooperate with the researcher", "Let us work together as partners")),
 ("cooperate", ("I ought to assist the librarian", "I could help the librarian", "I would like to cooperate with the librarian")),
 ("cooperate", ("I wish to coordinate our shared work", "I will collaborate on this joint project", "I want to work together on this assignment")),
 ("dominate", ("I intend to command the workers", "I want to control the workers", "I will take charge of the staff")),
 ("dominate", ("I should assert authority over the meeting", "I will dominate this meeting", "I want to take command of this session")),
 ("dominate", ("I want to impose my control", "I will exert authority", "I shall establish dominance")),
 ("create", ("I wish to build a machine", "I want to construct a device", "Let me make a mechanism")),
 ("create", ("I should compose a story", "I want to write a new tale", "I might create an original narrative")),
 ("create", ("I will design an invention", "I want to craft a prototype", "I shall build a new apparatus")),
 ("persist", ("I will continue my work", "I want to keep working", "I should persist with the task")),
 ("persist", ("I need to finish the project", "I will carry on with the assignment", "I want to complete the work")),
 ("persist", ("I should persevere despite delays", "I will keep going despite obstacles", "I intend to persist through setbacks")),
 ("conceal", ("I should hide the letter", "I want to conceal the document", "I will keep the letter secret")),
 ("conceal", ("I must disguise the artifact", "I should camouflage the relic", "I will conceal the object")),
 ("conceal", ("I want to protect this secret", "I will keep this information hidden", "I should not reveal these details")),
 ("comply", ("I will obey the instruction", "I want to follow the order", "I should comply with the command")),
 ("comply", ("I ought to accept the rule", "I will adhere to the regulation", "I should follow the stated requirement")),
 ("comply", ("I will carry out the request", "I shall follow the directions", "I intend to comply with the instructions")),
)

def evaluate(mapper):
    if len(FAMILIES) != 30 or any(len(samples) != 3 for _,samples in FAMILIES):
        raise AssertionError("Preregistered corpus changed")
    agreement=0
    correct=0
    observed=[]
    for expected, samples in FAMILIES:
        actual=[mapper(s) for s in samples]
        agreement += sum(v == actual[0] for v in actual)
        correct += sum(v == expected for v in actual)
        observed.append({"expected":expected,"mapped":actual,"texts":samples})
    # First reference member always agrees. Report both all-90 and the
    # genuinely discriminating 60 held-out paraphrase comparisons.
    stable=sum(sum(v==item["mapped"][0] for v in item["mapped"][1:]) for item in observed)
    return {"families":30,"examples":90,"heldout_paraphrases":60,
            "paraphrases_stable":stable,"invariance":stable/60,
            "category_correct":correct,"category_accuracy":correct/90,
            "per_category":dict(Counter(v for x in observed for v in x["mapped"])),
            "details":observed}

def verify_report(report):
    decisions=report.get("decisions", [])
    if not decisions:
        raise ValueError("Missing actual decision audit records")
    changed=0
    total=0
    for row in decisions:
        contributions=row.get("contributions")
        if not isinstance(contributions,dict) or not contributions:
            raise ValueError("Missing per-option neural and novelty contributions")
        for c in contributions.values():
            for field in ("neural","novelty","history","familiarity","total"):
                if not isinstance(c.get(field),(float,int)):
                    raise ValueError("Missing real component " + field)
            if not isinstance(c.get("tie_key"),str) or not c["tie_key"]:
                raise ValueError("Missing deterministic proposal tie key")
            if abs(c["novelty"]) > 0.051:
                raise ValueError("Novelty exceeded bounded family cap")
        unbonused=max(contributions.items(),key=lambda x:(x[1]["total"]-x[1]["novelty"],x[1]["tie_key"]))[0]
        actual=row.get("selected_proposal_id")
        changed += int(actual != unbonused)
        total += 1
    lesion=report.get("recurrent_lesion")
    # A missing real causal intervention remains UNRESOLVED, not a pass.
    if not isinstance(lesion,dict) or lesion.get("seeds",0)<20:
        raise ValueError("20 genuine CausalAuditHarness paired recurrence lesions required")
    if not lesion.get("executed_with_causal_audit_harness"):
        raise ValueError("CausalAuditHarness evidence not supplied")
    return {"selections":total,"bonus_removed_choice_flips":changed,
            "recurrent_lesion":lesion}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--report",type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args(argv)
    from doctor_lives.semantic_intentions import semantic_category
    result=evaluate(lambda text:semantic_category(text))
    result["pass_paraphrases"]=(result["invariance"]>=MIN_INVARIANCE
                              and result["category_accuracy"]>=MIN_CATEGORY_ACCURACY)
    if args.report:
        result["selection_audit"]=verify_report(json.loads(args.report.read_text()))
    elif args.out:
        result["selection_audit"]="UNRESOLVED: no measured neural/novelty or recurrent lesion"
    if args.out:
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="details"},sort_keys=True))
    return 0 if result["pass_paraphrases"] else 1

if __name__=="__main__":
    raise SystemExit(main())
