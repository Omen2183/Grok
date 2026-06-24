---
name: dnd-content-forge
description: Generate balanced encounters, monsters, magic items, quests, domain events, and faction ideas using campaign context. Triggers include generate encounter, create monster, random event, kingdom project ideas, create magic item, side quest, design boss. Supports 5e + homebrew. Tabletop vs kingdom mode changes output framing.
---

# D&D Content Forge

## When to Use
- Need a monster stat block scaffold or encounter budget
- Brainstorming quests, domain events, or faction moves
- Creating homebrew content tailored to party level

**Do not use when:** Persisting NPCs (npc-weaver), rolling loot tables (loot-generator), or live DM play (persistent-dm).

## Quick Start (Mobile)
1. Say **"Generate a CR 5 forest predator for my party"**.
2. Grok runs the prompt builder and authors the full stat block.
3. For encounters: add `--encounter` for XP budget guidance.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Monster prompt + CR scaling | ✅ Implemented | `generate_monster.py` |
| Encounter XP budget | ✅ Implemented | `--encounter` flag |
| Full encounter builder | ✅ Implemented | `encounter_builder.py build` |
| Quest / faction / item prompts | ✅ Implemented | `content_forge.py` |
| Party level from state | ✅ Implemented | Reads `player_character.json` |
| Full stat block output | ⚠️ Partial | Script builds prompt; Grok writes stats |
| Domain event prompts | ✅ Implemented | `content_forge.py domain-event` |
| Procedural magic items | ❌ Use loot-generator | content_forge builds prompts only |
| Auto-add to campaign JSON | ❌ Prompt-only | Manual save via npc-weaver / lore-archivist |

## Tools & Scripts
```bash
python .grok/skills/dnd-content-forge/scripts/generate_monster.py "My Campaign" --theme "Corrupted treant" --cr 5 --difficulty Hard
python .grok/skills/dnd-content-forge/scripts/generate_monster.py "My Campaign" --theme "Veil stalker" --cr 7 --encounter --difficulty Deadly --extra "Uses fear aura and hit-and-run"
python .grok/skills/dnd-content-forge/scripts/encounter_builder.py build "My Campaign" --theme "forest ambush" --difficulty Hard --save
python .grok/skills/dnd-content-forge/scripts/content_forge.py quest "My Campaign" --theme "missing caravan"
python .grok/skills/dnd-content-forge/scripts/content_forge.py faction "My Campaign" --name "Merchant Guild"
```

## Behavior
- Pull party level from campaign state when available.
- Present stat blocks in compact mobile format: AC, HP, key attacks.
- Kingdom mode: frame as domain threats, not just combatants.
- Offer to persist important creations via npc-weaver.

## State & Files
| File | R | Purpose |
|------|---|---------|
| `state/player_character.json` | R | Party level |
| `state/kingdom_state.json` | R | Domain context (import) |
| `state/world_state.json` | R | Mode (tabletop/kingdom) |

## Integration
- **Uses:** dnd-utils for party/kingdom context
- **Called by:** persistent-dm for encounters and side content
- **Pairs with:** combat-assistant (run fight), loot-generator (rewards)

## iOS / Voice Notes
- Summarize stat blocks verbally: HP, AC, one signature ability.
- Full block available if player asks *"details"*.

## Example Flow
→ `generate_monster.py "My Campaign" --theme "Ash wraith" --cr 4 --encounter`
→ Grok outputs wraith stat block + XP budget
→ Player accepts → `combat_tracker.py init` + adds
→ **What do you do?**