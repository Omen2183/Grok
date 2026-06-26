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
from paths import get_campaign_path, get_campaigns_root, get_runtime_context

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

    player_md = root / "state" / "player_character.md"
    if not player_md.exists():
        player_md.write_text(
            f"# {player['name']}\n\n*Level {player['level']} {player['race']}*\n",
            encoding="utf-8",
        )

    visual_canon = root / "state" / "visual_canon.md"
    if not visual_canon.exists():
        visual_canon.write_text(
            "# Visual Canon\n\nAdd appearance notes for PCs, companions, and key locations.\n",
            encoding="utf-8",
        )

    session_log = root / "logs" / "session_log.md"
    if not session_log.exists():
        session_log.write_text(
            f"# Session Log — {campaign_name}\n\n*Initialized {datetime.now().date()}*\n",
            encoding="utf-8",
        )

    rolls_log = root / "logs" / "rolls.json"
    if force or not rolls_log.exists():
        rolls_log.write_text("[]", encoding="utf-8")

    events_log = root / "logs" / "events.json"
    if force:
        events_log.write_text("[]", encoding="utf-8")

    if enable_sqlite:
        (root / "state" / "sqlite_enabled.flag").write_text("1", encoding="utf-8")
        try:
            from sqlite_layer import init_db
            init_db(campaign_name)
        except Exception:
            pass

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


def validate_campaign(campaign_name: str) -> Dict[str, Any]:
    """Strict structural validation before long sessions or exports."""
    root = get_campaign_path(campaign_name)
    errors: List[str] = []
    warnings: List[str] = []

    if not root.exists():
        return {"valid": False, "errors": [f"Campaign directory not found: {root}"], "warnings": []}

    required_dirs = ("state", "logs", "npcs", "combat", "recaps")
    for subdir in required_dirs:
        if not (root / subdir).is_dir():
            errors.append(f"Missing directory: {subdir}/")

    required_files = (
        "state/world_state.json",
        "state/player_character.json",
        "state/kingdom_state.json",
        "logs/session_log.md",
        "logs/rolls.json",
    )
    for rel in required_files:
        if not (root / rel).exists():
            errors.append(f"Missing file: {rel}")

    player = get_player_character(campaign_name)
    if not player.get("name"):
        warnings.append("Player character has no name set")
    if player.get("level", 1) < 1 or player.get("level", 1) > 20:
        errors.append(f"Invalid player level: {player.get('level')}")

    try:
        from xp_tables import check_level_up
        level_info = check_level_up(player)
        if level_info["level_up_available"]:
            warnings.append(
                f"XP supports level {level_info['derived_level']} but sheet shows "
                f"level {level_info['stored_level']} — run level-up"
            )
    except Exception:
        pass

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "campaign": campaign_name}


def audit_campaign(campaign_name: str) -> Dict[str, Any]:
    get_campaigns_root(create=True)
    root = get_campaign_path(campaign_name)
    issues: List[str] = []
    recommendations: List[str] = []

    validation = validate_campaign(campaign_name)
    issues.extend(validation.get("errors", []))
    for warning in validation.get("warnings", []):
        recommendations.append(warning)

    required = [
        root / "state" / "world_state.json",
        root / "state" / "player_character.json",
        root / "logs" / "session_log.md",
    ]
    for req in required:
        if not req.exists():
            rel = str(req.relative_to(root))
            if rel not in [e.replace("Missing file: ", "") for e in issues]:
                issues.append(f"Missing required file: {rel}")

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


