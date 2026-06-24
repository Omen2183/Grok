#!/usr/bin/env python3
"""
dnd-character-manager
Core script for managing player character sheets persistently.

Integrates with:
- dnd_state_utils (for campaign paths and state handling)
- combat-assistant (for HP/condition/death save sync)
- persistent-dm (orchestration)

Version 0.4 — Phase 3 enhancements:
- Lightweight multi-character / companion support
- Basic level-up suggestion system (class features & feat ideas)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"))
try:
    from bootstrap import ensure_utils_importable
    ensure_utils_importable()
    from dnd_state_utils import get_campaign_path, load_world_state, update_world_state
except ImportError:
    from paths import get_campaign_path  # type: ignore

    def load_world_state(campaign_name: str) -> Dict:
        return {}

    def update_world_state(campaign_name: str, updates: Dict) -> Dict:
        return {}


CHARACTER_JSON = "player_character.json"
CHARACTER_MD = "player_character.md"


def get_character_paths(campaign_name: str) -> Dict[str, Path]:
    """Return paths to character data files."""
    base = get_campaign_path(campaign_name) / "state"
    return {
        "json": base / CHARACTER_JSON,
        "md": base / CHARACTER_MD,
    }


def load_character(campaign_name: str) -> Dict[str, Any]:
    """Load the current character sheet from JSON."""
    paths = get_character_paths(campaign_name)
    if paths["json"].exists():
        with open(paths["json"], "r", encoding="utf-8") as f:
            return json.load(f)
    return create_default_character()


def save_character(campaign_name: str, character_data: Dict[str, Any]) -> None:
    """Save character data to JSON and regenerate markdown view."""
    paths = get_character_paths(campaign_name)
    paths["json"].parent.mkdir(parents=True, exist_ok=True)

    with open(paths["json"], "w", encoding="utf-8") as f:
        json.dump(character_data, f, indent=2, ensure_ascii=False)

    # TODO: Generate human-readable markdown version
    generate_character_markdown(campaign_name, character_data)


def create_default_character() -> Dict[str, Any]:
    """Create a minimal default character structure."""
    return {
        "name": "Unnamed Adventurer",
        "race": "Human",
        "classes": [{"name": "Fighter", "level": 1}],
        "background": "Folk Hero",
        "stats": {"str": 15, "dex": 14, "con": 13, "int": 10, "wis": 12, "cha": 8},
        "proficiency_bonus": 2,
        "hit_points": {"current": 12, "max": 12, "temp": 0},
        "death_saves": {"successes": 0, "failures": 0},
        "conditions": [],
        "inventory": [],
        "attunement": [],
        "attunement_max": 3,   # Configurable for homebrew (default 5e = 3)
        "feats": [],
        "xp": 0,
        "level": 1,
        "notes": "",
        "homebrew": {}
    }


def generate_character_markdown(campaign_name: str, character: Dict[str, Any]) -> str:
    """Generate a significantly richer Markdown character sheet with derived stats."""
    name = character.get("name", "Unnamed Character")
    race = character.get("race", "Unknown")
    background = character.get("background", "—")
    level = character.get("level", 1)
    prof = character.get("proficiency_bonus", 2)

    # Class breakdown
    classes = character.get("classes", [])
    class_str = " / ".join([f"{c.get('name', 'Class')} {c.get('level', 0)}" for c in classes])

    # Ability Scores + Modifiers
    stats = character.get("stats", {})
    modifiers = character.get("ability_modifiers", {})
    stats_lines = []
    for k in ["str", "dex", "con", "int", "wis", "cha"]:
        score = stats.get(k, 10)
        mod = modifiers.get(k, get_ability_modifier(score))
        mod_str = f"+{mod}" if mod >= 0 else str(mod)
        stats_lines.append(f"**{k.upper()}:** {score} ({mod_str})")
    stats_block = "\n".join(stats_lines)

    # Saving Throws
    saves = character.get("saving_throws", {})
    saves_lines = []
    for ability in ["str", "dex", "con", "int", "wis", "cha"]:
        bonus = saves.get(ability, get_ability_modifier(stats.get(ability, 10)))
        bonus_str = f"+{bonus}" if bonus >= 0 else str(bonus)
        saves_lines.append(f"**{ability.upper()}:** {bonus_str}")
    saves_block = " | ".join(saves_lines)

    # Skills (basic view)
    skills = character.get("skills", {})
    if skills:
        skills_lines = "\n".join([f"- **{k.title()}:** {v:+d}" for k, v in skills.items()])
    else:
        skills_lines = "_No skill bonuses calculated yet._"

    # Hit Points
    hp = character.get("hit_points", {})
    hp_line = f"**{hp.get('current', 0)}** / {hp.get('max', 0)} (Temp: {hp.get('temp', 0)})"

    # Death Saves
    ds = character.get("death_saves", {"successes": 0, "failures": 0})
    ds_line = f"Successes: {ds.get('successes', 0)} | Failures: {ds.get('failures', 0)}"

    # Conditions
    conditions = ", ".join(character.get("conditions", [])) or "None"

    # Feats
    feats = character.get("feats", [])
    if feats:
        feat_lines = "\n".join([f"- **{f.get('name', 'Feat')}**: {f.get('description', '')}" for f in feats])
    else:
        feat_lines = "_No feats recorded yet._"

    # Level History
    history = character.get("level_history", [])[-5:]
    if history:
        history_lines = "\n".join([
            f"- Level {h.get('from_level')} → {h.get('to_level')} ({h.get('class_leveled')}) | +{h.get('hp_gained')} HP ({h.get('hp_method', 'average')})"
            for h in history
        ])
    else:
        history_lines = "_No level-ups recorded yet._"

    # Attunement
    attunement_max = character.get("attunement_max", 3)
    attuned_count = len(character.get("attunement", []))
    attuned_names = ', '.join([a.get('name', '') for a in character.get('attunement', [])]) or 'None'

    # Critical state warning
    status = character.get("status", "Alive")
    if status.lower() in ["dying", "dead"]:
        critical_warning = f"\n⚠️ **CRITICAL STATE** — This character is currently **{status}**. Death saves are active."
    else:
        critical_warning = ""

    md = f"""# {name}

