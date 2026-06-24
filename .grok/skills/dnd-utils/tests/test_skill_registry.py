import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from skill_registry import (
    PLAYBOOKS,
    coordination_summary,
    get_playbook,
    list_all_skills,
    resolve_intent,
)


def test_list_all_skills():
    skills = list_all_skills()
    assert len(skills) == 16
    assert "dnd-persistent-dm" in skills
    assert "dnd-quest-tracker" in skills


def test_resolve_damage_intent():
    plan = resolve_intent("damage", campaign="Test", context={"damage": ("Goblin", 8)})
    assert plan["primary_skill"] == "dnd-combat-assistant"
    assert plan["resolved_args"] == ["--target", "Goblin", "--amount", "8"]


def test_playbooks_exist():
    assert "session-end" in PLAYBOOKS
    assert "kingdom-turn" in PLAYBOOKS
    steps = get_playbook("session-end")
    assert any(s["skill"] == "dnd-session-scribe" for s in steps)


def test_coordination_summary():
    summary = coordination_summary("dnd-combat-assistant")
    assert summary["skill"] == "dnd-combat-assistant"
    assert "dnd-persistent-dm" in summary["called_by"]