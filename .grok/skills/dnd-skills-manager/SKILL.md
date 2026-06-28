---
name: dnd-skills-manager
description: Meta-skill for maintaining, syncing, validating, and evolving the Grok D&D skills suite. v5.3.0 production. Local tooling for inventory, validation, smoke tests, 10-point suite score, git status, and hash-based drift checks against another skills folder or GitHub export.
---

# dnd-skills-manager

Meta-tooling for the Grok D&D skills ecosystem.

## When to Use

- Check suite health before or after iOS/PC deploys
- Run validation, smoke tests, and the 10-point suite score from one command
- Inventory installed skills (scripts, tests)
- Compare local skills against a GitHub export or second install (`sync-check`)
- Prepare GitHub pull/drift reviews with Ara or Grok chat

**Triggers:** "skills manager", "sync skills", "validate skills", "check drift", "skills status", "skills inventory", "maintain skills", "suite score"

## Capabilities

| Command | Purpose |
|---------|---------|
| `status` | Skills root, workspace, git status (when in repo) |
| `inventory` | List skills with scripts/tests |
| `validate` | Runs repo `scripts/validate_*.py` suite |
| `score` | 10-point production grade (`scripts/suite_score.py`) |
| `smoke` | Full end-to-end smoke test |
| `sync-all` | registry check + validate + smoke + pytest |
| `sync-check --against <path>` | Hash-compare `SKILL.md` + scripts vs another skills folder |
| `git` | Pass-through (`git status`, `git diff`, …) |
| `pull` / `drift` | Guides GitHub sync via connected tools in chat |

Repo script `scripts/suite_score.py` aggregates all validators into a **10/10 production grade** with per-dimension evidence.

## Tools & Scripts

```bash
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py status
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py inventory
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py validate
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py score
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py score --json
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py smoke
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py sync-all
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py sync-check --against ./export/skills
python scripts/suite_score.py
```

Primary script: `skills_manager.py` — commands: `status`, `inventory`, `validate`, `score`, `smoke`, `sync-all`, `sync-check`, `git`, `pull`, `drift`

## Layout Notes

- **Repo clone:** resolves `scripts/` from workspace root (full validation works).
- **Global/iOS install** (`~/.grok/skills`): inventory and `sync-check` work; `validate`/`smoke`/`sync-all` need repo `scripts/` or `GROK_WORKSPACE_ROOT` pointing at the clone.
- Campaign paths always resolve via `dnd-utils/paths.py` and `DND_CAMPAIGNS_ROOT` — never hardcode sandbox paths.

## Behavior / Workflow

1. Run `status` + `inventory` to see what is installed.
2. Run `validate` then `smoke` (or `sync-all`) before deploying to Grok iOS.
3. Run `python scripts/suite_score.py` for the authoritative 10-point grade.
4. After an iOS export, run `sync-check --against <export/skills>` to list drift.
5. Use chat (`pull` / `drift`) for GitHub tree comparison and approved merges.

## Skill Coordination

| Layer | Role |
|-------|------|
| Registry | Not routed during play — maintenance only |
| Orchestrator | Not invoked by playbooks |
| Other skills | Reads their `SKILL.md` + scripts for drift checks |

## Integration

- **Uses:** `dnd-utils/paths.py` for skills root and workspace resolution
- **Calls:** repo `scripts/validate_*.py`, `smoke_test.py`, `registry_sync.py`, `suite_score.py`
- **Does not modify:** `skill_registry.py` (use `scripts/registry_sync.py` in repo)

## iOS / Voice Notes

- Not player-facing. Run from PC/repo before pushing skills to Grok iOS.
- Voice play never routes here — use `dnd-voice-assistant` or `dnd-persistent-dm`.

## Limitations

- Does not auto-update `skill_registry.py` (use `scripts/registry_sync.py` in repo).
- GitHub network pull/push uses chat + GitHub tools, not raw sandbox git remote.
- Not part of in-game orchestration — maintenance only.