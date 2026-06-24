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

    p_save = sub.add_parser("save-canon")
    p_save.add_argument("campaign")
    p_save.add_argument("content")

    args = parser.parse_args()

    if args.cmd == "weave-prompt":
        result = weave_visual_prompt(args.campaign, args.scene, style=args.style, shot=args.shot)
    elif args.cmd == "save-canon":
        result = save_visual_canon(args.campaign, args.content)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()