#!/usr/bin/env python3
"""
Comprehensive D&D Dice Roller (production v3+)

Major expansion: multi-pool expressions, fudge dice, per-pool keep/exploding,
reroll-below, resistance/vulnerability/immunity, success counting, and richer
result objects for downstream skills (combat, loot, session logging).

Backward compatible with simple notation (2d6+3, 4d6kh3, 1d20+5) and existing CLI flags.
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

DICE_BACKEND_VERSION = "3.3.0"

DieSize = Union[int, str]


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


def _parse_single_pool_term(term: str) -> Dict[str, Any]:
    """Parse one dice term like '2d6kh3!', 'd20', '4d6k3', '1d8', '4dF'."""
    term = term.lower().strip()

    if term in ("d100", "1d100", "d%", "1d%"):
        return {
            "num_dice": 1,
            "die_size": 100,
            "keep_type": None,
            "keep_num": None,
            "exploding": False,
            "is_fudge": False,
            "is_percentile": True,
        }

    if term in ("d3", "1d3"):
        return {
            "num_dice": 1,
            "die_size": 3,
            "keep_type": None,
            "keep_num": None,
            "exploding": False,
            "is_fudge": False,
            "is_d3": True,
        }

    if "df" in term or re.fullmatch(r"\d*f", term):
        fudge_match = re.match(r"(\d*)df?", term)
        if fudge_match:
            num = int(fudge_match.group(1)) if fudge_match.group(1) else 1
            return {
                "num_dice": num,
                "die_size": "F",
                "keep_type": None,
                "keep_num": None,
                "exploding": False,
                "is_fudge": True,
            }

    exploding = False
    if "!" in term or term.endswith("x"):
        exploding = True
        term = term.replace("!", "").rstrip("x")

    term = re.sub(r"d(\d+)(k)(\d+)", r"d\1kh\3", term)
    if "dl" in term:
        term = term.replace("dl", "kl")

    match = re.match(r"(\d*)d(\d+)(kh|kl)?(\d+)?", term)
    if not match:
        raise ValueError(f"Invalid dice term: {term}")

    num_dice = int(match.group(1)) if match.group(1) else 1
    die_size = int(match.group(2))
    keep_type = match.group(3)
    keep_num = int(match.group(4)) if match.group(4) else None

    if keep_type and keep_num is None:
        keep_num = num_dice

    return {
        "num_dice": num_dice,
        "die_size": die_size,
        "keep_type": keep_type,
        "keep_num": keep_num,
        "exploding": exploding,
        "is_fudge": False,
    }


def _legacy_single_pool_parse(notation: str) -> Optional[Dict[str, Any]]:
    """Fallback parser for simple legacy single-pool strings."""
    notation = notation.lower().replace(" ", "")

    if notation in ("d100", "1d100", "percentile", "d%"):
        return {"roll_type": "percentile", "modifier": 0}

    if notation in ("d3", "1d3"):
        return {"roll_type": "d3", "modifier": 0}

    match = re.match(r"(\d*)d(\d+)(kh|kl)?(\d+)?([+-]\d+)?", notation)
    if not match:
        return None

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


def _to_legacy_parse(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Convert multi-pool parse to legacy single-pool dict when possible."""
    pools = parsed.get("pools", [])
    if len(pools) != 1:
        return parsed

    pool = pools[0]
    if pool.get("is_fudge") or pool.get("sign", 1) < 0:
        return parsed

    modifier = parsed.get("flat_modifier", 0)
    die_size = pool["die_size"]

    if pool.get("is_percentile") or die_size == 100:
        return {"roll_type": "percentile", "modifier": modifier}

    if pool.get("is_d3") or die_size == 3:
        return {"roll_type": "d3", "modifier": modifier}

    return {
        "roll_type": "pool",
        "num_dice": pool["num_dice"],
        "die_size": die_size,
        "keep_type": pool.get("keep_type"),
        "keep_num": pool.get("keep_num"),
        "modifier": modifier,
        "exploding": pool.get("exploding") or parsed.get("exploding", False),
        "advantage": parsed.get("advantage", False),
        "disadvantage": parsed.get("disadvantage", False),
    }


