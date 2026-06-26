"""Built-in tables and reference pools for dnd-randomizer."""

from __future__ import annotations

from typing import Any, Dict, List

RANDOMIZER_DATA_VERSION = "4.1.0"

RACES = [
    "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf",
    "Half-Orc", "Tiefling", "Aasimar", "Goliath", "Tabaxi", "Firbolg",
]

CLASSES = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin",
    "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard",
]

BACKGROUNDS = [
    "Acolyte", "Charlatan", "Criminal", "Entertainer", "Folk Hero", "Guild Artisan",
    "Hermit", "Noble", "Outlander", "Sage", "Sailor", "Soldier", "Urchin",
]

ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral",
    "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil",
]

MUNDANE_ITEMS = [
    {"name": "Rusty shortsword", "weight": 10, "value_gp": 5},
    {"name": "Healing potion", "weight": 15, "value_gp": 50},
    {"name": "Bag of caltrops", "weight": 8, "value_gp": 1},
    {"name": "Silver holy symbol", "weight": 6, "value_gp": 25},
    {"name": "Map fragment", "weight": 12, "value_gp": 0},
    {"name": "Enchanted-looking trinket (mundane)", "weight": 5, "value_gp": 10},
    {"name": "Fine wines (3 bottles)", "weight": 7, "value_gp": 15},
    {"name": "Thieves' tools", "weight": 9, "value_gp": 25},
    {"name": "Spell scroll (blank)", "weight": 4, "value_gp": 5},
    {"name": "Gemstone (50 gp)", "weight": 6, "value_gp": 50},
]

MAGIC_ITEMS = [
    {"name": "+1 Dagger", "weight": 12, "rarity": "uncommon"},
    {"name": "Cloak of Protection", "weight": 10, "rarity": "uncommon"},
    {"name": "Boots of Elvenkind", "weight": 8, "rarity": "uncommon"},
    {"name": "Wand of Magic Missiles", "weight": 7, "rarity": "uncommon"},
    {"name": "Ring of Warmth", "weight": 9, "rarity": "uncommon"},
    {"name": "Bag of Holding", "weight": 6, "rarity": "uncommon"},
    {"name": "Potion of Greater Healing", "weight": 14, "rarity": "uncommon"},
    {"name": "Sending Stones (pair)", "weight": 4, "rarity": "rare"},
    {"name": "Flame Tongue Longsword", "weight": 3, "rarity": "rare"},
    {"name": "Cloak of Displacement", "weight": 2, "rarity": "rare"},
]

WEATHER = [
    "Clear skies", "Light rain", "Heavy downpour", "Fog banks", "Sudden hail",
    "Unseasonable heat", "Biting wind", "Thunderstorm", "Ash-gray overcast", "Aurora at dusk",
]

TERRAIN = [
    "Open road", "Dense forest", "Rocky hills", "Marshland", "Mountain pass",
    "Coastal cliffs", "Ruined keep", "Underground cavern", "Frozen tundra", "Desert wastes",
]

TRAVEL_COMPLICATIONS = [
    "Bridge washed out — detour required",
    "Bandits demand a toll",
    "Guide got lost overnight",
    "Supply wagon axle breaks",
    "Strange lights on the horizon",
    "Refugees block the road with a plea",
    "Sudden rockslide",
    "Lost livestock scattered across trail",
]

DUNGEON_FEATURES = [
    "Collapsing ceiling trap", "Fountain of murky water", "Locked iron door",
    "Faded mural of an ancient god", "Pit with spikes", "Hidden cache behind loose stone",
    "Echoing whispers from below", "Fungal garden", "Abandoned camp with fresh embers",
]

NPC_ROLES = [
    "merchant", "guard captain", "hermit sage", "bounty hunter", "priest",
    "smuggler", "noble's spy", "tavern keeper", "wandering bard", "beast tamer",
]

QUEST_HOOKS = [
    "Recover a stolen relic before the solstice",
    "Escort a witness through hostile territory",
    "Clear monsters from a vital trade route",
    "Investigate lights in a sealed tomb",
    "Broker peace between feuding factions",
    "Find the source of a magical blight",
]

WORLD_DOMAINS = [
    "Thornvale Marches", "Ironspine Reach", "Mistharbor Isles", "Ashwold Expanse",
    "Glimmerdeep Warrens", "Stormcrown Peaks", "Verdant Coil", "Bleakwater Fens",
]

WORLD_THREATS = [
    "Rising undead in border graves", "Trade guild war", "Dragon sightings",
    "Cult activity in cities", "Famine after failed harvest", "Refugee crisis from the east",
]

GOVERNMENT_TYPES = [
    "Feudal barony", "Merchant council", "Theocratic order", "Tribal confederation",
    "Magocracy", "Military junta", "Elected syndics",
]

NAME_PREFIXES = ["Thorn", "Ash", "Grim", "Silver", "Storm", "Iron", "Mist", "Bright", "Deep", "Wild"]
NAME_SUFFIXES = ["hold", "vale", "ford", "mere", "spire", "haven", "watch", "fall", "crest", "wick"]
PERSON_FIRST = ["Aldric", "Bryn", "Cael", "Dara", "Eira", "Finn", "Garrick", "Hilda", "Ivor", "Jessa",
                "Kael", "Lyra", "Mira", "Nox", "Orin", "Piper", "Quinn", "Rook", "Sera", "Torin"]
PERSON_LAST = ["Blackwood", "Ironfoot", "Stormborn", "Ashvale", "Brightshield", "Deepdelver",
               "Grimhart", "Mistwalker", "Thornfield", "Wolfcrest"]

BUILTIN_TABLES: Dict[str, List[Dict[str, Any]]] = {
    "weather": [{"name": w, "weight": 1} for w in WEATHER],
    "terrain": [{"name": t, "weight": 1} for t in TERRAIN],
    "travel_complication": [{"name": c, "weight": 1} for c in TRAVEL_COMPLICATIONS],
    "dungeon_feature": [{"name": f, "weight": 1} for f in DUNGEON_FEATURES],
    "npc_role": [{"name": r, "weight": 1} for r in NPC_ROLES],
    "quest_hook": [{"name": q, "weight": 1} for q in QUEST_HOOKS],
    "mundane_item": MUNDANE_ITEMS,
    "magic_item": MAGIC_ITEMS,
    "world_threat": [{"name": t, "weight": 1} for t in WORLD_THREATS],
    "government": [{"name": g, "weight": 1} for g in GOVERNMENT_TYPES],
}

# Feats pool (subset — full lookup via rules-reference srd_data when available)
FEATS = [
    "Alert", "Lucky", "Mobile", "Tough", "War Caster", "Sharpshooter",
    "Great Weapon Master", "Magic Initiate", "Resilient", "Sentinel",
    "Polearm Master", "Observant", "Actor", "Athlete", "Healer",
]

CANTRIPS = [
    "Fire Bolt", "Ray of Frost", "Prestidigitation", "Mage Hand", "Eldritch Blast",
    "Sacred Flame", "Guidance", "Thorn Whip", "Vicious Mockery",
]

SPELLS_BY_LEVEL: Dict[int, List[str]] = {
    0: CANTRIPS,
    1: ["Magic Missile", "Cure Wounds", "Shield", "Bless", "Healing Word", "Hunter's Mark"],
    2: ["Misty Step", "Hold Person", "Spiritual Weapon", "Moonbeam"],
    3: ["Fireball", "Counterspell", "Revivify", "Dispel Magic"],
}