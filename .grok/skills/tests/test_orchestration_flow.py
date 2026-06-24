"""Cross-skill orchestration integration test."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "dnd-utils" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-persistent-dm" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-quest-tracker" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-combat-assistant" / "scripts"))

import dnd_state_utils as state  # noqa: E402
from persistent_dm import route_player_action, resume_campaign  # noqa: E402
from quest_tracker import add_quest, list_active  # noqa: E402
from skill_orchestrator import execute_intent  # noqa: E402
from combat_tracker import add_combatant, apply_damage, init_combat  # noqa: E402


def test_full_orchestration_chain(campaign):
    state.init_campaign(campaign, force=True, pc_name="Aria")

    resume = resume_campaign(campaign)
    assert resume["status"] == "ready"
    assert "coordination" in resume

    add_quest(campaign, "Clear the mine", summary="Village quest")
    route = route_player_action(campaign, "next turn")
    assert "delegation" in route

    init_combat(campaign, "Orc Raid")
    add_combatant(campaign, "Aria", hp=30, initiative=15, is_player=True)
    add_combatant(campaign, "Orc", hp=15, initiative=10)

    exec_result = execute_intent(
        campaign,
        "damage",
        context={"damage": ("Orc", 15)},
        confirmed=True,
    )
    assert exec_result["status"] == "executed"

    active = list_active(campaign)
    assert len(active["active_quests"]) == 1

    audit = state.enhanced_audit_campaign(campaign)
    assert audit["healthy"] is True