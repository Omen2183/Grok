---
name: dnd-rumor-event-generator
description: Generate rumors, faction actions, random world events, and downtime developments to keep campaigns reactive. v2.0.0 production. Triggers include what's the rumor mill, random event, faction move, downtime activity, kingdom event, world reacts. Especially strong in kingdom mode and sandbox play. Backed by rumor_generator.py CLI.
---

# D&D Rumor & Event Generator

## When to Use
- World needs to feel alive between player actions
- Downtime, travel, or kingdom turn events
- Faction reactions to player choices

**Do not use when:** Recording canonical lore updates (lore-archivist) or structured event logging alone (dnd-utils `record-event`).

## Quick Start (Mobile)
1. Say **"What's happening in the world while we rest?"**
2. Grok runs `rumor_generator rumors` from kingdom/world state.
3. Player pursues one → persistent-dm runs the scene.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Procedural rumors | ✅ Implemented | `rumor_generator.py rumors` |
| World events | ✅ Implemented | `rumor_generator.py world-event` |
| Context-aware generation | ✅ Implemented | Reads `kingdom_state.json` + factions |
| Kingdom/domain events | ✅ Implemented | Trade, unrest, military seeds |
| Faction reaction narratives | ✅ Implemented | State-driven templates + Grok polish |
| Persist generated events | ✅ Implemented | Via dnd-utils `record-event` |
| Long-horizon faction AI | ⚠️ Partial | Use kingdom_sim for cascading effects |

## Tools & Scripts
```bash
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py rumors "My Campaign" --count 3
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py world-event "My Campaign" --seed unrest
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
→ `rumor_generator rumors --count 3` → present hooks
→ *"1) Bandits on the east road. 2) Grain prices spike. 3) A lord seeks mercenaries."*
→ Player picks #1 → persistent-dm scenes it
→ `record-event` with tag `rumor`
→ **What do you do?**