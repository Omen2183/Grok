#!/usr/bin/env python3
"""Lightweight 5e rules quick-reference for Grok DM play."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List, Optional

CHEATSHEET: Dict[str, Dict[str, Any]] = {
    "advantage": {
        "summary": "Roll 2d20, take the higher result.",
        "details": [
            "Multiple sources of advantage still roll only 2d20.",
            "Advantage and disadvantage on the same roll cancel out.",
        ],
    },
    "disadvantage": {
        "summary": "Roll 2d20, take the lower result.",
        "details": [
            "Multiple sources of disadvantage still roll only 2d20.",
            "Advantage and disadvantage cancel — roll a single d20.",
        ],
    },
    "concentration": {
        "summary": "One concentration spell at a time; CON save DC 10 or half damage taken (whichever higher).",
        "details": [
            "Lose concentration when incapacitated or when you cast another concentration spell.",
            "DM may call for CON save on environmental hazards while concentrating.",
        ],
    },
    "death_saves": {
        "summary": "At 0 HP: roll d20 each turn — 10+ success, 9- failure; 3 of either stabilizes or kills.",
        "details": [
            "Natural 20: regain 1 HP. Natural 1: counts as 2 failures.",
            "Damage while at 0 HP causes 1 failure (2 on crit).",
        ],
    },
    "opportunity_attack": {
        "summary": "When a creature you can see leaves your reach, one melee attack as a reaction.",
        "details": [
            "Disengage prevents opportunity attacks from that creature.",
            "Forced movement does not provoke unless the mover uses its own movement.",
        ],
    },
    "grapple": {
        "summary": "Special melee attack: Athletics vs Athletics or Acrobatics; target is grappled (speed 0).",
        "details": [
            "Escape: action, Athletics or Acrobatics vs grappler's Athletics.",
            "Moving a grappled creature costs double movement.",
        ],
    },
    "cover": {
        "summary": "Half cover +2 AC/DEX saves; three-quarters +5; total cover cannot be targeted.",
        "details": ["DM adjudicates line of sight and obstruction."],
    },
    "conditions": {
        "summary": "Standard conditions include Blinded, Charmed, Frightened, Grappled, Incapacitated, and more.",
        "details": [
            "Incapacitated: can't take actions or reactions.",
            "Unconscious: incapacitated, drops items, auto-fail STR/DEX saves, attacks have advantage.",
        ],
    },
}


def lookup_rule(topic: str) -> Dict[str, Any]:
    key = topic.lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "adv": "advantage",
        "disadv": "disadvantage",
        "death_save": "death_saves",
        "opportunity_attacks": "opportunity_attack",
        "grappling": "grapple",
    }
    key = aliases.get(key, key)
    if key not in CHEATSHEET:
        matches = [k for k in CHEATSHEET if key in k or k in key]
        if len(matches) == 1:
            key = matches[0]
        else:
            return {
                "found": False,
                "topic": topic,
                "available": sorted(CHEATSHEET.keys()),
            }
    entry = CHEATSHEET[key]
    return {"found": True, "topic": key, **entry}


def list_topics() -> List[str]:
    return sorted(CHEATSHEET.keys())


def main() -> None:
    parser = argparse.ArgumentParser(description="5e rules cheatsheet lookup")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list")
    p_lookup = sub.add_parser("lookup")
    p_lookup.add_argument("topic")

    args = parser.parse_args()
    if args.cmd == "list":
        result: Any = {"topics": list_topics()}
    else:
        result = lookup_rule(args.topic)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()