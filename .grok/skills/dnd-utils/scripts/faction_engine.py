"""Faction simulation — goals, influence ticks, diplomacy graph, turn advancement."""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from dnd_state_utils import get_kingdom_state, update_kingdom_state
from event_system import record_event

FACTION_ENGINE_VERSION = "4.0.0"

GOAL_TEMPLATES = [
    "expand_trade",
    "secure_borders",
    "undermine_rival",
    "seek_alliance",
    "recover_artifact",
    "increase_influence",
]


def _normalize_faction(faction: Dict[str, Any]) -> Dict[str, Any]:
    faction.setdefault("influence", 0)
    faction.setdefault("attitude", "neutral")
    faction.setdefault("goals", [])
    faction.setdefault("relations", {})
    faction.setdefault("memory", [])
    return faction


def set_faction_goal(campaign_name: str, faction_name: str, goal: str) -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    factions = kingdom.setdefault("factions", {})
    fac = _normalize_faction(factions.setdefault(faction_name, {"name": faction_name}))
    if goal not in fac["goals"]:
        fac["goals"].append(goal)
    factions[faction_name] = fac
    update_kingdom_state(campaign_name, {"factions": factions})
    record_event(campaign_name, f"{faction_name} adopts goal: {goal}", tags=["faction", "goal"])
    return {"faction": faction_name, "goals": fac["goals"]}


def set_faction_relation(
    campaign_name: str, faction_a: str, faction_b: str, score: int
) -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    factions = kingdom.setdefault("factions", {})
    for name in (faction_a, faction_b):
        _normalize_faction(factions.setdefault(name, {"name": name}))
    factions[faction_a].setdefault("relations", {})[faction_b] = max(-100, min(100, score))
    factions[faction_b].setdefault("relations", {})[faction_a] = max(-100, min(100, score))
    update_kingdom_state(campaign_name, {"factions": factions})
    return {"faction_a": faction_a, "faction_b": faction_b, "score": score}


def diplomacy_graph(campaign_name: str) -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    factions = kingdom.get("factions", {})
    nodes, edges = [], []
    for name, data in factions.items():
        nodes.append({
            "id": name,
            "influence": data.get("influence", 0),
            "attitude": data.get("attitude", "neutral"),
            "goals": data.get("goals", []),
        })
        for other, score in data.get("relations", {}).items():
            if name < other:
                edges.append({"from": name, "to": other, "score": score})
    return {"nodes": nodes, "edges": edges, "version": FACTION_ENGINE_VERSION}


def simulate_faction_round(campaign_name: str, *, seed: Optional[int] = None) -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    factions = kingdom.get("factions", {})
    if not factions:
        return {"ticks": 0, "events": [], "message": "No factions in kingdom state"}

    rng = random.Random(seed)
    events: List[str] = []
    for name, fac in factions.items():
        fac = _normalize_faction(fac)
        delta = rng.randint(-2, 3) + (1 if fac.get("goals") else 0)
        fac["influence"] = max(0, min(100, fac.get("influence", 0) + delta))
        if fac["goals"] and rng.random() < 0.4:
            goal = rng.choice(fac["goals"])
            evt = f"{name} advances toward '{goal}' (influence now {fac['influence']})"
            events.append(evt)
            fac.setdefault("memory", []).append({"event": evt, "at": datetime.now().isoformat()})
            fac["memory"] = fac["memory"][-20:]
        factions[name] = fac

    update_kingdom_state(campaign_name, {"factions": factions})
    for evt in events:
        record_event(campaign_name, evt, tags=["faction", "simulation"])

    return {
        "ticks": len(factions),
        "events": events,
        "factions": {n: f.get("influence") for n, f in factions.items()},
        "version": FACTION_ENGINE_VERSION,
    }


def auto_seed_faction_goals(campaign_name: str) -> Dict[str, Any]:
    kingdom = get_kingdom_state(campaign_name)
    seeded = []
    for name in kingdom.get("factions", {}):
        goal = random.choice(GOAL_TEMPLATES)
        set_faction_goal(campaign_name, name, goal)
        seeded.append({"faction": name, "goal": goal})
    return {"seeded": seeded}