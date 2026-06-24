"""End-to-end campaign flow integration test."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "dnd-utils" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-combat-assistant" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-dice-engine" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-loot-generator" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-session-scribe" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-npc-personality-weaver" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-lore-archivist" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-rumor-event-generator" / "scripts"))

import dnd_state_utils as state  # noqa: E402
from combat_tracker import add_combatant, apply_damage, end_combat, init_combat  # noqa: E402
from dice_roller import roll_dice  # noqa: E402
from lore_archivist import append_lore, query_lore  # noqa: E402
from npc_manager import create_npc  # noqa: E402
from procedural_loot import generate_loot  # noqa: E402
from rumor_generator import generate_rumors  # noqa: E402
from session_scribe import end_session  # noqa: E402
from sqlite_layer import is_enabled, query_events_sql  # noqa: E402


def test_full_campaign_session(campaign):
    state.init_campaign(campaign, force=True, enable_sqlite=True, pc_name="Aria")

    state.update_world_state(campaign, {"current_location": "Whisperwood"})
    state.queue_kingdom_project(campaign, "Rebuild watchtower", turns_remaining=1)
    state.advance_kingdom_projects(campaign, turns=1)

    create_npc(campaign, {"name": "Elder Mara", "personality": "Wise", "secret": "Knows the vault"})
    append_lore(campaign, "The vault beneath Whisperwood holds an ancient prison.")
    rumors = generate_rumors(campaign, count=2)
    assert len(rumors) == 2

    roll = roll_dice("1d20+5", campaign=campaign)
    assert "total" in roll

    init_combat(campaign, "Goblin Ambush")
    add_combatant(campaign, "Aria", hp=30, initiative=18, is_player=True)
    add_combatant(campaign, "Goblin", hp=7, initiative=10)
    apply_damage(campaign, "Goblin", 7)

    loot = generate_loot(campaign, cr=1, count=2)
    assert len(loot) >= 1

    result = end_session(campaign, "Cleared goblins and learned vault lore.", xp=150)
    assert result["status"] == "session_saved"
    assert is_enabled(campaign)
    assert query_events_sql(campaign, limit=5)

    audit = state.audit_campaign(campaign)
    assert audit["healthy"] is True

    lore_hits = query_lore(campaign, "vault")
    assert lore_hits["keyword"] == "vault"