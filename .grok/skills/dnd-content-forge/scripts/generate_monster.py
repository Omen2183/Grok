#!/usr/bin/env python3
"""
generate_monster.py — Monster Generation Helper for dnd-content-forge

Provides automated monster stat block generation with scaling logic.
Combines rule-based scaling with rich prompt templates for high-quality,
campaign-native monsters (including heavy homebrew support).

Usage:
    python3 generate_monster.py "My Campaign" --theme "Veil Aberration" --cr 5 --difficulty "Hard"
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

try:
    from dnd_state_utils import get_kingdom_state, get_player_character
except ImportError:
    def get_kingdom_state(name): return {}
    def get_player_character(name): return {}


def get_party_level(campaign_name: str) -> int:
    """Try to get average party level from character data."""
    try:
        pc = get_player_character(campaign_name)
        if pc and "level" in pc:
            return int(pc.get("level", 5))
    except Exception:
        pass
    return 5  # Default


def scale_monster_base(cr: int) -> Dict[str, Any]:
    """
    Enhanced 5e-inspired monster scaling.
    Provides solid baselines for HP, AC, attack bonus, damage, and proficiency.
    Designed to be used as strong starting guidance for LLM generation.
    """
    # More accurate HP ranges (midpoint of typical 5e monster HP by CR)
    hp_ranges = {
        0: (1, 6), 1: (20, 30), 2: (40, 55), 3: (60, 80), 4: (80, 110),
        5: (100, 140), 6: (120, 170), 7: (140, 200), 8: (160, 230),
        9: (180, 260), 10: (200, 290), 11: (220, 320), 12: (240, 350),
        13: (260, 380), 14: (280, 410), 15: (300, 440), 16: (320, 470),
        17: (340, 500), 18: (360, 530), 19: (380, 560), 20: (400, 600)
    }
    hp_min, hp_max = hp_ranges.get(cr, (50 + cr * 15, 80 + cr * 20))
    suggested_hp = (hp_min + hp_max) // 2

    # AC scaling (roughly follows 5e monster design)
    ac = 12 + min(cr // 2, 8) + (1 if cr >= 10 else 0)

    # Attack bonus / proficiency
    prof_bonus = 2 + (cr // 4)  # Simplified but reasonable
    attack_bonus = prof_bonus + min(3 + cr // 3, 10)

    # Damage expression (rough average damage per hit)
    if cr <= 2:
        damage_dice = "1d6+2"
        avg_damage = 5
    elif cr <= 5:
        damage_dice = f"{max(1, cr-1)}d6 + {2 + cr//2}"
        avg_damage = 8 + cr
    elif cr <= 10:
        damage_dice = f"{max(2, cr//2)}d8 + {3 + cr//2}"
        avg_damage = 12 + cr * 1.5
    else:
        damage_dice = f"{max(2, cr//3)}d10 + {4 + cr//2}"
        avg_damage = 18 + cr * 1.2

    return {
        "cr": cr,
        "suggested_hp": suggested_hp,
        "hp_range": f"{hp_min}-{hp_max}",
        "ac": ac,
        "attack_bonus": attack_bonus,
        "proficiency_bonus": prof_bonus,
        "damage_dice": damage_dice,
        "avg_damage_per_hit": round(avg_damage),
        "saving_throw_dc": 8 + prof_bonus + min(3 + cr // 4, 8)
    }


def generate_monster_prompt(campaign_name: str, theme: str, cr: int = 5,
                            difficulty: str = "Medium", extra_instructions: str = "") -> str:
    """
    Builds a high-quality monster generation prompt using campaign context + enhanced scaling.
    """
    party_level = get_party_level(campaign_name)
    base = scale_monster_base(cr)

    prompt = f"""You are an expert D&D 5e monster designer creating content for a specific campaign.

**Campaign Context:**
- Party Level: {party_level}
- Target CR: {cr}
- Desired Difficulty: {difficulty}
- Creature Theme: {theme}

**Automated Scaling Baseline (strong guidance — adjust for flavor/balance):**
- Suggested HP: ~{base['suggested_hp']} (typical range {base['hp_range']})
- Suggested AC: {base['ac']}
- Attack Bonus: +{base['attack_bonus']} (Proficiency +{base['proficiency_bonus']})
- Damage per hit: {base['damage_dice']} (avg ~{base['avg_damage_per_hit']})
- Suggested Save DC: {base['saving_throw_dc']}

**Requirements:**
1. Create a **complete, balanced 5e stat block** in clean Markdown.
2. Include all standard sections: 
   - AC, HP, Speed, Ability Scores (STR/DEX/CON/INT/WIS/CHA)
   - Saving Throws, Skills, Vulnerabilities/Resistances/Immunities
   - Senses, Languages, Challenge Rating
   - Traits, Actions, Bonus Actions, Reactions
   - Legendary Actions + Lair Actions if the creature warrants them (especially CR 5+ or boss monsters)
