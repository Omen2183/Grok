"""Tests for dnd-skills-manager CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "skills_manager.py"


def test_inventory_lists_core_skills():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "inventory"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "dnd-persistent-dm" in result.stdout
    assert "dnd-skills-manager" in result.stdout


def test_sync_check_against_self():
    skills_root = Path(__file__).resolve().parent.parent.parent
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "sync-check",
            "--against",
            str(skills_root),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    payload = __import__("json").loads(result.stdout)
    assert payload["aligned"] is True