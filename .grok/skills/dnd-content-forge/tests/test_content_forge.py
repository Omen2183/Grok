import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from content_forge import (
    generate_domain_event_prompt,
    generate_faction_prompt,
    generate_magic_item_prompt,
    generate_quest_prompt,
)


def test_quest_prompt(campaign):
    result = generate_quest_prompt(campaign, "rescue mission")
    assert result["type"] == "quest"
    assert "generation_prompt" in result


def test_faction_prompt(campaign):
    result = generate_faction_prompt(campaign, "Thieves Guild")
    assert "Thieves Guild" in result["generation_prompt"]


def test_magic_item_prompt(campaign):
    result = generate_magic_item_prompt(campaign, rarity="rare", theme="shadow")
    assert result["rarity"] == "rare"


def test_domain_event_prompt(campaign):
    result = generate_domain_event_prompt(campaign, seed="drought")
    assert "drought" in result["generation_prompt"]