**Race:** {race} | **Background:** {background}  
**Total Level:** {level} | **Proficiency Bonus:** +{prof}

**Classes:** {class_str}

## Ability Scores
{stats_block}

## Saving Throws
{saves_block}

## Skills (Calculated)
{skills_lines}

## Hit Points
{hp_line}

## Death Saves
{ds_line}

**Status:** {character.get('status', 'Alive')}
{critical_warning}

## Conditions
{conditions}

## Feats & Features
{feat_lines}

## Level History (Recent)
{history_lines}

## Inventory & Attunement
{len(character.get('inventory', []))} items tracked  
**Attuned ({attuned_count}/{attunement_max}):** {attuned_names}

---
*Generated by dnd-character-manager v0.3 • Edit JSON directly for full control. Run recalculate_derived_stats() after major changes.*
"""

    paths = get_character_paths(campaign_name)
    with open(paths["md"], "w", encoding="utf-8") as f:
        f.write(md)
    return md


def level_up(
    campaign_name: str,
    levels: int = 1,
    class_name: Optional[str] = None,
    hp_increase_method: str = "average",
    con_modifier: Optional[int] = None
) -> Dict[str, Any]:
    """
    Improved level-up handler with multiclass support and HP calculation.

    Args:
        campaign_name: Name of the campaign
        levels: Number of levels to gain (usually 1)
        class_name: Which class to level up (for multiclass). If None, levels the first/only class.
        hp_increase_method: "average" (recommended) or "roll" (player can adjust manually)
        con_modifier: Constitution modifier. If not provided, tries to calculate from stats.

    Returns:
        Updated character dictionary
    """
    char = load_character(campaign_name)

    # Determine which class to level
    if not char.get("classes"):
        char["classes"] = [{"name": "Fighter", "level": 0}]

    if class_name:
        # Find existing class or add new one (multiclassing)
        target_class = next((c for c in char["classes"] if c["name"].lower() == class_name.lower()), None)
        if not target_class:
            target_class = {"name": class_name, "level": 0}
            char["classes"].append(target_class)
    else:
        target_class = char["classes"][0]  # Default to first class

    old_total_level = char.get("level", 1)
    new_total_level = old_total_level + levels

    # Update total level and the specific class level
    char["level"] = new_total_level
    target_class["level"] = target_class.get("level", 0) + levels

    # Update Proficiency Bonus (correct 5e formula)
    char["proficiency_bonus"] = 2 + ((new_total_level - 1) // 4)

    # Calculate HP increase
    if con_modifier is None:
        con_score = char.get("stats", {}).get("con", 10)
        con_modifier = (con_score - 10) // 2

    # Hit die by class (expandable)
    hit_die_map = {
        "barbarian": 12, "fighter": 10, "paladin": 10, "ranger": 10,
        "bard": 8, "cleric": 8, "druid": 8, "monk": 8, "rogue": 8, "warlock": 8,
        "sorcerer": 6, "wizard": 6
    }
    class_key = target_class["name"].lower()
    hit_die = hit_die_map.get(class_key, 8)  # Default to d8 if unknown

    average_per_level = (hit_die // 2) + 1 + con_modifier

    if hp_increase_method == "average":
        hp_increase = average_per_level * levels
        hp_roll_info = None
    else:
        # Rolling mode: do not apply yet. Return guidance so caller can prompt user.
        hp_increase = 0  # Will be applied later via confirm function
        hp_roll_info = {
            "hit_die": hit_die,
            "con_modifier": con_modifier,
            "average_per_level": average_per_level,
            "levels_gained": levels,
            "total_average": average_per_level * levels,
            "message": f"Roll {levels}d{hit_die} + ({con_modifier} Con mod per level). Average total: {average_per_level * levels}"
        }

    # Apply HP increase (only for average mode)
    if hp_increase_method == "average":
        char["hit_points"]["max"] = char["hit_points"].get("max", 0) + hp_increase
        char["hit_points"]["current"] = char["hit_points"].get("current", 0) + hp_increase

    # Track ASI / Feat eligibility (standard 5e levels)
    asi_levels = {4, 8, 12, 16, 19}
    new_asi_levels = [old_total_level + i for i in range(1, levels + 1) if (old_total_level + i) in asi_levels]

    if new_asi_levels:
        char.setdefault("notes", "")
        char["notes"] += f"\n[Level Up] ASI or Feat available at level(s): {new_asi_levels}"

    # Record level-up event (simple history)
    char.setdefault("level_history", [])
    char["level_history"].append({
        "from_level": old_total_level,
        "to_level": new_total_level,
        "class_leveled": target_class["name"],
        "hp_gained": hp_increase,
        "hp_method": hp_increase_method,
        "asi_available": bool(new_asi_levels)
    })

    save_character(campaign_name, char)

    if hp_roll_info:
        return {
            "status": "awaiting_hp_roll",
            "character": char,
            "roll_info": hp_roll_info,
            "message": hp_roll_info["message"]
        }

    # Recalculate derived stats after leveling
    recalculate_derived_stats(campaign_name)

    # Phase 3: Attach level-up suggestions
    suggestions = suggest_level_up_options(campaign_name)
    return {
        "character": char,
        "suggestions": suggestions
    }


def apply_level_up_hp_roll(campaign_name: str, rolled_total: int) -> Dict[str, Any]:
    """
    Apply a user-rolled HP total after level_up(..., hp_increase_method="roll") returned awaiting_hp_roll.
    """
    char = load_character(campaign_name)
    char["hit_points"]["max"] = char["hit_points"].get("max", 0) + rolled_total
    char["hit_points"]["current"] = char["hit_points"].get("current", 0) + rolled_total

    # Update the last level_history entry with actual HP gained
    if char.get("level_history"):
        char["level_history"][-1]["hp_gained"] = rolled_total
        char["level_history"][-1]["hp_method"] = "rolled"

    save_character(campaign_name, char)
    return char


def add_feat(campaign_name: str, feat_name: str, description: str = "", effects: Dict = None) -> Dict[str, Any]:
    """Add a feat or homebrew feature to the character."""
    char = load_character(campaign_name)
    feat_entry = {
        "name": feat_name,
        "description": description,
        "effects": effects or {}
    }
    char.setdefault("feats", []).append(feat_entry)
    save_character(campaign_name, char)
    recalculate_derived_stats(campaign_name)
    return char


def record_asi_or_feat(
    campaign_name: str,
    level: int,
    choice: str,
    details: str = ""
) -> Dict[str, Any]:
    """
    Record an Ability Score Improvement or Feat choice made at a specific level.
    This helps track progression choices over long campaigns.
    """
    char = load_character(campaign_name)
    char.setdefault("asi_choices", [])
    char["asi_choices"].append({
        "level": level,
        "choice": choice,      # e.g. "Feat: Great Weapon Master" or "ASI: +2 Strength"
        "details": details
    })
    save_character(campaign_name, char)
    return char


def update_inventory(campaign_name: str, action: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced inventory management.

    Supported actions:
    - "add"       : Add item to inventory
    - "remove"    : Remove item by name
    - "attune"    : Attune to an item (respects 3-item limit)
    - "unattune"  : Remove from attunement list
    - "equip"     : Mark item as equipped (simple flag)
    """
    char = load_character(campaign_name)
    inventory = char.setdefault("inventory", [])
    attunement = char.setdefault("attunement", [])

    item_name = item.get("name", "")

    if action == "add":
        # Avoid duplicates by name for simplicity
        if not any(i.get("name") == item_name for i in inventory):
            inventory.append(item)

    elif action == "remove":
        inventory = [i for i in inventory if i.get("name") != item_name]
        char["inventory"] = inventory
        # Also remove from attunement if present
        attunement = [a for a in attunement if a.get("name") != item_name]
        char["attunement"] = attunement

    elif action == "attune":
        attunement_max = char.get("attunement_max", 3)
        if len(attunement) >= attunement_max:
            print(f"Warning: Already at attunement limit ({attunement_max}). Cannot attune more items.")
        elif not any(a.get("name") == item_name for a in attunement):
            attunement.append(item)

    elif action == "unattune":
        attunement = [a for a in attunement if a.get("name") != item_name]
        char["attunement"] = attunement

    elif action == "equip":
        for i in inventory:
            if i.get("name") == item_name:
                i["equipped"] = True

    save_character(campaign_name, char)
    return char


