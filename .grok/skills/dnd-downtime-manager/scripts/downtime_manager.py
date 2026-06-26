#!/usr/bin/env python3
"""Short/long rests, hit dice spending, and downtime activity logging."""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"))

from bootstrap import ensure_utils_importable

ensure_utils_importable()

from dnd_state_utils import get_player_character, load_json, save_json  # noqa: E402
from class_progression import restore_spell_slots_on_long_rest  # noqa: E402
from event_system import record_event  # noqa: E402
from paths import get_campaign_path  # noqa: E402

DOWNTIME_BACKEND_VERSION = "4.0.0"

CLASS_HIT_DIE = {
    "barbarian": 12,
    "fighter": 10,
    "paladin": 10,
    "ranger": 10,
    "bard": 8,
    "cleric": 8,
    "druid": 8,
    "monk": 8,
    "rogue": 8,
    "warlock": 8,
    "sorcerer": 6,
    "wizard": 6,
}


def _char_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "player_character.json"


def _primary_hit_die(char: Dict[str, Any]) -> int:
    classes = char.get("classes", [{"name": "Fighter", "level": 1}])
    primary = classes[0].get("name", "Fighter").lower()
    return CLASS_HIT_DIE.get(primary, 8)


def _ability_mod(char: Dict[str, Any], stat: str = "con") -> int:
    return (char.get("stats", {}).get(stat, 10) - 10) // 2


def _ensure_hit_dice(char: Dict[str, Any]) -> Dict[str, Any]:
    hd = char.setdefault("hit_dice", {})
    if "total" not in hd:
        hd["total"] = char.get("level", 1)
    if "spent" not in hd:
        hd["spent"] = 0
    hd["die_size"] = hd.get("die_size") or _primary_hit_die(char)
    return hd


def roll_hit_die(campaign_name: str, *, count: int = 1) -> Dict[str, Any]:
    """Roll hit dice for healing (used by short rest and spend-hit-dice)."""
    char = load_json(_char_path(campaign_name), {})
    hd = _ensure_hit_dice(char)
    available = max(0, hd.get("total", 1) - hd.get("spent", 0))
    spend = min(count, available)
    die_size = hd.get("die_size", 8)
    con_mod = _ability_mod(char)
    rolls = [random.randint(1, die_size) for _ in range(spend)]
    healed = sum(max(1, r + con_mod) for r in rolls)

    hp = char.setdefault("hit_points", {"current": 10, "max": 10, "temp": 0})
    hp["current"] = min(hp.get("max", hp["current"]), hp.get("current", 0) + healed)
    hd["spent"] = hd.get("spent", 0) + spend
    char["hit_points"] = hp
    char["hit_dice"] = hd
    save_json(_char_path(campaign_name), char)

    return {
        "rolls": rolls,
        "healed": healed,
        "hit_dice_spent": spend,
        "hp": hp,
        "die_size": die_size,
    }


def short_rest(campaign_name: str, *, spend_hd: int = 0) -> Dict[str, Any]:
    healed = 0
    roll_result: Optional[Dict[str, Any]] = None
    if spend_hd > 0:
        roll_result = roll_hit_die(campaign_name, count=spend_hd)
        healed = roll_result["healed"]

    char = get_player_character(campaign_name)
    record_event(
        campaign_name,
        f"Short rest (healed {healed} HP)",
        tags=["rest", "short-rest"],
        metadata={"hit_dice_spent": spend_hd},
    )
    return {
        "rest": "short",
        "hp": char.get("hit_points", {}),
        "hit_dice": char.get("hit_dice", {}),
        "hit_dice_spent": spend_hd,
        "healed": healed,
        "roll_detail": roll_result,
    }


