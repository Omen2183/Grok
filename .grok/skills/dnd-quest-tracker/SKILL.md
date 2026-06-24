---
name: dnd-quest-tracker
description: Track active quests, session hooks, and completion state for persistent D&D campaigns. Triggers include add quest, complete quest, what quests are active, new hook, quest list. Integrates with session-scribe recaps and persistent-dm.
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
| List active | ✅ Implemented | Quests + unresolved hooks |
| Objective checklist | ⚠️ Partial | Objectives stored; per-objective CLI limited |
| Auto-sync from recaps | ❌ Not implemented | Manual add or Grok-driven |

## Tools & Scripts
```bash
python .grok/skills/dnd-quest-tracker/scripts/quest_tracker.py add "My Campaign" "Find the Lost Seal" --summary "The elder asked for help" --objective "Search the ruins" --reward "200 gp"
python .grok/skills/dnd-quest-tracker/scripts/quest_tracker.py add-hook "My Campaign" "Strange lights in the northern woods"
python .grok/skills/dnd-quest-tracker/scripts/quest_tracker.py list "My Campaign"
python .grok/skills/dnd-quest-tracker/scripts/quest_tracker.py complete "My Campaign" find-the-lost-seal --notes "Seal recovered"
```

## Behavior
- Keep quest titles short and memorable for voice play.
- Offer to add hooks at session end (session-scribe integration).
- Completed quests stay in JSON for history.

## Integration
| Trigger | Skill |
|---------|-------|
| Quest ideas | dnd-content-forge |
| Session hooks | dnd-session-scribe |
| DM orchestration | dnd-persistent-dm |