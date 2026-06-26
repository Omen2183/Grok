"""Shared import bootstrap for D&D skill Python scripts."""

from __future__ import annotations

import sys
from pathlib import Path

UTILS_SCRIPTS = Path(__file__).resolve().parent


def ensure_utils_importable() -> Path:
    """Add dnd-utils/scripts to sys.path if not already present."""
    path_str = str(UTILS_SCRIPTS)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    return UTILS_SCRIPTS


def skill_scripts_dir(skill_name: str) -> Path:
    from paths import get_skills_root  # noqa: WPS433

    return get_skills_root() / skill_name / "scripts"


# Re-export runtime helpers for skills that import bootstrap first.
def get_skills_root() -> Path:
    ensure_utils_importable()
    from paths import get_skills_root as _root  # noqa: WPS433

    return _root()


def get_grok_home() -> Path:
    ensure_utils_importable()
    from paths import get_grok_home as _home  # noqa: WPS433

    return _home()


def get_workspace_root() -> Path:
    ensure_utils_importable()
    from paths import get_workspace_root as _ws  # noqa: WPS433

    return _ws()


def format_python_cli(script_rel: str, *args: str) -> str:
    ensure_utils_importable()
    from paths import format_python_cli as _fmt  # noqa: WPS433

    return _fmt(script_rel, *args)