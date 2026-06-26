#!/usr/bin/env python3
"""Validate Grok iOS / PC runtime path conventions across the skill suite."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".grok" / "skills"
UTILS = SKILLS / "dnd-utils" / "scripts"
sys.path.insert(0, str(UTILS))

from paths import get_runtime_context, resolve_skill_script  # noqa: E402

ALLOWED_WORKDIR_FILES = {
    SKILLS / "dnd-utils" / "scripts" / "paths.py",
}

FORBIDDEN_PATTERNS = (
    '"/home/workdir/',
    "'/home/workdir/",
)


def _scan_python_hardcodes() -> list[str]:
    issues: list[str] = []
    for py in SKILLS.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        text = py.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text and py.resolve() not in {p.resolve() for p in ALLOWED_WORKDIR_FILES}:
                issues.append(f"{py.relative_to(REPO)}: hardcoded {pattern}")
    return issues


def validate() -> dict:
    issues: list[str] = []
    issues.extend(_scan_python_hardcodes())

    ctx = get_runtime_context()
    if not Path(ctx["skills_root"]).exists():
        issues.append(f"skills_root missing: {ctx['skills_root']}")

    try:
        dm = resolve_skill_script("dnd-persistent-dm/scripts/persistent_dm.py")
        if not dm.exists():
            issues.append("persistent_dm.py not resolvable from skills_root")
    except Exception as exc:
        issues.append(f"resolve_skill_script failed: {exc}")

    return {
        "valid": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
        "runtime_context": ctx,
    }


def main() -> int:
    report = validate()
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())