def parse_dice_notation(notation: str) -> Dict[str, Any]:
    """Parse complex D&D dice notation including multi-pool damage rolls."""
    original = notation.strip()
    n = original.lower().replace(" ", "")

    if n in ("d100", "1d100", "percentile", "d%"):
        return {"roll_type": "percentile", "modifier": 0}

    if n in ("d3", "1d3"):
        return {"roll_type": "d3", "modifier": 0}

    advantage = any(x in n for x in ("adv", "advantage"))
    disadvantage = any(x in n for x in ("disadv", "disadvantage"))
    if advantage and disadvantage:
        advantage = False
        disadvantage = False

    global_exploding = "!" in n or n.endswith("x") or "exploding" in n
    work = re.sub(r"(adv|advantage|disadv|disadvantage|exploding)", "", n)

    term_pattern = r"([+-]?(?:\d*d\d+[a-z0-9!]*|\d*df?|\d+f|\d+))"
    raw_terms = re.findall(term_pattern, work)

    pools: List[Dict[str, Any]] = []
    flat_modifier = 0

    for raw in raw_terms:
        raw = raw.strip()
        if not raw:
            continue
        sign = -1 if raw.startswith("-") else 1
        term = raw.lstrip("+-")

        if "d" in term or term.endswith("f"):
            try:
                pool = _parse_single_pool_term(term)
                pool["sign"] = sign
                pool["original_term"] = raw
                pools.append(pool)
            except ValueError:
                pass
        else:
            try:
                flat_modifier += sign * int(term)
            except ValueError:
                pass

    if not pools:
        legacy = _legacy_single_pool_parse(original)
        if legacy:
            return legacy
        raise ValueError(f"Invalid dice notation: {notation}")

    parsed_multi = {
        "roll_type": "multi_pool",
        "original_notation": original,
        "pools": pools,
        "flat_modifier": flat_modifier,
        "advantage": advantage,
        "disadvantage": disadvantage,
        "exploding": global_exploding,
    }

    if len(pools) == 1 and not pools[0].get("is_fudge"):
        legacy = _to_legacy_parse(parsed_multi)
        if legacy.get("roll_type") in ("percentile", "d3", "pool"):
            return legacy

    return parsed_multi


def roll_fudge_die() -> int:
    """Roll one fudge die: -1, 0, or +1."""
    return random.choice([-1, 0, 1])


def roll_single_pool(
    num_dice: int,
    die_size: DieSize,
    keep_type: Optional[str] = None,
    keep_num: Optional[int] = None,
    exploding: bool = False,
    reroll_below: Optional[int] = None,
) -> Dict[str, Any]:
    """Roll a pool with keep/drop, exploding, reroll-below, and fudge support."""
    if die_size == "F" or die_size == "f":
        rolls = [roll_fudge_die() for _ in range(num_dice)]
        total = sum(rolls)
        return {
            "rolls": rolls,
            "kept": rolls,
            "dropped": [],
            "total_before_modifier": total,
            "die_type": "fudge",
        }

    rolls: List[int] = []
    for _ in range(num_dice):
        roll = random.randint(1, int(die_size))
        if reroll_below is not None and roll <= reroll_below:
            rerolled = random.randint(1, int(die_size))
            rolls.extend([roll, rerolled])
        else:
            rolls.append(roll)
        last = rolls[-1]
        while exploding and last == int(die_size):
            extra = random.randint(1, int(die_size))
            rolls.append(extra)
            last = extra

    if keep_type == "kh" and keep_num:
        sorted_rolls = sorted(rolls, reverse=True)
        kept = sorted_rolls[:keep_num]
        dropped = sorted_rolls[keep_num:]
        total = sum(kept)
    elif keep_type == "kl" and keep_num:
        sorted_rolls = sorted(rolls)
        kept = sorted_rolls[:keep_num]
        dropped = sorted_rolls[keep_num:]
        total = sum(kept)
    else:
        kept = rolls
        dropped = []
        total = sum(rolls)

    return {
        "rolls": rolls,
        "kept": kept,
        "dropped": dropped,
        "total_before_modifier": total,
    }


