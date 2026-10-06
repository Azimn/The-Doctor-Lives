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
    # Neural-convergence controls. Defaults preserve the accepted v0.4 dynamics.
    "plasticity_rule": "hebbian",
    "neuromodulation_enabled": False,
    "synaptic_tagging_enabled": False,
    "provisional_update_fraction": 0.0,
    "tag_decay": 0.90,
    "capture_scale": 1.0,
    "spectral_homeostasis_mode": "off",
    "target_spectral_radius": 0.88,
    "min_spectral_radius": 0.74,
    "max_spectral_radius": 0.95,
    "spectral_check_interval": 64,
    "endogenous_noise": 0.0,
    "noise_persistence": 0.92,
    "intrinsic_excitability_homeostasis": False,
    "target_state_saturation": 0.18,
    "excitability_homeostasis_rate": 0.015,
    "min_state_gain": 0.20,
    "max_state_gain": 1.20,
}

# Versioned candidate profile transplanted from mechanisms already validated in
# Persona-and-Jelly-Sandwich. It is opt-in so accepted v0.4 checkpoints and
# causal results remain reproducible until this migration is independently gated.
NEURAL_CONVERGENCE_CONFIG = dict(DEFAULT_CONFIG)
NEURAL_CONVERGENCE_CONFIG.update({
    "plasticity_rule": "oja",
    "neuromodulation_enabled": True,
    "synaptic_tagging_enabled": True,
    "provisional_update_fraction": 0.08,
    "tag_decay": 0.90,
    "spectral_homeostasis_mode": "banded",
    "target_spectral_radius": 0.88,
    "min_spectral_radius": 0.74,
    "max_spectral_radius": 0.95,
    "spectral_check_interval": 32,
    "endogenous_noise": 0.008,
    "noise_persistence": 0.92,
    "intrinsic_excitability_homeostasis": True,
})



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
        self.cfg = dict(DEFAULT_CONFIG)
        if cfg is not None:
            self.cfg.update(cfg)
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
        self.state_gain = 1.0
        self.noise_state = np.zeros(self.n, dtype=np.float32)
        self.synaptic_tags = np.zeros_like(self.W.data, dtype=np.float32)
        self.homeostasis_events = 0
        self.last_recurrent_gain: float | None = None
        self.last_diagnostics: dict[str, float | int | str | bool | None] = {}
        if str(self.cfg.get("spectral_homeostasis_mode", "off")).lower() != "off":
            self._renormalize_recurrent(force=True)

    @staticmethod
    def _clip_unit(value: float) -> float:
        return float(np.clip(float(value), 0.0, 1.0))

    def _plasticity_gate(
        self,
        scalars: dict[str, float] | None,
        confidence: float,
    ) -> float:
        """Return a bounded global learning gate without adding persona traits.

        This is a mechanism transplant from the Gelatinblob/Jelly experiments.
        The gate changes how strongly the existing local rule writes; it does
        not choose an action or introduce character-specific latent variables.
        """
        if not bool(self.cfg.get("neuromodulation_enabled", False)):
            return 1.0
        values = scalars or {}
        novelty = self._clip_unit(max(float(values.get("novelty", 0.0)), 0.0))
        valence = self._clip_unit(abs(float(values.get("valence", 0.0))))
        threat = self._clip_unit(max(float(values.get("threat", 0.0)), 0.0))
        arousal = self._clip_unit(abs(float(values.get("arousal", 0.0))))
        stress = self._clip_unit(0.65 * threat + 0.35 * arousal)
        confidence = self._clip_unit(confidence)
        z = -1.15 + 2.0 * novelty + 1.15 * valence + 0.9 * stress + 0.7 * confidence
        return float(1.0 / (1.0 + np.exp(-z)))

    def _enforce_sign_and_bounds(self) -> None:
        exc = self.excitatory[self.pre_idx]
        limit = float(self.cfg["max_abs_weight"])
        self.W.data[exc] = np.clip(self.W.data[exc], 0.0, limit)
        self.W.data[~exc] = np.clip(self.W.data[~exc], -limit, 0.0)

    def _estimate_recurrent_gain(self) -> float:
        """Estimate dominant recurrent gain for sparse homeostasis.

        ARPACK receives a deterministic start vector. A deterministic power
        fallback is used if eigensolving fails. Diagnostics call this a gain
        estimate rather than claiming biological criticality.
        """
        if self.W.nnz == 0 or self.n == 0:
            return 0.0
        start = np.full(self.n, 1.0 / np.sqrt(max(self.n, 1)), dtype=np.float64)
        try:
            if self.n > 2:
                eig = sparse.linalg.eigs(
                    self.W.astype(np.float64),
                    k=1,
                    which="LM",
                    v0=start,
                    return_eigenvectors=False,
                    tol=1e-4,
                    maxiter=max(500, self.n * 2),
                )
                value = float(abs(eig[0]))
                if np.isfinite(value):
                    return value
        except Exception:
            pass
        vector = start
        gain = 0.0
        for _ in range(16):
            projected = self.W.dot(vector)
            gain = float(np.linalg.norm(projected))
            if gain <= 1e-12:
                return 0.0
            vector = projected / gain
        return gain

    def _renormalize_recurrent(self, *, force: bool = False) -> float | None:
        mode = str(self.cfg.get("spectral_homeostasis_mode", "off")).lower()
        if mode == "off":
            return self.last_recurrent_gain
        interval = max(1, int(self.cfg.get("spectral_check_interval", 64)))
        if not force and self.tick % interval != 0:
            return self.last_recurrent_gain
        gain = self._estimate_recurrent_gain()
        if gain <= 1e-12:
            self.last_recurrent_gain = gain
            return gain
        target = float(self.cfg.get("target_spectral_radius", 0.88))
        lower = float(self.cfg.get("min_spectral_radius", 0.74))
        upper = float(self.cfg.get("max_spectral_radius", 0.95))
        should_scale = mode == "hard" or gain < lower or gain > upper
        if should_scale:
            self.W.data *= np.float32(target / gain)
            self._enforce_sign_and_bounds()
            self.homeostasis_events += 1
            gain = self._estimate_recurrent_gain()
        self.last_recurrent_gain = float(gain)
        return self.last_recurrent_gain

    def capture_outcome(self, reward: float, confidence: float = 1.0) -> dict[str, float | bool | None]:
        """Resolve delayed provisional synaptic tags after an observed outcome.

        Nothing is captured in legacy mode. In convergence mode, recently
        eligible local changes are consolidated or opposed by signed outcome
        evidence, while the E/I sign contract and recurrent-gain bounds remain
        enforced.
        """
        if not bool(self.cfg.get("synaptic_tagging_enabled", False)):
            return {
                "captured": False,
                "capture_gate": 0.0,
                "tag_norm": float(np.linalg.norm(self.synaptic_tags)),
                "recurrent_gain": self.last_recurrent_gain,
            }
        signed_reward = float(np.clip(reward, -1.0, 1.0))
        confidence = self._clip_unit(confidence)
        capture_gate = confidence * (0.25 + 0.75 * abs(signed_reward))
        if abs(signed_reward) > 1e-12 and capture_gate > 0.0:
            scale = float(self.cfg.get("capture_scale", 1.0))
            self.W.data += np.float32(scale * signed_reward * capture_gate) * self.synaptic_tags
            self.synaptic_tags *= np.float32(1.0 - capture_gate)
            self._enforce_sign_and_bounds()
            self._renormalize_recurrent(force=True)
        report = {
            "captured": bool(abs(signed_reward) > 1e-12 and capture_gate > 0.0),
            "capture_gate": float(capture_gate),
            "tag_norm": float(np.linalg.norm(self.synaptic_tags)),
            "recurrent_gain": self.last_recurrent_gain,
        }
        self.last_diagnostics.update({
            "last_outcome_capture_gate": float(capture_gate),
            "last_outcome_signed_reward": signed_reward,
        })
        return report

    def diagnostics(self) -> dict[str, float | int | str | bool | None]:
        return {
            "profile": "neural_convergence_v05"
            if bool(self.cfg.get("neuromodulation_enabled", False))
            or bool(self.cfg.get("synaptic_tagging_enabled", False))
            or str(self.cfg.get("spectral_homeostasis_mode", "off")).lower() != "off"
            else "legacy_v04",
            "plasticity_rule": str(self.cfg.get("plasticity_rule", "hebbian")),
            "neuromodulation_enabled": bool(self.cfg.get("neuromodulation_enabled", False)),
            "synaptic_tagging_enabled": bool(self.cfg.get("synaptic_tagging_enabled", False)),
            "spectral_homeostasis_mode": str(self.cfg.get("spectral_homeostasis_mode", "off")),
            "endogenous_noise": float(self.cfg.get("endogenous_noise", 0.0)),
            "state_gain": float(self.state_gain),
            "noise_norm": float(np.linalg.norm(self.noise_state)),
            "synaptic_tag_norm": float(np.linalg.norm(self.synaptic_tags)),
            "recurrent_gain": self.last_recurrent_gain,
            "homeostasis_events": int(self.homeostasis_events),
            **self.last_diagnostics,
        }

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

    def step(
        self,
        text: str,
        scalars: dict[str, float] | None = None,
        reward: float = 0.0,
        learn: bool = True,
        confidence: float = 1.0,
    ) -> dict[str, float]:
        values = scalars or {}
        x = self.encoder.encode(text, values)
        syn = self.W.dot(self.rate)
        ext = self.Win.dot(x)

        noise_scale = float(self.cfg.get("endogenous_noise", 0.0))
        if noise_scale > 0.0:
            persistence = float(np.clip(self.cfg.get("noise_persistence", 0.92), 0.0, 0.999999))
            innovation = self.rng.normal(0.0, 1.0, self.n).astype(np.float32)
            self.noise_state = (
                persistence * self.noise_state
                + np.sqrt(max(0.0, 1.0 - persistence * persistence)) * innovation
            ).astype(np.float32)
        else:
            self.noise_state.fill(0.0)

        excess = max(float(self.rate.mean()) - self.target_rate, 0.0)
        global_term = float(self.cfg["global_inhibition"]) * excess
        gain = self.state_gain if bool(self.cfg.get("intrinsic_excitability_homeostasis", False)) else 1.0
        drive = gain * (syn + ext) + noise_scale * self.noise_state
        self.v += (float(self.cfg["dt"]) / float(self.cfg["tau"])) * (
            -self.v + drive + self.bias - global_term
        )
        self.rate = self._sigmoid(self.v)
        self.tick += 1

        saturation = float(np.mean((self.rate < 0.01) | (self.rate > 0.99)))
        if bool(self.cfg.get("intrinsic_excitability_homeostasis", False)):
            target_saturation = float(self.cfg.get("target_state_saturation", 0.18))
            homeo_rate = float(self.cfg.get("excitability_homeostasis_rate", 0.015))
            self.state_gain = float(np.clip(
                self.state_gain * np.exp(homeo_rate * (target_saturation - saturation)),
                float(self.cfg.get("min_state_gain", 0.20)),
                float(self.cfg.get("max_state_gain", 1.20)),
            ))

        plastic_gate = self._plasticity_gate(values, confidence)
        interval = int(self.cfg["plasticity_interval"])
        if learn and self.tick % interval == 0:
            pre = self.rate[self.pre_idx] - self.target_rate
            post = self.rate[self.post_idx] - self.target_rate
            corr = pre * post

            self.eligibility *= float(self.cfg["eligibility_decay"])
            self.eligibility += corr.astype(np.float32)

            rule = str(self.cfg.get("plasticity_rule", "hebbian")).lower()
            if rule == "oja":
                local_signal = corr - (post * post) * self.W.data
            elif rule == "hebbian":
                local_signal = corr
            else:
                raise ValueError(f"unknown plasticity_rule {rule!r}")

            local_update = (
                float(self.cfg["hebb_lr"]) * plastic_gate * local_signal
            ).astype(np.float32)
            reward_update = (
                float(self.cfg["reward_lr"]) * float(reward) * self.eligibility
            ).astype(np.float32)

            if bool(self.cfg.get("synaptic_tagging_enabled", False)):
                self.synaptic_tags *= float(self.cfg.get("tag_decay", 0.90))
                self.synaptic_tags += local_update
                provisional_fraction = float(np.clip(
                    self.cfg.get("provisional_update_fraction", 0.08), 0.0, 1.0
                ))
                local_applied = provisional_fraction * local_update
            else:
                local_applied = local_update

            delta = (
                local_applied
                + reward_update
                - float(self.cfg["weight_decay"]) * self.W.data
            )
            self.W.data += delta.astype(np.float32)
            self._enforce_sign_and_bounds()
            self.bias += float(self.cfg["homeostatic_lr"]) * (self.target_rate - self.rate)
            self._renormalize_recurrent()

        self.last_diagnostics = {
            "plastic_gate": float(plastic_gate),
            "state_saturation": saturation,
            "state_gain": float(self.state_gain),
            "synaptic_tag_norm": float(np.linalg.norm(self.synaptic_tags)),
            "recurrent_gain": self.last_recurrent_gain,
            "homeostasis_events": int(self.homeostasis_events),
        }
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
            path,
            v=self.v,
            rate=self.rate,
            bias=self.bias,
            w_data=self.W.data,
            w_indices=self.W.indices,
            w_indptr=self.W.indptr,
            excitatory=self.excitatory,
            eligibility=self.eligibility,
            synaptic_tags=self.synaptic_tags,
            noise_state=self.noise_state,
            state_gain=np.asarray([self.state_gain], dtype=np.float64),
            homeostasis_events=np.asarray([self.homeostasis_events], dtype=np.int64),
            last_recurrent_gain=np.asarray([
                np.nan if self.last_recurrent_gain is None else self.last_recurrent_gain
            ], dtype=np.float64),
            motor_w=self.motor_w,
            motor_b=self.motor_b,
            cfg_json=np.asarray(json.dumps(self.cfg)),
            rng_state_json=np.asarray(json.dumps(self.rng.bit_generator.state)),
            tick=np.asarray([self.tick], dtype=np.int64),
        )

    @classmethod
    def load(cls, path: str | Path) -> "PretoriusRecurrentSubstrate":
        payload = np.load(Path(path), allow_pickle=False)
        cfg = json.loads(str(payload["cfg_json"].item()))
        net = cls(cfg)
        net.v = payload["v"].astype(np.float32, copy=True)
        net.rate = payload["rate"].astype(np.float32, copy=True)
        net.bias = payload["bias"].astype(np.float32, copy=True)
        net.W = sparse.csr_matrix(
            (payload["w_data"], payload["w_indices"], payload["w_indptr"]),
            shape=(net.n, net.n),
            dtype=np.float32,
        )
        net.post_idx = np.repeat(np.arange(net.n, dtype=np.int32), np.diff(net.W.indptr))
        net.pre_idx = net.W.indices.astype(np.int32, copy=False)
        net.excitatory = payload["excitatory"].astype(bool, copy=True)
        net.eligibility = payload["eligibility"].astype(np.float32, copy=True)
        net.synaptic_tags = (
            payload["synaptic_tags"].astype(np.float32, copy=True)
            if "synaptic_tags" in payload.files
            else np.zeros_like(net.W.data, dtype=np.float32)
        )
        net.noise_state = (
            payload["noise_state"].astype(np.float32, copy=True)
            if "noise_state" in payload.files
            else np.zeros(net.n, dtype=np.float32)
        )
        net.state_gain = (
            float(payload["state_gain"][0]) if "state_gain" in payload.files else 1.0
        )
        net.homeostasis_events = (
            int(payload["homeostasis_events"][0])
            if "homeostasis_events" in payload.files
            else 0
        )
        if "last_recurrent_gain" in payload.files:
            saved_gain = float(payload["last_recurrent_gain"][0])
            net.last_recurrent_gain = None if np.isnan(saved_gain) else saved_gain
        else:
            net.last_recurrent_gain = None
        net.motor_w = payload["motor_w"].astype(np.float32, copy=True)
        net.motor_b = payload["motor_b"].astype(np.float32, copy=True)
        if "rng_state_json" in payload.files:
            net.rng.bit_generator.state = json.loads(str(payload["rng_state_json"].item()))
        net.tick = int(payload["tick"][0])
        net.last_diagnostics = {}
        return net

