#!/usr/bin/env python3
"""
combat_tracker.py — Combat State Manager (Backend for dnd-combat-assistant)

Production-ready combat tracking with persistent state:
- Initiative order and turn management
- HP tracking for players, companions, and monsters
- Conditions with duration support
- Concentration tracking
- Group combatant support
- End-of-combat cleanup and sync with central state layer

Designed for reliability during mobile play and long campaigns.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import shared utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))
try:
    from bootstrap import ensure_utils_importable
    ensure_utils_importable()
    from dnd_state_utils import (
        get_campaign_path,
        record_combat_outcome,
        update_player_hp,
        update_important_companion,
    )
    from sync_bridge import on_player_death_save, on_player_damaged, on_player_healed
except ImportError:
    print("Warning: dnd_state_utils not available. Running in limited mode.", file=sys.stderr)
    from paths import get_campaign_path  # type: ignore

    def update_player_hp(*a, **k): return {"current": 0, "max": 0}
    def update_important_companion(*a, **k): return {}
    def record_combat_outcome(*a, **k): return {}
    def on_player_damaged(*a, **k): return {}
    def on_player_healed(*a, **k): return {}
    def on_player_death_save(*a, **k): return {}

def get_combat_file(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "combat" / "current_combat.json"

def load_combat(campaign_name: str) -> Dict[str, Any]:
    """Load combat state. Returns safe default on missing or corrupted file."""
    path = get_combat_file(campaign_name)
    if not path.exists():
        return {
            "encounter_name": "No active combat",
            "combatants": [],
            "current_turn": 0,
            "round": 1,
            "log": []
        }
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure required keys exist
            data.setdefault("combatants", [])
            data.setdefault("current_turn", 0)
            data.setdefault("round", 1)
            data.setdefault("log", [])
            return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load combat state for {campaign_name}: {e}", file=sys.stderr)
        return {
            "encounter_name": "Corrupted combat state",
            "combatants": [],
            "current_turn": 0,
            "round": 1,
            "log": [f"Error loading combat state: {e}"]
        }

def save_combat(campaign_name: str, data: Dict[str, Any]) -> None:
    """Save combat state with atomic write protection."""
    path = get_combat_file(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    
    # Atomic write using temp file
    temp_path = path.with_suffix(".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        temp_path.replace(path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise IOError(f"Failed to save combat state: {e}") from e

def init_combat(campaign_name: str, encounter_name: str = "Unnamed Encounter") -> Dict[str, Any]:
    data = {
        "encounter_name": encounter_name,
        "started": datetime.now().isoformat(),
        "combatants": [],
        "current_turn": 0,
        "round": 1,
        "log": [f"Combat started: {encounter_name}"]
    }
    save_combat(campaign_name, data)
    return data

def add_combatant(campaign_name: str, name: str, hp: int, initiative: int, is_player: bool = False, is_companion: bool = False, group_size: int = 1) -> Dict[str, Any]:
    """
    Add a combatant. Supports group_size for large fights (e.g. 12 goblins as one entry).
    """
    combat = load_combat(campaign_name)
    combatant = {
        "name": name,
        "hp_current": hp,
        "hp_max": hp,
        "hp_temp": 0,
        "initiative": initiative,
        "is_player": is_player,
        "is_companion": is_companion,
        "is_group": group_size > 1,
        "group_size": group_size,
        "is_unconscious": False,
        "conditions": [],
        "concentration": None,
        "death_saves": {
            "successes": 0,
            "failures": 0
        },
        "notes": ""
    }
    combat["combatants"].append(combatant)
    combat["combatants"].sort(key=lambda x: x["initiative"], reverse=True)
    combat["log"].append(f"Added {name} (Init {initiative}, HP {hp}, Group: {group_size})")
    save_combat(campaign_name, combat)
    return combat


def add_combatant_group(campaign_name: str, name: str, hp_per: int, initiative: int, quantity: int, is_player: bool = False) -> Dict[str, Any]:
    """Convenience function to add a group of identical combatants as one tracked entry."""
    return add_combatant(
        campaign_name,
        name=name,
        hp=hp_per,
        initiative=initiative,
        is_player=is_player,
        group_size=quantity
    )

def apply_damage(campaign_name: str, target_name: str, amount: int) -> Dict[str, Any]:
    """
    Apply damage to a combatant or group.
    
    Features:
    - Temporary HP absorbs damage first (with logging)
    - Intelligent group damage handling
    - Concentration break on significant damage
    - Automatic Unconscious condition + state when HP reaches 0
    - Syncs player/companion HP back to main campaign state
    """
    combat = load_combat(campaign_name)
    target_found = False

    for c in combat["combatants"]:
        if c["name"].lower() == target_name.lower():
            target_found = True
            hp_before_damage = c.get("hp_current", 0)
            remaining = amount
            is_group = c.get("is_group", False) and c.get("group_size", 1) > 1
            hp_per = c.get("hp_max", c.get("hp_current", 1))

            # === Temporary HP absorption ===
            absorbed = 0
            if c.get("hp_temp", 0) > 0:
                absorbed = min(remaining, c["hp_temp"])
                c["hp_temp"] -= absorbed
                remaining -= absorbed
                if absorbed > 0:
                    combat["log"].append(f"{target_name}'s temporary HP absorbed {absorbed} damage")

            if is_group:
                # Group damage logic
                creatures_killed = 0
                while remaining >= hp_per and c.get("group_size", 1) > 0:
                    c["group_size"] -= 1
                    creatures_killed += 1
                    remaining -= hp_per

                c["hp_current"] = max(0, c["hp_current"] - remaining)

                if creatures_killed > 0:
                    combat["log"].append(f"{target_name} group lost {creatures_killed} member(s)")
                if c.get("group_size", 1) <= 0:
                    c["is_unconscious"] = True
                    c["group_size"] = 0
                    combat["log"].append(f"{target_name} group wiped out")
            else:
                # Single target
                c["hp_current"] = max(0, c["hp_current"] - remaining)
                if c["hp_current"] <= 0:
                    c["is_unconscious"] = True

            # === Concentration break ===
            if c.get("concentration") and amount > 0:
                combat["log"].append(f"⚠ {target_name}'s concentration on '{c['concentration']}' was broken!")
                c["concentration"] = None

            # === Unconscious handling ===
            if c.get("hp_current", 0) <= 0 and not c.get("is_unconscious"):
                c["is_unconscious"] = True
                c["concentration"] = None

                # Ensure conditions list exists and is a list
                if not isinstance(c.get("conditions"), list):
                    c["conditions"] = []

                has_unconscious = any(
                    isinstance(cond, dict) and cond.get("name") == "Unconscious"
                    for cond in c.get("conditions", [])
                )
                if not has_unconscious:
                    c["conditions"].append({
                        "name": "Unconscious",
                        "duration_rounds": 0,
                        "applied_round": combat.get("round", 1)
                    })
                combat["log"].append(f"⚠ {target_name} has been knocked Unconscious!")

            hp_delta = max(0, hp_before_damage - c.get("hp_current", 0))

            # === Sync to main campaign state ===
            if c.get("is_player"):
                try:
                    on_player_damaged(campaign_name, c.get("hp_current", 0))
                except Exception:
                    try:
                        update_player_hp(campaign_name, delta=-hp_delta)
                    except Exception:
                        pass
            elif c.get("is_companion"):
                try:
                    update_important_companion(campaign_name, {
                        "hp": {"current": c["hp_current"], "max": c.get("hp_max", c["hp_current"])}
                    })
                except Exception:
                    pass

            combat["log"].append(
                f"{target_name} took {amount} damage "
                f"(now {c.get('hp_current', 0)}/{c.get('hp_max', '?')}, temp: {c.get('hp_temp', 0)})"
            )
            break

    if not target_found:
        combat["log"].append(f"Warning: Target '{target_name}' not found in combat")

    try:
        save_combat(campaign_name, combat)
    except Exception as e:
        combat.setdefault("log", []).append(f"[Error] Failed to persist combat state: {e}")

    return combat


def _format_conditions(conditions: List[Any]) -> str:
    if not conditions:
        return ""
    names = []
    for cond in conditions:
        if isinstance(cond, dict):
            names.append(str(cond.get("name", cond)))
        else:
            names.append(str(cond))
    return ", ".join(names)


def apply_healing(campaign_name: str, target_name: str, amount: int) -> Dict[str, Any]:
    """Apply healing to a combatant (cannot exceed max HP)."""
    combat = load_combat(campaign_name)
    for c in combat["combatants"]:
        if c["name"].lower() == target_name.lower():
            before = c.get("hp_current", 0)
            c["hp_current"] = min(c.get("hp_max", before), before + amount)
            if c["hp_current"] > 0 and c.get("is_unconscious"):
                c["is_unconscious"] = False
                c["conditions"] = [
                    cond for cond in c.get("conditions", [])
                    if not (isinstance(cond, dict) and cond.get("name") == "Unconscious")
                ]
            healed = c["hp_current"] - before
            combat["log"].append(
                f"{target_name} healed for {healed} HP ({c['hp_current']}/{c['hp_max']})"
            )
            if c.get("is_player") and healed > 0:
                try:
                    on_player_healed(campaign_name, healed)
                except Exception:
                    try:
                        update_player_hp(campaign_name, delta=healed)
                    except Exception:
                        pass
            elif c.get("is_companion") and healed > 0:
                try:
                    update_important_companion(campaign_name, {
                        "hp": {"current": c["hp_current"], "max": c.get("hp_max", c["hp_current"])}
                    })
                except Exception:
                    pass
            break
    else:
        combat["log"].append(f"Warning: Target '{target_name}' not found in combat")
    save_combat(campaign_name, combat)
    return combat


def next_turn(campaign_name: str) -> Dict[str, Any]:
    """Advance to the next creature's turn. Handles empty combat gracefully."""
    combat = load_combat(campaign_name)
    if not combat.get("combatants"):
        combat["log"].append("Cannot advance turn: No combatants in combat")
        save_combat(campaign_name, combat)
        return combat
    
    num_combatants = len(combat["combatants"])
    combat["current_turn"] = (combat["current_turn"] + 1) % num_combatants
    
    if combat["current_turn"] == 0:
        combat["round"] = combat.get("round", 1) + 1
        combat["log"].append(f"--- Round {combat['round']} begins ---")
    
    try:
        current = combat["combatants"][combat["current_turn"]]
        combat["log"].append(f"Turn: {current['name']}")
    except IndexError:
        combat["log"].append("Warning: Turn index out of range after advancement")
    
    save_combat(campaign_name, combat)
    return combat

