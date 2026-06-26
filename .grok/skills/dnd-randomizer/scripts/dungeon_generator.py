"""Procedural dungeon floor generator with rooms, features, and encounters."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

DUNGEON_VERSION = "5.0.0"

ROOM_TYPES = [
    "empty chamber", "guard post", "treasure vault", "shrine", "prison cell",
    "fungal grotto", "collapsed hall", "arcane laboratory", "bone ossuary",
]

DIRECTIONS = ["north", "south", "east", "west", "up", "down"]


def generate_dungeon_floor(
    *,
    rooms: int = 6,
    party_level: int = 3,
    campaign_name: Optional[str] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    from randomizer_engine import roll_table  # noqa: E402

    rng = random.Random(seed)
    floor_rooms: List[Dict[str, Any]] = []
    for i in range(rooms):
        feature = roll_table(
            "dungeon_feature",
            campaign_name=campaign_name,
            count=1,
            seed=rng.randint(0, 999999),
        )
        trap = None
        if rng.random() < 0.35:
            trap_roll = roll_table("trap", count=1, seed=rng.randint(0, 999999))
            trap = trap_roll["results"][0]["name"] if trap_roll.get("results") else None
        foes = []
        if rng.random() < 0.5:
            foes.append({
                "name": rng.choice(["Goblin", "Skeleton", "Giant rat", "Cultist", "Kobold"]),
                "count": rng.randint(1, 4),
                "cr": round(max(0.125, party_level / 4 * rng.uniform(0.4, 1.0)), 2),
            })
        exits = rng.sample(DIRECTIONS, k=rng.randint(1, 3))
        floor_rooms.append({
            "room": i + 1,
            "type": rng.choice(ROOM_TYPES),
            "feature": feature["results"][0]["name"] if feature.get("results") else "dim torchlight",
            "trap": trap,
            "foes": foes,
            "exits": exits,
            "loot_hint": rng.choice(["none", "minor", "significant"]) if not foes else "after combat",
        })

    return {
        "floor": 1,
        "room_count": len(floor_rooms),
        "party_level": party_level,
        "rooms": floor_rooms,
        "theme": roll_table("terrain", count=1, seed=seed or rng.randint(0, 999999))["results"][0]["name"],
        "version": DUNGEON_VERSION,
    }