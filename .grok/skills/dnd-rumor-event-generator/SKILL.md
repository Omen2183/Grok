---
name: dnd-rumor-event-generator
description: Generate rumors, faction actions, random world events, and downtime developments to keep campaigns reactive. v5.3.0 production. Triggers include what's the rumor mill, random event, faction move, downtime activity, kingdom event, world reacts. Especially strong in kingdom mode and sandbox play. Backed by rumor_generator.py CLI with persistent ledger.
---

# D&D Rumor & Event Generator

## When to Use
- World needs to feel alive between player actions
- Downtime, travel, or kingdom turn events
- Faction reactions to player choices

**Do not use when:** Recording canonical lore updates (lore-archivist) or structured event logging alone (dnd-utils `record-event`).

## Quick Start (Mobile)
1. Say **"What's happening in the world while we rest?"**
2. Grok runs `rumors` from kingdom/world state.
3. Player pursues one → persistent-dm runs the scene.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Procedural rumors | ✅ Implemented | `rumors` |
| List recent rumors | ✅ Implemented | `list` (events + ledger) |
| Faction moves | ✅ Implemented | `faction-move` |
| Rumor ledger persistence | ✅ Implemented | `ledger`, `rumors_ledger.json` |
| World events | ✅ Implemented | `world-event` |
| Context-aware generation | ✅ Implemented | Reads `kingdom_state.json` + factions |
| Kingdom/domain events | ✅ Implemented | Via `kingdom_sim` domain chains |
| Persist generated events | ✅ Implemented | `record-event` + ledger (use `--no-persist` to skip) |
| Faction simulation engine | ✅ Implemented | `faction-sim`, `diplomacy-graph` via `faction_engine.py` |
| Long-horizon faction AI | ✅ Implemented | `faction-sim` rounds + `kingdom_sim` cascading effects |

## Tools & Scripts
Primary script: `rumor_generator.py` — commands: `rumors`, `list`, `faction-move`, `world-event`, `ledger`, `faction-sim`, `diplomacy-graph`

```bash
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py rumors "My Campaign" --count 3
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py rumors "My Campaign" --no-persist
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py list "My Campaign" --limit 10
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py faction-move "My Campaign" --faction merchants --seed bandits
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py world-event "My Campaign" --seed unrest
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py ledger "My Campaign"
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py faction-sim "My Campaign"
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py diplomacy-graph "My Campaign"
```

## Behavior
- Tie rumors to active factions, location, and recent player deeds.
- Offer 2–3 hooks; let player choose — don't force all.
- Kingdom mode: mix resource shifts, diplomatic moves, and threats.
- Log adopted rumors/events via `record-event` (default on).

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/kingdom_state.json` | R | Factions, resources, projects |
| `state/world_state.json` | R | Location, time, mode |
| `state/rumors_ledger.json` | W | Persisted rumor entries |
| `logs/events.json` | W | Recorded rumors/events |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Rumor/world-event intents → this skill |
| Orchestrator | `plan` may chain rumors after rest or kingdom turn |
| Playbooks | `kingdom-turn`, `downtime` include rumor generation |
| Voice (iOS) | One rumor at a time; ask *"Want another?"* |

## Integration
- **Uses:** dnd-utils state, `event_system`, `kingdom_sim`
- **Called by:** persistent-dm, downtime-manager (playbook `downtime`)
- **Pairs with:** lore-archivist (canonize events), quest-tracker (hooks), npc-weaver

## iOS / Voice Notes
- Present one rumor at a time in voice; ask *"Want another?"*
- Keep each rumor to 2 sentences.
- Don't read ledger JSON — summarize `list` results.

## Example Flow
→ `rumors --count 3` → present hooks
→ *"1) Bandits on the east road. 2) Grain prices spike. 3) A lord seeks mercenaries."*
→ Player picks #1 → persistent-dm scenes it
→ **What do you do?**