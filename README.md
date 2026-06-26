# Grok D&D Skills — v5.0.0

A complete Grok Build skill pack for running persistent, table-grade D&D 5e campaigns — classic tabletop and kingdom/domain play. Designed mobile-first for **Grok iOS** with full voice parity.

## What's Included

17 interconnected skills — **every skill has a Python CLI backend**:

| Skill | Role |
|-------|------|
| `dnd-persistent-dm` | DM orchestrator (`persistent_dm.py`) |
| `dnd-utils` | Campaign state, events, audits, narration CLI |
| `dnd-combat-assistant` | Initiative, HP, conditions, tactical grid |
| `dnd-dice-engine` | 5e dice rolling |
| `dnd-character-manager` | Sheets, leveling, inventory, VTT export |
| `dnd-session-scribe` | Recaps, XP, auto-recap from events |
| `dnd-loot-generator` | Procedural loot + ledger |
| `dnd-content-forge` | Monsters, encounters, quests, factions |
| `dnd-npc-personality-weaver` | NPC personality + persistence |
| `dnd-lore-archivist` | FTS lore search + campaign memory |
| `dnd-rules-reference` | Rules cheatsheet + SRD index |
| `dnd-rumor-event-generator` | World events, faction sim, rumors |
| `dnd-visual-weaver` | Consistent image prompts + battle maps |
| `dnd-voice-assistant` | Voice routing and phrase parsing |
| `dnd-downtime-manager` | Short/long rests, downtime logging |
| `dnd-quest-tracker` | Active quests and session hooks |
| `dnd-randomizer` | Unified chaos engine — parties, dungeons, cultures, wild magic |

## Quick Start

**New players:** see [PLAYERS.md](PLAYERS.md) for Grok iOS quickstart with plain language.

### Install skills into Grok Build

```powershell
# From this repo
.\install.ps1

# Global install (all Grok projects)
.\install.ps1 -Global
```

### Start a campaign

Say to Grok: **"Let's play D&D"** or **"DM mode"**

Or initialize manually:

```powershell
python .grok/skills/dnd-persistent-dm/scripts/persistent_dm.py init "My Campaign"
```

Campaign state: `%USERPROFILE%\.grok\artifacts\dnd-campaigns\[Campaign Name]\`

## v5.0.0 Highlights

- **Randomizer complete:** cultural names, class kits, party generator, dungeon floors, wild magic surge, `--balanced` delegation, table import/export
- **Playbooks:** `party-generator`, enhanced `random-session`
- **Voice 5.0:** party, dungeon, wild magic phrase routing
- **Premium player docs:** [PLAYERS.md](PLAYERS.md) rewritten for Grok iOS

## Production Standards

- **Grok iOS native:** mobile-first replies, honest capability matrices in each `SKILL.md`, voice routing via `dnd-voice-assistant`
- **Shared state:** `dnd-utils/scripts/paths.py` resolves campaign folders on Windows, macOS, and Grok cloud
- **125+ tests** + orchestration flow + full CLI smoke test (all 17 skills)
- **skill_registry** + **skill_orchestrator** for cross-skill coordination
- **GitHub Actions CI** on Python 3.11 and 3.12

See `.grok/skills/_PRODUCTION_CONVENTIONS.md` for agent conventions.

## Quality Gates

```powershell
python -m pytest -q
python scripts/smoke_test.py
python scripts/validate_skills.py
python scripts/validate_orchestration.py
python scripts/validate_backends.py
python scripts/validate_skill_docs.py
python scripts/registry_sync.py --check
python scripts/validate_runtime.py       # Grok iOS / PC path conventions
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py runtime-context
```

## Example Commands

```powershell
# Random party + dungeon (v5)
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-party --size 4 --level 3
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-dungeon "My Campaign" --rooms 6

# Balanced loot via randomizer
python .grok/skills/dnd-randomizer/scripts/randomizer.py random-item "My Campaign" --balanced --level 5

# Roll dice
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py roll 1d20+5 --advantage

# End a session
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py end-session "My Campaign" "We cleared the mine." --xp 150
```

## License

Private repository — for personal use. Not affiliated with Wizards of the Coast or Hasbro.