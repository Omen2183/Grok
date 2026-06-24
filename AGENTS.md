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

## Before Editing

1. Run `python -m pytest -q` from the repo root.
2. Prefer extending `dnd_state_utils.py` over duplicating state logic.
3. Do not commit `__pycache__`, campaign artifacts, or zip exports.

## Installing Locally

```powershell
.\install.ps1 -Global
```

This installs skills to `%USERPROFILE%\.grok\skills\`.