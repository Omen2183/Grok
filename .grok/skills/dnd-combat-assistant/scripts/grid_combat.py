#!/usr/bin/env python3
"""Tactical grid combat — positions, movement, distance, AoE, cover hints."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"))

from bootstrap import ensure_utils_importable

ensure_utils_importable()

from paths import get_campaign_path  # noqa: E402

GRID_COMBAT_VERSION = "4.0.0"


def _combat_path(campaign_name: str) -> Path:
    return get_campaign_path(campaign_name) / "combat" / "current_combat.json"


def _load_combat(campaign_name: str) -> Dict[str, Any]:
    path = _combat_path(campaign_name)
    if not path.exists():
        return {"combatants": [], "grid": None}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_combat(campaign_name: str, data: Dict[str, Any]) -> None:
    path = _combat_path(campaign_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def init_grid(
    campaign_name: str,
    *,
    width: int = 20,
    height: int = 20,
    cell_size_ft: int = 5,
    terrain: str = "open",
) -> Dict[str, Any]:
    data = _load_combat(campaign_name)
    data["grid"] = {
        "width": width,
        "height": height,
        "cell_size_ft": cell_size_ft,
        "terrain": terrain,
        "tokens": {},
        "obstacles": [],
        "version": GRID_COMBAT_VERSION,
    }
    _save_combat(campaign_name, data)
    return data["grid"]


def _get_grid(data: Dict[str, Any]) -> Dict[str, Any]:
    grid = data.get("grid")
    if not grid:
        raise ValueError("No grid initialized — run init-grid first")
    return grid


def place_token(
    campaign_name: str,
    name: str,
    x: int,
    y: int,
    *,
    size: str = "medium",
) -> Dict[str, Any]:
    data = _load_combat(campaign_name)
    grid = _get_grid(data)
    w, h = grid["width"], grid["height"]
    if not (0 <= x < w and 0 <= y < h):
        raise ValueError(f"Position ({x},{y}) outside grid {w}x{h}")
    grid["tokens"][name.lower()] = {"name": name, "x": x, "y": y, "size": size}
    _save_combat(campaign_name, data)
    return grid["tokens"][name.lower()]


def move_token(
    campaign_name: str,
    name: str,
    x: int,
    y: int,
    *,
    speed_ft: Optional[int] = None,
) -> Dict[str, Any]:
    data = _load_combat(campaign_name)
    grid = _get_grid(data)
    key = name.lower()
    if key not in grid["tokens"]:
        raise ValueError(f"Token not on grid: {name}")
    token = grid["tokens"][key]
    old_x, old_y = token["x"], token["y"]
    cell_ft = grid.get("cell_size_ft", 5)
    distance_ft = int(math.hypot(x - old_x, y - old_y) * cell_ft)
    if speed_ft is not None and distance_ft > speed_ft:
        return {
            "moved": False,
            "reason": f"Distance {distance_ft} ft exceeds speed {speed_ft} ft",
            "from": (old_x, old_y),
            "to": (x, y),
            "distance_ft": distance_ft,
        }
    token["x"], token["y"] = x, y
    _save_combat(campaign_name, data)
    return {
        "moved": True,
        "token": token,
        "from": (old_x, old_y),
        "to": (x, y),
        "distance_ft": distance_ft,
    }


def grid_distance(campaign_name: str, a: str, b: str) -> Dict[str, Any]:
    data = _load_combat(campaign_name)
    grid = _get_grid(data)
    ta = grid["tokens"].get(a.lower())
    tb = grid["tokens"].get(b.lower())
    if not ta or not tb:
        raise ValueError("Both tokens must be placed on the grid")
    cell_ft = grid.get("cell_size_ft", 5)
    squares = math.hypot(tb["x"] - ta["x"], tb["y"] - ta["y"])
    feet = int(squares * cell_ft)
    return {
        "from": a,
        "to": b,
        "squares": round(squares, 1),
        "feet": feet,
        "melee_range": feet <= 5,
    }


def tokens_in_radius(
    campaign_name: str,
    center_x: int,
    center_y: int,
    radius_ft: int,
) -> Dict[str, Any]:
    data = _load_combat(campaign_name)
    grid = _get_grid(data)
    cell_ft = grid.get("cell_size_ft", 5)
    radius_squares = radius_ft / cell_ft
    hits: List[Dict[str, Any]] = []
    for token in grid["tokens"].values():
        dist = math.hypot(token["x"] - center_x, token["y"] - center_y)
        if dist <= radius_squares:
            hits.append({**token, "distance_squares": round(dist, 1)})
    return {
        "center": (center_x, center_y),
        "radius_ft": radius_ft,
        "affected": hits,
        "count": len(hits),
    }


def add_obstacle(
    campaign_name: str,
    x: int,
    y: int,
    *,
    cover: str = "half",
    label: str = "",
) -> Dict[str, Any]:
    data = _load_combat(campaign_name)
    grid = _get_grid(data)
    obs = {"x": x, "y": y, "cover": cover, "label": label}
    grid.setdefault("obstacles", []).append(obs)
    _save_combat(campaign_name, data)
    return obs


def grid_summary(campaign_name: str) -> Dict[str, Any]:
    data = _load_combat(campaign_name)
    grid = data.get("grid")
    if not grid:
        return {"has_grid": False, "message": "No tactical grid active"}
    tokens = list(grid.get("tokens", {}).values())
    lines = [
        f"Grid {grid['width']}x{grid['height']} ({grid.get('cell_size_ft', 5)} ft/square)",
        f"Terrain: {grid.get('terrain', 'open')}",
        f"Tokens: {len(tokens)}",
    ]
    for t in tokens:
        lines.append(f"  • {t['name']} @ ({t['x']},{t['y']})")
    return {
        "has_grid": True,
        "summary": "\n".join(lines),
        "grid": grid,
        "encounter": data.get("encounter_name", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Tactical grid combat")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init-grid")
    p_init.add_argument("campaign")
    p_init.add_argument("--width", type=int, default=20)
    p_init.add_argument("--height", type=int, default=20)
    p_init.add_argument("--cell-ft", type=int, default=5)
    p_init.add_argument("--terrain", default="open")

    p_place = sub.add_parser("place")
    p_place.add_argument("campaign")
    p_place.add_argument("name")
    p_place.add_argument("x", type=int)
    p_place.add_argument("y", type=int)
    p_place.add_argument("--size", default="medium")

    p_move = sub.add_parser("move")
    p_move.add_argument("campaign")
    p_move.add_argument("name")
    p_move.add_argument("x", type=int)
    p_move.add_argument("y", type=int)
    p_move.add_argument("--speed", type=int)

    p_dist = sub.add_parser("distance")
    p_dist.add_argument("campaign")
    p_dist.add_argument("token_a")
    p_dist.add_argument("token_b")

    p_aoe = sub.add_parser("aoe")
    p_aoe.add_argument("campaign")
    p_aoe.add_argument("x", type=int)
    p_aoe.add_argument("y", type=int)
    p_aoe.add_argument("radius", type=int, help="Radius in feet")

    p_obs = sub.add_parser("add-obstacle")
    p_obs.add_argument("campaign")
    p_obs.add_argument("x", type=int)
    p_obs.add_argument("y", type=int)
    p_obs.add_argument("--cover", default="half")
    p_obs.add_argument("--label", default="")

    p_sum = sub.add_parser("summary")
    p_sum.add_argument("campaign")

    args = parser.parse_args()
    if args.cmd == "init-grid":
        result = init_grid(
            args.campaign,
            width=args.width,
            height=args.height,
            cell_size_ft=args.cell_ft,
            terrain=args.terrain,
        )
    elif args.cmd == "place":
        result = place_token(args.campaign, args.name, args.x, args.y, size=args.size)
    elif args.cmd == "move":
        result = move_token(args.campaign, args.name, args.x, args.y, speed_ft=args.speed)
    elif args.cmd == "distance":
        result = grid_distance(args.campaign, args.token_a, args.token_b)
    elif args.cmd == "aoe":
        result = tokens_in_radius(args.campaign, args.x, args.y, args.radius)
    elif args.cmd == "add-obstacle":
        result = add_obstacle(args.campaign, args.x, args.y, cover=args.cover, label=args.label)
    elif args.cmd == "summary":
        result = grid_summary(args.campaign)
    else:
        result = {"error": "unknown command"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()