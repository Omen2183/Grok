---
name: dnd-character-manager
description: Use for managing player character sheets including leveling up, multiclassing, homebrew feats, inventory, attunement, death saves, and conditions. Triggers include level up, update character sheet, add feat, manage inventory, attune item, death save, export character. Integrates with dnd-utils state, combat-assistant, and persistent-dm. Supports 5e + heavy homebrew.
---

# Dnd Character Manager

## Overview
Provides persistent, structured management of player character sheets with strong support for heavy homebrew. It handles leveling, multiclassing, feats, inventory, attunement, death saves, and bidirectional synchronization with combat. It serves as the authoritative source for character state, ensuring long-term coherence and enabling clean exports.

## When to Activate
- "Level up my character"
- "Update my character sheet"
- "Add the homebrew feat [Name]"
- "Manage my inventory" or "Attune to [item]"
- "Track death saves"
- "Export my character to JSON/Markdown"
- "Show my current character stats"
- During character creation or major progression moments

## Core Capabilities

### 1. Character Sheet Management
- Maintain a structured `player_character.json` + human-readable `player_character.md` in the campaign `state/` folder
- Track core stats, class levels (including multiclass), background, race, and proficiencies
- Support custom/homebrew races, classes, subclasses, and feats

### 2. Leveling & Progression
- Automated or guided level-up process
- Calculate and apply proficiency bonus, hit point increases, and new features
- Handle multiclass level distribution cleanly
- Track XP or milestone progress toward next level

### 3. Feats & Homebrew Features
- Add, remove, and track standard + homebrew feats
- Store feat descriptions, mechanical effects, and prerequisites
- Support custom features from subclasses or magic items

### 4. Inventory & Attunement
- Full item tracking (weapons, armor, wondrous items, consumables)
- Attunement management (max 3 items by default, with homebrew overrides)
- Categorization and searchability
- Weight and carrying capacity tracking (optional)

### 5. Death Saves & Conditions
- Track death saving throws (successes/failures)
- Integrate with `dnd-combat-assistant` for real-time condition and HP updates
- Automatic stabilization or death detection
- Sync conditions back to main combat and world state

### 6. Export & Integration
- Export clean Markdown character sheet (for notes/docs)
- Export structured JSON (for VTT import or external tools)
- Provide summary views optimized for mobile
- Feed current character state into `dnd-visual-weaver`, `dnd-persistent-dm`, and other skills

**Companion System Polish (Medium-Priority Enhancement)**: Evolving companions now have improved cross-skill tracking:
- Stats, bond level, abilities, and visual descriptors are synced more seamlessly between character-manager, combat-assistant, visual-weaver, and kingdom play.
- Visual canon automatically pulls companion evolution stages.
- Leveling or major events for companions can trigger suggested updates across systems.

## Integration with Existing Skills

- **dnd-utils**: Primary state storage using `player_character.json` and `player_character.md`. Uses shared update/audit patterns.
- **dnd-combat-assistant**: Bidirectional sync for HP, conditions, and death saves during combat.
- **dnd-persistent-dm**: The orchestrator should delegate character progression and queries to this skill.
- **dnd-visual-weaver**: Pulls appearance and key descriptors from the managed character sheet.
- **dnd-loot-generator**: Can update inventory when new items are awarded.

## State & File Structure
Character data lives in the campaign folder:
- `state/player_character.json` — Machine-readable authoritative data
- `state/player_character.md` — Human-readable formatted sheet (auto-generated or synced)
- Optional: `state/character_history.md` for leveling log and major changes

All changes should be auditable and backed up via the utils layer.

## Homebrew & Flexibility
- Explicitly designed for heavy homebrew
- Store custom feat text and mechanical effects
- Allow override of standard rules (e.g., attunement limits, death save variants)
- Record house rules related to character progression in the campaign state

## Behavior Guidelines
- Always load current character state before making changes
- Confirm major changes (especially leveling and attunement) with the player
- Keep the `.md` version human-friendly and the `.json` version complete
- After any significant update, suggest running a state sync via `dnd-session-scribe` or `dnd-persistent-dm`
- Provide clear before/after summaries for leveling and major inventory changes

## Integration with Combat & dnd-persistent-dm (Recommended Patterns)

This skill is designed to work closely with `dnd-combat-assistant` and `dnd-persistent-dm`.

**Recommended Flow:**

1. **During Combat**:
   - `dnd-combat-assistant` tracks real-time HP, initiative, and conditions.
   - When a character drops to 0 HP, call `handle_character_downed("Campaign Name")` to initialize death saves.

2. **Death Saves**:
   - Use `apply_death_save("Campaign Name", success=True/False)` for each death save roll.
   - The skill automatically handles stabilization (3 successes) and death (3 failures).

3. **Healing a Dying Character**:
   - Use `apply_healing_while_dying("Campaign Name", amount)` when healing is applied to a character at 0 HP.
   - If healing brings them above 0 HP, they automatically stabilize.

4. **After Combat**:
   - `dnd-persistent-dm` should call `get_death_save_status()` or load the full character to sync final state.
   - Run a state update / session scribe to persist everything.

**Key Functions for Orchestration**:
- `handle_character_downed()`
- `apply_death_save()`
- `apply_healing_while_dying()`
- `stabilize_character()`
- `get_death_save_status()`

This pattern keeps combat fast (via combat-assistant) while maintaining persistent, queryable character state.

## Success Criteria
- Player always has an accurate, up-to-date character representation
- Leveling and feat tracking feel smooth and low-friction
- Death saves and conditions stay in sync with combat
- Exports are clean and usable in external tools
- Homebrew content is tracked as reliably as official content

This skill closes one of the largest remaining gaps in long-term character progression tracking within the D&D skills ecosystem.