def get_status(campaign_name: str) -> Dict[str, Any]:
    return load_combat(campaign_name)


def get_combat_summary(campaign_name: str) -> str:
    """
    Returns a human-readable summary, with special handling for groups in large fights.
    Dynamically shows current group size as creatures die.
    """
    combat = load_combat(campaign_name)
    lines = [f"=== {combat.get('encounter_name', 'Combat')} (Round {combat.get('round', 1)}) ==="]

    for i, c in enumerate(combat["combatants"]):
        marker = "→" if i == combat.get("current_turn", 0) else " "
        group_info = ""

        current_group = c.get("group_size", 1)
        if c.get("is_group") and current_group > 1:
            group_info = f" [x{current_group}]"
        elif c.get("is_group") and current_group == 1:
            group_info = " [last one]"

        status = f"{c['name']}{group_info} ({c['hp_current']}/{c['hp_max']} HP)"
        cond_text = _format_conditions(c.get("conditions", []))
        if cond_text:
            status += f" | {cond_text}"
        if c.get("is_unconscious"):
            status += " [UNCONSCIOUS]"

        lines.append(f"{marker} {status}")

    return "\n".join(lines)


def apply_temp_hp(campaign_name: str, target_name: str, amount: int) -> Dict[str, Any]:
    """Grant or increase temporary HP on a combatant."""
    combat = load_combat(campaign_name)
    for c in combat["combatants"]:
        if c["name"].lower() == target_name.lower():
            current_temp = c.get("hp_temp", 0)
            # In 5e, new temp HP only replaces if higher
            if amount > current_temp:
                c["hp_temp"] = amount
                combat["log"].append(f"{target_name} gained {amount} temporary HP")
            else:
                combat["log"].append(f"{target_name} already has higher temporary HP ({current_temp})")
            break
    save_combat(campaign_name, combat)
    return combat


