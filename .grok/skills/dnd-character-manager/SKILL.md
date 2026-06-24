---
name: dnd-character-manager
description: Player character sheet management — summary, level-up, inventory, attunement, death saves, export. Triggers include level up, character sheet, add item, attune, death save, export character, companion status. Integrates with dnd-utils state and combat-assistant HP sync. Supports 5e + homebrew feats and multiclass.
---

# D&D Character Manager

## When to Use
- Viewing or updating the PC sheet outside combat
- Level-ups, inventory changes, attunement toggles
- Death save tracking on the character record
- Exporting a readable markdown sheet

**Do not use when:** In active combat HP tracking (combat-assistant) or full DM narration (persistent-dm).

## Quick Start (Mobile)
1. Say **"Show my character"** → summary from `player_character.json`.
2. After a level: **"Level up to 5"** → HP and proficiency updated.
3. Loot pickup: **"Add +1 longsword to inventory"**.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Character summary | ✅ Implemented | CLI `summary` |
| Level-up | ✅ Implemented | `--levels`, optional `--class` |
| Inventory add/remove/attune | ✅ Implemented | Persists to JSON |
| Death saves on sheet | ✅ Implemented | `death-save success/failure` |
| Markdown export | ✅ Implemented | `export` command |
| Level-up suggestions | ⚠️ Partial | `suggest_level_up_options()` — import only, no CLI |
| Companion management | ⚠️ Partial | Functions exist; no dedicated CLI commands |
| Full multiclass builder UI | ❌ Prompt-only | Grok guides; manual JSON edits for edge cases |

## Tools & Scripts
```bash
python .grok/skills/dnd-character-manager/scripts/character_manager.py summary "My Campaign"
python .grok/skills/dnd-character-manager/scripts/character_manager.py level-up "My Campaign" --levels 1 --class Fighter
python .grok/skills/dnd-character-manager/scripts/character_manager.py inventory "My Campaign" add --name "Cloak of Protection" --type wondrous
python .grok/skills/dnd-character-manager/scripts/character_manager.py inventory "My Campaign" attune --name "Cloak of Protection"
python .grok/skills/dnd-character-manager/scripts/character_manager.py death-save "My Campaign" success
python .grok/skills/dnd-character-manager/scripts/character_manager.py export "My Campaign"
```

## Behavior
- Confirm every stat change: *"HP max 32 → 38. Level 4 → 5."*
- Read sheet before suggesting feats or ASIs.
- Inventory limits: respect attunement (max 3) in narration.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `state/player_character.json` | R/W | Full PC sheet |
| `state/player_character.md` | W | Human-readable export |
| `state/companions.json` | R/W | Companion data (import functions) |

## Integration
- **Uses:** dnd-utils paths and world state
- **Called by:** persistent-dm, session-scribe (XP writes to same JSON)
- **Syncs with:** combat-assistant on HP/death saves

## iOS / Voice Notes
- Summaries ≤8 lines: name, level, HP, key conditions, attuned items.
- Voice: confirm level-ups and attunement before writing.

## Example Flow
Player: *"I hit level 5"*
→ `level-up "My Campaign" --levels 1`
→ *"Level 4 → 5. HP 32/32 → 38/38. Proficiency +3. **What do you do?**"*