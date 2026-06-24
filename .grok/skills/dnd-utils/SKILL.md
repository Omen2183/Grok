---
name: dnd-utils
description: Shared Python backend library and state management utilities used by all other D&D skills. Provides reliable campaign initialization, JSON state persistence, HP/condition tracking, time advancement, and common helpers. Not usually called directly by the player — other skills invoke it internally.
---

# D&D Utils (Shared Python Library)

## Purpose
This is the **foundational backend** of the entire D&D skill suite. It delivers deterministic, auditable, file-based state management that feels native to Grok — reliable, transparent, and engineered for long-term campaign coherence.

It eliminates hallucinated or drifting state, ensures consistency across dozens or hundreds of sessions, and makes complex tracking (combat, kingdom/domain play, companions, and events) robust and production-ready.

Every other D&D skill is architected to leverage these utilities rather than relying on fragile in-prompt memory. This is what makes the suite feel seamless and trustworthy over extended play.

## Location of Scripts
`/home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py`

## Core Capabilities (via dnd_state_utils.py)

### 1. Campaign Initialization
```bash
python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py init "My Campaign Name"
python3 ... init "My Campaign" --force          # Reset with backup
python3 ... init "My Campaign" --pc-name "Custom Name"
```

Creates full folder structure + seeds:
- `state/world_state.json`
- `state/player_character.json` + `.md` view (sensible generic defaults — easily customized with your character)
- `state/important_companion.json` (optional, for campaigns with a major evolving companion)
- `state/kingdom_state.json`
- `logs/session_log.md`
- Standard subdirs: npcs/, combat/, encounters/, recaps/, backups/

### 2. Status & Inspection
```bash
python3 .../dnd_state_utils.py status "My Campaign"
```

Returns clean JSON with current location, time, mode, player HP, etc.

### 3. State Updates (Safe & Audited)
```bash
python3 .../dnd_state_utils.py update "My Campaign" --set-location "Shadow Harbor"
python3 .../dnd_state_utils.py update "My Campaign" --advance-time 6
python3 .../dnd_state_utils.py update "My Campaign" --set-mode kingdom
```

**Kingdom Mode Helpers (Enhanced — Deeper Simulation Layer Added)**
Use these for deeper domain play (all optional and narrative-first):
- `get_kingdom_state`
- `queue_kingdom_project` (status, turns_remaining, dependencies, costs/rewards)
- `advance_kingdom_projects` (advances time and completes projects)
- `process_resource_flows` (passive income/expense)
- `adjust_faction_influence` (with attitude + history)
- `get_kingdom_summary`

**New Lightweight Kingdom Simulation Helpers (High-Priority Addition)**:
- `simple_population_update()` — Tracks rough population changes based on projects, events, and migration. Opt-in via kingdom_state.json flag.
- `process_trade_flows()` — Simple supply/demand and trade route impact simulation (affects resources and faction standing).
- `update_military_units()` — Basic tracking of domain military strength, recruitment, and losses from events.
- `apply_cascading_consequences()` — After major projects or events, automatically suggests or applies follow-on effects (e.g., successful watchtower → reduced bandit activity + minor trade boost).
- `generate_domain_event_chain()` — Creates linked event sequences for more dynamic kingdom play.
These keep the focus narrative while adding satisfying mechanical feedback. Enable via flags in kingdom_state.json.

**Optional SQLite Layer (for long campaigns)**
Enable during init for powerful SQL queries on events, factions, and projects:
```bash
python3 .../dnd_state_utils.py init "My Campaign" --enable-sqlite
```
- `sqlite_layer.py` provides `query_events_sql()`, `sync_event_to_sqlite()`, faction trends, etc.
- JSON/Markdown files remain the source of truth. SQLite is an opt-in query accelerator.

### 4. Audit & Cleanup
```bash
python3 .../dnd_state_utils.py audit "My Campaign"          # Health check + list issues
python3 .../dnd_state_utils.py clear-combat "My Campaign"   # Clean temp combat state after fights
```

### 5. Loading Specific State (for other scripts/skills)
```bash
python3 .../dnd_state_utils.py load "My Campaign" --file world_state
python3 .../dnd_state_utils.py load "My Campaign" --file player_character
python3 .../dnd_state_utils.py load "My Campaign" --file important_companion
```

### 6. Programmatic Use (import in other Python scripts)
```python
from dnd_state_utils import (
    init_campaign, get_campaign_path, get_world_state,
    update_world_state, update_player_hp, add_condition,
    audit_campaign, clear_combat_state
)
```

result = init_campaign("Shadows of the Veil")
state = get_world_state("Shadows of the Veil")
new_hp = update_player_hp("Shadows of the Veil", delta=-8)

# Automated session briefing
summary = generate_session_start_summary("Shadows of the Veil")
print(summary["briefing_markdown"])

# Record events (auto-syncs to SQLite if enabled)
record_event("Shadows of the Veil", "Major revelation about the Veil", importance="major", tags=["revelation", "veil"])
record_combat_outcome("Shadows of the Veil", "Victory against shadow cultists", enemies_defeated=["cultist leader"])
```

## Design Principles (xAI-Native)
- **File-based & Human-Readable**: JSON as the machine source of truth + clean Markdown views for easy reading and direct editing.
- **Safe & Auditable by Default**: Important files are backed up before every write. All changes are traceable.
- **Campaign Isolation**: Every campaign lives in its own clean folder under `artifacts/dnd-campaigns/`.
- **Extensible & Composable**: Easy to add new helpers while maintaining reliability.
- **Built for Long Campaigns**: Robust state management prevents drift across dozens or hundreds of sessions. This is foundational to feeling native and trustworthy.

## Integration with Other Skills
- **dnd-persistent-dm**: Primary consumer — uses init/status/update on every major transition.
- **dnd-combat-assistant**: Will use combat/ subfolder + player + companion HP/condition helpers when relevant.
- **dnd-loot-generator**, **dnd-content-forge**, etc.: Can read current level/location from state for context-aware generation.
- **dnd-session-scribe**: Appends to logs/ using state timestamps.
- **dnd-dice-engine**: Can be extended to log rolls into session state.

## June 2026 Enhancements (Completed)
- Added `auto_record_significant_event()` — smart default wrapper used by the orchestrator for major beats.
- Added `record_combat_outcome_v2()` — improved combat logging with better tagging and structure.
- Added `enhanced_audit_campaign()` — extended cross-file consistency checks and recommendations.
- These helpers are now integrated into `dnd-persistent-dm` orchestration for more proactive, lower-friction long-term play.

The utils layer continues to be the rock-solid foundation that makes the entire skill suite feel native, reliable, and production-ready for campaigns spanning dozens or hundreds of sessions.

Run `python3 /home/workdir/.grok/skills/dnd-utils/scripts/dnd_state_utils.py --help` for full CLI options (including the new helpers).
