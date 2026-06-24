import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from quest_tracker import add_hook, add_quest, complete_quest, list_active


def test_quest_lifecycle(campaign):
    quest = add_quest(campaign, "Find the Seal", summary="Elder needs help", objectives=["Search ruins"])
    assert quest["status"] == "active"
    add_hook(campaign, "Lights in the north")
    active = list_active(campaign)
    assert len(active["active_quests"]) == 1
    assert len(active["open_hooks"]) == 1
    done = complete_quest(campaign, quest["id"], notes="Found it")
    assert done is not None
    assert done["status"] == "completed"