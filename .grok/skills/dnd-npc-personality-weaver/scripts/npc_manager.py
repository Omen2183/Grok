#!/usr/bin/env python3
"""Persistent NPC storage and relationship tracking."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from event_system import record_event  # noqa: E402
from paths import get_campaign_path  # noqa: E402


def _npc_index_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "npcs" / "index.json"


def _npc_file(campaign_name: str, npc_id: str) -> Path:
    return get_campaign_path(campaign_name) / "npcs" / f"{npc_id}.json"


def _slugify(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")


def _load_index(campaign_name: str) -> Dict[str, Any]:
    path = _npc_index_path(campaign_name)
    if not path.exists():
        return {"npcs": []}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_index(campaign_name: str, index: Dict[str, Any]) -> None:
    path = _npc_index_path(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, ensure_ascii=False)


def create_npc(campaign_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    name = data.get("name", "Unnamed NPC")
    npc_id = data.get("id") or _slugify(name)
    record = {
        "id": npc_id,
        "name": name,
        "personality": data.get("personality", ""),
        "speech": data.get("speech", ""),
        "secret": data.get("secret", ""),
        "motivation": data.get("motivation", ""),
        "quirk": data.get("quirk", ""),
        "attitude": data.get("attitude", "neutral"),
        "faction": data.get("faction", ""),
        "relationship_score": data.get("relationship_score", 0),
        "notes": data.get("notes", ""),
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
    }

    npc_path = _npc_file(campaign_name, npc_id)
    npc_path.parent.mkdir(parents=True, exist_ok=True)
    with open(npc_path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)

    index = _load_index(campaign_name)
    ids = {entry["id"] for entry in index.get("npcs", [])}
    if npc_id not in ids:
        index.setdefault("npcs", []).append({"id": npc_id, "name": name})
        _save_index(campaign_name, index)

    record_event(campaign_name, f"NPC created: {name}", tags=["npc"], metadata={"npc_id": npc_id})
    return record


def update_npc(campaign_name: str, npc_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    path = _npc_file(campaign_name, npc_id)
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as handle:
        record = json.load(handle)

    record.update(updates)
    record["updated"] = datetime.now().isoformat()

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)

    record_event(
        campaign_name,
        f"NPC updated: {record.get('name', npc_id)}",
        tags=["npc"],
        metadata={"npc_id": npc_id},
    )
    return record


def get_npc(campaign_name: str, npc_id: str) -> Optional[Dict[str, Any]]:
    path = _npc_file(campaign_name, npc_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def list_npcs(campaign_name: str) -> List[Dict[str, Any]]:
    return _load_index(campaign_name).get("npcs", [])


def adjust_relationship(campaign_name: str, npc_id: str, delta: int, *, note: str = "") -> Optional[Dict[str, Any]]:
    npc = get_npc(campaign_name, npc_id)
    if not npc:
        return None
    npc["relationship_score"] = npc.get("relationship_score", 0) + delta
    if note:
        npc.setdefault("notes", "")
        npc["notes"] += f"\n[{datetime.now().date()}] {note} ({delta:+d})"
    return update_npc(campaign_name, npc_id, npc)


def main() -> None:
    parser = argparse.ArgumentParser(description="NPC manager for D&D campaigns")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("campaign")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--personality", default="")
    p_create.add_argument("--speech", default="")
    p_create.add_argument("--secret", default="")
    p_create.add_argument("--attitude", default="neutral")

    p_update = sub.add_parser("update")
    p_update.add_argument("campaign")
    p_update.add_argument("npc_id")
    p_update.add_argument("--attitude")
    p_update.add_argument("--note", default="")

    p_get = sub.add_parser("get")
    p_get.add_argument("campaign")
    p_get.add_argument("npc_id")

    p_list = sub.add_parser("list")
    p_list.add_argument("campaign")

    p_rel = sub.add_parser("adjust-relationship")
    p_rel.add_argument("campaign")
    p_rel.add_argument("npc_id")
    p_rel.add_argument("delta", type=int)
    p_rel.add_argument("--note", default="")

    args = parser.parse_args()

    if args.cmd == "create":
        result = create_npc(
            args.campaign,
            {
                "name": args.name,
                "personality": args.personality,
                "speech": args.speech,
                "secret": args.secret,
                "attitude": args.attitude,
            },
        )
    elif args.cmd == "update":
        updates = {}
        if args.attitude:
            updates["attitude"] = args.attitude
        if args.note:
            updates["notes"] = args.note
        result = update_npc(args.campaign, args.npc_id, updates)
    elif args.cmd == "get":
        result = get_npc(args.campaign, args.npc_id) or {"error": "NPC not found"}
    elif args.cmd == "list":
        result = list_npcs(args.campaign)
    elif args.cmd == "adjust-relationship":
        result = adjust_relationship(args.campaign, args.npc_id, args.delta, note=args.note)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()