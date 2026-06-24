import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from character_manager import level_up, load_character, update_inventory, apply_death_save


def test_level_up_and_inventory(campaign):
    level_up(campaign, levels=1, class_name="Fighter")
    char = load_character(campaign)
    assert char["level"] == 2

    update_inventory(campaign, "add", {"name": "Healing Potion", "type": "consumable"})
    char = load_character(campaign)
    assert any(i["name"] == "Healing Potion" for i in char["inventory"])


def test_death_saves(campaign):
    apply_death_save(campaign, success=True)
    char = load_character(campaign)
    assert char["death_saves"]["successes"] == 1