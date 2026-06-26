#!/usr/bin/env python3
"""Deep validation: every D&D skill has full Python backends (min CLI commands + smoke)."""

from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".grok" / "skills"

# Every player-facing skill must expose at least this many CLI subcommands.
MIN_CLI_COMMANDS = 5

# Multiple smoke invocations per skill (argv after script name)
SMOKE_COMMANDS: dict[str, list[list[str]]] = {
    "dnd-character-manager": [["summary", "AuditCampaign"], ["sync", "AuditCampaign"]],
    "dnd-combat-assistant": [["summary", "AuditCampaign"]],
    "dnd-content-forge": [["quest", "AuditCampaign"]],
    "dnd-dice-engine": [
        ["initiative", "0"],
        ["roll", "1d20"],
        ["roll", "1d8+1d6+3"],
        ["parse", "4d6kh3"],
        ["check", "3", "--dc", "15"],
        ["crit", "2d6+3"],
    ],
    "dnd-downtime-manager": [
        ["status", "AuditCampaign"],
        ["spend-hit-dice", "AuditCampaign", "1"],
        ["list-activities", "AuditCampaign"],
    ],
    "dnd-loot-generator": [
        ["ledger", "AuditCampaign"],
        ["generate", "AuditCampaign"],
        ["summary", "AuditCampaign"],
        ["tables"],
    ],
    "dnd-lore-archivist": [
        ["summary", "AuditCampaign"],
        ["search", "AuditCampaign", "vault"],
        ["rebuild-index", "AuditCampaign"],
    ],
    "dnd-npc-personality-weaver": [
        ["list", "AuditCampaign"],
        ["generate-personality", "Test NPC", "--role", "merchant"],
        ["relationship-tier", "15"],
    ],
    "dnd-persistent-dm": [["health", "AuditCampaign"], ["registry"]],
    "dnd-quest-tracker": [["list", "AuditCampaign"]],
    "dnd-rules-reference": [
        ["list"],
        ["search", "advantage"],
        ["condition", "prone"],
        ["spell", "fireball"],
        ["feat", "lucky"],
    ],
    "dnd-rumor-event-generator": [
        ["rumors", "AuditCampaign", "--no-persist"],
        ["list", "AuditCampaign"],
        ["faction-move", "AuditCampaign"],
        ["faction-sim", "AuditCampaign", "--seed", "1"],
        ["ledger", "AuditCampaign"],
    ],
    "dnd-session-scribe": [["auto-recap", "AuditCampaign"]],
    "dnd-utils": [
        ["campaigns-root"],
        ["validate", "AuditCampaign"],
        ["dashboard", "AuditCampaign"],
        ["analytics", "AuditCampaign", "--report", "tags"],
    ],
    "dnd-visual-weaver": [
        ["weave-prompt", "AuditCampaign", "test scene"],
        ["weave-map", "AuditCampaign"],
        ["status", "AuditCampaign"],
    ],
    "dnd-voice-assistant": [
        ["parse", "next turn"],
        ["plan", "AuditCampaign", "Goblin takes 5 damage"],
        ["detect-voice", "start voice dnd"],
    ],
    "dnd-randomizer": [
        ["list-tables"],
        ["roll-table", "weather"],
        ["random-item", "--level", "3"],
        ["random-character", "--level", "1"],
        ["mobile-summary", "item", "--seed", "1"],
        ["travel-day", "AuditCampaign", "--seed", "2"],
        ["random-everything", "--level", "2", "--seed", "42"],
    ],
}

UTILS_CLI_SCRIPTS = [
    "dnd-utils/scripts/dnd_state_utils.py",
    "dnd-utils/scripts/narration_cli.py",
    "dnd-utils/scripts/skill_registry.py",
    "dnd-utils/scripts/skill_orchestrator.py",
]

# Shared library modules imported by other skills — not required to expose CLI.
UTILS_LIBRARY_ONLY = {
    "bootstrap.py",
    "paths.py",
    "errors.py",
    "event_system.py",
    "kingdom_sim.py",
    "narration_helpers.py",
    "sqlite_layer.py",
    "sync_bridge.py",
    "xp_tables.py",
    "campaign_dashboard.py",
    "campaign_analytics.py",
    "lore_index.py",
    "class_progression.py",
    "faction_engine.py",
}

RANDOMIZER_LIBRARY_ONLY = {"randomizer_data.py", "randomizer_engine.py"}

RULES_LIBRARY_ONLY = {"rules_data.py", "srd_data.py"}

SCRIPT_FOR_SKILL: dict[str, str] = {
    "dnd-content-forge": "dnd-content-forge/scripts/content_forge.py",
    "dnd-utils": "dnd-utils/scripts/dnd_state_utils.py",
}


def _skill_scripts(skill_dir: Path) -> list[Path]:
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return []
    return sorted(scripts_dir.glob("*.py"))


def _cli_commands(script: Path) -> list[str]:
    text = script.read_text(encoding="utf-8")
    if "if __name__" not in text:
        return []
    return re.findall(r'add_parser\(\s*["\']([^"\']+)["\']', text)


def _primary_script(skill: str, scripts: list[Path]) -> Path | None:
    if skill in SCRIPT_FOR_SKILL:
        path = SKILLS / SCRIPT_FOR_SKILL[skill]
        return path if path.exists() else None
    return scripts[0] if scripts else None


