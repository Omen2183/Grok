#!/usr/bin/env python3
"""Quest, faction, magic item, and domain event prompt builders."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from dnd_state_utils import get_kingdom_state, get_player_character, get_world_state  # noqa: E402


def _campaign_context(campaign_name: str) -> Dict[str, Any]:
    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)
    kingdom = get_kingdom_state(campaign_name)
    return {
        "location": world.get("current_location", "Unknown"),
        "time": world.get("in_game_time", "Unknown"),
        "mode": world.get("mode", "tabletop"),
        "party_level": player.get("level", 5),
        "pc_name": player.get("name", "Adventurer"),
        "domain": kingdom.get("domain_name", "Unsettled Lands"),
        "resources": kingdom.get("resources", {}),
    }


def generate_quest_prompt(campaign_name: str, theme: str = "side quest") -> Dict[str, Any]:
    ctx = _campaign_context(campaign_name)
    prompt = f"""Create a compelling D&D 5e quest for this campaign.

**Context:** Level {ctx['party_level']} party at {ctx['location']} ({ctx['time']})
**Theme:** {theme}
**PC:** {ctx['pc_name']}

Deliver:
1. Quest hook (1-2 sentences players hear in-world)
2. Objectives (3 steps max)
3. Complications / twist
4. Rewards (XP guideline + tangible loot ideas)
5. Optional tie-in to domain/faction if mode is kingdom ({ctx['mode']})
"""
    return {"type": "quest", "theme": theme, "context": ctx, "generation_prompt": prompt}


def generate_faction_prompt(campaign_name: str, faction: str = "local power") -> Dict[str, Any]:
    ctx = _campaign_context(campaign_name)
    kingdom = get_kingdom_state(campaign_name)
    factions = kingdom.get("factions", {})
    prompt = f"""Design a faction move for a D&D campaign.

**Faction:** {faction}
**Location:** {ctx['location']}
**Known factions in state:** {list(factions.keys()) or 'none yet'}
**Domain:** {ctx['domain']} — resources {ctx['resources']}

Deliver:
1. What the faction does this week (concrete action)
2. How PCs might learn about it
3. Stakes if ignored
4. 2 ways PCs can engage (ally, oppose, exploit)
"""
    return {"type": "faction", "faction": faction, "context": ctx, "generation_prompt": prompt}


def generate_magic_item_prompt(
    campaign_name: str,
    *,
    rarity: str = "uncommon",
    theme: str = "campaign-themed",
) -> Dict[str, Any]:
    ctx = _campaign_context(campaign_name)
    prompt = f"""Design a {rarity} magic item for a level {ctx['party_level']} party.

**Theme:** {theme}
**Campaign location:** {ctx['location']}

Deliver full item block: name, rarity, attunement, description, mechanics, curse or drawback (optional), and one adventure hook for how it enters play.
"""
    return {"type": "magic_item", "rarity": rarity, "theme": theme, "context": ctx, "generation_prompt": prompt}


def generate_domain_event_prompt(campaign_name: str, seed: str = "random") -> Dict[str, Any]:
    ctx = _campaign_context(campaign_name)
    kingdom = get_kingdom_state(campaign_name)
    active = [p["name"] for p in kingdom.get("projects", []) if p.get("status") == "queued"]
    prompt = f"""Generate a kingdom/domain event for D&D domain play.

**Domain:** {ctx['domain']}
**Seed:** {seed}
**Active projects:** {active or 'none'}
**Resources:** {ctx['resources']}

Deliver:
1. Event headline
2. Mechanical effect on resources or morale
3. Player choices (2-3)
4. Long-term consequence if unresolved
"""
    return {"type": "domain_event", "seed": seed, "context": ctx, "generation_prompt": prompt}


def main() -> None:
    parser = argparse.ArgumentParser(description="D&D content forge — quests, factions, items, events")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_quest = sub.add_parser("quest")
    p_quest.add_argument("campaign")
    p_quest.add_argument("--theme", default="side quest")

    p_faction = sub.add_parser("faction")
    p_faction.add_argument("campaign")
    p_faction.add_argument("--name", default="local power")

    p_item = sub.add_parser("magic-item")
    p_item.add_argument("campaign")
    p_item.add_argument("--rarity", default="uncommon")
    p_item.add_argument("--theme", default="campaign-themed")

    p_domain = sub.add_parser("domain-event")
    p_domain.add_argument("campaign")
    p_domain.add_argument("--seed", default="random")

    args = parser.parse_args()

    if args.cmd == "quest":
        result = generate_quest_prompt(args.campaign, args.theme)
    elif args.cmd == "faction":
        result = generate_faction_prompt(args.campaign, args.name)
    elif args.cmd == "magic-item":
        result = generate_magic_item_prompt(args.campaign, rarity=args.rarity, theme=args.theme)
    elif args.cmd == "domain-event":
        result = generate_domain_event_prompt(args.campaign, args.seed)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()