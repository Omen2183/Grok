import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from encounter_builder import build_encounter, calculate_budget, list_encounters, save_encounter_plan


def test_calculate_budget():
    assert calculate_budget(5, "Medium", 4) == 750


def test_build_encounter(campaign):
    plan = build_encounter(campaign, theme="goblin raid", difficulty="Medium")
    assert plan["xp_budget"] > 0
    assert plan["enemies"]
    assert "generation_prompt" in plan


def test_save_and_list_encounter(campaign):
    plan = build_encounter(campaign, theme="test fight")
    save_encounter_plan(campaign, plan, name="test")
    listed = list_encounters(campaign)
    assert len(listed) >= 1