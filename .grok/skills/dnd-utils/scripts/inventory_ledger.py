#!/usr/bin/env python3
"""Lightweight party inventory ledger stored per campaign."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dnd_state_utils import load_json, save_json  # noqa: E402
from event_system import record_event  # noqa: E402
from paths import get_campaign_path  # noqa: E402


def inventory_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "inventory_ledger.json"


def load_inventory(campaign_name: str) -> Dict[str, Any]:
    return load_json(inventory_path(campaign_name), {"items": {}, "updated": None})


def save_inventory(campaign_name: str, data: Dict[str, Any]) -> None:
    data["updated"] = datetime.now().isoformat()
    save_json(inventory_path(campaign_name), data)


def add_item(campaign_name: str, item_name: str, quantity: int = 1) -> Dict[str, Any]:
    inv = load_inventory(campaign_name)
    items = inv.setdefault("items", {})
    key = item_name.strip()
    items[key] = int(items.get(key, 0)) + quantity
    save_inventory(campaign_name, inv)
    record_event(campaign_name, f"Inventory +{quantity} {key}", tags=["inventory"])
    return {"item": key, "quantity": items[key], "inventory": inv}


def remove_item(campaign_name: str, item_name: str, quantity: int = 1) -> Dict[str, Any]:
    inv = load_inventory(campaign_name)
    items = inv.setdefault("items", {})
    key = item_name.strip()
    current = int(items.get(key, 0))
    items[key] = max(0, current - quantity)
    if items[key] == 0:
        items.pop(key, None)
    save_inventory(campaign_name, inv)
    record_event(campaign_name, f"Inventory -{quantity} {key}", tags=["inventory"])
    return {"item": key, "quantity": items.get(key, 0), "inventory": inv}


def list_items(campaign_name: str) -> Dict[str, Any]:
    inv = load_inventory(campaign_name)
    return {"campaign": campaign_name, "items": inv.get("items", {}), "updated": inv.get("updated")}


def main() -> None:
    parser = argparse.ArgumentParser(description="Campaign inventory ledger")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("campaign")
    p_add.add_argument("--item", required=True)
    p_add.add_argument("--qty", type=int, default=1)

    p_rm = sub.add_parser("remove")
    p_rm.add_argument("campaign")
    p_rm.add_argument("--item", required=True)
    p_rm.add_argument("--qty", type=int, default=1)

    p_list = sub.add_parser("list")
    p_list.add_argument("campaign")

    args = parser.parse_args()
    if args.cmd == "add":
        result = add_item(args.campaign, args.item, args.qty)
    elif args.cmd == "remove":
        result = remove_item(args.campaign, args.item, args.qty)
    else:
        result = list_items(args.campaign)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()