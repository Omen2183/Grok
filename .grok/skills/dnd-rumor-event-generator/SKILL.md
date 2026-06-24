---
name: dnd-rumor-event-generator
description: Generate rumors, faction actions, random world events, and downtime developments to keep campaigns reactive. Triggers include what's the rumor mill, random event, faction move, downtime activity, kingdom event, world reacts. Especially strong in kingdom mode and sandbox play. Prompt-only — reads state, no generator script.
---

# D&D Rumor & Event Generator

## When to Use
- World needs to feel alive between player actions
- Downtime, travel, or kingdom turn events
- Faction reactions to player choices

**Do not use when:** Recording canonical lore updates (lore-archivist) or structured event logging alone (dnd-utils `record-event`).

## Quick Start (Mobile)
1. Say **"What's happening in the world while we rest?"**
2. Grok reads kingdom/world state and generates 1–3 rumors or events.
3. Player pursues one → persistent-dm runs the scene.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Context-aware rumor generation | ⚠️ Partial | Grok + state reads |
| Kingdom/domain events | ⚠️ Partial | Uses `kingdom_state.json` |
| Faction reaction narratives | ⚠️ Partial | Prompt-driven |
| Persist generated events | ✅ Implemented | Via dnd-utils `record-event` |
| Procedural event tables script | ❌ Prompt-only | No `event_generator.py` |
| Long-horizon faction AI | ❌ Prompt-only | No simulation backend |

## Tools & Scripts
Read context, then log chosen events:
```bash
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py load "My Campaign" --file kingdom_state
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py kingdom-summary "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py search-events "My Campaign" --tag rumor --limit 5
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py record-event "My Campaign" "Merchants whisper of iron shortages" --tags rumor,faction
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py advance-projects "My Campaign" --turns 1
```

## Behavior
- Tie rumors to active factions, location, and recent player deeds.
- Offer 2–3 hooks; let player choose — don't force all.
- Kingdom mode: mix resource shifts, diplomatic moves, and threats.
- Log adopted rumors/events via `record-event`.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/kingdom_state.json` | R | Factions, resources, projects |
| `state/world_state.json` | R | Location, time, mode |
| `logs/events.json` | W | Recorded rumors/events |

## Integration
- **Uses:** dnd-utils state + event logging
- **Called by:** persistent-dm during downtime/kingdom turns
- **Pairs with:** lore-archivist (canonize events), npc-weaver (involved NPCs)

## iOS / Voice Notes
- Present one rumor at a time in voice; ask *"Want another?"*
- Keep each rumor to 2 sentences.

## Example Flow
→ Read kingdom summary → generate 3 rumors
→ *"1) Bandits on the east road. 2) Grain prices spike. 3) A lord seeks mercenaries."*
→ Player picks #1 → persistent-dm scenes it
→ `record-event` with tag `rumor`
→ **What do you do?**