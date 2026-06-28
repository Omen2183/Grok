"""Per-campaign homebrew rules storage."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"))
from dnd_state_utils import load_json, save_json  # noqa: E402
from paths import get_campaign_path  # noqa: E402


def _path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "homebrew_rules.json"


def load_homebrew(campaign_name: str) -> Dict[str, Any]:
    return load_json(_path(campaign_name), {"rules": [], "updated": None})


def add_rule(
    campaign_name: str,
    topic: str,
    ruling: str,
    *,
    source: str = "table",
) -> Dict[str, Any]:
    data = load_homebrew(campaign_name)
    entry = {
        "topic": topic.strip().lower(),
        "ruling": ruling.strip(),
        "source": source,
        "added": datetime.now().isoformat(),
    }
    rules: List[Dict[str, Any]] = data.setdefault("rules", [])
    rules = [r for r in rules if r.get("topic") != entry["topic"]]
    rules.append(entry)
    data["rules"] = rules
    data["updated"] = datetime.now().isoformat()
    save_json(_path(campaign_name), data)
    return entry


def list_rules(campaign_name: str, *, topic: Optional[str] = None) -> Dict[str, Any]:
    data = load_homebrew(campaign_name)
    rules = data.get("rules", [])
    if topic:
        needle = topic.strip().lower()
        rules = [r for r in rules if needle in r.get("topic", "") or needle in r.get("ruling", "").lower()]
    return {"campaign": campaign_name, "count": len(rules), "rules": rules}


def lookup_homebrew_first(campaign_name: str, topic: str) -> Optional[Dict[str, Any]]:
    data = load_homebrew(campaign_name)
    key = topic.strip().lower().replace(" ", "_")
    for rule in data.get("rules", []):
        if key in rule.get("topic", "") or key in rule.get("ruling", "").lower():
            return {"found": True, "source": "homebrew", **rule}
    return None