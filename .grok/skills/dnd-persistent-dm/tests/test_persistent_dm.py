import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-utils" / "scripts"))

from persistent_dm import resume_campaign, route_player_action, whats_happening


def test_resume_initialized_campaign(campaign):
    result = resume_campaign(campaign)
    assert result["status"] == "ready"
    assert "mobile_status" in result
    assert "suggestions" in result


def test_route_attack_text(campaign):
    route = route_player_action(campaign, "Goblin takes 5 damage")
    assert route["primary_skill"] == "dnd-combat-assistant"


def test_whats_happening(campaign):
    result = whats_happening(campaign)
    assert result["status"] == "ok"
    assert result["prompt"] == "What do you do?"