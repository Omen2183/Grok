---
name: dnd-quest-tracker
description: Track active quests, session hooks, and completion state for persistent D&D campaigns. v3.2.0 production. Triggers include add quest, complete quest, complete objective, what quests are active, new hook, quest list. Integrates with session-scribe recaps and persistent-dm playbooks.
---

# D&D Quest Tracker

## When to Use
- Adding or completing quests and side objectives
- Storing hooks for the next session
- Answering **"What quests do we have?"**

**Do not use when:** Generating new quest ideas (content-forge) or writing lore (lore-archivist).

## Quick Start (Mobile)
1. After a quest hook: **"Track quest: Find the lost seal"**.
2. On completion: **"Complete quest find-the-lost-seal"**.
3. Resume: **"What quests are active?"** → `list` command.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Add quest | ✅ Implemented | `state/quests.json` |
| Add session hook | ✅ Implemented | Open hooks list |
| Complete quest | ✅ Implemented | Status + event log |
| Complete objective | ✅ Implemented | `complete-objective` CLI |
| List active | ✅ Implemented | Quests + unresolved hooks |
| Objective checklist | ✅ Implemented | Objectives stored; `complete-objective` per step |
| Auto-sync from recaps | ⚠️ Partial | session-scribe hooks; manual quest add |

## Tools & Scripts
Primary script: `quest_tracker.py` — commands: `add`, `add-hook`, `complete`, `complete-objective`, `list`

```bash
python .grok/skills/dnd-quest-tracker/scripts/quest_tracker.py add "My Campaign" "Find the Lost Seal" --summary "The elder asked for help" --objective "Search the ruins" --reward "200 gp"
python .grok/skills/dnd-quest-tracker/scripts/quest_tracker.py add-hook "My Campaign" "Strange lights in the northern woods"
python .grok/skills/dnd-quest-tracker/scripts/quest_tracker.py list "My Campaign"
python .grok/skills/dnd-quest-tracker/scripts/quest_tracker.py complete-objective "My Campaign" find-the-lost-seal "Search the ruins"
python .grok/skills/dnd-quest-tracker/scripts/quest_tracker.py complete "My Campaign" find-the-lost-seal --notes "Seal recovered"
```

## Behavior
- Keep quest titles short and memorable for voice play.
- Offer to add hooks at session end (session-scribe integration).
- Completed quests stay in JSON for history.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/quests.json` | R/W | Active and completed quests, hooks |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | `quest_list`, `add_quest` intents → this skill |
| Orchestrator | `plan` may surface hooks after session-end |
| Playbooks | `session-end` lists quests; `downtime` surfaces hooks |
| Voice (iOS) | Short quest titles; one quest per spoken beat |

## Integration
| Trigger | Skill |
|---------|-------|
| Quest ideas | dnd-content-forge |
| Session hooks | dnd-session-scribe |
| DM orchestration | dnd-persistent-dm |

## iOS / Voice Notes
- *"You have three active quests"* — list titles only unless player asks for detail.
- Voice completion: confirm before marking quest complete.
- End with **What do you do?** when presenting new hooks.

## Example Flow
→ `add` after NPC offers quest
→ Mid-campaign: `list` for resume
→ `complete-objective` then `complete` when done
→ **What do you do?**