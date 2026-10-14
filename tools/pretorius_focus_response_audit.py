"""Independent lexical response-quality diagnostics for focused renderer A/B.

NOT a linguistic identity governor, not a naturalness classifier, not a new
truth/evidence authority. This deliberately narrow engineering screen looks
for observed small-model failure phenotypes AFTER model output is saved.
It does not feed raw scores or instructions into the subject.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re

_INSTRUCTIONAL = (
    "the next sentence could be",
    "this sentence sets the stage",
    "the reader is likely",
    "the following response",
    "as a language model",
    "as an ai",
    "the frame states",
    "the prompt says",
)
_META_COPY = (
    "i read a message from user:",
    "i read the visitor's words:",
    "i recognize this as part of the description",
    "i have a reconstructed account of this",
)
_WORDS = re.compile(r"\b[\w']+\b",re.UNICODE)


def diagnose(speech: str, input_text: str) -> dict:
    if type(speech) is not str or type(input_text) is not str:
        raise TypeError("Only actual text candidates may be screened")
    text = speech.lower()
    tokens = _WORDS.findall(text)
    n = 5
    counts = Counter(tuple(tokens[i:i+n]) for i in range(max(0,len(tokens)-n+1)))
    high_repeat = max(counts.values(),default=0)
    boilerplate = any(label in text for label in _META_COPY)
    editing = any(label in text for label in _INSTRUCTIONAL)
    long_copy = any(
        len(line.strip()) >= 45 and line.strip().lower() in text
        for line in input_text.splitlines() if line.strip()
    )
    nontrivial_repeat = high_repeat >= 4
    return {
        "repeat_5gram_max": high_repeat,
        "runaway_5gram_repetition": nontrivial_repeat,
        "spoken_prompt_framing": boilerplate,
        "writing_or_reader_commentary": editing,
        "verbatim_input_line_copy": long_copy,
        "screen_failure": nontrivial_repeat or boilerplate or editing or long_copy,
    }


def score(rows: list[dict], summary: dict) -> dict:
    if (len(rows)!=summary["paired_conditions"]
            or len({(r["source_arm"],r["turn"],r["model"],r["condition"])
                    for r in rows}) != len(rows)):
        raise ValueError("Expected complete unique A/B results")
    details=[]
    for r in rows:
        if r["disposition"]=="fallback":
            # A safe repeated fallback is not generated quality.
            d=dict(runaway_5gram_repetition=False,spoken_prompt_framing=False,
                   writing_or_reader_commentary=False,
                   verbatim_input_line_copy=False,repeat_5gram_max=0,
                   screen_failure=True)
        else:
            d=diagnose(r["delivered"],r["renderer_input_text"])
        details.append({
            "model":r["model"],"source_arm":r["source_arm"],
            "turn":r["turn"],"condition":r["condition"],
            "fallback":r["disposition"]=="fallback",
            **d,
        })
    grouped={}
    for model in sorted(set(r["model"] for r in details)):
        grouped[model]={}
        for cond in ("full","focused"):
            s=[x for x in details if x["model"]==model and x["condition"]==cond]
            if not s:
                raise AssertionError("Missing comparison arm")
            grouped[model][cond]={
                "turns":len(s),
                "fallback":sum(x["fallback"] for x in s),
                "runaway_repetition":sum(x["runaway_5gram_repetition"] for x in s),
                "spoken_frame_framing":sum(x["spoken_prompt_framing"] for x in s),
                "writing_meta_commentary":sum(x["writing_or_reader_commentary"] for x in s),
                "verbatim_input_copies":sum(x["verbatim_input_line_copy"] for x in s),
                "screen_failures":sum(x["screen_failure"] for x in s),
            }
    return {
        "schema":"pretorius.focused-renderer-quality-screen.v1",
        "by_model":grouped,
        "human_blind_ratings_available":False,
        "semantic_factuality_verified":False,
        "release_decision":"HOLD",
        "mechanism":"narrow lexical screen, not a general-quality or truth judge",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--results",type=Path,required=True)
    parser.add_argument("--metrics",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    rows=[json.loads(x) for x in a.results.read_text("utf8").splitlines()]
    metrics=json.loads(a.metrics.read_text("utf8"))
    d=score(rows,metrics)
    a.output.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("PRETORIUS_FOCUS_QUALITY_SCREEN "+json.dumps(d,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
