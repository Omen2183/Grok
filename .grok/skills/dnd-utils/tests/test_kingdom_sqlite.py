import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from kingdom_sim import apply_cascading_consequences, simple_population_update
from sqlite_layer import is_enabled, query_events_sql
import dnd_state_utils as state


def test_sqlite_and_kingdom_sim(campaign):
    state.init_campaign(campaign, force=True, enable_sqlite=True)
    from event_system import record_event
    record_event(campaign, "SQLite sync test", tags=["test"])
    assert is_enabled(campaign)
    rows = query_events_sql(campaign, limit=5)
    assert len(rows) >= 1

    pop = simple_population_update(campaign, 50, reason="immigration")
    assert pop["population"] >= 1050

    effects = apply_cascading_consequences(campaign, "New watchtower")
    assert len(effects) >= 1