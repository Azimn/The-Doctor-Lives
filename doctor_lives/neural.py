from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse

ACTIONS = [
    "explore", "challenge", "approach", "avoid", "cooperate",
    "dominate", "create", "persist", "conceal", "comply",
]
SCALAR_KEYS = [
    "valence", "arousal", "social", "authority", "autonomy", "novelty",
    "achievement", "isolation", "threat", "intimacy", "control", "creation",
]

DEFAULT_CONFIG = {
    "neurons": 4096,
    "sensory_dim": 512,
    "avg_recurrent_degree": 32,
    "input_degree": 10,
    "excitatory_fraction": 0.8,
    "target_rate": 0.08,
    "tau": 12.0,
    "dt": 1.0,
    "recurrent_scale": 0.34,
    "input_scale": 0.55,
    "action_teaching_scale": 1.8,
    "global_inhibition": 1.7,
    "plasticity_interval": 8,
    "hebb_lr": 0.00035,
    "reward_lr": 0.0012,
    "weight_decay": 2e-5,
    "homeostatic_lr": 8e-5,
    "eligibility_decay": 0.92,
    "max_abs_weight": 0.75,
    "action_population_size": 72,
    "seed": 1842,
    "motor_lr": 0.025,
    "motor_weight_decay": 2e-5,
    "motor_temperature": 0.3,
}


class ExperienceEncoder:
    def __init__(self, sensory_dim: int = 512):
        self.sensory_dim = int(sensory_dim)
        self.scalar_offset = self.sensory_dim
        self.action_offset = self.scalar_offset + len(SCALAR_KEYS)
        self.input_dim = self.action_offset + len(ACTIONS)

    @staticmethod
    def _tokens(text: str) -> list[str]:
        import re
        toks = re.findall(r"[a-z0-9']+", text.lower())
        return toks + [f"{a}::{b}" for a, b in zip(toks, toks[1:])]

    def encode(self, text: str, scalars: dict[str, float] | None = None,
               action: str | None = None) -> np.ndarray:
        x = np.zeros(self.input_dim, dtype=np.float32)
        tokens = self._tokens(text)
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "little", signed=False)
            idx = value % self.sensory_dim
            x[idx] += 1.0 if ((value >> 8) & 1) else -1.0
        norm = float(np.linalg.norm(x[:self.sensory_dim]))
        if norm > 1e-8:
            x[:self.sensory_dim] /= norm
        for i, key in enumerate(SCALAR_KEYS):
            x[self.scalar_offset+i] = float(np.clip((scalars or {}).get(key, 0.0), -1.0, 1.0))
        if action is not None:
            x[self.action_offset + ACTIONS.index(action)] = 1.0
        return x


