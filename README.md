# Grok D&D Skills

A complete Grok Build skill pack for running persistent, high-quality D&D 5e campaigns — classic tabletop and kingdom/domain play.

## What's Included

16 interconnected skills — **every skill has a Python CLI backend**:

| Skill | Role |
|-------|------|
| `dnd-persistent-dm` | DM orchestrator (`persistent_dm.py`) |
| `dnd-utils` | Campaign state, events, audits, narration CLI |
| `dnd-combat-assistant` | Initiative, HP, conditions |
| `dnd-dice-engine` | 5e dice rolling |
| `dnd-character-manager` | Sheets, leveling, inventory, level-up suggestions |
| `dnd-session-scribe` | Recaps, XP, auto-recap from events |
| `dnd-loot-generator` | Procedural loot + ledger |
| `dnd-content-forge` | Monsters, encounters, quests, factions |
| `dnd-npc-personality-weaver` | NPC personality + persistence |
| `dnd-lore-archivist` | Campaign lore memory |
| `dnd-rules-reference` | Rules cheatsheet CLI + Grok rulings |
| `dnd-rumor-event-generator` | World events and rumors |
| `dnd-visual-weaver` | Consistent image prompts |
| `dnd-voice-assistant` | Voice routing and phrase parsing |
| `dnd-downtime-manager` | Short/long rests, downtime logging |
| `dnd-quest-tracker` | Active quests and session hooks |

## Quick Start

### Install skills into Grok Build

```powershell
# From this repo
.\install.ps1

# Or install into a specific project
.\install.ps1 -Target C:\path\to\your\project
```

This copies `.grok/skills/` into your user or project Grok directory.

### Start a campaign

Say to Grok: **"Let's play D&D"** or **"DM mode"**

Or initialize manually:

```powershell
python .grok/skills/dnd-persistent-dm/scripts/persistent_dm.py init "My Campaign"
```

Campaign state is stored at:

- **Windows:** `%USERPROFILE%\.grok\artifacts\dnd-campaigns\[Campaign Name]\`
- **Grok cloud:** `/home/workdir/artifacts/dnd-campaigns/[Campaign Name]/`

Override with the `DND_CAMPAIGNS_ROOT` environment variable.

## Production Standards

- **Grok iOS native:** mobile-first replies, honest capability matrices in each `SKILL.md`, voice routing via `dnd-voice-assistant`
- **Shared state:** `dnd-utils/scripts/paths.py` resolves campaign folders on Windows, macOS, and Grok cloud
- **68 tests** + orchestration flow + full CLI smoke test (all 16 skills)
- **skill_registry** + **skill_orchestrator** for cross-skill coordination
- **GitHub Actions CI** on Python 3.11 and 3.12

See `.grok/skills/_PRODUCTION_CONVENTIONS.md` for agent conventions.

## Quality Gates

```powershell
python -m pytest -q            # full test suite
python scripts/smoke_test.py   # smoke test all 16 skill CLIs
python scripts/validate_skills.py  # verify every skill has Python backend
python scripts/validate_orchestration.py  # verify registry matches all 16 skills
```

## Development

```powershell
# Run all tests
python -m pytest -q

# Run a single skill's tests
python -m pytest .grok/skills/dnd-combat-assistant/tests -v
```

## Repository Structure

```
.grok/skills/          # All 14 skills (SKILL.md + scripts/)
install.ps1            # Windows installer
install.sh             # macOS/Linux installer
pyproject.toml         # Dev dependencies
AGENTS.md              # Agent instructions for this repo
```

## Example Commands

```powershell
# Check campaign status
python .grok/skills/dnd-utils/scripts/dnd_state_utils.py status "My Campaign"

# Roll dice
python .grok/skills/dnd-dice-engine/scripts/dice_roller.py "1d20+5" --advantage

# Generate loot
python .grok/skills/dnd-loot-generator/scripts/procedural_loot.py generate "My Campaign" --cr 3

# End a session
python .grok/skills/dnd-session-scribe/scripts/session_scribe.py end-session "My Campaign" "We cleared the mine." --xp 150
```

## License

Private repository — for personal use.