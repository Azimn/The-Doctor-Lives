"""One strictly local, provider-neutral intention-text inference port.

Text from any model is an UNTRUSTED proposal, never a physical command, a
fact, a reward or a policy decision. No API keys, hosted inference or network
except the checked local loopback Ollama process.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from hashlib import sha256
import json
import random
from typing import Any
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

class InferencePort(ABC):
    @abstractmethod
    def propose(self, context: dict[str, Any]) -> list[str]:
        """Return *text only*. No action, tool or world authority."""

class LocalOllama(InferencePort):
    def __init__(self, model: str, endpoint: str = "http://127.0.0.1:11434"):
        url=urlsplit(endpoint)
        if (url.scheme!="http" or url.hostname not in ("localhost","127.0.0.1","::1")
                or url.username or url.password or url.query or url.fragment
                or url.path.strip("/") or not url.port):
            raise ValueError("Only an explicit local loopback Ollama API is allowed")
        if not isinstance(model,str) or not 1<=len(model)<=96:
            raise ValueError("Local Ollama model must be named")
        self.model=model
        self.endpoint=endpoint.rstrip("/")

    def propose(self, context: dict[str,Any]) -> list[str]:
        content=(
            "Generate 3 to 8 different possible FIRST-PERSON intentions for a "
            "persistent artificial laboratory subject. Reply ONLY with a JSON "
            "array of strings. Every item must be an idea, not a fact or a "
            "command. Include at least one wish outside current abilities. "
            "Use current observations, needs and memories as context. "
            "Available affordances are descriptions, NEVER commands to execute.\n"
            +json.dumps(context,sort_keys=True,ensure_ascii=False)
        )
        payload=json.dumps({"model":self.model,"prompt":content,"stream":False,
                             "format":"json","options":{"temperature":0.0,
                             "num_predict":384}}).encode()
        req=Request(self.endpoint+"/api/generate",data=payload,
                    headers={"Content-Type":"application/json"},method="POST")
        with urlopen(req,timeout=45) as answer:
            raw=json.loads(answer.read(128000).decode("utf-8"))
        try:
            parsed=json.loads(raw["response"])
            if isinstance(parsed,dict):
                parsed=parsed.get("intentions",parsed.get("proposals"))
            if not isinstance(parsed,list) or not 3<=len(parsed)<=8:
                raise ValueError("Local model must propose 3 to 8 intentions")
            if any(type(p) is not str or not p.strip() or len(p)>400 for p in parsed):
                raise ValueError("Model proposal shape invalid")
            return parsed
        except (KeyError,ValueError,TypeError) as exc:
            raise ValueError("Local model produced invalid, non-executable proposal JSON") from exc

class DeterministicFallback(InferencePort):
    """Model-off text proposer; memory-sensitive but never a second selector."""
    def propose(self, context: dict[str,Any]) -> list[str]:
        afforded=context.get("affordances",[])
        if not isinstance(afforded,list) or not afforded:
            # Keep wishes alive even when the world exposes zero abilities.
            return ["I might investigate the locked cabinets.",
                    "I would like to ask a visitor about their work.",
                    "I want to make a note about my situation."]
        ranked=[]
        seed_bytes=json.dumps(context,sort_keys=True,ensure_ascii=False).encode()
        seed=int.from_bytes(bytes.fromhex(sha256(seed_bytes).hexdigest())[:8],"big")
        rng=random.Random(seed)
        for a in afforded:
            label=str(a.get("description","")).strip()
            if label:
                ranked.append("I might "+label.rstrip(".")+".")
        rng.shuffle(ranked)
        # Do not fabricate novel capabilities or facts. The extra ungrounded
        # line is a real desire, not an instruction to an executor.
        wish=["I wish I could visit the village beyond the laboratory.",
              "I wonder whether I might build a clockwork bird.",
              "I would like to hear a stranger tell me a story.",
              "I would like to investigate a doorway that is not here."][seed%4]
        out=ranked[:5]+[wish]
        if len(out)<3:
            out+=["I want to understand what I remember.",
                  "I would like to prepare for tomorrow."]
        return out[:8]

def make_inference(provider: str, *, model: str | None = None) -> InferencePort:
    if provider=="fallback":
        return DeterministicFallback()
    if provider=="ollama" and model:
        return LocalOllama(model)
    raise ValueError("Inference provider must be local Ollama or deterministic fallback")
