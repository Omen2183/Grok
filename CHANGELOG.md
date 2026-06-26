# Changelog

## 4.1.0 — Unified Randomizer skill (skill #17)

### Added
- **`dnd-randomizer`** — unified chaos randomization hub
  - `randomizer.py` — tables, items, characters, NPCs, worlds, encounters, quests, feats, spells, `random-everything`, `apply-*`
  - `randomizer_engine.py` — weighted rolls, ledger, custom homebrew tables
  - `randomizer_data.py` — races, classes, feats, items, weather, terrain, hooks, names
- Registry intent `random`, playbook `chaos-campaign`
- `dnd-randomizer/tests/test_randomizer.py`

### Changed
- Suite expanded to **17 skills**; `skill_registry.py`, `validate_backends.py`, README updated

## 4.0.0 — 10/10 gap closure: lore FTS, grid combat, SRD index, VTT export, factions, multiclass

### Added
- `lore_index.py` — FTS5 semantic lore search (events, recaps, NPCs, lore_summary)
- `class_progression.py` — multiclass prereqs, spell slot tables, build validation
- `faction_engine.py` — faction goals, diplomacy graph, simulation rounds
- `srd_data.py` — SRD spell/feat index (15 spells, 12 feats)
- `grid_combat.py` — tactical grid (place, move, distance, AoE, obstacles)
- `vtt_export.py` — Foundry + Roll20 character/combat JSON export
- `lore_archivist` CLIs: `search`, `rebuild-index`
- `rules_cheatsheet` CLIs: `spell`, `feat`, `search-spells`, `search-feats`
- `character_manager` CLIs: `spell-slots`, `validate-multiclass`, `build-plan`
- `rumor_generator` CLIs: `faction-sim`, `diplomacy-graph`
- `visual_prompt_library` CLI: `weave-map` (battle map from grid state)
- Playbooks: `grid-combat`, `vtt-export`; `kingdom-turn` includes faction sim
- `tests/test_v4_features.py` — lore, grid, SRD, VTT, faction, multiclass tests
- `.gitignore` — excludes `__pycache__`, stale exports, campaign artifacts

### Removed
- `dnd-skills-source/`, `grok-dnd-skills-export/`, archive zips/tarballs (stale duplicates)

### Changed
- `pyproject.toml` version → 4.0.0
- Long rest restores spell slots via `class_progression`
- `query_lore` uses FTS5 results alongside keyword fallback
- Level-up recalculates spell slots for casters
- All affected SKILL.md capability matrices updated to ✅

## 3.4.0 — Dashboard, analytics, registry sync, E2E playbooks, PLAYERS.md

### Added
- `campaign_dashboard.py` — unified campaign snapshot + mobile summary
- `campaign_analytics.py` — tag counts, session timeline, NPC mention frequency, SQLite backfill, event archiving
- `dnd_state_utils` CLIs: `dashboard`, `analytics`, `archive-events`
- `narration_cli dashboard` — mobile-friendly full snapshot
- `scripts/registry_sync.py` — discover skills, validate registry, `--check` CI gate, `--fix-scripts`
- `tests/test_playbook_session_end.py` — E2E `session-end` playbook
- `tests/test_campaign_dashboard.py` — dashboard + analytics + archive tests
- **PLAYERS.md** — human-facing quickstart for Grok iOS players/DMs

### Changed
- CI runs `registry_sync.py --check`
- Smoke test covers dashboard + analytics
- `dnd-utils` SKILL.md documents new CLIs and capabilities matrix rows
- `init --force` resets `events.json` and `rolls.json` for a clean slate
- Test fixture sets `DND_CAMPAIGNS_ROOT` so playbook subprocesses share isolated state

## 3.3.0 — Comprehensive dice engine expansion

### Added
- **dnd-dice-engine** `dice_roller.py` v3.3.0:
  - True multi-pool expressions (`1d8+1d6+5`, signed terms)
  - Fudge dice (`4dF`, -1/0/+1)
  - Per-pool keep/exploding (`2d6kh3!`)
  - Reroll-below (`--reroll-below`) for GWF-style mechanics
  - `apply_damage_modifiers` — resistance, vulnerability, immunity, flat reduction
  - `roll_crit` / `crit` CLI — double damage dice on crits
  - `count_successes` / `count-successes` CLI — target-number systems
  - `modify-damage` CLI
- 8 new dice engine tests (multi-pool, fudge, crit, damage modifiers)

### Changed
- `parse_dice_notation` returns legacy single-pool shape for simple notation (backward compatible)
- `DICE_BACKEND_VERSION = 3.3.0`

## 3.2.1 — Documentation sweep + Grok iOS integration hardening