def remove_combatant(campaign_name: str, target_name: str) -> Dict[str, Any]:
    """Remove a combatant from the fight (e.g. when they die or flee)."""
    combat = load_combat(campaign_name)
    original_len = len(combat["combatants"])
    combat["combatants"] = [c for c in combat["combatants"] if c["name"].lower() != target_name.lower()]
    
    if len(combat["combatants"]) < original_len:
        combat["log"].append(f"{target_name} was removed from combat")
        # Adjust current_turn if needed
        if combat["current_turn"] >= len(combat["combatants"]) and combat["combatants"]:
            combat["current_turn"] = 0
    else:
        combat["log"].append(f"Warning: {target_name} not found in combat")
    
    save_combat(campaign_name, combat)
    return combat


def tick_conditions(campaign_name: str) -> Dict[str, Any]:
    """
    Decrement duration on all timed conditions.
    Call this at the end of each round (or when appropriate).
    """
    combat = load_combat(campaign_name)
    current_round = combat.get("round", 1)
    
    for c in combat["combatants"]:
        if "conditions" not in c:
            continue
        
        remaining_conditions = []
        for cond in c["conditions"]:
            dur = cond.get("duration_rounds", 0)
            if dur == 0:
                remaining_conditions.append(cond)
            else:
                applied = cond.get("applied_round", current_round)
                rounds_elapsed = current_round - applied
                if rounds_elapsed < dur:
                    remaining_conditions.append(cond)
                else:
                    combat["log"].append(f"{c['name']} is no longer {cond['name']}")
        
        c["conditions"] = remaining_conditions
    
    save_combat(campaign_name, combat)
    return combat


