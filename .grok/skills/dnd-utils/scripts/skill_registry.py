#!/usr/bin/env python3
"""
Canonical skill registry — triggers, CLI paths, and cross-skill delegation rules.

All skills and the persistent DM orchestrator should resolve routing through this module.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

SKILLS_ROOT = Path(__file__).resolve().parent.parent.parent

# skill_id -> metadata
SKILLS: Dict[str, Dict[str, Any]] = {
    "dnd-persistent-dm": {
        "role": "orchestrator",
        "script": "dnd-persistent-dm/scripts/persistent_dm.py",
        "triggers": ["play dnd", "dm mode", "continue campaign", "what's happening"],
        "calls": [
            "dnd-utils", "dnd-dice-engine", "dnd-combat-assistant", "dnd-character-manager",
            "dnd-session-scribe", "dnd-loot-generator", "dnd-content-forge", "dnd-npc-personality-weaver",
            "dnd-lore-archivist", "dnd-rules-reference", "dnd-rumor-event-generator",
            "dnd-visual-weaver", "dnd-voice-assistant", "dnd-downtime-manager", "dnd-quest-tracker",
        ],
    },
    "dnd-utils": {
        "role": "foundation",
        "script": "dnd-utils/scripts/dnd_state_utils.py",
        "triggers": ["init campaign", "update location", "kingdom mode", "audit", "record event"],
        "calls": ["event_system", "kingdom_sim", "sqlite_layer", "sync_bridge"],
        "called_by": ["all skills"],
    },
    "dnd-dice-engine": {
        "role": "mechanics",
        "script": "dnd-dice-engine/scripts/dice_roller.py",
        "triggers": ["roll", "attack roll", "saving throw", "advantage", "check"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm", "dnd-combat-assistant", "dnd-voice-assistant"],
    },
    "dnd-combat-assistant": {
        "role": "combat",
        "script": "dnd-combat-assistant/scripts/combat_tracker.py",
        "triggers": ["start combat", "damage", "heal", "next turn", "end combat", "apply condition"],
        "calls": ["dnd-utils", "sync_bridge"],
        "called_by": ["dnd-persistent-dm", "dnd-voice-assistant"],
        "after": ["dnd-loot-generator", "dnd-session-scribe"],
    },
    "dnd-character-manager": {
        "role": "character",
        "script": "dnd-character-manager/scripts/character_manager.py",
        "triggers": ["character sheet", "level up", "inventory", "attune", "death save"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm", "dnd-combat-assistant", "dnd-session-scribe", "dnd-voice-assistant"],
    },
    "dnd-session-scribe": {
        "role": "session",
        "script": "dnd-session-scribe/scripts/session_scribe.py",
        "triggers": ["end session", "award xp", "recap", "wrap up"],
        "calls": ["dnd-utils", "dnd-quest-tracker"],
        "called_by": ["dnd-persistent-dm", "dnd-voice-assistant"],
        "before": ["dnd-utils audit", "dnd-combat-assistant clear"],
    },
    "dnd-loot-generator": {
        "role": "loot",
        "script": "dnd-loot-generator/scripts/procedural_loot.py",
        "triggers": ["generate loot", "treasure hoard", "what did we find"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm", "dnd-combat-assistant"],
        "after": ["dnd-character-manager inventory add"],
    },
    "dnd-content-forge": {
        "role": "content",
        "scripts": {
            "monster": "dnd-content-forge/scripts/generate_monster.py",
            "encounter": "dnd-content-forge/scripts/encounter_builder.py",
            "quest": "dnd-content-forge/scripts/content_forge.py",
        },
        "triggers": ["generate encounter", "create monster", "side quest", "faction move"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm"],
        "after": ["dnd-combat-assistant", "dnd-quest-tracker", "dnd-npc-personality-weaver"],
    },
    "dnd-npc-personality-weaver": {
        "role": "npc",
        "script": "dnd-npc-personality-weaver/scripts/npc_manager.py",
        "triggers": ["create npc", "who is", "relationship with", "update npc"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm", "dnd-content-forge", "dnd-lore-archivist"],
    },
    "dnd-lore-archivist": {
        "role": "lore",
        "script": "dnd-lore-archivist/scripts/lore_archivist.py",
        "triggers": ["what happened at", "update lore", "what does know", "lore query"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm", "dnd-rumor-event-generator"],
    },
    "dnd-rules-reference": {
        "role": "rules",
        "script": "dnd-rules-reference/scripts/rules_cheatsheet.py",
        "triggers": ["how does work", "rules question", "advantage", "grapple", "concentration"],
        "calls": [],
        "called_by": ["dnd-persistent-dm", "dnd-combat-assistant", "dnd-voice-assistant"],
    },
    "dnd-rumor-event-generator": {
        "role": "world",
        "script": "dnd-rumor-event-generator/scripts/rumor_generator.py",
        "triggers": ["rumor", "world event", "faction move", "random event"],
        "calls": ["dnd-utils", "kingdom_sim"],
        "called_by": ["dnd-persistent-dm", "dnd-downtime-manager"],
        "after": ["dnd-lore-archivist append", "dnd-quest-tracker add-hook"],
    },
    "dnd-visual-weaver": {
        "role": "visual",
        "script": "dnd-visual-weaver/scripts/visual_prompt_library.py",
        "triggers": ["show me", "generate art", "what does look like", "portrait"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm"],
    },
    "dnd-voice-assistant": {
        "role": "voice",
        "script": "dnd-voice-assistant/scripts/voice_utils.py",
        "triggers": ["voice mode", "play by voice", "dm voice"],
        "calls": ["skill_registry", "dnd-persistent-dm"],
        "called_by": ["player voice input"],
        "routes_to": "all skills via intent map",
    },
    "dnd-downtime-manager": {
        "role": "downtime",
        "script": "dnd-downtime-manager/scripts/downtime_manager.py",
        "triggers": ["short rest", "long rest", "downtime activity"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm", "dnd-voice-assistant"],
        "after": ["dnd-rumor-event-generator rumors"],
    },
    "dnd-quest-tracker": {
        "role": "quests",
        "script": "dnd-quest-tracker/scripts/quest_tracker.py",
        "triggers": ["add quest", "active quests", "complete quest", "hook"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm", "dnd-session-scribe", "dnd-content-forge"],
    },
}

# Intent (from voice_utils / player text) -> delegation spec
INTENT_DELEGATIONS: Dict[str, Dict[str, Any]] = {
    "narrative": {
        "primary_skill": "dnd-persistent-dm",
        "command": "whats-happening",
        "confirm": False,
    },
    "dice_roll": {
        "primary_skill": "dnd-dice-engine",
        "script": "dnd-dice-engine/scripts/dice_roller.py",
        "command_template": '{notation}',
        "notes": "Grok picks notation from context; always pass --campaign",
        "confirm": False,
    },
    "combat_action": {
        "primary_skill": "dnd-dice-engine",
        "then": "dnd-combat-assistant",
        "flow": ["dice_roller attack roll", "combat_tracker damage on hit"],
        "confirm": False,
    },
    "damage": {
        "primary_skill": "dnd-combat-assistant",
        "script": "dnd-combat-assistant/scripts/combat_tracker.py",
        "command": "damage",
        "args_template": ["--target", "{target}", "--amount", "{amount}"],
        "confirm": False,
    },
    "healing": {
        "primary_skill": "dnd-combat-assistant",
        "script": "dnd-combat-assistant/scripts/combat_tracker.py",
        "command": "heal",
        "args_template": ["--target", "{target}", "--amount", "{amount}"],
        "confirm": False,
    },
    "next_turn": {
        "primary_skill": "dnd-combat-assistant",
        "script": "dnd-combat-assistant/scripts/combat_tracker.py",
        "command": "next-turn",
        "confirm": False,
    },
    "combat_status": {
        "primary_skill": "dnd-combat-assistant",
        "script": "dnd-combat-assistant/scripts/combat_tracker.py",
        "command": "summary",
        "confirm": False,
    },
    "apply_condition": {
        "primary_skill": "dnd-combat-assistant",
        "script": "dnd-combat-assistant/scripts/combat_tracker.py",
        "command": "apply-condition",
        "confirm": False,
    },
    "end_session": {
        "primary_skill": "dnd-session-scribe",
        "script": "dnd-session-scribe/scripts/session_scribe.py",
        "command": "end-session",
        "args_template": ["{summary}", "--auto"],
        "then": ["dnd-utils audit", "dnd-quest-tracker list"],
        "confirm": True,
    },
    "level_up": {
        "primary_skill": "dnd-character-manager",
        "script": "dnd-character-manager/scripts/character_manager.py",
        "command": "suggest-level-up",
        "then": "level-up after player confirms",
        "confirm": True,
    },
    "loot": {
        "primary_skill": "dnd-loot-generator",
        "script": "dnd-loot-generator/scripts/procedural_loot.py",
        "command": "generate",
        "then": "dnd-character-manager inventory add",
        "confirm": False,
    },
    "rumor": {
        "primary_skill": "dnd-rumor-event-generator",
        "script": "dnd-rumor-event-generator/scripts/rumor_generator.py",
        "command": "rumors",
        "args_template": ["--count", "3"],
        "confirm": False,
    },
    "rest": {
        "primary_skill": "dnd-downtime-manager",
        "script": "dnd-downtime-manager/scripts/downtime_manager.py",
        "command": "long-rest",
        "alt_command": "short-rest",
        "confirm": False,
    },
    "quest_list": {
        "primary_skill": "dnd-quest-tracker",
        "script": "dnd-quest-tracker/scripts/quest_tracker.py",
        "command": "list",
        "confirm": False,
    },
    "add_quest": {
        "primary_skill": "dnd-quest-tracker",
        "script": "dnd-quest-tracker/scripts/quest_tracker.py",
        "command": "add",
        "confirm": False,
    },
    "rules": {
        "primary_skill": "dnd-rules-reference",
        "script": "dnd-rules-reference/scripts/rules_cheatsheet.py",
        "command": "lookup",
        "confirm": False,
    },
    "lore_query": {
        "primary_skill": "dnd-lore-archivist",
        "script": "dnd-lore-archivist/scripts/lore_archivist.py",
        "command": "query",
        "confirm": False,
    },
    "encounter": {
        "primary_skill": "dnd-content-forge",
        "script": "dnd-content-forge/scripts/encounter_builder.py",
        "command": "build",
        "then": "dnd-combat-assistant init",
        "confirm": False,
    },
    "visual": {
        "primary_skill": "dnd-visual-weaver",
        "script": "dnd-visual-weaver/scripts/visual_prompt_library.py",
        "command": "weave-prompt",
        "confirm": False,
    },
}

# Named multi-step playbooks for persistent-dm
PLAYBOOKS: Dict[str, List[Dict[str, Any]]] = {
    "new-campaign": [
        {"skill": "dnd-persistent-dm", "command": "init", "args": ["--enable-sqlite"]},
        {"skill": "dnd-persistent-dm", "command": "resume"},
        {"skill": "dnd-rumor-event-generator", "command": "rumors", "args": ["--count", "2"]},
    ],
    "start-combat": [
        {"skill": "dnd-combat-assistant", "command": "init", "args": ["--encounter", "Encounter"]},
        {"skill": "dnd-dice-engine", "command": "initiative", "notes": "Roll initiative per combatant, then add"},
        {"skill": "dnd-combat-assistant", "command": "summary"},
    ],
    "end-combat": [
        {"skill": "dnd-combat-assistant", "command": "end-combat"},
        {"skill": "dnd-loot-generator", "command": "generate"},
        {"skill": "dnd-utils", "command": "clear-combat"},
        {"skill": "dnd-character-manager", "command": "sync", "notes": "HP synced via sync_bridge during combat"},
    ],
    "session-end": [
        {"skill": "dnd-session-scribe", "command": "auto-recap", "args": ["--save"]},
        {"skill": "dnd-session-scribe", "command": "end-session", "args": ["auto", "--auto"]},
        {"skill": "dnd-quest-tracker", "command": "list"},
        {"skill": "dnd-utils", "command": "enhanced-audit"},
    ],
    "kingdom-turn": [
        {"skill": "dnd-utils", "command": "advance-projects"},
        {"skill": "dnd-rumor-event-generator", "command": "rumors", "args": ["--count", "3"]},
        {"skill": "dnd-rumor-event-generator", "command": "world-event"},
        {"skill": "dnd-utils", "command": "kingdom-summary"},
    ],
    "downtime": [
        {"skill": "dnd-downtime-manager", "command": "long-rest"},
        {"skill": "dnd-rumor-event-generator", "command": "rumors", "args": ["--count", "2"]},
        {"skill": "dnd-quest-tracker", "command": "list"},
    ],
}


def script_path(relative: str) -> Path:
    return SKILLS_ROOT / relative


def get_skill(skill_id: str) -> Dict[str, Any]:
    if skill_id not in SKILLS:
        raise KeyError(f"Unknown skill: {skill_id}")
    return SKILLS[skill_id]


def resolve_intent(intent: str, *, campaign: str = "Campaign", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return full delegation plan for an intent."""
    ctx = context or {}
    spec = INTENT_DELEGATIONS.get(intent, INTENT_DELEGATIONS["narrative"]).copy()
    spec["intent"] = intent
    spec["campaign"] = campaign

    if "script" in spec:
        spec["script_path"] = str(script_path(spec["script"]))
        cmd_parts = ["python", spec["script_path"], spec.get("command", "")]
        if spec.get("command") not in ("", "whats-happening"):
            cmd_parts.insert(2, campaign)
        spec["cli_example"] = " ".join(p for p in cmd_parts if p)

    if intent == "damage" and ctx.get("damage"):
        target, amount = ctx["damage"]
        spec["resolved_args"] = ["--target", target, "--amount", str(amount)]
    elif intent == "healing" and ctx.get("healing"):
        target, amount = ctx["healing"]
        spec["resolved_args"] = ["--target", target, "--amount", str(amount)]

    if spec.get("then"):
        spec["follow_up"] = spec["then"] if isinstance(spec["then"], list) else [spec["then"]]

    return spec


