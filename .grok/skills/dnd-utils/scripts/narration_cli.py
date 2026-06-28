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
    format_kingdom_mobile,
    format_mobile_status,
    format_quick_status,
    proactive_opening,
    suggest_next_actions,
)
from event_system import pop_last_event  # noqa: E402


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

    p_dash = sub.add_parser("dashboard", help="Full campaign snapshot (mobile)")
    p_dash.add_argument("campaign")

    p_quick = sub.add_parser("quick-status", help="One-line status for quick-session play")
    p_quick.add_argument("campaign")

    p_health = sub.add_parser("campaign-health", help="Pre-session health check")
    p_health.add_argument("campaign")

    p_kingdom = sub.add_parser("kingdom-mobile", help="Short kingdom summary for voice")
    p_kingdom.add_argument("campaign")

    p_undo = sub.add_parser("undo-last", help="Pop last logged event (undo helper)")
    p_undo.add_argument("campaign")
    p_undo.add_argument("--tag")

    args = parser.parse_args()

    if args.cmd == "dashboard":
        from campaign_dashboard import build_campaign_dashboard
        dash = build_campaign_dashboard(args.campaign)
        result = {"dashboard": dash, "mobile_summary": dash.get("mobile_summary", "")}
    elif args.cmd == "quick-status":
        result = {"status": format_quick_status(args.campaign)}
    elif args.cmd == "campaign-health":
        from campaign_dashboard import build_campaign_health
        result = build_campaign_health(args.campaign)
    elif args.cmd == "kingdom-mobile":
        result = {"summary": format_kingdom_mobile(args.campaign)}
    elif args.cmd == "undo-last":
        result = pop_last_event(args.campaign, tag=args.tag)
    elif args.cmd == "mobile-status":
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