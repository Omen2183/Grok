# Production Conventions (All D&D Skills)

## Campaign data location
Resolved automatically by `dnd-utils/scripts/paths.py`:
- `DND_CAMPAIGNS_ROOT` env var (if set — preferred on Grok iOS if auto-detect fails)
- `GROK_ARTIFACTS_ROOT` / `GROK_USER_DATA` / `GROK_HOME` (host-provided roots)
- `~/.grok/artifacts/dnd-campaigns/` (Windows/macOS local, Grok iOS when sandboxed)
- `/home/workdir/artifacts/dnd-campaigns/` (Grok cloud)

## Script invocation
```bash
python .grok/skills/<skill>/scripts/<script>.py <command> ...
```

## Skill coordination (10/10 requirement)

Every skill must delegate through the canonical registry — never improvise cross-skill calls.

| Layer | Script | Purpose |
|-------|--------|---------|
| Registry | `dnd-utils/scripts/skill_registry.py` | Maps intents → skills, playbooks, who-calls-whom |
| Orchestrator | `dnd-utils/scripts/skill_orchestrator.py` | `plan`, `execute`, `playbook` |
| DM hub | `dnd-persistent-dm/scripts/persistent_dm.py` | `route`, `execute`, `playbook`, `registry` |

### Routing flow
1. **Voice/text input** → `voice_utils.route` OR `persistent_dm route`
2. **Enrich** → `skill_orchestrator plan` adds CLI commands + follow-ups
3. **Execute** → target skill backend (confirm if `needs_confirmation`)
4. **Follow-up** → registry `then` / `after` skills (loot after combat, audit after session)

### Playbooks (multi-skill sequences)
| Playbook | Steps |
|----------|-------|
| `new-campaign` | init → resume → rumors |
| `start-combat` | combat init → initiative (manual) → summary |
| `end-combat` | end-combat → loot → clear combat |
| `session-end` | auto-recap → end-session → quest list → enhanced audit |
| `kingdom-turn` | advance projects → rumors → world event → kingdom summary |
| `downtime` | long rest → rumors → quest list |

```bash
python .grok/skills/dnd-persistent-dm/scripts/persistent_dm.py playbook "My Campaign" session-end
python .grok/skills/dnd-utils/scripts/skill_registry.py resolve damage --campaign "My Campaign"
```

### Per-skill rules
- **Read state first** via `dnd-utils` before narrating
- **Write state** only through the owning skill backend
- **Never skip** combat→character HP sync (`sync_bridge`) when damage applies to PC
- **Session end** always chains: session-scribe → quest-tracker hooks → utils audit
- **Kingdom turns** always chain: utils projects → rumor-generator → optional lore-archivist

## SKILL.md requirements (all 16 skills)
Each `SKILL.md` must include:
1. **Capabilities (Honest Matrix)** — only ✅ for implemented CLI behavior
2. **Tools & Scripts** — every subcommand from `scripts/*.py` with examples
3. **Skill Coordination** — registry, orchestrator, relevant playbooks, voice path
4. **Integration** — who calls this skill and what it calls
5. **iOS / Voice Notes** — mobile-first output rules where player-facing

Validate with: `python scripts/validate_skill_docs.py`

## Grok iOS output rules
1. Lead with the answer — narration second, mechanics in a short block
2. Keep default replies under ~8 lines unless the player asks for detail
3. Confirm HP/XP/inventory changes with before → after
4. End active scenes with: **What do you do?**
5. In voice mode, route through `dnd-voice-assistant` → `skill_orchestrator plan`

## Never
- Hardcode `/home/workdir/` in player-facing text
- Claim a Python helper exists without checking `scripts/`
- Invent campaign state — read JSON first, write via backends
- Call another skill without checking `skill_registry.py` for the canonical path