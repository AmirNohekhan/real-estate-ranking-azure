from __future__ import annotations

import hashlib
import math

import numpy as np


def assign_variant(user_id: str, experiment_id: str = "ranking_v1") -> str:
    bucket = int(hashlib.sha256(f"{experiment_id}:{user_id}".encode()).hexdigest()[:8], 16) % 100
    return "challenger" if bucket >= 50 else "control"


def analyze_binary(control: np.ndarray, treatment: np.ndarray) -> dict[str, float]:
    pc, pt = float(control.mean()), float(treatment.mean())
    se = math.sqrt(pc * (1 - pc) / len(control) + pt * (1 - pt) / len(treatment))
    effect = pt - pc
    return {"control_rate": pc, "treatment_rate": pt, "absolute_effect": effect,
            "ci_low": effect - 1.96 * se, "ci_high": effect + 1.96 * se}


def sample_ratio_mismatch(n_control: int, n_treatment: int) -> bool:
    total = n_control + n_treatment
    if not total:
        return False
    chi2 = ((n_control - total / 2) ** 2 + (n_treatment - total / 2) ** 2) / (total / 2)
    return chi2 > 10.828  # p < .001, 1 degree of freedom