def get_attuned_items(campaign_name: str) -> list:
    """Return list of currently attuned items."""
    char = load_character(campaign_name)
    return char.get("attunement", [])


def set_attunement_max(campaign_name: str, new_max: int) -> Dict[str, Any]:
    """
    Set a new attunement maximum (homebrew friendly).
    Example: set_attunement_max("MyCampaign", 4) for a homebrew boon.
    """
    if new_max < 1:
        new_max = 1
    char = load_character(campaign_name)
    char["attunement_max"] = new_max
    save_character(campaign_name, char)
    return char


def get_ability_modifier(score: int) -> int:
    """Calculate standard 5e ability modifier."""
    return (score - 10) // 2


def recalculate_derived_stats(campaign_name: str) -> Dict[str, Any]:
    """
    Recalculate ability modifiers, saving throws, and basic skill bonuses.
    This is a foundational hook for Phase 2. Future versions can expand it significantly.
    """
    char = load_character(campaign_name)
    stats = char.get("stats", {})
    prof = char.get("proficiency_bonus", 2)

    # Ability modifiers
    modifiers = {k: get_ability_modifier(v) for k, v in stats.items()}
    char["ability_modifiers"] = modifiers

    # Basic saving throws (assume proficient in two common saves for demo; can be expanded)
    # For now, we store raw bonuses. Full proficiency tracking can be added later.
    saving_throws = {}
    for ability in ["str", "dex", "con", "int", "wis", "cha"]:
        mod = modifiers.get(ability, 0)
        # Placeholder: mark common saves. In real use, this would come from class data.
        saving_throws[ability] = mod + prof if ability in ["str", "con"] else mod

    char["saving_throws"] = saving_throws

    # Basic skills example (can be expanded with actual proficient skills)
    skills = {
        "athletics": modifiers.get("str", 0) + prof,
        "acrobatics": modifiers.get("dex", 0),
        "stealth": modifiers.get("dex", 0),
        "perception": modifiers.get("wis", 0) + prof,
        "insight": modifiers.get("wis", 0),
    }
    char["skills"] = skills

    save_character(campaign_name, char)
    return char


