import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

import paths
from combat_tracker import add_combatant, apply_damage, apply_healing, init_combat


def test_apply_healing(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_campaigns_root", lambda: tmp_path)
    campaign = "HealTest"
    init_combat(campaign, "Test")
    add_combatant(campaign, "Fighter", hp=20, initiative=10)
    apply_damage(campaign, "Fighter", 12)
    result = apply_healing(campaign, "Fighter", 5)
    fighter = result["combatants"][0]
    assert fighter["hp_current"] == 13
    assert fighter["is_unconscious"] is False