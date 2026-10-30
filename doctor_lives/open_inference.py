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
from .local_ollama_transport import post_local_ollama

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
        self.hostname=url.hostname
        self.port=url.port

    def propose(self, context: dict[str,Any]) -> list[str]:
        content=(
            "You are creating hypothetical possible intentions, NOT choosing "
            "physical actions. Return exactly five DIFFERENT, short, first-person "
            "ideas as one valid JSON object with key 'intentions' containing "
            "five strings. At least one idea must be an unfulfilled wish. "
            "Use first-person memories and needs only as tentative context. "
            "Available ability descriptions are opportunities, not commands. "
            "Nothing you write can be executed directly.\n"
            +json.dumps(context,sort_keys=True,ensure_ascii=False)
        )
        # Local Ollama supports JSON schema. A small local model can truncate
        # a short response or choose a different wrapper key; bounded retries
        # must still fail closed if the output is not genuinely model authored.
        expected={"type":"object","properties":{"intentions":{
            "type":"array","minItems":3,"maxItems":8,
            "items":{"type":"string"}}},"required":["intentions"]}
        for attempt in range(3):
            payload=json.dumps({"model":self.model,
                "prompt":content + ("\nReturn ONLY the required JSON object." if attempt else ""),
                "stream":False,"format":expected,
                "options":{"temperature":0.0,"num_predict":768}}).encode()
            raw=json.loads(post_local_ollama(
                self.hostname,self.port,"/api/generate",payload,
                timeout=90,max_response_bytes=128000).decode("utf-8"))
            try:
                parsed=json.loads(raw["response"])
                if isinstance(parsed,dict):
                    parsed=parsed.get("intentions",parsed.get("proposals",
                                  parsed.get("goals")))
                if (isinstance(parsed,list) and 3<=len(parsed)<=8
                    and all(type(p) is str and p.strip() and len(p)<=400
                            for p in parsed)):
                    return parsed
            except (KeyError,ValueError,TypeError):
                pass
        raise ValueError("Local Ollama failed three bounded genuine-proposal JSON attempts")

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