def get_inventory_summary(campaign_name: str) -> str:
    """Return a concise inventory summary."""
    char = load_character(campaign_name)
    inv = char.get("inventory", [])
    attuned = char.get("attunement", [])

    if not inv:
        return "Inventory is empty."

    lines = [f"- {item.get('name', 'Unknown')} ({item.get('type', 'item')})" for item in inv]
    attuned_names = [a.get("name") for a in attuned]

    summary = "\n".join(lines)
    summary += f"\n\nAttuned ({len(attuned)}/3): {', '.join(attuned_names) if attuned_names else 'None'}"
    return summary


def update_death_saves(campaign_name: str, success: Optional[bool] = None, reset: bool = False) -> Dict[str, Any]:
    """
    Track death saving throws with automatic stabilization/death detection.

    - 3 successes = character stabilizes (but remains at 0 HP)
    - 3 failures = character dies
    """
    char = load_character(campaign_name)
    ds = char.setdefault("death_saves", {"successes": 0, "failures": 0, "status": "stable"})

    if reset:
        ds["successes"] = 0
        ds["failures"] = 0
        ds["status"] = "stable"
    elif success is True:
        ds["successes"] += 1
        if ds["successes"] >= 3:
            ds["status"] = "stable"
    elif success is False:
        ds["failures"] += 1
        if ds["failures"] >= 3:
            ds["status"] = "dead"

    # Update overall character status if dying
    if ds["status"] == "dead":
        char["status"] = "Dead"
    elif ds.get("failures", 0) > 0 and ds.get("successes", 0) < 3:
        ds["status"] = "dying"
        char["status"] = "Dying"
    else:
        if ds.get("status") != "dead":
            ds["status"] = "stable"

    save_character(campaign_name, char)
    return char


def apply_death_save(campaign_name: str, success: bool) -> Dict[str, Any]:
    """Convenience function to apply a single death save roll."""
    return update_death_saves(campaign_name, success=success)


def stabilize_character(campaign_name: str) -> Dict[str, Any]:
    """Manually stabilize a dying character (e.g. via healing or successful death saves)."""
    char = load_character(campaign_name)
    ds = char.setdefault("death_saves", {"successes": 0, "failures": 0, "status": "stable"})
    ds["successes"] = 3
    ds["failures"] = 0
    ds["status"] = "stable"
    char["status"] = "Stable (0 HP)"
    save_character(campaign_name, char)
    return char


def handle_character_downed(campaign_name: str) -> Dict[str, Any]:
    """
    Called when a character drops to 0 HP (typically triggered from combat-assistant or persistent-dm).
    Initializes or resets death save tracking and sets status to 'Dying'.
    """
    char = load_character(campaign_name)
    ds = char.setdefault("death_saves", {"successes": 0, "failures": 0, "status": "dying"})
    ds["successes"] = 0
    ds["failures"] = 0
    ds["status"] = "dying"
    char["status"] = "Dying"
    save_character(campaign_name, char)
    return char


def apply_healing_while_dying(campaign_name: str, amount: int) -> Dict[str, Any]:
    """
    Apply healing to a dying character.
    - If healing brings HP above 0, the character stabilizes and death saves are reset.
    - If still at or below 0 HP, they remain dying.
    """
    char = load_character(campaign_name)
    hp = char.setdefault("hit_points", {"current": 0, "max": 0, "temp": 0})
    ds = char.setdefault("death_saves", {"successes": 0, "failures": 0, "status": "stable"})

    hp["current"] += amount

    if hp.get("current", 0) > 0:
        # Character is no longer dying
        ds["successes"] = 0
        ds["failures"] = 0
        ds["status"] = "stable"
        char["status"] = "Alive"
    else:
        ds["status"] = "dying"
        char["status"] = "Dying"

    save_character(campaign_name, char)
    return char


def get_death_save_status(campaign_name: str) -> Dict[str, Any]:
    """Return current death save state and overall character status."""
    char = load_character(campaign_name)
    return {
        "death_saves": char.get("death_saves", {"successes": 0, "failures": 0, "status": "stable"}),
        "character_status": char.get("status", "Alive")
    }


def reset_death_saves(campaign_name: str) -> Dict[str, Any]:
    """Fully reset death saves and set character to stable."""
    char = load_character(campaign_name)
    ds = char.setdefault("death_saves", {"successes": 0, "failures": 0, "status": "stable"})
    ds["successes"] = 0
    ds["failures"] = 0
    ds["status"] = "stable"
    char["status"] = "Alive"
    save_character(campaign_name, char)
    return char


