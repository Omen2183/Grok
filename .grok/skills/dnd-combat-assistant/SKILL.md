---
name: dnd-combat-assistant
description: Combat encounter tracker for initiative, HP, healing, conditions, concentration, death saves, and turn order. v4.0.0 production. Triggers include start combat, roll initiative, next turn, damage to [target], heal [target], apply condition, end combat. Mobile-first text combat for any D&D campaign. Syncs HP and death saves to character sheet via sync_bridge.
---

# D&D Combat Assistant

## When to Use
- Starting or running an active encounter
- Tracking initiative, HP, temp HP, conditions, concentration
- Applying damage/healing with before → after confirmation
- Death saves with bidirectional character-sheet sync
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
| Initiative & turn order | ✅ Implemented | `next-turn`, `status`, `summary` |
| Damage & healing | ✅ Implemented | `apply_healing()` + `heal` CLI |
| Temp HP, conditions, concentration | ✅ Implemented | Duration rounds supported |
| Death saves | ✅ Implemented | Success/failure tracking |
| Death save ↔ character sync | ✅ Implemented | `sync_bridge.on_player_death_save` |
| HP sync on damage/heal | ✅ Implemented | `sync_bridge` for player PC |
| End combat + XP hook | ✅ Implemented | Clears combat file, records outcome |
| Mass combat resolver | ✅ Implemented | Abstract kingdom-scale battles |
| Grid tactical combat | ✅ Implemented | `grid_combat.py` — positions, movement, AoE, cover |
| Auto-roll monster initiative | ✅ Implemented | `--auto-initiative` on `add`; `seed-from-party` for PCs |
| Visual battle maps | ✅ Implemented | Grid state + visual-weaver `weave-map` prompts |

## Tools & Scripts
```bash
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py init "My Campaign" --encounter "Goblin Ambush"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py add "My Campaign" --name "Aria" --hp 32 --initiative 18 --player
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py add "My Campaign" --name "Goblin 1" --hp 7 --auto-initiative --cr 0.25 --group-size 3
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py seed-from-party "My Campaign"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py summary "My Campaign" --dm-screen
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py damage "My Campaign" --target "Goblin 1" --amount 9
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py heal "My Campaign" --target "Aria" --amount 8
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py next-turn "My Campaign"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py status "My Campaign"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py summary "My Campaign"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py death-save-success "My Campaign" --target "Aria"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py death-save-failure "My Campaign" --target "Aria"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py apply-condition "My Campaign" --target "Aria" --condition "Poisoned" --duration-rounds 3
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py apply-temp-hp "My Campaign" --target "Aria" --amount 5
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py set-concentration "My Campaign" --caster "Aria" --spell "Bless"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py tick-conditions "My Campaign"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py remove "My Campaign" --target "Goblin 1"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py resolve-mass-combat "My Campaign" --attacker "Kingdom forces" --defender "Bandits" --scale medium
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py end-combat "My Campaign" --xp 150
python .grok/skills/dnd-combat-assistant/scripts/grid_combat.py init-grid "My Campaign" --width 20 --height 20 --terrain forest
python .grok/skills/dnd-combat-assistant/scripts/grid_combat.py place "My Campaign" "Aria" 10 8 --size medium
python .grok/skills/dnd-combat-assistant/scripts/grid_combat.py move "My Campaign" "Aria" 12 8 --speed 30
python .grok/skills/dnd-combat-assistant/scripts/grid_combat.py distance "My Campaign" "Aria" "Goblin 1"
python .grok/skills/dnd-combat-assistant/scripts/grid_combat.py aoe "My Campaign" 12 8 15
python .grok/skills/dnd-combat-assistant/scripts/grid_combat.py add-obstacle "My Campaign" 11 7 --cover half --label "tree"
python .grok/skills/dnd-combat-assistant/scripts/grid_combat.py summary "My Campaign"
```

Primary scripts: `combat_tracker.py` (`init`, `add`, `seed-from-party`, `damage`, `heal`, `summary`, `--dm-screen`), `grid_combat.py` (tactical grid).

## Behavior
- Lead with whose turn it is and target HP after each change.
- Confirm: *"Goblin 1: 7 → 0 HP (down)."*
- Player death saves sync to `player_character.json` via `sync_bridge`.
- End scenes with **What do you do?** between player turns.
- On `end-combat`, sync PC HP to `player_character.json`.

## State & Files
| File | R/W | Contents |
|------|-----|----------|
| `combat/current_combat.json` | R/W | Combatants, round, turn index, log |
| `state/player_character.json` | W | HP/death-save sync via sync_bridge |
| `state/important_companion.json` | W | Companion HP sync |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | `damage`, `healing`, `next_turn`, `combat_status` intents → this skill |
| Orchestrator | `plan` chains dice-engine attack roll → `damage` on hit |
| Playbooks | `start-combat` (init), `end-combat` (end + loot + sync) |
| sync_bridge | **Required** on PC damage/heal/death-saves — never skip sheet sync |

## Integration
- **Uses:** dnd-utils (`update_player_hp`, `record_combat_outcome`, `sync_bridge`)
- **Called by:** persistent-dm, voice-assistant (damage/healing phrases)
- **Pairs with:** dice-engine (attack rolls), loot-generator (post-fight rewards), character-manager (death saves)

## iOS / Voice Notes
- Keep combat blocks ≤6 lines: turn → HP snapshot → prompt.
- Voice: *"Goblin takes 8 damage"* parsed by voice-assistant → `damage` command.

## Example Flow
→ `init` → `add` PC + monsters → `status` shows order
→ Player attacks → dice-engine roll → `damage --amount 11`
→ *"Goblin 1 down. Round 2 — your turn. **What do you do?**"*