"""Campaign dashboard — unified state snapshot for mobile/Grok iOS inspection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from dnd_state_utils import (
    enhanced_audit_campaign,
    get_kingdom_state,
    get_player_character,
    get_world_state,
    load_json,
)
from event_system import search_events
from paths import get_campaign_path

DASHBOARD_VERSION = "3.4.0"


def _combat_snapshot(campaign_name: str) -> Dict[str, Any]:
    path = get_campaign_path(campaign_name) / "combat" / "current_combat.json"
    if not path.exists():
        return {"active": False}
    data = load_json(path, {})
    combatants = data.get("combatants", [])
    return {
        "active": bool(combatants),
        "encounter": data.get("encounter_name", ""),
        "round": data.get("round", 0),
        "combatant_count": len(combatants),
        "current_turn": data.get("current_turn_index"),
    }


def _quests_snapshot(campaign_name: str) -> Dict[str, Any]:
    path = get_campaign_path(campaign_name) / "state" / "quests.json"
    data = load_json(path, {"quests": [], "hooks": []})
    active = [q for q in data.get("quests", []) if q.get("status") == "active"]
    completed = [q for q in data.get("quests", []) if q.get("status") == "completed"]
    hooks = [h for h in data.get("hooks", []) if not h.get("resolved")]
    return {
        "active": len(active),
        "completed": len(completed),
        "hooks": len(hooks),
        "active_titles": [q.get("title", q.get("name", "")) for q in active[:5]],
    }


def _npc_count(campaign_name: str) -> int:
    index = get_campaign_path(campaign_name) / "npcs" / "index.json"
    data = load_json(index, {"npcs": []})
    npcs = data.get("npcs", data if isinstance(data, list) else [])
    return len(npcs) if isinstance(npcs, list) else len(data.get("npcs", []))


def _recap_count(campaign_name: str) -> int:
    recaps = get_campaign_path(campaign_name) / "recaps"
    if not recaps.exists():
        return 0
    return len(list(recaps.glob("session_*.md")))


def build_campaign_dashboard(campaign_name: str, *, include_audit: bool = False) -> Dict[str, Any]:
    """Return a scannable campaign snapshot for agents and mobile status."""
    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)
    kingdom = get_kingdom_state(campaign_name)
    hp = player.get("hit_points", {})
    recent = search_events(campaign_name, limit=5)

    try:
        from sqlite_layer import is_enabled
        sqlite_on = is_enabled(campaign_name)
    except Exception:
        sqlite_on = False

    dashboard: Dict[str, Any] = {
        "version": DASHBOARD_VERSION,
        "campaign": campaign_name,
        "location": world.get("current_location", "Unknown"),
        "time": world.get("in_game_time", "Unknown"),
        "mode": world.get("mode", "tabletop"),
        "weather": world.get("weather", "clear"),
        "character": {
            "name": player.get("name", "Adventurer"),
            "level": player.get("level", 1),
            "hp": f"{hp.get('current', '?')}/{hp.get('max', '?')}",
            "xp": player.get("xp", 0),
            "conditions": player.get("conditions", []),
        },
        "combat": _combat_snapshot(campaign_name),
        "quests": _quests_snapshot(campaign_name),
        "kingdom": {
            "domain": kingdom.get("domain_name", "Unsettled Lands"),
            "resources": kingdom.get("resources", {}),
            "active_projects": len([p for p in kingdom.get("projects", []) if p.get("status") == "queued"]),
        },
        "counts": {
            "npcs": _npc_count(campaign_name),
            "recaps": _recap_count(campaign_name),
            "recent_events": len(recent),
        },
        "sqlite_enabled": sqlite_on,
        "recent_events": [e.get("description", "") for e in recent],
        "mobile_summary": _format_mobile_summary(campaign_name, world, player, hp),
    }

    if include_audit:
        dashboard["audit"] = enhanced_audit_campaign(campaign_name)

    return dashboard


def _format_mobile_summary(
    campaign_name: str,
    world: Dict[str, Any],
    player: Dict[str, Any],
    hp: Dict[str, Any],
) -> str:
    combat = _combat_snapshot(campaign_name)
    quests = _quests_snapshot(campaign_name)
    lines = [
        f"**{player.get('name', 'Adventurer')}** (Lv {player.get('level', 1)}) — "
        f"HP {hp.get('current', '?')}/{hp.get('max', '?')}",
        f"**Where:** {world.get('current_location', 'Unknown')} · {world.get('in_game_time', '')}",
    ]
    if combat["active"]:
        lines.append(f"**Combat:** {combat.get('encounter', 'active')} (round {combat.get('round', 1)})")
    if quests["active"]:
        lines.append(f"**Quests:** {quests['active']} active")
    lines.append("**What do you do?**")
    return "\n".join(lines)