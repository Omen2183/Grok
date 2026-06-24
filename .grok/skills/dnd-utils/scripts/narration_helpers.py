"""Narration and mobile-friendly formatting helpers for DM output."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from dnd_state_utils import generate_session_start_summary, get_player_character, get_world_state


def format_hp_line(hp: Dict[str, Any]) -> str:
    current = hp.get("current", "?")
    maximum = hp.get("max", "?")
    temp = hp.get("temp", 0)
    line = f"{current}/{maximum} HP"
    if temp:
        line += f" (+{temp} temp)"
    return line


def format_mobile_status(campaign_name: str) -> str:
    """Short scannable status block for Grok iOS."""
    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)
    hp = player.get("hit_points", {})
    return "\n".join(
        [
            f"📍 {world.get('current_location', 'Unknown')}",
            f"🕐 {world.get('in_game_time', 'Unknown')}",
            f"⚔️ {player.get('name', 'Adventurer')} — {format_hp_line(hp)}",
            f"Mode: {world.get('mode', 'tabletop')}",
        ]
    )


def suggest_next_actions(campaign_name: str, *, mode: Optional[str] = None) -> List[str]:
    world = get_world_state(campaign_name)
    play_mode = mode or world.get("mode", "tabletop")
    if play_mode == "kingdom":
        return [
            "Review domain projects and resources",
            "Check faction standing",
            "Advance time and resolve world events",
            "Switch to an adventure scene",
        ]
    return [
        "Explore the current location",
        "Talk to a nearby NPC",
        "Check character sheet or inventory",
        "Roll for something specific",
    ]


def proactive_opening(campaign_name: str) -> Dict[str, Any]:
    summary = generate_session_start_summary(campaign_name)
    return {
        "briefing": summary["briefing_markdown"],
        "mobile_status": format_mobile_status(campaign_name),
        "suggestions": suggest_next_actions(campaign_name),
    }


def format_combat_change(target: str, before: int, after: int, *, change_type: str = "damage") -> str:
    delta = after - before
    sign = f"{delta:+d}" if delta else "±0"
    return f"{target}: {before} → {after} HP ({change_type} {sign})"