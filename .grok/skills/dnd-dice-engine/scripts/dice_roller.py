#!/usr/bin/env python3
"""
Enhanced D&D Dice Roller for Grok skills.
Supports standard 5e notation including:
- Basic: 2d6+3, 1d20-1
- Keep highest/lowest: 4d6kh3, 2d20kl1
- Advantage / Disadvantage on d20 rolls
- Percentile rolls (d100 or 2d10)
- d3 (d6 halved, rounded up)
"""

import random
import re
import sys
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

DICE_BACKEND_VERSION = "3.2.0"


def _strip_adv_disadv(notation: str) -> Tuple[str, bool, bool]:
    """Remove adv/disadv tokens from notation; return cleaned string and flags."""
    raw = notation.lower().replace(" ", "")
    disadvantage = bool(re.search(r"disadv(?:antage)?", raw))
    advantage = bool(re.search(r"(?<!dis)adv(?:antage)?", raw))
    if advantage and disadvantage:
        advantage = False
        disadvantage = False
    cleaned = re.sub(r"disadv(?:antage)?", "", raw)
    cleaned = re.sub(r"(?<!dis)adv(?:antage)?", "", cleaned)
    return cleaned, advantage, disadvantage


def parse_dice_notation(notation: str) -> Dict[str, Any]:
    """Parse dice notation like 2d6+3, 4d6kh3, 1d20+5, 2d20, d100, d3, etc."""
    notation = notation.lower().replace(" ", "")

    # Percentile shorthand
    if notation in ("d100", "1d100", "percentile", "d%"):
        return {"roll_type": "percentile", "modifier": 0}

    # d3 homebrew shorthand (d6 / 2, round up)
    if notation in ("d3", "1d3"):
        return {"roll_type": "d3", "modifier": 0}

    match = re.match(r"(\d*)d(\d+)(kh|kl)?(\d+)?([+-]\d+)?", notation)
    if not match:
        raise ValueError(f"Invalid dice notation: {notation}")

    num_dice = int(match.group(1)) if match.group(1) else 1
    die_size = int(match.group(2))
    keep_type = match.group(3)
    keep_num = int(match.group(4)) if match.group(4) else None
    modifier = int(match.group(5)) if match.group(5) else 0

    if die_size == 100 and num_dice == 1:
        return {"roll_type": "percentile", "modifier": modifier}

    if die_size == 3 and num_dice == 1 and not keep_type:
        return {"roll_type": "d3", "modifier": modifier}

    if keep_type and keep_num is None:
        keep_num = num_dice

    return {
        "roll_type": "pool",
        "num_dice": num_dice,
        "die_size": die_size,
        "keep_type": keep_type,
        "keep_num": keep_num,
        "modifier": modifier,
    }


