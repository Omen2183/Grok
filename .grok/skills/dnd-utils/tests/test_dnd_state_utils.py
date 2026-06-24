"""Tests for dnd_state_utils.py"""

import dnd_state_utils as state  # noqa: E402


def test_init_campaign_creates_structure(campaign):
    result = state.init_campaign(campaign, force=True)
    assert result["status"] == "created"

    root = state.get_campaign_path(campaign)
    assert (root / "state" / "world_state.json").exists()
    assert (root / "state" / "player_character.json").exists()
    assert (root / "logs" / "session_log.md").exists()


def test_update_player_hp(campaign):
    state.init_campaign(campaign)
    hp = state.update_player_hp(campaign, delta=-5)
    assert hp["current"] == 7

    hp = state.update_player_hp(campaign, new_current=3)
    assert hp["current"] == 3


def test_audit_healthy_campaign(campaign):
    state.init_campaign(campaign)
    audit = state.audit_campaign(campaign)
    assert audit["healthy"] is True
    assert audit["issues"] == []


def test_log_roll(campaign):
    state.init_campaign(campaign)
    state.log_roll(campaign, "1d20+5", 18, {"reason": "attack"})
    rolls_path = state.get_campaign_path(campaign) / "logs" / "rolls.json"
    assert rolls_path.exists()