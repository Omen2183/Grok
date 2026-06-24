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
    """Sync combat HP to the character sheet; initialize dying state at 0 HP."""
    update_player_hp(campaign_name, new_current=max(0, new_hp))
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


def _sync_death_saves_from_combat(
    campaign_name: str,
    combatant: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Align sheet death saves with combat tracker counts (reconciliation path)."""
    ds = combatant.get("death_saves", {})
    if not ds:
        return None
    try:
        from character_manager import load_character, save_character, stabilize_character  # noqa: E402
    except ImportError:
        return None

    sheet = load_character(campaign_name)
    sheet_ds = sheet.setdefault("death_saves", {"successes": 0, "failures": 0, "status": "dying"})
    successes = ds.get("successes", 0)
    failures = ds.get("failures", 0)
    if (
        successes == sheet_ds.get("successes")
        and failures == sheet_ds.get("failures")
    ):
        return sheet

    sheet_ds["successes"] = successes
    sheet_ds["failures"] = failures
    if successes >= 3:
        return stabilize_character(campaign_name)
    if failures >= 3:
        sheet_ds["status"] = "dead"
        sheet["status"] = "Dead"
        save_character(campaign_name, sheet)
        return sheet

    sheet_ds["status"] = "dying"
    sheet["status"] = "Dying"
    save_character(campaign_name, sheet)
    return sheet


def _sync_unconscious_condition(campaign_name: str, combatant: Dict[str, Any]) -> None:
    """Mirror Unconscious condition between combat JSON and character sheet."""
    try:
        from character_manager import load_character, save_character  # noqa: E402
    except ImportError:
        return

    hp_current = combatant.get("hp_current", 0)
    sheet = load_character(campaign_name)
    conditions = sheet.setdefault("conditions", [])
    unconscious = combatant.get("is_unconscious") or hp_current <= 0

    if unconscious and "Unconscious" not in conditions:
        conditions.append("Unconscious")
        save_character(campaign_name, sheet)
    elif not unconscious and "Unconscious" in conditions:
        sheet["conditions"] = [c for c in conditions if c != "Unconscious"]
        save_character(campaign_name, sheet)


def sync_combatant_to_character(
    campaign_name: str,
    combatant: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Full combat→sheet sync: HP, dying state, death saves, and Unconscious condition."""
    if not combatant.get("is_player"):
        return None

    hp_current = combatant.get("hp_current", 0)
    char = on_player_damaged(campaign_name, hp_current)

    if hp_current <= 0:
        _sync_death_saves_from_combat(campaign_name, combatant)
    _sync_unconscious_condition(campaign_name, combatant)
    return get_player_character(campaign_name)