def is_character_dying(campaign_name: str) -> bool:
    """Quick check if the character is currently dying."""
    char = load_character(campaign_name)
    status = char.get("status", "Alive")
    ds_status = char.get("death_saves", {}).get("status", "stable")
    return status.lower() == "dying" or ds_status == "dying"


def is_character_dead(campaign_name: str) -> bool:
    """Quick check if the character is dead."""
    char = load_character(campaign_name)
    status = char.get("status", "Alive")
    ds_status = char.get("death_saves", {}).get("status", "stable")
    return status.lower() == "dead" or ds_status == "dead"


def sync_character_status(campaign_name: str) -> Dict[str, Any]:
    """
    Ensures the top-level 'status' field is consistent with the current death_saves state.
    Call this after external updates (e.g. from combat-assistant) to keep state clean.
    """
    char = load_character(campaign_name)
    ds = char.get("death_saves", {"successes": 0, "failures": 0, "status": "stable"})
    ds_status = ds.get("status", "stable")

    if ds_status == "dead":
        char["status"] = "Dead"
    elif ds_status == "dying":
        char["status"] = "Dying"
    elif ds.get("successes", 0) >= 3:
        char["status"] = "Stable (0 HP)"
    else:
        if char.get("status") in ["Dying", "Dead"]:
            char["status"] = "Alive"

    save_character(campaign_name, char)
    return char


def get_character_summary(campaign_name: str) -> str:
    """Return a concise summary suitable for mobile or quick reference."""
    char = load_character(campaign_name)
    status = char.get("status", "Alive")
    base = (
        f"{char.get('name')} — "
        f"Level {char.get('level')} "
        f"{char.get('race')} "
        f"{'/'.join([c['name'] for c in char.get('classes', [])])}"
    )
    if status.lower() not in ["alive", "stable"]:
        base += f" [{status}]"
    return base


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="D&D character manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_summary = sub.add_parser("summary")
    p_summary.add_argument("campaign")

    p_level = sub.add_parser("level-up")
    p_level.add_argument("campaign")
    p_level.add_argument("--levels", type=int, default=1)
    p_level.add_argument("--class")

    p_inv = sub.add_parser("inventory")
    p_inv.add_argument("campaign")
    p_inv.add_argument("action", choices=["add", "remove", "attune", "unattune"])
    p_inv.add_argument("--name", required=True)
    p_inv.add_argument("--type", default="item")

    p_ds = sub.add_parser("death-save")
    p_ds.add_argument("campaign")
    p_ds.add_argument("result", choices=["success", "failure"])

    p_export = sub.add_parser("export")
    p_export.add_argument("campaign")

    args = parser.parse_args()

    if args.cmd == "summary":
        print(get_character_summary(args.campaign))
    elif args.cmd == "level-up":
        result = level_up(args.campaign, levels=args.levels, class_name=args.class)
        print(json.dumps(result, indent=2))
    elif args.cmd == "inventory":
        item = {"name": args.name, "type": args.type}
        print(json.dumps(update_inventory(args.campaign, args.action, item), indent=2))
    elif args.cmd == "death-save":
        success = args.result == "success"
        print(json.dumps(apply_death_save(args.campaign, success), indent=2))
    elif args.cmd == "export":
        char = load_character(args.campaign)
        md = generate_character_markdown(args.campaign, char)
        print(md)


if __name__ == "__main__":
    run_cli()

# ============================================================
# PHASE 3: Lightweight Multi-Character & Level-up Suggestions
# ============================================================