def get_playbook(name: str) -> List[Dict[str, Any]]:
    if name not in PLAYBOOKS:
        raise KeyError(f"Unknown playbook: {name}. Available: {list(PLAYBOOKS.keys())}")
    return PLAYBOOKS[name]


def coordination_summary(skill_id: str) -> Dict[str, Any]:
    """Summary for SKILL.md / agent context."""
    skill = get_skill(skill_id)
    return {
        "skill": skill_id,
        "role": skill.get("role"),
        "called_by": skill.get("called_by", []),
        "calls": skill.get("calls", []),
        "after": skill.get("after", []),
        "before": skill.get("before", []),
        "triggers": skill.get("triggers", []),
    }


def list_all_skills() -> List[str]:
    return sorted(SKILLS.keys())


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="D&D skill registry and delegation resolver")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    p_resolve = sub.add_parser("resolve")
    p_resolve.add_argument("intent")
    p_resolve.add_argument("--campaign", default="My Campaign")

    p_playbook = sub.add_parser("playbook")
    p_playbook.add_argument("name")

    p_coord = sub.add_parser("coordination")
    p_coord.add_argument("skill_id")

    p_graph = sub.add_parser("graph")

    args = parser.parse_args()

    if args.cmd == "list":
        result = {"skills": list_all_skills(), "count": len(SKILLS)}
    elif args.cmd == "resolve":
        result = resolve_intent(args.intent, campaign=args.campaign)
    elif args.cmd == "playbook":
        result = {"name": args.playbook, "steps": get_playbook(args.playbook)}
    elif args.cmd == "coordination":
        result = coordination_summary(args.coordination)
    elif args.cmd == "graph":
        result = {
            "skills": SKILLS,
            "intents": list(INTENT_DELEGATIONS.keys()),
            "playbooks": list(PLAYBOOKS.keys()),
        }
    else:
        result = {"error": "unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()