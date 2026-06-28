#!/usr/bin/env python3
"""Build balanced encounters with XP budgets, enemy mixes, and saveable plans."""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from dnd_state_utils import get_player_character, get_world_state  # noqa: E402
from paths import get_campaign_path  # noqa: E402

# Per-level XP budgets (Medium difficulty, party of 4) — scaled by difficulty & party size
BUDGET_TABLE: Dict[int, Dict[str, int]] = {
    1: {"Easy": 50, "Medium": 75, "Hard": 100, "Deadly": 150},
    2: {"Easy": 100, "Medium": 150, "Hard": 200, "Deadly": 300},
    3: {"Easy": 150, "Medium": 225, "Hard": 400, "Deadly": 600},
    4: {"Easy": 250, "Medium": 375, "Hard": 500, "Deadly": 750},
    5: {"Easy": 375, "Medium": 750, "Hard": 1100, "Deadly": 1700},
    6: {"Easy": 500, "Medium": 1000, "Hard": 1400, "Deadly": 2100},
    7: {"Easy": 600, "Medium": 1200, "Hard": 1700, "Deadly": 2500},
    8: {"Easy": 750, "Medium": 1500, "Hard": 2100, "Deadly": 3200},
    9: {"Easy": 900, "Medium": 1800, "Hard": 2600, "Deadly": 3900},
    10: {"Easy": 1100, "Medium": 2200, "Hard": 3200, "Deadly": 4800},
}

# Approximate XP per CR (single creature)
CR_XP = {
    0: 10, 0.125: 25, 0.25: 50, 0.5: 100,
    1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800,
    6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900,
}

TERRAIN_TAGS = [
    "open field", "dense forest", "ruined keep", "cave system",
    "urban alley", "swamp", "mountain pass", "throne room",
]

ENEMY_ARCHETYPES = [
    {"role": "bruiser", "cr_offset": 1, "count_weight": 1},
    {"role": "skirmisher", "cr_offset": -1, "count_weight": 3},
    {"role": "controller", "cr_offset": 0, "count_weight": 1},
    {"role": "minion", "cr_offset": -2, "count_weight": 4},
]


def get_party_level(campaign_name: str) -> int:
    pc = get_player_character(campaign_name)
    return int(pc.get("level", 5))


def calculate_budget(
    party_level: int,
    difficulty: str = "Medium",
    party_size: int = 4,
) -> int:
    row = BUDGET_TABLE.get(min(party_level, 10), BUDGET_TABLE[5])
    base = row.get(difficulty, row["Medium"])
    return int(base * (party_size / 4))


def _cr_for_level(party_level: int, offset: int = 0) -> float:
    cr = max(0.125, min(10, party_level + offset))
    return cr


