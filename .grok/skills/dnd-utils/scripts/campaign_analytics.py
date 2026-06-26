"""SQLite and JSON campaign analytics (read-only insights)."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dnd_state_utils import load_json
from event_system import search_events
from paths import get_campaign_path

ANALYTICS_VERSION = "3.4.0"


def _load_all_events(campaign_name: str) -> List[Dict[str, Any]]:
    path = get_campaign_path(campaign_name) / "logs" / "events.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("events", [])
    except (json.JSONDecodeError, OSError):
        return []


def sync_sqlite_from_json(campaign_name: str) -> Dict[str, Any]:
    """Backfill SQLite index from events.json (idempotent per event description+timestamp)."""
    from sqlite_layer import init_db, is_enabled, _db_path  # noqa: WPS436

    if not is_enabled(campaign_name):
        return {"synced": 0, "enabled": False, "message": "Enable SQLite via init --enable-sqlite"}

    events = _load_all_events(campaign_name)
    init_db(campaign_name)
    import sqlite3

    synced = 0
    with sqlite3.connect(_db_path(campaign_name)) as conn:
        existing = {
            (row[0], row[1])
            for row in conn.execute("SELECT timestamp, description FROM events").fetchall()
        }
        for event in events:
            key = (event.get("timestamp"), event.get("description"))
            if key in existing:
                continue
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
            synced += 1
        conn.commit()
    return {"synced": synced, "enabled": True, "total_json_events": len(events)}


def event_counts_by_tag(campaign_name: str, *, limit: int = 20) -> Dict[str, Any]:
    events = _load_all_events(campaign_name)
    counter: Counter[str] = Counter()
    for event in events:
        for tag in event.get("tags", []):
            counter[tag] += 1
    top = counter.most_common(limit)
    return {
        "campaign": campaign_name,
        "total_events": len(events),
        "tag_counts": dict(top),
        "version": ANALYTICS_VERSION,
    }


def session_timeline(campaign_name: str, *, limit: int = 30) -> Dict[str, Any]:
    events = search_events(campaign_name, limit=limit)
    timeline = [
        {
            "timestamp": e.get("timestamp"),
            "description": e.get("description"),
            "tags": e.get("tags", []),
            "importance": e.get("importance", "normal"),
        }
        for e in events
    ]
    return {
        "campaign": campaign_name,
        "timeline": timeline,
        "count": len(timeline),
        "version": ANALYTICS_VERSION,
    }


def npc_touch_frequency(campaign_name: str, *, limit: int = 15) -> Dict[str, Any]:
    """Estimate NPC mentions in events + npc index."""
    events = _load_all_events(campaign_name)
    index_path = get_campaign_path(campaign_name) / "npcs" / "index.json"
    index = load_json(index_path, {"npcs": []})
    npc_entries = index.get("npcs", [])
    names = [n.get("name", n.get("id", "")) for n in npc_entries if isinstance(n, dict)]
    if not names and isinstance(npc_entries, list):
        names = [str(n) for n in npc_entries]

    counts: Dict[str, int] = {name: 0 for name in names if name}
    for event in events:
        desc = (event.get("description") or "").lower()
        for name in names:
            if name and name.lower() in desc:
                counts[name] = counts.get(name, 0) + 1

    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    return {
        "campaign": campaign_name,
        "npc_mentions": dict(ranked),
        "indexed_npcs": len(names),
        "version": ANALYTICS_VERSION,
    }


def archive_old_events(campaign_name: str, *, keep: int = 500) -> Dict[str, Any]:
    """Move overflow events to logs/events_archive.json (scale helper)."""
    path = get_campaign_path(campaign_name) / "logs" / "events.json"
    events = _load_all_events(campaign_name)
    if len(events) <= keep:
        return {"archived": 0, "kept": len(events), "message": "No archive needed"}

    to_archive = events[:-keep]
    kept = events[-keep:]
    archive_path = path.parent / "events_archive.json"
    existing_archive: List[Dict[str, Any]] = []
    if archive_path.exists():
        try:
            existing_archive = json.loads(archive_path.read_text(encoding="utf-8"))
            if not isinstance(existing_archive, list):
                existing_archive = []
        except (json.JSONDecodeError, OSError):
            existing_archive = []

    existing_archive.extend(to_archive)
    archive_path.write_text(json.dumps(existing_archive, indent=2), encoding="utf-8")
    path.write_text(json.dumps(kept, indent=2), encoding="utf-8")

    return {
        "archived": len(to_archive),
        "kept": len(kept),
        "archive_file": str(archive_path),
        "version": ANALYTICS_VERSION,
    }


def run_analytics(
    campaign_name: str,
    report: str = "summary",
    *,
    limit: int = 20,
    keep_events: int = 500,
) -> Dict[str, Any]:
    """Dispatch analytics sub-reports."""
    if report == "tags":
        return event_counts_by_tag(campaign_name, limit=limit)
    if report == "timeline":
        return session_timeline(campaign_name, limit=limit)
    if report == "npcs":
        return npc_touch_frequency(campaign_name, limit=limit)
    if report == "sync-sqlite":
        return sync_sqlite_from_json(campaign_name)
    if report == "archive":
        return archive_old_events(campaign_name, keep=keep_events)

    sqlite_stats: Dict[str, Any] = {}
    try:
        from sqlite_layer import is_enabled, query_events_sql
        if is_enabled(campaign_name):
            sqlite_stats = {"sqlite_sample": query_events_sql(campaign_name, limit=5)}
    except Exception as exc:
        sqlite_stats = {"sqlite_error": str(exc)}

    return {
        "campaign": campaign_name,
        "report": "summary",
        "tags": event_counts_by_tag(campaign_name, limit=10),
        "timeline_recent": session_timeline(campaign_name, limit=10),
        "npcs": npc_touch_frequency(campaign_name, limit=10),
        "sqlite": sqlite_stats,
        "version": ANALYTICS_VERSION,
    }