def record_death_save(campaign_name: str, creature_name: str, success: bool) -> Dict[str, Any]:
    """
    Record a death save success or failure for an unconscious creature.
    3 successes = stable. 3 failures = dead.
    """
    combat = load_combat(campaign_name)
    for c in combat["combatants"]:
        if c["name"].lower() == creature_name.lower():
            if not c.get("is_unconscious"):
                combat["log"].append(f"Warning: {creature_name} is not unconscious. Death saves only apply when at 0 HP.")
                break
            
            ds = c.setdefault("death_saves", {"successes": 0, "failures": 0})
            
            if success:
                ds["successes"] = ds.get("successes", 0) + 1
                combat["log"].append(f"{creature_name} rolled a Death Save Success ({ds['successes']}/3)")
                if c.get("is_player"):
                    try:
                        on_player_death_save(campaign_name, True)
                    except Exception:
                        pass
                if ds["successes"] >= 3:
                    c["is_unconscious"] = False
                    combat["log"].append(f"🎉 {creature_name} has stabilized (3 death save successes)!")
            else:
                ds["failures"] = ds.get("failures", 0) + 1
                combat["log"].append(f"{creature_name} rolled a Death Save Failure ({ds['failures']}/3)")
                if c.get("is_player"):
                    try:
                        on_player_death_save(campaign_name, False)
                    except Exception:
                        pass
                if ds["failures"] >= 3:
                    combat["log"].append(f"💀 {creature_name} has died (3 death save failures)!")
                    c["is_unconscious"] = False  # Consider marking as dead in future versions
            
            break
    save_combat(campaign_name, combat)
    return combat


def apply_condition(campaign_name: str, target_name: str, condition: str, duration_rounds: int = 0) -> Dict[str, Any]:
    """
    Apply a condition to a combatant.
    
    duration_rounds: Number of rounds the condition lasts (0 = until removed manually).
    """
    combat = load_combat(campaign_name)
    for c in combat["combatants"]:
        if c["name"].lower() == target_name.lower():
            if "conditions" not in c:
                c["conditions"] = []
            
            cond_entry = {
                "name": condition,
                "duration_rounds": duration_rounds,
                "applied_round": combat.get("round", 1)
            }
            c["conditions"].append(cond_entry)
            
            duration_text = f" for {duration_rounds} rounds" if duration_rounds > 0 else ""
            combat["log"].append(f"{target_name} gained condition: {condition}{duration_text}")
            break
    save_combat(campaign_name, combat)
    return combat


