---
name: dnd-skills-manager
description: Meta-skill for maintaining, syncing, validating, and evolving the Grok D&D skills suite. Local tooling for inventory, validation, smoke tests, git status, and hash-based drift checks against another skills folder or GitHub export.
---

# dnd-skills-manager

Meta-tooling for the Grok D&D skills ecosystem.

## When to Use

- Check suite health before or after iOS/PC deploys
- Run validation and smoke tests from one command
- Inventory installed skills (scripts, tests)
- Compare local skills against a GitHub export or second install (`sync-check`)
- Prepare GitHub pull/drift reviews with Ara or Grok chat

**Triggers:** "skills manager", "sync skills", "validate skills", "check drift", "skills status", "skills inventory", "maintain skills"

## Capabilities

| Command | Purpose |
|---------|---------|
| `status` | Skills root, workspace, git status (when in repo) |
| `inventory` | List skills with scripts/tests |
| `validate` | Runs repo `scripts/validate_*.py` suite |
| `smoke` | Full end-to-end smoke test |
| `sync-check --against <path>` | Hash-compare `SKILL.md` + scripts vs another skills folder |
| `git` | Pass-through (`git status`, `git diff`, …) |
| `pull` / `drift` | Guides GitHub sync via connected tools in chat |

## Layout Notes

- **Repo clone:** resolves `scripts/` from workspace root (full validation works).
- **Global/iOS install** (`~/.grok/skills` or `/home/workdir/.grok/skills`): inventory and `sync-check` work; `validate`/`smoke` need repo `scripts/` or `GROK_WORKSPACE_ROOT` pointing at the clone.

## Example Commands

```bash
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py status
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py inventory
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py validate
python .grok/skills/dnd-skills-manager/scripts/skills_manager.py sync-check --against ./export/skills
```

## Behavior / Workflow

1. Run `status` + `inventory` to see what is installed.
2. Run `validate` then `smoke` before deploying to Grok iOS.
3. After an iOS export, run `sync-check --against <export/skills>` to list drift.
4. Use chat (`pull` / `drift`) for GitHub tree comparison and approved merges.

## Limitations

- Does not auto-update `skill_registry.py` (use `scripts/registry_sync.py` in repo).
- GitHub network pull/push uses chat + GitHub tools, not raw sandbox git remote.
- Not part of in-game orchestration — maintenance only.