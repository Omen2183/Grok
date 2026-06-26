"""E2E: session-end playbook chains scribe → quests → audit."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "dnd-utils" / "scripts"))
sys.path.insert(0, str(ROOT / "dnd-quest-tracker" / "scripts"))

import dnd_state_utils as state  # noqa: E402
from quest_tracker import add_quest, list_active  # noqa: E402
from skill_orchestrator import run_playbook  # noqa: E402
from paths import get_campaign_path  # noqa: E402


def test_session_end_playbook_e2e(campaign):
    state.init_campaign(campaign, force=True, enable_sqlite=True, pc_name="Aria")
    state.record_event(campaign, "Party cleared the mine", tags=["exploration"])
    state.record_event(campaign, "Found a sealed door", tags=["hook"], importance="major")

    add_quest(campaign, "Investigate the sealed door", summary="Vault mystery")

    result = run_playbook(campaign, "session-end", stop_on_error=True)
    assert result["playbook"] == "session-end"
    assert result["steps_run"] >= 3

    step_statuses = [r.get("status") for r in result.get("results", [])]
    assert "failed" not in step_statuses

    recaps = list((get_campaign_path(campaign) / "recaps").glob("session_*.md"))
    assert len(recaps) >= 1

    quests = list_active(campaign)
    assert len(quests.get("active_quests", [])) >= 1

    audit = state.enhanced_audit_campaign(campaign)
    assert audit["healthy"] is True

    from event_system import search_events
    events = search_events(campaign, tag="session-end", limit=5)
    assert any("session" in (e.get("description") or "").lower() for e in events)