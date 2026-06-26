"""Multiclass prerequisites, spell slot tables, and build validation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

CLASS_PROGRESSION_VERSION = "4.0.0"

# Ability score prerequisites for multiclassing into a class (5e PHB)
MULTICLASS_PREREQS: Dict[str, Dict[str, int]] = {
    "barbarian": {"str": 13},
    "bard": {"cha": 13},
    "cleric": {"wis": 13},
    "druid": {"wis": 13},
    "fighter": {"str": 13, "dex": 13},  # either
    "monk": {"dex": 13, "wis": 13},
    "paladin": {"str": 13, "cha": 13},
    "ranger": {"dex": 13, "wis": 13},
    "rogue": {"dex": 13},
    "sorcerer": {"cha": 13},
    "warlock": {"cha": 13},
    "wizard": {"int": 13},
}

FULL_CASTER_SLOTS: Dict[int, List[int]] = {
    1: [2],
    2: [3],
    3: [4, 2],
    4: [4, 3],
    5: [4, 3, 2],
    6: [4, 3, 3],
    7: [4, 3, 3, 1],
    8: [4, 3, 3, 2],
    9: [4, 3, 3, 3, 1],
    10: [4, 3, 3, 3, 2],
    11: [4, 3, 3, 3, 2, 1],
    12: [4, 3, 3, 3, 2, 1],
    13: [4, 3, 3, 3, 2, 1, 1],
    14: [4, 3, 3, 3, 2, 1, 1],
    15: [4, 3, 3, 3, 2, 1, 1, 1],
    16: [4, 3, 3, 3, 2, 1, 1, 1],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
}

HALF_CASTER_SLOTS: Dict[int, List[int]] = {
    1: [],
    2: [2],
    3: [3],
    4: [3],
    5: [4, 2],
    6: [4, 2],
    7: [4, 3],
    8: [4, 3],
    9: [4, 3, 2],
    10: [4, 3, 2],
    11: [4, 3, 3],
    12: [4, 3, 3],
    13: [4, 3, 3, 1],
    14: [4, 3, 3, 1],
    15: [4, 3, 3, 2],
    16: [4, 3, 3, 2],
    17: [4, 3, 3, 3, 1],
    18: [4, 3, 3, 3, 1],
    19: [4, 3, 3, 3, 2],
    20: [4, 3, 3, 3, 2],
}

THIRD_CASTER_SLOTS: Dict[int, List[int]] = {
    1: [],
    2: [2],
    3: [3],
    4: [3],
    5: [4, 2],
    6: [4, 2],
    7: [4, 3],
    8: [4, 3],
    9: [4, 3, 2],
    10: [4, 3, 2],
    11: [4, 3, 3],
    12: [4, 3, 3],
    13: [4, 3, 3, 1],
    14: [4, 3, 3, 1],
    15: [4, 3, 3, 2],
    16: [4, 3, 3, 2],
    17: [4, 3, 3, 3, 1],
    18: [4, 3, 3, 3, 1],
    19: [4, 3, 3, 3, 2],
    20: [4, 3, 3, 3, 2],
}

PACT_MAGIC_SLOTS: Dict[int, Dict[str, int]] = {
    1: {"slots": 1, "level": 1},
    2: {"slots": 2, "level": 1},
    3: {"slots": 2, "level": 2},
    4: {"slots": 2, "level": 2},
    5: {"slots": 2, "level": 3},
    6: {"slots": 2, "level": 3},
    7: {"slots": 2, "level": 4},
    8: {"slots": 2, "level": 4},
    9: {"slots": 2, "level": 5},
    10: {"slots": 2, "level": 5},
    11: {"slots": 3, "level": 5},
    12: {"slots": 3, "level": 5},
    13: {"slots": 3, "level": 5},
    14: {"slots": 3, "level": 5},
    15: {"slots": 3, "level": 5},
    16: {"slots": 3, "level": 5},
    17: {"slots": 4, "level": 5},
    18: {"slots": 4, "level": 5},
    19: {"slots": 4, "level": 5},
    20: {"slots": 4, "level": 5},
}

CASTER_TYPE: Dict[str, str] = {
    "bard": "full",
    "cleric": "full",
    "druid": "full",
    "sorcerer": "full",
    "wizard": "full",
    "paladin": "half",
    "ranger": "half",
    "warlock": "pact",
    "barbarian": "none",
    "fighter": "none",
    "monk": "none",
    "rogue": "none",
}


def _effective_caster_level(classes: List[Dict[str, Any]]) -> Tuple[int, Optional[Dict[str, int]]]:
    """Return combined caster level and optional pact magic override."""
    full = half = third = 0
    pact_level = 0
    for cls in classes:
        name = cls.get("name", "").lower()
        lvl = cls.get("level", 0)
        ctype = CASTER_TYPE.get(name, "none")
        if ctype == "full":
            full += lvl
        elif ctype == "half":
            half += lvl
        elif ctype == "third":
            third += lvl
        elif ctype == "pact":
            pact_level = max(pact_level, lvl)

    combined = full + (half // 2) + (third // 3)
    combined = min(20, max(0, combined))
    pact = PACT_MAGIC_SLOTS.get(pact_level) if pact_level else None
    return combined, pact


def calculate_spell_slots(classes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute max spell slots per level for multiclass character."""
    combined, pact = _effective_caster_level(classes)
    if combined == 0 and not pact:
        return {"caster_level": 0, "slots": {}, "pact_magic": None}

    slot_list = FULL_CASTER_SLOTS.get(combined, [])
    slots = {str(i + 1): n for i, n in enumerate(slot_list) if n > 0}
    return {
        "caster_level": combined,
        "slots": slots,
        "pact_magic": pact,
        "version": CLASS_PROGRESSION_VERSION,
    }


