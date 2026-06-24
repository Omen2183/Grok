#!/usr/bin/env python3
"""Short/long rests, hit dice spending, and downtime activity logging."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from dnd_state_utils import get_player_character, load_json, save_json, update_player_hp  # noqa: E402
from event_system import record_event  # noqa: E402
from paths import get_campaign_path  # noqa: E402


def _char_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "player_character.json"


def short_rest(campaign_name: str, *, spend_hd: int = 0) -> Dict[str, Any]:
    """Short rest: optionally spend hit dice to heal."""
    char = load_json(_char_path(campaign_name), {})
    hp = char.setdefault("hit_points", {"current": 10, "max": 10, "temp": 0})
    hit_dice = char.setdefault("hit_dice", {"total": char.get("level", 1), "spent": 0})
    healed = 0

    if spend_hd > 0:
        available = hit_dice.get("total", 1) - hit_dice.get("spent", 0)
        spend = min(spend_hd, max(0, available))
        # Simplified: each HD heals avg of primary class die (d8 default) + CON mod
        con_mod = (char.get("stats", {}).get("con", 10) - 10) // 2
        per_die = 5 + con_mod  # average d8 + mod
        healed = spend * max(1, per_die)
        hit_dice["spent"] = hit_dice.get("spent", 0) + spend
        hp["current"] = min(hp.get("max", hp["current"]), hp.get("current", 0) + healed)
        char["hit_dice"] = hit_dice
        char["hit_points"] = hp
        save_json(_char_path(campaign_name), char)

    record_event(campaign_name, f"Short rest (healed {healed} HP)", tags=["rest", "short-rest"])
    return {
        "rest": "short",
        "hp": hp,
        "hit_dice_spent": spend_hd if spend_hd else 0,
        "healed": healed,
    }


def long_rest(campaign_name: str) -> Dict[str, Any]:
    """Long rest: restore HP, reset hit dice spent, clear death saves."""
    char = load_json(_char_path(campaign_name), {})
    hp = char.setdefault("hit_points", {"current": 10, "max": 10, "temp": 0})
    hp["current"] = hp.get("max", hp["current"])
    hp["temp"] = 0
    char["hit_points"] = hp
    char["hit_dice"] = {"total": char.get("level", 1), "spent": 0}
    char["death_saves"] = {"successes": 0, "failures": 0, "status": "stable"}
    if char.get("status") in ("Dying", "Dead", "Stable (0 HP)"):
        char["status"] = "Alive"
    char["conditions"] = [c for c in char.get("conditions", []) if c not in ("Exhaustion",)]
    save_json(_char_path(campaign_name), char)

    record_event(campaign_name, "Long rest completed", importance="normal", tags=["rest", "long-rest"])
    return {"rest": "long", "hp": hp, "status": char.get("status")}


def log_downtime_activity(
    campaign_name: str,
    activity: str,
    *,
    days: int = 1,
    outcome: str = "",
) -> Dict[str, Any]:
    """Record a downtime activity and append to downtime log."""
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


def get_rest_status(campaign_name: str) -> Dict[str, Any]:
    char = get_player_character(campaign_name)
    return {
        "hp": char.get("hit_points", {}),
        "hit_dice": char.get("hit_dice", {}),
        "status": char.get("status", "Alive"),
        "conditions": char.get("conditions", []),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="D&D downtime and rest manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_short = sub.add_parser("short-rest")
    p_short.add_argument("campaign")
    p_short.add_argument("--spend-hd", type=int, default=0)

    p_long = sub.add_parser("long-rest")
    p_long.add_argument("campaign")

    p_log = sub.add_parser("log-activity")
    p_log.add_argument("campaign")
    p_log.add_argument("activity")
    p_log.add_argument("--days", type=int, default=1)
    p_log.add_argument("--outcome", default="")

    p_status = sub.add_parser("status")
    p_status.add_argument("campaign")

    args = parser.parse_args()

    if args.cmd == "short-rest":
        result = short_rest(args.campaign, spend_hd=args.spend_hd)
    elif args.cmd == "long-rest":
        result = long_rest(args.campaign)
    elif args.cmd == "log-activity":
        result = log_downtime_activity(args.campaign, args.activity, days=args.days, outcome=args.outcome)
    elif args.cmd == "status":
        result = get_rest_status(args.campaign)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()