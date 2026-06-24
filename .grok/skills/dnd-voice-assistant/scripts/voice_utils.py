"""Voice-mode helpers: parse intent, format spoken responses, route and execute."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VOICE_BACKEND_VERSION = "3.2.0"

VOICE_TRIGGERS = (
    "voice mode",
    "play by voice",
    "dm voice",
    "start voice dnd",
    "continue voice campaign",
)

AMBIGUOUS_PATTERNS = (
    (re.compile(r"\b(hit|attack|strike|swing at)\b", re.I), "combat_action"),
    (re.compile(r"\b(roll|check|save|initiative)\b", re.I), "dice_roll"),
    (re.compile(r"\b(end session|wrap up|save session)\b", re.I), "end_session"),
    (re.compile(r"\b(next turn|whose turn|advance turn)\b", re.I), "next_turn"),
    (re.compile(r"\b(combat status|who('s| is) up|battle status)\b", re.I), "combat_status"),
    (re.compile(r"\b(heal|healing word|cure wounds|lay on hands)\b", re.I), "healing"),
    (re.compile(r"\b(apply condition|grappled|stunned|prone)\b", re.I), "apply_condition"),
    (re.compile(r"\b(level up|level-up)\b", re.I), "level_up"),
    (re.compile(r"\b(attune|attunement)\b", re.I), "attune"),
    (re.compile(r"\b(init campaign|new campaign|start (a )?new campaign)\b", re.I), "init_campaign"),
    (re.compile(r"\b(generate loot|treasure|what did we find)\b", re.I), "loot"),
    (re.compile(r"\b(rumor|rumour|what('s| is) the word)\b", re.I), "rumor"),
    (re.compile(r"\b(short rest|long rest|take a rest)\b", re.I), "rest"),
    (re.compile(r"\b(active quests|quest list|what quests)\b", re.I), "quest_list"),
    (re.compile(r"\b(track quest|new quest|add quest)\b", re.I), "add_quest"),
)


def is_voice_session(text: str) -> bool:
    lowered = text.lower()
    return any(trigger in lowered for trigger in VOICE_TRIGGERS)


def detect_intent(text: str) -> Optional[str]:
    for pattern, intent in AMBIGUOUS_PATTERNS:
        if pattern.search(text):
            return intent
    return None


def needs_confirmation(intent: str, text: str) -> bool:
    destructive = {"end_session", "level_up", "attune", "init_campaign"}
    if intent in destructive:
        return True
    if re.search(r"\b(all|everyone|wipe|reset)\b", text, re.I):
        return True
    return False


def format_spoken_reply(
    narration: str,
    mechanical: str = "",
    *,
    prompt: str = "What do you do?",
) -> str:
    parts = [narration.strip()]
    if mechanical:
        parts.append(mechanical.strip())
    parts.append(prompt)
    return " ".join(p for p in parts if p)


def parse_damage_phrase(text: str) -> Optional[Tuple[str, int]]:
    match = re.search(
        r"(?P<target>[A-Za-z][A-Za-z0-9' -]{0,40}?)\s+(?:takes?|took)\s+(?P<amount>\d+)\s+damage",
        text,
        re.I,
    )
    if not match:
        return None
    return match.group("target").strip(), int(match.group("amount"))


def parse_healing_phrase(text: str) -> Optional[Tuple[str, int]]:
    match = re.search(
        r"(?P<target>[A-Za-z][A-Za-z0-9' -]{0,40}?)\s+(?:heals?|healed|recovers?)\s+(?P<amount>\d+)",
        text,
        re.I,
    )
    if not match:
        return None
    return match.group("target").strip(), int(match.group("amount"))


def voice_confirm_prompt(action: str) -> str:
    return f"Confirm {action}? Say yes to proceed or correct me."


def _utils_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "dnd-utils" / "scripts"


def route_voice_request(text: str, *, campaign: Optional[str] = None) -> Dict[str, Any]:
    intent = detect_intent(text) or "narrative"
    damage = parse_damage_phrase(text)
    healing = parse_healing_phrase(text)
    route: Dict[str, Any] = {
        "intent": intent,
        "needs_confirmation": needs_confirmation(intent, text),
        "primary_skill": "dnd-persistent-dm",
        "version": VOICE_BACKEND_VERSION,
    }
    skill_map = {
        "dice_roll": "dnd-dice-engine",
        "end_session": "dnd-session-scribe",
        "next_turn": "dnd-combat-assistant",
        "combat_status": "dnd-combat-assistant",
        "healing": "dnd-combat-assistant",
        "apply_condition": "dnd-combat-assistant",
        "combat_action": "dnd-combat-assistant",
        "level_up": "dnd-character-manager",
        "loot": "dnd-loot-generator",
        "rumor": "dnd-rumor-event-generator",
        "rest": "dnd-downtime-manager",
        "quest_list": "dnd-quest-tracker",
        "add_quest": "dnd-quest-tracker",
        "attune": "dnd-character-manager",
        "init_campaign": "dnd-persistent-dm",
    }

    if damage:
        route.update({"primary_skill": "dnd-combat-assistant", "damage": damage, "intent": "damage"})
    elif healing:
        route.update({"primary_skill": "dnd-combat-assistant", "healing": healing, "intent": "healing"})
    elif intent in skill_map:
        route["primary_skill"] = skill_map[intent]

    if campaign:
        route["campaign"] = campaign
        try:
            utils = _utils_path()
            if str(utils) not in sys.path:
                sys.path.insert(0, str(utils))
            from skill_orchestrator import enrich_route  # noqa: E402

            route = enrich_route(campaign, route)
            route["version"] = VOICE_BACKEND_VERSION
        except Exception as exc:
            route["coordination_hint"] = (
                "Enrich via: python .grok/skills/dnd-utils/scripts/skill_orchestrator.py plan "
                f"{campaign} \"{text[:80]}\""
            )
            route["enrich_error"] = str(exc)
    return route


def build_execution_plan(campaign: str, text: str) -> Dict[str, Any]:
    """Return route plus suggested CLI command strings."""
    route = route_voice_request(text, campaign=campaign)
    commands: List[str] = []
    delegation = route.get("delegation", {})
    if route.get("damage"):
        target, amount = route["damage"]
        commands.append(
            f"python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py damage "
            f"\"{campaign}\" --target \"{target}\" --amount {amount}"
        )
    elif route.get("healing"):
        target, amount = route["healing"]
        commands.append(
            f"python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py heal "
            f"\"{campaign}\" --target \"{target}\" --amount {amount}"
        )
    elif delegation.get("script") and delegation.get("command"):
        commands.append(
            f"python .grok/skills/{delegation['script']} {delegation['command']} \"{campaign}\""
        )
    route["suggested_commands"] = commands
    return route


def execute_voice_request(
    campaign: str,
    text: str,
    *,
    confirmed: bool = False,
) -> Dict[str, Any]:
    """Route and optionally execute via skill_orchestrator."""
    route = route_voice_request(text, campaign=campaign)
    if route.get("needs_confirmation") and not confirmed:
        return {
            "status": "confirmation_required",
            "prompt": voice_confirm_prompt(route.get("intent", "action")),
            "route": route,
        }
    try:
        utils = _utils_path()
        if str(utils) not in sys.path:
            sys.path.insert(0, str(utils))
        from skill_orchestrator import execute_intent  # noqa: E402

        result = execute_intent(
            campaign,
            route.get("intent", "narrative"),
            context={k: route[k] for k in ("damage", "healing") if k in route},
            confirmed=True,
        )
        return {"status": "executed", "route": route, "result": result}
    except Exception as exc:
        return {"status": "route_only", "route": route, "error": str(exc)}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Voice assistant routing and parsing")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_route = sub.add_parser("route")
    p_route.add_argument("campaign")
    p_route.add_argument("text")

    p_parse = sub.add_parser("parse")
    p_parse.add_argument("text")

    p_detect = sub.add_parser("detect-voice")
    p_detect.add_argument("text")

    p_fmt = sub.add_parser("format-spoken")
    p_fmt.add_argument("narration")
    p_fmt.add_argument("--mechanical", default="")
    p_fmt.add_argument("--prompt", default="What do you do?")

    p_plan = sub.add_parser("plan")
    p_plan.add_argument("campaign")
    p_plan.add_argument("text")

    p_exec = sub.add_parser("execute")
    p_exec.add_argument("campaign")
    p_exec.add_argument("text")
    p_exec.add_argument("--yes", action="store_true")

    p_confirm = sub.add_parser("confirm-check")
    p_confirm.add_argument("text")

    args = parser.parse_args()

    if args.cmd == "route":
        result = route_voice_request(args.text, campaign=args.campaign)
    elif args.cmd == "parse":
        intent = detect_intent(args.text) or "narrative"
        result = {
            "intent": intent,
            "damage": parse_damage_phrase(args.text),
            "healing": parse_healing_phrase(args.text),
            "needs_confirmation": needs_confirmation(intent, args.text),
            "version": VOICE_BACKEND_VERSION,
        }
    elif args.cmd == "detect-voice":
        result = {"voice_session": is_voice_session(args.text), "version": VOICE_BACKEND_VERSION}
    elif args.cmd == "format-spoken":
        result = {
            "spoken": format_spoken_reply(args.narration, args.mechanical, prompt=args.prompt),
            "version": VOICE_BACKEND_VERSION,
        }
    elif args.cmd == "plan":
        result = build_execution_plan(args.campaign, args.text)
    elif args.cmd == "execute":
        result = execute_voice_request(args.campaign, args.text, confirmed=args.yes)
    elif args.cmd == "confirm-check":
        intent = detect_intent(args.text) or ""
        result = {
            "needs_confirmation": needs_confirmation(intent, args.text),
            "prompt": voice_confirm_prompt(intent or "action") if needs_confirmation(intent, args.text) else None,
            "version": VOICE_BACKEND_VERSION,
        }
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()