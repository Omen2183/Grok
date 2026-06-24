"""Tests for cross-platform campaign path resolution."""

import os
from pathlib import Path

from paths import get_campaigns_root


def test_campaigns_root_env_override(tmp_path, monkeypatch):
    custom = tmp_path / "my-campaigns"
    custom.mkdir()
    monkeypatch.setenv("DND_CAMPAIGNS_ROOT", str(custom))
    assert get_campaigns_root() == custom.resolve()


def test_grok_artifacts_root_env(tmp_path, monkeypatch):
    monkeypatch.delenv("DND_CAMPAIGNS_ROOT", raising=False)
    host = tmp_path / "grok-home"
    (host / "artifacts").mkdir(parents=True)
    monkeypatch.setenv("GROK_ARTIFACTS_ROOT", str(host))
    assert get_campaigns_root() == (host / "artifacts" / "dnd-campaigns").resolve()