def enhanced_audit_campaign(campaign_name: str) -> Dict[str, Any]:
    """Extended audit with content inventory and sync checks."""
    base = audit_campaign(campaign_name)
    root = get_campaign_path(campaign_name)
    inventory: Dict[str, Any] = {}

    npc_index = root / "npcs" / "index.json"
    if npc_index.exists():
        npc_data = load_json(npc_index, {})
        inventory["npc_count"] = len(npc_data.get("npcs", []))
    else:
        inventory["npc_count"] = 0

    lore_file = root / "state" / "lore_index.json"
    inventory["lore_entries"] = len(load_json(lore_file, {}).get("entries", [])) if lore_file.exists() else 0

    rolls_path = root / "logs" / "rolls.json"
    if rolls_path.exists():
        try:
            with open(rolls_path, "r", encoding="utf-8") as handle:
                inventory["roll_count"] = len(json.load(handle))
        except (json.JSONDecodeError, OSError):
            inventory["roll_count"] = 0
            base["issues"].append("rolls.json is corrupted")
            base["healthy"] = False
    else:
        inventory["roll_count"] = 0

    recaps = list((root / "recaps").glob("session_*.md")) if (root / "recaps").exists() else []
    inventory["recap_count"] = len(recaps)

    kingdom = get_kingdom_state(campaign_name)
    active_projects = [p for p in kingdom.get("projects", []) if p.get("status") == "queued"]
    inventory["active_kingdom_projects"] = len(active_projects)

    player = get_player_character(campaign_name)
    combat_file = root / "combat" / "current_combat.json"
    if combat_file.exists():
        combat = load_json(combat_file, {})
        for c in combat.get("combatants", []):
            if c.get("is_player"):
                combat_hp = c.get("hp_current")
                sheet_hp = player.get("hit_points", {}).get("current")
                if combat_hp is not None and sheet_hp is not None and combat_hp != sheet_hp:
                    base["recommendations"].append(
                        f"HP mismatch: combat has {combat_hp}, character sheet has {sheet_hp}"
                    )

    base["inventory"] = inventory
    base["validation"] = validation if (validation := validate_campaign(campaign_name)) else {}
    return base


def get_kingdom_state(campaign_name: str) -> Dict[str, Any]:
    return load_json(_state_dir(campaign_name) / "kingdom_state.json", DEFAULT_KINGDOM)


