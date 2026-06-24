---
name: dnd-session-scribe
description: Handles session recaps, state synchronization, XP tracking (including kingdom/domain awards), and preparation of future hooks. Turns play into clean, usable records so campaigns remain easy to resume even after long breaks.
---

# Dnd Session Scribe

## Overview
The session closer and archivist. It turns play into clean, usable records, updates all state files, awards and logs XP (including the lighter kingdom mode awards), and gives you clear "what's next" hooks so picking up later is effortless.

## When to Activate
- "End session"
- "Recap what happened"
- "Save the session"
- After a major scene or when wrapping up play for the day
- Automatically suggested at natural stopping points

## Core Tasks
1. **Create a Recap**:
   - Write a concise but flavorful summary of what occurred.
   - Highlight key decisions, revelations, combat outcomes, and kingdom developments.
   - Note any important NPC interactions or faction shifts.
   - Save to `recaps/` folder with date/session number.

2. **Update State**:
   - Use `dnd_state_utils.py` helpers for world/kingdom state and `combat_tracker.py` for combat cleanup.
   - Use `session_scribe.py award-xp` for experience tracking.
   - Record major events in `logs/session_log.md`.
   - Run `audit` when needed for consistency checks.
   - Briefly confirm with `persistent-dm` that the campaign state is now in sync.

**Bootstrap / Fallback Behavior**

If state files are missing or incomplete when ending a session:
- Create minimal versions of `world_state.json`, `player_character.md`, and `logs/session_log.md`.
- Record that initialization occurred during this session close.
- Still produce a recap and hooks.

3. **XP Tracking** (especially important in kingdom mode):
   - Clearly log all XP awarded during the session.
   - In kingdom mode, note the smaller domain action awards (50–300 XP range) separately so progress remains visible and satisfying.
   - Calculate and display total XP gained this session and current progress toward next level.

4. **Next Session Hooks**:
   - Provide 3–5 compelling hooks or loose threads for the next time you play.
   - Include both immediate personal hooks and longer-term kingdom/domain opportunities.
   - Note any time-sensitive situations (e.g. "The trade caravan arrives in two days").

## Output Style
- Clean, scannable format good for mobile review.
- Separate sections: What Happened, Key Changes, XP Gained, Loose Threads & Hooks.
- End with something like: "Session saved. Ready to continue whenever you are."

## Kingdom Mode Specific
When in kingdom mode, the recap should emphasize domain progress, faction reactions, construction/research outcomes, and how these actions affected the player character's standing and the wider world. Still award and clearly show the lighter XP so character growth continues.

## Long Campaign Polish
For very long-running campaigns:
- Occasionally suggest updating `state/lore_summary.md` (compressed lore) and `state/visual_canon.md` during major recaps.
- Consider running `dnd_state_utils.py audit "Campaign Name"` periodically to catch drift early.
- This keeps the game coherent without context bloat.

This skill turns your endless campaign into something you can easily pick up after days or weeks away and still feel fully immersed.