def suggest_enemy_mix(
    party_level: int,
    xp_budget: int,
    *,
    theme: str = "generic",
) -> List[Dict[str, Any]]:
    """Propose a creature mix that roughly fits the XP budget."""
    enemies: List[Dict[str, Any]] = []
    remaining = xp_budget
    picks = random.sample(ENEMY_ARCHETYPES, k=min(3, len(ENEMY_ARCHETYPES)))

    for arch in picks:
        if remaining <= 0:
            break
        cr = _cr_for_level(party_level, arch["cr_offset"])
        xp_each = CR_XP.get(cr, CR_XP.get(int(cr), 200))
        count = min(arch["count_weight"], max(1, remaining // max(xp_each, 1)))
        if count < 1:
            continue
        spent = count * xp_each
        if spent > remaining and count > 1:
            count = max(1, remaining // xp_each)
            spent = count * xp_each
        enemies.append({
            "role": arch["role"],
            "cr": cr,
            "count": count,
            "xp_each": xp_each,
            "xp_total": count * xp_each,
            "name_hint": f"{theme} {arch['role']}".strip(),
        })
        remaining -= spent

    return enemies


def build_encounter(
    campaign_name: str,
    *,
    theme: str = "ambush",
    difficulty: str = "Medium",
    party_size: int = 4,
) -> Dict[str, Any]:
    """Build a full encounter plan with budget, enemies, terrain, and DM prompt."""
    party_level = get_party_level(campaign_name)
    world = get_world_state(campaign_name)
    budget = calculate_budget(party_level, difficulty, party_size)
    enemies = suggest_enemy_mix(party_level, budget, theme=theme)
    total_xp = sum(e["xp_total"] for e in enemies)
    terrain = random.choice(TERRAIN_TAGS)
    mode = world.get("mode", "tabletop")

    prompt = f"""Design a {difficulty} encounter for a level {party_level} party ({party_size} PCs).

**Theme:** {theme}
**Location context:** {world.get('current_location', 'unknown')}
**Mode:** {mode}
**Terrain:** {terrain}
**XP budget:** ~{budget} (planned total ~{total_xp})

**Suggested enemy mix:**
{json.dumps(enemies, indent=2)}

Provide:
1. Named creatures with quick stat references (AC, HP, main attack)
2. Terrain features that matter in combat
3. Tactics for intelligent enemies
4. Optional reward or story hook tied to the campaign
"""

    return {
        "campaign": campaign_name,
        "party_level": party_level,
        "difficulty": difficulty,
        "party_size": party_size,
        "xp_budget": budget,
        "xp_planned": total_xp,
        "theme": theme,
        "terrain": terrain,
        "location": world.get("current_location"),
        "enemies": enemies,
        "generation_prompt": prompt,
        "mode": mode,
    }


def save_encounter_plan(campaign_name: str, plan: Dict[str, Any], *, name: Optional[str] = None) -> Dict[str, Any]:
    folder = get_campaign_path(campaign_name) / "encounters"
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = (name or plan.get("theme", "encounter")).lower()
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in slug).strip("-")
    path = folder / f"encounter_{slug}_{stamp}.json"
    path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return {"saved": str(path), "name": slug}


def difficulty_report(
    campaign_name: str,
    *,
    party_level: Optional[int] = None,
    party_size: int = 4,
    enemy_cr: float = 1.0,
    enemy_count: int = 4,
) -> Dict[str, Any]:
    """Compare party level/HP band to a proposed encounter."""
    level = party_level or get_party_level(campaign_name)
    pc = get_player_character(campaign_name)
    hp = pc.get("hit_points", {})
    budget = calculate_budget(level, "Medium", party_size)
    xp_each = CR_XP.get(enemy_cr, CR_XP.get(int(enemy_cr), 200))
    total_xp = int(xp_each * enemy_count)
    ratio = total_xp / max(budget, 1)
    if ratio < 0.5:
        band = "trivial"
    elif ratio < 0.85:
        band = "easy"
    elif ratio < 1.15:
        band = "medium"
    elif ratio < 1.5:
        band = "hard"
    else:
        band = "deadly"
    return {
        "party_level": level,
        "party_hp": f"{hp.get('current', '?')}/{hp.get('max', '?')}",
        "medium_budget": budget,
        "enemy_cr": enemy_cr,
        "enemy_count": enemy_count,
        "encounter_xp": total_xp,
        "difficulty_band": band,
        "advice": f"Encounter looks **{band}** for level {level} party of {party_size}.",
    }


def list_encounters(campaign_name: str) -> List[Dict[str, Any]]:
    folder = get_campaign_path(campaign_name) / "encounters"
    if not folder.exists():
        return []
    results = []
    for f in sorted(folder.glob("encounter_*.json"), reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results.append({"file": f.name, "theme": data.get("theme"), "xp_budget": data.get("xp_budget")})
        except (json.JSONDecodeError, OSError):
            continue
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="D&D encounter builder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build")
    p_build.add_argument("campaign")
    p_build.add_argument("--theme", default="ambush")
    p_build.add_argument("--difficulty", default="Medium", choices=["Easy", "Medium", "Hard", "Deadly"])
    p_build.add_argument("--party-size", type=int, default=4)
    p_build.add_argument("--save", action="store_true")

    p_list = sub.add_parser("list")
    p_list.add_argument("campaign")

    p_diff = sub.add_parser("difficulty-report")
    p_diff.add_argument("campaign")
    p_diff.add_argument("--cr", type=float, default=1.0)
    p_diff.add_argument("--count", type=int, default=4)
    p_diff.add_argument("--party-size", type=int, default=4)

    args = parser.parse_args()

    if args.cmd == "build":
        result = build_encounter(
            args.campaign,
            theme=args.theme,
            difficulty=args.difficulty,
            party_size=args.party_size,
        )
        if args.save:
            result["save"] = save_encounter_plan(args.campaign, result, name=args.theme)
    elif args.cmd == "list":
        result = {"encounters": list_encounters(args.campaign)}
    elif args.cmd == "difficulty-report":
        result = difficulty_report(
            args.campaign,
            party_size=args.party_size,
            enemy_cr=args.cr,
            enemy_count=args.count,
        )
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()