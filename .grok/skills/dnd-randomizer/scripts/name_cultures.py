"""Cultural naming tables for procedural character and place generation."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

NAME_CULTURES_VERSION = "5.0.0"

CULTURES: Dict[str, Dict[str, List[str]]] = {
    "human": {
        "prefix": ["North", "South", "East", "West", "High", "Low", "Old", "New"],
        "suffix": ["ford", "haven", "shire", "field", "bridge", "moor"],
        "first": ["Aldric", "Bryn", "Cael", "Dara", "Finn", "Garrick", "Hilda", "Jessa", "Torin"],
        "last": ["Blackwood", "Ashvale", "Ironfoot", "Thornfield", "Brightshield"],
    },
    "elven": {
        "prefix": ["Sil", "Moon", "Star", "Silver", "Mist", "Dawn"],
        "suffix": ["thal", "wyn", "iel", "ara", "eth"],
        "first": ["Aelindra", "Caelynn", "Erevan", "Liriel", "Thalion", "Vaeril"],
        "last": ["Moonwhisper", "Starbloom", "Silverleaf", "Nightbrook"],
    },
    "dwarven": {
        "prefix": ["Iron", "Stone", "Deep", "Hammer", "Anvil", "Grim"],
        "suffix": ["heim", "gar", "dur", "bold", "forge"],
        "first": ["Balin", "Dagnal", "Helja", "Kildrak", "Thorin", "Vondal"],
        "last": ["Ironfist", "Stonehelm", "Hammerfall", "Deepdelver"],
    },
    "orcish": {
        "prefix": ["Blood", "Skull", "Ash", "War", "Bone", "Gore"],
        "suffix": ["mash", "gash", "fang", "crag", "pit"],
        "first": ["Gruk", "Morg", "Shagra", "Thokk", "Urzul", "Varg"],
        "last": ["Skullcrusher", "Bloodtusk", "Ashscar", "Wargrip"],
    },
    "gnomish": {
        "prefix": ["Glim", "Spark", "Cog", "Whistle", "Copper"],
        "suffix": ["wick", "gleam", "tinker", "spring"],
        "first": ["Bimble", "Fizzwick", "Lina", "Nackle", "Pip", "Zook"],
        "last": ["Geargrinder", "Copperkettle", "Whistlebrook"],
    },
    "dragonborn": {
        "prefix": ["Storm", "Ember", "Frost", "Scale", "Claw"],
        "suffix": ["scale", "breath", "fang", "wing"],
        "first": ["Arjhan", "Bharash", "Donaar", "Kava", "Rhogar", "Sora"],
        "last": ["Stormborn", "Emberscale", "Frostfang", "Ironclaw"],
    },
}

RACE_TO_CULTURE = {
    "human": "human",
    "elf": "elven",
    "half-elf": "elven",
    "dwarf": "dwarven",
    "half-orc": "orcish",
    "orc": "orcish",
    "gnome": "gnomish",
    "dragonborn": "dragonborn",
    "tiefling": "human",
    "halfling": "human",
}


def culture_for_race(race: str) -> str:
    return RACE_TO_CULTURE.get(race.lower(), "human")


def generate_cultural_name(
    culture: str = "human",
    *,
    name_type: str = "person",
    seed: Optional[int] = None,
) -> Dict[str, str]:
    rng = random.Random(seed)
    data = CULTURES.get(culture, CULTURES["human"])
    if name_type == "place":
        name = f"{rng.choice(data['prefix'])}{rng.choice(data['suffix'])}"
    elif name_type == "tavern":
        adj = rng.choice(["Weary", "Gilded", "Prancing", "Broken", "Laughing"])
        noun = rng.choice(data["prefix"] + data["suffix"])
        name = f"The {adj} {noun.title()}"
    else:
        name = f"{rng.choice(data['first'])} {rng.choice(data['last'])}"
    return {"name": name, "culture": culture, "type": name_type}


def list_cultures() -> List[str]:
    return sorted(CULTURES.keys())