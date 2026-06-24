# Grok D&D Skills — Full Editable Source Export

**Date:** June 24, 2026  
**For:** Omen2183 (Josh)  
**Purpose:** Complete source for editing/customizing the D&D skills suite in a local "Grok Build CLI" or development workflow.

## What's Included

This export contains the **complete source** of all 14 D&D skills:

- Every `SKILL.md` specification file
- All Python backend scripts (`scripts/*.py`)
- Test files where present (`tests/`)
- Additional documentation (`docs/`) in skills that have them (especially dnd-utils and dnd-character-manager)
- Any README.md files inside the skill directories

**Skills included:**
- dnd-persistent-dm (the central orchestrator)
- dnd-character-manager
- dnd-combat-assistant
- dnd-content-forge
- dnd-dice-engine
- dnd-loot-generator
- dnd-lore-archivist
- dnd-npc-personality-weaver
- dnd-rules-reference
- dnd-rumor-event-generator
- dnd-session-scribe
- dnd-utils (shared state, helpers, narration, etc.)
- dnd-visual-weaver
- dnd-voice-assistant

## How to Use This Export

1. Download `grok-dnd-skills-full-source.tar.gz`
2. Extract it:
   ```bash
   tar -xzf grok-dnd-skills-full-source.tar.gz
   ```
3. You now have a `dnd-skills-source/` folder containing all the editable skill directories.

You can now:
- Edit any `SKILL.md` to change behavior descriptions/triggers
- Modify the Python scripts in `scripts/` to change actual logic (dice rolling, combat tracking, state management, etc.)
- Add new features, homebrew support, or fix bugs
- Version everything with git and push to your GitHub repo

## Recommended GitHub Workflow

1. Create a repo on GitHub (e.g. `grok-dnd-skills` or `dnd-skills-dev`)
2. Upload/extract this source into it
3. Treat `dnd-skills-source/` as the root of your skill development

When you make improvements locally:
- Commit and push to GitHub
- Share the updated files here with me if you want me to apply the same changes to the live skills in our conversations

## Important Notes

- `__pycache__` and `.pyc` files were excluded (they are generated at runtime)
- The Python scripts use relative imports and expect to be run from within the Grok environment or with proper `sys.path` setup
- `dnd-utils/scripts/` contains the most important shared utilities (`dnd_state_utils.py`, `narration_helpers.py`, etc.)
- Many skills have tight integration — changing one often requires coordinated changes in others (especially anything touching state or combat)

## Next Steps / How I Can Help

If you want, I can:
- Help you set up a local development workflow or simple "build" script
- Review/edit specific files together here
- Generate updated exports after you make changes
- Add a proper `pyproject.toml` / packaging setup if you want to turn this into an installable skill package later

Just let me know how you want to proceed with editing in your Grok Build CLI setup.

This export should give you everything you need to fully customize and evolve the D&D skills suite.

---

*Exported with care so you have full ownership and editability of your D&D toolkit.*