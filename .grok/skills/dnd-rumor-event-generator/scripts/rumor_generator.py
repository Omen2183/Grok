#!/usr/bin/env python3
"""Procedural rumors and world events from campaign state."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"))

from dnd_state_utils import get_kingdom_state, get_world_state  # noqa: E402
from event_system import record_event  # noqa: E402
from kingdom_sim import generate_domain_event_chain  # noqa: E402


RUMOR_TEMPLATES = [
    "Whispers say {subject} was seen near {location}.",
    "A merchant claims {subject} will change everything in {domain}.",
    "Locals argue whether {subject} is a blessing or a curse.",
    "A bard's new song hints at secrets involving {subject}.",
]


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
    subject = seed or random.choice([
        "a missing caravan", "a strange light", "an old treaty", "a hidden vault",
    ])
    rng = random.Random(hash((campaign_name, subject, world.get("in_game_time", ""))))
    rumors = []
    for template in rng.sample(RUMOR_TEMPLATES, k=min(count, len(RUMOR_TEMPLATES))):
        text = template.format(subject=subject, location=location, domain=domain)
        rumors.append({"text": text, "reliability": rng.choice(["likely", "uncertain", "dubious"])})
    if persist and rumors:
        for rumor in rumors:
            record_event(
                campaign_name,
                rumor["text"],
                tags=["rumor"],
                importance="normal",
                metadata={"reliability": rumor["reliability"]},
            )
    return rumors


def generate_world_event(campaign_name: str, *, seed: str = "unrest") -> Dict[str, Any]:
    chain = generate_domain_event_chain(campaign_name, seed)
    event = {"headline": chain[0], "followups": chain[1:], "seed": seed}
    record_event(campaign_name, event["headline"], tags=["rumor", "world-event"], importance="normal")
    return event


def main() -> None:
    parser = argparse.ArgumentParser(description="Rumor and world event generator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_rumors = sub.add_parser("rumors")
    p_rumors.add_argument("campaign")
    p_rumors.add_argument("--count", type=int, default=3)
    p_rumors.add_argument("--seed", default="")
    p_rumors.add_argument("--no-persist", action="store_true")

    p_event = sub.add_parser("world-event")
    p_event.add_argument("campaign")
    p_event.add_argument("--seed", default="unrest")

    args = parser.parse_args()
    if args.cmd == "rumors":
        result = generate_rumors(
            args.campaign, args.count, seed=args.seed, persist=not args.no_persist
        )
    elif args.cmd == "world-event":
        result = generate_world_event(args.campaign, seed=args.seed)
    else:
        result = {"error": "unknown command"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()