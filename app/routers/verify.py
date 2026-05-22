from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from ..db import connect
from ..schemas import CheckIn, RegisterIn

router = APIRouter(prefix="/v1/verify")


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@router.post("/register")
def register(body: RegisterIn) -> dict:
    with connect() as c:
        c.execute(
            """INSERT OR REPLACE INTO codewords
               (user_pid, family_label, salt, hash, created_at)
               VALUES (?,?,?,?,?)""",
            (body.user_pid, body.family_label, body.salt, body.hash, _now_iso()),
        )
    return {"ok": True}


@router.post("/check")
def check(body: CheckIn) -> dict:
    with connect() as c:
        row = c.execute(
            "SELECT hash FROM codewords WHERE user_pid = ? AND family_label = ?",
            (body.user_pid, body.family_label),
        ).fetchone()
    if not row:
        return {"status": "no_such_record"}
    return {"status": "matched" if row["hash"] == body.hash else "no_match"}
