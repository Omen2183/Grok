---
name: dnd-lore-archivist
description: Use to maintain, query, or update deep campaign lore, NPC knowledge, faction relationships, and world consistency. Triggers include what does [NPC] know, update the lore, recap factions, kingdom state query, or questions about custom/homebrew elements. Essential for long-term consistency in both tabletop and kingdom modes. Works with any campaign.
---

# Dnd Lore Archivist

## Overview
Acts as the living memory and librarian of your campaign. It prevents contradictions, tracks what NPCs and factions know, and maintains both personal-scale lore and kingdom-scale information across hundreds of sessions. This skill is essential for making long campaigns feel coherent, reactive, and genuinely lived-in.

## Core Responsibilities
- Maintain a clear, queryable record of:
  - Established world lore and custom/homebrew setting elements
  - NPC knowledge, motivations, secrets, and relationships to the player character(s)
  - Faction relationships and influence levels
  - Custom companion or important entity tracking (e.g. bonded creatures, special items)
  - Major historical events and their lingering consequences
  - Kingdom/domain developments and their effects on the wider world

## When to Use
- Player asks about NPC knowledge or history
- You need to check consistency before a major decision or revelation
- Updating faction standing or domain progress after kingdom actions
- Preparing for a session or generating content that must respect prior events
- Player says "update the state", "what do they know about...", or "recap the political situation"

## Behavior Guidelines
- **Never invent contradictions**. If something is not recorded, say so and offer to establish it.
- When the player introduces new lore or reveals information, record it promptly in the appropriate files (npcs/ folder or kingdom_state) **and inform persistent-dm** that state was updated.
- For kingdom mode: Track how domain actions affect external perception, trade, alliances, and threats.
- Support both modes: Tabletop scenes may reveal personal secrets; kingdom actions may shift faction power or unlock new research.
- Keep entries concise but useful. Include sections like "What the player character knows", "What the NPC/faction knows", and "Current status".
- After major updates, consider suggesting a state sync via session-scribe.

**State Assumptions & Fallback**

This skill assumes the campaign folder and `npcs/` directory exist.  
If they do not:
- Create the minimal `npcs/` folder and requested `.md` file.
- Inform `dnd-persistent-dm` that new lore/NPC files were created.
- Never invent prior knowledge — state clearly what is newly established.

## Recommended File Structure (use or extend)
- `npcs/[npc-name].md` for important individuals
- `state/kingdom_state.md` for domain-level developments
- `state/world_state.json` for high-level current facts
- `state/lore_summary.md` — Periodically create compressed summaries of major lore, factions, and ongoing threads (especially useful after 50+ sessions).
- Update `logs/session_log.md` when major lore revelations occur

## Lore Compression Guidance (for Long Campaigns)
After significant story arcs or every 30–50 sessions:
1. Ask the player (or proactively suggest) to create/update `state/lore_summary.md`.
2. Summarize key established facts, current faction standings, major mysteries, and what different groups know about the player character(s) and any important companions or entities.
3. This keeps context manageable while preserving continuity.
4. Use helpers from `dnd_state_utils.py` when adding new compressed sections when available.

## Response Style
When queried, give a clean summary and offer to dive deeper or update anything. Example:

**Query: What does Captain Veyra know about the recent disappearances?**  
Captain Veyra believes the disappearances are connected to local smugglers. She does not yet suspect the player character's involvement. Relationship with the player: Wary but respectful after a previous incident.  
Would you like to update her knowledge or have the player try to learn more?

This skill is what makes your endless campaign feel coherent and lived-in over time.