def validate_multiclass(
    stats: Dict[str, int],
    current_classes: List[Dict[str, Any]],
    new_class: str,
) -> Dict[str, Any]:
    """Check if character meets prerequisites to multiclass into new_class."""
    key = new_class.lower()
    prereqs = MULTICLASS_PREREQS.get(key)
    if not prereqs:
        return {"valid": False, "class": new_class, "reason": f"Unknown class: {new_class}"}

    existing = {c.get("name", "").lower() for c in current_classes}
    if key in existing:
        return {"valid": True, "class": new_class, "reason": "Already has this class — level it instead"}

    # Multiclassing out also requires meeting prereqs of ALL current classes (simplified: check new only for add)
    if key == "fighter":
        met = stats.get("str", 10) >= 13 or stats.get("dex", 10) >= 13
        detail = "STR 13 or DEX 13"
    else:
        met = all(stats.get(abbr, 10) >= req for abbr, req in prereqs.items())
        detail = ", ".join(f"{k.upper()} {v}" for k, v in prereqs.items())

    return {
        "valid": met,
        "class": new_class,
        "requirements": detail,
        "reason": "Prerequisites met" if met else f"Missing: {detail}",
    }


def build_multiclass_plan(classes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize multiclass build: caster level, slots, class breakdown."""
    total = sum(c.get("level", 0) for c in classes)
    slots_info = calculate_spell_slots(classes)
    return {
        "classes": classes,
        "total_level": total,
        "spell_slots": slots_info,
        "version": CLASS_PROGRESSION_VERSION,
    }


def restore_spell_slots_on_long_rest(classes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return full spell slot pool after long rest."""
    info = calculate_spell_slots(classes)
    used = {k: 0 for k in info.get("slots", {})}
    pact = info.get("pact_magic")
    pact_used = 0
    return {
        "slots": info.get("slots", {}),
        "slots_used": used,
        "pact_magic": pact,
        "pact_slots_used": pact_used,
    }