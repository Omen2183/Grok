import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "dnd-voice-assistant" / "scripts"))

from skill_orchestrator import enrich_route, route_and_plan


def test_route_and_plan_enriches(campaign):
    plan = route_and_plan(campaign, "Goblin takes 5 damage")
    assert plan["primary_skill"] == "dnd-combat-assistant"
    assert "delegation" in plan
    assert plan["delegation"]["intent"] == "damage"


def test_enrich_route_adds_follow_up():
    base = {"intent": "end_session", "needs_confirmation": True, "primary_skill": "dnd-session-scribe"}
    enriched = enrich_route("Test", base)
    assert enriched.get("must_confirm_before_execute") is True
    assert "delegation" in enriched