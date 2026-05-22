"""Pydantic request/response models."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    user_pid: str = Field(min_length=4, max_length=64)
    family_label: str = Field(min_length=1, max_length=64)
    salt: str = Field(min_length=8, max_length=64)
    hash: str = Field(min_length=16, max_length=128)


class CheckIn(BaseModel):
    user_pid: str
    family_label: str
    salt: str
    hash: str


class RiskParts(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    jitter: Optional[float] = None
    shimmer: Optional[float] = None
    smoothness: Optional[float] = None
    sf: Optional[float] = None
    hf: Optional[float] = None
    hnr_db: Optional[float] = None


class SightingIn(BaseModel):
    event_id: str
    ts: str
    channel: Literal["upload", "mic", "call", "voicemail"]
    origin_cc: Optional[str] = None
    risk: RiskParts
    language: Optional[str] = None
    action_taken: Optional[
        Literal["alert_shown", "blocked", "user_dismissed", "reported"]
    ] = None
    user_pid: str


class AnalyzeFeaturesIn(BaseModel):
    """Optional /v1/analyze endpoint for clients that want a server-side score.

    Client passes already-extracted features (computed on-device) and the server
    returns the canonical risk score. This keeps raw audio on-device.
    """

    jitter_pct: float
    shimmer_pct: float
    smoothness: float
    spectral_flatness: float
    hf_rolloff: float
    hnr_db: float
    voiced_fraction: float = 1.0
    language: Optional[str] = None
