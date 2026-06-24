---
name: dnd-lore-archivist
description: Maintain, query, and update deep campaign lore, NPC knowledge, faction relationships, and world consistency. v2.0.0 production. Triggers include what does [NPC] know, update the lore, recap factions, kingdom state query, homebrew lore question, what happened at [location]. Essential for long-running sandbox and kingdom campaigns. Backed by lore_archivist.py CLI.
---

# D&D Lore Archivist

## When to Use
- Player asks about established world facts, history, or factions
- Updating lore after major story beats
- Consistency checks before introducing new elements

**Do not use when:** Creating new NPC profiles (npc-weaver), rules lookups (rules-reference), or live encounter play (persistent-dm).

## Quick Start (Mobile)
1. Ask **"What do the Iron Compact know about the vault?"**
2. Grok runs `lore_archivist query` + reads state, events, NPC files.
3. After revelations: **"Update lore — the vault is a prison"** → `append`.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Append lore entries | ✅ Implemented | `lore_archivist.py append` → `lore_summary.md` |
| Lore summary read | ✅ Implemented | `lore_archivist.py summary` |
| Keyword lore query | ✅ Implemented | `lore_archivist.py query` + event search |
| Query campaign JSON state | ✅ Implemented | Via dnd-utils `load` / reads |
| Search event log | ✅ Implemented | `search-events` in dnd-utils |
| Read NPC profiles | ✅ Implemented | `npcs/*.json` |
| Read session recaps | ✅ Implemented | `recaps/*.md` |
| Automated lore writes | ✅ Implemented | `append` persists markdown + events |
| Lore consistency reasoning | ⚠️ Partial | Grok LLM; no vector DB |
| Faction simulation engine | ❌ Prompt-only | Use rumor-event-generator |

## Tools & Scripts
```bash
python .grok/skills/dnd-lore-archivist/scripts/lore_archivist.py append "My Campaign" "The vault beneath Thornhold is a prison for ancient wraiths"
python .grok/skills/dnd-lore-archivist/scripts/lore_archivist.py summary "My Campaign"
python .grok/skills/dnd-lore-archivist/scripts/lore_archivist.py query "My Campaign" "vault"
python .grok/skills/dnd-lore-archivist/scripts/lore_archivist.py list-npcs "My Campaign"
python .grok/skills/dnd-lore-archivist/scripts/lore_archivist.py list-recaps "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py load "My Campaign" --file kingdom_state
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py search-events "My Campaign" --tag lore --limit 10
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py get "My Campaign" npc-id
```

## Behavior
- **Never invent** established facts — read files first.
- Cite uncertainty: *"Not recorded yet — want to establish it?"*
- Canon updates: `lore_archivist append` + optional `record-event`.
- Keep answers ≤8 lines unless player asks for deep lore.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/lore_summary.md` | R/W | Chronological lore digest |
| `state/world_state.json` | R/W | Location, notes, mode |
| `state/kingdom_state.json` | R | Factions, domain flags |
| `npcs/{id}.json` | R | NPC knowledge in notes/secrets |
| `logs/events.json` | R/W | Lore-tagged events |
| `recaps/session_*.md` | R | Historical narrative |
| `logs/session_log.md` | R | GM notes |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | Lore query/update intents → this skill |
| Orchestrator | `plan` may chain rumor events → `append` for canonization |
| Playbooks | Optional follow-up after `kingdom-turn` rumors |
| Voice (iOS) | One fact per sentence; offer *"Want more detail?"* |

## Integration
- **Uses:** dnd-utils, npc-weaver (reads)
- **Called by:** persistent-dm for lore questions
- **Pairs with:** rumor-event-generator for world reactions

## iOS / Voice Notes
- Voice lore answers: one fact per sentence, chronological when recounting history.
- Offer *"Want more detail?"* instead of dumping paragraphs.

## Example Flow
Player: *"What factions control the eastern trade road?"*
→ `lore_archivist query "eastern trade"` + read `kingdom_state.json`
→ *"Iron Compact (friendly) patrols the road; Hollow Guild smuggles at night."*
→ **What do you do?**