def validate() -> dict:
    issues: list[str] = []
    skills_report: list[dict] = []

    with tempfile.TemporaryDirectory() as tmp:
        env = {**dict(__import__("os").environ), "DND_CAMPAIGNS_ROOT": tmp}
        py = sys.executable

        init_script = SKILLS / "dnd-utils/scripts/dnd_state_utils.py"
        subprocess.run(
            [py, str(init_script), "init", "AuditCampaign", "--force", "--pc-name", "Audit Hero"],
            capture_output=True,
            text=True,
            env=env,
            cwd=REPO,
            check=False,
        )

        for skill_dir in sorted(SKILLS.iterdir()):
            if not skill_dir.is_dir() or not skill_dir.name.startswith("dnd-"):
                continue
            skill = skill_dir.name
            scripts = _skill_scripts(skill_dir)
            skill_issues: list[str] = []

            if not scripts:
                skill_issues.append("No scripts/*.py found")

            cli_scripts: list[str] = []
            all_commands: list[str] = []
            for script in scripts:
                try:
                    py_compile.compile(str(script), doraise=True)
                except py_compile.PyCompileError as exc:
                    skill_issues.append(f"Compile error {script.name}: {exc}")

                text = script.read_text(encoding="utf-8")
                if "if __name__" not in text:
                    library_only = RULES_LIBRARY_ONLY if skill == "dnd-rules-reference" else set()
                    if skill == "dnd-utils":
                        library_only = UTILS_LIBRARY_ONLY
                    if skill == "dnd-randomizer":
                        library_only = RANDOMIZER_LIBRARY_ONLY
                    if script.name not in library_only:
                        skill_issues.append(f"No CLI entry point: {script.name}")
                else:
                    cli_scripts.append(script.name)
                    all_commands.extend(_cli_commands(script))

            unique_commands = sorted(set(all_commands))
            if len(unique_commands) < MIN_CLI_COMMANDS:
                skill_issues.append(
                    f"Only {len(unique_commands)} CLI commands (minimum {MIN_CLI_COMMANDS}): {unique_commands}"
                )

            primary = _primary_script(skill, scripts)
            for cmd_argv in SMOKE_COMMANDS.get(skill, []):
                script = primary
                if skill == "dnd-rules-reference":
                    script = skill_dir / "scripts" / "rules_cheatsheet.py"
                elif skill == "dnd-npc-personality-weaver" and cmd_argv[0] in (
                    "generate-personality", "relationship-tier"
                ):
                    script = skill_dir / "scripts" / "npc_manager.py"
                elif skill == "dnd-voice-assistant":
                    script = skill_dir / "scripts" / "voice_utils.py"
                elif skill == "dnd-dice-engine":
                    script = skill_dir / "scripts" / "dice_roller.py"
                elif skill == "dnd-loot-generator" and cmd_argv[0] == "tables":
                    script = skill_dir / "scripts" / "procedural_loot.py"
                elif skill == "dnd-combat-assistant" and cmd_argv[0] in (
                    "init-grid", "place", "move", "distance", "aoe", "summary"
                ):
                    script = skill_dir / "scripts" / "grid_combat.py"
                elif skill == "dnd-character-manager" and cmd_argv[0] in (
                    "foundry", "roll20", "combat-foundry", "spell-slots", "validate-multiclass", "build-plan"
                ):
                    if cmd_argv[0] in ("foundry", "roll20", "combat-foundry"):
                        script = skill_dir / "scripts" / "vtt_export.py"
                    else:
                        script = skill_dir / "scripts" / "character_manager.py"
                elif skill == "dnd-randomizer" and cmd_argv[0] in (
                    "apply-npc", "apply-quest", "add-random-loot", "travel-day", "mobile-summary"
                ):
                    script = skill_dir / "scripts" / "randomizer.py"
                elif skill == "dnd-lore-archivist" and cmd_argv[0] in ("search", "rebuild-index"):
                    script = skill_dir / "scripts" / "lore_archivist.py"
                elif skill == "dnd-rules-reference" and cmd_argv[0] in ("spell", "feat", "search-spells", "search-feats"):
                    script = skill_dir / "scripts" / "rules_cheatsheet.py"
                elif skill == "dnd-persistent-dm" and cmd_argv[0] == "registry":
                    script = skill_dir / "scripts" / "persistent_dm.py"

                if not script or not script.exists():
                    skill_issues.append(f"Smoke target missing for {' '.join(cmd_argv)}")
                    continue
                proc = subprocess.run(
                    [py, str(script), *cmd_argv],
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=REPO,
                )
                if proc.returncode != 0:
                    skill_issues.append(
                        f"Smoke failed {' '.join(cmd_argv)}: {proc.stderr.strip() or proc.stdout.strip()}"
                    )

            if skill == "dnd-utils":
                for rel in UTILS_CLI_SCRIPTS[1:]:
                    script = SKILLS / rel
                    if "if __name__" not in script.read_text(encoding="utf-8"):
                        skill_issues.append(f"Missing CLI entry: {rel}")

            issues.extend(f"{skill}: {msg}" for msg in skill_issues)
            skills_report.append(
                {
                    "skill": skill,
                    "scripts": [s.name for s in scripts],
                    "cli_scripts": cli_scripts,
                    "command_count": len(unique_commands),
                    "commands": unique_commands,
                    "valid": len(skill_issues) == 0,
                    "issues": skill_issues,
                }
            )

    return {
        "skills_checked": len(skills_report),
        "min_cli_commands": MIN_CLI_COMMANDS,
        "valid": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
        "skills": skills_report,
    }


def main() -> int:
    report = validate()
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())