def update_kingdom_state(campaign_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    path = _state_dir(campaign_name) / "kingdom_state.json"
    state = load_json(path, DEFAULT_KINGDOM)
    state.update(updates)
    save_json(path, state)
    return state


def queue_kingdom_project(
    campaign_name: str,
    name: str,
    *,
    turns_remaining: int = 3,
    cost: Optional[Dict[str, int]] = None,
    reward: Optional[str] = None,
) -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    projects = kingdom.setdefault("projects", [])
    project = {
        "name": name,
        "status": "queued",
        "turns_remaining": turns_remaining,
        "cost": cost or {},
        "reward": reward or "",
        "created": datetime.now().isoformat(),
    }
    projects.append(project)
    update_kingdom_state(campaign_name, {"projects": projects})
    record_event(campaign_name, f"Kingdom project queued: {name}", tags=["kingdom", "project"])
    return project


def advance_kingdom_projects(campaign_name: str, turns: int = 1) -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    completed: List[str] = []
    for project in kingdom.get("projects", []):
        if project.get("status") != "queued":
            continue
        project["turns_remaining"] = max(0, project.get("turns_remaining", 0) - turns)
        if project["turns_remaining"] == 0:
            project["status"] = "completed"
            completed.append(project.get("name", "project"))
    update_kingdom_state(campaign_name, {"projects": kingdom.get("projects", [])})
    consequences: List[str] = []
    simulation: Dict[str, Any] = {}
    try:
        from kingdom_sim import advance_kingdom_turn_simulation

        simulation = advance_kingdom_turn_simulation(campaign_name)
    except Exception:
        pass
    if completed:
        record_event(
            campaign_name,
            f"Kingdom projects completed: {', '.join(completed)}",
            tags=["kingdom", "project"],
        )
        try:
            from kingdom_sim import apply_cascading_consequences
            for project_name in completed:
                consequences.extend(apply_cascading_consequences(campaign_name, project_name))
        except Exception:
            pass
    return {
        "completed": completed,
        "projects": kingdom.get("projects", []),
        "consequences": consequences,
        "simulation": simulation,
    }


def get_kingdom_summary(campaign_name: str) -> str:
    kingdom = get_kingdom_state(campaign_name)
    resources = kingdom.get("resources", {})
    active = [p for p in kingdom.get("projects", []) if p.get("status") == "queued"]
    lines = [
        f"**Domain:** {kingdom.get('domain_name', 'Unknown')}",
        f"**Resources:** {resources}",
        f"**Active projects:** {len(active)}",
    ]
    for project in active[:5]:
        lines.append(f"- {project.get('name')} ({project.get('turns_remaining')} turns left)")
    return "\n".join(lines)


def record_combat_outcome(
    campaign_name: str,
    description: str,
    *,
    enemies_defeated: Optional[List[str]] = None,
    importance: str = "normal",
) -> Dict[str, Any]:
    return record_combat_event(
        campaign_name,
        description,
        outcome="completed",
        importance=importance,
        metadata={"enemies_defeated": enemies_defeated or []},
    )


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

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("campaign")

    p_enhanced = sub.add_parser("enhanced-audit")
    p_enhanced.add_argument("campaign")

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
    p_search.add_argument("--type", dest="event_type")
    p_search.add_argument("--importance")
    p_search.add_argument("--limit", type=int, default=10)

    p_root = sub.add_parser("campaigns-root")
    p_runtime = sub.add_parser("runtime-context", help="Grok iOS / PC path diagnostics")

    p_kingdom = sub.add_parser("kingdom-summary")
    p_kingdom.add_argument("campaign")

    p_queue = sub.add_parser("queue-project")
    p_queue.add_argument("campaign")
    p_queue.add_argument("name")
    p_queue.add_argument("--turns", type=int, default=3)

    p_advance = sub.add_parser("advance-projects")
    p_advance.add_argument("campaign")
    p_advance.add_argument("--turns", type=int, default=1)

    p_sql = sub.add_parser("query-sql-events")
    p_sql.add_argument("campaign")
    p_sql.add_argument("--tag")
    p_sql.add_argument("--limit", type=int, default=20)

    p_dash = sub.add_parser("dashboard", help="Unified campaign snapshot")
    p_dash.add_argument("campaign")
    p_dash.add_argument("--audit", action="store_true")

    p_analytics = sub.add_parser("analytics", help="Campaign analytics reports")
    p_analytics.add_argument("campaign")
    p_analytics.add_argument(
        "--report",
        choices=["summary", "tags", "timeline", "npcs", "sync-sqlite", "archive"],
        default="summary",
    )
    p_analytics.add_argument("--limit", type=int, default=20)
    p_analytics.add_argument("--keep-events", type=int, default=500)

    p_archive = sub.add_parser("archive-events", help="Archive overflow events.json entries")
    p_archive.add_argument("campaign")
    p_archive.add_argument("--keep", type=int, default=500)

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
    elif args.cmd == "validate":
        result = validate_campaign(args.campaign)
    elif args.cmd == "enhanced-audit":
        result = enhanced_audit_campaign(args.campaign)
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
        result = search_events(
            args.campaign,
            tag=args.tag,
            event_type=args.event_type,
            importance=args.importance,
            limit=args.limit,
        )
    elif args.cmd == "campaigns-root":
        result = {"campaigns_root": str(get_campaigns_root())}
    elif args.cmd == "runtime-context":
        result = get_runtime_context()
    elif args.cmd == "kingdom-summary":
        result = {"summary": get_kingdom_summary(args.campaign), "state": get_kingdom_state(args.campaign)}
    elif args.cmd == "queue-project":
        result = queue_kingdom_project(args.campaign, args.name, turns_remaining=args.turns)
    elif args.cmd == "advance-projects":
        result = advance_kingdom_projects(args.campaign, turns=args.turns)
    elif args.cmd == "query-sql-events":
        try:
            from sqlite_layer import is_enabled, query_events_sql

            if not is_enabled(args.campaign):
                result = {"enabled": False, "events": [], "message": "SQLite not enabled for campaign"}
            else:
                result = {
                    "enabled": True,
                    "events": query_events_sql(args.campaign, tag=args.tag, limit=args.limit),
                }
        except Exception as exc:
            result = {"enabled": False, "error": str(exc)}
    elif args.cmd == "dashboard":
        from campaign_dashboard import build_campaign_dashboard
        result = build_campaign_dashboard(args.campaign, include_audit=args.audit)
    elif args.cmd == "analytics":
        from campaign_analytics import run_analytics
        result = run_analytics(
            args.campaign,
            report=args.report,
            limit=args.limit,
            keep_events=args.keep_events,
        )
    elif args.cmd == "archive-events":
        from campaign_analytics import archive_old_events
        result = archive_old_events(args.campaign, keep=args.keep)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()