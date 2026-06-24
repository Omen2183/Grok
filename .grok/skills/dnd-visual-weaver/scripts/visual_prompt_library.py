#!/usr/bin/env python3
"""Build consistent image prompts from live campaign state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from dnd_state_utils import get_player_character, get_world_state, load_json  # noqa: E402  # type: ignore
from paths import get_campaign_path  # noqa: E402

VISUAL_BACKEND_VERSION = "3.2.0"


def load_visual_canon(campaign_name: str) -> str:
    canon_path = get_campaign_path(campaign_name) / "state" / "visual_canon.md"
    if canon_path.exists():
        return canon_path.read_text(encoding="utf-8")
    return ""


def load_companion_visual(campaign_name: str) -> str:
    path = get_campaign_path(campaign_name) / "state" / "important_companion.json"
    if not path.exists():
        return ""
    data = load_json(path, {})
    name = data.get("name", "companion")
    appearance = data.get("appearance", data.get("notes", ""))
    return f"{name}: {appearance}".strip(": ")


def weave_visual_prompt(
    campaign_name: str,
    scene: str,
    *,
    style: str = "cinematic fantasy illustration",
    shot: str = "wide establishing shot",
) -> Dict[str, Any]:
    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)
    canon = load_visual_canon(campaign_name)
    companion = load_companion_visual(campaign_name)

    location = world.get("current_location", "unknown location")
    weather = world.get("weather", "clear")
    time = world.get("in_game_time", "daytime")
    pc_name = player.get("name", "the adventurer")
    hp = player.get("hit_points", {})
    mode = world.get("mode", "tabletop")

    prompt_parts = [
        style,
        shot,
        f"Scene: {scene}",
        f"Location: {location}",
        f"Time and weather: {time}, {weather}",
        f"Focus character: {pc_name}",
    ]

    if mode == "kingdom":
        prompt_parts.append("Domain/kingdom establishing shot with settlement scale")
    if hp.get("current", 1) <= hp.get("max", 1) * 0.25:
        prompt_parts.append("Character appears wounded and battle-worn")
    if canon:
        prompt_parts.append(f"Visual canon: {canon[:500]}")
    if companion:
        prompt_parts.append(f"Companion reference: {companion[:200]}")

    prompt = ". ".join(prompt_parts)
    return {
        "prompt": prompt,
        "location": location,
        "character": pc_name,
        "style": style,
        "shot": shot,
        "has_canon": bool(canon),
        "mode": mode,
    }


def weave_kingdom_prompt(
    campaign_name: str,
    focus: str = "domain overview",
    *,
    style: str = "grand strategy fantasy map illustration",
) -> Dict[str, Any]:
    """Build a kingdom-mode visual prompt from live domain state."""
    from dnd_state_utils import get_kingdom_state  # noqa: E402

    kingdom = get_kingdom_state(campaign_name)
    world = get_world_state(campaign_name)
    resources = kingdom.get("resources", {})
    active = [p["name"] for p in kingdom.get("projects", []) if p.get("status") == "queued"]

    prompt_parts = [
        style,
        f"Kingdom focus: {focus}",
        f"Domain: {kingdom.get('domain_name', 'Unsettled Lands')}",
        f"Region: {world.get('current_location', 'unknown')}",
        f"Resources — gold {resources.get('gold', 0)}, food {resources.get('food', 0)}, "
        f"materials {resources.get('materials', 0)}",
        f"Weather and time: {world.get('weather', 'clear')}, {world.get('in_game_time', 'day')}",
    ]
    if active:
        prompt_parts.append(f"Active construction: {', '.join(active[:3])}")
    canon = load_visual_canon(campaign_name)
    if canon:
        prompt_parts.append(f"Visual canon: {canon[:400]}")

    prompt = ". ".join(prompt_parts)
    return {
        "prompt": prompt,
        "mode": "kingdom",
        "domain": kingdom.get("domain_name"),
        "focus": focus,
        "style": style,
        "has_canon": bool(canon),
    }


def update_visual_canon_after_generation(
    campaign_name: str,
    subject: str,
    description: str,
    *,
    category: str = "generated",
) -> Dict[str, Any]:
    """Append a post-generation visual note to visual_canon.md."""
    from datetime import datetime

    path = get_campaign_path(campaign_name) / "state" / "visual_canon.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n\n### {subject} ({category}, {stamp})\n{description.strip()}\n"
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        path.write_text(existing.rstrip() + entry, encoding="utf-8")
    else:
        path.write_text(f"# Visual Canon{entry}", encoding="utf-8")
    return {"updated": str(path), "subject": subject, "category": category}


def visual_status(campaign_name: str) -> Dict[str, Any]:
    """Summarize visual assets and canon state for a campaign."""
    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)
    canon = load_visual_canon(campaign_name)
    companion = load_companion_visual(campaign_name)
    canon_path = get_campaign_path(campaign_name) / "state" / "visual_canon.md"
    return {
        "campaign": campaign_name,
        "location": world.get("current_location", "unknown"),
        "mode": world.get("mode", "tabletop"),
        "character": player.get("name", "unknown"),
        "has_canon": bool(canon),
        "canon_chars": len(canon),
        "canon_path": str(canon_path) if canon_path.exists() else None,
        "has_companion": bool(companion),
        "companion_preview": companion[:120] if companion else "",
        "version": VISUAL_BACKEND_VERSION,
    }


def save_visual_canon(campaign_name: str, content: str) -> Dict[str, Any]:
    path = get_campaign_path(campaign_name) / "state" / "visual_canon.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"saved": str(path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Visual prompt weaver for D&D campaigns")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_weave = sub.add_parser("weave-prompt")
    p_weave.add_argument("campaign")
    p_weave.add_argument("scene")
    p_weave.add_argument("--style", default="cinematic fantasy illustration")
    p_weave.add_argument("--shot", default="wide establishing shot")

    p_kingdom = sub.add_parser("weave-kingdom")
    p_kingdom.add_argument("campaign")
    p_kingdom.add_argument("--focus", default="domain overview")
    p_kingdom.add_argument("--style", default="grand strategy fantasy map illustration")

    p_save = sub.add_parser("save-canon")
    p_save.add_argument("campaign")
    p_save.add_argument("content")

    p_append = sub.add_parser("append-canon")
    p_append.add_argument("campaign")
    p_append.add_argument("subject")
    p_append.add_argument("description")
    p_append.add_argument("--category", default="generated")

    p_status = sub.add_parser("status", help="Visual canon and companion status")
    p_status.add_argument("campaign")

    args = parser.parse_args()

    if args.cmd == "weave-prompt":
        result = weave_visual_prompt(args.campaign, args.scene, style=args.style, shot=args.shot)
    elif args.cmd == "weave-kingdom":
        result = weave_kingdom_prompt(args.campaign, args.focus, style=args.style)
    elif args.cmd == "save-canon":
        result = save_visual_canon(args.campaign, args.content)
    elif args.cmd == "append-canon":
        result = update_visual_canon_after_generation(
            args.campaign, args.subject, args.description, category=args.category
        )
    elif args.cmd == "status":
        result = visual_status(args.campaign)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()