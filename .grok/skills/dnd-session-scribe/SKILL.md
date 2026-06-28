---
name: dnd-session-scribe
description: Session recaps, XP awards, end-of-session cleanup, and log management. Triggers include end session, wrap up, award XP, session recap, save recap, what happened last time. Keeps campaigns resumable after long breaks. Integrates with dnd-utils audit and event logging.
---

# D&D Session Scribe

## When to Use
- Ending a play session with recap + XP
- Mid-campaign recap saves with future hooks
- Awarding XP for combat, milestones, or kingdom turns

**Do not use when:** Active encounter tracking (combat-assistant) or live DM narration (persistent-dm).

## Quick Start (Mobile)
1. Say **"End session"** with a one-line summary of what happened.
2. Grok awards XP, writes recap, runs audit, clears combat.
3. Next time: **"What happened last time?"** → reads latest recap.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Award XP | ✅ Implemented | Updates `player_character.json`; reports level-up availability |
| Save session recap | ✅ Implemented | Timestamped markdown in `recaps/` |
| End session (full) | ✅ Implemented | Recap + XP + audit + combat clear |
| Append session log | ✅ Implemented | `logs/session_log.md` |
| Event recording | ✅ Implemented | Via dnd-utils `record_event` |
| Auto-generate recap from events | ✅ Implemented | `auto-recap`; `end-session --auto` |
| Kingdom domain XP formulas | ✅ Implemented | `award-domain-xp` milestone suggestions via `xp_tables` |
| Quest hook sync from recap | ✅ Implemented | `sync-quests` imports hooks into quest tracker |

## Tools & Scripts
```bash
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py award-xp "My Campaign" 300 --reason "Defeated bandit chief"
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py recap "My Campaign" "The party cleared the mine and found a sealed door." --hook "Something stirs behind the door"
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py auto-recap "My Campaign" --save
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py end-session "My Campaign" "auto" --auto --xp 450 --reason "Session 12" --hook "Corruption spreads north"
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py append-log "My Campaign" "Party negotiated with the baron"
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py award-domain-xp "My Campaign" "reclaimed_mine"
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py sync-quests "My Campaign"
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py end-session "My Campaign" "auto" --auto --xp 450 --sync-quests
```

Primary script: `session_scribe.py` — commands: `award-xp`, `award-domain-xp`, `recap`, `auto-recap`, `end-session`, `append-log`, `sync-quests`

## Behavior
- Confirm XP: *"XP 2,700 → 3,150 (+450)."*
- Recaps capture location, PC status, and 1–3 hooks.
- End-session always offers a clean resume point.
- Ask before end-session in voice mode (destructive intent).

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/player_character.json` | W | XP total |
| `recaps/session_*.md` | W | Timestamped recaps |
| `logs/session_log.md` | W | Append-only notes |
| `logs/events.json` | W | XP/session events |
| `combat/current_combat.json` | W | Cleared on end-session |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | `end_session` intent → this skill (requires confirmation in voice) |
| Orchestrator | `plan` chains `auto-recap` → `end-session` → quest list |
| Playbooks | `session-end`: auto-recap → end-session → quest list → enhanced audit |
| Voice (iOS) | Confirm before `end-session`; player speaks summary |

## Integration
- **Uses:** dnd-utils (`audit_campaign`, `clear_combat_state`, `get_world_state`)
- **Called by:** persistent-dm, voice-assistant (`end_session` intent)

## iOS / Voice Notes
- End-session recap: player speaks summary; Grok condenses to ≤5 lines.
- Voice confirmation required before `end-session`.

## Example Flow
Player: *"Let's wrap up — we saved the village, 400 XP"*
→ `end-session "My Campaign" "..." --xp 400`
→ *"Saved. XP 1,200 → 1,600. Recap filed. **See you next session.**"*