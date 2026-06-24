#!/usr/bin/env python3
"""Shared campaign state management for the D&D skill suite."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from event_system import record_combat_event, record_event, search_events
from paths import get_campaign_path, get_campaigns_root

DEFAULT_WORLD_STATE: Dict[str, Any] = {
    "campaign_name": "",
    "current_location": "Unknown",
    "in_game_time": "Day 1, Morning",
    "mode": "tabletop",
    "weather": "clear",
    "notes": "",
    "last_updated": None,
}

DEFAULT_PLAYER: Dict[str, Any] = {
    "name": "Adventurer",
    "race": "Human",
    "classes": [{"name": "Fighter", "level": 1}],
    "level": 1,
    "proficiency_bonus": 2,
    "stats": {"str": 15, "dex": 14, "con": 13, "int": 10, "wis": 12, "cha": 8},
    "hit_points": {"current": 12, "max": 12, "temp": 0},
    "conditions": [],
    "xp": 0,
    "status": "Alive",
}

DEFAULT_KINGDOM: Dict[str, Any] = {
    "domain_name": "Unsettled Lands",
    "resources": {"gold": 100, "food": 50, "materials": 25},
    "projects": [],
    "factions": {},
    "flags": {"population_tracking": False, "trade_flows": False},
}


def load_json(path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not path.exists():
        return default.copy() if default else {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return default.copy() if default else {}


def save_json(path: Path, data: Dict[str, Any], *, create_backup: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if create_backup and path.exists():
        backup_dir = path.parent.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(path, backup_dir / f"{path.stem}_{stamp}{path.suffix}")

    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
    temp.replace(path)


def _state_dir(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state"


def init_campaign(
    campaign_name: str,
    *,
    force: bool = False,
    pc_name: Optional[str] = None,
    enable_sqlite: bool = False,
) -> Dict[str, Any]:
    root = get_campaign_path(campaign_name)
    world_file = root / "state" / "world_state.json"

    if world_file.exists() and not force:
        return {"status": "exists", "path": str(root), "message": "Campaign already initialized"}

    if force and root.exists():
        backup = root.parent / "backups" / f"{campaign_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copytree(root, backup, dirs_exist_ok=True)

    for subdir in ("state", "npcs", "logs", "recaps", "combat", "encounters", "backups"):
        (root / subdir).mkdir(parents=True, exist_ok=True)

    world = DEFAULT_WORLD_STATE.copy()
    world["campaign_name"] = campaign_name
    world["last_updated"] = datetime.now().isoformat()
    save_json(world_file, world, create_backup=False)

    player = DEFAULT_PLAYER.copy()
    if pc_name:
        player["name"] = pc_name
    save_json(root / "state" / "player_character.json", player, create_backup=False)

    save_json(root / "state" / "kingdom_state.json", DEFAULT_KINGDOM.copy(), create_backup=False)

    session_log = root / "logs" / "session_log.md"
    if not session_log.exists():
        session_log.write_text(
            f"# Session Log — {campaign_name}\n\n*Initialized {datetime.now().date()}*\n",
            encoding="utf-8",
        )

    rolls_log = root / "logs" / "rolls.json"
    if not rolls_log.exists():
        rolls_log.write_text("[]", encoding="utf-8")

    if enable_sqlite:
        (root / "state" / "sqlite_enabled.flag").write_text("1", encoding="utf-8")

    record_event(campaign_name, "Campaign initialized", importance="major", tags=["init"])
    return {"status": "created", "path": str(root), "campaign_name": campaign_name}


def get_world_state(campaign_name: str) -> Dict[str, Any]:
    return load_json(_state_dir(campaign_name) / "world_state.json", DEFAULT_WORLD_STATE)


def load_world_state(campaign_name: str) -> Dict[str, Any]:
    return get_world_state(campaign_name)


def update_world_state(campaign_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    path = _state_dir(campaign_name) / "world_state.json"
    state = load_json(path, DEFAULT_WORLD_STATE)
    state.update(updates)
    state["last_updated"] = datetime.now().isoformat()
    save_json(path, state)
    return state


def get_player_character(campaign_name: str) -> Dict[str, Any]:
    return load_json(_state_dir(campaign_name) / "player_character.json", DEFAULT_PLAYER)


def update_player_hp(
    campaign_name: str,
    *,
    delta: int = 0,
    new_current: Optional[int] = None,
) -> Dict[str, Any]:
    path = _state_dir(campaign_name) / "player_character.json"
    char = load_json(path, DEFAULT_PLAYER)
    hp = char.setdefault("hit_points", {"current": 12, "max": 12, "temp": 0})

    if new_current is not None:
        hp["current"] = max(0, min(new_current, hp.get("max", new_current)))
    else:
        hp["current"] = max(0, hp.get("current", 0) + delta)

    if hp["current"] <= 0:
        char["status"] = "Dying"
    elif char.get("status") in ("Dying", "Dead"):
        char["status"] = "Alive"

    save_json(path, char)
    return hp


def add_condition(campaign_name: str, condition: str) -> Dict[str, Any]:
    path = _state_dir(campaign_name) / "player_character.json"
    char = load_json(path, DEFAULT_PLAYER)
    conditions = char.setdefault("conditions", [])
    if condition not in conditions:
        conditions.append(condition)
    save_json(path, char)
    return char


def update_important_companion(campaign_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    path = _state_dir(campaign_name) / "important_companion.json"
    companion = load_json(path, {})
    companion.update(updates)
    save_json(path, companion)
    return companion


def log_roll(
    campaign_name: str,
    notation: str,
    total: int,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    path = get_campaign_path(campaign_name) / "logs" / "rolls.json"
    rolls: List[Dict[str, Any]] = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as handle:
                rolls = json.load(handle)
        except (json.JSONDecodeError, OSError):
            rolls = []

    rolls.append(
        {
            "timestamp": datetime.now().isoformat(),
            "notation": notation,
            "total": total,
            "metadata": metadata or {},
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(rolls[-500:], handle, indent=2)


def clear_combat_state(campaign_name: str) -> Dict[str, Any]:
    combat_dir = get_campaign_path(campaign_name) / "combat"
    combat_file = combat_dir / "current_combat.json"
    if combat_file.exists():
        ended = combat_dir / f"current_combat.ended_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        combat_file.rename(ended)
        return {"status": "cleared", "archived_to": str(ended)}
    return {"status": "no_active_combat"}


def audit_campaign(campaign_name: str) -> Dict[str, Any]:
    root = get_campaign_path(campaign_name)
    issues: List[str] = []
    recommendations: List[str] = []

    required = [
        root / "state" / "world_state.json",
        root / "state" / "player_character.json",
        root / "logs" / "session_log.md",
    ]
    for req in required:
        if not req.exists():
            issues.append(f"Missing required file: {req.relative_to(root)}")

    world = get_world_state(campaign_name)
    if not world.get("current_location"):
        issues.append("world_state.json has no current_location set")

    player = get_player_character(campaign_name)
    hp = player.get("hit_points", {})
    if hp.get("current", 0) > hp.get("max", 0):
        issues.append("Player current HP exceeds max HP")

    combat_file = root / "combat" / "current_combat.json"
    if combat_file.exists():
        recommendations.append("Active combat file found — run clear-combat after fights end")

    if not issues:
        recommendations.append("Campaign state looks healthy")

    return {
        "campaign": campaign_name,
        "path": str(root),
        "issues": issues,
        "recommendations": recommendations,
        "healthy": len(issues) == 0,
    }


def generate_session_start_summary(campaign_name: str) -> Dict[str, Any]:
    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)
    hp = player.get("hit_points", {})
    recent = search_events(campaign_name, limit=3)

    lines = [
        f"# Resuming {campaign_name}",
        "",
        f"**Location:** {world.get('current_location', 'Unknown')}",
        f"**Time:** {world.get('in_game_time', 'Unknown')}",
        f"**Mode:** {world.get('mode', 'tabletop')}",
        f"**Character:** {player.get('name', 'Adventurer')} (Level {player.get('level', 1)})",
        f"**HP:** {hp.get('current', '?')}/{hp.get('max', '?')}",
    ]
    if recent:
        lines.extend(["", "**Recent events:**"])
        for event in recent:
            lines.append(f"- {event.get('description', '')}")

    return {"briefing_markdown": "\n".join(lines), "world": world, "player": player}


def main() -> None:
    parser = argparse.ArgumentParser(description="D&D campaign state utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("campaign")
    p_init.add_argument("--force", action="store_true")
    p_init.add_argument("--pc-name")
    p_init.add_argument("--enable-sqlite", action="store_true")

    p_status = sub.add_parser("status")
    p_status.add_argument("campaign")

    p_update = sub.add_parser("update")
    p_update.add_argument("campaign")
    p_update.add_argument("--set-location")
    p_update.add_argument("--advance-time", type=int)
    p_update.add_argument("--set-mode", choices=["tabletop", "kingdom"])

    p_audit = sub.add_parser("audit")
    p_audit.add_argument("campaign")

    p_clear = sub.add_parser("clear-combat")
    p_clear.add_argument("campaign")

    p_load = sub.add_parser("load")
    p_load.add_argument("campaign")
    p_load.add_argument("--file", required=True)

    p_summary = sub.add_parser("session-summary")
    p_summary.add_argument("campaign")

    p_event = sub.add_parser("record-event")
    p_event.add_argument("campaign")
    p_event.add_argument("description")
    p_event.add_argument("--importance", default="normal")
    p_event.add_argument("--tags", default="")

    p_search = sub.add_parser("search-events")
    p_search.add_argument("campaign")
    p_search.add_argument("--tag")
    p_search.add_argument("--limit", type=int, default=10)

    p_root = sub.add_parser("campaigns-root")
    args = parser.parse_args()

    if args.cmd == "init":
        result = init_campaign(
            args.campaign,
            force=args.force,
            pc_name=args.pc_name,
            enable_sqlite=args.enable_sqlite,
        )
    elif args.cmd == "status":
        result = {
            "campaign": args.campaign,
            "world": get_world_state(args.campaign),
            "player": get_player_character(args.campaign),
            "campaigns_root": str(get_campaigns_root()),
        }
    elif args.cmd == "update":
        updates: Dict[str, Any] = {}
        if args.set_location:
            updates["current_location"] = args.set_location
        if args.set_mode:
            updates["mode"] = args.set_mode
        if args.advance_time:
            world = get_world_state(args.campaign)
            updates["in_game_time"] = f"{world.get('in_game_time', 'Day 1')} (+{args.advance_time}h)"
        result = update_world_state(args.campaign, updates)
    elif args.cmd == "audit":
        result = audit_campaign(args.campaign)
    elif args.cmd == "clear-combat":
        result = clear_combat_state(args.campaign)
    elif args.cmd == "load":
        file_map = {
            "world_state": "world_state.json",
            "player_character": "player_character.json",
            "kingdom_state": "kingdom_state.json",
            "important_companion": "important_companion.json",
        }
        filename = file_map.get(args.file, args.file)
        path = _state_dir(args.campaign) / filename
        result = load_json(path, {})
    elif args.cmd == "session-summary":
        result = generate_session_start_summary(args.campaign)
    elif args.cmd == "record-event":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        result = record_event(args.campaign, args.description, importance=args.importance, tags=tags)
    elif args.cmd == "search-events":
        result = search_events(args.campaign, tag=args.tag, limit=args.limit)
    elif args.cmd == "campaigns-root":
        result = {"campaigns_root": str(get_campaigns_root())}
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()