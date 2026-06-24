"""Shared pytest fixtures for all D&D skill tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

UTILS = Path(__file__).parent / "dnd-utils" / "scripts"
if str(UTILS) not in sys.path:
    sys.path.insert(0, str(UTILS))

import paths  # noqa: E402
import dnd_state_utils as state  # noqa: E402


@pytest.fixture
def campaign_root(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "get_campaigns_root", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def campaign(campaign_root):
    name = "Integration Campaign"
    state.init_campaign(name, force=True, pc_name="Test Hero")
    return name