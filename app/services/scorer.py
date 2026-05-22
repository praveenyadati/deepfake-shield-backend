"""Weighted ensemble that converts forensic features to a 0..1 risk score.

This mirrors the Kotlin and JS implementations so all three platforms produce
identical scores given identical features.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureWeights:
    jitter: float = 0.28
    shimmer: float = 0.22
    smoothness: float = 0.22
    sf: float = 0.10
    hf: float = 0.08
    hnr: float = 0.10


W = FeatureWeights()


def _clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _jitter_sub(jitter_pct: float) -> float:
    """Human pitch jitter is ~0.5%-2.0%; TTS often <0.3% (too clean)."""
    if jitter_pct < 0.3:
        return 1.0
    if jitter_pct < 0.5:
        return 0.7
    if jitter_pct < 2.0:
        return 0.1
    return 0.4  # very noisy can also be suspicious


def _shimmer_sub(shimmer_pct: float) -> float:
    if shimmer_pct < 1.0:
        return 0.9
    if shimmer_pct < 3.0:
        return 0.4
    return 0.1


def _smoothness_sub(smoothness: float) -> float:
    """Lower second-difference RMS = unnaturally smooth pitch contour."""
    if smoothness < 0.002:
        return 0.9
    if smoothness < 0.01:
        return 0.4
    return 0.1


def _sf_sub(sf: float) -> float:
    """Wiener entropy: very low = tonal/synth, very high = noisy."""
    if sf < 0.05:
        return 0.6
    if sf < 0.2:
        return 0.2
    return 0.5


def _hf_sub(hf: float) -> float:
    """HF rolloff above 7 kHz; TTS commonly has weak HF."""
    if hf < 0.005:
        return 0.7
    if hf < 0.05:
        return 0.3
    return 0.1


def _hnr_sub(hnr_db: float) -> float:
    """Human conversational HNR ~10-25 dB; very low or very high is unusual."""
    if hnr_db < 5.0:
        return 0.6
    if hnr_db < 25.0:
        return 0.2
    return 0.5


def score_features(
    jitter_pct: float,
    shimmer_pct: float,
    smoothness: float,
    sf: float,
    hf: float,
    hnr_db: float,
    voiced_fraction: float = 1.0,
) -> float:
    parts = (
        _jitter_sub(jitter_pct) * W.jitter
        + _shimmer_sub(shimmer_pct) * W.shimmer
        + _smoothness_sub(smoothness) * W.smoothness
        + _sf_sub(sf) * W.sf
        + _hf_sub(hf) * W.hf
        + _hnr_sub(hnr_db) * W.hnr
    )
    # Down-weight if very little voiced speech was present
    if voiced_fraction < 0.3:
        parts *= 0.7
    return _clip01(parts)
