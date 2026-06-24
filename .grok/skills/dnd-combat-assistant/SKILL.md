---
name: dnd-combat-assistant
description: Combat encounter tracker for initiative, HP, healing, conditions, concentration, death saves, and turn order. Triggers include start combat, roll initiative, next turn, damage to [target], heal [target], apply condition, end combat. Mobile-first text combat for any D&D campaign. Syncs HP to central state on end-combat.
---

# D&D Combat Assistant

## When to Use
- Starting or running an active encounter
- Tracking initiative, HP, temp HP, conditions, concentration
- Applying damage/healing with before → after confirmation
- Ending combat and syncing player HP to campaign state

**Do not use when:** Out of combat (use character-manager), rules questions (rules-reference), or loot rolls (loot-generator).

## Quick Start (Mobile)
1. Say **"Start combat — goblin ambush"** to init and add combatants.
2. On your turn: **"I hit the goblin for 9"** → damage applied, HP shown.
3. Say **"Next turn"** until done, then **"End combat, 150 XP"**.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Init & add combatants | ✅ Implemented | Player, companion, monster flags |
| Initiative & turn order | ✅ Implemented | `next-turn`, `status` |
| Damage & healing | ✅ Implemented | Syncs player/companion HP via dnd-utils |
| Temp HP, conditions, concentration | ✅ Implemented | Duration rounds supported |
| Death saves | ✅ Implemented | Success/failure tracking |
| End combat + XP hook | ✅ Implemented | Clears combat file, records outcome |
| Mass combat resolver | ✅ Implemented | Abstract kingdom-scale battles |
| Auto-roll monster initiative | ⚠️ Partial | Manual `--initiative` required on add |
| Visual battle maps | ❌ Prompt-only | Text tracker only |

## Tools & Scripts
```bash
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py init "My Campaign" --encounter "Goblin Ambush"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py add "My Campaign" --name "Aria" --hp 32 --initiative 18 --player
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py add "My Campaign" --name "Goblin 1" --hp 7 --initiative 12 --group-size 3
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py damage "My Campaign" --target "Goblin 1" --amount 9
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py heal "My Campaign" --target "Aria" --amount 8
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py next-turn "My Campaign"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py status "My Campaign"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py apply-condition "My Campaign" --target "Aria" --condition "Poisoned" --duration-rounds 3
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py end-combat "My Campaign" --xp 150
```

## Behavior
- Lead with whose turn it is and target HP after each change.
- Confirm: *"Goblin 1: 7 → 0 HP (down)."*
- End scenes with **What do you do?** between player turns.
- On `end-combat`, sync PC HP to `player_character.json`.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `combat/current_combat.json` | R/W | Combatants, round, turn index, log |
| `state/player_character.json` | W | HP sync on end-combat |
| `state/important_companion.json` | W | Companion HP sync |

## Integration
- **Uses:** dnd-utils (`update_player_hp`, `record_combat_outcome`)
- **Called by:** persistent-dm, voice-assistant (damage/healing phrases)
- **Pairs with:** dice-engine (attack rolls), loot-generator (post-fight rewards)

## iOS / Voice Notes
- Keep combat blocks ≤6 lines: turn → HP snapshot → prompt.
- Voice: *"Goblin takes 8 damage"* parsed by voice-assistant → `damage` command.

## Example Flow
→ `init` → `add` PC + monsters → `status` shows order
→ Player attacks → dice-engine roll → `damage --amount 11`
→ *"Goblin 1 down. Round 2 — your turn. **What do you do?**"*