---
name: dnd-persistent-dm
description: Play or continue any D&D campaign with Grok as DM. Classic tabletop and kingdom/domain builder modes. v2.0.0 production orchestrator (10/10). Triggers include play D&D, DM mode, continue the campaign, switch to kingdom mode, kingdom actions, generate encounter, update state, end session, what's happening. Supports 5e + heavy homebrew. Orchestrates all D&D skills — coordinates backends and prompt skills. Persistent JSON state per campaign.
---

# D&D Persistent DM

## When to Use
- Player wants to play, continue, or start a D&D campaign
- Any in-game action: explore, talk, fight, rest, kingdom turns
- Switching between tabletop and kingdom/domain mode

**Do not use when:** Pure rules lookup (rules-reference), standalone dice (dice-engine), or voice routing setup (voice-assistant first in voice mode).

## Quick Start (Mobile)
1. Say **"Let's play D&D"** or **"Continue [campaign name]"**.
2. Grok checks `state/world_state.json` — init if missing, recap if exists.
3. Play naturally; Grok delegates combat, dice, loot, lore, rumors, and session saves automatically.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Campaign init & resume | ✅ Implemented | Via dnd-utils `init` / state reads |
| Tabletop narration & pacing | ✅ Implemented | Orchestrator + narration_helpers |
| Kingdom/domain play | ✅ Implemented | Projects + `kingdom_sim.py` consequences |
| Combat orchestration | ✅ Implemented | Delegates to combat-assistant + sync_bridge |
| Dice & loot automation | ✅ Implemented | dice-engine, loot-generator |
| NPC / lore / content routing | ✅ Implemented | npc-weaver, lore-archivist, content-forge |
| Rumors & world events | ✅ Implemented | rumor_generator.py |
| Session end & XP | ✅ Implemented | session-scribe |
| SQLite / analytics | ✅ Implemented | `sqlite_layer.py` via dnd-utils |
| Kingdom simulation | ✅ Implemented | Population, trade, military, cascading effects |
| Visual moment offers | ⚠️ Partial | visual-weaver prompts; image is optional |
| Voice play | ✅ Implemented | Route through voice-assistant first |
| Single orchestrator script | ❌ N/A | Coordination skill — no `persistent_dm.py` |

## Tools & Scripts
Orchestrator invokes specialists — no dedicated script:
```bash
# Bootstrap
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py init "My Campaign" --pc-name "Aria" --enable-sqlite
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py status "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py session-summary "My Campaign"

# During play
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py "1d20+7" --advantage --campaign "My Campaign"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py init "My Campaign" --encounter "Ambush"
python .grok/skills/dnd-combat-assistant/scripts/combat_tracker.py damage "My Campaign" --target "Goblin" --amount 8
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py hoard "My Campaign" --level 5 --cr 4
python .grok/skills/dnd-npc-personality-weaver/scripts/npc_manager.py create "My Campaign" --name "Elder Mara"
python .grok/skills/dnd-content-forge/scripts/generate_monster.py "My Campaign" --theme "Ash wraith" --cr 4 --encounter
python .grok/skills/dnd-character-manager/scripts/character_manager.py inventory "My Campaign" add --name "Healing potion"
python .grok/skills/dnd-lore-archivist/scripts/lore_archivist.py query "My Campaign" "vault"
python .grok/skills/dnd-lore-archivist/scripts/lore_archivist.py append "My Campaign" "The vault is a prison"
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py rumors "My Campaign" --count 3
python .grok/skills/dnd-rumor-event-generator/scripts/rumor_generator.py world-event "My Campaign" --seed unrest
python .grok/skills/dnd-visual-weaver/scripts/visual_prompt_library.py weave-prompt "My Campaign" "Throne room confrontation"

# Kingdom
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py update "My Campaign" --set-mode kingdom
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py queue-project "My Campaign" "Rebuild granary" --turns 3
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py advance-projects "My Campaign"

# Session end
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py end-session "My Campaign" "Summary" --xp 400
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py audit "My Campaign"
```

