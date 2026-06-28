---
name: dnd-utils
description: Shared Python backend for all D&D skills — campaign init, state, events, kingdom sim, lore index, class progression, faction engine, plus skill_registry and skill_orchestrator for cross-skill coordination. v4.0.0 production foundation. Not player-facing; all skills route through registry for delegation. Triggers include initialize campaign, update location, kingdom mode, queue project, advance projects, audit state, session summary, record event. Not player-facing; other skills invoke it internally. Supports 5e + homebrew campaigns.
---

# D&D Utils

## When to Use
- Bootstrapping or resuming a campaign folder structure
- Reading/writing `world_state.json`, `player_character.json`, `kingdom_state.json`
- Kingdom project queue, turn advancement, and simulation hooks
- Event logging, roll logging, campaign audits, SQLite indexing
- Formatting short mobile status blocks via `narration_helpers.py`

**Do not use when:** The player wants narration, rules, or combat — route to `dnd-persistent-dm` or the specialist skill.

## Quick Start (Mobile)
1. Say **"Start a new campaign called [name]"** — persistent-dm calls init automatically.
2. On resume, Grok reads `state/world_state.json` before narrating.
3. Kingdom turns: **"Advance my domain projects"** → `advance-projects`.

## Capabilities (Honest Matrix)
| Capability | Status | Notes |
|------------|--------|-------|
| Campaign init & folder scaffold | ✅ Implemented | `init` creates state/npcs/logs/recaps/combat |
| World & player JSON read/write | ✅ Implemented | Atomic saves with backups |
| Kingdom project queue/advance | ✅ Implemented | `queue-project`, `advance-projects` |
| Kingdom simulation | ✅ Implemented | `kingdom_sim.py` — population, trade, military, cascading consequences |
| Event log (JSON) | ✅ Implemented | `event_system.py` → `logs/events.json` |
| Roll logging | ✅ Implemented | Used by dice-engine when `--campaign` set |
| Session start summary | ✅ Implemented | `session-summary` command |
| Campaign audit | ✅ Implemented | `audit`, `validate`, `enhanced-audit` |
| Narration helpers | ✅ Implemented | `format_mobile_status`, `suggest_next_actions` |
| SQLite analytics layer | ✅ Implemented | `sqlite_layer.py`; enable via `init --enable-sqlite` |
| Campaign dashboard | ✅ Implemented | `campaign_dashboard.py` — world, PC, combat, quests, kingdom snapshot |
| Campaign analytics | ✅ Implemented | `campaign_analytics.py` — tags, timeline, NPC mentions, SQLite sync |
| Event archive (scale) | ✅ Implemented | `archive-events` moves overflow to `logs/events_archive.json` |
| Combat ↔ character sync bridge | ✅ Implemented | `sync_bridge.py` — HP, healing, death saves |
| Lore FTS5 index | ✅ Implemented | `lore_index.py` — rebuild + semantic search |
| Multiclass / spell slots | ✅ Implemented | `class_progression.py` — prereqs, slot tables, restore |
| Faction simulation engine | ✅ Implemented | `faction_engine.py` — goals, influence, diplomacy graph |
| Grok iOS / PC path resolution | ✅ Implemented | `paths.py` — skills, workspace, campaigns; `runtime-context` CLI |
| Campaign health & quick status | ✅ Implemented | `campaign-health`, `quick-status` via `narration_cli.py` |
| Kingdom mobile summary | ✅ Implemented | `kingdom-mobile` — short voice-friendly domain snapshot |
| Event undo helper | ✅ Implemented | `undo-last` pops last logged event |
| Shared inventory ledger | ✅ Implemented | `inventory_ledger.py` — `add`, `remove`, `list` |

