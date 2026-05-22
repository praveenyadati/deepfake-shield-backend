"""SQLite connection helpers + schema bootstrapping."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS codewords (
  user_pid TEXT NOT NULL,
  family_label TEXT NOT NULL,
  salt TEXT NOT NULL,
  hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (user_pid, family_label)
);

CREATE TABLE IF NOT EXISTS sightings (
  event_id TEXT PRIMARY KEY,
  user_pid TEXT NOT NULL,
  ts TEXT NOT NULL,
  channel TEXT NOT NULL,
  origin_cc TEXT,
  risk_score REAL NOT NULL,
  jitter REAL,
  shimmer REAL,
  smoothness REAL,
  sf REAL,
  hf REAL,
  hnr_db REAL,
  language TEXT,
  action_taken TEXT,
  received_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sightings_ts ON sightings(ts);
CREATE INDEX IF NOT EXISTS idx_sightings_language ON sightings(language);
CREATE INDEX IF NOT EXISTS idx_sightings_risk ON sightings(risk_score);
"""


def init_db() -> None:
    path = Path(settings.db_path)
    if path.parent and not path.parent.exists():
        os.makedirs(path.parent, exist_ok=True)
    with connect() as c:
        c.executescript(SCHEMA)
        c.commit()


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Yield a connection with row factory; commits on success, rolls back on error."""
    conn = sqlite3.connect(settings.db_path, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        yield conn
    finally:
        conn.close()
