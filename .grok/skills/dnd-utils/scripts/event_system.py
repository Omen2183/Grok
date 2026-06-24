"""Lightweight event logging for D&D campaigns."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from paths import get_campaign_path


def _events_file(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "logs" / "events.json"


def _load_events(campaign_name: str) -> List[Dict[str, Any]]:
    path = _events_file(campaign_name)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_events(campaign_name: str, events: List[Dict[str, Any]]) -> None:
    path = _events_file(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as handle:
        json.dump(events, handle, indent=2, ensure_ascii=False)
    temp.replace(path)


def record_event(
    campaign_name: str,
    description: str,
    *,
    importance: str = "normal",
    tags: Optional[List[str]] = None,
    event_type: str = "general",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Append a structured event to the campaign log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "description": description,
        "importance": importance,
        "tags": tags or [],
        "type": event_type,
        "metadata": metadata or {},
    }
    events = _load_events(campaign_name)
    events.append(entry)
    _save_events(campaign_name, events)
    return entry


def record_combat_event(
    campaign_name: str,
    description: str,
    *,
    outcome: str = "unknown",
    importance: str = "normal",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Record a combat-related event."""
    return record_event(
        campaign_name,
        description,
        importance=importance,
        event_type="combat",
        metadata={"outcome": outcome, **(metadata or {})},
    )


def search_events(
    campaign_name: str,
    *,
    tag: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Search recent events, optionally filtered by tag."""
    events = _load_events(campaign_name)
    if tag:
        tags = {t.strip().lower() for t in tag.split(",") if t.strip()}
        events = [
            e
            for e in events
            if tags.intersection({t.lower() for t in e.get("tags", [])})
        ]
    return events[-limit:]