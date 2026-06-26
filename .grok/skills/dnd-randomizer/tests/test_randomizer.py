"""Tests for dnd-randomizer."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
UTILS = Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(UTILS))

from randomizer import (  # noqa: E402
    apply_world,
    random_character,
    random_everything,
    random_item,
    random_name,
)
from randomizer_engine import list_tables, roll_table  # noqa: E402


@pytest.fixture
def campaign(tmp_path, monkeypatch):
    monkeypatch.setenv("DND_CAMPAIGNS_ROOT", str(tmp_path))
    from dnd_state_utils import init_campaign  # noqa: E402

    init_campaign("RandTest", pc_name="Hero", force=True)
    return "RandTest"


def test_list_tables():
    tables = list_tables()
    assert "weather" in tables["builtin"]
    assert "magic_item" in tables["builtin"]


def test_roll_table_seeded():
    a = roll_table("weather", count=1, seed=99)
    b = roll_table("weather", count=1, seed=99)
    assert a["results"][0]["name"] == b["results"][0]["name"]


def test_random_character_has_classes():
    result = random_character(level=5, multiclass=True, seed=1)
    char = result["character"]
    assert char["level"] == 5
    assert len(char["classes"]) >= 1
    assert char["stats"]["str"] >= 3


def test_random_item():
    item = random_item(level=3, seed=2)
    assert "item" in item
    assert "name" in item["item"]


def test_random_everything_package():
    pkg = random_everything(level=2, seed=3)
    assert "character" in pkg
    assert "world" in pkg
    assert "encounter" in pkg


def test_random_name():
    person = random_name(name_type="person", seed=4)
    tavern = random_name(name_type="tavern", seed=5)
    assert " " in person["name"] or len(person["name"]) > 2
    assert "The" in tavern["name"]


def test_apply_world(campaign):
    result = apply_world(campaign, seed=7)
    assert result["world"]["domain_name"]
    from dnd_state_utils import get_world_state  # noqa: E402

    world = get_world_state(campaign)
    assert world.get("current_location")


def test_travel_day(campaign):
    from randomizer import travel_day  # noqa: E402

    day = travel_day(campaign, seed=11)
    assert "weather" in day
    assert "complication" in day


def test_mobile_summary():
    from randomizer import mobile_summary  # noqa: E402

    result = mobile_summary("feat", seed=12)
    assert result["summary"].startswith("Random feat:")


def test_new_tables():
    tables = list_tables()
    for name in ("trinket", "wild_magic", "trap", "social_scene", "shop_stock"):
        assert name in tables["builtin"]


def test_srd_feat():
    from randomizer import random_feat  # noqa: E402

    result = random_feat(seed=99)
    assert result.get("feat") or result.get("detail")