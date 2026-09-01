from __future__ import annotations

from dataclasses import dataclass
from .models import VCTSBreakdown


@dataclass(frozen=True)
class TrustInputs:
    detection: float
    image_quality: float
    temporal_consistency: float
    stress_robustness: float
    geometry_consistency: float


WEIGHTS = {
    "detection": 0.25,
    "image_quality": 0.20,
    "temporal_consistency": 0.20,
    "stress_robustness": 0.20,
    "geometry_consistency": 0.15,
}


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def calculate_vcts(inputs: TrustInputs) -> VCTSBreakdown:
    vals = {k: _clamp01(getattr(inputs, k)) for k in WEIGHTS}
    score = 100.0 * sum(vals[k] * WEIGHTS[k] for k in WEIGHTS)
    return VCTSBreakdown(**vals, score=round(score, 2))


def decide_action(score: float, evidence_in_zone: bool) -> str:
    if not evidence_in_zone:
        return "IGNORE"
    if score >= 85:
        return "ACT"
    if score >= 65:
        return "VERIFY"
    if score >= 40:
        return "RE_OBSERVE"
    return "HUMAN_REVIEW"