def long_rest(campaign_name: str) -> Dict[str, Any]:
    char = load_json(_char_path(campaign_name), {})
    hp = char.setdefault("hit_points", {"current": 10, "max": 10, "temp": 0})
    hp["current"] = hp.get("max", hp["current"])
    hp["temp"] = 0
    char["hit_points"] = hp
    level = char.get("level", 1)
    recovered_hd = max(1, level // 2)
    hd = _ensure_hit_dice(char)
    hd["spent"] = max(0, hd.get("spent", 0) - recovered_hd)
    char["hit_dice"] = hd
    char["death_saves"] = {"successes": 0, "failures": 0, "status": "stable"}
    if char.get("status") in ("Dying", "Dead", "Stable (0 HP)"):
        char["status"] = "Alive"
    char["conditions"] = [c for c in char.get("conditions", []) if c not in ("Exhaustion",)]
    restored_slots = restore_spell_slots_on_long_rest(char.get("classes", []))
    if restored_slots.get("slots"):
        char["spell_slots"] = {
            "max": restored_slots["slots"],
            "used": restored_slots["slots_used"],
            "pact_magic": restored_slots.get("pact_magic"),
            "pact_slots_used": restored_slots.get("pact_slots_used", 0),
        }
    save_json(_char_path(campaign_name), char)

    record_event(campaign_name, "Long rest completed", importance="normal", tags=["rest", "long-rest"])
    return {
        "rest": "long",
        "hp": hp,
        "status": char.get("status"),
        "hit_dice_recovered": recovered_hd,
        "hit_dice": hd,
        "spell_slots": char.get("spell_slots"),
    }


def log_downtime_activity(
    campaign_name: str,
    activity: str,
    *,
    days: int = 1,
    outcome: str = "",
) -> Dict[str, Any]:
    log_path = get_campaign_path(campaign_name) / "logs" / "downtime_log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n### {activity} ({stamp}, {days} day(s))\n"
    if outcome:
        entry += f"{outcome}\n"
    if log_path.exists():
        log_path.write_text(log_path.read_text(encoding="utf-8").rstrip() + entry, encoding="utf-8")
    else:
        log_path.write_text(f"# Downtime Log — {campaign_name}{entry}", encoding="utf-8")

    record_event(
        campaign_name,
        f"Downtime: {activity} ({days} days)",
        tags=["downtime"],
        metadata={"activity": activity, "days": days, "outcome": outcome},
    )
    return {"logged": str(log_path), "activity": activity, "days": days}


def list_downtime_activities(campaign_name: str, *, limit: int = 20) -> Dict[str, Any]:
    log_path = get_campaign_path(campaign_name) / "logs" / "downtime_log.md"
    if not log_path.exists():
        return {"activities": [], "path": str(log_path)}
    text = log_path.read_text(encoding="utf-8")
    sections = [s.strip() for s in text.split("### ") if s.strip()]
    entries = []
    for section in sections[-limit:]:
        lines = section.splitlines()
        title = lines[0] if lines else section
        body = "\n".join(lines[1:]).strip()
        entries.append({"title": title, "body": body})
    return {"activities": entries, "path": str(log_path), "count": len(entries)}


def get_rest_status(campaign_name: str) -> Dict[str, Any]:
    char = get_player_character(campaign_name)
    hd = _ensure_hit_dice(char)
    return {
        "version": DOWNTIME_BACKEND_VERSION,
        "hp": char.get("hit_points", {}),
        "hit_dice": hd,
        "status": char.get("status", "Alive"),
        "conditions": char.get("conditions", []),
        "available_hit_dice": max(0, hd.get("total", 1) - hd.get("spent", 0)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="D&D downtime and rest manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_short = sub.add_parser("short-rest")
    p_short.add_argument("campaign")
    p_short.add_argument("--spend-hd", type=int, default=0)

    p_long = sub.add_parser("long-rest")
    p_long.add_argument("campaign")

    p_hd = sub.add_parser("spend-hit-dice")
    p_hd.add_argument("campaign")
    p_hd.add_argument("count", type=int, nargs="?", default=1)

    p_log = sub.add_parser("log-activity")
    p_log.add_argument("campaign")
    p_log.add_argument("activity")
    p_log.add_argument("--days", type=int, default=1)
    p_log.add_argument("--outcome", default="")

    p_list = sub.add_parser("list-activities")
    p_list.add_argument("campaign")
    p_list.add_argument("--limit", type=int, default=20)

    p_status = sub.add_parser("status")
    p_status.add_argument("campaign")

    args = parser.parse_args()

    if args.cmd == "short-rest":
        result = short_rest(args.campaign, spend_hd=args.spend_hd)
    elif args.cmd == "long-rest":
        result = long_rest(args.campaign)
    elif args.cmd == "spend-hit-dice":
        result = roll_hit_die(args.campaign, count=args.count)
    elif args.cmd == "log-activity":
        result = log_downtime_activity(args.campaign, args.activity, days=args.days, outcome=args.outcome)
    elif args.cmd == "list-activities":
        result = list_downtime_activities(args.campaign, limit=args.limit)
    elif args.cmd == "status":
        result = get_rest_status(args.campaign)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()