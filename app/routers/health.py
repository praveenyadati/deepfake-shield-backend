from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from ..config import settings

router = APIRouter()


@router.get("/v1/health")
def health() -> dict:
    return {
        "ok": True,
        "version": settings.service_version,
        "db": settings.db_path,
        "model_loaded": Path(settings.model_path).exists(),
    }


@router.get("/v1/model/status")
def model_status() -> dict:
    return {
        "version": settings.service_version,
        "model_loaded": Path(settings.model_path).exists(),
        "model_path": settings.model_path,
        "engine": "feature-ensemble" if not Path(settings.model_path).exists() else "onnx-rawnet3",
    }
