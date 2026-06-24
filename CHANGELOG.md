# Changelog

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