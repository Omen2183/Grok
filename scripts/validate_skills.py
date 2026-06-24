#!/usr/bin/env python3
"""Validate SKILL.md files in the Grok D&D skill pack."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / ".grok" / "skills"

REQUIRED_SECTION_HINTS = (
    ("when to use", "triggers"),
    ("capabilities", "capability"),
    ("behavior", "workflow", "example flow"),
)

REQUIRED_FRONTMATTER = ("name", "description")


def validate_skill_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []

    if not text.startswith("---"):
        issues.append("Missing YAML frontmatter")
    else:
        end = text.find("---", 3)
        if end == -1:
            issues.append("Unclosed YAML frontmatter")
        else:
            front = text[3:end]
            for key in REQUIRED_FRONTMATTER:
                if f"{key}:" not in front:
                    issues.append(f"Frontmatter missing '{key}'")

    body_lower = text.lower()
    for hints in REQUIRED_SECTION_HINTS:
        if not any(h in body_lower for h in hints):
            issues.append(f"Missing section (one of: {', '.join(hints)})")

    scripts_dir = path.parent / "scripts"
    scripts = list(scripts_dir.glob("*.py")) if scripts_dir.exists() else []
    script_count = len(scripts)
    if script_count == 0:
        issues.append("Missing scripts/ — every skill must have at least one Python backend")
    elif not any("if __name__" in s.read_text(encoding="utf-8") for s in scripts):
        issues.append("No CLI entry point found (scripts lack if __name__ == '__main__')")

    return {
        "skill": path.parent.name,
        "path": str(path),
        "valid": len(issues) == 0,
        "issues": issues,
        "scripts": script_count,
    }


def main() -> int:
    results = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith(("_", ".")):
            continue
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            results.append(validate_skill_md(skill_md))

    failed = [r for r in results if not r["valid"]]
    print(json.dumps({"checked": len(results), "failed": len(failed), "results": results}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())