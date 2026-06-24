"""Regression tests for v3.1.0 backend hardening."""

import sys
from pathlib import Path

import dnd_state_utils as state
from event_system import search_events

UTILS = Path(__file__).parent.parent / "dnd-utils" / "scripts"
sys.path.insert(0, str(UTILS))
sys.path.insert(0, str(Path(__file__).parent.parent / "dnd-combat-assistant" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent / "dnd-session-scribe" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent / "dnd-rumor-event-generator" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent / "dnd-dice-engine" / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent / "dnd-character-manager" / "scripts"))

from combat_tracker import add_combatant, end_combat, init_combat  # noqa: E402
from dice_roller import roll_initiative  # noqa: E402
from rumor_generator import generate_rumors  # noqa: E402


def test_end_combat_awards_xp(campaign):
    init_combat(campaign, "XP Test")
    add_combatant(campaign, "Test Hero", hp=12, initiative=10, is_player=True)
    before = state.get_player_character(campaign).get("xp", 0)
    result = end_combat(campaign, award_xp=50)
    after = state.get_player_character(campaign).get("xp", 0)
    assert result["xp_awarded"] == 50
    assert after == before + 50


def test_rumors_persist_by_default(campaign):
    generate_rumors(campaign, count=2, persist=True)
    events = search_events(campaign, tag="rumor", limit=10)
    assert len(events) >= 2


def test_roll_initiative_returns_total():
    result = roll_initiative(3)
    assert result["type"] == "initiative"
    assert result["initiative_total"] == result["roll"]["total"] + 3


def test_character_sync_cli(campaign, capsys):
    from character_manager import run_cli
    import sys as _sys

    _sys.argv = ["character_manager.py", "sync", campaign]
    run_cli()
    captured = capsys.readouterr()
    assert "Test Hero" in captured.out or "name" in captured.out