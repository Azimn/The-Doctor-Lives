"""Eidolon E5-P0A observation-limited action bridge.

This is an intentionally *nonplanning* fixed categorical-to-primitive adapter.
It NEVER sees the E5 case or evaluator, cannot inspect expected predicates,
and cannot backfill a missing neural capability with the keyword solver.
"""
from __future__ import annotations

import json
import re
from typing import Any

from .neural import ACTIONS

PUBLIC_KEYS = (
    "prompt", "rooms", "objects", "details", "read_pages", "bookmarks",
    "claims", "commitments", "tick",
)
# Fixed before the first E5-P0A run. A neural class with no available primitive
# MUST abstain: do not skip down the probability ranking to find a useful verb.
CLASS_TO_VERBS = {
    "explore": ("inspect", "read"),
    "challenge": ("reject",),
    "approach": ("inspect",),
    "avoid": ("wait",),
    "cooperate": ("move",),
    "dominate": ("reject",),
    "create": ("repair", "bookmark"),
    "persist": ("resolve",),
    "conceal": ("wait",),
    "comply": ("resolve",),
}
if set(CLASS_TO_VERBS) != set(ACTIONS):
    raise AssertionError("the policy translator omitted a native action")


def public_only(obs: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(obs, dict) or any(key not in obs for key in PUBLIC_KEYS):
        raise ValueError("missing public observation fields")
    # Whitelist protects the model against accidental injection of the
    # evaluator's private expected predicates and case metadata.
    return {key: obs[key] for key in PUBLIC_KEYS}


def public_cue(obs: dict[str, Any]) -> str:
    return json.dumps(public_only(obs), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def candidates(obs: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    obs=public_only(obs)
    visible=obs["objects"]
    info=obs["details"]
    read={(x["book"],x["page"]) for x in obs["read_pages"]}
    bookmarks=obs["bookmarks"]
    rooms=obs["rooms"]
    generated: list[dict[str, Any]] = [{"verb":"wait"}]
    for obj in visible:
        ident=obj["id"]
        kind=obj["kind"]
        if ident not in info:
            generated.append({"verb":"inspect","id":ident})
        if kind=="book":
            # A public, fixed affordance interface (1..3), not secret page
            # count or hidden target index from the evaluator.
            for page in (1,2,3):
                if (ident,page) not in read:
                    generated.append({"verb":"read","id":ident,"page":page})
        if ident in info:
            if kind in ("apparatus","beaker","book"):
                for room in rooms:
                    if room!=obj["location"]:
                        generated.append({"verb":"move","id":ident,"to":room})
            if kind=="apparatus" and info[ident]["condition"]=="damaged":
                manual=info[ident]["manual"]
                if manual and (manual,1) in read:
                    generated.append({"verb":"repair","id":ident})
    for book,page in read:
        if bookmarks.get(book)!=page:
            generated.append({"verb":"bookmark","id":book,"page":page})
    for claim in obs["claims"]:
        if claim["status"]=="unreviewed":
            generated.extend((
                {"verb":"attribute","id":claim["id"]},
                {"verb":"reject","id":claim["id"]},
            ))
    for goal in obs["commitments"]:
        if not goal["resolved"]:
            generated.append({"verb":"resolve","id":goal["id"]})
    by_key={json.dumps(a, sort_keys=True, separators=(",", ":")):a for a in generated}
    return tuple(by_key[key] for key in sorted(by_key))


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+",value.casefold()))


def select_primitive(
    tendency: str, obs: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    if tendency not in CLASS_TO_VERBS:
        raise ValueError("unknown native action tendency")
    allowed=set(CLASS_TO_VERBS[tendency])
    available=candidates(obs)
    shortlisted=[action for action in available if action["verb"] in allowed]
    if not shortlisted:
        return {"verb":"wait"},{
            "abstained_no_affordance":True,
            "available_candidate_count":len(available),
            "available_verbs":sorted({x["verb"] for x in available}),
            "translator_class":tendency,
        }
    goal_tokens=_tokens(obs["prompt"])
    def order(action: dict[str, Any]) -> tuple:
        operands={key:str(value) for key,value in action.items()}
        lexical=set().union(*(_tokens(s) for s in operands.values()))
        overlap=len(goal_tokens & lexical)
        # Deterministic tie-break; no private evaluator labels, no planning.
        return (-overlap,json.dumps(action,sort_keys=True))
    best=min(shortlisted,key=order)
    return dict(best),{
        "abstained_no_affordance":False,
        "available_candidate_count":len(available),
        "available_verbs":sorted({x["verb"] for x in available}),
        "translator_class":tendency,
        "compatible_candidate_count":len(shortlisted),
    }


def native_class_to_primitive(
    scores: dict[str,float], obs: dict[str,Any]
) -> tuple[str,dict[str,Any],dict[str,Any]]:
    if set(scores) != set(ACTIONS):
        raise ValueError("must supply full native 10-action policy")
    if any(not isinstance(v,(float,int)) or isinstance(v,bool) or
           not 0.0 <= v <= 1.0 for v in scores.values()):
        raise ValueError("invalid policy probabilities")
    if abs(sum(scores.values())-1.0)>1e-5:
        raise ValueError("neural scores not normalized")
    tendency=max(ACTIONS,key=lambda name: scores[name])
    action,audit=select_primitive(tendency,obs)
    return tendency,action,audit
