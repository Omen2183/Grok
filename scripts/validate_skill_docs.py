#!/usr/bin/env python3
"""Verify SKILL.md documents CLI commands and required production sections."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".grok" / "skills"

REQUIRED_SECTIONS = (
    "capabilities",
    "tools & scripts",
    "ios / voice",
    "skill coordination",
    "integration",
)

# Skills that are import-only libraries within dnd-utils
UTILS_LIBRARY_ONLY = {
    "bootstrap.py", "paths.py", "errors.py", "event_system.py", "kingdom_sim.py",
    "narration_helpers.py", "sqlite_layer.py", "sync_bridge.py", "xp_tables.py",
    "campaign_dashboard.py", "campaign_analytics.py",
}

# dice_roller registers check/attack/save via loop variable
EXTRA_COMMANDS: dict[str, set[str]] = {
    "dnd-dice-engine": {"check", "attack", "save", "crit", "count-successes", "modify-damage"},
}

# generate_monster uses argparse without subcommands
EXTRA_COMMANDS["dnd-content-forge"] = {"generate_monster"}


def _cli_commands(skill_dir: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    scripts = skill_dir / "scripts"
    if not scripts.exists():
        return out
    for script in sorted(scripts.glob("*.py")):
        if script.name in UTILS_LIBRARY_ONLY:
            continue
        text = script.read_text(encoding="utf-8")
        if "if __name__" not in text:
            continue
        cmds = sorted(set(re.findall(r'add_parser\(\s*["\']([^"\']+)["\']', text)))
        extra = EXTRA_COMMANDS.get(skill_dir.name, set())
        cmds = sorted(set(cmds) | extra)
        if cmds or script.name == "generate_monster.py":
            out[script.name] = cmds
    return out


def validate_skill(skill_dir: Path) -> dict:
    skill = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    issues: list[str] = []
    if not skill_md.exists():
        return {"skill": skill, "valid": False, "issues": ["Missing SKILL.md"]}

    text = skill_md.read_text(encoding="utf-8")
    lower = text.lower()

    for section in REQUIRED_SECTIONS:
        if section not in lower:
            issues.append(f"Missing section: {section}")

    commands_by_script = _cli_commands(skill_dir)
    all_cmds = {c for cmds in commands_by_script.values() for c in cmds}
    missing_cmds = [c for c in sorted(all_cmds) if c not in text]
    if missing_cmds:
        issues.append(f"SKILL.md missing CLI mentions: {missing_cmds}")

    if "/home/workdir/" in text:
        issues.append("Hardcoded /home/workdir/ in SKILL.md (use paths.py / DND_CAMPAIGNS_ROOT)")

    return {
        "skill": skill,
        "valid": len(issues) == 0,
        "issues": issues,
        "commands": commands_by_script,
        "command_count": len(all_cmds),
    }


def main() -> int:
    results = [validate_skill(d) for d in sorted(SKILLS.iterdir()) if d.is_dir() and d.name.startswith("dnd-")]
    failed = [r for r in results if not r["valid"]]
    report = {
        "checked": len(results),
        "failed": len(failed),
        "valid": len(failed) == 0,
        "results": results,
    }
    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())