def suggest_level_up_options(campaign_name: str) -> Dict[str, Any]:
    """
    Provide smarter level-up suggestions.
    Includes ASI recommendations, feat ideas, and subclass hints.
    """
    char = load_character(campaign_name)
    classes = char.get("classes", [])
    level = char.get("level", 1)
    next_level = level + 1
    stats = char.get("stats", {})
    existing_feats = [f.get("name", "").lower() for f in char.get("feats", [])]

    suggestions = {
        "next_level": next_level,
        "asi_available": next_level in [4, 8, 12, 16, 19],
        "recommended_asi": None,
        "recommended_path": "ASI" if next_level in [4, 8, 12, 16, 19] else "Feat or Class Feature",
        "feat_ideas": [],
        "subclass_hint": None,
        "notes": ""
    }

    # Multiclass-aware primary class detection
    if len(classes) > 1:
        # For multiclass, suggest based on the highest level class or overall needs
        primary_class = max(classes, key=lambda c: c.get("level", 0))["name"].lower()
        suggestions["notes"] = "Multiclass detected. Suggestions prioritize your highest-level class."
    else:
        primary_class = classes[0]["name"].lower() if classes else "fighter"

    # Recommend strongest stat for ASI, with some intelligence
    if suggestions["asi_available"]:
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        main_stat = sorted_stats[0][0] if sorted_stats else "str"
        con_score = stats.get("con", 10)

        # Suggest Resilient if Con is low
        if con_score < 14 and "resilient" not in str(existing_feats):
            suggestions["recommended_asi"] = "+1 Con + Resilient (Con) feat (strong defensive choice)"
        else:
            suggestions["recommended_asi"] = f"+2 to {main_stat.upper()} (or a half-feat)"

    # Class-based feat suggestions (avoid duplicates)
    feat_suggestions = {
        "fighter": ["Great Weapon Master", "Polearm Master", "Sentinel", "Martial Adept"],
        "rogue": ["Skilled", "Alert", "Mobile", "Sharpshooter"],
        "wizard": ["War Caster", "Resilient (Con)", "Spell Sniper", "Elemental Adept"],
        "cleric": ["War Caster", "Resilient (Wis)", "Heavy Armor Master"],
        "barbarian": ["Great Weapon Master", "Tavern Brawler", "Resilient (Con)"],
        "ranger": ["Sharpshooter", "Crossbow Expert", "Mobile"],
        "paladin": ["Great Weapon Master", "Sentinel", "War Caster"],
        "sorcerer": ["War Caster", "Metamagic Adept", "Resilient (Con)"],
        "warlock": ["War Caster", "Resilient (Con)", "Eldritch Adept"],
        "bard": ["War Caster", "Resilient (Cha)", "Skilled"],
        "druid": ["War Caster", "Resilient (Wis)", "Elemental Adept"],
        "monk": ["Mobile", "Alert", "Resilient (Dex)"]
    }

    ideas = feat_suggestions.get(primary_class, ["War Caster", "Resilient", "Alert", "Skilled"])
    suggestions["feat_ideas"] = [f for f in ideas if f.lower() not in existing_feats][:4]

    # Subclass hints at common levels
    if next_level in [3, 6, 10, 14]:
        suggestions["subclass_hint"] = f"Consider choosing or advancing your {primary_class.title()} subclass."

    if suggestions["asi_available"]:
        suggestions["notes"] = f"ASI available. Recommended: {suggestions['recommended_asi']}"
    else:
        suggestions["notes"] = "No ASI this level. Good opportunity for a strong feat or subclass feature."

    return suggestions


