"""Optional server-side scoring endpoint.

Clients (including the Android app) compute features on-device and call this
endpoint to get the canonical risk score. Raw audio never leaves the device.
"""
from __future__ import annotations

from fastapi import APIRouter

from ..schemas import AnalyzeFeaturesIn
from ..services.scorer import score_features

router = APIRouter(prefix="/v1/analyze")


@router.post("/features")
def analyze_features(body: AnalyzeFeaturesIn) -> dict:
    score = score_features(
        body.jitter_pct,
        body.shimmer_pct,
        body.smoothness,
        body.spectral_flatness,
        body.hf_rolloff,
        body.hnr_db,
        body.voiced_fraction,
    )
    return {
        "risk_score": score,
        "verdict": _verdict(score),
        "language": body.language,
    }


def _verdict(score: float) -> str:
    if score >= 0.65:
        return "high"
    if score >= 0.4:
        return "inconclusive"
    return "low"