## Tools & Scripts
```bash
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py init "My Campaign" --pc-name "Aria" --enable-sqlite
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py status "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py update "My Campaign" --set-location "Whisperwood" --advance-time 8
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py kingdom-summary "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py queue-project "My Campaign" "Rebuild the watchtower" --turns 4
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py advance-projects "My Campaign" --turns 1
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py audit "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py session-summary "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py record-event "My Campaign" "Party entered the crypt" --tags exploration
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py campaigns-root
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py runtime-context
python .grok/skills/dnd-utils/scripts/skill_registry.py list
python .grok/skills/dnd-utils/scripts/skill_registry.py resolve damage --campaign "My Campaign"
python .grok/skills/dnd-utils/scripts/skill_orchestrator.py plan "My Campaign" "next turn"
python .grok/skills/dnd-utils/scripts/skill_orchestrator.py playbook "My Campaign" kingdom-turn
python .grok/skills/dnd-utils/scripts/skill_orchestrator.py playbook "My Campaign" grid-combat
python .grok/skills/dnd-utils/scripts/skill_orchestrator.py playbook "My Campaign" vtt-export
python .grok/skills/dnd-utils/scripts/skill_orchestrator.py execute "My Campaign" damage --target Goblin --amount 8
python .grok/skills/dnd-utils/scripts/skill_registry.py coordination damage --campaign "My Campaign"
python .grok/skills/dnd-utils/scripts/skill_registry.py graph
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py validate "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py enhanced-audit "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py clear-combat "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py search-events "My Campaign" --tag combat --limit 10
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py query-sql-events "My Campaign" --limit 5
python .grok/skills/dnd-utils/scripts/narration_cli.py mobile-status "My Campaign"
python .grok/skills/dnd-utils/scripts/narration_cli.py opening "My Campaign"
python .grok/skills/dnd-utils/scripts/narration_cli.py suggest "My Campaign"
python .grok/skills/dnd-utils/scripts/narration_cli.py hp-change "My Campaign" --before 32 --after 24
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py dashboard "My Campaign"
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py analytics "My Campaign" --report summary
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py analytics "My Campaign" --report tags
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py analytics "My Campaign" --report sync-sqlite
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py archive-events "My Campaign" --keep 500
python .grok/skills/dnd-utils/scripts/narration_cli.py dashboard "My Campaign"
python .grok/skills/dnd-utils/scripts/narration_cli.py campaign-health "My Campaign"
python .grok/skills/dnd-utils/scripts/narration_cli.py quick-status "My Campaign"
python .grok/skills/dnd-utils/scripts/narration_cli.py kingdom-mobile "My Campaign"
python .grok/skills/dnd-utils/scripts/narration_cli.py undo-last "My Campaign"
python .grok/skills/dnd-utils/scripts/inventory_ledger.py add "My Campaign" --name "Healing potion" --qty 2
python .grok/skills/dnd-utils/scripts/inventory_ledger.py remove "My Campaign" --name "Healing potion" --qty 1
python .grok/skills/dnd-utils/scripts/inventory_ledger.py list "My Campaign"
```

Supporting modules (import-only): `paths.py`, `event_system.py`, `narration_helpers.py`, `bootstrap.py`, `sqlite_layer.py`, `kingdom_sim.py`, `sync_bridge.py`, `lore_index.py`, `class_progression.py`, `faction_engine.py`, `xp_tables.py`, `errors.py`.

Playbooks (v5.3.0, **16**): `campaign-health`, `chaos-campaign`, `downtime`, `end-combat`, `grid-combat`, `kingdom-turn`, `new-campaign`, `party-generator`, `party-to-combat`, `pre-session`, `quick-session`, `random-session`, `session-end`, `start-combat`, `visual-scene`, `vtt-export`

## Behavior
- Resolve campaign root via `paths.py` (`DND_CAMPAIGNS_ROOT` → `~/.grok/artifacts/dnd-campaigns/`).
- Never invent state — load JSON first, write via `save_json`.
- Confirm location/mode/HP changes with before → after when surfacing to the player.
- `advance-projects` may invoke `kingdom_sim.apply_cascading_consequences` on completion.
- Keep replies scannable; use `format_mobile_status` for status checks.

## State & Files
| File | Purpose |
|------|---------|
| `state/world_state.json` | Location, time, mode, weather |
| `state/player_character.json` | PC stats, HP, XP, conditions |
| `state/kingdom_state.json` | Domain resources, projects, factions, military |
| `state/important_companion.json` | Key companion snapshot |
| `state/campaign_index.sqlite` | Optional event index (JSON remains source of truth) |
| `logs/events.json` | Structured event timeline |
| `logs/rolls.json` | Dice roll history |
| `logs/session_log.md` | Append-only session notes |
| `combat/current_combat.json` | Active encounter (combat-assistant) |

## Skill Coordination
| Layer | Role |
|-------|------|
| Registry | `skill_registry.py` — canonical map for all 17 skills |
| Orchestrator | `skill_orchestrator.py` — `plan`, `execute`, `playbook` |
| Mobile (iOS) | `narration_cli.py` — `mobile-status`, `opening`, `hp-change` for short replies |
| sync_bridge | Library module — combat-assistant ↔ character-manager HP sync |

## Integration
- **Called by:** persistent-dm, combat-assistant, character-manager, session-scribe, loot-generator, npc-weaver, visual-weaver, dice-engine
- **Calls:** `event_system.py`, `kingdom_sim.py`, `sqlite_layer.py`, `sync_bridge.py` internally
- **No direct player narration** — use persistent-dm or narration_cli for player-facing text

## iOS / Voice Notes
- Campaign paths auto-resolve on Grok iOS cloud and PC via `paths.py` — no manual setup.
- Run `runtime-context` if a session cannot find campaign files; set `DND_CAMPAIGNS_ROOT` only as last resort.
- Status replies should be ≤8 lines; lead with location + HP.
- Voice sessions still use utils indirectly via persistent-dm routing.

## Example Flow
Player: *"Switch to kingdom mode and queue a granary."*
→ `update --set-mode kingdom` → `queue-project "Granary expansion" --turns 3`
→ Reply: *"Granary queued (3 turns). Gold 100 → unchanged. **What do you do?**"*