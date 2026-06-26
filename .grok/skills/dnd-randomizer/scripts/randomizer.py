#!/usr/bin/env python3
"""Unified D&D randomization — items, characters, worlds, tables, total chaos."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"))

from bootstrap import ensure_utils_importable

ensure_utils_importable()

from class_progression import (  # noqa: E402
    build_multiclass_plan,
    calculate_spell_slots,
    validate_multiclass,
)
from dnd_state_utils import (  # noqa: E402
    get_kingdom_state,
    get_world_state,
    load_json,
    save_json,
    update_kingdom_state,
    update_world_state,
)
from event_system import record_event  # noqa: E402
from paths import get_campaign_path  # noqa: E402

from randomizer_data import (  # noqa: E402
    ALIGNMENTS,
    BACKGROUNDS,
    CLASSES,
    FEATS,
    NAME_PREFIXES,
    NAME_SUFFIXES,
    PERSON_FIRST,
    PERSON_LAST,
    PERSONALITY_TRAITS,
    RACES,
    SPEECH_PATTERNS,
    SPELLS_BY_LEVEL,
    WORLD_DOMAINS,
    RANDOMIZER_DATA_VERSION,
)
from randomizer_engine import (  # noqa: E402
    add_custom_entry,
    export_custom_tables,
    import_custom_tables,
    ledger_summary,
    list_tables,
    roll_table,
    weighted_pick,
    ENGINE_VERSION,
)
from name_cultures import (  # noqa: E402
    culture_for_race,
    generate_cultural_name,
    list_cultures,
)
from equipment_generator import generate_starting_equipment  # noqa: E402
from dungeon_generator import generate_dungeon_floor  # noqa: E402

RANDOMIZER_VERSION = "5.0.0"

SKILLS_ROOT = Path(__file__).resolve().parent.parent.parent
RULES_SCRIPTS = SKILLS_ROOT / "dnd-rules-reference" / "scripts"
NPC_SCRIPTS = SKILLS_ROOT / "dnd-npc-personality-weaver" / "scripts"
QUEST_SCRIPTS = SKILLS_ROOT / "dnd-quest-tracker" / "scripts"
CHAR_SCRIPTS = SKILLS_ROOT / "dnd-character-manager" / "scripts"
LOOT_SCRIPTS = SKILLS_ROOT / "dnd-loot-generator" / "scripts"
FORGE_SCRIPTS = SKILLS_ROOT / "dnd-content-forge" / "scripts"


def _rng(seed: Optional[int] = None) -> random.Random:
    return random.Random(seed)


def _roll_stats(rng: random.Random) -> Dict[str, int]:
    stats = {}
    for abbr in ("str", "dex", "con", "int", "wis", "cha"):
        rolls = sorted(rng.randint(1, 6) for _ in range(4))
        stats[abbr] = sum(rolls[1:])
    return stats


def random_name(
    *,
    name_type: str = "person",
    culture: Optional[str] = None,
    race: Optional[str] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    if culture or race:
        cult = culture or culture_for_race(race or "human")
        result = generate_cultural_name(cult, name_type=name_type, seed=seed)
        return {**result, "version": RANDOMIZER_VERSION}

    rng = _rng(seed)
    if name_type == "place":
        name = f"{rng.choice(NAME_PREFIXES)}{rng.choice(NAME_SUFFIXES)}".title()
    elif name_type == "tavern":
        name = f"The {rng.choice(['Prancing', 'Gilded', 'Weary', 'Broken', 'Laughing'])} {rng.choice(['Stag', 'Dragon', 'Mug', 'Crown', 'Rat'])}"
    else:
        name = f"{rng.choice(PERSON_FIRST)} {rng.choice(PERSON_LAST)}"
    return {"type": name_type, "name": name, "version": RANDOMIZER_VERSION}


def random_item(
    *,
    level: int = 5,
    magic_chance: float = 0.35,
    seed: Optional[int] = None,
    campaign_name: Optional[str] = None,
    balanced: bool = False,
) -> Dict[str, Any]:
    if balanced and campaign_name:
        if str(LOOT_SCRIPTS) not in sys.path:
            sys.path.insert(0, str(LOOT_SCRIPTS))
        from procedural_loot import generate_loot  # noqa: E402

        cr = max(0.25, level / 2)
        items = generate_loot(campaign_name, cr=cr, count=1, party_level=level)
        item = items[0] if items else {"name": "Empty coffer", "note": "No loot rolled"}
        return {
            "item": item,
            "balanced": True,
            "source": "dnd-loot-generator",
            "level": level,
            "version": RANDOMIZER_VERSION,
        }

    rng = _rng(seed)
    if campaign_name:
        table = "magic_item" if rng.random() < magic_chance else "mundane_item"
        rolled = roll_table(table, campaign_name=campaign_name, count=1, seed=seed, use_ledger=True)
        if "results" in rolled:
            item = rolled["results"][0]
            return {"item": item, "table": table, "level": level, "version": RANDOMIZER_VERSION}
    from randomizer_data import MAGIC_ITEMS, MUNDANE_ITEMS  # noqa: E402

    pool = MAGIC_ITEMS if rng.random() < magic_chance else MUNDANE_ITEMS
    item = weighted_pick(pool, rng=rng)
    return {"item": item, "magic": pool is MAGIC_ITEMS, "level": level, "version": RANDOMIZER_VERSION}


def random_character(
    *,
    level: int = 1,
    multiclass: bool = False,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = _rng(seed)
    race = rng.choice(RACES)
    background = rng.choice(BACKGROUNDS)
    alignment = rng.choice(ALIGNMENTS)
    stats = _roll_stats(rng)
    cult = culture_for_race(race)
    name = generate_cultural_name(cult, name_type="person", seed=rng.randint(0, 999999))["name"]

    primary = rng.choice(CLASSES)
    classes = [{"name": primary, "level": level}]
    multiclass_valid = True
    if multiclass and level >= 2:
        candidates = [c for c in CLASSES if c != primary]
        rng.shuffle(candidates)
        second = primary
        for cand in candidates:
            check = validate_multiclass(stats, [{"name": primary, "level": max(1, level - 1)}], cand)
            if check.get("valid"):
                second = cand
                break
        if second != primary:
            split = rng.randint(1, level - 1)
            classes = [
                {"name": primary, "level": level - split},
                {"name": second, "level": split},
            ]
        else:
            multiclass_valid = False

    feats = []
    if level >= 4 and rng.random() < 0.5:
        feats.append({"name": rng.choice(FEATS), "source": "random"})

    known_spells = []
    caster = primary.lower() in ("wizard", "sorcerer", "cleric", "druid", "bard", "warlock", "paladin", "ranger")
    if caster:
        for lvl, spells in SPELLS_BY_LEVEL.items():
            if lvl <= min(3, level // 2 + 1):
                known_spells.append(rng.choice(spells))

    slots = calculate_spell_slots(classes)
    equip = generate_starting_equipment(primary, level=level, seed=rng.randint(0, 999999))
    bonus_item = random_item(level=level, seed=rng.randint(0, 999999))["item"]
    char = {
        "name": name,
        "race": race,
        "background": background,
        "alignment": alignment,
        "classes": classes,
        "level": level,
        "stats": stats,
        "proficiency_bonus": 2 + ((level - 1) // 4),
        "hit_points": {"current": 10 + level * 6, "max": 10 + level * 6, "temp": 0},
        "feats": feats,
        "inventory": equip["equipment"] + [bonus_item],
        "gold_gp": equip["gold_gp"],
        "spell_slots": {"max": slots.get("slots", {}), "used": {}} if slots.get("slots") else None,
        "known_spells": known_spells,
        "notes": "Generated by dnd-randomizer",
        "homebrew": {"randomized": True, "name_culture": cult},
    }
    char["build_plan"] = build_multiclass_plan(classes)
    return {
        "character": char,
        "multiclass_valid": multiclass_valid,
        "version": RANDOMIZER_VERSION,
    }


def random_npc(*, seed: Optional[int] = None, campaign_name: Optional[str] = None) -> Dict[str, Any]:
    rng = _rng(seed)
    role_roll = roll_table("npc_role", campaign_name=campaign_name, seed=seed) if campaign_name else None
    role = role_roll["results"][0]["name"] if role_roll and role_roll.get("results") else rng.choice(
        ["merchant", "guard", "sage"]
    )
    npc_race = rng.choice(RACES)
    cult = culture_for_race(npc_race)
    name = generate_cultural_name(cult, name_type="person", seed=rng.randint(0, 999999))["name"]
    return {
        "npc": {
            "name": name,
            "role": role,
            "race": npc_race,
            "alignment": rng.choice(ALIGNMENTS),
            "personality": rng.choice(PERSONALITY_TRAITS),
            "speech": rng.choice(SPEECH_PATTERNS),
            "motivation": rng.choice(["profit", "revenge", "redemption", "knowledge", "power"]),
            "quirk": rng.choice(["never sits", "quotes poetry", "afraid of birds", "collects teeth"]),
            "secret": rng.choice(["owes a crime lord", "is a disguised noble", "hunts a lost sibling", "none yet"]),
        },
        "version": RANDOMIZER_VERSION,
    }


def random_world(*, seed: Optional[int] = None, campaign_name: Optional[str] = None) -> Dict[str, Any]:
    rng = _rng(seed)
    existing_world = get_world_state(campaign_name) if campaign_name else {}
    existing_kingdom = get_kingdom_state(campaign_name) if campaign_name else {}
    domain = existing_kingdom.get("domain_name") or rng.choice(WORLD_DOMAINS)
    if existing_world.get("current_location"):
        location = existing_world["current_location"]
    else:
        location = f"{rng.choice(['North', 'South', 'East', 'West'])}ern {domain}"

    def _tbl(name: str) -> str:
        if campaign_name:
            r = roll_table(name, campaign_name=campaign_name, count=1, seed=rng.randint(0, 999999))
            if r.get("results"):
                return r["results"][0]["name"]
        return roll_table(name, count=1, seed=rng.randint(0, 999999))["results"][0]["name"]

    world = {
        "domain_name": domain,
        "current_location": location,
        "weather": _tbl("weather"),
        "terrain": _tbl("terrain"),
        "government": _tbl("government"),
        "threat": _tbl("world_threat"),
        "hook": _tbl("quest_hook"),
        "in_game_time": rng.choice(["dawn", "midday", "dusk", "midnight"]),
        "mode": existing_world.get("mode") or rng.choice(["tabletop", "sandbox", "kingdom"]),
        "notes": "Random world seed from dnd-randomizer",
    }
    if existing_world.get("weather") and rng.random() < 0.4:
        world["weather"] = existing_world["weather"]
    if existing_kingdom.get("factions"):
        factions = existing_kingdom["factions"]
    else:
        factions = {
            rng.choice(["locals", "merchants", "militia", "cult", "nobles"]): {
                "influence": rng.randint(1, 30),
                "attitude": rng.choice(["friendly", "neutral", "hostile", "wary"]),
                "goals": [rng.choice(["expand_trade", "secure_borders", "seek_alliance"])],
            }
        }
    return {
        "world": world,
        "kingdom": {
            "domain_name": domain,
            "resources": {
                "gold": rng.randint(100, 2000),
                "food": rng.randint(50, 500),
                "materials": rng.randint(20, 300),
            },
            "factions": factions,
            "population": rng.randint(500, 50000),
        },
        "version": RANDOMIZER_VERSION,
    }


def random_encounter(
    *,
    party_level: int = 3,
    seed: Optional[int] = None,
    campaign_name: Optional[str] = None,
    balanced: bool = False,
) -> Dict[str, Any]:
    if balanced and campaign_name:
        if str(FORGE_SCRIPTS) not in sys.path:
            sys.path.insert(0, str(FORGE_SCRIPTS))
        from encounter_builder import build_encounter  # noqa: E402

        themes = ["ambush", "patrol", "lair", "ritual", "siege"]
        theme = _rng(seed).choice(themes)
        enc = build_encounter(campaign_name, theme=theme, difficulty="Medium")
        return {
            "balanced": True,
            "source": "dnd-content-forge",
            "party_level": enc.get("party_level", party_level),
            "terrain": enc.get("terrain"),
            "theme": enc.get("theme"),
            "enemies": enc.get("enemies"),
            "xp_budget": enc.get("xp_budget"),
            "generation_prompt": enc.get("generation_prompt"),
            "version": RANDOMIZER_VERSION,
        }

    rng = _rng(seed)
    terrain = roll_table("terrain", count=1, seed=seed)["results"][0]["name"]
    feature = roll_table("dungeon_feature", count=1, seed=rng.randint(0, 999999))["results"][0]["name"]
    num_foes = rng.randint(1, 4)
    cr_each = max(0.25, party_level / num_foes * rng.uniform(0.5, 1.2))
    foes = [
        {
            "name": rng.choice(["Goblin", "Bandit", "Wolf", "Skeleton", "Cultist", "Stirge"]),
            "cr": round(cr_each, 2),
            "count": rng.randint(1, 3),
        }
        for _ in range(num_foes)
    ]
    return {
        "party_level": party_level,
        "terrain": terrain,
        "feature": feature,
        "complication": roll_table("travel_complication", count=1, seed=rng.randint(0, 999999))["results"][0]["name"],
        "foes": foes,
        "version": RANDOMIZER_VERSION,
    }


def _srd_feats() -> List[str]:
    if str(RULES_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(RULES_SCRIPTS))
    try:
        from srd_data import FEATS as SRD_FEATS  # noqa: E402

        return list(SRD_FEATS.keys())
    except ImportError:
        return FEATS


def _srd_spells() -> Dict[int, List[str]]:
    if str(RULES_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(RULES_SCRIPTS))
    try:
        from srd_data import SPELLS  # noqa: E402

        by_level: Dict[int, List[str]] = {}
        for key, data in SPELLS.items():
            lvl = data.get("level", 0)
            by_level.setdefault(lvl, []).append(data.get("name", key))
        return by_level
    except ImportError:
        return SPELLS_BY_LEVEL


def random_feat(*, seed: Optional[int] = None) -> Dict[str, Any]:
    rng = _rng(seed)
    pool = _srd_feats()
    feat_key = rng.choice(pool)
    if str(RULES_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(RULES_SCRIPTS))
    try:
        from srd_data import lookup_feat  # noqa: E402

        detail = lookup_feat(feat_key)
        if detail.get("found"):
            return {"feat": detail.get("name", feat_key), "detail": detail, "version": RANDOMIZER_VERSION}
    except ImportError:
        pass
    return {"feat": feat_key, "version": RANDOMIZER_VERSION}


def random_spell(*, max_level: int = 3, seed: Optional[int] = None) -> Dict[str, Any]:
    rng = _rng(seed)
    spells_by_level = _srd_spells()
    level = rng.randint(0, min(max_level, 9))
    pool = spells_by_level.get(level) or spells_by_level.get(0, ["Cantrip"])
    spell = rng.choice(pool)
    return {"spell": spell, "level": level, "version": RANDOMIZER_VERSION}


def random_quest(*, seed: Optional[int] = None, campaign_name: Optional[str] = None) -> Dict[str, Any]:
    rng = _rng(seed)
    hook = roll_table("quest_hook", campaign_name=campaign_name, count=1, seed=seed)
    hook_text = hook["results"][0]["name"] if hook.get("results") else "Unknown quest"
    return {
        "quest": {
            "title": hook_text[:60],
            "hook": hook_text,
            "urgency": rng.choice(["low", "medium", "high"]),
            "reward_hint": random_item(level=rng.randint(1, 10), seed=rng.randint(0, 999999))["item"]["name"],
        },
        "version": RANDOMIZER_VERSION,
    }


def random_party(
    *,
    size: int = 4,
    level: int = 3,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = _rng(seed)
    party_size = max(3, min(5, size))
    members = []
    for _ in range(party_size):
        gen = random_character(
            level=level,
            multiclass=level >= 2 and rng.random() < 0.25,
            seed=rng.randint(0, 999999),
        )
        members.append(gen["character"])
    return {
        "party_size": party_size,
        "level": level,
        "party": members,
        "version": RANDOMIZER_VERSION,
    }


def random_dungeon(
    *,
    rooms: int = 6,
    party_level: int = 3,
    campaign_name: Optional[str] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    floor = generate_dungeon_floor(
        rooms=rooms,
        party_level=party_level,
        campaign_name=campaign_name,
        seed=seed,
    )
    return {"dungeon": floor, "version": RANDOMIZER_VERSION}


def wild_magic_surge(
    *,
    seed: Optional[int] = None,
    campaign_name: Optional[str] = None,
) -> Dict[str, Any]:
    surge = roll_table(
        "wild_magic",
        campaign_name=campaign_name,
        count=1,
        seed=seed,
        use_ledger=bool(campaign_name),
    )
    effect = surge["results"][0]["name"] if surge.get("results") else "Uncontrolled arcane feedback"
    return {
        "trigger": "spell_cast",
        "surge": effect,
        "roll": surge,
        "dm_note": "Apply immediately for Wild Magic Surge or optional sorcerer table.",
        "version": RANDOMIZER_VERSION,
    }


def random_everything(
    campaign_name: Optional[str] = None,
    *,
    level: int = 3,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = _rng(seed)
    s = lambda: rng.randint(0, 999999)
    package = {
        "character": random_character(level=level, multiclass=rng.random() < 0.3, seed=s())["character"],
        "npc": random_npc(campaign_name=campaign_name, seed=s())["npc"],
        "world": random_world(campaign_name=campaign_name, seed=s()),
        "encounter": random_encounter(party_level=level, seed=s()),
        "item": random_item(level=level, campaign_name=campaign_name, seed=s()),
        "quest": random_quest(campaign_name=campaign_name, seed=s())["quest"],
        "feat": random_feat(seed=s())["feat"],
        "spell": random_spell(seed=s()),
        "name_place": random_name(name_type="place", seed=s()),
        "version": RANDOMIZER_VERSION,
    }
    return package


def apply_character(campaign_name: str, *, seed: Optional[int] = None, level: int = 1) -> Dict[str, Any]:
    gen = random_character(level=level, multiclass=level > 1, seed=seed)
    char = gen["character"]
    path = get_campaign_path(campaign_name) / "state" / "player_character.json"
    save_json(path, char)
    record_event(campaign_name, f"Random character applied: {char['name']}", tags=["randomizer", "character"])
    return {"applied": str(path), "character": char, "version": RANDOMIZER_VERSION}


def apply_world(campaign_name: str, *, seed: Optional[int] = None) -> Dict[str, Any]:
    gen = random_world(campaign_name=campaign_name, seed=seed)
    update_world_state(campaign_name, gen["world"])
    update_kingdom_state(campaign_name, gen["kingdom"])
    record_event(campaign_name, f"Random world applied: {gen['world']['domain_name']}", tags=["randomizer", "world"])
    return {"world": gen["world"], "kingdom": gen["kingdom"], "version": RANDOMIZER_VERSION}


def apply_npc(campaign_name: str, *, seed: Optional[int] = None) -> Dict[str, Any]:
    gen = random_npc(campaign_name=campaign_name, seed=seed)
    npc = gen["npc"]
    if str(NPC_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(NPC_SCRIPTS))
    from npc_manager import create_npc  # noqa: E402

    record = create_npc(campaign_name, {
        "name": npc["name"],
        "personality": npc.get("personality", ""),
        "speech": npc.get("speech", ""),
        "motivation": npc.get("motivation", ""),
        "quirk": npc.get("quirk", ""),
        "secret": npc.get("secret", ""),
        "notes": f"Role: {npc.get('role')}; Race: {npc.get('race')}; Alignment: {npc.get('alignment')}",
    })
    return {"applied": True, "npc": record, "version": RANDOMIZER_VERSION}


def apply_quest(campaign_name: str, *, seed: Optional[int] = None) -> Dict[str, Any]:
    gen = random_quest(campaign_name=campaign_name, seed=seed)
    quest = gen["quest"]
    if str(QUEST_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(QUEST_SCRIPTS))
    from quest_tracker import add_quest  # noqa: E402

    saved = add_quest(
        campaign_name,
        quest["title"],
        summary=quest["hook"],
        reward=quest.get("reward_hint", ""),
    )
    return {"applied": True, "quest": saved, "version": RANDOMIZER_VERSION}


def add_random_loot(campaign_name: str, *, level: int = 5, seed: Optional[int] = None) -> Dict[str, Any]:
    item = random_item(level=level, campaign_name=campaign_name, seed=seed)["item"]
    if str(CHAR_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(CHAR_SCRIPTS))
    from character_manager import update_inventory  # noqa: E402

    result = update_inventory(campaign_name, "add", {"name": item.get("name", "Mystery item"), "type": "loot"})
    record_event(campaign_name, f"Random loot added: {item.get('name')}", tags=["randomizer", "loot"])
    return {"item": item, "inventory": result, "version": RANDOMIZER_VERSION}


def travel_day(campaign_name: str, *, seed: Optional[int] = None) -> Dict[str, Any]:
    rng = _rng(seed)
    s = lambda: rng.randint(0, 999999)
    return {
        "weather": roll_table("weather", campaign_name=campaign_name, count=1, seed=s()),
        "complication": roll_table("travel_complication", campaign_name=campaign_name, count=1, seed=s()),
        "terrain": roll_table("terrain", campaign_name=campaign_name, count=1, seed=s()),
        "social_scene": roll_table("social_scene", campaign_name=campaign_name, count=1, seed=s()),
        "version": RANDOMIZER_VERSION,
    }


def mobile_summary(
    kind: str,
    *,
    campaign_name: Optional[str] = None,
    seed: Optional[int] = None,
    level: int = 3,
) -> Dict[str, Any]:
    """One-line mobile/voice-friendly random result."""
    generators = {
        "item": lambda: random_item(level=level, campaign_name=campaign_name, seed=seed),
        "character": lambda: random_character(level=level, seed=seed),
        "npc": lambda: random_npc(campaign_name=campaign_name, seed=seed),
        "world": lambda: random_world(campaign_name=campaign_name, seed=seed),
        "encounter": lambda: random_encounter(party_level=level, seed=seed),
        "quest": lambda: random_quest(campaign_name=campaign_name, seed=seed),
        "feat": lambda: random_feat(seed=seed),
        "spell": lambda: random_spell(seed=seed),
        "trinket": lambda: roll_table("trinket", campaign_name=campaign_name, count=1, seed=seed),
        "trap": lambda: roll_table("trap", campaign_name=campaign_name, count=1, seed=seed),
        "wild_magic": lambda: wild_magic_surge(seed=seed, campaign_name=campaign_name),
        "dungeon": lambda: random_dungeon(
            party_level=level, campaign_name=campaign_name, seed=seed
        ),
        "party": lambda: random_party(size=4, level=level, seed=seed),
    }
    if kind not in generators:
        return {"error": f"Unknown kind: {kind}", "available": sorted(generators.keys())}

    data = generators[kind]()
    line = ""
    if kind == "item":
        line = f"Random item: {data['item'].get('name')}"
    elif kind == "character":
        c = data["character"]
        line = f"{c['name']} — L{c['level']} {c['race']} {'/'.join(x['name'] for x in c['classes'])}"
    elif kind == "npc":
        n = data["npc"]
        line = f"{n['name']} ({n['role']}) — {n.get('personality', '')}"
    elif kind == "world":
        w = data["world"]
        line = f"{w['current_location']}: {w['weather']}, threat — {w['threat']}"
    elif kind == "encounter":
        foes = ", ".join(f"{f['count']}x {f['name']}" for f in data["foes"][:3])
        line = f"Encounter on {data['terrain']}: {foes}"
    elif kind == "quest":
        line = f"Quest hook: {data['quest']['hook']}"
    elif kind == "feat":
        line = f"Random feat: {data['feat']}"
    elif kind == "spell":
        line = f"Random spell (L{data['level']}): {data['spell']}"
    elif kind in ("trinket", "trap"):
        line = data["results"][0]["name"] if data.get("results") else str(data)
    elif kind == "wild_magic":
        line = f"Wild magic surge: {data.get('surge', 'Unknown effect')}"
    elif kind == "dungeon":
        d = data.get("dungeon", {})
        line = f"Dungeon floor: {d.get('room_count', 0)} rooms, theme — {d.get('theme', 'unknown')}"
    elif kind == "party":
        names = ", ".join(m["name"] for m in data.get("party", [])[:4])
        line = f"Random party (L{data.get('level', '?')}): {names}"

    return {"kind": kind, "summary": line, "detail": data, "version": RANDOMIZER_VERSION}


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified D&D randomizer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list-tables")
    p_list.add_argument("campaign", nargs="?")

    p_roll = sub.add_parser("roll-table")
    p_roll.add_argument("table")
    p_roll.add_argument("campaign", nargs="?")
    p_roll.add_argument("--count", type=int, default=1)
    p_roll.add_argument("--seed", type=int)
    p_roll.add_argument("--no-ledger", action="store_true")

    p_item = sub.add_parser("random-item")
    p_item.add_argument("campaign", nargs="?")
    p_item.add_argument("--level", type=int, default=5)
    p_item.add_argument("--seed", type=int)
    p_item.add_argument("--balanced", action="store_true")

    p_char = sub.add_parser("random-character")
    p_char.add_argument("--level", type=int, default=1)
    p_char.add_argument("--multiclass", action="store_true")
    p_char.add_argument("--seed", type=int)

    p_npc = sub.add_parser("random-npc")
    p_npc.add_argument("campaign", nargs="?")
    p_npc.add_argument("--seed", type=int)

    p_world = sub.add_parser("random-world")
    p_world.add_argument("campaign", nargs="?")
    p_world.add_argument("--seed", type=int)

    p_enc = sub.add_parser("random-encounter")
    p_enc.add_argument("campaign", nargs="?")
    p_enc.add_argument("--party-level", type=int, default=3)
    p_enc.add_argument("--seed", type=int)
    p_enc.add_argument("--balanced", action="store_true")

    p_name = sub.add_parser("random-name")
    p_name.add_argument("--type", default="person", choices=["person", "place", "tavern"])
    p_name.add_argument("--culture", choices=list_cultures())
    p_name.add_argument("--race")
    p_name.add_argument("--seed", type=int)

    sub.add_parser("list-cultures")

    p_feat = sub.add_parser("random-feat")
    p_feat.add_argument("--seed", type=int)

    p_spell = sub.add_parser("random-spell")
    p_spell.add_argument("--max-level", type=int, default=3)
    p_spell.add_argument("--seed", type=int)

    p_quest = sub.add_parser("random-quest")
    p_quest.add_argument("campaign", nargs="?")
    p_quest.add_argument("--seed", type=int)

    p_all = sub.add_parser("random-everything")
    p_all.add_argument("campaign", nargs="?")
    p_all.add_argument("--level", type=int, default=3)
    p_all.add_argument("--seed", type=int)

    p_apply_c = sub.add_parser("apply-character")
    p_apply_c.add_argument("campaign")
    p_apply_c.add_argument("--level", type=int, default=1)
    p_apply_c.add_argument("--seed", type=int)

    p_apply_w = sub.add_parser("apply-world")
    p_apply_w.add_argument("campaign")
    p_apply_w.add_argument("--seed", type=int)

    p_ledger = sub.add_parser("ledger")
    p_ledger.add_argument("campaign")
    p_ledger.add_argument("--limit", type=int, default=20)

    p_add = sub.add_parser("add-table-entry")
    p_add.add_argument("campaign")
    p_add.add_argument("table")
    p_add.add_argument("name")
    p_add.add_argument("--weight", type=int, default=1)

    p_apply_n = sub.add_parser("apply-npc")
    p_apply_n.add_argument("campaign")
    p_apply_n.add_argument("--seed", type=int)

    p_apply_q = sub.add_parser("apply-quest")
    p_apply_q.add_argument("campaign")
    p_apply_q.add_argument("--seed", type=int)

    p_loot = sub.add_parser("add-random-loot")
    p_loot.add_argument("campaign")
    p_loot.add_argument("--level", type=int, default=5)
    p_loot.add_argument("--seed", type=int)

    p_travel = sub.add_parser("travel-day")
    p_travel.add_argument("campaign")
    p_travel.add_argument("--seed", type=int)

    p_mobile = sub.add_parser("mobile-summary")
    p_mobile.add_argument("kind")
    p_mobile.add_argument("campaign", nargs="?")
    p_mobile.add_argument("--level", type=int, default=3)
    p_mobile.add_argument("--seed", type=int)

    p_party = sub.add_parser("random-party")
    p_party.add_argument("--size", type=int, default=4)
    p_party.add_argument("--level", type=int, default=3)
    p_party.add_argument("--seed", type=int)

    p_dungeon = sub.add_parser("random-dungeon")
    p_dungeon.add_argument("campaign", nargs="?")
    p_dungeon.add_argument("--rooms", type=int, default=6)
    p_dungeon.add_argument("--party-level", type=int, default=3)
    p_dungeon.add_argument("--seed", type=int)

    p_surge = sub.add_parser("wild-magic-surge")
    p_surge.add_argument("campaign", nargs="?")
    p_surge.add_argument("--seed", type=int)

    p_export = sub.add_parser("export-tables")
    p_export.add_argument("campaign")
    p_export.add_argument("--output")

    p_import = sub.add_parser("import-tables")
    p_import.add_argument("campaign")
    p_import.add_argument("input_path")
    p_import.add_argument("--replace", action="store_true")

    args = parser.parse_args()

    if args.cmd == "list-tables":
        result = list_tables(args.campaign)
    elif args.cmd == "roll-table":
        result = roll_table(
            args.table,
            campaign_name=args.campaign,
            count=args.count,
            seed=args.seed,
            use_ledger=not args.no_ledger,
        )
    elif args.cmd == "random-item":
        result = random_item(
            level=args.level,
            seed=args.seed,
            campaign_name=args.campaign,
            balanced=args.balanced,
        )
    elif args.cmd == "random-character":
        result = random_character(level=args.level, multiclass=args.multiclass, seed=args.seed)
    elif args.cmd == "random-npc":
        result = random_npc(seed=args.seed, campaign_name=args.campaign)
    elif args.cmd == "random-world":
        result = random_world(seed=args.seed, campaign_name=args.campaign)
    elif args.cmd == "random-encounter":
        result = random_encounter(
            party_level=args.party_level,
            seed=args.seed,
            campaign_name=args.campaign,
            balanced=args.balanced,
        )
    elif args.cmd == "random-name":
        result = random_name(
            name_type=args.type,
            culture=args.culture,
            race=args.race,
            seed=args.seed,
        )
    elif args.cmd == "list-cultures":
        result = {"cultures": list_cultures(), "version": RANDOMIZER_VERSION}
    elif args.cmd == "random-feat":
        result = random_feat(seed=args.seed)
    elif args.cmd == "random-spell":
        result = random_spell(max_level=args.max_level, seed=args.seed)
    elif args.cmd == "random-quest":
        result = random_quest(seed=args.seed, campaign_name=args.campaign)
    elif args.cmd == "random-everything":
        result = random_everything(args.campaign, level=args.level, seed=args.seed)
    elif args.cmd == "apply-character":
        result = apply_character(args.campaign, seed=args.seed, level=args.level)
    elif args.cmd == "apply-world":
        result = apply_world(args.campaign, seed=args.seed)
    elif args.cmd == "ledger":
        result = ledger_summary(args.campaign, limit=args.limit)
    elif args.cmd == "add-table-entry":
        result = add_custom_entry(args.campaign, args.table, args.name, weight=args.weight)
    elif args.cmd == "apply-npc":
        result = apply_npc(args.campaign, seed=args.seed)
    elif args.cmd == "apply-quest":
        result = apply_quest(args.campaign, seed=args.seed)
    elif args.cmd == "add-random-loot":
        result = add_random_loot(args.campaign, level=args.level, seed=args.seed)
    elif args.cmd == "travel-day":
        result = travel_day(args.campaign, seed=args.seed)
    elif args.cmd == "mobile-summary":
        result = mobile_summary(
            args.kind, campaign_name=args.campaign, seed=args.seed, level=args.level
        )
    elif args.cmd == "random-party":
        result = random_party(size=args.size, level=args.level, seed=args.seed)
    elif args.cmd == "random-dungeon":
        result = random_dungeon(
            rooms=args.rooms,
            party_level=args.party_level,
            campaign_name=args.campaign,
            seed=args.seed,
        )
    elif args.cmd == "wild-magic-surge":
        result = wild_magic_surge(seed=args.seed, campaign_name=args.campaign)
    elif args.cmd == "export-tables":
        result = export_custom_tables(args.campaign, output_path=args.output)
    elif args.cmd == "import-tables":
        result = import_custom_tables(
            args.campaign, args.input_path, merge=not args.replace
        )
    else:
        result = {"error": "unknown command"}

    result.setdefault("data_version", RANDOMIZER_DATA_VERSION)
    result.setdefault("engine_version", ENGINE_VERSION)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()