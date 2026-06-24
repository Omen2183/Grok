---
name: dnd-combat-assistant
description: Use during combat encounters to track initiative, HP, conditions, and turn order. Triggers include start combat, initiative, next turn, damage to, add condition, end combat. Provides clean text-based combat tracking optimized for mobile play. Works with any campaign.
---

# Dnd Combat Assistant

## Overview
A reliable, mobile-optimized combat tracker that removes bookkeeping friction during fights. It handles initiative, hit points, conditions, turn order, and state synchronization so the game stays focused on tactics, narrative, and player decisions rather than manual tracking. This skill integrates tightly with the central state layer for long-term coherence.

## When to Activate
- "Start combat" or "Roll initiative"
- "Next turn"
- "[Player] takes 12 damage"
- "Add Frightened to the bandit"
- "Show combat status"
- "End combat"

## Core Capabilities
- Track initiative order with names and current HP
- Apply damage and healing
- Track conditions
- Advance turns cleanly
- Display combat status in a clear, readable format
- Support both player characters and NPCs/monsters

**New Python Backend**: Uses `scripts/combat_tracker.py` + shared `dnd_state_utils` for reliable JSON state, automatic player/companion HP sync, and persistence across turns/sessions.

## Recommended Behavior
- **Combat Start**: Ask for or accept initiative rolls and establish clear order.
- **During Combat**: Clearly indicate whose turn it is. Track HP and conditions accurately.
- **Damage & Effects**: Confirm changes and update state immediately.
- **End of Combat**: Provide a brief summary and reset the tracker.
- **Output Style**: Keep responses concise and mobile-friendly by default. Use clear formatting for status updates.

**Success Criteria**
- Initiative order and current turn are always clear.
- HP and conditions are accurately tracked.
- Major outcomes (deaths, loot, alliances) are handed off to persistent-dm at combat end.

## State Handling & Integration (Improved — Persistent Combat State)
This skill now maintains **persistent combat state** during encounters using a temporary file for reliability across messages.

**Combat State File**:
- Path: `/home/workdir/artifacts/dnd-campaigns/[campaign-name]/combat/combat_state.json`
- Contents: initiative order, current HP for all participants, active conditions, turn counter, and notes.
- **Strongly Recommended**: Use the new Python backend:
- `python3 /home/workdir/.grok/skills/dnd-combat-assistant/scripts/combat_tracker.py ...` for all tracking
- `python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py clear-combat "Name"` after fights end
- The tracker automatically syncs player & companion HP back to main campaign state.

**State Protocol (Follow Strictly)**:
1. **Combat Start** ("Start combat", "Roll initiative"):
   - Use `save_combat_state()` (or manually ensure the file exists) to initialize a clean combat state.
   - Collect or roll initiative (delegate to `dnd-dice-engine`).
   - Build the full combat state dict and save it using the helper.
   - Display clean, mobile-friendly initiative order + current status.

2. **During Combat** (every update):
   - Load current state with `load_combat_state(campaign_name)`.
   - Apply the requested change (damage, healing, condition, next turn, etc.).
   - Immediately save the updated state using `save_combat_state()`.
   - Confirm the change and show updated relevant status (especially whose turn it is).

3. **Combat End** ("End combat"):
   - Display final summary (who survived, key events, loot, conditions).
   - Use `clear_combat_state(campaign_name)` to remove the temporary combat file.
   - **Strongly recommended**: Automatically record the combat outcome using one of:
     - `record_combat_outcome()` (simple)
     - `smart_record_event()` (intelligent classification + auto-tagging)
   - Pass all mechanically important outcomes to `dnd-persistent-dm` so they are recorded in long-term state (and auto-synced to SQLite if enabled).
   - Example:
     ```python
     record_combat_outcome("Campaign", "Victory against shadow cultists",
                           enemies_defeated=["High Priest"], importance="normal")
     ```

**Minimal Fallback if Combat State File Missing**

If `/combat/combat_state.json` does not exist when combat starts:
- Create a fresh combat state file.
- Initialize with the current participants and rolled initiative.
- Note in the response: “New combat tracker started.”
- At combat end, still attempt to hand off major outcomes to `dnd-persistent-dm`.

**Large Combats (25+ participants)** — Improved Support:
- Use `add_combatant(..., group_size=N)` or `add_combatant_group()` to track large numbers of similar creatures.
- **Smart Group Damage**: Applying damage to groups automatically kills members and reduces `group_size` as HP thresholds are crossed.
- Status shows live group size (e.g. "Goblin Archers x7").
- At combat end, use `smart_record_event()` with scale descriptions for good logging.
- Best practice: Track key individuals normally + use groups for minions.

## Example Flow
You: "Start combat with the shadow cultists. I rolled 18 on initiative."
→ Skill builds order and shows current status.

You: "Next turn"
→ Skill advances and shows whose turn it is.

You: "The cultist takes 14 damage"
→ Skill updates HP and notes if anyone drops.

This skill removes the friction of manual tracking during mobile sessions.