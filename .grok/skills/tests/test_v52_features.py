"""Regression tests for v5.2 suite improvements."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_SKILLS = Path(__file__).resolve().parent.parent


def _run(cmd: list[str], env: dict) -> dict:
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=REPO_SKILLS.parent.parent)
    assert r.returncode == 0, r.stderr or r.stdout
    return json.loads(r.stdout) if r.stdout.strip().startswith("{") else {"raw": r.stdout}


def test_quick_session_playbook_registered():
    utils = REPO_SKILLS / "dnd-utils" / "scripts"
    sys.path.insert(0, str(utils))
    from skill_registry import PLAYBOOKS  # noqa: E402

    assert "quick-session" in PLAYBOOKS
    assert "pre-session" in PLAYBOOKS
    assert "party-to-combat" in PLAYBOOKS


def test_auto_initiative_and_dm_screen():
    with tempfile.TemporaryDirectory() as tmp:
        env = {**dict(__import__("os").environ), "DND_CAMPAIGNS_ROOT": tmp}
        py = sys.executable
        campaign = "Combat V52"
        subprocess.run([py, str(REPO_SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "init", campaign], env=env, check=True)
        subprocess.run([py, str(REPO_SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"), "init", campaign], env=env, check=True)
        out = subprocess.run(
            [
                py,
                str(REPO_SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"),
                "add",
                campaign,
                "--name",
                "Goblin",
                "--hp",
                "7",
                "--auto-initiative",
                "--cr",
                "0.25",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        data = json.loads(out.stdout)
        assert data["combatants"][0]["initiative"] >= 1
        summary = subprocess.run(
            [py, str(REPO_SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"), "summary", campaign, "--dm-screen"],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        assert "healthy" in summary.stdout or "wounded" in summary.stdout or "Goblin" in summary.stdout


def test_campaign_health_cli():
    with tempfile.TemporaryDirectory() as tmp:
        env = {**dict(__import__("os").environ), "DND_CAMPAIGNS_ROOT": tmp}
        py = sys.executable
        campaign = "Health V52"
        subprocess.run([py, str(REPO_SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "init", campaign], env=env, check=True)
        out = subprocess.run(
            [py, str(REPO_SKILLS / "dnd-utils/scripts/narration_cli.py"), "campaign-health", campaign],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        data = json.loads(out.stdout)
        assert data.get("health") == "ok"
        assert "voice_summary" in data