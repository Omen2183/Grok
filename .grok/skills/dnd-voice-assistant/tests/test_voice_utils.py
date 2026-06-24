import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from voice_utils import parse_damage_phrase, parse_healing_phrase, route_voice_request


def test_voice_parsing():
    assert parse_damage_phrase("Goblin takes 8 damage") == ("Goblin", 8)
    assert parse_healing_phrase("Aria heals 10") == ("Aria", 10)
    route = route_voice_request("Goblin takes 5 damage")
    assert route["primary_skill"] == "dnd-combat-assistant"


def test_voice_routing_intents():
    assert route_voice_request("next turn")["primary_skill"] == "dnd-combat-assistant"
    assert route_voice_request("roll perception")["primary_skill"] == "dnd-dice-engine"
    assert route_voice_request("what's the rumor")["primary_skill"] == "dnd-rumor-event-generator"