## Behavior

### iOS output rules
1. **Lead with the answer** — narration second, mechanics in a short block
2. Default replies **≤8 lines** unless player asks for detail
3. Confirm HP/XP/inventory: **before → after**
4. End active scenes: **What do you do?**
5. **Voice mode:** route through `dnd-voice-assistant` first

### Campaign init protocol
1. Identify or ask for campaign name
2. If `state/world_state.json` exists → load, `session-summary`, brief resume
3. If missing → `dnd_state_utils.py init "[name]"` (confirm PC name if new)
4. Never invent state — read JSON before narrating

### Mode handling
| Mode | Focus | Key backends |
|------|-------|--------------|
| **tabletop** | Scenes, combat, social | combat-assistant, dice-engine, npc-weaver |
| **kingdom** | Domain resources, projects, factions | dnd-utils, kingdom_sim, rumor-event-generator |

### Automation patterns
- **Combat:** `combat_tracker init` → add combatants → damage/heal each hit → `end-combat --xp N` → optional `procedural_loot hoard`
- **Significant NPC:** `npc_manager create` after Grok authors personality
- **Lore beat:** `lore_archivist append` after major revelations
- **Downtime / travel:** `rumor_generator rumors` → `record-event`
- **Session end:** `session_scribe end-session` (confirm first)
- **Health check:** `audit` if state feels inconsistent

### Narration helpers
Import `narration_helpers.py` for `format_mobile_status`, `suggest_next_actions`, `build_opening_scene`. Offer proactive suggestions when player says *"What's happening?"* or seems stuck.

## State & Files
Campaign root resolved by `paths.py` (`DND_CAMPAIGNS_ROOT` or `~/.grok/artifacts/dnd-campaigns/[name]/`).

| Path | Purpose |
|------|---------|
| `state/world_state.json` | Location, time, mode |
| `state/player_character.json` | PC sheet |
| `state/kingdom_state.json` | Domain state |
| `state/lore_summary.md` | Canon lore digest |
| `combat/current_combat.json` | Active fight |
| `npcs/` | Persistent NPCs |
| `logs/` | events, rolls, session_log |
| `recaps/` | Session recaps |

## Integration
| Trigger | Delegate to |
|---------|-------------|
| Roll / check / save | dnd-dice-engine |
| Combat | dnd-combat-assistant |
| Character sheet | dnd-character-manager |
| Loot | dnd-loot-generator |
| NPC create/update | dnd-npc-personality-weaver |
| Monster/encounter design | dnd-content-forge |
| Lore query / update | dnd-lore-archivist |
| Rules question | dnd-rules-reference |
| Rumors / world events | dnd-rumor-event-generator |
| Images | dnd-visual-weaver |
| End session | dnd-session-scribe |
| All state I/O | dnd-utils |
| Voice input | dnd-voice-assistant → back here |

## iOS / Voice Notes
- Scannable beats: location line → scene → prompt
- Don't expose raw JSON or script paths to the player
- Confirm campaign init, mode switches, and session end
- Kingdom turns: summarize resources + project progress in 4 lines

## Example Flow
**New campaign**
Player: *"Let's play D&D — campaign Shadowmere"*
→ No `world_state.json` → `init "Shadowmere"`
→ Opening scene + **What do you do?**

**Combat**
Player: *"I attack the captain"*
→ dice-engine `1d20+8` → on hit, damage roll → `combat_tracker damage`
→ *"Captain 45 → 31 HP. Your turn ends. **What do you do?**"*

**Kingdom turn**
Player: *"Advance the domain"*
→ `advance-projects` → `rumor_generator rumors`
→ *"Granary 2 turns left. Rumor: drought in the south. **What do you do?**"*

**End session**
Player: *"Wrap up"*
→ Confirm → `end-session` + recap
→ *"Saved. XP 1,200 → 1,600. See you next time."*