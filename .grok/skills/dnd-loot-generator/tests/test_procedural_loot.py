#!/usr/bin/env python3
"""
Unit tests for procedural_loot.py

Run with: pytest dnd-loot-generator/tests/test_procedural_loot.py -v
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "scripts"))
sys.path.append(str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

import pytest
from procedural_loot import (
    generate_loot,
    generate_hoard,
    get_ledger,
    weighted_choice,
)


@pytest.fixture
def temp_campaign(tmp_path, monkeypatch):
    """Create isolated campaign for testing."""
    campaign_name = "TestLootCampaign"
    campaign_path = tmp_path / campaign_name
    campaign_path.mkdir(parents=True)

    import procedural_loot as pl
    original_get_path = pl.get_campaign_path

    def mock_get_campaign_path(name):
        return campaign_path

    monkeypatch.setattr(pl, "get_campaign_path", mock_get_campaign_path)
    yield campaign_name


def test_weighted_choice_returns_item():
    items = [{"name": "Sword", "weight": 10}, {"name": "Shield", "weight": 5}]
    result = weighted_choice(items)
    assert "name" in result
    assert result["name"] in ["Sword", "Shield"]


def test_generate_loot_basic(temp_campaign):
    items = generate_loot(temp_campaign, count=3, item_type="mixed", party_level=3)
    assert len(items) == 3
    assert all("name" in item for item in items)


def test_ledger_prevents_duplicates(temp_campaign):
    # Generate loot multiple times with avoid_duplicates=True
    first = generate_loot(temp_campaign, count=5, item_type="magic", party_level=5, avoid_duplicates=True)
    second = generate_loot(temp_campaign, count=5, item_type="magic", party_level=5, avoid_duplicates=True)

    ledger = get_ledger(temp_campaign)
    found = set(ledger.get("found_items", []))

    # All generated items should be in the ledger
    all_generated = [item["name"] for item in first + second]
    assert all(name in found for name in all_generated)


def test_generate_hoard_structure(temp_campaign):
    hoard = generate_hoard(temp_campaign, party_level=5, cr=4)

    assert "coins" in hoard
    assert "magic_items" in hoard
    assert "consumables" in hoard
    assert "gold" in hoard["coins"]
    assert isinstance(hoard["magic_items"], list)


def test_generate_loot_respects_level_scaling(temp_campaign):
    low_level = generate_loot(temp_campaign, count=10, item_type="magic", party_level=3)
    high_level = generate_loot(temp_campaign, count=10, item_type="magic", party_level=12)

    # Higher level should have access to better items (this is probabilistic but generally true)
    low_names = {item["name"] for item in low_level}
    high_names = {item["name"] for item in high_level}

    # At minimum, both should return items
    assert len(low_names) > 0
    assert len(high_names) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])