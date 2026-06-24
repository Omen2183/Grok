import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from npc_manager import append_npc_note, create_npc, get_npc, adjust_relationship


def test_npc_lifecycle(campaign):
    npc = create_npc(campaign, {"name": "Mira Voss", "personality": "Sharp"})
    assert npc["name"] == "Mira Voss"
    updated = adjust_relationship(campaign, npc["id"], 2, note="Helped at the docks")
    assert updated is not None
    assert updated["relationship_score"] == 2


def test_note_append_on_update(campaign):
    npc = create_npc(campaign, {"name": "Test NPC", "notes": "First note"})
    append_npc_note(campaign, npc["id"], "Second note")
    refreshed = get_npc(campaign, npc["id"])
    assert "First note" in refreshed["notes"]
    assert "Second note" in refreshed["notes"]