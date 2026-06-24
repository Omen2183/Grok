#!/usr/bin/env python3
"""Lore storage, query, and summary for long-running campaigns."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"))

from dnd_state_utils import get_kingdom_state, get_world_state, load_json, save_json  # noqa: E402
from event_system import record_event, search_events  # noqa: E402
from paths import get_campaign_path  # noqa: E402


def lore_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "lore_summary.md"


def append_lore(campaign_name: str, entry: str, *, tag: str = "lore") -> Dict[str, Any]:
    path = lore_path(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    block = f"\n\n### {stamp}\n{entry.strip()}\n"
    if path.exists():
        path.write_text(path.read_text(encoding="utf-8") + block, encoding="utf-8")
    else:
        path.write_text(f"# Lore Summary — {campaign_name}{block}", encoding="utf-8")
    record_event(campaign_name, entry[:200], tags=[tag, "lore"])
    return {"saved": str(path), "entry": entry}


def get_lore_summary(campaign_name: str) -> str:
    path = lore_path(campaign_name)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "No lore summary recorded yet."


def list_npc_profiles(campaign_name: str) -> Dict[str, Any]:
    npc_dir = get_campaign_path(campaign_name) / "npcs"
    index = load_json(npc_dir / "index.json", {"npcs": []})
    profiles: List[Dict[str, Any]] = []
    for entry in index.get("npcs", []):
        npc_id = entry.get("id") or entry.get("name", "")
        path = npc_dir / f"{npc_id}.json"
        if path.exists():
            profiles.append(load_json(path, {}))
        else:
            profiles.append(entry)
    return {"npc_count": len(profiles), "npcs": profiles}


def list_session_recaps(campaign_name: str, *, limit: int = 10) -> Dict[str, Any]:
    recap_dir = get_campaign_path(campaign_name) / "recaps"
    if not recap_dir.exists():
        return {"recap_count": 0, "recaps": []}
    files = sorted(recap_dir.glob("session_*.md"), reverse=True)[:limit]
    recaps = []
    for path in files:
        recaps.append({"file": path.name, "excerpt": path.read_text(encoding="utf-8")[:500]})
    return {"recap_count": len(recaps), "recaps": recaps}


def query_lore(campaign_name: str, keyword: str, *, limit: int = 10) -> Dict[str, Any]:
    events = search_events(campaign_name, tag="lore", limit=50)
    matches = [
        e for e in events
        if keyword.lower() in e.get("description", "").lower()
    ][:limit]
    world = get_world_state(campaign_name)
    kingdom = get_kingdom_state(campaign_name)
    return {
        "keyword": keyword,
        "matches": matches,
        "location": world.get("current_location"),
        "factions": kingdom.get("factions", {}),
        "lore_excerpt": get_lore_summary(campaign_name)[:800],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Campaign lore archivist")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("append")
    p_add.add_argument("campaign")
    p_add.add_argument("entry")

    p_summary = sub.add_parser("summary")
    p_summary.add_argument("campaign")

    p_query = sub.add_parser("query")
    p_query.add_argument("campaign")
    p_query.add_argument("keyword")

    p_npcs = sub.add_parser("list-npcs")
    p_npcs.add_argument("campaign")

    p_recaps = sub.add_parser("list-recaps")
    p_recaps.add_argument("campaign")
    p_recaps.add_argument("--limit", type=int, default=5)

    args = parser.parse_args()
    if args.cmd == "append":
        result = append_lore(args.campaign, args.entry)
    elif args.cmd == "summary":
        result = {"summary": get_lore_summary(args.campaign)}
    elif args.cmd == "query":
        result = query_lore(args.campaign, args.keyword)
    elif args.cmd == "list-npcs":
        result = list_npc_profiles(args.campaign)
    elif args.cmd == "list-recaps":
        result = list_session_recaps(args.campaign, limit=args.limit)
    else:
        result = {"error": "unknown command"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()