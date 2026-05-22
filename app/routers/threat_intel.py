from __future__ import annotations

from fastapi import APIRouter

from ..config import settings
from ..db import connect
from ..services.stix import build_bundle

router = APIRouter()


@router.get("/v1/threat-intel")
def threat_intel(limit: int = 100) -> dict:
    limit = max(1, min(limit, 1000))
    with connect() as c:
        rows = [
            dict(r)
            for r in c.execute(
                """SELECT * FROM sightings
                   WHERE risk_score >= ?
                   ORDER BY received_at DESC
                   LIMIT ?""",
                (settings.high_risk_threshold, limit),
            ).fetchall()
        ]
    return build_bundle(rows)
