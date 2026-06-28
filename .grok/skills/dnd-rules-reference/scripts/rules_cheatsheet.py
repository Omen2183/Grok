#!/usr/bin/env python3
"""Full 5e rules quick-reference backend for Grok DM play."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"))

from rules_data import CHEATSHEET, CONDITION_ALIASES, TOPIC_ALIASES  # noqa: E402
from srd_data import (  # noqa: E402
    SRD_DATA_VERSION,
    lookup_feat,
    lookup_spell,
    search_feats,
    search_spells,
)

RULES_BACKEND_VERSION = "4.0.0"


def list_topics(*, tag: Optional[str] = None) -> List[str]:
    if not tag:
        return sorted(CHEATSHEET.keys())
    return sorted(k for k, v in CHEATSHEET.items() if tag.lower() in v.get("tags", []))


def lookup_rule(topic: str, *, campaign_name: Optional[str] = None) -> Dict[str, Any]:
    if campaign_name:
        from rules_homebrew import lookup_homebrew_first  # noqa: E402

        homebrew = lookup_homebrew_first(campaign_name, topic)
        if homebrew:
            return homebrew
    key = topic.lower().replace(" ", "_").replace("-", "_")
    key = CONDITION_ALIASES.get(key, TOPIC_ALIASES.get(key, key))
    if key not in CHEATSHEET:
        matches = [k for k in CHEATSHEET if key in k or k in key]
        if len(matches) == 1:
            key = matches[0]
        else:
            return {
                "found": False,
                "topic": topic,
                "available": sorted(CHEATSHEET.keys()),
            }
    entry = CHEATSHEET[key]
    return {"found": True, "topic": key, **entry}


def search_rules(query: str, *, limit: int = 10) -> Dict[str, Any]:
    needle = query.lower()
    hits: List[Dict[str, Any]] = []
    for topic, entry in CHEATSHEET.items():
        hay = " ".join([topic, entry.get("summary", ""), *entry.get("details", [])]).lower()
        if needle in hay or any(needle in t for t in entry.get("tags", [])):
            hits.append({"topic": topic, "summary": entry.get("summary", "")})
    return {"query": query, "count": len(hits), "results": hits[:limit]}


def lookup_condition(name: str) -> Dict[str, Any]:
    key = name.lower().replace(" ", "_")
    if key in CHEATSHEET:
        return lookup_rule(key)
    if key in CONDITION_ALIASES:
        return lookup_rule(CONDITION_ALIASES[key])
    return lookup_rule("conditions")


def campaign_homebrew_notes(campaign_name: str) -> Dict[str, Any]:
    try:
        from dnd_state_utils import get_world_state  # noqa: E402

        world = get_world_state(campaign_name)
        return {
            "campaign": campaign_name,
            "notes": world.get("notes", ""),
            "mode": world.get("mode", "tabletop"),
            "location": world.get("current_location", ""),
        }
    except Exception as exc:
        return {"campaign": campaign_name, "error": str(exc), "notes": ""}


def main() -> None:
    parser = argparse.ArgumentParser(description="5e rules cheatsheet lookup")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")
    p_topics = sub.add_parser("topics")
    p_topics.add_argument("--tag")

    p_lookup = sub.add_parser("lookup")
    p_lookup.add_argument("topic")
    p_lookup.add_argument("--campaign", default=None)

    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=10)

    p_cond = sub.add_parser("condition")
    p_cond.add_argument("name")

    p_home = sub.add_parser("homebrew")
    p_home.add_argument("campaign")

    p_hb_add = sub.add_parser("homebrew-add")
    p_hb_add.add_argument("campaign")
    p_hb_add.add_argument("topic")
    p_hb_add.add_argument("ruling")

    p_hb_list = sub.add_parser("homebrew-list")
    p_hb_list.add_argument("campaign")
    p_hb_list.add_argument("--topic", default=None)

    p_spell = sub.add_parser("spell", help="Lookup SRD spell")
    p_spell.add_argument("name")

    p_feat = sub.add_parser("feat", help="Lookup SRD feat")
    p_feat.add_argument("name")

    p_spells = sub.add_parser("search-spells")
    p_spells.add_argument("query")
    p_spells.add_argument("--limit", type=int, default=10)

    p_feats = sub.add_parser("search-feats")
    p_feats.add_argument("query")
    p_feats.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    if args.cmd == "list":
        result: Any = {"topics": list_topics(), "version": RULES_BACKEND_VERSION}
    elif args.cmd == "topics":
        result = {"topics": list_topics(tag=args.tag), "tag": args.tag}
    elif args.cmd == "lookup":
        result = lookup_rule(args.topic, campaign_name=args.campaign)
    elif args.cmd == "homebrew-add":
        from rules_homebrew import add_rule  # noqa: E402
        result = add_rule(args.campaign, args.topic, args.ruling)
    elif args.cmd == "homebrew-list":
        from rules_homebrew import list_rules  # noqa: E402
        result = list_rules(args.campaign, topic=args.topic)
    elif args.cmd == "search":
        result = search_rules(args.query, limit=args.limit)
    elif args.cmd == "condition":
        result = lookup_condition(args.name)
    elif args.cmd == "homebrew":
        result = campaign_homebrew_notes(args.campaign)
    elif args.cmd == "spell":
        result = lookup_spell(args.name)
    elif args.cmd == "feat":
        result = lookup_feat(args.name)
    elif args.cmd == "search-spells":
        result = {"query": args.query, "results": search_spells(args.query, limit=args.limit), "version": SRD_DATA_VERSION}
    elif args.cmd == "search-feats":
        result = {"query": args.query, "results": search_feats(args.query, limit=args.limit), "version": SRD_DATA_VERSION}
    else:
        result = {"error": "Unknown command"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()