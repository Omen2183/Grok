"""Tests for cross-platform Grok iOS / PC path resolution."""

import os
from pathlib import Path

from paths import (
    detect_runtime_platform,
    format_python_cli,
    get_campaigns_root,
    get_grok_home,
    get_runtime_context,
    get_skills_root,
    get_workspace_root,
    python_cli_argv,
    resolve_skill_script,
)


def test_campaigns_root_env_override(tmp_path, monkeypatch):
    custom = tmp_path / "my-campaigns"
    custom.mkdir()
    monkeypatch.setenv("DND_CAMPAIGNS_ROOT", str(custom))
    assert get_campaigns_root() == custom.resolve()


def test_grok_artifacts_root_env(tmp_path, monkeypatch):
    monkeypatch.delenv("DND_CAMPAIGNS_ROOT", raising=False)
    host = tmp_path / "grok-home"
    (host / "artifacts").mkdir(parents=True)
    monkeypatch.setenv("GROK_ARTIFACTS_ROOT", str(host / "artifacts"))
    assert get_campaigns_root() == (host / "artifacts" / "dnd-campaigns").resolve()


def test_grok_home_campaigns_default(tmp_path, monkeypatch):
    monkeypatch.delenv("DND_CAMPAIGNS_ROOT", raising=False)
    monkeypatch.delenv("GROK_ARTIFACTS_ROOT", raising=False)
    grok_home = tmp_path / ".grok"
    (grok_home / "skills" / "dnd-utils" / "scripts").mkdir(parents=True)
    monkeypatch.setenv("GROK_HOME", str(grok_home))
    root = get_campaigns_root(create=True)
    assert root == (grok_home / "artifacts" / "dnd-campaigns").resolve()
    assert root.exists()


def test_grok_workspace_root_env(tmp_path, monkeypatch):
    ws = tmp_path / "workspace"
    ws.mkdir()
    for key in (
        "DND_CAMPAIGNS_ROOT",
        "GROK_CAMPAIGNS_ROOT",
        "GROK_ARTIFACTS_ROOT",
        "GROK_USER_DATA",
        "GROK_HOME",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("GROK_WORKSPACE_ROOT", str(ws))
    assert get_campaigns_root() == (ws / "artifacts" / "dnd-campaigns").resolve()


def test_skills_root_from_module_location():
    skills = get_skills_root()
    assert skills.name == "skills"
    assert (skills / "dnd-utils" / "scripts" / "paths.py").exists()


def test_resolve_skill_script():
    script = resolve_skill_script("dnd-utils/scripts/dnd_state_utils.py")
    assert script.name == "dnd_state_utils.py"
    assert script.exists()


def test_format_python_cli_repo_relative():
    ctx = get_runtime_context()
    cmd = format_python_cli("dnd-utils/scripts/dnd_state_utils.py", "campaigns-root")
    if ctx["skills_layout"] == "repo":
        assert cmd.startswith("python .grok/skills/")
    else:
        assert "dnd_state_utils.py" in cmd


def test_python_cli_argv_absolute():
    argv = python_cli_argv("dnd-dice-engine/scripts/dice_roller.py", "roll", "1d20")
    assert argv[1].endswith("dice_roller.py")
    assert Path(argv[1]).is_absolute()


def test_runtime_context_keys():
    ctx = get_runtime_context()
    for key in ("platform", "skills_root", "grok_home", "workspace_root", "campaigns_root"):
        assert key in ctx


def test_detect_runtime_platform_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("DND_CAMPAIGNS_ROOT", str(tmp_path))
    assert detect_runtime_platform() == "env_override"