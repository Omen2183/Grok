---
name: dnd-lore-archivist
description: Maintain, query, and update deep campaign lore, NPC knowledge, faction relationships, and world consistency. Triggers include what does [NPC] know, update the lore, recap factions, kingdom state query, homebrew lore question, what happened at [location]. Essential for long-running sandbox and kingdom campaigns. Prompt-driven with JSON state reads.
---

# D&D Lore Archivist

## When to Use
- Player asks about established world facts, history, or factions
- Updating lore after major story beats
- Consistency checks before introducing new elements

**Do not use when:** Creating new NPC profiles (npc-weaver), rules lookups (rules-reference), or live encounter play (persistent-dm).

## Quick Start (Mobile)
1. Ask **"What do the Iron Compact know about the vault?"**
2. Grok reads state, events, NPC files, and session recaps.
3. After revelations: **"Update lore — the vault is a prison"**.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Query campaign JSON state | ✅ Implemented | Via dnd-utils `load` / reads |
| Search event log | ✅ Implemented | `search-events` in dnd-utils |
| Read NPC profiles | ✅ Implemented | `npcs/*.json` |
| Read session recaps | ✅ Implemented | `recaps/*.md` |
| Lore consistency reasoning | ⚠️ Partial | Grok LLM; no vector DB |
| Automated lore writes | ❌ Prompt-only | Grok appends to notes/recaps |
| Faction simulation engine | ❌ Prompt-only | Use rumor-event-generator |

## Tools & Scripts
No dedicated script — read state via dnd-utils:
```bash
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py load "My Campaign" --file world_state
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py load "My Campaign" --file kingdom_state
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py search-events "My Campaign" --tag lore --limit 10
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py get "My Campaign" npc-id
```

## Behavior
- **Never invent** established facts — read files first.
- Cite uncertainty: *"Not recorded yet — want to establish it?"*
- Updates go to `world_state.json` notes, NPC files, or `record-event`.
- Keep answers ≤8 lines unless player asks for deep lore.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/world_state.json` | R/W | Location, notes, mode |
| `state/kingdom_state.json` | R | Factions, domain flags |
| `npcs/{id}.json` | R | NPC knowledge in notes/secrets |
| `logs/events.json` | R/W | Lore-tagged events |
| `recaps/session_*.md` | R | Historical narrative |
| `logs/session_log.md` | R | GM notes |

## Integration
- **Uses:** dnd-utils, npc-weaver (reads)
- **Called by:** persistent-dm for lore questions
- **Pairs with:** rumor-event-generator for world reactions

## iOS / Voice Notes
- Voice lore answers: one fact per sentence, chronological when recounting history.
- Offer *"Want more detail?"* instead of dumping paragraphs.

## Example Flow
Player: *"What factions control the eastern trade road?"*
→ Read `kingdom_state.json` + `search-events --tag faction`
→ *"Iron Compact (friendly) patrols the road; Hollow Guild smuggles at night."*
→ **What do you do?**