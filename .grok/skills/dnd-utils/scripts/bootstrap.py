"""Shared import bootstrap for D&D skill Python scripts."""

from __future__ import annotations

import sys
from pathlib import Path

UTILS_SCRIPTS = Path(__file__).resolve().parent
SKILLS_ROOT = UTILS_SCRIPTS.parent.parent


def ensure_utils_importable() -> Path:
    """Add dnd-utils/scripts to sys.path if not already present."""
    path_str = str(UTILS_SCRIPTS)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    return UTILS_SCRIPTS


def skill_scripts_dir(skill_name: str) -> Path:
    return SKILLS_ROOT / skill_name / "scripts"