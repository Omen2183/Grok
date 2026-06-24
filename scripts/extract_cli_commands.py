#!/usr/bin/env python3
"""Extract CLI subcommands from all skill scripts."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".grok" / "skills"


def extract_commands(script: Path) -> list[str]:
    text = script.read_text(encoding="utf-8")
    if "if __name__" not in text:
        return []
    return sorted(set(re.findall(r'add_parser\(\s*["\']([^"\']+)["\']', text)))


def main() -> None:
    report: dict[str, dict] = {}
    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir() or not skill_dir.name.startswith("dnd-"):
            continue
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.exists():
            continue
        skill_cmds: dict[str, list[str]] = {}
        for script in sorted(scripts_dir.glob("*.py")):
            cmds = extract_commands(script)
            if cmds:
                skill_cmds[script.name] = cmds
        report[skill_dir.name] = skill_cmds
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()