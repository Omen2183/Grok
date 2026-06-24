import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from character_manager import suggest_level_up_options


def test_suggest_level_up(campaign):
    result = suggest_level_up_options(campaign)
    assert "next_level" in result
    assert "feat_ideas" in result
    assert isinstance(result["feat_ideas"], list)