class PretoriusRecurrentSubstrate:
    """Portable recurrent phenotype organ derived from Pretorius-Neural-Network.

    It has no named personality traits. It consumes generic environmental
    features and exposes tendencies over the donor's ten generic actions.
    """

    def __init__(self, cfg: dict[str, Any] | None = None):
        self.cfg = dict(DEFAULT_CONFIG if cfg is None else cfg)
        self.encoder = ExperienceEncoder(int(self.cfg["sensory_dim"]))
        self.n = int(self.cfg["neurons"])
        self.rng = np.random.default_rng(int(self.cfg.get("seed", 1842)))
        self.target_rate = float(self.cfg["target_rate"])
        self.tick = 0
        self.excitatory = self.rng.random(self.n) < float(self.cfg["excitatory_fraction"])
        self.W = self._make_recurrent()
        self.post_idx = np.repeat(np.arange(self.n, dtype=np.int32), np.diff(self.W.indptr))
        self.pre_idx = self.W.indices.astype(np.int32, copy=False)
        self.eligibility = np.zeros_like(self.W.data, dtype=np.float32)
        self.action_populations = self._make_action_populations()
        self.Win = self._make_input_matrix()
        self.motor_w = self.rng.normal(0.0, 0.01, size=(len(ACTIONS), self.n)).astype(np.float32)
        self.motor_b = np.zeros(len(ACTIONS), dtype=np.float32)
        self.v = np.zeros(self.n, dtype=np.float32)
        self.rate = np.full(self.n, self.target_rate, dtype=np.float32)
        self.bias = np.full(self.n, -2.45, dtype=np.float32)

    def _make_recurrent(self) -> sparse.csr_matrix:
        k = int(self.cfg["avg_recurrent_degree"])
        m = self.n * k
        post = np.repeat(np.arange(self.n, dtype=np.int32), k)
        pre = self.rng.integers(0, self.n, size=m, dtype=np.int32)
        same = pre == post
        while np.any(same):
            pre[same] = self.rng.integers(0, self.n, size=int(same.sum()), dtype=np.int32)
            same = pre == post
        scale = float(self.cfg["recurrent_scale"]) / np.sqrt(max(k, 1))
        mag = self.rng.lognormal(-1.0, 0.45, size=m).astype(np.float32) * scale
        sign = np.where(self.excitatory[pre], 1.0, -1.0).astype(np.float32)
        W = sparse.csr_matrix((mag*sign, (post, pre)), shape=(self.n, self.n), dtype=np.float32)
        W.sum_duplicates()
        return W

    def _make_action_populations(self) -> dict[str, np.ndarray]:
        size = min(
            int(self.cfg["action_population_size"]),
            max(8, self.n // (len(ACTIONS) * 2)),
        )
        available = np.arange(self.n, dtype=np.int32)
        self.rng.shuffle(available)
        populations = {}
        cursor = 0
        for action in ACTIONS:
            if cursor + size > len(available):
                available = np.arange(self.n, dtype=np.int32)
                self.rng.shuffle(available)
                cursor = 0
            populations[action] = np.sort(available[cursor:cursor + size])
            cursor += size
        return populations

    def _make_input_matrix(self) -> sparse.csr_matrix:
        k = int(self.cfg["input_degree"])
        m = self.n * k
        rows = np.repeat(np.arange(self.n, dtype=np.int32), k)
        cols = self.rng.integers(0, self.encoder.input_dim, size=m, dtype=np.int32)
        data = self.rng.normal(
            0.0, float(self.cfg["input_scale"]) / np.sqrt(max(k, 1)), size=m
        ).astype(np.float32)

        extra_rows = []
        extra_cols = []
        extra_data = []
        teaching = float(self.cfg["action_teaching_scale"])
        for index, action in enumerate(ACTIONS):
            column = self.encoder.action_offset + index
            population = self.action_populations[action]
            extra_rows.extend(population.tolist())
            extra_cols.extend([column] * len(population))
            extra_data.extend([teaching] * len(population))

        rows = np.concatenate([rows, np.asarray(extra_rows, dtype=np.int32)])
        cols = np.concatenate([cols, np.asarray(extra_cols, dtype=np.int32)])
        data = np.concatenate([data, np.asarray(extra_data, dtype=np.float32)])
        W = sparse.csr_matrix(
            (data, (rows, cols)), shape=(self.n, self.encoder.input_dim), dtype=np.float32
        )
        W.sum_duplicates()
        return W

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        z = np.clip(x, -10.0, 10.0)
        return (1.0 / (1.0 + np.exp(-z))).astype(np.float32, copy=False)

    def step(self, text: str, scalars: dict[str, float] | None = None,
             reward: float = 0.0, learn: bool = True) -> dict[str, float]:
        x = self.encoder.encode(text, scalars)
        syn = self.W.dot(self.rate)
        ext = self.Win.dot(x)
        excess = max(float(self.rate.mean()) - self.target_rate, 0.0)
        global_term = float(self.cfg["global_inhibition"]) * excess
        self.v += (float(self.cfg["dt"])/float(self.cfg["tau"])) * (-self.v + syn + ext + self.bias - global_term)
        self.rate = self._sigmoid(self.v)
        self.tick += 1
        interval = int(self.cfg["plasticity_interval"])
        if learn and self.tick % interval == 0:
            pre = self.rate[self.pre_idx] - self.target_rate
            post = self.rate[self.post_idx] - self.target_rate
            corr = pre * post
            self.eligibility *= float(self.cfg["eligibility_decay"])
            self.eligibility += corr.astype(np.float32)
            delta = (
                float(self.cfg["hebb_lr"])*corr
                + float(self.cfg["reward_lr"])*float(reward)*self.eligibility
                - float(self.cfg["weight_decay"])*self.W.data
            )
            self.W.data += delta.astype(np.float32)
            exc = self.excitatory[self.pre_idx]
            lim = float(self.cfg["max_abs_weight"])
            self.W.data[exc] = np.clip(self.W.data[exc], 0.0, lim)
            self.W.data[~exc] = np.clip(self.W.data[~exc], -lim, 0.0)
            self.bias += float(self.cfg["homeostatic_lr"]) * (self.target_rate-self.rate)
        return self.action_scores()

    def action_scores(self) -> dict[str, float]:
        f = (self.rate-self.target_rate).astype(np.float32, copy=True)
        norm = float(np.linalg.norm(f))
        if norm > 1e-8:
            f /= norm
        logits = (self.motor_w.dot(f)+self.motor_b).astype(np.float64)
        logits -= logits.max()
        temp = max(float(self.cfg["motor_temperature"]), 1e-4)
        p = np.exp(logits/temp)
        p /= p.sum()
        return {a: float(v) for a, v in zip(ACTIONS, p)}

    def reinforce_action(self, action: str, strength: float = 1.0) -> None:
        if action not in ACTIONS:
            return
        f = (self.rate-self.target_rate).astype(np.float32, copy=True)
        norm = float(np.linalg.norm(f))
        if norm > 1e-8:
            f /= norm
        probs = np.asarray(list(self.action_scores().values()), dtype=np.float32)
        target = np.zeros(len(ACTIONS), dtype=np.float32)
        target[ACTIONS.index(action)] = 1.0
        error = (target-probs) * float(np.clip(strength, -1.0, 1.0))
        self.motor_w *= 1.0-float(self.cfg["motor_weight_decay"])
        self.motor_w += float(self.cfg["motor_lr"]) * np.outer(error, f).astype(np.float32)
        self.motor_b += float(self.cfg["motor_lr"])*0.1*error

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path, v=self.v, rate=self.rate, bias=self.bias,
            w_data=self.W.data, w_indices=self.W.indices, w_indptr=self.W.indptr,
            excitatory=self.excitatory, eligibility=self.eligibility,
            motor_w=self.motor_w, motor_b=self.motor_b,
            cfg_json=np.asarray(json.dumps(self.cfg)), tick=np.asarray([self.tick], dtype=np.int64),
        )

    @classmethod
    def load(cls, path: str | Path) -> "PretoriusRecurrentSubstrate":
        payload = np.load(Path(path), allow_pickle=False)
        cfg = json.loads(str(payload["cfg_json"].item()))
        net = cls(cfg)
        net.v = payload["v"].astype(np.float32, copy=True)
        net.rate = payload["rate"].astype(np.float32, copy=True)
        net.bias = payload["bias"].astype(np.float32, copy=True)
        net.W = sparse.csr_matrix((payload["w_data"], payload["w_indices"], payload["w_indptr"]), shape=(net.n,net.n), dtype=np.float32)
        net.post_idx = np.repeat(np.arange(net.n, dtype=np.int32), np.diff(net.W.indptr))
        net.pre_idx = net.W.indices.astype(np.int32, copy=False)
        net.excitatory = payload["excitatory"].astype(bool, copy=True)
        net.eligibility = payload["eligibility"].astype(np.float32, copy=True)
        net.motor_w = payload["motor_w"].astype(np.float32, copy=True)
        net.motor_b = payload["motor_b"].astype(np.float32, copy=True)
        net.tick = int(payload["tick"][0])
        return net
