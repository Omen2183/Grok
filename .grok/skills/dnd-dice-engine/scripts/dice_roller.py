#!/usr/bin/env python3
"""
Enhanced D&D Dice Roller for Grok skills.
Supports standard 5e notation including:
- Basic: 2d6+3, 1d20-1
- Keep highest/lowest: 4d6kh3, 2d20kl1
- Advantage / Disadvantage on d20 rolls
- Percentile rolls (d100 or 2d10)
"""

import random
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def parse_dice_notation(notation: str) -> Dict[str, Any]:
    """Parse dice notation like 2d6+3, 4d6kh3, 1d20+5, 2d20 adv, etc."""
    notation = notation.lower().replace(" ", "")
    
    # Handle common shorthands
    if "adv" in notation or "advantage" in notation:
        notation = notation.replace("adv", "").replace("advantage", "").strip()
        # Will be handled by caller
    if "disadv" in notation or "disadvantage" in notation:
        notation = notation.replace("disadv", "").replace("disadvantage", "").strip()
    
    # Match patterns like: 2d6+3, 4d6kh3, 1d20-2, d6, 2d20, etc.
    match = re.match(r'(\d*)d(\d+)(kh|kl)?(\d+)?([+-]\d+)?', notation)
    if not match:
        raise ValueError(f"Invalid dice notation: {notation}")
    
    num_dice = int(match.group(1)) if match.group(1) else 1
    die_size = int(match.group(2))
    keep_type = match.group(3)
    keep_num = int(match.group(4)) if match.group(4) else None
    modifier = int(match.group(5)) if match.group(5) else 0
    
    if keep_type and keep_num is None:
        keep_num = num_dice
    
    return {
        "num_dice": num_dice,
        "die_size": die_size,
        "keep_type": keep_type,
        "keep_num": keep_num,
        "modifier": modifier
    }

def roll_single_pool(num_dice: int, die_size: int, keep_type: str = None, keep_num: int = None, exploding: bool = False) -> Dict[str, Any]:
    """Roll a pool of dice. Supports keep highest/lowest and basic exploding dice."""
    rolls = []
    for _ in range(num_dice):
        roll = random.randint(1, die_size)
        rolls.append(roll)
        # Basic exploding: keep rolling while max is hit (simple version)
        while exploding and roll == die_size:
            roll = random.randint(1, die_size)
            rolls.append(roll)

    if keep_type == "kh" and keep_num:
        sorted_rolls = sorted(rolls, reverse=True)
        kept = sorted_rolls[:keep_num]
        dropped = sorted_rolls[keep_num:]
        total = sum(kept)
        return {"rolls": rolls, "kept": kept, "dropped": dropped, "total_before_modifier": total}
    elif keep_type == "kl" and keep_num:
        sorted_rolls = sorted(rolls)
        kept = sorted_rolls[:keep_num]
        dropped = sorted_rolls[keep_num:]
        total = sum(kept)
        return {"rolls": rolls, "kept": kept, "dropped": dropped, "total_before_modifier": total}
    else:
        return {"rolls": rolls, "kept": rolls, "dropped": [], "total_before_modifier": sum(rolls)}

def roll_dice(notation: str, advantage: bool = False, disadvantage: bool = False, exploding: bool = False, campaign: Optional[str] = None) -> Dict[str, Any]:
    """Main rolling function with full D&D support + homebrew options.
    
    If `campaign` is provided, the roll is automatically logged to logs/rolls.json.
    """
    parsed = parse_dice_notation(notation)
    num_dice = parsed["num_dice"]
    die_size = parsed["die_size"]
    keep_type = parsed["keep_type"]
    keep_num = parsed["keep_num"]
    modifier = parsed["modifier"]
    
    # Handle Advantage / Disadvantage (primarily for d20 rolls)
    if (advantage or disadvantage) and die_size == 20:
        roll1 = roll_single_pool(num_dice, die_size, keep_type, keep_num)
        roll2 = roll_single_pool(num_dice, die_size, keep_type, keep_num)
        
        total1 = roll1["total_before_modifier"] + modifier
        total2 = roll2["total_before_modifier"] + modifier
        
        if advantage:
            chosen_total = max(total1, total2)
            chosen_data = roll1 if total1 >= total2 else roll2
            note = "Advantage — took higher result"
        else:
            chosen_total = min(total1, total2)
            chosen_data = roll1 if total1 <= total2 else roll2
            note = "Disadvantage — took lower result"
        
        result = {
            "notation": notation,
            "advantage": advantage,
            "disadvantage": disadvantage,
            "roll_1": {
                "rolls": roll1["rolls"],
                "kept": roll1.get("kept", roll1["rolls"]),
                "total_before_mod": roll1["total_before_modifier"]
            },
            "roll_2": {
                "rolls": roll2["rolls"],
                "kept": roll2.get("kept", roll2["rolls"]),
                "total_before_mod": roll2["total_before_modifier"]
            },
            "chosen": {
                "rolls": chosen_data["rolls"],
                "kept": chosen_data.get("kept", chosen_data["rolls"]),
                "total": chosen_total
            },
            "modifier": modifier,
            "total": chosen_total,
            "note": note
        }

        if campaign:
            try:
                sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))
                from dnd_state_utils import log_roll
                log_roll(campaign, notation, chosen_total, {"advantage": advantage or disadvantage})
            except Exception:
                pass

        return result

    # Normal roll (with optional keep highest/lowest + exploding)
    result = roll_single_pool(num_dice, die_size, keep_type, keep_num, exploding=exploding)
    total = result["total_before_modifier"] + modifier
    
    if campaign:
        try:
            sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))
            from dnd_state_utils import log_roll
            log_roll(campaign, notation, total, {
                "exploding": exploding,
                "kept": result.get("kept", result["rolls"]),
                "dropped": result.get("dropped", [])
            })
        except Exception:
            # Logging failure should never break dice rolls
            pass

    return {
        "notation": notation,
        "exploding": exploding,
        "rolls": result["rolls"],
        "kept": result.get("kept", result["rolls"]),
        "dropped": result.get("dropped", []),
        "modifier": modifier,
        "total": total,
        "note": "Exploding dice enabled" if exploding else ""
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Reliable D&D Dice Roller (supports 5e notation + keep highest/lowest + advantage/disadvantage)"
    )
    parser.add_argument("notation", help="Dice notation e.g. 1d20+5, 4d6kh3, 2d20 advantage")
    parser.add_argument("--advantage", action="store_true", help="Roll with advantage (best of two)")
    parser.add_argument("--disadvantage", action="store_true", help="Roll with disadvantage (worst of two)")
    parser.add_argument("--exploding", action="store_true", help="Enable exploding dice (roll again on max value)")
    parser.add_argument("--campaign", help="Optional campaign name to log this roll")

    args = parser.parse_args()

    try:
        result = roll_dice(args.notation, args.advantage, args.disadvantage, args.exploding, campaign=args.campaign)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "notation": args.notation}))
        sys.exit(1)
