"""Playbook wiring tests for randomizer steps on Grok iOS / PC."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "dnd-utils" / "scripts"))

from skill_orchestrator import _build_playbook_argv, run_playbook  # noqa: E402
import dnd_state_utils as state  # noqa: E402


def test_party_generator_argv_no_campaign_injection():
    argv = _build_playbook_argv(
        "dnd-randomizer/scripts/randomizer.py",
        "Test Campaign",
        "random-party",
        ["--size", "4", "--level", "3"],
        pass_campaign=False,
    )
    assert "random-party" in argv
    assert "Test Campaign" not in argv
    assert "--size" in argv


def test_mobile_summary_campaign_after_kind():
    argv = _build_playbook_argv(
        "dnd-randomizer/scripts/randomizer.py",
        "Test Campaign",
        "mobile-summary",
        ["party", "--level", "3"],
        campaign_after_args=True,
    )
    idx_party = argv.index("party")
    idx_campaign = argv.index("Test Campaign")
    assert idx_party < idx_campaign


def test_party_generator_playbook_runs(campaign, monkeypatch, tmp_path):
    monkeypatch.setenv("DND_CAMPAIGNS_ROOT", str(tmp_path))
    state.init_campaign(campaign, force=True, pc_name="Hero")
    result = run_playbook(campaign, "party-generator", stop_on_error=False)
    assert result["playbook"] == "party-generator"
    statuses = [r["status"] for r in result["results"]]
    assert "ok" in statuses
    assert statuses.count("skipped") == 0