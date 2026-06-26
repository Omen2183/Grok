"""Core weighted table engine with campaign ledger."""

from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from paths import get_campaign_path

from randomizer_data import BUILTIN_TABLES, RANDOMIZER_DATA_VERSION

ENGINE_VERSION = "4.2.0"


def _ledger_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "randomizer_ledger.json"


def _custom_tables_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "state" / "custom_random_tables.json"


def load_ledger(campaign_name: str) -> Dict[str, Any]:
    path = _ledger_path(campaign_name)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"entries": [], "version": ENGINE_VERSION}


def save_ledger(campaign_name: str, data: Dict[str, Any]) -> None:
    path = _ledger_path(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_custom_tables(campaign_name: str) -> Dict[str, List[Dict[str, Any]]]:
    path = _custom_tables_path(campaign_name)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_custom_tables(campaign_name: str, tables: Dict[str, List[Dict[str, Any]]]) -> None:
    path = _custom_tables_path(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tables, indent=2), encoding="utf-8")


def list_tables(campaign_name: Optional[str] = None) -> Dict[str, Any]:
    builtin = sorted(BUILTIN_TABLES.keys())
    custom = sorted(load_custom_tables(campaign_name).keys()) if campaign_name else []
    return {"builtin": builtin, "custom": custom, "version": ENGINE_VERSION}


def weighted_pick(
    table: List[Dict[str, Any]],
    *,
    rng: random.Random,
    avoid: Optional[set] = None,
) -> Dict[str, Any]:
    avoid = avoid or set()
    candidates = [e for e in table if e.get("name") not in avoid]
    if not candidates:
        candidates = table
    total = sum(e.get("weight", 1) for e in candidates)
    roll = rng.uniform(0, total)
    cumulative = 0.0
    for entry in candidates:
        cumulative += entry.get("weight", 1)
        if roll <= cumulative:
            return dict(entry)
    return dict(candidates[-1])


def roll_table(
    table_name: str,
    *,
    campaign_name: Optional[str] = None,
    count: int = 1,
    seed: Optional[int] = None,
    use_ledger: bool = True,
) -> Dict[str, Any]:
    tables = dict(BUILTIN_TABLES)
    if campaign_name:
        tables.update(load_custom_tables(campaign_name))
    if table_name not in tables:
        return {
            "error": f"Unknown table: {table_name}",
            "available": sorted(tables.keys()),
        }

    rng = random.Random(seed)
    avoid: set = set()
    if campaign_name and use_ledger:
        ledger = load_ledger(campaign_name)
        avoid = {e.get("result") for e in ledger.get("entries", []) if e.get("table") == table_name}

    results = []
    for _ in range(count):
        pick = weighted_pick(tables[table_name], rng=rng, avoid=avoid)
        results.append(pick)
        avoid.add(pick.get("name", ""))
        if campaign_name and use_ledger:
            ledger = load_ledger(campaign_name)
            ledger.setdefault("entries", []).append({
                "table": table_name,
                "result": pick.get("name"),
                "at": datetime.now().isoformat(),
            })
            ledger["entries"] = ledger["entries"][-500:]
            save_ledger(campaign_name, ledger)

    return {
        "table": table_name,
        "count": len(results),
        "results": results,
        "seed": seed,
        "version": ENGINE_VERSION,
    }


def add_custom_entry(
    campaign_name: str,
    table_name: str,
    name: str,
    *,
    weight: int = 1,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    tables = load_custom_tables(campaign_name)
    entry = {"name": name, "weight": weight, **(extra or {})}
    tables.setdefault(table_name, []).append(entry)
    save_custom_tables(campaign_name, tables)
    return {"table": table_name, "added": entry}


def ledger_summary(campaign_name: str, *, limit: int = 20) -> Dict[str, Any]:
    data = load_ledger(campaign_name)
    entries = data.get("entries", [])
    return {
        "total": len(entries),
        "recent": entries[-limit:],
        "version": ENGINE_VERSION,
    }