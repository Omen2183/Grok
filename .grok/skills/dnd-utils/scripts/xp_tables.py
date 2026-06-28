"""5e XP thresholds and level-up helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional  # noqa: F401 — Dict used by DOMAIN_XP_MILESTONES

# Cumulative XP required to reach each level (index 0 = level 1)
XP_BY_LEVEL: List[int] = [
    0,
    300,
    900,
    2700,
    6500,
    14000,
    23000,
    34000,
    48000,
    64000,
    85000,
    100000,
    120000,
    140000,
    165000,
    195000,
    225000,
    265000,
    305000,
    355000,
]

PROFICIENCY_BY_LEVEL: List[int] = [
    2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6,
]

# Suggested domain milestone XP awards (kingdom mode — DM may override)
DOMAIN_XP_MILESTONES: Dict[str, int] = {
    "project_complete": 150,
    "trade_route": 100,
    "faction_alliance": 120,
    "territory_expansion": 200,
    "crisis_resolved": 175,
    "festival": 50,
}


def suggest_domain_xp(milestone: str) -> Dict[str, Any]:
    key = milestone.lower().replace(" ", "_").replace("-", "_")
    amount = DOMAIN_XP_MILESTONES.get(key)
    return {
        "milestone": milestone,
        "suggested_xp": amount,
        "known_milestones": sorted(DOMAIN_XP_MILESTONES.keys()),
        "note": "Award via session-scribe award-xp or end-session --xp",
    }


def level_from_xp(xp: int) -> int:
    """Return character level for cumulative XP (1–20)."""
    level = 1
    for idx, threshold in enumerate(XP_BY_LEVEL, start=1):
        if xp >= threshold:
            level = idx
    return min(level, 20)


def xp_to_next_level(xp: int) -> Optional[int]:
    """XP still needed to reach the next level, or None at level 20."""
    current = level_from_xp(xp)
    if current >= 20:
        return None
    return XP_BY_LEVEL[current] - xp


def check_level_up(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare stored level vs XP-derived level.
    Returns level-up info without mutating the character.
    """
    xp = int(character.get("xp", 0))
    stored_level = int(character.get("level", 1))
    derived_level = level_from_xp(xp)
    pending = max(0, derived_level - stored_level)
    return {
        "stored_level": stored_level,
        "derived_level": derived_level,
        "xp": xp,
        "pending_level_ups": pending,
        "level_up_available": pending > 0,
        "xp_to_next": xp_to_next_level(xp),
        "proficiency_bonus": PROFICIENCY_BY_LEVEL[min(derived_level, 20) - 1],
    }