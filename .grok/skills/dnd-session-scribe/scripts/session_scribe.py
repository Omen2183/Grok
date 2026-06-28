#!/usr/bin/env python3
"""Session recap, XP tracking, and log management for D&D campaigns."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from dnd_state_utils import (  # noqa: E402
    audit_campaign,
    clear_combat_state,
    get_player_character,
    get_world_state,
    load_json,
    save_json,
)
from event_system import record_event, search_events  # noqa: E402
from paths import get_campaign_path  # noqa: E402
from xp_tables import check_level_up, level_from_xp, suggest_domain_xp, xp_to_next_level  # noqa: E402


def _append_session_log(campaign_name: str, text: str) -> None:
    log_path = get_campaign_path(campaign_name) / "logs" / "session_log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(text)


def award_xp(campaign_name: str, amount: int, *, reason: str = "") -> Dict[str, Any]:
    path = get_campaign_path(campaign_name) / "state" / "player_character.json"
    char = load_json(path, {})
    char["xp"] = char.get("xp", 0) + amount
    save_json(path, char)

    level_info = check_level_up(char)
    derived_level = level_from_xp(char["xp"])
    xp_remaining = xp_to_next_level(char["xp"])

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    note = f"\n\n### XP +{amount} ({stamp})\n"
    if reason:
        note += f"- **Reason:** {reason}\n"
    note += f"- **Total XP:** {char['xp']}\n"
    note += f"- **Level (by XP):** {derived_level}\n"
    if xp_remaining is not None:
        note += f"- **XP to next level:** {xp_remaining}\n"
    if level_info["level_up_available"]:
        note += (
            f"- **Level-up available:** {level_info['pending_level_ups']} "
            f"(stored level {level_info['stored_level']} → {derived_level})\n"
        )
    _append_session_log(campaign_name, note)

    record_event(
        campaign_name,
        f"XP awarded: {amount}" + (f" — {reason}" if reason else ""),
        importance="normal",
        tags=["xp"],
        metadata={"amount": amount, "level_up_available": level_info["level_up_available"]},
    )
    return {
        "xp_awarded": amount,
        "total_xp": char["xp"],
        "reason": reason,
        "derived_level": derived_level,
        "xp_to_next_level": xp_remaining,
        "level_up": level_info,
    }


def save_recap(
    campaign_name: str,
    summary: str,
    *,
    hooks: Optional[List[str]] = None,
    xp_gained: int = 0,
) -> Dict[str, Any]:
    recaps_dir = get_campaign_path(campaign_name) / "recaps"
    recaps_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    recap_path = recaps_dir / f"session_{stamp}.md"

    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)

    lines = [
        f"# Session Recap — {campaign_name}",
        f"*{datetime.now().strftime('%B %d, %Y')}*",
        "",
        "## What Happened",
        summary,
        "",
        "## Key State",
        f"- **Location:** {world.get('current_location', 'Unknown')}",
        f"- **Time:** {world.get('in_game_time', 'Unknown')}",
        f"- **Character:** {player.get('name', 'Adventurer')} (Level {player.get('level', 1)})",
        f"- **XP this session:** {xp_gained}",
    ]

    quest_hooks: List[str] = []
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-quest-tracker" / "scripts"))
        from quest_tracker import list_active
        active = list_active(campaign_name)
        for q in active.get("active_quests", [])[:3]:
            quest_hooks.append(f"Quest: {q.get('title', 'Unknown')}")
        for h in active.get("open_hooks", [])[:3]:
            text = h.get("text", h) if isinstance(h, dict) else str(h)
            quest_hooks.append(f"Hook: {text}")
    except Exception:
        pass

    all_hooks = list(hooks or []) + quest_hooks
    if all_hooks:
        lines.extend(["", "## Hooks for Next Session"])
        for hook in all_hooks:
            lines.append(f"- {hook}")

    content = "\n".join(lines) + "\n"
    recap_path.write_text(content, encoding="utf-8")
    _append_session_log(campaign_name, f"\n\n## Session Recap ({stamp})\n{summary}\n")

    record_event(campaign_name, "Session recap saved", importance="major", tags=["recap"])
    return {"recap_path": str(recap_path), "hooks": hooks or []}


def generate_auto_recap(
    campaign_name: str,
    *,
    event_limit: int = 25,
    include_hooks: bool = True,
) -> Dict[str, Any]:
    """Build a session recap draft from recent campaign events."""
    events = search_events(campaign_name, limit=event_limit)
    if not events:
        return {
            "campaign": campaign_name,
            "summary": "No events logged yet this session.",
            "event_count": 0,
            "hooks": [],
        }

    world = get_world_state(campaign_name)
    player = get_player_character(campaign_name)
    bullets: List[str] = []
    hooks: List[str] = []
    xp_total = 0

    for event in events:
        desc = event.get("description", "")
        tags = event.get("tags", [])
        importance = event.get("importance", "normal")
        if importance in ("major", "normal") and desc:
            bullets.append(f"- {desc}")
        if "hook" in tags or importance == "major":
            hooks.append(desc)
        if "xp" in tags:
            xp_total += int(event.get("metadata", {}).get("amount", 0))

    summary_lines = [
        f"The party ({player.get('name', 'Adventurer')}, level {player.get('level', 1)}) "
        f"operated near {world.get('current_location', 'unknown')}.",
        "",
        "**Key beats:**",
        *bullets[-12:],
    ]
    if xp_total:
        summary_lines.append(f"\n**XP this period:** {xp_total}")

    summary = "\n".join(summary_lines)
    hook_list = hooks[-3:] if include_hooks else []

    return {
        "campaign": campaign_name,
        "summary": summary,
        "hooks": hook_list,
        "event_count": len(events),
        "location": world.get("current_location"),
        "suggested_xp": xp_total or None,
    }


def extract_quest_hooks(text: str) -> List[str]:
    """Pull quest-hook candidates from recap or log text."""
    import re

    hooks: List[str] = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("-*•").strip()
        if not stripped or len(stripped) < 12:
            continue
        lower = stripped.lower()
        if any(k in lower for k in ("quest", "hook", "leads to", "clue", "mystery", "investigate", "rumor")):
            hooks.append(stripped[:200])
    if not hooks:
        for match in re.finditer(r"(?:must|need to|should)\s+([^.!?]{10,80})", text, re.I):
            hooks.append(match.group(0).strip()[:200])
    return hooks[:5]


def sync_quest_hooks(
    campaign_name: str,
    *,
    dry_run: bool = False,
    source: str = "auto",
) -> Dict[str, Any]:
    """Import quest hooks from latest recap or auto-recap into quest tracker."""
    if str(Path(__file__).parent.parent.parent / "dnd-quest-tracker" / "scripts") not in sys.path:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-quest-tracker" / "scripts"))
    from quest_tracker import add_hook, add_quest  # noqa: E402

    if source == "auto":
        auto = generate_auto_recap(campaign_name)
        text = auto.get("summary", "")
        candidates = extract_quest_hooks(text) + list(auto.get("hooks", []))
    else:
        candidates = extract_quest_hooks(source)

    seen = set()
    added: List[Dict[str, Any]] = []
    for hook in candidates:
        key = hook.lower()[:80]
        if key in seen:
            continue
        seen.add(key)
        if dry_run:
            added.append({"hook": hook, "dry_run": True})
            continue
        if hook.lower().startswith("quest:"):
            title = hook.split(":", 1)[-1].strip()
            added.append({"type": "quest", "result": add_quest(campaign_name, title, summary=hook)})
        else:
            added.append({"type": "hook", "result": add_hook(campaign_name, hook)})
    return {"campaign": campaign_name, "candidates": len(candidates), "added": added, "dry_run": dry_run}


def award_domain_xp(campaign_name: str, milestone: str, *, apply: bool = True) -> Dict[str, Any]:
    """Suggest and optionally award kingdom milestone XP."""
    suggestion = suggest_domain_xp(milestone)
    amount = suggestion.get("suggested_xp")
    if amount is None:
        return {"awarded": False, **suggestion}
    if not apply:
        return {"awarded": False, "would_award": amount, **suggestion}
    return {"awarded": True, "xp": award_xp(campaign_name, amount, reason=f"Domain: {milestone}"), **suggestion}


def end_session(
    campaign_name: str,
    summary: str,
    *,
    xp: int = 0,
    xp_reason: str = "Session completion",
    hooks: Optional[List[str]] = None,
    run_audit: bool = True,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {"campaign": campaign_name}

    if xp > 0:
        results["xp"] = award_xp(campaign_name, xp, reason=xp_reason)

    results["recap"] = save_recap(campaign_name, summary, hooks=hooks, xp_gained=xp)
    results["combat"] = clear_combat_state(campaign_name)

    if run_audit:
        results["audit"] = audit_campaign(campaign_name)

    record_event(campaign_name, "Session ended", importance="major", tags=["session-end"])
    results["status"] = "session_saved"
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="D&D session scribe")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_xp = sub.add_parser("award-xp")
    p_xp.add_argument("campaign")
    p_xp.add_argument("amount", type=int)
    p_xp.add_argument("--reason", default="")

    p_recap = sub.add_parser("recap")
    p_recap.add_argument("campaign")
    p_recap.add_argument("summary")
    p_recap.add_argument("--hook", action="append", default=[])

    p_auto = sub.add_parser("auto-recap")
    p_auto.add_argument("campaign")
    p_auto.add_argument("--events", type=int, default=25)
    p_auto.add_argument("--save", action="store_true")

    p_end = sub.add_parser("end-session")
    p_end.add_argument("campaign")
    p_end.add_argument("summary")
    p_end.add_argument("--xp", type=int, default=0)
    p_end.add_argument("--reason", default="Session completion")
    p_end.add_argument("--hook", action="append", default=[])
    p_end.add_argument("--skip-audit", action="store_true")
    p_end.add_argument("--auto", action="store_true", help="Generate summary from events if summary empty")
    p_end.add_argument("--sync-quests", action="store_true", help="Import hooks from recap into quest tracker")

    p_sync = sub.add_parser("sync-quests")
    p_sync.add_argument("campaign")
    p_sync.add_argument("--dry-run", action="store_true")

    p_domain = sub.add_parser("award-domain-xp")
    p_domain.add_argument("campaign")
    p_domain.add_argument("milestone")
    p_domain.add_argument("--dry-run", action="store_true")

    p_log = sub.add_parser("append-log")
    p_log.add_argument("campaign")
    p_log.add_argument("text")

    args = parser.parse_args()

    if args.cmd == "award-xp":
        result = award_xp(args.campaign, args.amount, reason=args.reason)
    elif args.cmd == "auto-recap":
        result = generate_auto_recap(args.campaign, event_limit=args.events)
        if args.save:
            result["saved"] = save_recap(args.campaign, result["summary"], hooks=result.get("hooks"))
    elif args.cmd == "recap":
        result = save_recap(args.campaign, args.summary, hooks=args.hook)
    elif args.cmd == "sync-quests":
        result = sync_quest_hooks(args.campaign, dry_run=args.dry_run)
    elif args.cmd == "award-domain-xp":
        result = award_domain_xp(args.campaign, args.milestone, apply=not args.dry_run)
    elif args.cmd == "append-log":
        _append_session_log(args.campaign, f"\n{args.text}\n")
        result = {"status": "appended", "campaign": args.campaign}
    elif args.cmd == "end-session":
        summary = args.summary
        hooks = args.hook
        if args.auto or summary.strip().lower() in ("", "auto", "generate"):
            auto = generate_auto_recap(args.campaign)
            summary = auto["summary"]
            hooks = hooks or auto.get("hooks", [])
        result = end_session(
            args.campaign,
            summary,
            xp=args.xp,
            xp_reason=args.reason,
            hooks=hooks,
            run_audit=not args.skip_audit,
        )
        if args.sync_quests:
            result["quest_sync"] = sync_quest_hooks(args.campaign)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()