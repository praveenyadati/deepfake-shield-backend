from __future__ import annotations

from fastapi import APIRouter

from ..config import settings
from ..db import connect

router = APIRouter()


@router.get("/v1/stats")
def stats() -> dict:
    with connect() as c:
        scans_total = c.execute("SELECT COUNT(*) AS n FROM sightings").fetchone()["n"]
        high_risk = c.execute(
            "SELECT COUNT(*) AS n FROM sightings WHERE risk_score >= ?",
            (settings.high_risk_threshold,),
        ).fetchone()["n"]
        by_lang = {
            r["language"] or "unknown": r["n"]
            for r in c.execute(
                "SELECT language, COUNT(*) AS n FROM sightings GROUP BY language"
            ).fetchall()
        }
        by_channel = {
            r["channel"]: r["n"]
            for r in c.execute(
                "SELECT channel, COUNT(*) AS n FROM sightings GROUP BY channel"
            ).fetchall()
        }
        codewords = c.execute("SELECT COUNT(*) AS n FROM codewords").fetchone()["n"]

    return {
        "scans_total": scans_total,
        "high_risk": high_risk,
        "languages": by_lang,
        "channels": by_channel,
        "codewords": codewords,
        "version": settings.service_version,
    }
