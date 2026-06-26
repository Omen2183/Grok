"""Class-based starting equipment and gold for random characters."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

EQUIPMENT_VERSION = "5.0.0"

STARTING_GOLD: Dict[str, int] = {
    "barbarian": 50, "bard": 125, "cleric": 125, "druid": 50,
    "fighter": 125, "monk": 15, "paladin": 125, "ranger": 125,
    "rogue": 100, "sorcerer": 75, "warlock": 100, "wizard": 80,
}

CLASS_KITS: Dict[str, List[Dict[str, Any]]] = {
    "fighter": [
        {"name": "Chain mail", "type": "armor"},
        {"name": "Longsword", "type": "weapon"},
        {"name": "Shield", "type": "armor"},
        {"name": "Light crossbow", "type": "weapon"},
        {"name": "Explorer's pack", "type": "gear"},
    ],
    "wizard": [
        {"name": "Spellbook", "type": "focus"},
        {"name": "Quarterstaff", "type": "weapon"},
        {"name": "Component pouch", "type": "gear"},
        {"name": "Scholar's pack", "type": "gear"},
        {"name": "Dagger", "type": "weapon"},
    ],
    "rogue": [
        {"name": "Leather armor", "type": "armor"},
        {"name": "Shortsword", "type": "weapon"},
        {"name": "Shortbow", "type": "weapon"},
        {"name": "Thieves' tools", "type": "tool"},
        {"name": "Burglar's pack", "type": "gear"},
    ],
    "cleric": [
        {"name": "Scale mail", "type": "armor"},
        {"name": "Mace", "type": "weapon"},
        {"name": "Shield", "type": "armor"},
        {"name": "Holy symbol", "type": "focus"},
        {"name": "Priest's pack", "type": "gear"},
    ],
    "ranger": [
        {"name": "Scale mail", "type": "armor"},
        {"name": "Longbow", "type": "weapon"},
        {"name": "Shortsword", "type": "weapon"},
        {"name": "Explorer's pack", "type": "gear"},
    ],
    "barbarian": [
        {"name": "Greataxe", "type": "weapon"},
        {"name": "Handaxe (2)", "type": "weapon"},
        {"name": "Explorer's pack", "type": "gear"},
        {"name": "Javelin (4)", "type": "weapon"},
    ],
    "bard": [
        {"name": "Leather armor", "type": "armor"},
        {"name": "Rapier", "type": "weapon"},
        {"name": "Lute", "type": "gear"},
        {"name": "Diplomat's pack", "type": "gear"},
    ],
    "paladin": [
        {"name": "Chain mail", "type": "armor"},
        {"name": "Longsword", "type": "weapon"},
        {"name": "Shield", "type": "armor"},
        {"name": "Holy symbol", "type": "focus"},
        {"name": "Priest's pack", "type": "gear"},
    ],
    "monk": [
        {"name": "Shortsword", "type": "weapon"},
        {"name": "Dart (10)", "type": "weapon"},
        {"name": "Explorer's pack", "type": "gear"},
    ],
    "sorcerer": [
        {"name": "Light crossbow", "type": "weapon"},
        {"name": "Component pouch", "type": "gear"},
        {"name": "Dungeoneer's pack", "type": "gear"},
        {"name": "Dagger", "type": "weapon"},
    ],
    "warlock": [
        {"name": "Leather armor", "type": "armor"},
        {"name": "Light crossbow", "type": "weapon"},
        {"name": "Component pouch", "type": "gear"},
        {"name": "Scholar's pack", "type": "gear"},
        {"name": "Dagger", "type": "weapon"},
    ],
    "druid": [
        {"name": "Leather armor", "type": "armor"},
        {"name": "Shield", "type": "armor"},
        {"name": "Scimitar", "type": "weapon"},
        {"name": "Druidic focus", "type": "focus"},
        {"name": "Explorer's pack", "type": "gear"},
    ],
}

DEFAULT_KIT = [
    {"name": "Leather armor", "type": "armor"},
    {"name": "Shortsword", "type": "weapon"},
    {"name": "Explorer's pack", "type": "gear"},
]


def generate_starting_equipment(
    primary_class: str,
    *,
    level: int = 1,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    key = primary_class.lower()
    kit = list(CLASS_KITS.get(key, DEFAULT_KIT))
    gold_base = STARTING_GOLD.get(key, 50)
    gold = gold_base + rng.randint(0, gold_base // 2) + max(0, (level - 1) * 25)
    return {
        "class": primary_class,
        "level": level,
        "equipment": kit,
        "gold_gp": gold,
        "version": EQUIPMENT_VERSION,
    }