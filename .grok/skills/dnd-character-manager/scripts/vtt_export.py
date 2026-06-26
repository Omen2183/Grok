#!/usr/bin/env python3
"""Export characters and combatants to Foundry VTT and Roll20 JSON formats."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"))

from bootstrap import ensure_utils_importable

ensure_utils_importable()

from paths import get_campaign_path  # noqa: E402

VTT_EXPORT_VERSION = "4.0.0"


def _load_character(campaign_name: str) -> Dict[str, Any]:
    path = get_campaign_path(campaign_name) / "state" / "player_character.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_combat(campaign_name: str) -> Dict[str, Any]:
    path = get_campaign_path(campaign_name) / "combat" / "current_combat.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _ability_mod(score: int) -> int:
    return (score - 10) // 2


def export_foundry_actor(char: Dict[str, Any]) -> Dict[str, Any]:
    """Foundry D&D 5e actor JSON (simplified, import-friendly)."""
    stats = char.get("stats", {})
    abilities: Dict[str, Dict[str, int]] = {}
    for abbr in ("str", "dex", "con", "int", "wis", "cha"):
        val = stats.get(abbr, 10)
        mod = _ability_mod(val)
        abilities[abbr] = {"value": val, "mod": mod, "proficient": 0}

    hp = char.get("hit_points", {})
    classes = char.get("classes", [{"name": "Fighter", "level": 1}])
    class_str = " / ".join(f"{c.get('name', '?')} {c.get('level', 0)}" for c in classes)

    return {
        "name": char.get("name", "Adventurer"),
        "type": "character",
        "system": {
            "details": {
                "race": char.get("race", ""),
                "background": char.get("background", ""),
                "level": char.get("level", 1),
                "class": class_str,
            },
            "abilities": abilities,
            "attributes": {
                "hp": {
                    "value": hp.get("current", 0),
                    "max": hp.get("max", 0),
                    "temp": hp.get("temp", 0),
                },
                "ac": {"flat": char.get("armor_class", 10)},
                "prof": char.get("proficiency_bonus", 2),
            },
            "traits": {
                "size": "med",
                "di": {"value": []},
                "dr": {"value": []},
            },
        },
        "flags": {"dnd-skills": {"export_version": VTT_EXPORT_VERSION}},
    }


def export_roll20_character(char: Dict[str, Any]) -> Dict[str, Any]:
    """Roll20-compatible character blob (attributes + abilities)."""
    stats = char.get("stats", {})
    hp = char.get("hit_points", {})
    attrs: Dict[str, Any] = {
        "name": char.get("name", "Adventurer"),
        "race": char.get("race", ""),
        "class": char.get("classes", [{}])[0].get("name", ""),
        "level": char.get("level", 1),
        "hp": hp.get("current", 0),
        "hp_max": hp.get("max", 0),
        "ac": char.get("armor_class", 10),
    }
    for abbr in ("str", "dex", "con", "int", "wis", "cha"):
        val = stats.get(abbr, 10)
        attrs[f"{abbr}_score"] = val
        attrs[f"{abbr}_mod"] = _ability_mod(val)
    return {"character": attrs, "export_version": VTT_EXPORT_VERSION}


def export_combat_foundry(campaign_name: str) -> Dict[str, Any]:
    combat = _load_combat(campaign_name)
    actors: List[Dict[str, Any]] = []
    for c in combat.get("combatants", []):
        actors.append({
            "name": c.get("name", "Unknown"),
            "type": "npc" if not c.get("is_player") else "character",
            "system": {
                "attributes": {
                    "hp": {
                        "value": c.get("hp", c.get("current_hp", 0)),
                        "max": c.get("max_hp", c.get("hp", 0)),
                    },
                    "init": {"bonus": c.get("initiative", 0)},
                },
                "details": {"cr": c.get("cr", "")},
            },
            "flags": {"conditions": c.get("conditions", [])},
        })
    grid = combat.get("grid")
    return {
        "encounter": combat.get("encounter_name", ""),
        "actors": actors,
        "grid": grid,
        "export_version": VTT_EXPORT_VERSION,
    }


def write_export(campaign_name: str, data: Dict[str, Any], filename: str) -> str:
    out_dir = get_campaign_path(campaign_name) / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return str(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="VTT export (Foundry / Roll20)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_f = sub.add_parser("foundry")
    p_f.add_argument("campaign")
    p_r = sub.add_parser("roll20")
    p_r.add_argument("campaign")
    p_c = sub.add_parser("combat-foundry")
    p_c.add_argument("campaign")

    args = parser.parse_args()
    char = _load_character(args.campaign)
    if args.cmd == "foundry":
        data = export_foundry_actor(char)
        path = write_export(args.campaign, data, "character_foundry.json")
        result = {"format": "foundry", "path": path, "preview": data}
    elif args.cmd == "roll20":
        data = export_roll20_character(char)
        path = write_export(args.campaign, data, "character_roll20.json")
        result = {"format": "roll20", "path": path, "preview": data}
    elif args.cmd == "combat-foundry":
        data = export_combat_foundry(args.campaign)
        path = write_export(args.campaign, data, "combat_foundry.json")
        result = {"format": "combat-foundry", "path": path, "preview": data}
    else:
        result = {"error": "unknown command"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()