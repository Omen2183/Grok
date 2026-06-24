"""Integration tests: combat_tracker sync_bridge wiring to character sheet."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-character-manager" / "scripts"))

import dnd_state_utils as state
from combat_tracker import add_combatant, apply_damage, apply_healing, end_combat, init_combat, record_death_save


def test_player_damage_syncs_to_character_sheet(campaign):
    init_combat(campaign, "Sync Test")
    add_combatant(campaign, "Test Hero", hp=12, initiative=15, is_player=True)

    apply_damage(campaign, "Test Hero", 12)
    char = state.get_player_character(campaign)
    assert char["hit_points"]["current"] == 0
    assert char["status"] == "Dying"


def test_player_healing_syncs_while_dying(campaign):
    init_combat(campaign, "Heal Sync")
    add_combatant(campaign, "Test Hero", hp=12, initiative=10, is_player=True)
    apply_damage(campaign, "Test Hero", 12)
    apply_healing(campaign, "Test Hero", 5)

    char = state.get_player_character(campaign)
    assert char["hit_points"]["current"] == 5
    assert char["status"] == "Alive"


def test_death_save_syncs_to_character_sheet(campaign):
    init_combat(campaign, "Death Saves")
    add_combatant(campaign, "Test Hero", hp=12, initiative=10, is_player=True)
    apply_damage(campaign, "Test Hero", 12)

    record_death_save(campaign, "Test Hero", success=True)
    char = state.get_player_character(campaign)
    assert char["death_saves"]["successes"] == 1


def test_sync_reconciles_death_saves(campaign):
    init_combat(campaign, "DS Sync")
    add_combatant(campaign, "Test Hero", hp=12, initiative=10, is_player=True)
    apply_damage(campaign, "Test Hero", 12)
    record_death_save(campaign, "Test Hero", success=True)
    record_death_save(campaign, "Test Hero", success=True)

    char = state.get_player_character(campaign)
    assert char["death_saves"]["successes"] == 2
    assert char["hit_points"]["current"] == 0
    assert "Unconscious" in char.get("conditions", [])


def test_end_combat_reconciles_player_hp(campaign):
    init_combat(campaign, "End Sync")
    add_combatant(campaign, "Test Hero", hp=12, initiative=10, is_player=True)
    apply_damage(campaign, "Test Hero", 4)

    state.update_player_hp(campaign, new_current=5)
    end_combat(campaign)

    char = state.get_player_character(campaign)
    assert char["hit_points"]["current"] == 8