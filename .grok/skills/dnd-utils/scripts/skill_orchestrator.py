#!/usr/bin/env python3
"""Execute cross-skill delegations and enrich routes with actionable CLI plans."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from bootstrap import ensure_utils_importable

ensure_utils_importable()

from paths import get_workspace_root, python_cli_argv  # noqa: E402
from skill_registry import (  # noqa: E402
    PLAYBOOKS,
    SKILLS,
    SKILLS_ROOT,
    get_playbook,
    resolve_intent,
    script_path,
)

ORCHESTRATOR_VERSION = "5.1.1"


def enrich_route(campaign: str, route: Dict[str, Any]) -> Dict[str, Any]:
    """Add delegation plan and example commands to a voice/persistent-dm route."""
    intent = route.get("intent", "narrative")
    context = {k: route[k] for k in ("damage", "healing") if k in route}
    plan = resolve_intent(intent, campaign=campaign, context=context)
    enriched = {**route, "delegation": plan}
    enriched["orchestrator"] = "dnd-persistent-dm"
    enriched["read_state_first"] = ["dnd-utils status", "dnd-utils load world_state"]
    if plan.get("confirm") or route.get("needs_confirmation"):
        enriched["must_confirm_before_execute"] = True
    if plan.get("follow_up"):
        enriched["after_execute"] = plan["follow_up"]
    return enriched


def _script_for_skill(skill_id: str, command: str) -> Optional[str]:
    if skill_id == "dnd-character-manager" and command in ("foundry", "roll20", "combat-foundry"):
        return "dnd-character-manager/scripts/vtt_export.py"
    return SKILLS.get(skill_id, {}).get("script")


def _build_playbook_argv(
    script_rel: str,
    campaign: str,
    command: str,
    extra_args: Optional[List[str]] = None,
    *,
    pass_campaign: bool = True,
    campaign_after_args: bool = False,
) -> List[str]:
    extra = list(extra_args or [])
    if not pass_campaign:
        return python_cli_argv(script_rel, command, *extra)
    if campaign_after_args:
        return python_cli_argv(script_rel, command, *extra, campaign)
    return python_cli_argv(script_rel, command, campaign, *extra)


def _run_cli(
    script_rel: str,
    campaign: str,
    command: str,
    extra_args: Optional[List[str]] = None,
    *,
    step: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    meta = step or {}
    cmd = _build_playbook_argv(
        script_rel,
        campaign,
        command,
        extra_args,
        pass_campaign=meta.get("pass_campaign", True),
        campaign_after_args=meta.get("campaign_after_args", False),
    )
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(get_workspace_root()))
    stdout = proc.stdout.strip()
    try:
        payload = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        payload = {"output": stdout}
    return {
        "ok": proc.returncode == 0,
        "command": cmd,
        "result": payload,
        "stderr": proc.stderr.strip() or None,
    }


def execute_intent(
    campaign: str,
    intent: str,
    *,
    context: Optional[Dict[str, Any]] = None,
    confirmed: bool = False,
) -> Dict[str, Any]:
    """Execute the primary backend for an intent when safe to auto-run."""
    ctx = context or {}
    plan = resolve_intent(intent, campaign=campaign, context=ctx)
    if plan.get("confirm") and not confirmed:
        return {
            "status": "confirmation_required",
            "intent": intent,
            "delegation": plan,
            "message": f"Confirm before executing {intent}",
        }

    script = plan.get("script")
    command = plan.get("command")
    if not script or not command:
        return {"status": "manual", "intent": intent, "delegation": plan, "message": "Grok narrates; no auto-exec"}

    extra = plan.get("resolved_args", [])
    if command == "damage" and ctx.get("damage"):
        target, amount = ctx["damage"]
        extra = ["--target", target, "--amount", str(amount)]
    elif command == "heal" and ctx.get("healing"):
        target, amount = ctx["healing"]
        extra = ["--target", target, "--amount", str(amount)]

    result = _run_cli(script, campaign, command, extra)
    return {
        "status": "executed" if result["ok"] else "failed",
        "intent": intent,
        "delegation": plan,
        "execution": result,
    }


def run_playbook(campaign: str, name: str, *, stop_on_error: bool = True) -> Dict[str, Any]:
    """Run a named multi-skill playbook sequentially."""
    steps = get_playbook(name)
    results: List[Dict[str, Any]] = []

    for step in steps:
        skill = step["skill"]
        command = step["command"]
        if command in ("initiative", "sync") or step.get("notes") and "Roll" in step.get("notes", ""):
            results.append({"step": step, "status": "skipped", "reason": step.get("notes", "manual step")})
            continue
        script = _script_for_skill(skill, command)
        if not script:
            results.append({"step": step, "status": "skipped", "reason": f"No auto script for {skill}"})
            continue
        extra = step.get("args", [])
        exec_result = _run_cli(script, campaign, command, extra, step=step)
        results.append({"step": step, "status": "ok" if exec_result["ok"] else "failed", "execution": exec_result})
        if stop_on_error and not exec_result["ok"]:
            break

    return {"playbook": name, "campaign": campaign, "steps_run": len(results), "results": results}


def route_and_plan(campaign: str, text: str) -> Dict[str, Any]:
    """Full pipeline: parse text -> route -> enrich with registry."""
    sys.path.insert(0, str(SKILLS_ROOT / "dnd-voice-assistant" / "scripts"))
    from voice_utils import route_voice_request

    base = route_voice_request(text)
    base["campaign"] = campaign
    base["player_text"] = text
    return enrich_route(campaign, base)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Cross-skill orchestrator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan")
    p_plan.add_argument("campaign")
    p_plan.add_argument("text")

    p_exec = sub.add_parser("execute")
    p_exec.add_argument("campaign")
    p_exec.add_argument("intent")
    p_exec.add_argument("--target")
    p_exec.add_argument("--amount", type=int)
    p_exec.add_argument("--confirmed", action="store_true")

    p_pb = sub.add_parser("playbook")
    p_pb.add_argument("campaign")
    p_pb.add_argument("name")

    args = parser.parse_args()

    if args.cmd == "plan":
        result = route_and_plan(args.campaign, args.text)
    elif args.cmd == "execute":
        ctx: Dict[str, Any] = {}
        if args.target and args.amount is not None:
            if args.intent == "healing":
                ctx["healing"] = (args.target, args.amount)
            else:
                ctx["damage"] = (args.target, args.amount)
        result = execute_intent(args.campaign, args.intent, context=ctx, confirmed=args.confirmed)
    elif args.cmd == "playbook":
        result = run_playbook(args.campaign, args.name)
    else:
        result = {"error": "unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()