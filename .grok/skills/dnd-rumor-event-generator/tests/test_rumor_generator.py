"""Tests for rumor event generator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "rumor_generator.py"
DM = Path(__file__).resolve().parent.parent.parent / "dnd-persistent-dm" / "scripts" / "persistent_dm.py"


def test_generate_rumors():
    with tempfile.TemporaryDirectory() as tmp:
        env = {**dict(__import__("os").environ), "DND_CAMPAIGNS_ROOT": tmp}
        campaign = "Rumor Test"
        subprocess.run([sys.executable, str(DM), "init", campaign], capture_output=True, env=env, check=True)
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "rumors", campaign, "--count", "2"],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        data = json.loads(r.stdout)
        rumors = data.get("rumors", data.get("results", []))
        assert len(rumors) >= 1