def roll_percentile(modifier: int = 0) -> Dict[str, Any]:
    """Roll d100 using tens + ones dice (00+0 = 100)."""
    tens = random.randint(0, 9) * 10
    ones = random.randint(0, 9)
    total = 100 if tens == 0 and ones == 0 else tens + ones
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


def _roll_multi_pool(
    parsed: Dict[str, Any],
    *,
    exploding: bool = False,
    reroll_below: Optional[int] = None,
) -> Dict[str, Any]:
    """Roll all pools in a multi-pool expression and sum signed contributions."""
    pool_results: List[Dict[str, Any]] = []
    subtotal = parsed.get("flat_modifier", 0)

    for pool in parsed.get("pools", []):
        pool_exploding = pool.get("exploding") or exploding or parsed.get("exploding", False)
        rolled = roll_single_pool(
            pool["num_dice"],
            pool["die_size"],
            pool.get("keep_type"),
            pool.get("keep_num"),
            exploding=pool_exploding,
            reroll_below=reroll_below,
        )
        signed = rolled["total_before_modifier"] * pool.get("sign", 1)
        subtotal += signed
        pool_results.append({
            "term": pool.get("original_term", ""),
            "sign": pool.get("sign", 1),
            "die_size": pool["die_size"],
            "rolls": rolled["rolls"],
            "kept": rolled.get("kept", rolled["rolls"]),
            "dropped": rolled.get("dropped", []),
            "subtotal": signed,
            "is_fudge": pool.get("is_fudge", False),
        })

    return {
        "roll_type": "multi_pool",
        "notation": parsed.get("original_notation", ""),
        "pools": pool_results,
        "flat_modifier": parsed.get("flat_modifier", 0),
        "total": subtotal,
        "modifier": parsed.get("flat_modifier", 0),
    }


