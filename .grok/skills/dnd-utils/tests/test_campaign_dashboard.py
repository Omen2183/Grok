"""Tests for campaign dashboard and analytics."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import dnd_state_utils as state
from campaign_analytics import _load_all_events, archive_old_events, event_counts_by_tag, run_analytics, sync_sqlite_from_json
from campaign_dashboard import build_campaign_dashboard


def test_dashboard_snapshot(campaign):
    state.init_campaign(campaign, force=True, pc_name="Test Hero")
    state.record_event(campaign, "Arrived at tavern", tags=["travel"])
    dash = build_campaign_dashboard(campaign)
    assert dash["campaign"] == campaign
    assert dash["character"]["name"] == "Test Hero"
    assert "mobile_summary" in dash
    assert "What do you do?" in dash["mobile_summary"]


def test_analytics_tags(campaign):
    state.init_campaign(campaign, force=True)
    state.record_event(campaign, "Fight", tags=["combat"])
    state.record_event(campaign, "Loot", tags=["loot"])
    report = event_counts_by_tag(campaign)
    assert report["total_events"] >= 2
    assert "combat" in report["tag_counts"]


def test_sqlite_sync_and_analytics(campaign):
    state.init_campaign(campaign, force=True, enable_sqlite=True)
    state.record_event(campaign, "Indexed event", tags=["test"])
    sync = sync_sqlite_from_json(campaign)
    assert sync["enabled"] is True
    summary = run_analytics(campaign, report="summary")
    assert summary["report"] == "summary"


def test_archive_events(campaign):
    state.init_campaign(campaign, force=True)
    for i in range(12):
        state.record_event(campaign, f"Event {i}", tags=["bulk"])
    total = len(_load_all_events(campaign))
    result = archive_old_events(campaign, keep=5)
    assert result["kept"] == 5
    assert result["archived"] == total - 5