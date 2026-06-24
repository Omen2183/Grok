#!/usr/bin/env python3
"""Procedural rumors and world events from campaign state."""

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

from dnd_state_utils import get_kingdom_state, get_world_state, load_json, save_json  # noqa: E402
from event_system import record_event, search_events  # noqa: E402
from kingdom_sim import generate_domain_event_chain  # noqa: E402

RUMOR_BACKEND_VERSION = "3.2.0"

RUMOR_TEMPLATES = [
    "Whispers say {subject} was seen near {location}.",
    "A merchant claims {subject} will change everything in {domain}.",
    "Locals argue whether {subject} is a blessing or a curse.",
    "A bard's new song hints at secrets involving {subject}.",
    "The {faction} faction spreads word that {subject} threatens their interests.",
]

FACTION_MOVE_TEMPLATES = [
    "{faction} ({attitude}) increases patrols after rumors of {subject}.",
    "Envoys from {faction} demand answers about {subject} in {location}.",
    "{faction} offers a reward for information on {subject}.",
]


def _rumors_ledger_file(campaign_name: str) -> Path:
    from paths import get_campaign_path  # noqa: E402

    return get_campaign_path(campaign_name) / "state" / "rumors_ledger.json"


def _append_ledger(campaign_name: str, entry: Dict[str, Any]) -> None:
    path = _rumors_ledger_file(campaign_name)
    data = load_json(path, {"rumors": []})
    data.setdefault("rumors", []).append({**entry, "recorded": datetime.now().isoformat()})
    save_json(path, data)


def generate_rumors(
    campaign_name: str,
    count: int = 3,
    *,
    seed: str = "",
    persist: bool = True,
) -> List[Dict[str, Any]]:
    world = get_world_state(campaign_name)
    kingdom = get_kingdom_state(campaign_name)
    location = world.get("current_location", "the region")
    domain = kingdom.get("domain_name", "the realm")
    factions = kingdom.get("factions", {})
    faction_name = next(iter(factions), "local guild") if factions else "local guild"
    subject = seed or random.choice([
        "a missing caravan", "a strange light", "an old treaty", "a hidden vault",
    ])
    rng = random.Random(hash((campaign_name, subject, world.get("in_game_time", ""))))
    rumors = []
    templates = list(RUMOR_TEMPLATES)
    for template in rng.sample(templates, k=min(count, len(templates))):
        text = template.format(
            subject=subject,
            location=location,
            domain=domain,
            faction=faction_name,
        )
        rumor = {"text": text, "reliability": rng.choice(["likely", "uncertain", "dubious"])}
        rumors.append(rumor)
        if persist:
            record_event(
                campaign_name,
                text,
                tags=["rumor"],
                importance="normal",
                metadata={"reliability": rumor["reliability"]},
            )
            _append_ledger(campaign_name, rumor)
    return rumors


def list_recent_rumors(campaign_name: str, *, limit: int = 10) -> Dict[str, Any]:
    events = search_events(campaign_name, tag="rumor", limit=limit)
    ledger = load_json(_rumors_ledger_file(campaign_name), {"rumors": []})
    return {
        "events": events,
        "ledger_count": len(ledger.get("rumors", [])),
        "ledger_recent": ledger.get("rumors", [])[-limit:],
    }


def generate_faction_move(
    campaign_name: str,
    *,
    faction: Optional[str] = None,
    seed: str = "",
) -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    world = get_world_state(campaign_name)
    factions = kingdom.get("factions", {})
    if not factions:
        factions = {"locals": {"attitude": "wary", "influence": 1}}
    faction_name = faction or next(iter(factions))
    data = factions.get(faction_name, {"attitude": "neutral", "influence": 0})
    subject = seed or "unrest"
    template = random.choice(FACTION_MOVE_TEMPLATES)
    headline = template.format(
        faction=faction_name,
        attitude=data.get("attitude", "neutral"),
        subject=subject,
        location=world.get("current_location", "the region"),
    )
    move = {
        "faction": faction_name,
        "headline": headline,
        "influence": data.get("influence", 0),
        "seed": subject,
    }
    record_event(campaign_name, headline, tags=["rumor", "faction"], metadata=move)
    _append_ledger(campaign_name, {"text": headline, "reliability": "likely", "faction": faction_name})
    return move


def get_rumors_ledger(campaign_name: str, *, limit: int = 20) -> Dict[str, Any]:
    """Return persisted rumor ledger entries."""
    ledger = load_json(_rumors_ledger_file(campaign_name), {"rumors": []})
    rumors = ledger.get("rumors", [])
    return {
        "campaign": campaign_name,
        "total": len(rumors),
        "rumors": rumors[-limit:] if limit else rumors,
        "version": RUMOR_BACKEND_VERSION,
    }


def generate_world_event(campaign_name: str, *, seed: str = "unrest") -> Dict[str, Any]:
    chain = generate_domain_event_chain(campaign_name, seed)
    event = {"headline": chain[0], "followups": chain[1:], "seed": seed}
    record_event(campaign_name, event["headline"], tags=["rumor", "world-event"], importance="normal")
    _append_ledger(campaign_name, {"text": event["headline"], "reliability": "likely", "type": "world-event"})
    return event


def main() -> None:
    parser = argparse.ArgumentParser(description="Rumor and world event generator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_rumors = sub.add_parser("rumors")
    p_rumors.add_argument("campaign")
    p_rumors.add_argument("--count", type=int, default=3)
    p_rumors.add_argument("--seed", default="")
    p_rumors.add_argument("--no-persist", action="store_true")

    p_list = sub.add_parser("list")
    p_list.add_argument("campaign")
    p_list.add_argument("--limit", type=int, default=10)

    p_faction = sub.add_parser("faction-move")
    p_faction.add_argument("campaign")
    p_faction.add_argument("--faction")
    p_faction.add_argument("--seed", default="")

    p_event = sub.add_parser("world-event")
    p_event.add_argument("campaign")
    p_event.add_argument("--seed", default="unrest")

    p_ledger = sub.add_parser("ledger", help="Show persisted rumor ledger")
    p_ledger.add_argument("campaign")
    p_ledger.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    if args.cmd == "rumors":
        result = generate_rumors(
            args.campaign, args.count, seed=args.seed, persist=not args.no_persist
        )
    elif args.cmd == "list":
        result = list_recent_rumors(args.campaign, limit=args.limit)
    elif args.cmd == "faction-move":
        result = generate_faction_move(args.campaign, faction=args.faction, seed=args.seed)
    elif args.cmd == "world-event":
        result = generate_world_event(args.campaign, seed=args.seed)
    elif args.cmd == "ledger":
        result = get_rumors_ledger(args.campaign, limit=args.limit)
    else:
        result = {"error": "unknown command"}
    if isinstance(result, list):
        result = {"rumors": result, "version": RUMOR_BACKEND_VERSION}
    else:
        result["version"] = RUMOR_BACKEND_VERSION
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()