from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from ..db import connect
from ..schemas import SightingIn

router = APIRouter(prefix="/v1/telemetry")


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@router.post("/sighting")
def sighting(body: SightingIn) -> dict:
    with connect() as c:
        c.execute(
            """INSERT OR REPLACE INTO sightings
               (event_id, user_pid, ts, channel, origin_cc, risk_score,
                jitter, shimmer, smoothness, sf, hf, hnr_db,
                language, action_taken, received_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                body.event_id,
                body.user_pid,
                body.ts,
                body.channel,
                body.origin_cc,
                body.risk.score,
                body.risk.jitter,
                body.risk.shimmer,
                body.risk.smoothness,
                body.risk.sf,
                body.risk.hf,
                body.risk.hnr_db,
                body.language,
                body.action_taken,
                _now_iso(),
            ),
        )
    return {"stored": True, "event_id": body.event_id}
