# Changelog

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