def set_concentration(campaign_name: str, creature_name: str, effect: str) -> Dict[str, Any]:
    """Set what a creature is concentrating on (only one per creature)."""
    combat = load_combat(campaign_name)
    for c in combat["combatants"]:
        if c["name"].lower() == creature_name.lower():
            c["concentration"] = effect
            combat["log"].append(f"{creature_name} is now concentrating on: {effect}")
            break
    save_combat(campaign_name, combat)
    return combat


def end_combat(campaign_name: str, award_xp: int = 0) -> Dict[str, Any]:
    """End combat cleanly and optionally award XP."""
    combat = load_combat(campaign_name)
    combat["log"].append("=== COMBAT ENDED ===")
    if award_xp > 0:
        combat["log"].append(f"XP awarded: {award_xp}")
    
    # Clear the combat file (with backup)
    combat_file = get_combat_file(campaign_name)
    if combat_file.exists():
        backup_path = combat_file.with_suffix(".ended.json")
        combat_file.rename(backup_path)

    try:
        record_combat_outcome(
            campaign_name,
            f"Combat ended: {combat.get('encounter_name', 'unknown encounter')}",
            importance="normal",
        )
    except Exception:
        pass
    
    return {"status": "combat_ended", "log": combat["log"], "xp_awarded": award_xp}


