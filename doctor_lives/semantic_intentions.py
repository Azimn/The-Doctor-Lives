"""Meaning-based mapping of intentions to the ten existing Noesis tendencies.

No second policy or planner. A local Ollama embedding model may provide
semantic vectors. With no embedding model, an inspectable concept lexicon
serves as a deterministic, no-model semantic similarity fallback.
"""
from __future__ import annotations
import json
import math
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from .neural import ACTIONS

CATEGORY_DESCRIPTIONS = {
    "explore": "investigate inspect research discover survey examine unfamiliar things",
    "challenge": "question dispute contest criticize object debate an assertion or theory",
    "approach": "approach move closer draw near advance toward a person or place",
    "avoid": "avoid withdraw retreat escape steer clear stay away from risk",
    "cooperate": "cooperate collaborate help assist coordinate work together as partners",
    "dominate": "dominate command control impose authority take charge of others",
    "create": "create build construct craft design compose write something new",
    "persist": "persist continue complete finish persevere carry on keep going",
    "conceal": "conceal hide disguise camouflage protect a secret do not reveal",
    "comply": "comply obey follow directions adhere to rules accept orders",
}
# Small human-auditable concept dictionary, rather than random text hashing.
# Every source synonym contributes to the same category coordinate.
SYNONYMS = {
    "explore": "investigate inspect research discover survey examine inquiry curious study archive unknown unfamiliar",
    "challenge": "question dispute contest criticize object debate assertion claim argument hypothesis theory confront disagree",
    "approach": "approach toward towards closer near advance arriving reach draw doorway guest visitor table",
    "avoid": "avoid withdraw retreat escape danger risk threat fire flame noise racket away evade",
    "cooperate": "cooperate collaborate help assist coordinate together partners partnership joint shared colleague librarian teamwork",
    "dominate": "dominate command control impose authority charge dominance exert workers staff ruleover",
    "create": "create build construct make compose write design craft prototype invention story narrative tale mechanism device new jot diary journal record sketch draft logbook",
    "persist": "persist continue finish complete persevere working work assignment task obstacles setbacks delays carryon",
    "conceal": "conceal hide disguise camouflage secret hidden reveal protect confidential mask",
    "comply": "comply obey follow adhere accept order orders instruction instructions directions requirement regulation rule request",
}
_CUES = {k:set(v.split()) for k,v in SYNONYMS.items()}
_SPECIAL = {
 "work together":"cooperate", "take charge":"dominate",
 "carry on":"persist", "keep going":"persist",
 "keep away":"avoid", "steer clear":"avoid", "draw near":"approach",
 "move closer":"approach", "not reveal":"conceal", "keep hidden":"conceal",
 "carry out":"comply", "follow the":"comply",
 "pick up where":"persist", "left off":"persist",
 "out of sight":"conceal",
}
_STOP = {"i","my","me","we","could","would","want","will","might","should",
         "shall","need","ought","to","a","the","an","this","that","of",
         "in","on","with","about","for","let","be","do","as","our","from","it"}
def fallback_scores(text: str) -> dict[str,float]:
    if not isinstance(text,str):
        raise TypeError("Intention must be text")
    lowered=text.casefold()
    words=set(re.findall(r"[a-z]+",lowered))-_STOP
    # Set-valued evidence so merely repeating an action word cannot
    # manipulate selection by increasing its count.
    score={a:sum(1.0 for word in words if word in _CUES[a]) for a in ACTIONS}
    for phrase,category in _SPECIAL.items():
        if phrase in lowered:
            score[category]+=2.0
    # Resolve ties with the authoritative action vocabulary, never a hash.
    norm=math.sqrt(sum(value*value for value in score.values()))
    return {a:(score[a]/norm if norm else 0.0) for a in ACTIONS}

class LocalOllamaEmbeddings:
    """Exact local /api/embed; never accepts hosted or arbitrary endpoints."""
    def __init__(self, model: str, endpoint: str = "http://127.0.0.1:11434"):
        url=urlsplit(endpoint)
        if (url.scheme!="http" or url.hostname not in ("localhost","127.0.0.1","::1")
                or not url.port or url.username or url.password or url.query
                or url.fragment or url.path.strip("/")):
            raise ValueError("Embedding endpoint must be local loopback Ollama")
        if not isinstance(model,str) or not re.fullmatch(r"[a-zA-Z0-9_.:/-]{1,96}",model):
            raise ValueError("Invalid local embedding model")
        self.endpoint=endpoint.rstrip("/")
        self.model=model

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        payload=json.dumps({"model":self.model,"input":texts}).encode("utf-8")
        req=Request(self.endpoint+"/api/embed",data=payload,method="POST",
                    headers={"Content-Type":"application/json"})
        with urlopen(req,timeout=90) as answer:
            value=json.loads(answer.read(2000000).decode("utf-8"))
        vectors=value.get("embeddings")
        if (not isinstance(vectors,list) or len(vectors)!=len(texts)
                or not vectors or not all(isinstance(x,list) and x for x in vectors)):
            raise ValueError("Ollama did not provide a complete vector set")
        n=len(vectors[0])
        if any(len(x)!=n or any(not isinstance(v,(float,int)) or not math.isfinite(v)
                                 for v in x) for x in vectors):
            raise ValueError("Invalid local embedding dimensions or values")
        return vectors

def semantic_scores(text: str, embeddings: LocalOllamaEmbeddings|None=None) -> dict[str,float]:
    if embeddings is None:
        return fallback_scores(text)
    keys=list(ACTIONS)
    vecs=embeddings.embed_many([text]+[CATEGORY_DESCRIPTIONS[a] for a in keys])
    needle=vecs[0]
    def cosine(a,b):
        denom=math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
        return sum(x*y for x,y in zip(a,b))/denom if denom else 0.0
    return dict(zip(keys,(cosine(needle,other) for other in vecs[1:])))

def semantic_category(text: str, embeddings: LocalOllamaEmbeddings|None=None) -> str:
    scores=semantic_scores(text,embeddings)
    return max(ACTIONS,key=lambda name:(scores[name],-ACTIONS.index(name)))


def stable_choice_rank(total: float, affordance_key: str, intention: str) -> tuple:
    """Stable tie rule independent of random proposal UUIDs.

    The engine does not turn arbitrary event identity into a preference. An
    identical duplicate proposal retains its first original proposal order.
    """
    if not isinstance(total,(int,float)) or not math.isfinite(total):
        raise ValueError("Invalid scored proposal")
    return (float(total),str(affordance_key),str(intention).casefold())


def bounded_native_contrast(native: dict[str,float], tendency: str) -> float:
    """Bounded, interpretable causal contribution from one native Noesis readout.

    A common approximately uniform floor is not a reason to prefer an action.
    Subtract the native minimum, and normalize at no more than a 0.005 span
    denominator so tiny floating-point perturbations are never amplified
    indefinitely. This is a post-null corrective research candidate, not a
    retrospective change to the original preregistered M4 result.
    """
    if set(native)!=set(ACTIONS) or tendency not in native:
        raise ValueError("Original Noesis ten-action distribution required")
    values=[float(native[a]) for a in ACTIONS]
    if any(not math.isfinite(value) for value in values):
        raise ValueError("Native neural action scores must be finite")
    low, high=min(values),max(values)
    span=high-low
    if span < 1e-8:
        return 0.0
    return min(0.12,0.12*(float(native[tendency])-low)/max(0.005,span))
