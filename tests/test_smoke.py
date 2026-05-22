"""Smoke tests: spin up app in-process and hit every endpoint."""
from __future__ import annotations

import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    os.environ["DB_PATH"] = tmp.name
    # Late import so config picks up the env var
    from app.main import app  # noqa: WPS433

    with TestClient(app) as c:
        yield c
    os.unlink(tmp.name)


def test_health(client):
    r = client.get("/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True


def test_register_and_check(client):
    pid = "pid_test"
    payload = {
        "user_pid": pid,
        "family_label": "grandson",
        "salt": "abcd1234efgh",
        "hash": "0" * 64,
    }
    assert client.post("/v1/verify/register", json=payload).status_code == 200
    r = client.post("/v1/verify/check", json=payload)
    assert r.json()["status"] == "matched"
    bad = {**payload, "hash": "f" * 64}
    assert client.post("/v1/verify/check", json=bad).json()["status"] == "no_match"


def test_sighting_and_stats(client):
    event = {
        "event_id": str(uuid.uuid4()),
        "ts": "2026-05-22T01:00:00Z",
        "channel": "call",
        "origin_cc": "US",
        "risk": {
            "score": 0.78,
            "jitter": 0.27,
            "shimmer": 3.0,
            "smoothness": 0.004,
            "sf": 0.0001,
            "hf": 0.0,
            "hnr_db": 9.0,
        },
        "language": "en",
        "action_taken": "alert_shown",
        "user_pid": "pid_test",
    }
    r = client.post("/v1/telemetry/sighting", json=event)
    assert r.status_code == 200
    assert r.json()["stored"] is True

    stats = client.get("/v1/stats").json()
    assert stats["scans_total"] >= 1
    assert stats["high_risk"] >= 1


def test_threat_intel_bundle(client):
    r = client.get("/v1/threat-intel")
    bundle = r.json()
    assert bundle["type"] == "bundle"
    assert bundle["spec_version"] == "2.1"
    assert isinstance(bundle["objects"], list)


def test_analyze_features(client):
    r = client.post(
        "/v1/analyze/features",
        json={
            "jitter_pct": 0.2,
            "shimmer_pct": 0.5,
            "smoothness": 0.001,
            "spectral_flatness": 0.01,
            "hf_rolloff": 0.001,
            "hnr_db": 28.0,
        },
    )
    body = r.json()
    assert body["verdict"] in {"high", "inconclusive", "low"}
    assert 0.0 <= body["risk_score"] <= 1.0
