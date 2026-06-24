"""Cross-platform path resolution for D&D campaign artifacts."""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_campaigns_root() -> Path:
    """Resolve the root directory for all campaign state.

    Priority:
    1. DND_CAMPAIGNS_ROOT environment variable
    2. Grok cloud workdir layout
    3. Local Grok Build user directory
    4. ./artifacts/dnd-campaigns relative to cwd
    """
    env_root = os.environ.get("DND_CAMPAIGNS_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    cloud = Path("/home/workdir/artifacts/dnd-campaigns")
    if cloud.parent.exists():
        return cloud

    home = Path.home()
    local_candidates = [
        home / ".grok" / "artifacts" / "dnd-campaigns",
        home / "artifacts" / "dnd-campaigns",
        Path.cwd() / "artifacts" / "dnd-campaigns",
    ]
    for candidate in local_candidates:
        if candidate.exists():
            return candidate.resolve()

    return (home / ".grok" / "artifacts" / "dnd-campaigns").resolve()


def get_campaign_path(campaign_name: str) -> Path:
    """Return the filesystem path for a named campaign."""
    safe_name = campaign_name.strip()
    if not safe_name:
        raise ValueError("Campaign name cannot be empty")
    return get_campaigns_root() / safe_name


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