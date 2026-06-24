import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from npc_manager import create_npc, get_npc, adjust_relationship


def test_npc_lifecycle(campaign):
    npc = create_npc(campaign, {"name": "Mira Voss", "personality": "Sharp"})
    assert npc["name"] == "Mira Voss"
    updated = adjust_relationship(campaign, npc["id"], 2, note="Helped at the docks")
    assert updated is not None
    assert updated["relationship_score"] == 2