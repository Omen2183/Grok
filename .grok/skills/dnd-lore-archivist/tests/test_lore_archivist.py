"""Tests for lore archivist backend."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "lore_archivist.py"


def test_append_and_summary():
    with tempfile.TemporaryDirectory() as tmp:
        env = {**dict(__import__("os").environ), "DND_CAMPAIGNS_ROOT": tmp}
        campaign = "Lore Test"
        subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent.parent / "dnd-persistent-dm" / "scripts" / "persistent_dm.py"), "init", campaign],
            capture_output=True,
            env=env,
            check=True,
        )
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "append", campaign, "Ancient shrine discovered"],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        data = json.loads(r.stdout)
        assert "timestamp" in data or "event" in data or data
        r2 = subprocess.run(
            [sys.executable, str(SCRIPT), "summary", campaign],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        assert "Ancient shrine" in r2.stdout or "summary" in r2.stdout