def roll_dice(
    notation: str,
    advantage: bool = False,
    disadvantage: bool = False,
    exploding: bool = False,
    campaign: Optional[str] = None,
    reroll_below: Optional[int] = None,
    resistance: bool = False,
    vulnerability: bool = False,
    immunity: bool = False,
    flat_reduction: int = 0,
) -> Dict[str, Any]:
    """Main rolling function with single-pool, multi-pool, and adv/disadv support."""
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

    if roll_type == "percentile":
        result = roll_percentile(parsed.get("modifier", 0))
        result["version"] = DICE_BACKEND_VERSION
        if campaign:
            _log_roll(campaign, notation, result["total"], {"type": "percentile"})
        return _maybe_apply_damage_modifiers(result, resistance, vulnerability, immunity, flat_reduction)

    if roll_type == "d3":
        result = roll_d3(parsed.get("modifier", 0))
        result["version"] = DICE_BACKEND_VERSION
        if campaign:
            _log_roll(campaign, notation, result["total"], {"type": "d3", "d6": result["underlying_d6"]})
        return _maybe_apply_damage_modifiers(result, resistance, vulnerability, immunity, flat_reduction)

    if roll_type == "multi_pool":
        pools = parsed.get("pools", [])
        has_d20 = any(p.get("die_size") == 20 and p.get("num_dice", 1) == 1 for p in pools)
        if (advantage or disadvantage) and has_d20 and len(pools) == 1:
            modifier = parsed.get("flat_modifier", 0)
            roll1 = roll_single_pool(1, 20, reroll_below=reroll_below)
            roll2 = roll_single_pool(1, 20, reroll_below=reroll_below)
            total1 = roll1["total_before_modifier"] + modifier
            total2 = roll2["total_before_modifier"] + modifier
            if advantage:
                chosen_total = max(total1, total2)
                chosen_data = roll1 if total1 >= total2 else roll2
                note = "Advantage — took higher result"
                result = {
                    "notation": notation,
                    "advantage": True,
                    "roll_1": {"rolls": roll1["rolls"], "kept": roll1["kept"], "total_before_mod": roll1["total_before_modifier"]},
                    "roll_2": {"rolls": roll2["rolls"], "kept": roll2["kept"], "total_before_mod": roll2["total_before_modifier"]},
                    "chosen": {"rolls": chosen_data["rolls"], "kept": chosen_data["kept"], "total": chosen_total},
                    "modifier": modifier,
                    "total": chosen_total,
                    "note": note,
                    "version": DICE_BACKEND_VERSION,
                }
            else:
                chosen_total = min(total1, total2)
                chosen_data = roll1 if total1 <= total2 else roll2
                note = "Disadvantage — took lower result"
                result = {
                    "notation": notation,
                    "disadvantage": True,
                    "roll_1": {"rolls": roll1["rolls"], "kept": roll1["kept"], "total_before_mod": roll1["total_before_modifier"]},
                    "roll_2": {"rolls": roll2["rolls"], "kept": roll2["kept"], "total_before_mod": roll2["total_before_modifier"]},
                    "chosen": {"rolls": chosen_data["rolls"], "kept": chosen_data["kept"], "total": chosen_total},
                    "modifier": modifier,
                    "total": chosen_total,
                    "note": note,
                    "version": DICE_BACKEND_VERSION,
                }
            if campaign:
                _log_roll(campaign, notation, chosen_total, {"advantage": advantage or disadvantage})
            return _maybe_apply_damage_modifiers(result, resistance, vulnerability, immunity, flat_reduction)

        result = _roll_multi_pool(parsed, exploding=exploding, reroll_below=reroll_below)
        result["version"] = DICE_BACKEND_VERSION
        if campaign:
            _log_roll(campaign, notation, result["total"], {"pools": len(result.get("pools", []))})
        return _maybe_apply_damage_modifiers(result, resistance, vulnerability, immunity, flat_reduction)

    num_dice = parsed["num_dice"]
    die_size = parsed["die_size"]
    keep_type = parsed.get("keep_type")
    keep_num = parsed.get("keep_num")
    modifier = parsed.get("modifier", 0)
    pool_exploding = exploding or parsed.get("exploding", False)

    if (advantage or disadvantage) and die_size == 20:
        roll1 = roll_single_pool(num_dice, die_size, keep_type, keep_num, reroll_below=reroll_below)
        roll2 = roll_single_pool(num_dice, die_size, keep_type, keep_num, reroll_below=reroll_below)
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
            "version": DICE_BACKEND_VERSION,
        }
        if campaign:
            _log_roll(campaign, notation, chosen_total, {"advantage": advantage or disadvantage})
        return _maybe_apply_damage_modifiers(result, resistance, vulnerability, immunity, flat_reduction)

    rolled = roll_single_pool(
        num_dice, die_size, keep_type, keep_num,
        exploding=pool_exploding, reroll_below=reroll_below,
    )
    total = rolled["total_before_modifier"] + modifier

    if campaign:
        _log_roll(
            campaign,
            notation,
            total,
            {
                "exploding": pool_exploding,
                "kept": rolled.get("kept", rolled["rolls"]),
                "dropped": rolled.get("dropped", []),
            },
        )

    result = {
        "notation": notation,
        "exploding": pool_exploding,
        "rolls": rolled["rolls"],
        "kept": rolled.get("kept", rolled["rolls"]),
        "dropped": rolled.get("dropped", []),
        "modifier": modifier,
        "total": total,
        "note": "Exploding dice enabled" if pool_exploding else "",
        "version": DICE_BACKEND_VERSION,
    }
    return _maybe_apply_damage_modifiers(result, resistance, vulnerability, immunity, flat_reduction)


def _maybe_apply_damage_modifiers(
    result: Dict[str, Any],
    resistance: bool,
    vulnerability: bool,
    immunity: bool,
    flat_reduction: int,
) -> Dict[str, Any]:
    if not any((resistance, vulnerability, immunity, flat_reduction)):
        return result
    mod = apply_damage_modifiers(
        result.get("total", 0),
        resistance=resistance,
        vulnerability=vulnerability,
        immunity=immunity,
        flat_reduction=flat_reduction,
    )
    result["damage_modifiers"] = mod
    result["total"] = mod["final"]
    return result