3. Add **1-2 unique flavorful twists or minor homebrew mechanics** that fit the campaign theme and make the monster memorable.
4. Provide short **"Tactics"** and **"Roleplay / Lore Notes"** sections.
5. If this is a significant or recurring monster, suggest 1-2 ways it could connect to ongoing campaign lore or factions.

{extra_instructions}

**Output Format:** Full monster stat block in clean, ready-to-use Markdown (suitable for text or VTT import). Start directly with the monster name as a heading.
"""
    return prompt


def save_stat_block(
    campaign_name: str,
    name: str,
    markdown: str,
    *,
    cr: Optional[int] = None,
) -> Dict[str, Any]:
    """Persist a generated stat block to encounters/ for reuse."""
    from paths import get_campaign_path  # type: ignore

    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in name.lower()).strip("-")
    folder = get_campaign_path(campaign_name) / "encounters"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{safe}.md"
    header = f"# {name}\n"
    if cr is not None:
        header += f"*CR {cr}*\n\n"
    path.write_text(header + markdown.strip() + "\n", encoding="utf-8")
    return {"saved": str(path), "name": name, "cr": cr}


def generate_monster(campaign_name: str, theme: str, cr: int = 5,
                     difficulty: str = "Medium", extra: str = "") -> Dict[str, Any]:
    """
    Main entry point. Returns rich context + prompt for high-quality monster generation.
    Now includes stronger scaling and lore integration suggestions.
    """
    prompt = generate_monster_prompt(campaign_name, theme, cr, difficulty, extra)
    base = scale_monster_base(cr)

    lore_suggestion = (
        f"After generation, consider creating a lore entry in dnd-lore-archivist "
        f"for this {theme} (CR {cr}) so it can recur meaningfully."
    )

    return {
        "campaign": campaign_name,
        "theme": theme,
        "cr": cr,
        "difficulty": difficulty,
        "base_stats": base,
        "generation_prompt": prompt,
        "lore_integration_note": lore_suggestion,
        "usage": "Feed generation_prompt to Grok (or another strong model) to produce the final stat block."
    }


def suggest_encounter_budget(party_level: int, difficulty: str = "Medium", party_size: int = 4) -> Dict[str, Any]:
    """
    Suggests a reasonable XP budget for an encounter based on 5e guidelines.
    Returns budget and rough guidance.
    """
    # Simplified 5e XP thresholds (approximate daily budget / 4-6 encounters)
    xp_per_level = {
        1: 300, 2: 600, 3: 1200, 4: 1700, 5: 2300,
        6: 2900, 7: 3600, 8: 4300, 9: 5100, 10: 5900
    }
    base_xp = xp_per_level.get(party_level, 300 + party_level * 600)

    multipliers = {"Easy": 0.5, "Medium": 1.0, "Hard": 1.5, "Deadly": 2.0}
    budget = int(base_xp * multipliers.get(difficulty, 1.0) * (party_size / 4))

    return {
        "party_level": party_level,
        "difficulty": difficulty,
        "party_size": party_size,
        "suggested_xp_budget": budget,
        "guidance": f"Build an encounter worth roughly {budget} XP. Mix 1-2 significant threats with minions for best pacing."
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced D&D 5e Monster & Encounter Generator for the Grok skill suite"
    )
    parser.add_argument("campaign_name", help="Campaign name (used to pull party level)")
    parser.add_argument("--theme", default="Custom Creature", help="Creature theme or concept")
    parser.add_argument("--cr", type=int, default=5, help="Target Challenge Rating")
    parser.add_argument("--difficulty", default="Medium", choices=["Easy", "Medium", "Hard", "Deadly"])
    parser.add_argument("--extra", default="", help="Additional instructions for the generator")
    parser.add_argument("--encounter", action="store_true", help="Also output an encounter budget suggestion")
    parser.add_argument("--save", metavar="NAME", help="Save stat block markdown from --content file")
    parser.add_argument("--content", help="Markdown stat block body when using --save")

    args = parser.parse_args()

    if args.save:
        if not args.content:
            print(json.dumps({"error": "--content required with --save"}))
            sys.exit(1)
        result = save_stat_block(args.campaign_name, args.save, args.content, cr=args.cr)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    result = generate_monster(args.campaign_name, args.theme, args.cr, args.difficulty, args.extra)

    if args.encounter:
        party_level = get_party_level(args.campaign_name)
        budget = suggest_encounter_budget(party_level, args.difficulty)
        result["encounter_budget"] = budget

    print(json.dumps(result, indent=2))