def add_companion(campaign_name: str, companion_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lightweight support for important companions (animal companions, sidekicks, bonded creatures, etc.).
    Stores companions separately from the main player character.
    """
    base = get_campaign_path(campaign_name) / "state"
    companions_file = base / "companions.json"

    companions = {}
    if companions_file.exists():
        with open(companions_file, "r", encoding="utf-8") as f:
            companions = json.load(f)

    companion_name = companion_data.get("name", "Unnamed Companion")
    companions[companion_name] = companion_data

    base.mkdir(parents=True, exist_ok=True)
    with open(companions_file, "w", encoding="utf-8") as f:
        json.dump(companions, f, indent=2)

    return companions


def get_companion(campaign_name: str, companion_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve a specific companion."""
    base = get_campaign_path(campaign_name) / "state"
    companions_file = base / "companions.json"

    if not companions_file.exists():
        return None

    with open(companions_file, "r", encoding="utf-8") as f:
        companions = json.load(f)

    return companions.get(companion_name)


def list_companions(campaign_name: str) -> list:
    """List all tracked companions."""
    base = get_campaign_path(campaign_name) / "state"
    companions_file = base / "companions.json"

    if not companions_file.exists():
        return []

    with open(companions_file, "r", encoding="utf-8") as f:
        companions = json.load(f)

    return list(companions.keys())


def update_companion(campaign_name: str, companion_name: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update fields on an existing companion."""
    base = get_campaign_path(campaign_name) / "state"
    companions_file = base / "companions.json"

    if not companions_file.exists():
        return None

    with open(companions_file, "r", encoding="utf-8") as f:
        companions = json.load(f)

    if companion_name not in companions:
        return None

    companions[companion_name].update(updates)

    with open(companions_file, "w", encoding="utf-8") as f:
        json.dump(companions, f, indent=2)

    return companions[companion_name]


def remove_companion(campaign_name: str, companion_name: str) -> bool:
    """Remove a companion from tracking."""
    base = get_campaign_path(campaign_name) / "state"
    companions_file = base / "companions.json"

    if not companions_file.exists():
        return False

    with open(companions_file, "r", encoding="utf-8") as f:
        companions = json.load(f)

    if companion_name in companions:
        del companions[companion_name]
        with open(companions_file, "w", encoding="utf-8") as f:
            json.dump(companions, f, indent=2)
        return True

    return False


# ============================================================
# Companion Combat / HP Tracking Hooks (Combat Integration)
# ============================================================

def _load_companions(campaign_name: str) -> Dict[str, Any]:
    """Internal helper to load companions JSON."""
    base = get_campaign_path(campaign_name) / "state"
    companions_file = base / "companions.json"
    if not companions_file.exists():
        return {}
    with open(companions_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_companions(campaign_name: str, companions: Dict[str, Any]) -> None:
    """Internal helper to save companions JSON."""
    base = get_campaign_path(campaign_name) / "state"
    companions_file = base / "companions.json"
    base.mkdir(parents=True, exist_ok=True)
    with open(companions_file, "w", encoding="utf-8") as f:
        json.dump(companions, f, indent=2)


def update_companion_hp(campaign_name: str, companion_name: str, delta: int = 0, new_current: int = None) -> Optional[Dict[str, Any]]:
    """
    Update a companion's current HP.
    Use delta for damage/healing (negative for damage) or set new_current directly.
    """
    companions = _load_companions(campaign_name)
    if companion_name not in companions:
        return None

    comp = companions[companion_name]
    hp = comp.setdefault("hit_points", {"current": 0, "max": 0})

    if new_current is not None:
        hp["current"] = max(0, min(new_current, hp.get("max", new_current)))
    else:
        hp["current"] = max(0, hp.get("current", 0) + delta)

    _save_companions(campaign_name, companions)
    return comp


def apply_damage_to_companion(campaign_name: str, companion_name: str, damage: int) -> Optional[Dict[str, Any]]:
    """Convenience wrapper for applying damage to a companion."""
    return update_companion_hp(campaign_name, companion_name, delta=-damage)


# (get_companion_combat_status has been enhanced below with death save support)


def add_companion_to_combat(campaign_name: str, companion_name: str) -> Optional[Dict[str, Any]]:
    """
    Prepare a companion for combat tracking.
    Returns combat-ready data that can be passed to dnd-combat-assistant.
    """
    status = get_companion_combat_status(campaign_name, companion_name)
    if not status:
        return None

    return {
        "name": f"{status['name']} ({status['type']})",
        "hp": status["hp_current"],
        "max_hp": status["hp_max"],
        "conditions": status["conditions"],
        "is_companion": True,
        "status": status.get("status", "Alive")
    }


def add_companion_to_active_combat(campaign_name: str, companion_name: str, initiative: int = None) -> Optional[Dict[str, Any]]:
    """
    Deep integration: Adds a companion directly into the active combat state used by dnd-combat-assistant.
    This enables auto-including companions in initiative order.
    """
    combat_file = get_campaign_path(campaign_name) / "combat" / "current_combat.json"
    if not combat_file.exists():
        return {"error": "No active combat found. Start combat first using dnd-combat-assistant."}

    try:
        with open(combat_file, "r", encoding="utf-8") as f:
            combat_data = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load combat state: {e}"}

    companion_data = add_companion_to_combat(campaign_name, companion_name)
    if not companion_data:
        return {"error": f"Companion '{companion_name}' not found."}

    existing_names = [c.get("name") for c in combat_data.get("combatants", [])]
    full_name = companion_data["name"]

    if full_name not in existing_names:
        combatant_entry = {
            "name": full_name,
            "hp_current": companion_data["hp"],
            "hp_max": companion_data["max_hp"],
            "hp_temp": 0,
            "initiative": initiative if initiative is not None else 0,
            "conditions": companion_data.get("conditions", []),
            "is_companion": True,
            "is_player": False,
            "is_unconscious": companion_data.get("status", "Alive").lower() in ("dying", "unconscious"),
            "status": companion_data.get("status", "Alive"),
        }
        combat_data.setdefault("combatants", []).append(combatant_entry)

        with open(combat_file, "w", encoding="utf-8") as f:
            json.dump(combat_data, f, indent=2)

        return {
            "success": True,
            "message": f"Added {full_name} to active combat.",
            "combatant": combatant_entry
        }
    else:
        return {"message": f"{full_name} is already participating in combat."}


# --- Condition Tracking for Companions ---

def add_condition_to_companion(campaign_name: str, companion_name: str, condition: str) -> Optional[Dict[str, Any]]:
    """Add a condition to a companion (e.g. 'Poisoned', 'Frightened')."""
    companions = _load_companions(campaign_name)
    if companion_name not in companions:
        return None

    comp = companions[companion_name]
    conditions = comp.setdefault("conditions", [])
    if condition not in conditions:
        conditions.append(condition)

    _save_companions(campaign_name, companions)
    return comp


def remove_condition_from_companion(campaign_name: str, companion_name: str, condition: str) -> Optional[Dict[str, Any]]:
    """Remove a condition from a companion."""
    companions = _load_companions(campaign_name)
    if companion_name not in companions:
        return None

    comp = companions[companion_name]
    conditions = comp.get("conditions", [])
    if condition in conditions:
        conditions.remove(condition)
        comp["conditions"] = conditions

    _save_companions(campaign_name, companions)
    return comp


# --- Basic Death Save Support for Companions ---

def handle_companion_downed(campaign_name: str, companion_name: str) -> Optional[Dict[str, Any]]:
    """Mark a companion as downed and initialize death saves."""
    companions = _load_companions(campaign_name)
    if companion_name not in companions:
        return None

    comp = companions[companion_name]
    ds = comp.setdefault("death_saves", {"successes": 0, "failures": 0, "status": "dying"})
    ds["successes"] = 0
    ds["failures"] = 0
    ds["status"] = "dying"
    comp["status"] = "Dying"

    _save_companions(campaign_name, companions)
    return comp


def update_companion_death_saves(campaign_name: str, companion_name: str, success: bool = None, reset: bool = False) -> Optional[Dict[str, Any]]:
    """
    Apply a death save to a companion or reset them.
    3 successes = stable, 3 failures = dead.
    """
    companions = _load_companions(campaign_name)
    if companion_name not in companions:
        return None

    comp = companions[companion_name]
    ds = comp.setdefault("death_saves", {"successes": 0, "failures": 0, "status": "stable"})

    if reset:
        ds["successes"] = 0
        ds["failures"] = 0
        ds["status"] = "stable"
        comp["status"] = "Alive"
    elif success is True:
        ds["successes"] = ds.get("successes", 0) + 1
        if ds["successes"] >= 3:
            ds["status"] = "stable"
            comp["status"] = "Stable (0 HP)"
    elif success is False:
        ds["failures"] = ds.get("failures", 0) + 1
        if ds["failures"] >= 3:
            ds["status"] = "dead"
            comp["status"] = "Dead"

    _save_companions(campaign_name, companions)
    return comp


def get_companion_combat_status(campaign_name: str, companion_name: str) -> Optional[Dict[str, Any]]:
    """Return enhanced combat-relevant status including death saves."""
    companions = _load_companions(campaign_name)
    if companion_name not in companions:
        return None

    comp = companions[companion_name]
    hp = comp.get("hit_points", {"current": 0, "max": 0})
    ds = comp.get("death_saves", {"successes": 0, "failures": 0, "status": "stable"})

    return {
        "name": companion_name,
        "type": comp.get("type", "Companion"),
        "hp_current": hp.get("current", 0),
        "hp_max": hp.get("max", 0),
        "conditions": comp.get("conditions", []),
        "status": comp.get("status", "Alive"),
        "death_saves": ds,
        "notes": comp.get("notes", "")
    }


def add_all_companions_to_combat(
    campaign_name: str,
    auto_roll_initiative: bool = True,
    only_active: bool = True,
    min_level: int = None,
    max_level: int = None,
    companion_types: list = None
) -> Dict[str, Any]:
    """
    Advanced automation with rich filtering.
    Uses filter_companions() internally for flexibility.
    """
    companions_to_add = filter_companions(
        campaign_name=campaign_name,
        only_active=only_active,
        min_level=min_level,
        max_level=max_level,
        companion_types=companion_types
    )

    if not companions_to_add:
        return {
            "message": "No companions matched the provided filters.",
            "added": []
        }

    results = []
    dice_available = False

    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-dice-engine" / "scripts"))
        from dice_roller import roll_dice
        dice_available = True
    except Exception:
        dice_available = False

    for name in companions_to_add:
        init_roll = 0
        if auto_roll_initiative and dice_available:
            try:
                roll = roll_dice("1d20")
                init_roll = roll.get("total", 0)
            except Exception:
                init_roll = 0

        result = add_companion_to_active_combat(campaign_name, name, initiative=init_roll)
        results.append({
            "companion": name,
            "initiative": init_roll,
            "result": result
        })

    return {
        "success": True,
        "message": f"Added {len(companions_to_add)} companion(s) using filters.",
        "results": results,
        "dice_engine_used": dice_available,
        "filters": {
            "only_active": only_active,
            "min_level": min_level,
            "max_level": max_level,
            "companion_types": companion_types
        }
    }


def get_companion_status_summary(campaign_name: str, only_active: bool = True) -> str:
    """
    Generate a clean, readable status summary for companions.
    Useful for session briefings or quick overviews.
    """
    if only_active:
        names = get_active_companions(campaign_name)
    else:
        names = list_companions(campaign_name)

    if not names:
        return "No companions found."

    companions_data = _load_companions(campaign_name)
    lines = ["**Companion Status Summary**"]

    for name in names:
        comp = companions_data.get(name, {})
        hp = comp.get("hit_points", {})
        hp_str = f"{hp.get('current', '?')}/{hp.get('max', '?')}" if hp else "—"
        status = comp.get("status", "Alive")
        conditions = ", ".join(comp.get("conditions", [])) or "None"
        level = comp.get("level", "")
        level_str = f" (Lvl {level})" if level else ""

        line = f"- **{name}**{level_str} — HP: {hp_str} | Status: {status} | Conditions: {conditions}"
        lines.append(line)

    return "\n".join(lines)


def set_companion_active(campaign_name: str, companion_name: str, active: bool = True) -> Optional[Dict[str, Any]]:
    """
    Mark a companion as active or inactive.
    Inactive companions are excluded from add_all_companions_to_combat() when only_active=True.
    Useful for companions who are back at camp, injured, or temporarily unavailable.
    """
    companions = _load_companions(campaign_name)
    if companion_name not in companions:
        return None

    companions[companion_name]["active"] = active
    _save_companions(campaign_name, companions)
    return companions[companion_name]


def get_active_companions(campaign_name: str) -> list:
    """Return list of companions currently marked as active."""
    all_names = list_companions(campaign_name)
    if not all_names:
        return []

    companions_data = _load_companions(campaign_name)
    return [name for name in all_names if companions_data.get(name, {}).get("active", True)]


def filter_companions(
    campaign_name: str,
    only_active: bool = True,
    min_level: int = None,
    max_level: int = None,
    companion_types: list = None
) -> list:
    """
    Flexible companion filtering system.
    Supports level range and type filtering in addition to active status.
    """
    all_names = list_companions(campaign_name)
    if not all_names:
        return []

    companions_data = _load_companions(campaign_name)
    filtered = []

    for name in all_names:
        comp = companions_data.get(name, {})

        if only_active and not comp.get("active", True):
            continue

        comp_level = comp.get("level", 0)
        if min_level is not None and comp_level < min_level:
            continue
        if max_level is not None and comp_level > max_level:
            continue

        if companion_types:
            if comp.get("type") not in companion_types:
                continue

        filtered.append(name)

    return filtered