def apply_damage_modifiers(
    base_total: int,
    *,
    resistance: bool = False,
    vulnerability: bool = False,
    immunity: bool = False,
    flat_reduction: int = 0,
) -> Dict[str, Any]:
    """Apply resistance / vulnerability / immunity / flat reduction."""
    if immunity:
        return {
            "base": base_total,
            "final": 0,
            "immunity": True,
            "resistance": False,
            "vulnerability": False,
            "flat_reduction": flat_reduction,
            "note": "Immunity — damage negated",
        }

    adjusted = base_total
    notes: List[str] = []

    if resistance:
        adjusted = math.floor(adjusted / 2)
        notes.append("Resistance — halved")
    if vulnerability:
        adjusted = adjusted * 2
        notes.append("Vulnerability — doubled")
    if flat_reduction:
        adjusted = max(0, adjusted - flat_reduction)
        notes.append(f"Flat reduction −{flat_reduction}")

    return {
        "base": base_total,
        "final": adjusted,
        "immunity": False,
        "resistance": resistance,
        "vulnerability": vulnerability,
        "flat_reduction": flat_reduction,
        "note": "; ".join(notes) if notes else "",
    }


def roll_crit(
    notation: str,
    *,
    crit_multiplier: int = 2,
    campaign: Optional[str] = None,
) -> Dict[str, Any]:
    """Roll damage notation and apply critical-hit dice doubling (default: double dice, not modifier)."""
    base = roll_dice(notation, campaign=campaign)
    if base.get("roll_type") == "multi_pool":
        doubled_total = base.get("flat_modifier", 0)
        doubled_pools = []
        for pool in base.get("pools", []):
            dice_sum = sum(pool.get("kept", pool.get("rolls", [])))
            doubled_dice = dice_sum * crit_multiplier
            signed = doubled_dice * pool.get("sign", 1)
            doubled_total += signed
            doubled_pools.append({**pool, "crit_dice_sum": doubled_dice, "subtotal": signed})
        result = {
            **base,
            "crit": True,
            "crit_multiplier": crit_multiplier,
            "pools": doubled_pools,
            "pre_crit_total": base["total"],
            "total": doubled_total,
            "note": f"Critical hit — damage dice ×{crit_multiplier}",
            "version": DICE_BACKEND_VERSION,
        }
    else:
        dice_sum = sum(base.get("kept", base.get("rolls", [])))
        modifier = base.get("modifier", 0)
        crit_total = dice_sum * crit_multiplier + modifier
        result = {
            **base,
            "crit": True,
            "crit_multiplier": crit_multiplier,
            "pre_crit_total": base["total"],
            "total": crit_total,
            "note": f"Critical hit — dice ×{crit_multiplier}, modifier kept",
            "version": DICE_BACKEND_VERSION,
        }
    if campaign:
        _log_roll(campaign, f"crit {notation}", result["total"], {"crit": True, "multiplier": crit_multiplier})
    return result


