# Grok D&D Skills — v5.3.0

A complete Grok Build skill pack for running persistent, table-grade D&D 5e campaigns — classic tabletop and kingdom/domain play. Designed mobile-first for **Grok iOS** with full voice parity.

## What's Included

**18 skills** (17 play skills + `dnd-skills-manager` meta-tooling) — every player-facing skill has a Python CLI backend:

| Skill | Role |
|-------|------|
| `dnd-persistent-dm` | DM orchestrator (`persistent_dm.py`) — **16 playbooks** |
| `dnd-utils` | Campaign state, events, audits, narration CLI, registry |
| `dnd-combat-assistant` | Initiative, HP, conditions, tactical grid, auto-initiative |
| `dnd-dice-engine` | 5e dice rolling |
| `dnd-character-manager` | Sheets, leveling, inventory, multiclass, VTT export |
| `dnd-session-scribe` | Recaps, XP, auto-recap, `sync-quests` |
| `dnd-loot-generator` | Procedural loot + ledger |
| `dnd-content-forge` | Monsters, encounters, quests, factions |
| `dnd-npc-personality-weaver` | NPC personality + persistence |
| `dnd-lore-archivist` | FTS lore search + campaign memory |
| `dnd-rules-reference` | Rules cheatsheet + SRD + homebrew rulings |
| `dnd-rumor-event-generator` | World events, faction sim, rumors |
| `dnd-visual-weaver` | Consistent image prompts + battle maps |
| `dnd-voice-assistant` | Voice routing, compound phrases |
| `dnd-downtime-manager` | Short/long rests, downtime logging |
| `dnd-quest-tracker` | Active quests and session hooks |
| `dnd-randomizer` | Unified chaos engine — parties, dungeons, cultures, wild magic |
| `dnd-skills-manager` | Validate, smoke, score, drift-check (maintenance) |

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

## v5.3.0 Highlights

- **10-point suite gate:** `python scripts/suite_score.py` — validators + 143 tests + smoke
- **16 playbooks** including `quick-session`, `pre-session`, `party-to-combat`, `campaign-health`
- **Session-end** auto-runs `sync-quests` before quest list
- **Combat:** `--auto-initiative`, `seed-from-party`, `--dm-screen`
- **Skills manager:** `score --json`, `sync-all`, drift-check vs iOS exports

## Playbooks (16)

`campaign-health`, `chaos-campaign`, `downtime`, `end-combat`, `grid-combat`, `kingdom-turn`, `new-campaign`, `party-generator`, `party-to-combat`, `pre-session`, `quick-session`, `random-session`, `session-end`, `start-combat`, `visual-scene`, `vtt-export`

## Production Standards

- **Grok iOS native:** mobile-first replies, honest capability matrices in each `SKILL.md`, voice routing via `dnd-voice-assistant`
- **Shared state:** `dnd-utils/scripts/paths.py` resolves campaign folders on Windows, macOS, and Grok cloud
- **143 tests** + orchestration flow + full CLI smoke test
- **skill_registry** + **skill_orchestrator** for cross-skill coordination
- **GitHub Actions CI** on Python 3.11 and 3.12

See `.grok/skills/_PRODUCTION_CONVENTIONS.md` for agent conventions.

## Quality Gates

```powershell
python scripts/suite_score.py
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py sync-all
python scripts/registry_sync.py --check
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py runtime-context
```

### iOS deploy parity

After updating skills on device, compare against this repo:

```powershell
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py sync-check --against <path-to-ios-export/skills>
```

Target: `aligned: true` (zero drift) before calling the suite production-ready on iOS.

## Example Commands

```powershell
# Pre-session health + resume
python .grok/skills/dnd-persistent-dm/scripts/persistent_dm.py playbook "My Campaign" pre-session

# Quick one-shot session
python .grok/skills/dnd-persistent-dm/scripts/persistent_dm.py playbook "My Campaign" quick-session

# End session (sync-quests → end → quest list → audit)
python .grok/skills/dnd-persistent-dm/scripts/persistent_dm.py playbook "My Campaign" session-end

# Suite production grade
python scripts/suite_score.py
```

## License

Private repository — for personal use. Not affiliated with Wizards of the Coast or Hasbro.