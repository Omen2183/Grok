#!/usr/bin/env python3
"""Track active quests, hooks, and completion state per campaign."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from dnd_state_utils import load_json, save_json  # noqa: E402
from event_system import record_event  # noqa: E402
from paths import get_campaign_path  # noqa: E402


def _quests_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "quests.json"


def _load_quests(campaign_name: str) -> Dict[str, Any]:
    return load_json(_quests_path(campaign_name), {"quests": [], "hooks": []})


def _save_quests(campaign_name: str, data: Dict[str, Any]) -> None:
    save_json(_quests_path(campaign_name), data)


def add_quest(
    campaign_name: str,
    title: str,
    *,
    summary: str = "",
    objectives: Optional[List[str]] = None,
    reward: str = "",
) -> Dict[str, Any]:
    data = _load_quests(campaign_name)
    quest_id = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")[:40]
    quest = {
        "id": quest_id,
        "title": title,
        "summary": summary,
        "objectives": objectives or [],
        "reward": reward,
        "status": "active",
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
    }
    data.setdefault("quests", []).append(quest)
    _save_quests(campaign_name, data)
    record_event(campaign_name, f"Quest added: {title}", tags=["quest"], metadata={"quest_id": quest_id})
    return quest


def add_hook(campaign_name: str, hook: str) -> Dict[str, Any]:
    data = _load_quests(campaign_name)
    entry = {"text": hook, "added": datetime.now().isoformat(), "resolved": False}
    data.setdefault("hooks", []).append(entry)
    _save_quests(campaign_name, data)
    return entry


def complete_quest(campaign_name: str, quest_id: str, *, notes: str = "") -> Optional[Dict[str, Any]]:
    data = _load_quests(campaign_name)
    for quest in data.get("quests", []):
        if quest.get("id") == quest_id or quest.get("title", "").lower() == quest_id.lower():
            quest["status"] = "completed"
            quest["updated"] = datetime.now().isoformat()
            if notes:
                quest["completion_notes"] = notes
            _save_quests(campaign_name, data)
            record_event(campaign_name, f"Quest completed: {quest.get('title')}", tags=["quest", "completed"])
            return quest
    return None


def list_active(campaign_name: str) -> Dict[str, Any]:
    data = _load_quests(campaign_name)
    active = [q for q in data.get("quests", []) if q.get("status") == "active"]
    hooks = [h for h in data.get("hooks", []) if not h.get("resolved")]
    return {"active_quests": active, "open_hooks": hooks}


def update_objective(campaign_name: str, quest_id: str, objective_index: int, *, done: bool = True) -> Optional[Dict[str, Any]]:
    data = _load_quests(campaign_name)
    for quest in data.get("quests", []):
        if quest.get("id") == quest_id:
            objectives = quest.get("objectives", [])
            if 0 <= objective_index < len(objectives):
                if isinstance(objectives[objective_index], dict):
                    objectives[objective_index]["done"] = done
                else:
                    objectives[objective_index] = {"text": objectives[objective_index], "done": done}
                quest["objectives"] = objectives
                quest["updated"] = datetime.now().isoformat()
                _save_quests(campaign_name, data)
                return quest
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="D&D quest and hook tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("campaign")
    p_add.add_argument("title")
    p_add.add_argument("--summary", default="")
    p_add.add_argument("--objective", action="append", default=[])
    p_add.add_argument("--reward", default="")

    p_hook = sub.add_parser("add-hook")
    p_hook.add_argument("campaign")
    p_hook.add_argument("hook")

    p_done = sub.add_parser("complete")
    p_done.add_argument("campaign")
    p_done.add_argument("quest_id")
    p_done.add_argument("--notes", default="")

    p_list = sub.add_parser("list")
    p_list.add_argument("campaign")

    args = parser.parse_args()

    if args.cmd == "add":
        result = add_quest(args.campaign, args.title, summary=args.summary, objectives=args.objective, reward=args.reward)
    elif args.cmd == "add-hook":
        result = add_hook(args.campaign, args.hook)
    elif args.cmd == "complete":
        result = complete_quest(args.campaign, args.quest_id, notes=args.notes) or {"error": "Quest not found"}
    elif args.cmd == "list":
        result = list_active(args.campaign)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()