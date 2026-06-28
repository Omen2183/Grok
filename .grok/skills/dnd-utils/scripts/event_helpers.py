"""Thin wrappers for consistent event logging across skills."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from event_system import record_combat_event, record_event, search_events


def log_significant_event(
    campaign_name: str,
    description: str,
    *,
    event_type: str = "general",
    importance: str = "normal",
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return record_event(
        campaign_name,
        description,
        event_type=event_type,
        importance=importance,
        tags=tags or [],
        metadata=metadata or {},
    )


def log_combat_beat(
    campaign_name: str,
    description: str,
    *,
    outcome: str = "ongoing",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return record_combat_event(
        campaign_name,
        description,
        outcome=outcome,
        metadata=metadata,
    )


def recent_hook_candidates(campaign_name: str, *, limit: int = 10) -> List[str]:
    hooks: List[str] = []
    for event in search_events(campaign_name, limit=limit * 2):
        tags = {t.lower() for t in event.get("tags", [])}
        if "hook" in tags or event.get("importance") == "major":
            desc = event.get("description", "").strip()
            if desc:
                hooks.append(desc)
    return hooks[-limit:]