def count_successes(
    notation: str,
    target: int = 5,
    *,
    reroll_below: Optional[int] = None,
    explode_on: Optional[int] = None,
    campaign: Optional[str] = None,
) -> Dict[str, Any]:
    """Count successes for target-number systems (e.g. dice >= target)."""
    parsed = parse_dice_notation(notation)
    if parsed.get("roll_type") == "multi_pool":
        all_rolls: List[int] = []
        for pool in parsed.get("pools", []):
            if pool.get("is_fudge"):
                continue
            rolled = roll_single_pool(
                pool["num_dice"],
                pool["die_size"],
                pool.get("keep_type"),
                pool.get("keep_num"),
                exploding=bool(explode_on),
                reroll_below=reroll_below,
            )
            all_rolls.extend(rolled["rolls"])
    else:
        rolled = roll_single_pool(
            parsed.get("num_dice", 1),
            parsed.get("die_size", 6),
            parsed.get("keep_type"),
            parsed.get("keep_num"),
            exploding=bool(explode_on),
            reroll_below=reroll_below,
        )
        all_rolls = rolled["rolls"]

    successes = 0
    exploded = 0
    for value in all_rolls:
        if value >= target:
            successes += 1
        if explode_on is not None and value >= explode_on:
            extra = random.randint(1, int(parsed.get("die_size", 6)) if parsed.get("roll_type") != "multi_pool" else 6)
            exploded += 1
            if extra >= target:
                successes += 1
            all_rolls.append(extra)

    result = {
        "notation": notation,
        "target": target,
        "rolls": all_rolls,
        "successes": successes,
        "exploded_extra": exploded,
        "reroll_below": reroll_below,
        "explode_on": explode_on,
        "version": DICE_BACKEND_VERSION,
    }
    if campaign:
        _log_roll(campaign, notation, successes, {"type": "success_count", "target": target})
    return result


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
        "version": DICE_BACKEND_VERSION,
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
        "crit", "count-successes", "modify-damage",
    }
    argv = sys.argv[1:]
    if argv and argv[0] not in KNOWN_CMDS and argv[0] not in ("-h", "--help") and not argv[0].startswith("-"):
        argv = ["roll", *argv]
        sys.argv = [sys.argv[0], *argv]

    parser = argparse.ArgumentParser(
        description="Comprehensive D&D Dice Roller (5e + multi-pool + homebrew)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_roll = sub.add_parser("roll", help="Roll dice notation e.g. 1d20+5, 1d8+1d6+5")
    p_roll.add_argument("notation")
    p_roll.add_argument("--advantage", action="store_true")
    p_roll.add_argument("--disadvantage", action="store_true")
    p_roll.add_argument("--exploding", action="store_true")
    p_roll.add_argument("--reroll-below", type=int)
    p_roll.add_argument("--resistance", action="store_true")
    p_roll.add_argument("--vulnerability", action="store_true")
    p_roll.add_argument("--immunity", action="store_true")
    p_roll.add_argument("--flat-reduction", type=int, default=0)
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

    p_crit = sub.add_parser("crit", help="Critical hit damage (double dice by default)")
    p_crit.add_argument("notation")
    p_crit.add_argument("--multiplier", type=int, default=2)
    p_crit.add_argument("--campaign")

    p_succ = sub.add_parser("count-successes", help="Count dice meeting target number")
    p_succ.add_argument("notation")
    p_succ.add_argument("--target", type=int, default=5)
    p_succ.add_argument("--reroll-below", type=int)
    p_succ.add_argument("--explode-on", type=int)
    p_succ.add_argument("--campaign")

    p_mod = sub.add_parser("modify-damage", help="Apply resistance/vulnerability/immunity to a total")
    p_mod.add_argument("total", type=int)
    p_mod.add_argument("--resistance", action="store_true")
    p_mod.add_argument("--vulnerability", action="store_true")
    p_mod.add_argument("--immunity", action="store_true")
    p_mod.add_argument("--flat-reduction", type=int, default=0)

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
        elif args.cmd == "crit":
            result = roll_crit(args.notation, crit_multiplier=args.multiplier, campaign=args.campaign)
        elif args.cmd == "count-successes":
            result = count_successes(
                args.notation,
                target=args.target,
                reroll_below=args.reroll_below,
                explode_on=args.explode_on,
                campaign=args.campaign,
            )
        elif args.cmd == "modify-damage":
            result = apply_damage_modifiers(
                args.total,
                resistance=args.resistance,
                vulnerability=args.vulnerability,
                immunity=args.immunity,
                flat_reduction=args.flat_reduction,
            )
            result["version"] = DICE_BACKEND_VERSION
        else:
            result = roll_dice(
                args.notation,
                args.advantage,
                args.disadvantage,
                args.exploding,
                campaign=args.campaign,
                reroll_below=args.reroll_below,
                resistance=args.resistance,
                vulnerability=args.vulnerability,
                immunity=args.immunity,
                flat_reduction=args.flat_reduction,
            )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)