def resolve_mass_combat(
    attacker_name: str,
    defender_name: str,
    attacker_strength: int,
    defender_strength: int,
    attacker_morale: int = 10,
    defender_morale: int = 10
) -> Dict[str, Any]:
    """
    Simple mass combat resolver for large battles.
    Uses opposed rolls + strength comparison to determine outcome and casualties.
    """
    import random

    # Attacker roll
    attacker_roll = random.randint(1, 20) + (attacker_strength // 5)
    defender_roll = random.randint(1, 20) + (defender_strength // 5)

    attacker_advantage = attacker_roll > defender_roll
    total_strength = attacker_strength + defender_strength

    if total_strength == 0:
        return {"error": "No forces present"}

    # Casualty calculation (simplified)
    if attacker_advantage:
        attacker_casualties = max(1, attacker_strength // 8)
        defender_casualties = max(2, defender_strength // 5)
        winner = attacker_name
    else:
        attacker_casualties = max(2, attacker_strength // 5)
        defender_casualties = max(1, defender_strength // 8)
        winner = defender_name

    # Morale check
    attacker_morale_check = random.randint(1, 20) + (attacker_morale // 2)
    defender_morale_check = random.randint(1, 20) + (defender_morale // 2)

    attacker_broken = attacker_morale_check < 10
    defender_broken = defender_morale_check < 10

    result = {
        "attacker": attacker_name,
        "defender": defender_name,
        "attacker_roll": attacker_roll,
        "defender_roll": defender_roll,
        "winner": winner,
        "attacker_casualties": attacker_casualties,
        "defender_casualties": defender_casualties,
        "attacker_morale_broken": attacker_broken,
        "defender_morale_broken": defender_broken,
        "summary": f"{winner} wins the engagement. Attacker lost ~{attacker_casualties}, Defender lost ~{defender_casualties}."
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Combat Tracker for D&D skills")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    p_init = sub.add_parser("init")
    p_init.add_argument("campaign")
    p_init.add_argument("--encounter", default="Encounter")
    
    p_add = sub.add_parser("add")
    p_add.add_argument("campaign")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--hp", type=int, required=True)
    p_add.add_argument("--initiative", type=int, required=True)
    p_add.add_argument("--player", action="store_true")
    p_add.add_argument("--companion", action="store_true")
    p_add.add_argument("--group-size", type=int, default=1)
    
    p_dmg = sub.add_parser("damage")
    p_dmg.add_argument("campaign")
    p_dmg.add_argument("--target", required=True)
    p_dmg.add_argument("--amount", type=int, required=True)

    p_heal = sub.add_parser("heal")
    p_heal.add_argument("campaign")
    p_heal.add_argument("--target", required=True)
    p_heal.add_argument("--amount", type=int, required=True)
    
    p_next = sub.add_parser("next-turn")
    p_next.add_argument("campaign")
    
    p_status = sub.add_parser("status")
    p_status.add_argument("campaign")
    
    p_temp = sub.add_parser("apply-temp-hp")
    p_temp.add_argument("campaign")
    p_temp.add_argument("--target", required=True)
    p_temp.add_argument("--amount", type=int, required=True)
    
    p_remove = sub.add_parser("remove")
    p_remove.add_argument("campaign")
    p_remove.add_argument("--target", required=True)
    
    p_tick = sub.add_parser("tick-conditions")
    p_tick.add_argument("campaign")
    
    p_ds_success = sub.add_parser("death-save-success")
    p_ds_success.add_argument("campaign")
    p_ds_success.add_argument("--target", required=True)
    
    p_ds_fail = sub.add_parser("death-save-failure")
    p_ds_fail.add_argument("campaign")
    p_ds_fail.add_argument("--target", required=True)
    
    p_cond = sub.add_parser("apply-condition")
    p_cond.add_argument("campaign")
    p_cond.add_argument("--target", required=True)
    p_cond.add_argument("--condition", required=True)
    p_cond.add_argument("--duration-rounds", type=int, default=0)
    
    p_conc = sub.add_parser("set-concentration")
    p_conc.add_argument("campaign")
    p_conc.add_argument("--creature", required=True)
    p_conc.add_argument("--effect", required=True)
    
    p_end = sub.add_parser("end-combat")
    p_end.add_argument("campaign")
    p_end.add_argument("--xp", type=int, default=0)

    # Mass combat resolver
    p_mass = sub.add_parser("resolve-mass-combat", help="Resolve large-scale battles abstractly")
    p_mass.add_argument("attacker_name")
    p_mass.add_argument("defender_name")
    p_mass.add_argument("--attacker-strength", type=int, required=True)
    p_mass.add_argument("--defender-strength", type=int, required=True)
    p_mass.add_argument("--attacker-morale", type=int, default=10)
    p_mass.add_argument("--defender-morale", type=int, default=10)
    
    args = parser.parse_args()
    
    if args.cmd == "init":
        print(json.dumps(init_combat(args.campaign, args.encounter), indent=2))
    elif args.cmd == "add":
        print(json.dumps(add_combatant(
            args.campaign, args.name, args.hp, args.initiative,
            args.player, args.companion, group_size=args.group_size,
        ), indent=2))
    elif args.cmd == "damage":
        print(json.dumps(apply_damage(args.campaign, args.target, args.amount), indent=2))
    elif args.cmd == "heal":
        print(json.dumps(apply_healing(args.campaign, args.target, args.amount), indent=2))
    elif args.cmd == "next-turn":
        print(json.dumps(next_turn(args.campaign), indent=2))
    elif args.cmd == "status":
        print(json.dumps(get_status(args.campaign), indent=2))
    elif args.cmd == "apply-temp-hp":
        print(json.dumps(apply_temp_hp(args.campaign, args.target, args.amount), indent=2))
    elif args.cmd == "remove":
        print(json.dumps(remove_combatant(args.campaign, args.target), indent=2))
    elif args.cmd == "tick-conditions":
        print(json.dumps(tick_conditions(args.campaign), indent=2))
    elif args.cmd == "death-save-success":
        print(json.dumps(record_death_save(args.campaign, args.target, success=True), indent=2))
    elif args.cmd == "death-save-failure":
        print(json.dumps(record_death_save(args.campaign, args.target, success=False), indent=2))
    elif args.cmd == "apply-condition":
        print(json.dumps(apply_condition(args.campaign, args.target, args.condition, args.duration_rounds), indent=2))
    elif args.cmd == "set-concentration":
        print(json.dumps(set_concentration(args.campaign, args.creature, args.effect), indent=2))
    elif args.cmd == "end-combat":
        print(json.dumps(end_combat(args.campaign, args.xp), indent=2))
    elif args.cmd == "resolve-mass-combat":
        result = resolve_mass_combat(
            args.attacker_name,
            args.defender_name,
            args.attacker_strength,
            args.defender_strength,
            args.attacker_morale,
            args.defender_morale
        )
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
