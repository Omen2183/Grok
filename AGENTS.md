# AGENTS.md — Grok D&D Skills

This repository is a Grok Build skill pack for persistent D&D 5e campaigns.

## Layout

- `.grok/skills/<skill-name>/SKILL.md` — skill specifications
- `.grok/skills/<skill-name>/scripts/` — Python backends
- `.grok/skills/<skill-name>/tests/` — pytest tests where present

## Conventions

- Campaign state lives under `artifacts/dnd-campaigns/[name]/` (or `DND_CAMPAIGNS_ROOT`).
- `dnd-utils` is the shared foundation — other skills import from `dnd-utils/scripts/`.
- Use atomic JSON writes (temp file + rename) for state files.
- Keep `SKILL.md` files as the behavior spec; Python scripts handle deterministic logic.
- Cross-skill calls **must** go through `skill_registry.py` / `skill_orchestrator.py` — see `_PRODUCTION_CONVENTIONS.md`.

## Production Rules (Grok iOS)

1. Read `_PRODUCTION_CONVENTIONS.md` before editing any skill.
2. Every `SKILL.md` must include an honest **Capabilities** matrix — never document unimplemented helpers.
3. Player-facing output: short, scannable, confirm HP/XP changes, end with **What do you do?**
4. Use `python .grok/skills/...` paths — never hardcode `/home/workdir/`.

## Before Editing

1. Run `python -m pytest -q`, `python scripts/smoke_test.py`, `python scripts/validate_skills.py`, `python scripts/validate_backends.py`, and `python scripts/validate_skill_docs.py` from the repo root.
2. Every skill under `.grok/skills/` must ship at least one `scripts/*.py` with a CLI entry point.
3. Prefer extending `dnd_state_utils.py` over duplicating state logic.
4. Do not commit `__pycache__`, campaign artifacts, or zip exports.

## Installing Locally

```powershell
.\install.ps1 -Global
```

This installs skills to `%USERPROFILE%\.grok\skills\`.