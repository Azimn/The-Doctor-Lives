"""Stage 02 source-aware routing: frozen authored probe scorecard.

Deterministic and intentionally NOT independent held-out evaluation. This
prints every error and never silently excludes ambiguous queries.
"""
from __future__ import annotations

from collections import Counter
import argparse
import json
from pathlib import Path
from .firsthand_router import classify_firsthand


def evaluate(data: dict) -> dict:
    if data.get("schema") != "pretorius.firsthand-router.predeclared.v01":
        raise ValueError("unrecognized frozen router fixture")
    items=data["items"]
    if len(items)!=40 or len({x["id"] for x in items})!=40:
        raise ValueError("expected 40 distinct author-declared inputs")
    counts=Counter((x["gold"],str(classify_firsthand(x["question"]))) for x in items)
    rows=[{"id":item["id"],"gold":item["gold"],
           "predicted":str(classify_firsthand(item["question"])),
           "correct":str(classify_firsthand(item["question"]))==item["gold"]}
          for item in items]
    positives=sum(x["gold"]=="firsthand_event" for x in items)
    negatives=sum(x["gold"]=="not_firsthand" for x in items)
    ambiguous=sum(x["gold"]=="ambiguous_requires_review" for x in items)
    tp=counts[("firsthand_event","firsthand_event")]
    fp= sum(v for (g,p),v in counts.items() if g!="firsthand_event" and p=="firsthand_event")
    fn=positives-tp
    tn=negatives-counts[("not_firsthand","firsthand_event")]
    return {
        "schema":"pretorius.firsthand-router.mechanical-evaluation.v01",
        "evaluation":"investigator_authored_in_sample_not_independent",
        "total":len(items),"positive":positives,"negative":negatives,
        "ambiguous":ambiguous,"true_positive":tp,"false_positive":fp,
        "false_negative":fn,"true_negative_nonfirsthand":tn,
        "precision":round(tp/max(1,tp+fp),6),
        "recall":round(tp/max(1,positives),6),
        "strict_accuracy":round(sum(x["correct"] for x in rows)/len(rows),6),
        "ambiguous_review_recall":round(
            counts[("ambiguous_requires_review","ambiguous_requires_review")]
            / max(1,ambiguous),6
        ),
        "confusion":[{"gold":g,"predicted":p,"count":n}
                     for (g,p),n in sorted(counts.items())],
        "items":rows,
        "notes":"Routing intent only. Does not verify world truth, LLM outputs or unanticipated spontaneous claims.",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fixture",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=evaluate(json.loads(args.fixture.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in (
        "total","true_positive","false_positive","false_negative",
        "precision","recall","strict_accuracy","ambiguous_review_recall",
    )},sort_keys=True))


if __name__=="__main__":
    main()
