"""Tests for v4.0.0 features: lore FTS, grid combat, SRD, multiclass, factions, VTT."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

UTILS = Path(__file__).resolve().parent.parent / "dnd-utils" / "scripts"
sys.path.insert(0, str(UTILS))

from class_progression import (  # noqa: E402
    calculate_spell_slots,
    validate_multiclass,
)
from lore_index import rebuild_lore_index, search_lore  # noqa: E402


@pytest.fixture
def campaign(tmp_path, monkeypatch):
    monkeypatch.setenv("DND_CAMPAIGNS_ROOT", str(tmp_path))
    name = "V4Test"
    from dnd_state_utils import init_campaign  # noqa: E402

    init_campaign(name, pc_name="Test Hero", force=True, enable_sqlite=True)
    return name


def test_fts_lore_search(campaign):
    lore_scripts = Path(__file__).resolve().parent.parent / "dnd-lore-archivist" / "scripts"
    sys.path.insert(0, str(lore_scripts))
    from lore_archivist import append_lore  # noqa: E402

    append_lore(campaign, "The ancient vault beneath Thornhold imprisons wraiths.")
    stats = rebuild_lore_index(campaign)
    assert stats["events"] >= 1 or stats["lore_summary"] >= 1
    result = search_lore(campaign, "vault wraiths", limit=5)
    assert result["engine"] == "fts5"
    assert result["count"] >= 0


def test_multiclass_spell_slots():
    classes = [{"name": "Wizard", "level": 5}, {"name": "Fighter", "level": 3}]
    slots = calculate_spell_slots(classes)
    assert slots["caster_level"] == 5
    assert "3" in slots["slots"]


def test_multiclass_prereqs():
    stats = {"str": 14, "dex": 12, "con": 13, "int": 16, "wis": 10, "cha": 8}
    result = validate_multiclass(stats, [{"name": "Wizard", "level": 5}], "Fighter")
    assert result["valid"] is True


def test_grid_combat_init_and_place(campaign):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dnd-combat-assistant" / "scripts"))
    from grid_combat import init_grid, place_token, grid_distance  # noqa: E402

    init_grid(campaign, width=10, height=10)
    place_token(campaign, "Hero", 2, 3)
    place_token(campaign, "Goblin", 5, 3)
    dist = grid_distance(campaign, "Hero", "Goblin")
    assert dist["feet"] == 15


def test_srd_spell_lookup():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dnd-rules-reference" / "scripts"))
    from srd_data import lookup_spell, search_spells  # noqa: E402

    fireball = lookup_spell("fireball")
    assert fireball["found"] is True
    assert fireball["level"] == 3
    hits = search_spells("heal")
    assert len(hits) >= 1


def test_vtt_foundry_export(campaign):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dnd-character-manager" / "scripts"))
    from vtt_export import export_foundry_actor, write_export  # noqa: E402
    from character_manager import load_character  # noqa: E402

    char = load_character(campaign)
    data = export_foundry_actor(char)
    assert data["type"] == "character"
    path = write_export(campaign, data, "test_foundry.json")
    assert Path(path).exists()


def test_faction_simulation(campaign):
    from dnd_state_utils import update_kingdom_state  # noqa: E402
    from faction_engine import set_faction_goal, simulate_faction_round  # noqa: E402

    update_kingdom_state(
        campaign,
        {"factions": {"merchants": {"influence": 5, "attitude": "friendly", "goals": []}}},
    )
    set_faction_goal(campaign, "merchants", "expand_trade")
    result = simulate_faction_round(campaign, seed=42)
    assert result["ticks"] == 1
    assert "merchants" in result["factions"]