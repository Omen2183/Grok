"""Tests for event_system.py and paths helpers."""

from pathlib import Path

import dnd_state_utils as state
from event_system import record_event, search_events
from paths import backup_file, ensure_dir


def test_ensure_dir_and_backup_file(campaign, tmp_path, monkeypatch):
    monkeypatch.setenv("DND_CAMPAIGNS_ROOT", str(tmp_path))
    state.init_campaign(campaign, force=True)
    events_path = state.get_campaign_path(campaign) / "logs" / "events.json"
    events_path.write_text("[]", encoding="utf-8")

    ensure_dir(events_path.parent)
    backup = backup_file(events_path)

    assert events_path.parent.is_dir()
    assert backup is not None
    assert backup.exists()


def test_search_events_filters(campaign):
    state.init_campaign(campaign, force=True)
    record_event(campaign, "Minor scouting", tags=["exploration"], importance="minor")
    record_event(campaign, "Boss defeated", tags=["combat", "boss"], importance="major", event_type="combat")
    record_event(campaign, "Quest hook found", tags=["quest"], importance="normal")

    by_tag = search_events(campaign, tag="combat", limit=10)
    assert len(by_tag) == 1
    assert by_tag[0]["description"] == "Boss defeated"

    by_type = search_events(campaign, event_type="combat", limit=10)
    assert len(by_type) == 1

    by_importance = search_events(campaign, importance="minor", limit=10)
    assert len(by_importance) == 1
    assert by_importance[0]["description"] == "Minor scouting"

    combined = search_events(campaign, tag="combat,boss", importance="major", limit=10)
    assert len(combined) == 1