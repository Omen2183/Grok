"""SRD spell, feat, and multiclass reference data (5e OGL subset)."""

from __future__ import annotations

from typing import Any, Dict, List

SRD_DATA_VERSION = "4.0.0"

SPELLS: Dict[str, Dict[str, Any]] = {
    "fireball": {
        "name": "Fireball",
        "level": 3,
        "school": "evocation",
        "casting_time": "1 action",
        "range": "150 feet",
        "components": "V, S, M (a tiny ball of bat guano and sulfur)",
        "duration": "Instantaneous",
        "classes": ["sorcerer", "wizard"],
        "summary": "20-ft-radius sphere; DEX save for half; 8d6 fire damage (scales +1d6 per slot above 3rd).",
    },
    "magic_missile": {
        "name": "Magic Missile",
        "level": 1,
        "school": "evocation",
        "casting_time": "1 action",
        "range": "120 feet",
        "components": "V, S",
        "duration": "Instantaneous",
        "classes": ["sorcerer", "wizard"],
        "summary": "Three darts, each 1d4+1 force damage; auto-hit. +1 dart per slot above 1st.",
    },
    "cure_wounds": {
        "name": "Cure Wounds",
        "level": 1,
        "school": "evocation",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, S",
        "duration": "Instantaneous",
        "classes": ["bard", "cleric", "druid", "paladin", "ranger"],
        "summary": "1d8 + spellcasting modifier HP healed; +1d8 per slot above 1st.",
    },
    "healing_word": {
        "name": "Healing Word",
        "level": 1,
        "school": "evocation",
        "casting_time": "1 bonus action",
        "range": "60 feet",
        "components": "V",
        "duration": "Instantaneous",
        "classes": ["bard", "cleric", "druid"],
        "summary": "1d4 + spellcasting modifier HP; bonus action at range.",
    },
    "shield": {
        "name": "Shield",
        "level": 1,
        "school": "abjuration",
        "casting_time": "1 reaction",
        "range": "Self",
        "components": "V, S",
        "duration": "1 round",
        "classes": ["sorcerer", "wizard"],
        "summary": "+5 AC until start of next turn; reaction when hit or targeted by magic missile.",
    },
    "counterspell": {
        "name": "Counterspell",
        "level": 3,
        "school": "abjuration",
        "casting_time": "1 reaction",
        "range": "60 feet",
        "components": "S",
        "duration": "Instantaneous",
        "classes": ["sorcerer", "warlock", "wizard"],
        "summary": "Interrupt spell of 3rd level or lower. Higher slots: auto-counter or ability check.",
    },
    "hold_person": {
        "name": "Hold Person",
        "level": 2,
        "school": "enchantment",
        "casting_time": "1 action",
        "range": "60 feet",
        "components": "V, S, M",
        "duration": "Concentration, up to 1 minute",
        "classes": ["bard", "cleric", "druid", "sorcerer", "warlock", "wizard"],
        "summary": "Humanoid WIS save or paralyzed; repeat save end of each turn.",
    },
    "bless": {
        "name": "Bless",
        "level": 1,
        "school": "enchantment",
        "casting_time": "1 action",
        "range": "30 feet",
        "components": "V, S, M",
        "duration": "Concentration, up to 1 minute",
        "classes": ["cleric", "paladin"],
        "summary": "Up to 3 creatures add 1d4 to attack rolls and saving throws.",
    },
    "spiritual_weapon": {
        "name": "Spiritual Weapon",
        "level": 2,
        "school": "evocation",
        "casting_time": "1 bonus action",
        "range": "60 feet",
        "components": "V, S",
        "duration": "1 minute",
        "classes": ["cleric"],
        "summary": "Bonus action melee spell attack for 1d8+mod force; move 20 ft as bonus action.",
    },
    "hunters_mark": {
        "name": "Hunter's Mark",
        "level": 1,
        "school": "divination",
        "casting_time": "1 bonus action",
        "range": "90 feet",
        "components": "V",
        "duration": "Concentration, up to 1 hour",
        "classes": ["ranger"],
        "summary": "+1d6 damage on weapon hits vs marked target; advantage on Perception/Survival to find.",
    },
    "eldritch_blast": {
        "name": "Eldritch Blast",
        "level": 0,
        "school": "evocation",
        "casting_time": "1 action",
        "range": "120 feet",
        "components": "V, S",
        "duration": "Instantaneous",
        "classes": ["warlock"],
        "summary": "Ranged spell attack for 1d10 force; scales with character level (extra beams).",
    },
    "misty_step": {
        "name": "Misty Step",
        "level": 2,
        "school": "conjuration",
        "casting_time": "1 bonus action",
        "range": "Self",
        "components": "V",
        "duration": "Instantaneous",
        "classes": ["sorcerer", "warlock", "wizard"],
        "summary": "Teleport up to 30 feet to unoccupied space you can see.",
    },
    "revivify": {
        "name": "Revivify",
        "level": 3,
        "school": "necromancy",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, S, M (diamonds worth 300 gp)",
        "duration": "Instantaneous",
        "classes": ["cleric", "paladin"],
        "summary": "Return creature dead ≤1 minute to 1 HP.",
    },
    "detect_magic": {
        "name": "Detect Magic",
        "level": 1,
        "school": "divination",
        "casting_time": "1 action",
        "range": "Self",
        "components": "V, S",
        "duration": "Concentration, up to 10 minutes",
        "classes": ["bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "wizard"],
        "summary": "Sense magic within 30 feet; action to see aura and school.",
    },
    "dispel_magic": {
        "name": "Dispel Magic",
        "level": 3,
        "school": "abjuration",
        "casting_time": "1 action",
        "range": "120 feet",
        "components": "V, S",
        "duration": "Instantaneous",
        "classes": ["bard", "cleric", "druid", "paladin", "sorcerer", "warlock", "wizard"],
        "summary": "End spells of 3rd level or lower on target; ability check for higher.",
    },
}

FEATS: Dict[str, Dict[str, Any]] = {
    "great_weapon_master": {
        "name": "Great Weapon Master",
        "prerequisite": "STR 13+",
        "summary": "Take -5 to attack for +10 damage on melee heavy weapon hits; bonus attack on crit or kill.",
    },
    "sharpshooter": {
        "name": "Sharpshooter",
        "prerequisite": "DEX 13+",
        "summary": "Ignore cover; -5 attack for +10 ranged damage; no disadvantage at long range.",
    },
    "war_caster": {
        "name": "War Caster",
        "prerequisite": "Ability to cast spells",
        "summary": "Advantage on CON saves for concentration; somatic with hands full; OA with spells.",
    },
    "lucky": {
        "name": "Lucky",
        "prerequisite": "None",
        "summary": "3 luck points per long rest; reroll attack, save, or ability check (yours or against you).",
    },
    "alert": {
        "name": "Alert",
        "prerequisite": "None",
        "summary": "+5 initiative; can't be surprised while conscious; hidden creatures don't get advantage.",
    },
    "mobile": {
        "name": "Mobile",
        "prerequisite": "None",
        "summary": "+10 speed; Dash ignores difficult terrain; no OA from creature you melee attack.",
    },
    "resilient": {
        "name": "Resilient",
        "prerequisite": "None",
        "summary": "+1 to chosen ability; proficiency in saves using that ability.",
    },
    "polearm_master": {
        "name": "Polearm Master",
        "prerequisite": "None",
        "summary": "Bonus action butt attack; OA when enemy enters reach with glaive/halberd/quarterstaff/spear.",
    },
    "sentinel": {
        "name": "Sentinel",
        "prerequisite": "None",
        "summary": "OA reduces speed to 0; OA even if target Disengages; reaction attack when ally hit in 5 ft.",
    },
    "tough": {
        "name": "Tough",
        "prerequisite": "None",
        "summary": "+2 HP per level (retroactive).",
    },
    "magic_initiate": {
        "name": "Magic Initiate",
        "prerequisite": "None",
        "summary": "Two cantrips + one 1st-level spell from a class list; cast 1st-level once per long rest.",
    },
    "observant": {
        "name": "Observant",
        "prerequisite": "None",
        "summary": "+1 INT or WIS; read lips; +5 passive Investigation and Perception.",
    },
}


def search_spells(query: str, *, limit: int = 10) -> List[Dict[str, Any]]:
    needle = query.lower().replace(" ", "_")
    hits = []
    for key, spell in SPELLS.items():
        hay = f"{key} {spell.get('name', '')} {spell.get('summary', '')} {' '.join(spell.get('classes', []))}".lower()
        if needle in hay or any(w in hay for w in needle.split("_")):
            hits.append({"id": key, **spell})
    return hits[:limit]


def search_feats(query: str, *, limit: int = 10) -> List[Dict[str, Any]]:
    needle = query.lower().replace(" ", "_")
    hits = []
    for key, feat in FEATS.items():
        hay = f"{key} {feat.get('name', '')} {feat.get('summary', '')}".lower()
        if needle in hay:
            hits.append({"id": key, **feat})
    return hits[:limit]


def lookup_spell(name: str) -> Dict[str, Any]:
    key = name.lower().replace(" ", "_")
    if key in SPELLS:
        return {"found": True, "id": key, **SPELLS[key]}
    matches = [k for k in SPELLS if key in k]
    if len(matches) == 1:
        k = matches[0]
        return {"found": True, "id": k, **SPELLS[k]}
    return {"found": False, "query": name, "available": sorted(SPELLS.keys())}


def lookup_feat(name: str) -> Dict[str, Any]:
    key = name.lower().replace(" ", "_")
    if key in FEATS:
        return {"found": True, "id": key, **FEATS[key]}
    matches = [k for k in FEATS if key in k]
    if len(matches) == 1:
        k = matches[0]
        return {"found": True, "id": k, **FEATS[k]}
    return {"found": False, "query": name, "available": sorted(FEATS.keys())}