#!/usr/bin/env python3
"""CLI for mobile narration helpers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from narration_helpers import (  # noqa: E402
    format_combat_change,
    format_mobile_status,
    proactive_opening,
    suggest_next_actions,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="DM narration formatting helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_status = sub.add_parser("mobile-status")
    p_status.add_argument("campaign")

    p_open = sub.add_parser("opening")
    p_open.add_argument("campaign")

    p_suggest = sub.add_parser("suggest")
    p_suggest.add_argument("campaign")
    p_suggest.add_argument("--mode", choices=["tabletop", "kingdom"])

    p_hp = sub.add_parser("hp-change")
    p_hp.add_argument("target")
    p_hp.add_argument("before", type=int)
    p_hp.add_argument("after", type=int)
    p_hp.add_argument("--type", default="damage")

    args = parser.parse_args()

    if args.cmd == "mobile-status":
        result = {"status": format_mobile_status(args.campaign)}
    elif args.cmd == "opening":
        result = proactive_opening(args.campaign)
    elif args.cmd == "suggest":
        result = {"suggestions": suggest_next_actions(args.campaign, mode=args.mode)}
    elif args.cmd == "hp-change":
        result = {"line": format_combat_change(args.target, args.before, args.after, change_type=args.type)}
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()