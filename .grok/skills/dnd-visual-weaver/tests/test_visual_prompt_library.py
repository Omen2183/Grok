import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from visual_prompt_library import (
    weave_kingdom_prompt,
    weave_visual_prompt,
    update_visual_canon_after_generation,
)


def test_weave_visual_prompt(campaign):
    result = weave_visual_prompt(campaign, "entering the tavern")
    assert "prompt" in result
    assert "tavern" in result["prompt"].lower() or "entering" in result["prompt"].lower()


def test_weave_kingdom_prompt(campaign):
    result = weave_kingdom_prompt(campaign, focus="capital city")
    assert result["mode"] == "kingdom"
    assert "capital city" in result["prompt"]


def test_append_visual_canon(campaign):
    result = update_visual_canon_after_generation(campaign, "Aria", "Silver hair, green cloak")
    assert result["subject"] == "Aria"
    second = update_visual_canon_after_generation(campaign, "Tavern", "Dim lanterns, oak bar")
    assert second["updated"] == result["updated"]