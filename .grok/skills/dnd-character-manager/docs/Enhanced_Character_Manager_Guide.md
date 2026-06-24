# Enhanced dnd-character-manager Guide (v0.4)

## Overview

`dnd-character-manager` is the authoritative character sheet engine for long-term D&D campaigns. It provides persistent, structured tracking for player characters with strong support for **homebrew**, **multiclassing**, **death saves**, and **companions**.

It integrates tightly with:
- `dnd-persistent-dm` (orchestrator)
- `dnd-combat-assistant`
- `dnd-utils` (state management)
- `dnd-visual-weaver`

---

## Key Features by Version

### Phase 1 (v0.2)
- **Configurable Attunement Maximum** — Change from the default 3 via `set_attunement_max()`
- **Rolled or Averaged HP on Level Up** — Supports both `hp_increase_method="average"` and `"roll"` with manual confirmation via `apply_level_up_hp_roll()`

### Phase 2 (v0.3)
- **Richer Markdown Exports** — Includes ability modifiers, saving throws, calculated skills, and correct attunement display
- **Automatic Derived Stat Recalculation** — `recalculate_derived_stats()` runs after level-ups and feat additions

### Phase 3 (v0.4)
- **Smart Level-Up Suggestions** — `suggest_level_up_options()` provides ASI recommendations, feat ideas, and subclass hints
- **Lightweight Companion Support** — Track animal companions, sidekicks, or important NPCs separately

---

## Core Functions

### Leveling
```python
level_up(campaign_name, levels=1, class_name=None, hp_increase_method="average")
apply_level_up_hp_roll(campaign_name, rolled_total)
suggest_level_up_options(campaign_name)
```

### Feats & Progression
```python
add_feat(campaign_name, feat_name, description="", effects=None)
record_asi_or_feat(campaign_name, level, choice, details="")
```

### Inventory & Attunement
```python
update_inventory(campaign_name, action="add|remove|attune|unattune|equip", item={})
set_attunement_max(campaign_name, new_max)
```

### Companions (Phase 3)
```python
add_companion(campaign_name, companion_data)
get_companion(campaign_name, name)
update_companion(campaign_name, name, updates)
remove_companion(campaign_name, name)
list_companions(campaign_name)
```

**Companion Combat Hooks** (new in latest refinement):
```python
update_companion_hp(campaign_name, name, delta=-damage)
apply_damage_to_companion(campaign_name, name, damage)
get_companion_combat_status(campaign_name, name)
add_companion_to_combat(campaign_name, name)   # Returns data ready for combat-assistant
```

### Derived Stats & Export
```python
recalculate_derived_stats(campaign_name)
generate_character_markdown(campaign_name, character)  # Usually called automatically
```

---

## Recommended Workflows

### Leveling Up
1. Call `level_up()` (it now returns suggestions automatically)
2. Review `result["suggestions"]`
3. If using rolled HP, follow up with `apply_level_up_hp_roll()`
4. The system automatically recalculates derived stats

### Managing Companions
Use companions for:
- Animal companions / familiars
- Sidekicks
- Important bonded NPCs or creatures

They are stored separately in `state/companions.json`.

### After Major Changes
Always consider calling:
```python
recalculate_derived_stats("Campaign Name")
```

---

## Integration Notes

- **With `dnd-persistent-dm`**: 
  - After calling `level_up()`, present suggestions.
  - Proactively include `get_companion_status_summary()` in session briefings and at combat start for companion awareness.
- **With Combat**: Use `handle_character_downed()`, `apply_death_save()`, and `apply_healing_while_dying()` for the main character. For companions, use the enhanced combat hooks including HP tracking, conditions, and basic death saves (`update_companion_hp`, `add_condition_to_companion`, `handle_companion_downed`, `get_companion_combat_status`, `add_companion_to_combat`).
- **With Visuals**: The richer character data improves prompt quality in `dnd-visual-weaver`.

---

## Future Roadmap Ideas

- Deeper multiclass feature tracking
- Full skill proficiency management
- Companion integration into combat tracking (advanced filters + `get_companion_status_summary()`)
- Stronger subclass and subclass feature suggestions

---

*Maintained as part of the D&D Skills Suite • Version 0.4*