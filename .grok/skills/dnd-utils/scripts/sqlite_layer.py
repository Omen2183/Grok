"""Optional SQLite index for campaign events (JSON remains source of truth)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from paths import get_campaign_path


def _db_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "campaign_index.sqlite"


def is_enabled(campaign_name: str) -> bool:
    return (get_campaign_path(campaign_name) / "state" / "sqlite_enabled.flag").exists()


def init_db(campaign_name: str) -> None:
    path = _db_path(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                description TEXT,
                importance TEXT,
                event_type TEXT,
                tags TEXT,
                metadata TEXT
            )
            """
        )
        conn.commit()


def sync_event_to_sqlite(campaign_name: str, event: Dict[str, Any]) -> None:
    if not is_enabled(campaign_name):
        return
    init_db(campaign_name)
    with sqlite3.connect(_db_path(campaign_name)) as conn:
        conn.execute(
            """
            INSERT INTO events (timestamp, description, importance, event_type, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event.get("timestamp"),
                event.get("description"),
                event.get("importance", "normal"),
                event.get("type", "general"),
                json.dumps(event.get("tags", [])),
                json.dumps(event.get("metadata", {})),
            ),
        )
        conn.commit()


def query_events_sql(
    campaign_name: str,
    *,
    tag: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    if not is_enabled(campaign_name):
        return []
    init_db(campaign_name)
    with sqlite3.connect(_db_path(campaign_name)) as conn:
        conn.row_factory = sqlite3.Row
        if tag:
            rows = conn.execute(
                """
                SELECT * FROM events
                WHERE tags LIKE ?
                ORDER BY id DESC LIMIT ?
                """,
                (f'%"{tag}"%', limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
    results = []
    for row in rows:
        results.append(
            {
                "timestamp": row["timestamp"],
                "description": row["description"],
                "importance": row["importance"],
                "type": row["event_type"],
                "tags": json.loads(row["tags"] or "[]"),
                "metadata": json.loads(row["metadata"] or "{}"),
            }
        )
    return results