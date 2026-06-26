#!/usr/bin/env python3
"""Smoke test all D&D skill CLIs against a temp campaign."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".grok" / "skills"


def run(cmd: list[str], env: dict) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=REPO)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nstdout: {result.stdout}\nstderr: {result.stderr}")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        env = {**dict(**__import__("os").environ), "DND_CAMPAIGNS_ROOT": tmp}
        campaign = "Smoke Campaign"
        py = sys.executable

        # Orchestrator + utils
        run([py, str(SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "init", campaign, "--enable-sqlite"], env)
        run([py, str(SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "resume", campaign], env)
        run([py, str(SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "route", campaign, "roll stealth"], env)
        run([py, str(SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "registry"], env)
        run([py, str(SKILLS / "dnd-utils/scripts/skill_registry.py"), "resolve", "loot", "--campaign", campaign], env)
        run([py, str(SKILLS / "dnd-utils/scripts/skill_orchestrator.py"), "plan", campaign, "next turn"], env)
        run([py, str(SKILLS / "dnd-utils/scripts/dnd_state_utils.py"), "validate", campaign], env)
        run([py, str(SKILLS / "dnd-utils/scripts/dnd_state_utils.py"), "dashboard", campaign], env)
        run([py, str(SKILLS / "dnd-utils/scripts/dnd_state_utils.py"), "analytics", campaign, "--report", "tags"], env)
        run([py, str(SKILLS / "dnd-utils/scripts/narration_cli.py"), "mobile-status", campaign], env)
        run([py, str(SKILLS / "dnd-utils/scripts/narration_cli.py"), "dashboard", campaign], env)

        # Core play backends
        run([py, str(SKILLS / "dnd-dice-engine/scripts/dice_roller.py"), "1d20", "--campaign", campaign], env)
        run([py, str(SKILLS / "dnd-dice-engine/scripts/dice_roller.py"), "initiative", "2", "--campaign", campaign], env)
        run([py, str(SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"), "init", campaign], env)
        run([py, str(SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"), "summary", campaign], env)
        run([py, str(SKILLS / "dnd-character-manager/scripts/character_manager.py"), "summary", campaign], env)
        run([py, str(SKILLS / "dnd-character-manager/scripts/character_manager.py"), "suggest-level-up", campaign], env)
        run([py, str(SKILLS / "dnd-character-manager/scripts/character_manager.py"), "sync", campaign], env)

        # Content & world
        run([py, str(SKILLS / "dnd-content-forge/scripts/generate_monster.py"), campaign, "--theme", "Test"], env)
        run([py, str(SKILLS / "dnd-content-forge/scripts/encounter_builder.py"), "build", campaign, "--theme", "ambush"], env)
        run([py, str(SKILLS / "dnd-content-forge/scripts/content_forge.py"), "quest", campaign], env)
        run([py, str(SKILLS / "dnd-loot-generator/scripts/procedural_loot.py"), "generate", campaign], env)
        run([py, str(SKILLS / "dnd-npc-personality-weaver/scripts/npc_manager.py"), "create", campaign, "--name", "Test NPC"], env)
        run([py, str(SKILLS / "dnd-lore-archivist/scripts/lore_archivist.py"), "append", campaign, "Smoke lore"], env)
        run([py, str(SKILLS / "dnd-lore-archivist/scripts/lore_archivist.py"), "list-npcs", campaign], env)
        run([py, str(SKILLS / "dnd-rumor-event-generator/scripts/rumor_generator.py"), "rumors", campaign], env)
        run([py, str(SKILLS / "dnd-rules-reference/scripts/rules_cheatsheet.py"), "lookup", "advantage"], env)
        run([py, str(SKILLS / "dnd-visual-weaver/scripts/visual_prompt_library.py"), "weave-prompt", campaign, "tavern scene"], env)

        # New skills
        run([py, str(SKILLS / "dnd-downtime-manager/scripts/downtime_manager.py"), "long-rest", campaign], env)
        run([py, str(SKILLS / "dnd-quest-tracker/scripts/quest_tracker.py"), "add", campaign, "Smoke Quest"], env)
        run([py, str(SKILLS / "dnd-quest-tracker/scripts/quest_tracker.py"), "list", campaign], env)

        # Voice + session
        run([py, str(SKILLS / "dnd-voice-assistant/scripts/voice_utils.py"), "route", campaign, "next turn"], env)
        run([py, str(SKILLS / "dnd-session-scribe/scripts/session_scribe.py"), "auto-recap", campaign], env)
        run([py, str(SKILLS / "dnd-session-scribe/scripts/session_scribe.py"), "append-log", campaign, "Smoke note"], env)
        run([py, str(SKILLS / "dnd-session-scribe/scripts/session_scribe.py"), "end-session", campaign, "Smoke complete", "--xp", "50"], env)

        skill_dirs = [d for d in SKILLS.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
        scripts_ok = all(any((d / "scripts").glob("*.py")) for d in skill_dirs)

        print(json.dumps({
            "ok": True,
            "campaign_root": tmp,
            "skills_tested": len(skill_dirs),
            "all_skills_have_scripts": scripts_ok,
        }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())