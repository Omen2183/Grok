#!/usr/bin/env python3
"""
procedural_loot.py — Python backend for dnd-loot-generator skill.

Production-ready loot generation system:
- Weighted random selection from categorized tables
- Party level / CR-aware scaling
- Persistent "already found" ledger per campaign (prevents duplicates)
- Generic, theme-agnostic item generation suitable for any campaign
- CLI + importable functions
- Integrates with dnd_state_utils for context (level, location)

Usage examples:
  python3 procedural_loot.py generate "My Campaign" --cr 3 --count 4
  python3 procedural_loot.py generate "My Campaign" --type magic --level 5
  python3 procedural_loot.py ledger "My Campaign"
"""

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import shared utils
sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))
try:
    from dnd_state_utils import get_campaign_path, load_json, save_json
except ImportError:
    print("Warning: dnd_state_utils not available. Running in limited mode.", file=sys.stderr)
    def get_campaign_path(name): return Path(f"/home/workdir/artifacts/dnd-campaigns/{name}")
    def load_json(p, default=None):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return default or {}
    def save_json(p, data, create_backup=True):
        p.parent.mkdir(parents=True, exist_ok=True)
        temp = p.with_suffix(".tmp")
        try:
            with open(temp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            temp.replace(p)
        except Exception:
            pass

# =============================================================================
# GENERIC LOOT TABLES (Easily extensible)
# =============================================================================

MUNDANE_ITEMS = [
    {"name": "Gold coins", "weight": 30, "value": "varies"},
    {"name": "Silver coins", "weight": 20, "value": "varies"},
    {"name": "Gemstone (small)", "weight": 10, "value": "10-50 gp"},
    {"name": "Fine clothing", "weight": 8, "value": "5-15 gp"},
    {"name": "Quality tool set", "weight": 7, "value": "15-25 gp"},
    {"name": "Potion of Healing (common)", "weight": 15, "value": "50 gp"},
    {"name": "Scroll of a 1st-level spell", "weight": 10, "value": "25-50 gp"},
]

CONSUMABLES = [
    {"name": "Potion of Healing", "weight": 25},
    {"name": "Potion of Greater Healing", "weight": 10},
    {"name": "Antitoxin", "weight": 8},
    {"name": "Oil of Slipperiness", "weight": 5},
    {"name": "Scroll of Protection", "weight": 7},
    {"name": "Goodberry pouch (10 berries)", "weight": 12},
    {"name": "Smoke bomb (3)", "weight": 8},
]

MAGIC_ITEMS_COMMON = [
    {"name": "Cloak of Protection", "weight": 15},
    {"name": "Boots of Striding and Springing", "weight": 10},
    {"name": "Bracers of Armor", "weight": 12},
    {"name": "Ring of Mind Shielding", "weight": 8},
    {"name": "Wand of Magic Detection", "weight": 15},
    {"name": "+1 Weapon (any)", "weight": 20},
    {"name": "Bag of Holding", "weight": 10},
    {"name": "Helm of Telepathy", "weight": 5},
]

MAGIC_ITEMS_UNCOMMON = [
    {"name": "Cloak of Elvenkind", "weight": 12},
    {"name": "Boots of Speed", "weight": 8},
    {"name": "Ring of Protection", "weight": 10},
    {"name": "Wand of Web", "weight": 10},
    {"name": "+1 Shield", "weight": 15},
    {"name": "Gauntlets of Ogre Power", "weight": 7},
    {"name": "Periapt of Wound Closure", "weight": 8},
    {"name": "Decanter of Endless Water", "weight": 10},
    {"name": "Boots of Striding and Springing", "weight": 9},
    {"name": "Cloak of Protection", "weight": 11},
]

MAGIC_ITEMS_RARE = [
    {"name": "+2 Weapon (any)", "weight": 20},
    {"name": "Ring of Evasion", "weight": 10},
    {"name": "Wings of Flying", "weight": 8},
    {"name": "Staff of Fire", "weight": 7},
    {"name": "Cloak of Displacement", "weight": 9},
    {"name": "Periapt of Proof Against Poison", "weight": 8},
]

def get_loot_table(item_type: str, party_level: int) -> List[Dict]:
    """Return appropriate weighted table based on type and party level."""
    if item_type == "mundane":
        return MUNDANE_ITEMS
    elif item_type == "consumable":
        return CONSUMABLES
    elif item_type == "magic":
        if party_level >= 11:
            return MAGIC_ITEMS_RARE + MAGIC_ITEMS_UNCOMMON + MAGIC_ITEMS_COMMON
        elif party_level >= 7:
            return MAGIC_ITEMS_UNCOMMON + MAGIC_ITEMS_COMMON
        else:
            return MAGIC_ITEMS_COMMON
    else:
        # Mixed table with level-appropriate magic
        base = MUNDANE_ITEMS + CONSUMABLES[:4]
        if party_level >= 11:
            base += MAGIC_ITEMS_RARE[:2] + MAGIC_ITEMS_UNCOMMON[:3] + MAGIC_ITEMS_COMMON[:3]
        elif party_level >= 7:
            base += MAGIC_ITEMS_UNCOMMON[:4] + MAGIC_ITEMS_COMMON[:4]
        else:
            base += MAGIC_ITEMS_COMMON[:4]
        return base

def weighted_choice(items: List[Dict]) -> Dict:
    """Select one item using weights."""
    total = sum(item.get("weight", 10) for item in items)
    r = random.uniform(0, total)
    upto = 0
    for item in items:
        weight = item.get("weight", 10)
        if upto + weight >= r:
            return item.copy()
        upto += weight
    return items[-1].copy()

def get_ledger_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "loot_ledger.json"

def load_ledger(campaign_name: str) -> Dict[str, Any]:
    path = get_ledger_path(campaign_name)
    return load_json(path, {"found_items": [], "last_updated": None})

def save_ledger(campaign_name: str, ledger: Dict[str, Any]) -> None:
    """Save the loot ledger with atomic write protection."""
    path = get_ledger_path(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    ledger["last_updated"] = datetime.now().isoformat()
    
    # Atomic write protection
    temp_path = path.with_suffix(".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2, ensure_ascii=False)
        temp_path.replace(path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        print(f"Warning: Failed to save loot ledger for {campaign_name}: {e}", file=sys.stderr)

def generate_loot(campaign_name: str, cr: float = 1.0, count: int = 3, 
                  item_type: str = "mixed", party_level: int = 3,
                  avoid_duplicates: bool = True) -> List[Dict]:
    """
    Generate a list of loot items.
    - cr: Challenge rating of encounter (affects quality slightly)
    - count: Number of items to generate
    - item_type: "mundane", "consumable", "magic", or "mixed"
    - avoid_duplicates: Respect the campaign's loot ledger
    """
    table = get_loot_table(item_type, party_level)
    ledger = load_ledger(campaign_name)
    found = set(ledger.get("found_items", []))
    
    results = []
    attempts = 0
    max_attempts = count * 5  # prevent infinite loops on small tables

    while len(results) < count and attempts < max_attempts:
        attempts += 1
        item = weighted_choice(table)
        item_name = item["name"]

        if avoid_duplicates and item_name in found:
            continue

        # Light CR scaling flavor
        if cr >= 5 and item_type in ["magic", "mixed"] and random.random() < 0.3:
            item["note"] = "Found on a powerful foe"

        results.append(item)
        found.add(item_name)

    # Update ledger
    ledger["found_items"] = list(found)
    save_ledger(campaign_name, ledger)

    return results

def get_ledger(campaign_name: str) -> Dict[str, Any]:
    return load_ledger(campaign_name)


def generate_hoard(campaign_name: str, party_level: int = 5, cr: float = 5.0) -> Dict[str, Any]:
    """
    Generate a proper treasure hoard (coins + items).
    Suitable for boss fights, dungeons, or major rewards.
    """
    # Coin generation (simplified 5e-style)
    gold = random.randint(100, 400) * max(1, int(party_level / 2))
    silver = random.randint(200, 600)
    copper = random.randint(500, 1500)

    # Item generation
    num_magic = max(1, party_level // 3)
    magic_items = generate_loot(
        campaign_name,
        cr=cr,
        count=num_magic,
        item_type="magic",
        party_level=party_level,
        avoid_duplicates=True
    )

    num_consumables = random.randint(1, 3)
    consumables = generate_loot(
        campaign_name,
        cr=cr,
        count=num_consumables,
        item_type="consumable",
        party_level=party_level,
        avoid_duplicates=False
    )

    hoard = {
        "coins": {
            "gold": gold,
            "silver": silver,
            "copper": copper
        },
        "magic_items": magic_items,
        "consumables": consumables,
        "total_value_estimate": f"~{gold + (silver // 10) + (copper // 100)} gp + items"
    }

    return hoard

# =============================================================================
# CLI
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Procedural Loot Generator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("generate", help="Generate loot for a campaign")
    p_gen.add_argument("campaign")
    p_gen.add_argument("--cr", type=float, default=1.0, help="Challenge rating of encounter")
    p_gen.add_argument("--count", type=int, default=3, help="Number of items")
    p_gen.add_argument("--type", choices=["mixed", "mundane", "consumable", "magic"], default="mixed")
    p_gen.add_argument("--level", type=int, default=3, help="Approximate party level")
    p_gen.add_argument("--allow-duplicates", action="store_true", help="Allow previously found items")

    p_ledger = sub.add_parser("ledger", help="Show what has already been found")
    p_ledger.add_argument("campaign")

    p_hoard = sub.add_parser("hoard", help="Generate a treasure hoard")
    p_hoard.add_argument("campaign")
    p_hoard.add_argument("--level", type=int, default=5, help="Party level")
    p_hoard.add_argument("--cr", type=float, default=5.0, help="Challenge rating of encounter")

    args = parser.parse_args()

    if args.cmd == "generate":
        items = generate_loot(
            args.campaign,
            cr=args.cr,
            count=args.count,
            item_type=args.type,
            party_level=args.level,
            avoid_duplicates=not args.allow_duplicates
        )
        print(json.dumps({
            "generated": items,
            "count": len(items),
            "parameters": {
                "cr": args.cr,
                "type": args.type,
                "level": args.level
            }
        }, indent=2))

    elif args.cmd == "ledger":
        ledger = get_ledger(args.campaign)
        print(json.dumps(ledger, indent=2))

    elif args.cmd == "hoard":
        hoard = generate_hoard(args.campaign, party_level=args.level, cr=args.cr)
        print(json.dumps(hoard, indent=2))

if __name__ == "__main__":
    main()