### Added
- `scripts/validate_skill_docs.py` — verifies SKILL.md documents all CLI commands, Skill Coordination, and iOS/Voice sections
- `scripts/extract_cli_commands.py` — helper to list subcommands per skill
- `test_paths.py` — `DND_CAMPAIGNS_ROOT` and `GROK_ARTIFACTS_ROOT` resolution tests
- **Skill Coordination** section in all 16 SKILL.md files (registry → orchestrator → playbooks → voice)

### Changed
- All 16 `SKILL.md` files updated with honest capability matrices and complete CLI examples
- `paths.py` — Grok iOS host env vars (`GROK_ARTIFACTS_ROOT`, `GROK_USER_DATA`, `GROK_HOME`) + mobile path candidates
- `procedural_loot.py` — uses `bootstrap`/`paths` instead of hardcoded `/home/workdir/` fallback
- `_PRODUCTION_CONVENTIONS.md` — SKILL.md requirements checklist + iOS path notes
- CI runs `validate_skill_docs.py`

## 3.2.0 — Full Python backends for all 16 skills

### Added
- **dnd-downtime-manager** — hit-dice spending, activity ledger, class-based HD recovery (`DOWNTIME_BACKEND_VERSION = 3.2.0`)
- **dnd-npc-personality-weaver** — personality generation, search, relationship tiers, what-knows, append-note (`NPC_BACKEND_VERSION = 3.2.0`)
- **dnd-rules-reference** — `rules_data.py` with 25+ topics; search, condition, homebrew CLIs (`RULES_BACKEND_VERSION = 3.2.0`)
- **dnd-rumor-event-generator** — faction moves, rumor ledger persistence, list/ledger CLIs (`RUMOR_BACKEND_VERSION = 3.2.0`)
- **dnd-voice-assistant** — execute/plan/format-spoken/detect-voice/confirm-check pipeline (`VOICE_BACKEND_VERSION = 3.2.0`)
- **dnd-dice-engine** — parse, percentile, check/attack/save, history CLIs (`DICE_BACKEND_VERSION = 3.2.0`)
- **dnd-loot-generator** — summary, search-ledger, tables CLIs (`LOOT_BACKEND_VERSION = 3.2.0`)
- **dnd-visual-weaver** — status CLI for canon/companion state (`VISUAL_BACKEND_VERSION = 3.2.0`)
- `tests/test_full_backends.py` — integration tests for expanded backends
- `validate_backends.py` — `MIN_CLI_COMMANDS = 5`; library-only whitelist for `dnd-utils` shared modules

### Changed
- All 16 skills now pass backend validation (≥5 CLI commands + smoke tests)
- `dnd-utils` library modules (`event_system`, `sync_bridge`, `kingdom_sim`, etc.) exempt from per-file CLI requirement

## 3.1.1 — Complete combat sync_bridge wiring

### Fixed
- `sync_combatant_to_character` now runs full bridge logic: HP via `on_player_damaged`, death save reconciliation, Unconscious condition on sheet
- `apply_damage`, `apply_healing`, and `record_death_save` all call `sync_combatant_to_character` after bridge hooks (not HP-only)
- Import failure now logs CRITICAL warning when sync_bridge is unavailable (no silent stub mode)
- `COMBAT_SYNC_VERSION` marker in combat_tracker for deployment verification

### Notes
- GitHub had wiring since v3.0.2; Grok cloud `/home/workdir/.grok/skills/` and stale local copies may lag — pull v3.1.1 and run `install.ps1 -Global`

## 3.1.0 — Full backend audit & hardening pass

### Added
- `scripts/validate_backends.py` — multi-level audit: compile check, CLI detection, per-skill smoke invocation
- `dice_roller initiative` subcommand (legacy `roll` notation shim preserved)
- `character_manager sync` CLI for post-combat sheet reconciliation
- `session_scribe append-log`, `quest_tracker complete-objective`, `lore_archivist list-npcs` / `list-recaps`
- `dnd_state_utils query-sql-events` for SQLite-enabled campaigns
- `kingdom_sim.advance_kingdom_turn_simulation` wired into `advance-projects`
- Rumor persistence by default (`--no-persist` to opt out)
- Faction-aware domain event chains in `kingdom_sim`
- Voice routing now calls `skill_orchestrator.enrich_route`; attune/init intent detection
- Integration tests for XP-on-end-combat, rumor persist, initiative, sync CLI

### Fixed
- `end_combat --xp` now awards XP to `player_character.json` via session-scribe
- Playbook `initiative` and `sync` commands now map to real CLIs
- `rumor_generator` imports `record_event` from `event_system` directly

## 3.0.2 — Combat sync verification & end-of-combat reconciliation