def roll_percentile(modifier: int = 0) -> Dict[str, Any]:
    """Roll d100 using tens + ones dice (00+0 = 100)."""
    tens = random.randint(0, 9) * 10
    ones = random.randint(0, 9)
    if tens == 0 and ones == 0:
        total = 100
    else:
        total = tens + ones
    total += modifier
    return {
        "notation": "d100",
        "roll_type": "percentile",
        "tens": tens // 10,
        "ones": ones,
        "rolls": [tens // 10, ones],
        "modifier": modifier,
        "total": total,
        "note": "Percentile roll (tens + ones)",
    }


def roll_d3(modifier: int = 0) -> Dict[str, Any]:
    """Roll d3 as ceil(d6 / 2)."""
    d6 = random.randint(1, 6)
    result = math.ceil(d6 / 2)
    total = result + modifier
    return {
        "notation": "d3",
        "roll_type": "d3",
        "underlying_d6": d6,
        "rolls": [result],
        "modifier": modifier,
        "total": total,
        "note": f"d3 via d6={d6} (ceil half)",
    }


def roll_single_pool(
    num_dice: int,
    die_size: int,
    keep_type: str = None,
    keep_num: int = None,
    exploding: bool = False,
) -> Dict[str, Any]:
    """Roll a pool of dice. Supports keep highest/lowest and basic exploding dice."""
    rolls = []
    for _ in range(num_dice):
        roll = random.randint(1, die_size)
        rolls.append(roll)
        while exploding and roll == die_size:
            roll = random.randint(1, die_size)
            rolls.append(roll)

    if keep_type == "kh" and keep_num:
        sorted_rolls = sorted(rolls, reverse=True)
        kept = sorted_rolls[:keep_num]
        dropped = sorted_rolls[keep_num:]
        total = sum(kept)
        return {"rolls": rolls, "kept": kept, "dropped": dropped, "total_before_modifier": total}
    if keep_type == "kl" and keep_num:
        sorted_rolls = sorted(rolls)
        kept = sorted_rolls[:keep_num]
        dropped = sorted_rolls[keep_num:]
        total = sum(kept)
        return {"rolls": rolls, "kept": kept, "dropped": dropped, "total_before_modifier": total}
    return {"rolls": rolls, "kept": rolls, "dropped": [], "total_before_modifier": sum(rolls)}


def roll_dice(
    notation: str,
    advantage: bool = False,
    disadvantage: bool = False,
    exploding: bool = False,
    campaign: Optional[str] = None,
) -> Dict[str, Any]:
    """Main rolling function with full D&D support + homebrew options."""
    cleaned, adv_from_notation, dis_from_notation = _strip_adv_disadv(notation)
    if not advantage:
        advantage = adv_from_notation
    if not disadvantage:
        disadvantage = dis_from_notation
    if advantage and disadvantage:
        advantage = False
        disadvantage = False

    parsed = parse_dice_notation(cleaned if cleaned else notation)
    roll_type = parsed.get("roll_type", "pool")
    modifier = parsed.get("modifier", 0)

    if roll_type == "percentile":
        result = roll_percentile(modifier)
        if campaign:
            _log_roll(campaign, notation, result["total"], {"type": "percentile"})
        return result

    if roll_type == "d3":
        result = roll_d3(modifier)
        if campaign:
            _log_roll(campaign, notation, result["total"], {"type": "d3", "d6": result["underlying_d6"]})
        return result

    num_dice = parsed["num_dice"]
    die_size = parsed["die_size"]
    keep_type = parsed.get("keep_type")
    keep_num = parsed.get("keep_num")

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
                "total_before_mod": roll1["total_before_modifier"],
            },
            "roll_2": {
                "rolls": roll2["rolls"],
                "kept": roll2.get("kept", roll2["rolls"]),
                "total_before_mod": roll2["total_before_modifier"],
            },
            "chosen": {
                "rolls": chosen_data["rolls"],
                "kept": chosen_data.get("kept", chosen_data["rolls"]),
                "total": chosen_total,
            },
            "modifier": modifier,
            "total": chosen_total,
            "note": note,
        }
        if campaign:
            _log_roll(campaign, notation, chosen_total, {"advantage": advantage or disadvantage})
        return result

    result = roll_single_pool(num_dice, die_size, keep_type, keep_num, exploding=exploding)
    total = result["total_before_modifier"] + modifier

    if campaign:
        _log_roll(
            campaign,
            notation,
            total,
            {
                "exploding": exploding,
                "kept": result.get("kept", result["rolls"]),
                "dropped": result.get("dropped", []),
            },
        )

    return {
        "notation": notation,
        "exploding": exploding,
        "rolls": result["rolls"],
        "kept": result.get("kept", result["rolls"]),
        "dropped": result.get("dropped", []),
        "modifier": modifier,
        "total": total,
        "note": "Exploding dice enabled" if exploding else "",
    }


def _log_roll(campaign: str, notation: str, total: int, metadata: Dict[str, Any]) -> None:
    try:
        sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))
        from dnd_state_utils import log_roll
        log_roll(campaign, notation, total, metadata)
    except Exception:
        pass


def roll_initiative(modifier: int = 0, *, campaign: Optional[str] = None) -> Dict[str, Any]:
    """Roll 1d20 + modifier for initiative order."""
    base = roll_dice("1d20", campaign=campaign)
    total = base["total"] + modifier
    return {
        "type": "initiative",
        "roll": base,
        "modifier": modifier,
        "initiative_total": total,
    }


def roll_d20_check(
    modifier: int = 0,
    *,
    advantage: bool = False,
    disadvantage: bool = False,
    check_type: str = "check",
    dc: Optional[int] = None,
    campaign: Optional[str] = None,
) -> Dict[str, Any]:
    """Roll a standard 1d20 check (ability check, attack, or save)."""
    result = roll_dice(
        "1d20",
        advantage=advantage,
        disadvantage=disadvantage,
        campaign=campaign,
    )
    total = result["total"] + modifier
    outcome: Dict[str, Any] = {
        "type": check_type,
        "roll": result,
        "modifier": modifier,
        "total": total,
        "version": DICE_BACKEND_VERSION,
    }
    if dc is not None:
        outcome["dc"] = dc
        outcome["success"] = total >= dc
    return outcome


