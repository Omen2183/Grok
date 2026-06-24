"""Lightweight kingdom simulation helpers."""

from __future__ import annotations

from typing import Any, Dict, List

from dnd_state_utils import get_kingdom_state, update_kingdom_state
from event_system import record_event


def simple_population_update(campaign_name: str, delta: int, *, reason: str = "") -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    if not kingdom.get("flags", {}).get("population_tracking", False):
        kingdom.setdefault("flags", {})["population_tracking"] = True
    pop = kingdom.setdefault("population", 1000)
    kingdom["population"] = max(0, pop + delta)
    update_kingdom_state(campaign_name, kingdom)
    if reason:
        record_event(campaign_name, f"Population {delta:+d}: {reason}", tags=["kingdom", "population"])
    return {"population": kingdom["population"], "delta": delta}


def process_trade_flows(campaign_name: str) -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    resources = kingdom.setdefault("resources", {})
    gold_delta = 10 if kingdom.get("flags", {}).get("trade_flows", False) else 5
    resources["gold"] = resources.get("gold", 0) + gold_delta
    update_kingdom_state(campaign_name, {"resources": resources})
    record_event(campaign_name, f"Trade income +{gold_delta} gold", tags=["kingdom", "trade"])
    return {"gold_gained": gold_delta, "resources": resources}


def update_military_units(campaign_name: str, delta: int, *, unit_type: str = "militia") -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    military = kingdom.setdefault("military", {})
    military[unit_type] = max(0, military.get(unit_type, 0) + delta)
    update_kingdom_state(campaign_name, {"military": military})
    return {"military": military}


def apply_cascading_consequences(campaign_name: str, completed_project: str) -> List[str]:
    kingdom = get_kingdom_state(campaign_name)
    effects: List[str] = []
    name_lower = completed_project.lower()
    if "watchtower" in name_lower or "watch" in name_lower:
        effects.append("Bandit activity reduced along nearby roads")
        factions = kingdom.setdefault("factions", {})
        factions.setdefault("locals", {"influence": 5, "attitude": "grateful"})
        factions["locals"]["influence"] = factions["locals"].get("influence", 0) + 2
        update_kingdom_state(campaign_name, {"factions": factions})
    if "granary" in name_lower or "farm" in name_lower:
        resources = kingdom.setdefault("resources", {})
        resources["food"] = resources.get("food", 0) + 20
        update_kingdom_state(campaign_name, {"resources": resources})
        effects.append("Food stores increased from harvest surplus")
    if effects:
        record_event(
            campaign_name,
            f"Cascading effects from {completed_project}: {'; '.join(effects)}",
            tags=["kingdom", "consequence"],
        )
    return effects


def generate_domain_event_chain(campaign_name: str, seed: str) -> List[str]:
    kingdom = get_kingdom_state(campaign_name)
    domain = kingdom.get("domain_name", "the realm")
    return [
        f"Rumors spread in {domain} about {seed}",
        f"A minor faction reacts to news of {seed}",
        f"Trade prices shift slightly due to {seed}",
    ]