"""Deepfake Shield FastAPI application."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .routers import analyze, health, stats, telemetry, threat_intel, verify


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Deepfake Shield API",
    version=settings.service_version,
    description=(
        "Privacy-first synthetic-voice detection backend. Raw audio is never "
        "transmitted; clients send extracted features and STIX-compatible "
        "sightings."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(verify.router, tags=["family-verify"])
app.include_router(telemetry.router, tags=["telemetry"])
app.include_router(stats.router, tags=["stats"])
app.include_router(threat_intel.router, tags=["threat-intel"])
app.include_router(analyze.router, tags=["analyze"])
