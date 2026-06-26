---
name: dnd-voice-assistant
description: Voice execution layer for the D&D skills suite. v5.1.0 production. Triggers include voice mode, play by voice, DM voice, start voice D&D, continue voice campaign. Routes utterances through skill_orchestrator plan/execute to persistent-dm, combat-assistant, dice-engine, downtime-manager, and session-scribe. Parses damage/healing phrases, confirms destructive actions, and formats listenable short replies. Full mechanical parity with text play on Grok iOS.
---

# D&D Voice Assistant

## When to Use
- Player enables voice D&D or speaks instead of typing (Grok iOS standalone app)
- Ambiguous combat/dice/session phrases need routing
- Replies must be short and listenable on mobile

**Do not use when:** Player is in text mode (route directly to persistent-dm).

## Quick Start (Mobile)
1. Say **"Start voice D&D"** or **"Play by voice"**.
2. Talk naturally — Grok runs `detect-voice` → `plan` → target skill `execute`.
3. Confirm destructive actions when prompted (*"Say yes to proceed"*).

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Voice session detection | ✅ Implemented | `detect-voice` / `is_voice_session()` |
| Full intent routing | ✅ Implemented | `route` → enrich via `plan` |
| Execution pipeline | ✅ Implemented | `execute` runs orchestrator + target CLIs |
| Damage phrase parsing | ✅ Implemented | `parse` — *"Goblin takes 8 damage"* |
| Healing phrase parsing | ✅ Implemented | *"Aria heals 10"* |
| Confirmation gates | ✅ Implemented | `confirm-check` for end-session, level-up, attune, init |
| Spoken reply formatting | ✅ Implemented | `format-spoken` |
| Speech-to-text / TTS | ❌ Platform | Grok iOS handles I/O; this skill formats routing only |
| Continuous ambient listening | ❌ Platform | Turn-based voice turns |

## Tools & Scripts
Primary script: `voice_utils.py` — commands: `route`, `parse`, `detect-voice`, `format-spoken`, `plan`, `execute`, `confirm-check`

```bash
python .grok/skills/dnd-voice-assistant/scripts/voice_utils.py detect-voice "start voice dnd"
python .grok/skills/dnd-voice-assistant/scripts/voice_utils.py route "My Campaign" "Goblin takes 8 damage"
python .grok/skills/dnd-voice-assistant/scripts/voice_utils.py parse "next turn"
python .grok/skills/dnd-voice-assistant/scripts/voice_utils.py plan "My Campaign" "Goblin takes 8 damage"
python .grok/skills/dnd-voice-assistant/scripts/voice_utils.py execute "My Campaign" "Goblin takes 8 damage"
python .grok/skills/dnd-voice-assistant/scripts/voice_utils.py format-spoken "Your blade finds its mark." --mechanical "Goblin 7 to 0 HP"
python .grok/skills/dnd-voice-assistant/scripts/voice_utils.py confirm-check end-session --text "yes"
```

Downstream CLIs (invoked after `plan` / `execute`):
```bash
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py damage "My Campaign" --target "Goblin" --amount 8
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py attack 8 --advantage --campaign "My Campaign"
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py long-rest "My Campaign"
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py end-session "My Campaign" "Summary here"
```

## Behavior
- **Always route voice through this skill first**, then `plan` → delegate.
- Replies ≤3 sentences + mechanical line + *"What do you do?"*
- Confirm before: end session, level-up, attune, campaign init, mass resets.
- State changes: speak before → after (*"32 to 24 HP"*).

## State & Files
No direct file I/O — delegates to routed skills. Campaign root via `paths.py` (`DND_CAMPAIGNS_ROOT` or `~/.grok/artifacts/dnd-campaigns/`).

## Skill Coordination
| Layer | Role |
|-------|------|
| Entry point | **All Grok iOS voice play starts here** |
| Registry | `route` uses `skill_registry` intent map |
| Orchestrator | `plan` / `execute` call `skill_orchestrator.py` for CLI + follow-ups |
| Playbooks | Destructive flows use `confirm-check` then `playbook session-end` etc. |
| sync_bridge | Indirect — combat damage routes to combat-assistant which syncs PC HP |

## Integration
| Intent | Routes to |
|--------|-----------|
| `narrative` (default) | dnd-persistent-dm |
| damage/healing parsed | dnd-combat-assistant |
| `dice_roll` | dnd-dice-engine |
| `end_session` | dnd-session-scribe → playbook session-end |
| `rest` | dnd-downtime-manager |
| `quest_list` / `add_quest` | dnd-quest-tracker |
| `combat_action` | dnd-dice-engine → dnd-combat-assistant |

## iOS / Voice Notes
- Avoid bullet lists and markdown in spoken output; use `format-spoken`.
- Spell numbers for clarity on small totals (*"eight damage"*).
- Pause after confirmation questions; wait for *yes/no*.
- Long recaps: offer *"Want the short or full version?"*
- Campaign data resolves automatically on iOS via `paths.py` (no hardcoded cloud paths).

## Example Flow
Player (voice): *"I hit the goblin for 8"*
→ `plan "My Campaign" "Goblin takes 8 damage"` → combat `damage --amount 8`
→ `format-spoken` → *"What do you do?"*