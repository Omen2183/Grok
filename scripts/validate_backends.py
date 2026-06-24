#!/usr/bin/env python3
"""Deep validation: every D&D skill has real Python backends with CLI entry points."""

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

# Minimum smoke command per skill (script relative path, argv after script name)
SMOKE_COMMANDS: dict[str, list[list[str]]] = {
    "dnd-character-manager": [["summary", "AuditCampaign"]],
    "dnd-combat-assistant": [["summary", "AuditCampaign"]],
    "dnd-content-forge": [["quest", "AuditCampaign"]],
    "dnd-dice-engine": [["initiative", "0"]],
    "dnd-downtime-manager": [["status", "AuditCampaign"]],
    "dnd-loot-generator": [["ledger", "AuditCampaign"]],
    "dnd-lore-archivist": [["summary", "AuditCampaign"]],
    "dnd-npc-personality-weaver": [["list", "AuditCampaign"]],
    "dnd-persistent-dm": [["health", "AuditCampaign"]],
    "dnd-quest-tracker": [["list", "AuditCampaign"]],
    "dnd-rules-reference": [["list"]],
    "dnd-rumor-event-generator": [["rumors", "AuditCampaign", "--no-persist"]],
    "dnd-session-scribe": [["auto-recap", "AuditCampaign"]],
    "dnd-utils": [["campaigns-root"]],
    "dnd-visual-weaver": [["weave-prompt", "AuditCampaign", "test scene"]],
    "dnd-voice-assistant": [["parse", "next turn"]],
}

UTILS_CLI_SCRIPTS = [
    "dnd-utils/scripts/dnd_state_utils.py",
    "dnd-utils/scripts/narration_cli.py",
    "dnd-utils/scripts/skill_registry.py",
    "dnd-utils/scripts/skill_orchestrator.py",
]


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


def validate() -> dict:
    issues: list[str] = []
    skills_report: list[dict] = []

    with tempfile.TemporaryDirectory() as tmp:
        env = {**dict(__import__("os").environ), "DND_CAMPAIGNS_ROOT": tmp}
        py = sys.executable

        init_script = SKILLS / "dnd-utils/scripts/dnd_state_utils.py"
        subprocess.run(
            [py, str(init_script), "init", "AuditCampaign", "--force"],
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

            cli_scripts = []
            for script in scripts:
                try:
                    py_compile.compile(str(script), doraise=True)
                except py_compile.PyCompileError as exc:
                    skill_issues.append(f"Compile error {script.name}: {exc}")

                text = script.read_text(encoding="utf-8")
                if "if __name__" in text:
                    cli_scripts.append(script.name)
                if "NotImplementedError" in text or "raise NotImplemented" in text:
                    skill_issues.append(f"NotImplemented stub in {script.name}")

            commands = skill_issues and [] or []
            for script in scripts:
                commands.extend(_cli_commands(script))

            for cmd_argv in SMOKE_COMMANDS.get(skill, []):
                if skill == "dnd-utils":
                    script = SKILLS / UTILS_CLI_SCRIPTS[0]
                elif skill == "dnd-content-forge":
                    script = SKILLS / "dnd-content-forge/scripts/content_forge.py"
                else:
                    script = scripts[0] if scripts else None
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
                    "commands_sample": sorted(set(commands))[:12],
                    "valid": len(skill_issues) == 0,
                    "issues": skill_issues,
                }
            )

    return {
        "skills_checked": len(skills_report),
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