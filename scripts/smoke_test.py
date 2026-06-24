#!/usr/bin/env python3
"""Smoke test all D&D skill CLIs against a temp campaign."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".grok" / "skills"


def run(cmd: list[str], env: dict) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=REPO)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        env = {**dict(**__import__("os").environ), "DND_CAMPAIGNS_ROOT": tmp}
        campaign = "Smoke Campaign"
        py = sys.executable

        run([py, str(SKILLS / "dnd-utils/scripts/dnd_state_utils.py"), "init", campaign, "--enable-sqlite"], env)
        run([py, str(SKILLS / "dnd-dice-engine/scripts/dice_roller.py"), "1d20", "--campaign", campaign], env)
        run([py, str(SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"), "init", campaign], env)
        run([py, str(SKILLS / "dnd-loot-generator/scripts/procedural_loot.py"), "generate", campaign], env)
        run([py, str(SKILLS / "dnd-npc-personality-weaver/scripts/npc_manager.py"), "create", campaign, "--name", "Test NPC"], env)
        run([py, str(SKILLS / "dnd-lore-archivist/scripts/lore_archivist.py"), "append", campaign, "Smoke lore entry"], env)
        run([py, str(SKILLS / "dnd-rumor-event-generator/scripts/rumor_generator.py"), "rumors", campaign], env)
        run([py, str(SKILLS / "dnd-session-scribe/scripts/session_scribe.py"), "end-session", campaign, "Smoke test complete", "--xp", "50"], env)

        print(json.dumps({"ok": True, "campaign_root": tmp}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())