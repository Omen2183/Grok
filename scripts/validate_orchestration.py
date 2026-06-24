#!/usr/bin/env python3
"""Verify skill_registry matches installed skills and playbooks are runnable."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / ".grok" / "skills"
sys.path.insert(0, str(SKILLS_DIR / "dnd-utils" / "scripts"))

from skill_registry import PLAYBOOKS, SKILLS as SKILL_META, list_all_skills  # noqa: E402


def main() -> int:
    issues: list[str] = []
    installed = {
        d.name
        for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    }
    registered = set(list_all_skills())

    missing_registry = installed - registered
    missing_install = registered - installed
    if missing_registry:
        issues.append(f"Skills missing from registry: {sorted(missing_registry)}")
    if missing_install:
        issues.append(f"Registry entries without SKILL.md: {sorted(missing_install)}")

    for skill_id, meta in SKILL_META.items():
        script = meta.get("script")
        scripts = meta.get("scripts", {})
        paths = [script] if script else list(scripts.values())
        for rel in paths:
            if rel and not (SKILLS_DIR / rel).exists():
                issues.append(f"{skill_id}: missing script {rel}")

    for name, steps in PLAYBOOKS.items():
        if not steps:
            issues.append(f"Empty playbook: {name}")

    print(json.dumps({
        "installed": len(installed),
        "registered": len(registered),
        "playbooks": len(PLAYBOOKS),
        "valid": len(issues) == 0,
        "issues": issues,
    }, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())