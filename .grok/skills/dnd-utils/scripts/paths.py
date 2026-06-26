"""Cross-platform path resolution for Grok iOS, Grok cloud, and local Grok Build."""

from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


PATHS_VERSION = "5.1.0"

# Grok iOS cloud sandbox (agent workdir)
GROK_CLOUD_WORKDIR = Path("/home/workdir")


def get_skills_root() -> Path:
    """Directory containing all dnd-* skill folders (.grok/skills)."""
    env = os.environ.get("GROK_SKILLS_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    # paths.py lives at .grok/skills/dnd-utils/scripts/paths.py
    return Path(__file__).resolve().parent.parent.parent


def get_grok_home() -> Path:
    """Grok config root (~/.grok or host-provided GROK_HOME)."""
    env = os.environ.get("GROK_HOME")
    if env:
        return Path(env).expanduser().resolve()
    skills = get_skills_root()
    if skills.name == "skills" and skills.parent.name == ".grok":
        return skills.parent.resolve()
    return (Path.home() / ".grok").resolve()


def get_workspace_root() -> Path:
    """Workspace cwd for subprocesses and repo-relative .grok/skills/ invocations."""
    for key in ("GROK_WORKSPACE_ROOT", "CLAUDE_PROJECT_DIR", "GROK_WORKDIR"):
        val = os.environ.get(key)
        if val:
            return Path(val).expanduser().resolve()

    skills = get_skills_root()
    if skills.name == "skills" and skills.parent.name == ".grok":
        return skills.parent.parent.resolve()

    if GROK_CLOUD_WORKDIR.is_dir() and (GROK_CLOUD_WORKDIR / ".grok" / "skills").exists():
        return GROK_CLOUD_WORKDIR.resolve()

    return Path.cwd().resolve()


def detect_runtime_platform() -> str:
    """Best-effort label for diagnostics."""
    if os.environ.get("DND_CAMPAIGNS_ROOT"):
        return "env_override"
    workdir = get_workspace_root()
    if str(workdir) == str(GROK_CLOUD_WORKDIR) or (
        GROK_CLOUD_WORKDIR.is_dir() and workdir == GROK_CLOUD_WORKDIR.resolve()
    ):
        return "grok_ios_cloud"
    skills = get_skills_root()
    if skills.name == "skills" and skills.parent.name == ".grok":
        ws = skills.parent.parent
        if (ws / ".git").exists() or (ws / "pyproject.toml").exists():
            return "grok_build_repo"
        if skills.parent == get_grok_home():
            return "grok_global_user"
    return "local"


def _campaign_candidate_from_host(host: Path, *, artifacts_subdir: bool = True) -> Path:
    if artifacts_subdir:
        return host.expanduser().resolve() / "artifacts" / "dnd-campaigns"
    return host.expanduser().resolve() / "dnd-campaigns"


def get_campaigns_root(*, create: bool = False) -> Path:
    """Resolve the root directory for all campaign state.

    Priority:
    1. DND_CAMPAIGNS_ROOT
    2. GROK_CAMPAIGNS_ROOT
    3. GROK_ARTIFACTS_ROOT/dnd-campaigns
    4. GROK_WORKSPACE_ROOT/artifacts/dnd-campaigns
    5. GROK_USER_DATA/artifacts/dnd-campaigns
    6. GROK_HOME/artifacts/dnd-campaigns
    7. Grok cloud /home/workdir/artifacts/dnd-campaigns
    8. Existing local candidates (~/.grok, Library, Documents, cwd)
    9. Default: grok_home/artifacts/dnd-campaigns (created on demand)
    """
    env_root = os.environ.get("DND_CAMPAIGNS_ROOT")
    if env_root:
        root = Path(env_root).expanduser().resolve()
        if create:
            ensure_dir(root)
        return root

    explicit = os.environ.get("GROK_CAMPAIGNS_ROOT")
    if explicit:
        root = Path(explicit).expanduser().resolve()
        if create:
            ensure_dir(root)
        return root

    artifacts_root = os.environ.get("GROK_ARTIFACTS_ROOT")
    if artifacts_root:
        root = _campaign_candidate_from_host(Path(artifacts_root), artifacts_subdir=False)
        if create:
            ensure_dir(root)
        return root

    ws_env = os.environ.get("GROK_WORKSPACE_ROOT") or os.environ.get("GROK_WORKDIR")
    if ws_env:
        root = _campaign_candidate_from_host(Path(ws_env))
        if create:
            ensure_dir(root)
        return root

    for key in ("GROK_USER_DATA", "GROK_HOME"):
        host_root = os.environ.get(key)
        if host_root:
            root = _campaign_candidate_from_host(Path(host_root))
            if create:
                ensure_dir(root)
            return root

    cloud = GROK_CLOUD_WORKDIR / "artifacts" / "dnd-campaigns"
    if GROK_CLOUD_WORKDIR.is_dir():
        if create:
            ensure_dir(cloud)
        return cloud.resolve()

    home = Path.home()
    grok_home = get_grok_home()
    local_candidates: List[Path] = [
        grok_home / "artifacts" / "dnd-campaigns",
        home / ".grok" / "artifacts" / "dnd-campaigns",
        home / "Library" / "Application Support" / "Grok" / "artifacts" / "dnd-campaigns",
        home / "Documents" / "Grok" / "artifacts" / "dnd-campaigns",
        home / "artifacts" / "dnd-campaigns",
        get_workspace_root() / "artifacts" / "dnd-campaigns",
        Path.cwd() / "artifacts" / "dnd-campaigns",
    ]
    for candidate in local_candidates:
        if candidate.exists():
            return candidate.resolve()

    default = (grok_home / "artifacts" / "dnd-campaigns").resolve()
    if create:
        ensure_dir(default)
    return default


def get_campaign_path(campaign_name: str) -> Path:
    """Return the filesystem path for a named campaign."""
    safe_name = campaign_name.strip()
    if not safe_name:
        raise ValueError("Campaign name cannot be empty")
    return get_campaigns_root() / safe_name


def resolve_skill_script(script_rel: str) -> Path:
    """Absolute path to a skill script (e.g. dnd-utils/scripts/dnd_state_utils.py)."""
    rel = script_rel.replace("\\", "/").lstrip("/")
    if rel.startswith(".grok/skills/"):
        rel = rel[len(".grok/skills/") :]
    return (get_skills_root() / rel).resolve()


def format_python_cli(script_rel: str, *args: str) -> str:
    """Portable CLI hint: repo-relative when workspace contains .grok/skills, else absolute."""
    script = resolve_skill_script(script_rel)
    workspace = get_workspace_root()
    try:
        rel = script.relative_to(workspace)
        rel_posix = rel.as_posix()
        if rel_posix.startswith(".grok/"):
            parts = ["python", rel_posix, *args]
            return " ".join(parts)
    except ValueError:
        pass
    quoted = [sys.executable, str(script), *args]
    return " ".join(quoted)


def python_cli_argv(script_rel: str, *args: str) -> List[str]:
    """Argv list for subprocess — always uses absolute script path."""
    return [sys.executable, str(resolve_skill_script(script_rel)), *list(args)]


def get_runtime_context() -> Dict[str, Any]:
    """Diagnostic snapshot for Grok iOS / PC parity checks."""
    skills = get_skills_root()
    grok_home = get_grok_home()
    workspace = get_workspace_root()
    campaigns = get_campaigns_root()
    return {
        "paths_version": PATHS_VERSION,
        "platform": detect_runtime_platform(),
        "skills_root": str(skills),
        "grok_home": str(grok_home),
        "workspace_root": str(workspace),
        "campaigns_root": str(campaigns),
        "campaigns_root_exists": campaigns.exists(),
        "skills_layout": "repo" if (workspace / ".grok" / "skills").exists() else "global_or_cloud",
        "env": {
            k: os.environ[k]
            for k in (
                "DND_CAMPAIGNS_ROOT",
                "GROK_CAMPAIGNS_ROOT",
                "GROK_ARTIFACTS_ROOT",
                "GROK_USER_DATA",
                "GROK_HOME",
                "GROK_SKILLS_ROOT",
                "GROK_WORKSPACE_ROOT",
                "GROK_WORKDIR",
                "CLAUDE_PROJECT_DIR",
            )
            if os.environ.get(k)
        },
    }


def ensure_dir(path: Path) -> Path:
    """Create a directory (and parents) if missing."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def backup_file(path: Path, *, backup_dir: Optional[Path] = None) -> Optional[Path]:
    """Copy an existing file into the campaign backups folder."""
    if not path.exists():
        return None
    target_dir = backup_dir or (path.parent.parent / "backups")
    ensure_dir(target_dir)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = target_dir / f"{path.stem}_{stamp}{path.suffix}"
    shutil.copy2(path, dest)
    return dest