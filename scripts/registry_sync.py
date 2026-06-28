#!/usr/bin/env python3
"""Discover installed skills and validate/sync skill_registry.py manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / ".grok" / "skills"
UTILS_SCRIPTS = SKILLS_DIR / "dnd-utils" / "scripts"
sys.path.insert(0, str(UTILS_SCRIPTS))

from skill_registry import SKILLS, list_all_skills  # noqa: E402

SCRIPT_FOR_SKILL: Dict[str, str] = {
    "dnd-content-forge": "dnd-content-forge/scripts/content_forge.py",
    "dnd-utils": "dnd-utils/scripts/dnd_state_utils.py",
}

LIBRARY_ONLY = {
    "bootstrap.py", "paths.py", "errors.py", "event_system.py", "kingdom_sim.py",
    "narration_helpers.py", "sqlite_layer.py", "sync_bridge.py", "xp_tables.py",
    "rules_data.py", "srd_data.py", "campaign_dashboard.py", "campaign_analytics.py",
    "lore_index.py", "class_progression.py", "faction_engine.py",
    "randomizer_data.py", "randomizer_engine.py",
}


def _cli_commands(script: Path) -> List[str]:
    text = script.read_text(encoding="utf-8")
    if "if __name__" not in text:
        return []
    return sorted(set(re.findall(r'add_parser\(\s*["\']([^"\']+)["\']', text)))


def discover_skills() -> Dict[str, Dict[str, Any]]:
    """Scan .grok/skills for installed skill packages."""
    manifest: Dict[str, Dict[str, Any]] = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or not skill_dir.name.startswith("dnd-"):
            continue
        skill = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        scripts_dir = skill_dir / "scripts"
        cli_scripts: Dict[str, List[str]] = {}
        primary: Optional[str] = None

        if scripts_dir.exists():
            for script in sorted(scripts_dir.glob("*.py")):
                if script.name in LIBRARY_ONLY:
                    continue
                cmds = _cli_commands(script)
                if cmds:
                    rel = f"{skill}/scripts/{script.name}"
                    cli_scripts[script.name] = cmds
                    if primary is None or script.name == SCRIPT_FOR_SKILL.get(skill, "").split("/")[-1]:
                        primary = rel
            if skill in SCRIPT_FOR_SKILL:
                primary = SCRIPT_FOR_SKILL[skill]
            elif not primary and cli_scripts:
                primary = f"{skill}/scripts/{next(iter(cli_scripts))}"

        manifest[skill] = {
            "skill_md": str(skill_md.relative_to(REPO)),
            "primary_script": primary,
            "cli_scripts": cli_scripts,
            "command_count": sum(len(v) for v in cli_scripts.values()),
        }
    return manifest


def validate_registry() -> Dict[str, Any]:
    discovered = discover_skills()
    registered = set(list_all_skills())
    installed = set(discovered.keys())

    issues: List[str] = []
    missing_registry = sorted(installed - registered)
    missing_install = sorted(registered - installed)

    if missing_registry:
        issues.append(f"Skills missing from registry: {missing_registry}")
    if missing_install:
        issues.append(f"Registry entries without SKILL.md: {missing_install}")

    script_mismatches: List[Dict[str, str]] = []
    for skill_id, meta in SKILLS.items():
        if skill_id not in discovered:
            continue
        reg_script = meta.get("script")
        if reg_script:
            disc_primary = discovered[skill_id].get("primary_script")
            if disc_primary and reg_script != disc_primary:
                if not (SKILLS_DIR / reg_script).exists():
                    issues.append(f"{skill_id}: registry script missing: {reg_script}")
                    script_mismatches.append({
                        "skill": skill_id,
                        "registry": reg_script,
                        "discovered": disc_primary or "",
                    })

    return {
        "installed": len(installed),
        "registered": len(registered),
        "valid": len(issues) == 0,
        "issues": issues,
        "script_mismatches": script_mismatches,
        "discovered": discovered,
    }


def generate_registry_stub(skill_id: str) -> str:
    """Template entry for a newly discovered skill."""
    name = skill_id.replace("dnd-", "").replace("-", " ").title()
    return f'''    "{skill_id}": {{
        "role": "specialist",
        "script": "{skill_id}/scripts/TODO.py",
        "triggers": ["{name.lower()}"],
        "calls": ["dnd-utils"],
        "called_by": ["dnd-persistent-dm"],
    }},'''


def fix_registry_scripts(dry_run: bool = True) -> Dict[str, Any]:
    """Update broken script paths in skill_registry.py when discovered primary exists."""
    report = validate_registry()
    registry_path = UTILS_SCRIPTS / "skill_registry.py"
    text = registry_path.read_text(encoding="utf-8")
    changes: List[Dict[str, str]] = []

    for mismatch in report.get("script_mismatches", []):
        skill = mismatch["skill"]
        old = mismatch["registry"]
        new = mismatch["discovered"]
        if not new or not (SKILLS_DIR / new).exists():
            continue
        if f'"{old}"' in text:
            if not dry_run:
                text = text.replace(f'"{old}"', f'"{new}"', 1)
            changes.append({"skill": skill, "from": old, "to": new})

    if changes and not dry_run:
        registry_path.write_text(text, encoding="utf-8")

    return {"dry_run": dry_run, "changes": changes, "applied": not dry_run and bool(changes)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill registry discovery and sync")
    parser.add_argument("--check", action="store_true", help="Exit 1 if registry drift detected")
    parser.add_argument("--discover", action="store_true", help="Print discovered manifest JSON")
    parser.add_argument("--fix-scripts", action="store_true", help="Apply script path fixes")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true", help="Actually write fixes")
    parser.add_argument("--suggest", action="store_true", help="List skills missing from registry")
    args = parser.parse_args()

    if args.discover:
        print(json.dumps(discover_skills(), indent=2))
        return 0

    if args.fix_scripts:
        result = fix_registry_scripts(dry_run=not args.apply)
        print(json.dumps(result, indent=2))
        return 0

    if args.suggest:
        discovered = set(discover_skills().keys())
        registered = set(list_all_skills())
        missing = sorted(discovered - registered)
        extra = sorted(registered - discovered)
        print(json.dumps({
            "missing_from_registry": missing,
            "registry_without_folder": extra,
            "suggested_stubs": [generate_registry_stub(s) for s in missing],
        }, indent=2))
        return 0

    report = validate_registry()
    if args.check:
        print(json.dumps({k: report[k] for k in ("installed", "registered", "valid", "issues")}, indent=2))
        return 0 if report["valid"] else 1

    # Default: full report with stubs for missing skills
    stubs = []
    for skill in sorted(set(discover_skills().keys()) - set(list_all_skills())):
        stubs.append(generate_registry_stub(skill))
    report["suggested_stubs"] = stubs
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())