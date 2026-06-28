---
name: dnd-downtime-manager
description: Short and long rests, hit dice spending, spell slot restore, and downtime activity logging for D&D campaigns. v5.3.0 production. Triggers include short rest, long rest, spend hit dice, downtime activity, rest status. Integrates with dnd-utils player state, rumor-event-generator after long rest, and voice-assistant rest routing.
---

# D&D Downtime Manager

## When to Use
- Player takes a short or long rest
- Spending hit dice between fights
- Logging crafting, research, or other downtime activities

**Do not use when:** Combat HP tracking (combat-assistant) or session wrap-up (session-scribe).

## Quick Start (Mobile)
1. Say **"We take a short rest"** or **"Long rest at the inn"**.
2. Grok runs the rest backend and confirms HP / hit dice changes.
3. For downtime: **"I spend 3 days crafting"** → logged with outcome.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Short rest | ✅ Implemented | Optional `--spend-hd` healing |
| Long rest | ✅ Implemented | Full HP, recover half HD (class-based), clear death saves |
| Spend hit dice (standalone) | ✅ Implemented | `spend-hit-dice` CLI |
| List downtime activities | ✅ Implemented | `list-activities` reads log |
| Downtime activity log | ✅ Implemented | `logs/downtime_log.md` |
| Rest status read | ✅ Implemented | `status` command |
| Post-rest rumors | ✅ Implemented | Via `playbook downtime` → rumor-generator |
| Spell slot restore (long rest) | ✅ Implemented | `long-rest` restores slots via `class_progression.py` |
| Exhaustion recovery | ⚠️ Partial | Long rest clears Exhaustion condition if present |

## Tools & Scripts
Primary script: `downtime_manager.py` — commands: `short-rest`, `long-rest`, `spend-hit-dice`, `log-activity`, `list-activities`, `status`

```bash
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py short-rest "My Campaign" --spend-hd 2
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py long-rest "My Campaign"
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py spend-hit-dice "My Campaign" 2
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py log-activity "My Campaign" "Craft healing potions" --days 3 --outcome "Created 2 potions"
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py list-activities "My Campaign"
python .grok/skills/dnd-downtime-manager/scripts/downtime_manager.py status "My Campaign"
```

## Behavior
- Confirm HP changes: before → after.
- Long rest assumes safe rest environment unless player says otherwise.
- Downtime activities append to log; Grok narrates outcomes.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/player_character.json` | R/W | HP, hit dice, conditions |
| `logs/downtime_log.md` | W | Activity log |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Intent `rest` → `short-rest` or `long-rest` |
| Orchestrator | `plan` maps voice phrases like *"long rest"* to CLI |
| Playbooks | `downtime`: long-rest → rumors → quest list |
| Voice (iOS) | `voice_utils` routes `rest` intent here; confirm HP before→after |

## Integration
| Trigger | Delegate from |
|---------|---------------|
| Rest after combat | persistent-dm / voice-assistant |
| Character HP | dnd-utils / character-manager |
| Rumors after rest | rumor-event-generator (playbook `downtime`) |
| Session end | session-scribe |

## iOS / Voice Notes
- Voice: *"Short rest, spend two hit dice"* → `short-rest --spend-hd 2`
- Speak HP changes clearly: *"You're back to full — 24 of 24."*
- Keep rest summaries to 3–4 lines unless player asks for detail.
- End with **What do you do?**

## Example Flow
Player: *"Long rest at the inn"*
→ `long-rest "My Campaign"`
→ *"Full rest. HP 18 → 32. Hit dice recovered. **What do you do?**"*