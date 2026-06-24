"""Bidirectional sync between combat tracker and character manager."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

UTILS = Path(__file__).resolve().parent
CHAR_SCRIPTS = UTILS.parent.parent / "dnd-character-manager" / "scripts"
if str(CHAR_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(CHAR_SCRIPTS))

from dnd_state_utils import get_player_character, update_player_hp  # noqa: E402

try:
    from character_manager import (  # noqa: E402
        apply_death_save,
        apply_healing_while_dying,
        handle_character_downed,
        stabilize_character,
        sync_character_status,
    )
except ImportError:
    def handle_character_downed(campaign_name: str) -> Dict[str, Any]:
        return update_player_hp(campaign_name, new_current=0)

    def apply_death_save(campaign_name: str, success: bool) -> Dict[str, Any]:
        return {"success": success}

    def apply_healing_while_dying(campaign_name: str, amount: int) -> Dict[str, Any]:
        return update_player_hp(campaign_name, delta=amount)

    def stabilize_character(campaign_name: str) -> Dict[str, Any]:
        return {}

    def sync_character_status(campaign_name: str) -> Dict[str, Any]:
        return get_player_character(campaign_name)


def on_player_damaged(campaign_name: str, new_hp: int) -> Dict[str, Any]:
    if new_hp <= 0:
        return handle_character_downed(campaign_name)
    return sync_character_status(campaign_name)


def on_player_healed(campaign_name: str, amount: int) -> Dict[str, Any]:
    char = get_player_character(campaign_name)
    if char.get("status", "Alive").lower() in ("dying", "stable (0 hp)"):
        return apply_healing_while_dying(campaign_name, amount)
    return update_player_hp(campaign_name, delta=amount)


def on_player_death_save(campaign_name: str, success: bool) -> Dict[str, Any]:
    result = apply_death_save(campaign_name, success)
    ds = result.get("death_saves", {})
    if ds.get("successes", 0) >= 3:
        stabilize_character(campaign_name)
    return result


def sync_combatant_to_character(
    campaign_name: str,
    combatant: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    if not combatant.get("is_player"):
        return None
    hp_current = combatant.get("hp_current", 0)
    char = get_player_character(campaign_name)
    char_hp = char.get("hit_points", {}).get("current", 0)
    if hp_current != char_hp:
        return update_player_hp(campaign_name, new_current=hp_current)
    return char