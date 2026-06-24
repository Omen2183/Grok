# Production Conventions (All D&D Skills)

## Campaign data location
Resolved automatically by `dnd-utils/scripts/paths.py`:
- `DND_CAMPAIGNS_ROOT` env var (if set)
- `~/.grok/artifacts/dnd-campaigns/` (Windows/macOS local)
- `/home/workdir/artifacts/dnd-campaigns/` (Grok cloud)

## Script invocation
```bash
python .grok/skills/<skill>/scripts/<script>.py <command> ...
```

## Grok iOS output rules
1. Lead with the answer — narration second, mechanics in a short block
2. Keep default replies under ~8 lines unless the player asks for detail
3. Confirm HP/XP/inventory changes with before → after
4. End active scenes with: **What do you do?**
5. In voice mode, route through `dnd-voice-assistant` first

## Never
- Hardcode `/home/workdir/` in player-facing text
- Claim a Python helper exists without checking `scripts/`
- Invent campaign state — read JSON first, write via backends