#!/usr/bin/env python3
"""Session recap, XP tracking, and log management for D&D campaigns."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from dnd_state_utils import (  # noqa: E402
    audit_campaign,
    clear_combat_state,
    get_player_character,
    get_world_state,
    load_json,
    save_json,
)
from event_system import record_event  # noqa: E402
from paths import get_campaign_path  # noqa: E402


def _append_session_log(campaign_name: str, text: str) -> None:
    log_path = get_campaign_path(campaign_name) / "logs" / "session_log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(text)


def award_xp(campaign_name: str, amount: int, *, reason: str = "") -> Dict[str, Any]:
    path = get_campaign_path(campaign_name) / "state" / "player_character.json"
    char = load_json(path, {})
    char["xp"] = char.get("xp", 0) + amount
    save_json(path, char)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    note = f"\n\n### XP +{amount} ({stamp})\n"
    if reason:
        note += f"- **Reason:** {reason}\n"
    note += f"- **Total XP:** {char['xp']}\n"
    _append_session_log(campaign_name, note)

    record_event(
        campaign_name,
        f"XP awarded: {amount}" + (f" — {reason}" if reason else ""),
        importance="normal",
        tags=["xp"],
        metadata={"amount": amount},
    )
    return {"xp_awarded": amount, "total_xp": char["xp"], "reason": reason}


def save_recap(
    campaign_name: str,
    summary: str,
    *,
    hooks: Optional[List[str]] = None,
    xp_gained: int = 0,
) -> Dict[str, Any]:
    recaps_dir = get_campaign_path(campaign_name) / "recaps"
    recaps_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    recap_path = recaps_dir / f"session_{stamp}.md"

    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)

    lines = [
        f"# Session Recap — {campaign_name}",
        f"*{datetime.now().strftime('%B %d, %Y')}*",
        "",
        "## What Happened",
        summary,
        "",
        "## Key State",
        f"- **Location:** {world.get('current_location', 'Unknown')}",
        f"- **Time:** {world.get('in_game_time', 'Unknown')}",
        f"- **Character:** {player.get('name', 'Adventurer')} (Level {player.get('level', 1)})",
        f"- **XP this session:** {xp_gained}",
    ]

    if hooks:
        lines.extend(["", "## Hooks for Next Session"])
        for hook in hooks:
            lines.append(f"- {hook}")

    content = "\n".join(lines) + "\n"
    recap_path.write_text(content, encoding="utf-8")
    _append_session_log(campaign_name, f"\n\n## Session Recap ({stamp})\n{summary}\n")

    record_event(campaign_name, "Session recap saved", importance="major", tags=["recap"])
    return {"recap_path": str(recap_path), "hooks": hooks or []}


def end_session(
    campaign_name: str,
    summary: str,
    *,
    xp: int = 0,
    xp_reason: str = "Session completion",
    hooks: Optional[List[str]] = None,
    run_audit: bool = True,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {"campaign": campaign_name}

    if xp > 0:
        results["xp"] = award_xp(campaign_name, xp, reason=xp_reason)

    results["recap"] = save_recap(campaign_name, summary, hooks=hooks, xp_gained=xp)
    results["combat"] = clear_combat_state(campaign_name)

    if run_audit:
        results["audit"] = audit_campaign(campaign_name)

    record_event(campaign_name, "Session ended", importance="major", tags=["session-end"])
    results["status"] = "session_saved"
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="D&D session scribe")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_xp = sub.add_parser("award-xp")
    p_xp.add_argument("campaign")
    p_xp.add_argument("amount", type=int)
    p_xp.add_argument("--reason", default="")

    p_recap = sub.add_parser("recap")
    p_recap.add_argument("campaign")
    p_recap.add_argument("summary")
    p_recap.add_argument("--hook", action="append", default=[])

    p_end = sub.add_parser("end-session")
    p_end.add_argument("campaign")
    p_end.add_argument("summary")
    p_end.add_argument("--xp", type=int, default=0)
    p_end.add_argument("--reason", default="Session completion")
    p_end.add_argument("--hook", action="append", default=[])
    p_end.add_argument("--skip-audit", action="store_true")

    args = parser.parse_args()

    if args.cmd == "award-xp":
        result = award_xp(args.campaign, args.amount, reason=args.reason)
    elif args.cmd == "recap":
        result = save_recap(args.campaign, args.summary, hooks=args.hook)
    elif args.cmd == "end-session":
        result = end_session(
            args.campaign,
            args.summary,
            xp=args.xp,
            xp_reason=args.reason,
            hooks=args.hook,
            run_audit=not args.skip_audit,
        )
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()