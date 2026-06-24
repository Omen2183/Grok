"""Verify expanded backends for formerly 'light' skills."""

import sys
from pathlib import Path

RULES = Path(__file__).parent.parent / "dnd-rules-reference" / "scripts"
DOWNTIME = Path(__file__).parent.parent / "dnd-downtime-manager" / "scripts"
NPC = Path(__file__).parent.parent / "dnd-npc-personality-weaver" / "scripts"
RUMOR = Path(__file__).parent.parent / "dnd-rumor-event-generator" / "scripts"
VOICE = Path(__file__).parent.parent / "dnd-voice-assistant" / "scripts"
UTILS = Path(__file__).parent.parent / "dnd-utils" / "scripts"

for p in (RULES, DOWNTIME, NPC, RUMOR, VOICE, UTILS):
    sys.path.insert(0, str(p))

from rules_cheatsheet import list_topics, search_rules  # noqa: E402
from downtime_manager import roll_hit_die, list_downtime_activities  # noqa: E402
from npc_manager import generate_personality_seed, relationship_tier, search_npcs  # noqa: E402
from rumor_generator import generate_faction_move, list_recent_rumors  # noqa: E402
from voice_utils import build_execution_plan, is_voice_session, VOICE_BACKEND_VERSION  # noqa: E402


def test_rules_backend_depth():
    topics = list_topics()
    assert len(topics) >= 20
    hits = search_rules("grapple")
    assert hits["count"] >= 1


def test_downtime_hit_dice(campaign):
    result = roll_hit_die(campaign, count=1)
    assert "healed" in result
    assert result["hit_dice_spent"] == 1


def test_npc_personality_generator():
    seed = generate_personality_seed("Mira", role="innkeeper")
    assert seed["name"] == "Mira"
    assert seed["personality"]
    assert relationship_tier(25) == "friendly"


def test_npc_search(campaign):
    from npc_manager import create_npc

    create_npc(campaign, {"name": "Unique Merchant Zyx"})
    matches = search_npcs(campaign, "Zyx")
    assert len(matches) >= 1


def test_rumor_faction_move(campaign):
    move = generate_faction_move(campaign, seed="bandits")
    assert "headline" in move
    listed = list_recent_rumors(campaign, limit=5)
    assert "events" in listed


def test_voice_execution_plan(campaign):
    assert is_voice_session("start voice dnd")
    plan = build_execution_plan(campaign, "Goblin takes 8 damage")
    assert plan["primary_skill"] == "dnd-combat-assistant"
    assert plan["suggested_commands"]
    assert VOICE_BACKEND_VERSION.startswith("3.")