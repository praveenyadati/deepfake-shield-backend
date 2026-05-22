# Deepfake Shield — Backend

Privacy-first FastAPI service for the Deepfake Shield Android app and the web prototype. Stores family code-words (salted SHA-256 only, never plaintext), receives forensic-feature sightings, and emits STIX 2.1 indicators for partners (CERT-In, FCC, banks).

**Raw audio never crosses the network.** Clients compute features on-device and either score locally or POST features to `/v1/analyze/features` for the canonical server score.

## Quick start

```bash
cp .env.example .env
docker compose up --build
# → API listening on http://localhost:8000
# → SQLite persisted in the `shield-data` Docker volume
```

Health check:

```bash
curl http://localhost:8000/v1/health
# {"ok":true,"version":"deepfake-shield-1.0","db":"/data/deepfake_shield.db","model_loaded":false}
```

OpenAPI / Swagger UI: `http://localhost:8000/docs`

## Local dev without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DB_PATH=./deepfake_shield.db uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pip install pytest httpx
pytest tests/ -q
```

## Endpoints

| Method | Path                       | Purpose                                          |
| ------ | -------------------------- | ------------------------------------------------ |
| GET    | `/v1/health`               | Liveness + version + DB path                     |
| GET    | `/v1/model/status`         | Whether ONNX model is loaded (else feature mode) |
| POST   | `/v1/verify/register`      | Store salted code-word hash                      |
| POST   | `/v1/verify/check`         | Compare a candidate hash, return matched/no_match |
| POST   | `/v1/telemetry/sighting`   | Persist a forensic sighting                      |
| GET    | `/v1/stats`                | Aggregate counts (per language, channel)         |
| GET    | `/v1/threat-intel`         | STIX 2.1 bundle of high-risk sightings           |
| POST   | `/v1/analyze/features`     | Server-side scorer for on-device features        |

## Privacy posture

- Raw audio is not accepted by any endpoint.
- `user_pid` is a client-generated pseudonymous identifier (e.g. random per-device 64-bit hex).
- `salt` is generated client-side; the server only stores `salt + SHA-256(salt + codeword)`.
- STIX bundles include feature vectors and risk scores but no PII, no audio, no transcripts.
- Indexes on `ts`, `language`, and `risk_score` only — no full-text indices that might be abused.

## Configuration (`.env`)

```dotenv
DB_PATH=/data/deepfake_shield.db
CORS_ORIGINS=*
SERVICE_VERSION=deepfake-shield-1.0
MODEL_PATH=/models/rawnet3.onnx
HIGH_RISK_THRESHOLD=0.65
```

## Deployment notes

- The Dockerfile runs `uvicorn` with 2 workers as non-root user `shield` (uid 10001).
- SQLite lives on the named volume `shield-data:/data`. To migrate to Postgres later, swap `app/db.py` to use SQLAlchemy + asyncpg; the schema is small and forward-compatible.
- For HTTPS, put nginx or Caddy in front of the container. Example Caddyfile:

  ```
  api.deepfakeshield.in {
      reverse_proxy localhost:8000
  }
  ```

## Future work hooks

- `app/services/scorer.py` weights are tunable in one file — calibrate against the ASVspoof 2021-LA dev set.
- Replace the feature ensemble with a RawNet3 ONNX model: drop the model at `MODEL_PATH` and add an `onnxruntime` inference path inside `app/services/scorer.py`.
- Add `/v1/analyze/audio` (multipart WAV upload) only if a future product decision allows it — currently intentionally absent.
