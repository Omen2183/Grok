"""Tests for dnd_state_utils.py"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent / "scripts"))

import dnd_state_utils as state  # noqa: E402


@pytest.fixture
def temp_campaign(tmp_path, monkeypatch):
    import paths
    monkeypatch.setattr(paths, "get_campaigns_root", lambda: tmp_path)
    return "Test Campaign"


def test_init_campaign_creates_structure(temp_campaign):
    result = state.init_campaign(temp_campaign)
    assert result["status"] == "created"

    root = state.get_campaign_path(temp_campaign)
    assert (root / "state" / "world_state.json").exists()
    assert (root / "state" / "player_character.json").exists()
    assert (root / "logs" / "session_log.md").exists()


def test_update_player_hp(temp_campaign):
    state.init_campaign(temp_campaign)
    hp = state.update_player_hp(temp_campaign, delta=-5)
    assert hp["current"] == 7

    hp = state.update_player_hp(temp_campaign, new_current=3)
    assert hp["current"] == 3


def test_audit_healthy_campaign(temp_campaign):
    state.init_campaign(temp_campaign)
    audit = state.audit_campaign(temp_campaign)
    assert audit["healthy"] is True
    assert audit["issues"] == []


def test_log_roll(temp_campaign):
    state.init_campaign(temp_campaign)
    state.log_roll(temp_campaign, "1d20+5", 18, {"reason": "attack"})
    rolls_path = state.get_campaign_path(temp_campaign) / "logs" / "rolls.json"
    assert rolls_path.exists()