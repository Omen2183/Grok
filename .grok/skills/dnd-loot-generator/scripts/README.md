# Loot Generator Python Backend (Planned)

This directory will contain `procedural_loot.py` and supporting tables.

## Goals
- Weighted random loot generation scaled by party level / CR
- Thematically appropriate items for shadow/veil or custom campaign themes (example)
- Persistent loot ledger (what has already been found)
- Magic item balance checks
- Easy integration with dnd_state_utils for current location/level context

## Current Status
Scaffolding created. Core dnd_state_utils is available for context (location, level, etc.).

Next implementation pass will add the actual generator script.
