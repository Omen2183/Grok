#!/usr/bin/env python3
"""Campaign orchestrator — init, resume, kingdom turns, and action routing."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SKILLS_ROOT = Path(__file__).resolve().parent.parent.parent
UTILS = SKILLS_ROOT / "dnd-utils" / "scripts"
sys.path.insert(0, str(UTILS))

from bootstrap import ensure_utils_importable  # noqa: E402

ensure_utils_importable()

from dnd_state_utils import (  # noqa: E402
    advance_kingdom_projects,
    audit_campaign,
    enhanced_audit_campaign,
    generate_session_start_summary,
    get_kingdom_summary,
    get_player_character,
    get_world_state,
    init_campaign,
)
from narration_helpers import format_mobile_status, proactive_opening, suggest_next_actions  # noqa: E402
from paths import get_campaign_path  # noqa: E402


def _campaign_exists(campaign_name: str) -> bool:
    return (get_campaign_path(campaign_name) / "state" / "world_state.json").exists()


def resume_campaign(campaign_name: str) -> Dict[str, Any]:
    """Load briefing, mobile status, and suggestions for session resume."""
    if not _campaign_exists(campaign_name):
        return {
            "status": "not_initialized",
            "campaign": campaign_name,
            "action": "init",
            "message": f"Campaign '{campaign_name}' not found. Run init first.",
        }
    opening = proactive_opening(campaign_name)
    combat_file = get_campaign_path(campaign_name) / "combat" / "current_combat.json"
    combat_active = combat_file.exists()
    result = {
        "status": "ready",
        "campaign": campaign_name,
        "mode": get_world_state(campaign_name).get("mode", "tabletop"),
        "briefing_markdown": opening["briefing"],
        "mobile_status": opening["mobile_status"],
        "suggestions": opening["suggestions"],
        "combat_active": combat_active,
    }
    if combat_active:
        try:
            sys.path.insert(0, str(SKILLS_ROOT / "dnd-combat-assistant" / "scripts"))
            from combat_tracker import get_combat_summary
            result["combat_summary"] = get_combat_summary(campaign_name)
        except Exception:
            pass
    return result


def kingdom_turn(campaign_name: str, *, turns: int = 1, rumor_count: int = 2) -> Dict[str, Any]:
    """Advance domain projects and surface rumors for kingdom mode."""
    projects = advance_kingdom_projects(campaign_name, turns=turns)
    rumors: List[str] = []
    try:
        sys.path.insert(0, str(SKILLS_ROOT / "dnd-rumor-event-generator" / "scripts"))
        from rumor_generator import generate_rumors
        rumor_result = generate_rumors(campaign_name, count=rumor_count)
        rumors = rumor_result if isinstance(rumor_result, list) else rumor_result.get("rumors", [])
    except Exception:
        pass
    return {
        "campaign": campaign_name,
        "kingdom_summary": get_kingdom_summary(campaign_name),
        "projects": projects,
        "rumors": rumors,
        "mobile_status": format_mobile_status(campaign_name),
        "suggestions": suggest_next_actions(campaign_name, mode="kingdom"),
    }


def route_player_action(campaign_name: str, text: str) -> Dict[str, Any]:
    """Map free-text player input to the responsible skill/backend."""
    sys.path.insert(0, str(SKILLS_ROOT / "dnd-voice-assistant" / "scripts"))
    from voice_utils import route_voice_request

    route = route_voice_request(text)
    route["campaign"] = campaign_name
    route["player_text"] = text
    world = get_world_state(campaign_name)
    route["mode"] = world.get("mode", "tabletop")
    route["location"] = world.get("current_location", "Unknown")
    return route


def whats_happening(campaign_name: str) -> Dict[str, Any]:
    """Proactive DM beat when the player is stuck or asks what's going on."""
    if not _campaign_exists(campaign_name):
        return {"status": "not_initialized", "campaign": campaign_name}
    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)
    recent = generate_session_start_summary(campaign_name)
    return {
        "status": "ok",
        "campaign": campaign_name,
        "location": world.get("current_location"),
        "time": world.get("in_game_time"),
        "character": player.get("name"),
        "mobile_status": format_mobile_status(campaign_name),
        "recent_events": recent.get("briefing_markdown", ""),
        "suggestions": suggest_next_actions(campaign_name),
        "prompt": "What do you do?",
    }


def run_script(relative_script: str, args: List[str]) -> Dict[str, Any]:
    """Run another skill script and return parsed JSON stdout when possible."""
    script = SKILLS_ROOT / relative_script
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=str(SKILLS_ROOT.parent.parent),
    )
    stdout = result.stdout.strip()
    try:
        payload = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        payload = {"output": stdout}
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "result": payload,
        "stderr": result.stderr.strip() or None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="D&D persistent DM orchestrator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("campaign")
    p_init.add_argument("--pc-name")
    p_init.add_argument("--force", action="store_true")
    p_init.add_argument("--enable-sqlite", action="store_true")

    p_resume = sub.add_parser("resume")
    p_resume.add_argument("campaign")

    p_status = sub.add_parser("status")
    p_status.add_argument("campaign")

    p_whats = sub.add_parser("whats-happening")
    p_whats.add_argument("campaign")

    p_kingdom = sub.add_parser("kingdom-turn")
    p_kingdom.add_argument("campaign")
    p_kingdom.add_argument("--turns", type=int, default=1)
    p_kingdom.add_argument("--rumors", type=int, default=2)

    p_route = sub.add_parser("route")
    p_route.add_argument("campaign")
    p_route.add_argument("text")

    p_health = sub.add_parser("health")
    p_health.add_argument("campaign")
    p_health.add_argument("--enhanced", action="store_true")

    args = parser.parse_args()

    if args.cmd == "init":
        result = init_campaign(
            args.campaign,
            force=args.force,
            pc_name=args.pc_name,
            enable_sqlite=args.enable_sqlite,
        )
    elif args.cmd == "resume":
        result = resume_campaign(args.campaign)
    elif args.cmd == "status":
        result = {
            "campaign": args.campaign,
            "mobile_status": format_mobile_status(args.campaign),
            "world": get_world_state(args.campaign),
            "player": get_player_character(args.campaign),
        }
    elif args.cmd == "whats-happening":
        result = whats_happening(args.campaign)
    elif args.cmd == "kingdom-turn":
        result = kingdom_turn(args.campaign, turns=args.turns, rumor_count=args.rumors)
    elif args.cmd == "route":
        result = route_player_action(args.campaign, args.text)
    elif args.cmd == "health":
        result = enhanced_audit_campaign(args.campaign) if args.enhanced else audit_campaign(args.campaign)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()