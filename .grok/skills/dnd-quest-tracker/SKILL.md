---
name: dnd-quest-tracker
description: Track active quests, session hooks, and completion state for persistent D&D campaigns. v3.2.0 production. Triggers include add quest, complete quest, complete objective, what quests are active, new hook, quest list, sync quests from recap. Integrates with session-scribe `sync-quests` and persistent-dm playbooks.
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
| Auto-sync from recaps | ✅ Implemented | `session-scribe sync-quests` or `end-session --sync-quests` imports hooks/quests from auto-recap |

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
- At session end, offer `sync-quests` when the recap contains new hooks (via session-scribe).
- `sync-quests` extracts hooks from auto-recap; lines starting with `quest:` become full quests, others become hooks.
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
| Playbooks | `session-end` lists quests; run `sync-quests` before `list` when recap has new hooks |
| Voice (iOS) | Short quest titles; one quest per spoken beat |

## Integration
| Trigger | Skill |
|---------|-------|
| Quest ideas | dnd-content-forge |
| Recap hook import | dnd-session-scribe (`sync-quests`, `end-session --sync-quests`) |
| Session hooks in recaps | dnd-session-scribe → writes hooks; this skill receives via `sync-quests` |
| DM orchestration | dnd-persistent-dm |

```bash
# Import hooks from latest auto-recap (session-scribe → quest tracker)
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py sync-quests "My Campaign"
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py end-session "My Campaign" "auto" --auto --xp 400 --sync-quests
```

## iOS / Voice Notes
- *"You have three active quests"* — list titles only unless player asks for detail.
- Voice completion: confirm before marking quest complete.
- End with **What do you do?** when presenting new hooks.

## Example Flow
→ `add` after NPC offers quest
→ Mid-campaign: `list` for resume
→ Session end: session-scribe `sync-quests` → `list` shows new hooks
→ `complete-objective` then `complete` when done
→ **What do you do?**