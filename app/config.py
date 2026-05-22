"""Environment-driven configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


@dataclass(frozen=True)
class Settings:
    db_path: str
    cors_origins: list[str]
    service_version: str
    model_path: str
    high_risk_threshold: float


def load_settings() -> Settings:
    return Settings(
        db_path=os.getenv("DB_PATH", "deepfake_shield.db"),
        cors_origins=_split_csv(os.getenv("CORS_ORIGINS", "*")),
        service_version=os.getenv("SERVICE_VERSION", "deepfake-shield-1.0"),
        model_path=os.getenv("MODEL_PATH", "models/rawnet3.onnx"),
        high_risk_threshold=float(os.getenv("HIGH_RISK_THRESHOLD", "0.65")),
    )


settings = load_settings()