def get_roll_history(campaign: str, *, limit: int = 10) -> Dict[str, Any]:
    """Return recent rolls logged for a campaign."""
    try:
        sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))
        from paths import get_campaign_path  # noqa: E402

        path = get_campaign_path(campaign) / "state" / "rolls.json"
        if not path.exists():
            return {"campaign": campaign, "rolls": [], "count": 0, "version": DICE_BACKEND_VERSION}
        data = json.loads(path.read_text(encoding="utf-8"))
        rolls = data if isinstance(data, list) else data.get("rolls", [])
        recent = rolls[-limit:] if limit else rolls
        return {
            "campaign": campaign,
            "rolls": recent,
            "count": len(rolls),
            "version": DICE_BACKEND_VERSION,
        }
    except Exception as exc:
        return {"campaign": campaign, "rolls": [], "error": str(exc), "version": DICE_BACKEND_VERSION}


if __name__ == "__main__":
    import argparse

    KNOWN_CMDS = {
        "roll", "initiative", "parse", "percentile", "check", "attack", "save", "history",
    }
    argv = sys.argv[1:]
    if argv and argv[0] not in KNOWN_CMDS and argv[0] not in ("-h", "--help") and not argv[0].startswith("-"):
        argv = ["roll", *argv]
        sys.argv = [sys.argv[0], *argv]

    parser = argparse.ArgumentParser(
        description="Reliable D&D Dice Roller (supports 5e notation + keep highest/lowest + advantage/disadvantage)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_roll = sub.add_parser("roll", help="Roll dice notation e.g. 1d20+5, 4d6kh3")
    p_roll.add_argument("notation")
    p_roll.add_argument("--advantage", action="store_true")
    p_roll.add_argument("--disadvantage", action="store_true")
    p_roll.add_argument("--exploding", action="store_true")
    p_roll.add_argument("--campaign")

    p_init = sub.add_parser("initiative", help="Roll 1d20 + modifier for initiative")
    p_init.add_argument("modifier", type=int, nargs="?", default=0)
    p_init.add_argument("--campaign")

    p_parse = sub.add_parser("parse", help="Parse dice notation without rolling")
    p_parse.add_argument("notation")

    p_pct = sub.add_parser("percentile", help="Roll d100 (percentile)")
    p_pct.add_argument("modifier", type=int, nargs="?", default=0)
    p_pct.add_argument("--campaign")

    for name, help_text in (
        ("check", "Ability check: 1d20 + modifier"),
        ("attack", "Attack roll: 1d20 + modifier"),
        ("save", "Saving throw: 1d20 + modifier"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("modifier", type=int, nargs="?", default=0)
        p.add_argument("--advantage", action="store_true")
        p.add_argument("--disadvantage", action="store_true")
        p.add_argument("--dc", type=int)
        p.add_argument("--campaign")

    p_hist = sub.add_parser("history", help="Recent rolls logged for a campaign")
    p_hist.add_argument("campaign")
    p_hist.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()

    try:
        if args.cmd == "initiative":
            result = roll_initiative(args.modifier, campaign=args.campaign)
        elif args.cmd == "parse":
            result = {"parsed": parse_dice_notation(args.notation), "version": DICE_BACKEND_VERSION}
        elif args.cmd == "percentile":
            result = roll_percentile(args.modifier)
            result["version"] = DICE_BACKEND_VERSION
        elif args.cmd in ("check", "attack", "save"):
            result = roll_d20_check(
                args.modifier,
                advantage=args.advantage,
                disadvantage=args.disadvantage,
                check_type=args.cmd,
                dc=args.dc,
                campaign=args.campaign,
            )
        elif args.cmd == "history":
            result = get_roll_history(args.campaign, limit=args.limit)
        else:
            result = roll_dice(
                args.notation,
                args.advantage,
                args.disadvantage,
                args.exploding,
                campaign=args.campaign,
            )
            result["version"] = DICE_BACKEND_VERSION
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)