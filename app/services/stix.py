"""STIX 2.1 bundle builder for high-risk sightings."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Iterable


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def build_bundle(rows: Iterable[dict]) -> dict:
    objects = []
    for r in rows:
        event_id = r["event_id"]
        indicator_id = f"indicator--{uuid.uuid5(uuid.NAMESPACE_URL, event_id)}"
        pattern = (
            "[x-deepfake-shield:risk_score >= 0.65 "
            f"AND x-deepfake-shield:language = '{r.get('language') or 'unknown'}']"
        )
        objects.append(
            {
                "type": "indicator",
                "spec_version": "2.1",
                "id": indicator_id,
                "created": r["received_at"],
                "modified": r["received_at"],
                "name": "Suspected synthetic voice",
                "description": (
                    f"Risk {r['risk_score']:.2f} on channel {r['channel']} "
                    f"(jitter={r.get('jitter')}, shimmer={r.get('shimmer')}, "
                    f"hnr={r.get('hnr_db')} dB)"
                ),
                "indicator_types": ["malicious-activity"],
                "pattern": pattern,
                "pattern_type": "stix",
                "valid_from": r["ts"],
                "labels": ["deepfake", "voice", "scam"],
            }
        )
    return {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "spec_version": "2.1",
        "objects": objects,
    }
