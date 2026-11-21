"""Small SQLite persistence layer shared by every node in an HIF session."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HIFStore:
    def __init__(self, database_path: Path | str) -> None:
        self.path = Path(database_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=20)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS memory (
                    memory_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
                    memory_key TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_node TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_memory_session_time
                    ON memory(session_id, created_at);
                CREATE INDEX IF NOT EXISTS ix_memory_session_key
                    ON memory(session_id, memory_key);
                CREATE TABLE IF NOT EXISTS nodes (
                    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
                    node_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    model TEXT,
                    result_json TEXT,
                    started_at TEXT,
                    finished_at TEXT,
                    PRIMARY KEY(session_id, node_id)
                );
                CREATE TABLE IF NOT EXISTS usage (
                    usage_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
                    model TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    cost_usd REAL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_usage_model_time ON usage(model, created_at);
                """
            )

    def create_session(self, goal: str, session_id: str | None = None) -> str:
        sid = session_id or str(uuid4())
        now = utc_now().isoformat()
        with self._connect() as db:
            existing = db.execute(
                "SELECT session_id FROM sessions WHERE session_id = ?", (sid,)
            ).fetchone()
            if existing:
                db.execute(
                    "UPDATE sessions SET goal=?, status='running', updated_at=? WHERE session_id=?",
                    (goal, now, sid),
                )
            else:
                db.execute(
                    "INSERT INTO sessions(session_id, goal, status, created_at, updated_at) "
                    "VALUES (?, ?, 'running', ?, ?)",
                    (sid, goal, now, now),
                )
        return sid

    def set_session_status(self, session_id: str, status: str) -> None:
        with self._connect() as db:
            db.execute(
                "UPDATE sessions SET status=?, updated_at=? WHERE session_id=?",
                (status, utc_now().isoformat(), session_id),
            )

    def add_memory(
        self,
        session_id: str,
        memory_key: str,
        role: str,
        content: str,
        source_node: str | None = None,
    ) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO memory(memory_id, session_id, memory_key, role, content, "
                "source_node, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    str(uuid4()), session_id, memory_key, role, content, source_node,
                    utc_now().isoformat(),
                ),
            )

    def get_memory(
        self, session_id: str, keys: list[str] | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        with self._connect() as db:
            if keys:
                placeholders = ",".join("?" for _ in keys)
                rows = db.execute(
                    f"SELECT memory_key, role, content, source_node, created_at FROM memory "
                    f"WHERE session_id=? AND memory_key IN ({placeholders}) "
                    "ORDER BY created_at DESC LIMIT ?",
                    (session_id, *keys, limit),
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT memory_key, role, content, source_node, created_at FROM memory "
                    "WHERE session_id=? ORDER BY created_at DESC LIMIT ?",
                    (session_id, limit),
                ).fetchall()
        return [dict(row) for row in rows]

    def save_node(self, session_id: str, node_id: str, role: str, status: str,
                  model: str | None = None, result: dict[str, Any] | None = None) -> None:
        now = utc_now().isoformat()
        result_json = json.dumps(result, ensure_ascii=False) if result is not None else None
        with self._connect() as db:
            db.execute(
                "INSERT INTO nodes(session_id, node_id, role, status, model, result_json, "
                "started_at, finished_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(session_id, node_id) DO UPDATE SET status=excluded.status, "
                "model=excluded.model, result_json=excluded.result_json, "
                "finished_at=excluded.finished_at",
                (session_id, node_id, role, status, model, result_json, now, now if status in {
                    "completed", "failed", "cancelled"
                } else None),
            )

    def add_usage(
        self, session_id: str, model: str, input_tokens: int, output_tokens: int,
        cost_usd: float | None = None,
    ) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO usage(usage_id, session_id, model, input_tokens, output_tokens, "
                "cost_usd, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    str(uuid4()), session_id, model, max(0, input_tokens),
                    max(0, output_tokens), cost_usd, utc_now().isoformat(),
                ),
            )

    def model_usage_since(self, model: str, since: datetime) -> int:
        with self._connect() as db:
            row = db.execute(
                "SELECT COALESCE(SUM(input_tokens + output_tokens), 0) AS total "
                "FROM usage WHERE model=? AND created_at>=?",
                (model, since.isoformat()),
            ).fetchone()
        return int(row["total"] if row else 0)

    def usage_summary(self, window_hours: int = 168) -> list[dict[str, Any]]:
        since = (utc_now() - timedelta(hours=window_hours)).isoformat()
        with self._connect() as db:
            rows = db.execute(
                "SELECT model, SUM(input_tokens) AS input_tokens, "
                "SUM(output_tokens) AS output_tokens, SUM(cost_usd) AS cost_usd "
                "FROM usage WHERE created_at>=? GROUP BY model ORDER BY model",
                (since,),
            ).fetchall()
        return [dict(row) for row in rows]

    def session_nodes(self, session_id: str) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT node_id, role, status, model, started_at, finished_at "
                "FROM nodes WHERE session_id=? ORDER BY started_at",
                (session_id,),
            ).fetchall()
        return [dict(row) for row in rows]
