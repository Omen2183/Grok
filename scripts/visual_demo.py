#!/usr/bin/env python3
"""Full visual walkthrough of the D&D skills suite — readable live demo output."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".grok" / "skills"
PY = sys.executable

# ANSI (Windows 10+ supports in modern terminals)
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
DIM = "\033[2m"
RESET = "\033[0m"


def banner(title: str, subtitle: str = "") -> None:
    width = 72
    print()
    print(f"{CYAN}{'═' * width}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    if subtitle:
        print(f"{DIM}  {subtitle}{RESET}")
    print(f"{CYAN}{'═' * width}{RESET}")
    print()


def step(n: int, total: int, label: str) -> None:
    print(f"{BOLD}{YELLOW}[{n}/{total}]{RESET} {label}")
    print(f"{DIM}{'─' * 60}{RESET}")


def pause_ms(ms: int = 400) -> None:
    time.sleep(ms / 1000)


def run_json(cmd: list[str], env: dict) -> dict[str, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=REPO)
    if proc.returncode != 0:
        print(f"{YELLOW}FAILED:{RESET} {' '.join(cmd[-4:])}")
        print(proc.stderr or proc.stdout)
        raise RuntimeError("demo step failed")
    raw = proc.stdout.strip()
    if not raw:
        return {"status": "ok"}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw[:500]}


def pick(data: dict[str, Any], *keys: str, default: str = "—") -> str:
    for k in keys:
        if k in data and data[k] not in (None, "", []):
            v = data[k]
            if isinstance(v, (dict, list)):
                return json.dumps(v)[:120]
            return str(v)[:200]
    return default


def show_kv(rows: list[tuple[str, str]]) -> None:
    w = max(len(k) for k, _ in rows) if rows else 0
    for k, v in rows:
        print(f"  {DIM}{k:<{w}}{RESET}  {GREEN}{v}{RESET}")
    print()


def main() -> int:
    campaign = "Visual Demo Campaign"
    total_steps = 18

    banner(
        "GROK D&D SKILLS SUITE — LIVE VISUAL DEMO",
        "v5.3.0 · 18 skills · 16 playbooks · watch each layer execute",
    )

    # Suite gate
    step(1, total_steps, "Production gate (suite_score)")
    score_proc = subprocess.run([PY, str(REPO / "scripts/suite_score.py")], capture_output=True, text=True, cwd=REPO)
    score = json.loads(score_proc.stdout)
    show_kv([
        ("Grade", score.get("grade", "?")),
        ("Score", f"{score.get('score')}/10"),
        ("Skills", str(score.get("skills_count"))),
        ("Pytest", str(score["dimensions"][-2]["evidence"]["pytest"]["passed"]) + " passed"),
    ])
    pause_ms(600)

    with tempfile.TemporaryDirectory() as tmp:
        env = {**dict(__import__("os").environ), "DND_CAMPAIGNS_ROOT": tmp}

        # Pre-session
        step(2, total_steps, "Playbook: pre-session (health → resume → quests)")
        health = run_json(
            [PY, str(SKILLS / "dnd-utils/scripts/narration_cli.py"), "campaign-health", campaign],
            env,
        )
        run_json([PY, str(SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "init", campaign, "--pc-name", "Aria", "--enable-sqlite"], env)
        resume = run_json([PY, str(SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "resume", campaign], env)
        show_kv([
            ("Health", pick(health, "health", "voice_summary")),
            ("Location", pick(resume, "location", default=pick(resume, "world_state", "location"))),
            ("Mode", pick(resume, "mode", default="tabletop")),
        ])
        pause_ms(500)

        # Voice route
        step(3, total_steps, "Voice: parse + route damage phrase")
        route = run_json(
            [PY, str(SKILLS / "dnd-voice-assistant/scripts/voice_utils.py"), "route", campaign, "Goblin takes 8 damage"],
            env,
        )
        show_kv([
            ("Intent", pick(route, "intent")),
            ("Primary skill", pick(route, "primary_skill")),
            ("Target", pick(route, "parsed", "target", default="Goblin")),
        ])
        pause_ms(400)

        # Combat
        step(4, total_steps, "Playbook: party-to-combat (party → seed → encounter)")
        pb = run_json(
            [PY, str(SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "playbook", campaign, "party-to-combat"],
            env,
        )
        show_kv([("Playbook", "party-to-combat"), ("Steps run", str(len(pb.get("steps", pb.get("results", [])))))])
        pause_ms(500)

        step(5, total_steps, "Combat: add goblin with auto-initiative + damage")
        run_json([PY, str(SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"), "init", campaign, "--encounter", "Goblin Ambush"], env)
        add = run_json(
            [PY, str(SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"), "add", campaign,
             "--name", "Goblin", "--hp", "7", "--auto-initiative", "--cr", "0.25"],
            env,
        )
        roll = run_json([PY, str(SKILLS / "dnd-dice-engine/scripts/dice_roller.py"), "roll", "1d20+5", "--campaign", campaign], env)
        dmg = run_json(
            [PY, str(SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"), "damage", campaign, "--target", "Goblin", "--amount", "7"],
            env,
        )
        summary = run_json(
            [PY, str(SKILLS / "dnd-combat-assistant/scripts/combat_tracker.py"), "summary", campaign, "--dm-screen"],
            env,
        )
        init_val = add.get("combatants", [{}])[0].get("initiative", "?") if add.get("combatants") else "?"
        show_kv([
            ("Goblin initiative", str(init_val)),
            ("Attack roll", pick(roll, "total", "result", default=pick(roll, "notation"))),
            ("Goblin HP after hit", pick(dmg, "target_hp", "hp", default="0")),
            ("DM screen", (summary.get("summary") or summary.get("raw", "ok"))[:80]),
        ])
        pause_ms(600)

        # Grid + visual
        step(6, total_steps, "Grid combat + visual-weaver map prompt")
        run_json([PY, str(SKILLS / "dnd-combat-assistant/scripts/grid_combat.py"), "init-grid", campaign, "--width", "12", "--height", "12"], env)
        visual = run_json(
            [PY, str(SKILLS / "dnd-visual-weaver/scripts/visual_prompt_library.py"), "weave-prompt", campaign, "forest ambush at dusk"],
            env,
        )
        show_kv([("Image prompt", (visual.get("prompt") or visual.get("weave", str(visual)))[:100])])
        pause_ms(400)

        # World layer
        step(7, total_steps, "Content, loot, NPC, lore, rumors")
        quest = run_json([PY, str(SKILLS / "dnd-content-forge/scripts/content_forge.py"), "quest", campaign, "--theme", "sealed mine"], env)
        loot = run_json([PY, str(SKILLS / "dnd-loot-generator/scripts/procedural_loot.py"), "generate", campaign], env)
        npc = run_json([PY, str(SKILLS / "dnd-npc-personality-weaver/scripts/npc_manager.py"), "create", campaign, "--name", "Elder Mara"], env)
        rumors = run_json([PY, str(SKILLS / "dnd-rumor-event-generator/scripts/rumor_generator.py"), "rumors", campaign, "--count", "2"], env)
        show_kv([
            ("Quest hook", pick(quest, "title", "hook", default=pick(quest, "summary"))),
            ("Loot", pick(loot, "item", "description", default=pick(loot, "loot"))),
            ("NPC", pick(npc, "name", default="Elder Mara")),
            ("Rumor", str((rumors.get("rumors") or rumors.get("events") or ["—"])[0])[:80]),
        ])
        pause_ms(500)

        # Rules + randomizer
        step(8, total_steps, "Rules lookup + randomizer party snippet")
        rule = run_json([PY, str(SKILLS / "dnd-rules-reference/scripts/rules_cheatsheet.py"), "lookup", "advantage"], env)
        party = run_json(
            [PY, str(SKILLS / "dnd-randomizer/scripts/randomizer.py"), "random-party", "--size", "3", "--level", "2", "--seed", "42"],
            env,
        )
        party_line = pick(party, "summary", default=str(party.get("party", party)))[:90]
        show_kv([
            ("Advantage ruling", (rule.get("ruling") or rule.get("summary") or str(rule))[:90]),
            ("Random party", party_line),
        ])
        pause_ms(400)

        # Character + downtime
        step(9, total_steps, "Character sheet + long rest")
        char = run_json([PY, str(SKILLS / "dnd-character-manager/scripts/character_manager.py"), "summary", campaign], env)
        rest = run_json([PY, str(SKILLS / "dnd-downtime-manager/scripts/downtime_manager.py"), "long-rest", campaign], env)
        show_kv([
            ("PC", pick(char, "name", default="Aria")),
            ("HP", pick(char, "hp", "current_hp", default=pick(char, "hit_points"))),
            ("Long rest", pick(rest, "status", default="complete")),
        ])
        pause_ms(400)

        # Session end with sync-quests
        step(10, total_steps, "Playbook: session-end (auto-recap → sync-quests → end → list)")
        run_json([PY, str(SKILLS / "dnd-quest-tracker/scripts/quest_tracker.py"), "add-hook", campaign, "quest: Investigate the sealed mine"], env)
        end_pb = run_json(
            [PY, str(SKILLS / "dnd-persistent-dm/scripts/persistent_dm.py"), "playbook", campaign, "session-end"],
            env,
        )
        quests = run_json([PY, str(SKILLS / "dnd-quest-tracker/scripts/quest_tracker.py"), "list", campaign], env)
        hooks = quests.get("hooks", [])
        active = quests.get("active_quests", quests.get("quests", []))
        show_kv([
            ("Session-end steps", str(len(end_pb.get("steps", end_pb.get("results", []))))),
            ("Active quests", str(len(active) if isinstance(active, list) else 0)),
            ("Hooks", str(len(hooks) if isinstance(hooks, list) else 0)),
        ])
        pause_ms(600)

        # Dashboard finale
        step(11, total_steps, "Campaign dashboard + mobile status")
        dash = run_json([PY, str(SKILLS / "dnd-utils/scripts/dnd_state_utils.py"), "dashboard", campaign], env)
        mobile = run_json([PY, str(SKILLS / "dnd-utils/scripts/narration_cli.py"), "mobile-status", campaign], env)
        show_kv([
            ("Dashboard", pick(dash, "status", default="ok")),
            ("Mobile line", pick(mobile, "status_line", "summary", default=str(mobile)[:80])),
        ])

    banner("DEMO COMPLETE", f"{GREEN}All visual demo phases passed{RESET} · suite ready for play")
    print(f"  {DIM}Re-run: python scripts/visual_demo.py{RESET}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())