### Added
- `end_combat` calls `sync_combatant_to_character` for player PCs before archiving combat state
- Integration tests proving `apply_damage`, `apply_healing`, `record_death_save`, and `end_combat` sync via `sync_bridge`

### Fixed
- `sync_bridge.on_player_damaged` now writes combat HP to the character sheet (was only setting Dying status at 0 HP)
- `handle_character_downed` explicitly zeroes sheet HP when a PC drops

### Notes
- GitHub `combat_tracker.py` already wires `sync_bridge` in damage/heal/death-save paths (v3.0.0+). Cloud/local copies that only call `update_player_hp` should pull this repo to restore full dying/stable/healing logic.

## 3.0.1 — Event system hardening

### Added
- `paths.ensure_dir` and `paths.backup_file` — shared helpers for atomic writes and backups
- `search_events` filters for `event_type` and `importance` (comma-separated)
- `search-events` CLI flags: `--type`, `--importance`
- Tests for path helpers and event search filters

### Fixed
- Event log writes now back up `events.json` before atomic replace (matches state save pattern)
- Aligns cloud sandbox fixes with the GitHub repo

## 3.0.0 — Production orchestration (10/10)

### Added
- `skill_registry.py` — canonical intent→skill map, playbooks, coordination graph
- `skill_orchestrator.py` — `plan`, `execute`, `playbook` cross-skill runner
- `persistent_dm` commands: `execute`, `playbook`, `registry`
- Playbooks: new-campaign, start-combat, end-combat, session-end, kingdom-turn, downtime
- Session scribe pulls active quests/hooks into recaps automatically
- Orchestration integration tests (70+ total tests)
- `_PRODUCTION_CONVENTIONS.md` skill coordination section

### Changed
- All routing flows through registry before skill invocation
- Voice routes include coordination hints for orchestrator enrichment
- persistent-dm is the required hub for multi-skill sequences

## 2.2.0 — Full Python backend coverage

### Added
- `persistent_dm.py` — orchestrator CLI (init, resume, route, kingdom-turn, health)
- `encounter_builder.py` and `content_forge.py` — encounters, quests, factions, domain events
- `narration_cli.py` — mobile status and opening helpers
- **New skill:** `dnd-downtime-manager` — short/long rest, downtime activity log
- **New skill:** `dnd-quest-tracker` — quests and session hooks
- `session_scribe auto-recap` and `end-session --auto`
- `character_manager suggest-level-up` and `companion` CLI
- `voice_utils.py` CLI (`route`, `parse`)
- 16 skills total — every skill has a Python CLI backend

### Fixed
- `character_manager` — moved `if __name__` to end so phase-3 helpers work in CLI

### Changed
- Smoke test covers all 16 skill CLIs
- `validate_skills.py` requires scripts/ on every skill
- Voice routing extended for rest and quest intents

## 2.1.0 — Strengthening pass

### Added
- `xp_tables.py` — 5e XP thresholds, level-up detection on XP awards
- `rules_cheatsheet.py` — CLI quick-reference for common 5e rulings
- `validate_campaign()` and `enhanced_audit_campaign()` in dnd-utils
- Combat `summary` CLI command (human-readable mobile/voice output)
- Visual weaver `weave-kingdom` and `append-canon` commands
- `save_stat_block()` in content-forge; reference data for encounters and loot
- `scripts/validate_skills.py` — SKILL.md structure validator
- Dice: d100 percentile, d3 (d6/2), advantage/disadvantage cancellation
- Expanded tests (40+), smoke test coverage for new CLIs

### Fixed
- NPC `update --note` now appends instead of replacing notes
- Removed stale TODO in character_manager (markdown generation already wired)

### Changed
- Voice assistant routes more intents (next turn, loot, rumors, conditions)
- Session scribe reports level-up availability after XP awards

## 2.0.0 — Production (10/10 target)

### Added
- `sqlite_layer.py` — optional SQLite event index synced from JSON
- `kingdom_sim.py` — population, trade, military, cascading project consequences
- `sync_bridge.py` — bidirectional combat ↔ character death save / HP sync
- `lore_archivist.py` — append, query, and summarize campaign lore
- `rumor_generator.py` — procedural rumors and world events from state
- `errors.py` — standard CLI error envelope
- Shared `conftest.py` campaign fixtures
- Integration test: full session flow (27 tests total)
- `scripts/smoke_test.py` — CLI smoke test for all backends
- GitHub Actions CI (Python 3.11 + 3.12)

### Fixed
- `character_manager` CLI `--class` reserved keyword syntax error
- Combat death saves sync to player character sheet
- Kingdom project completion triggers cascading consequences

### Changed
- All 14 `SKILL.md` files updated for honest 10/10 capability matrices
- Version bumped to 2.0.0

## 1.0.0
- Initial installable skill pack restructure